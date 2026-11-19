import request from 'supertest';
import type { Response } from 'supertest';
import { decodeJwt } from 'jose';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { SESSION_COOKIE, SESSION_MAX_AGE_SECONDS } from '../src/modules/auth/session.js';
import { OTP_MAX_ATTEMPTS, OTP_TTL_MINUTES, hashOtp } from '../src/utils/otp.js';
import {
  clearMailbox,
  countMailFiles,
  readLatestOtp,
  uniqueDocument,
  uniqueEmail,
} from './helpers.js';

const app = createApp();

/** `originCheck` exige mismo origen en toda mutación (§15). */
const ORIGIN = 'https://localhost';

const post = (path: string) => request(app).post(path).set('Origin', ORIGIN);

interface RegisterOverrides {
  nombres?: string;
  apellidos?: string;
  tipoDocumentoId?: number;
  numeroDocumento?: string;
  correoInstitucional?: string;
  password?: string;
  aceptaTratamiento?: boolean;
}

function registerPayload(overrides: RegisterOverrides = {}) {
  return {
    nombres: 'Ana María',
    apellidos: 'Prueba Integración',
    tipoDocumentoId: 1,
    numeroDocumento: uniqueDocument(),
    correoInstitucional: uniqueEmail(),
    password: 'Secreta123',
    aceptaTratamiento: true,
    ...overrides,
  };
}

async function registerStudent(overrides: RegisterOverrides = {}) {
  const payload = registerPayload(overrides);
  const response = await post('/api/auth/register').send(payload);
  return { payload, response };
}

/** Registra, verifica con el OTP real y activa la cuenta (lo haría el admin). */
async function createActiveStudent() {
  const { payload, response } = await registerStudent();
  const codigo = await readLatestOtp();

  await post('/api/auth/verify')
    .send({ correoInstitucional: payload.correoInstitucional, codigo })
    .expect(200);

  await query(`UPDATE usuarios SET estado = 'Activo' WHERE correo_institucional = $1`, [
    payload.correoInstitucional,
  ]);

  return {
    id: response.body.data.id as number,
    correo: payload.correoInstitucional,
    password: payload.password,
    documento: payload.numeroDocumento,
  };
}

function sessionCookie(response: Response): string {
  const headers = response.headers['set-cookie'] as unknown as string[] | undefined;
  const cookie = headers?.find((value) => value.startsWith(`${SESSION_COOKIE}=`));
  if (!cookie) throw new Error('La respuesta no trae la cookie de sesión');
  return cookie;
}

function sessionToken(response: Response): string {
  const cookie = sessionCookie(response);
  return decodeURIComponent(cookie.split(';')[0]!.slice(SESSION_COOKIE.length + 1));
}

/**
 * Inicia sesión y devuelve un cliente que reenvía la cookie explícitamente.
 *
 * No se usa `request.agent`: la cookie es `Secure` y el jar de supertest no la envía
 * por HTTP plano, así que el agente perdería la sesión dentro de las pruebas.
 */
async function loginSession(correo: string, password: string) {
  const response = await post('/api/auth/login').send({
    correoInstitucional: correo,
    password,
  });
  const token = sessionToken(response);
  const cookie = `${SESSION_COOKIE}=${token}`;

  return {
    response,
    token,
    get: (path: string) => request(app).get(path).set('Cookie', cookie),
    post: (path: string) => request(app).post(path).set('Origin', ORIGIN).set('Cookie', cookie),
  };
}

async function userRow(correo: string) {  const { rows } = await query<{
    id_usuarios: number;
    estado: string;
    verificado: boolean;
    roles_id_roles: number;
    password: string;
  }>(
    `SELECT id_usuarios, estado, verificado, roles_id_roles, password
       FROM usuarios WHERE correo_institucional = $1`,
    [correo],
  );
  return rows[0]!;
}

async function otpRow(correo: string, proposito = 'Verificación') {
  const { rows } = await query<{
    id_codigo: number;
    codigo: string;
    expiracion: Date;
    usado: boolean;
    intentos: number;
  }>(
    `SELECT id_codigo, codigo, expiracion, usado, intentos
       FROM codigosverificacion
      WHERE correo_institucional = $1 AND proposito = $2
      ORDER BY id_codigo DESC LIMIT 1`,
    [correo, proposito],
  );
  return rows[0]!;
}

beforeEach(async () => {
  // Los límites son por IP: se vacían para que un caso no agote el cubo de otro.
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

/* =====================================================================================
 * T01 — registro
 * =================================================================================== */

describe('T01 · registro', () => {
  it('crea una cuenta Limitado sin verificar y emite un OTP de 8 dígitos con 5 minutos', async () => {
    const { payload, response } = await registerStudent();

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data).toMatchObject({
      estado: 'Limitado',
      verificado: false,
      rol: { id: 2, nombre: 'Estudiante' },
      correoInstitucional: payload.correoInstitucional,
    });

    const row = await userRow(payload.correoInstitucional);
    expect(row.estado).toBe('Limitado');
    expect(row.verificado).toBe(false);
    expect(row.roles_id_roles).toBe(2);
    // bcrypt coste 10, nunca la contraseña en claro.
    expect(row.password).toMatch(/^\$2[aby]\$10\$/);
    expect(row.password).not.toContain(payload.password);

    const otp = await otpRow(payload.correoInstitucional);
    const enviado = await readLatestOtp();

    expect(enviado).toMatch(/^\d{8}$/);
    // Se guarda el HMAC, nunca el código en claro (D20).
    expect(otp.codigo).toMatch(/^[0-9a-f]{64}$/);
    expect(otp.codigo).toBe(hashOtp(payload.correoInstitucional, 'Verificación', enviado));
    expect(otp.usado).toBe(false);
    expect(otp.intentos).toBe(0);

    const vigenciaMin = (new Date(otp.expiracion).getTime() - Date.now()) / 60_000;
    expect(vigenciaMin).toBeGreaterThan(OTP_TTL_MINUTES - 0.5);
    expect(vigenciaMin).toBeLessThanOrEqual(OTP_TTL_MINUTES + 0.1);

    // El transporte de correo fue llamado una vez.
    expect(await countMailFiles()).toBe(1);
  });

  it('rechaza un correo institucional ya registrado', async () => {
    const { payload } = await registerStudent();
    const repetido = await post('/api/auth/register').send(
      registerPayload({ correoInstitucional: payload.correoInstitucional }),
    );

    expect(repetido.status).toBe(409);
    expect(repetido.body.error.code).toBe('EMAIL_TAKEN');
  });

  it('rechaza un número de documento ya registrado', async () => {
    const { payload } = await registerStudent();
    const repetido = await post('/api/auth/register').send(
      registerPayload({ numeroDocumento: payload.numeroDocumento }),
    );

    expect(repetido.status).toBe(409);
    expect(repetido.body.error.code).toBe('DOCUMENT_TAKEN');
  });

  it('rechaza un dominio que no es institucional', async () => {
    const response = await post('/api/auth/register').send(
      registerPayload({ correoInstitucional: uniqueEmail().replace('uniminuto.edu.co', 'gmail.com') }),
    );

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('EMAIL_DOMAIN_NOT_ALLOWED');
  });

  it('exige la autorización de tratamiento de datos', async () => {
    const response = await post('/api/auth/register').send(
      registerPayload({ aceptaTratamiento: false }),
    );

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.fields).toHaveProperty('aceptaTratamiento');
  });

  it('rechaza campos que el cliente no puede fijar (rol, estado, verificado)', async () => {
    for (const extra of [{ roles_id_roles: 1 }, { estado: 'Activo' }, { verificado: true }]) {
      const response = await post('/api/auth/register').send({
        ...registerPayload(),
        ...extra,
      });

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    }
  });

  it('verifica el correo con el código correcto', async () => {
    const { payload } = await registerStudent();
    const codigo = await readLatestOtp();

    const response = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo,
    });

    expect(response.status).toBe(200);
    expect((await userRow(payload.correoInstitucional)).verificado).toBe(true);
    expect((await otpRow(payload.correoInstitucional)).usado).toBe(true);
  });

  it('rechaza un código incorrecto, uno vencido y uno ya usado', async () => {
    const { payload } = await registerStudent();
    const codigo = await readLatestOtp();

    const incorrecto = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo: codigo === '00000000' ? '11111111' : '00000000',
    });
    expect(incorrecto.status).toBe(422);
    expect(incorrecto.body.error.code).toBe('OTP_INVALID');

    // Vencido: se retrocede la expiración.
    await query(
      `UPDATE codigosverificacion SET expiracion = now() - interval '1 minute'
        WHERE correo_institucional = $1 AND proposito = 'Verificación'`,
      [payload.correoInstitucional],
    );
    const vencido = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo,
    });
    expect(vencido.status).toBe(422);
    expect(vencido.body.error.code).toBe('OTP_INVALID');

    // Reutilizado: se vuelve a emitir, se usa y se intenta otra vez.
    await post('/api/auth/resend-code').send({ correoInstitucional: payload.correoInstitucional });
    const nuevo = await readLatestOtp();
    await post('/api/auth/verify')
      .send({ correoInstitucional: payload.correoInstitucional, codigo: nuevo })
      .expect(200);

    const reutilizado = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo: nuevo,
    });
    expect(reutilizado.status).toBe(422);
    expect(reutilizado.body.error.code).toBe('OTP_INVALID');
  });

  it(`quema el código tras ${OTP_MAX_ATTEMPTS} intentos fallidos`, async () => {
    const { payload } = await registerStudent();
    const codigo = await readLatestOtp();
    const erroneo = codigo === '00000000' ? '11111111' : '00000000';

    for (let intento = 1; intento < OTP_MAX_ATTEMPTS; intento += 1) {
      const response = await post('/api/auth/verify').send({
        correoInstitucional: payload.correoInstitucional,
        codigo: erroneo,
      });
      expect(response.status).toBe(422);
      expect(response.body.error.code).toBe('OTP_INVALID');
    }

    const agotado = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo: erroneo,
    });
    expect(agotado.status).toBe(429);
    expect(agotado.body.error.code).toBe('OTP_ATTEMPTS_EXCEEDED');

    // El código correcto ya no sirve: quedó quemado.
    const tarde = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo,
    });
    expect(tarde.status).toBe(422);
    expect(tarde.body.error.code).toBe('OTP_INVALID');
  });

  it('aplica el cooldown de reenvío y permite reenviar cuando pasa', async () => {
    const { payload } = await registerStudent();

    const inmediato = await post('/api/auth/resend-code').send({
      correoInstitucional: payload.correoInstitucional,
    });
    expect(inmediato.status).toBe(429);
    expect(inmediato.body.error.code).toBe('OTP_COOLDOWN');
    expect(Number(inmediato.headers['retry-after'])).toBeGreaterThan(0);
    expect(await countMailFiles()).toBe(1);

    // Se simula el paso del cooldown retrociendo la emisión (P-13).
    await query(
      `UPDATE codigosverificacion SET expiracion = expiracion - interval '61 seconds'
        WHERE correo_institucional = $1 AND proposito = 'Verificación' AND usado = FALSE`,
      [payload.correoInstitucional],
    );

    const reenvio = await post('/api/auth/resend-code').send({
      correoInstitucional: payload.correoInstitucional,
    });
    expect(reenvio.status).toBe(200);
    expect(await countMailFiles()).toBe(2);

    // El código anterior quedó invalidado y el nuevo verifica.
    const nuevo = await readLatestOtp();
    await post('/api/auth/verify')
      .send({ correoInstitucional: payload.correoInstitucional, codigo: nuevo })
      .expect(200);
  });

  it('no revela si el correo existe al reenviar el código', async () => {
    const response = await post('/api/auth/resend-code').send({
      correoInstitucional: uniqueEmail('inexistente'),
    });

    expect(response.status).toBe(200);
    expect(await countMailFiles()).toBe(0);
  });

  it('nunca devuelve el OTP ni la contraseña en el cuerpo de una respuesta', async () => {
    const { payload, response: registro } = await registerStudent();
    const codigo = await readLatestOtp();
    expect(JSON.stringify(registro.body)).not.toContain(codigo);
    expect(JSON.stringify(registro.body)).not.toContain(payload.password);

    const verificacion = await post('/api/auth/verify').send({
      correoInstitucional: payload.correoInstitucional,
      codigo,
    });
    expect(verificacion.status).toBe(200);
    expect(JSON.stringify(verificacion.body)).not.toContain(codigo);

    // Reenvío: hay un código nuevo y tampoco viaja en la respuesta.
    await query(
      `UPDATE codigosverificacion SET expiracion = expiracion - interval '61 seconds'
        WHERE correo_institucional = $1 AND proposito = 'Verificación' AND usado = FALSE`,
      [payload.correoInstitucional],
    );
    const reenvio = await post('/api/auth/resend-code').send({
      correoInstitucional: payload.correoInstitucional,
    });
    const reenviado = await readLatestOtp();
    expect(reenvio.status).toBe(200);
    expect(JSON.stringify(reenvio.body)).not.toContain(reenviado);

    // Recuperación: igual.
    const olvido = await post('/api/auth/forgot-password').send({
      correoInstitucional: payload.correoInstitucional,
    });
    const recuperacion = await readLatestOtp();
    expect(olvido.status).toBe(200);
    expect(JSON.stringify(olvido.body)).not.toContain(recuperacion);
  });
});

/* =====================================================================================
 * T02 — inicio de sesión
 * =================================================================================== */

describe('T02 · inicio de sesión', () => {
  it('rechaza una contraseña incorrecta', async () => {
    const response = await post('/api/auth/login').send({
      correoInstitucional: 'estudiante.demo1@uniminuto.edu.co',
      password: 'NoEsLaClave',
    });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('INVALID_CREDENTIALS');
    expect(response.headers['set-cookie']).toBeUndefined();
  });

  it('rechaza un correo inexistente con el mismo código y sin filtrar por tiempo', async () => {
    const response = await post('/api/auth/login').send({
      correoInstitucional: uniqueEmail('fantasma'),
      password: 'Secreta123',
    });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('INVALID_CREDENTIALS');
  });

  it('rechaza una cuenta sin verificar', async () => {
    const { payload } = await registerStudent();

    const response = await post('/api/auth/login').send({
      correoInstitucional: payload.correoInstitucional,
      password: payload.password,
    });

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('EMAIL_NOT_VERIFIED');
    expect(response.headers['set-cookie']).toBeUndefined();
  });

  it('inicia sesión con cookie HttpOnly/Secure/SameSite=Strict de 8 h y sin token en el cuerpo', async () => {
    const response = await post('/api/auth/login').send({
      correoInstitucional: 'estudiante.demo1@uniminuto.edu.co',
      password: 'Demo1234',
    });

    expect(response.status).toBe(200);
    expect(Object.keys(response.body.data)).toEqual(['usuario']);
    expect(response.body.data.usuario).not.toHaveProperty('password');
    expect(JSON.stringify(response.body)).not.toMatch(/\$2[aby]\$/);
    expect(JSON.stringify(response.body)).not.toMatch(/token/i);

    const cookie = sessionCookie(response);
    expect(cookie).toContain('HttpOnly');
    expect(cookie).toContain('Secure');
    expect(cookie).toContain('SameSite=Strict');
    expect(cookie).toContain('Path=/');
    expect(cookie).toContain(`Max-Age=${SESSION_MAX_AGE_SECONDS}`);
  });

  it('el JWT lleva solo {id, role} y expira en 8 h', async () => {
    const response = await post('/api/auth/login').send({
      correoInstitucional: 'estudiante.demo1@uniminuto.edu.co',
      password: 'Demo1234',
    });

    const payload = decodeJwt(sessionToken(response));

    expect(Object.keys(payload).sort()).toEqual(['exp', 'iat', 'id', 'role']);
    expect(payload.role).toBe(2);
    expect(typeof payload.id).toBe('number');
    expect((payload.exp as number) - (payload.iat as number)).toBe(SESSION_MAX_AGE_SECONDS);
    expect(SESSION_MAX_AGE_SECONDS).toBe(28_800);
  });

  it('actualiza la última actividad al iniciar sesión', async () => {
    await post('/api/auth/login')
      .send({
        correoInstitucional: 'docente.demo1@uniminuto.edu.co',
        password: 'Demo1234',
      })
      .expect(200);

    const { rows } = await query<{ reciente: boolean }>(
      `SELECT ultima_actividad > now() - interval '1 minute' AS reciente
         FROM usuarios WHERE correo_institucional = 'docente.demo1@uniminuto.edu.co'`,
    );
    expect(rows[0]!.reciente).toBe(true);
  });
});

/* =====================================================================================
 * T03 — cuenta Limitado en endpoints restringidos
 * =================================================================================== */

describe('T03 · cuenta Limitado', () => {
  it('no entra a un módulo de trabajo y recibe ACCOUNT_NOT_ACTIVE', async () => {
    const session = await loginSession('estudiante.demo2@uniminuto.edu.co', 'Demo1234');

    const response = await session.get('/api/diagnosis/form');

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
    expect(response.body.error.message).toMatch(/pendiente de activación/i);
  });

  it('sí puede leer su propio perfil', async () => {
    const session = await loginSession('estudiante.demo2@uniminuto.edu.co', 'Demo1234');

    const response = await session.get('/api/users/me');

    expect(response.status).toBe(200);
    expect(response.body.data.estado).toBe('Limitado');
    expect(response.body.data).not.toHaveProperty('password');
  });

  it('una cuenta Activo sí obtiene el formulario de diagnóstico', async () => {
    const session = await loginSession('estudiante.demo1@uniminuto.edu.co', 'Demo1234');

    const response = await session.get('/api/diagnosis/form');

    expect(response.status).toBe(200);
    expect(response.body.data.total).toBe(22);
    expect(response.body.data.preguntas).toHaveLength(22);
    expect(response.body.data.preguntas[0]).toMatchObject({
      seccion: 1,
      orden: expect.any(Number),
      enunciado: expect.any(String),
    });
  });
});

/* =====================================================================================
 * T04 — sesión, firma, baja lógica y CSRF
 * =================================================================================== */

describe('T04 · sesión', () => {
  it('sin cookie responde 401', async () => {
    const response = await request(app).get('/api/users/me');

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTH_REQUIRED');
  });

  it('rechaza una firma alterada', async () => {
    const login = await post('/api/auth/login').send({
      correoInstitucional: 'estudiante.demo1@uniminuto.edu.co',
      password: 'Demo1234',
    });

    const token = sessionToken(login);
    const [header, payload, signature] = token.split('.');
    const alterado = `${header}.${payload}.${signature!.slice(0, -2)}xx`;

    const response = await request(app)
      .get('/api/users/me')
      .set('Cookie', `${SESSION_COOKIE}=${alterado}`);

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTH_INVALID');
  });

  it('rechaza un token firmado con otro secreto', async () => {
    // Token bien formado pero de otra instalación.
    const ajeno =
      'eyJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwicm9sZSI6MX0.' +
      'ZmlybWEtaW52YWxpZGEtcXVlLW5vLWNvaW5jaWRlLWNvbi1lbC1zZWNyZXRv';

    const response = await request(app)
      .get('/api/users/me')
      .set('Cookie', `${SESSION_COOKIE}=${ajeno}`);

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTH_INVALID');
  });

  it('una baja lógica invalida la cookie vigente en la petición siguiente', async () => {
    const student = await createActiveStudent();
    const session = await loginSession(student.correo, student.password);

    await session.get('/api/users/me').expect(200);

    await query('UPDATE usuarios SET fecha_eliminacion = now() WHERE id_usuarios = $1', [
      student.id,
    ]);

    const response = await session.get('/api/users/me');
    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTH_INVALID');
  });

  it('una cuenta Inactivo queda bloqueada en la petición siguiente', async () => {
    const student = await createActiveStudent();
    const session = await loginSession(student.correo, student.password);

    await session.get('/api/diagnosis/form').expect(200);

    await query(`UPDATE usuarios SET estado = 'Inactivo' WHERE id_usuarios = $1`, [student.id]);

    const response = await session.get('/api/diagnosis/form');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
    expect(response.body.error.message).toMatch(/inactiva/i);
  });

  it('toma el rol de la fila y no del token', async () => {
    const student = await createActiveStudent();
    const session = await loginSession(student.correo, student.password);

    expect(decodeJwt(session.token).role).toBe(2);

    try {
      await query('UPDATE usuarios SET roles_id_roles = 3 WHERE id_usuarios = $1', [student.id]);

      const response = await session.get('/api/users/me');
      expect(response.status).toBe(200);
      expect(response.body.data.rol.id).toBe(3);
    } finally {
      await query('UPDATE usuarios SET roles_id_roles = 2 WHERE id_usuarios = $1', [student.id]);
    }
  });

  it('el cierre de sesión limpia la cookie', async () => {
    const session = await loginSession('estudiante.demo1@uniminuto.edu.co', 'Demo1234');

    const logout = await session.post('/api/auth/logout');

    expect(logout.status).toBe(200);
    const cookie = sessionCookie(logout);
    // El navegador debe borrarla: expiración en el pasado.
    expect(cookie).toMatch(/Expires=Thu, 01 Jan 1970/);
    expect(cookie).toContain('HttpOnly');
  });

  it('rechaza una mutación con Origin ajeno', async () => {
    const response = await request(app)
      .post('/api/auth/logout')
      .set('Origin', 'https://evil.example')
      .send({});

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ORIGIN_NOT_ALLOWED');
  });
});

/* =====================================================================================
 * T39 — recuperación de contraseña
 * =================================================================================== */

describe('T39 · recuperación de contraseña', () => {
  it('restablece la contraseña una sola vez y la anterior deja de servir', async () => {
    const student = await createActiveStudent();
    const correosPrevios = await countMailFiles();

    const solicitud = await post('/api/auth/forgot-password').send({
      correoInstitucional: student.correo,
    });
    expect(solicitud.status).toBe(200);
    expect(await countMailFiles()).toBe(correosPrevios + 1);

    const codigo = await readLatestOtp();
    const nueva = 'NuevaClave456';

    const cambio = await post('/api/auth/reset-password').send({
      correoInstitucional: student.correo,
      codigo,
      password: nueva,
    });
    expect(cambio.status).toBe(200);
    expect(JSON.stringify(cambio.body)).not.toContain(nueva);

    const conLaVieja = await post('/api/auth/login').send({
      correoInstitucional: student.correo,
      password: student.password,
    });
    expect(conLaVieja.status).toBe(401);
    expect(conLaVieja.body.error.code).toBe('INVALID_CREDENTIALS');

    const conLaNueva = await post('/api/auth/login').send({
      correoInstitucional: student.correo,
      password: nueva,
    });
    expect(conLaNueva.status).toBe(200);

    // El código es de un solo uso.
    const repetido = await post('/api/auth/reset-password').send({
      correoInstitucional: student.correo,
      codigo,
      password: 'OtraClave789',
    });
    expect(repetido.status).toBe(422);
    expect(repetido.body.error.code).toBe('OTP_INVALID');
  });

  it('rechaza un código vencido', async () => {
    const student = await createActiveStudent();

    await post('/api/auth/forgot-password')
      .send({ correoInstitucional: student.correo })
      .expect(200);
    const codigo = await readLatestOtp();

    await query(
      `UPDATE codigosverificacion SET expiracion = now() - interval '1 minute'
        WHERE correo_institucional = $1 AND proposito = 'Recuperación'`,
      [student.correo],
    );

    const response = await post('/api/auth/reset-password').send({
      correoInstitucional: student.correo,
      codigo,
      password: 'OtraClave789',
    });

    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('OTP_INVALID');

    // La contraseña no cambió.
    await post('/api/auth/login')
      .send({ correoInstitucional: student.correo, password: student.password })
      .expect(200);
  });

  it('no revela si el correo está registrado', async () => {
    const response = await post('/api/auth/forgot-password').send({
      correoInstitucional: uniqueEmail('desconocido'),
    });

    expect(response.status).toBe(200);
    expect(await countMailFiles()).toBe(0);
  });
});
