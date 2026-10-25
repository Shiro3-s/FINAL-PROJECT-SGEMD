import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import {
  clearMailbox,
  countMailFiles,
  readLatestOtp,
  uniqueDocument,
  uniqueEmail,
} from './helpers.js';
import { loginSession, post } from './api.js';

interface CreateOverrides {
  nombres?: string;
  apellidos?: string;
  numeroDocumento?: string;
  correoInstitucional?: string;
  rolId?: number;
  tipoDocumentoId?: number;
  estado?: string;
  [key: string]: unknown;
}

function createPayload(overrides: CreateOverrides = {}) {
  return {
    nombres: 'Cuenta',
    apellidos: 'De Prueba',
    numeroDocumento: uniqueDocument(),
    correoInstitucional: uniqueEmail('alta'),
    rolId: 2,
    tipoDocumentoId: 1,
    ...overrides,
  };
}

async function createUser(admin: Session, overrides: CreateOverrides = {}) {
  const payload = createPayload(overrides);
  const response = await admin.post('/api/users').send(payload);
  return { payload, response };
}

async function userRow(id: number) {
  const { rows } = await query<{
    codigo: string;
    estado: string;
    verificado: boolean;
    roles_id_roles: number;
    password: string;
    fecha_eliminacion: Date | null;
    correo_institucional: string;
  }>(
    `SELECT codigo, estado, verificado, roles_id_roles, password, fecha_eliminacion,
            correo_institucional
       FROM usuarios WHERE id_usuarios = $1`,
    [id],
  );
  return rows[0]!;
}

async function auditRows(entidadId: number, accion: string) {
  const { rows } = await query<{
    valor_anterior: Record<string, unknown> | null;
    valor_nuevo: Record<string, unknown> | null;
    usuarios_id_usuarios: number | null;
  }>(
    `SELECT valor_anterior, valor_nuevo, usuarios_id_usuarios
       FROM auditoria_eventos
      WHERE entidad = 'usuarios' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

async function notificationsOf(id: number) {
  const { rows } = await query<{ tipo: string; mensaje: string; leida: boolean }>(
    `SELECT tipo, mensaje, leida
       FROM notificaciones WHERE usuarios_id_usuarios = $1
      ORDER BY id_notificaciones DESC`,
    [id],
  );
  return rows;
}

/** Registro público completo: queda `Limitado` y verificado, con contraseña conocida. */
async function registerStudent() {
  const payload = {
    nombres: 'Estudiante',
    apellidos: 'Registrado',
    tipoDocumentoId: 1,
    numeroDocumento: uniqueDocument(),
    correoInstitucional: uniqueEmail('registrado'),
    password: 'Secreta123',
    aceptaTratamiento: true,
  };

  const response = await post('/api/auth/register').send(payload);
  expect(response.status).toBe(201);

  const codigo = await readLatestOtp();
  await post('/api/auth/verify')
    .send({ correoInstitucional: payload.correoInstitucional, codigo })
    .expect(200);

  return { id: response.body.data.id as number, ...payload };
}

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

/* =====================================================================================
 * T06 — alta de estudiantes y docentes
 * =================================================================================== */

describe('T06 · alta de cuentas por el administrador', () => {
  it('crea un estudiante con código de 6 dígitos, verificado y Activo por defecto', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { payload, response } = await createUser(admin);

    expect(response.status).toBe(201);
    expect(response.body.data).toMatchObject({
      correoInstitucional: payload.correoInstitucional,
      verificado: true,
      estado: 'Activo',
      rol: { id: 2, nombre: 'Estudiante' },
    });
    expect(response.body.data.codigo).toMatch(/^\d{6}$/);
    expect(response.body.data).not.toHaveProperty('password');

    const row = await userRow(response.body.data.id);
    expect(row.verificado).toBe(true);
    expect(row.roles_id_roles).toBe(2);
    // La contraseña inicial es aleatoria e inservible, y nunca viaja en la respuesta.
    expect(row.password).toMatch(/^\$2[aby]\$10\$/);
    expect(JSON.stringify(response.body)).not.toContain(row.password);

    // El alta queda auditada con el actor.
    const audits = await auditRows(response.body.data.id, 'Alta de usuario');
    expect(audits).toHaveLength(1);
    expect(audits[0]!.usuarios_id_usuarios).toBe(admin.id);
    expect(audits[0]!.valor_nuevo).toMatchObject({ rolId: 2, estado: 'Activo' });

    // La invitación sale por el transporte de correo con un código de 8 dígitos.
    expect(await countMailFiles()).toBe(1);
    expect(await readLatestOtp()).toMatch(/^\d{8}$/);
  });

  it('crea un docente con código secuencial DOC-###', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const primero = await createUser(admin, { rolId: 3, nombres: 'Docente' });
    const segundo = await createUser(admin, { rolId: 3, nombres: 'Docente' });

    expect(primero.response.status).toBe(201);
    expect(primero.response.body.data.rol.id).toBe(3);

    // El código es secuencial, pero el valor absoluto depende de cuántos docentes haya
    // creado la suite antes: se comprueba el formato y el incremento, no un número fijo.
    const firstCode = primero.response.body.data.codigo as string;
    const secondCode = segundo.response.body.data.codigo as string;
    expect(firstCode).toMatch(/^DOC-\d{3}$/);
    expect(secondCode).toMatch(/^DOC-\d{3}$/);
    expect(Number(secondCode.slice(4))).toBe(Number(firstCode.slice(4)) + 1);
  });

  it('rechaza un correo institucional repetido con 409', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.post('/api/users').send(
      createPayload({ correoInstitucional: 'estudiante.demo1@uniminuto.edu.co' }),
    );

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('EMAIL_TAKEN');
    expect(response.body.error.fields).toHaveProperty('correoInstitucional');
  });

  it('rechaza un documento repetido con 409', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.post('/api/users').send(
      createPayload({ numeroDocumento: '900000004' }),
    );

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('DOCUMENT_TAKEN');
    expect(response.body.error.fields).toHaveProperty('numeroDocumento');
  });

  it('solo permite los roles Estudiante y Docente', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    for (const rolId of [1, 4, 99]) {
      const response = await admin.post('/api/users').send(createPayload({ rolId }));
      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    }
  });

  it('rechaza un dominio no institucional', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.post('/api/users').send(
      createPayload({ correoInstitucional: uniqueEmail('externo').replace('uniminuto.edu.co', 'gmail.com') }),
    );

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('EMAIL_DOMAIN_NOT_ALLOWED');
  });

  it('rechaza un catálogo que no existe', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.post('/api/users').send(
      createPayload({ programaAcademicoId: 9999 }),
    );

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.fields).toHaveProperty('programaAcademicoId');
  });

  it('rechaza los campos que el servidor decide (código, contraseña, verificado)', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    for (const extra of [{ codigo: 'DOC-999' }, { password: 'Otra12345' }, { verificado: false }]) {
      const response = await admin.post('/api/users').send({ ...createPayload(), ...extra });
      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    }
  });

  it('un docente y un estudiante no pueden crear ni listar cuentas', async () => {
    const docente = await loginSession('docente.demo1@uniminuto.edu.co');
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    for (const session of [docente, estudiante]) {
      const alta = await session.post('/api/users').send(createPayload());
      expect(alta.status).toBe(403);
      expect(alta.body.error.code).toBe('ROLE_NOT_ALLOWED');

      const listado = await session.get('/api/users');
      expect(listado.status).toBe(403);
      expect(listado.body.error.code).toBe('ROLE_NOT_ALLOWED');
    }
  });

  it('una cuenta de coordinación Limitado no puede gestionar usuarios', async () => {
    // No hay forma de crear un administrador desde la API (R33): se siembra uno.
    const { hashPassword } = await import('../src/utils/password.js');
    const correo = uniqueEmail('admin.limitado');

    await query(
      `INSERT INTO usuarios
         (codigo, nombres, apellidos, numero_documento, correo_institucional, password,
          verificado, estado, roles_id_roles, tipo_documentos_id_tipo_documentos)
       VALUES ('ADM-900', 'Coordinación', 'Limitada', $1, $2, $3, TRUE, 'Limitado', 1, 1)`,
      [uniqueDocument(), correo, await hashPassword('Demo1234')],
    );

    const limitado = await loginSession(correo);

    const listado = await limitado.get('/api/users');
    expect(listado.status).toBe(403);
    expect(listado.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');

    const alta = await limitado.post('/api/users').send(createPayload());
    expect(alta.status).toBe(403);
    expect(alta.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });
});

/* =====================================================================================
 * T13 — ciclo de vida de la cuenta
 * =================================================================================== */

describe('T13 · ciclo de vida de la cuenta', () => {
  it('el administrador valida Limitado → Activo y la auditoría guarda ambos valores', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { response: alta } = await createUser(admin, { estado: 'Limitado' });
    const id = alta.body.data.id as number;

    const correosAntes = await countMailFiles();

    const response = await admin.post(`/api/users/${id}/validate`).send({});

    expect(response.status).toBe(200);
    expect(response.body.data.estado).toBe('Activo');
    expect((await userRow(id)).estado).toBe('Activo');

    const audits = await auditRows(id, 'Cambio de estado de cuenta');
    expect(audits).toHaveLength(1);
    expect(audits[0]!.valor_anterior).toEqual({ estado: 'Limitado' });
    expect(audits[0]!.valor_nuevo).toEqual({ estado: 'Activo' });
    expect(audits[0]!.usuarios_id_usuarios).toBe(admin.id);

    // Notificación en la misma transacción y correo de bienvenida después.
    const avisos = await notificationsOf(id);
    expect(avisos[0]).toMatchObject({ tipo: 'Sistema', leida: false });
    expect(avisos[0]!.mensaje).toMatch(/activada/i);
    expect(await countMailFiles()).toBe(correosAntes + 1);
  });

  it('Activo → Inactivo y de vuelta con reactivate', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { response: alta } = await createUser(admin);
    const id = alta.body.data.id as number;

    const baja = await admin.patch(`/api/users/${id}/state`).send({ estado: 'Inactivo' });
    expect(baja.status).toBe(200);
    expect(baja.body.data.estado).toBe('Inactivo');

    const vuelta = await admin.post(`/api/users/${id}/reactivate`).send({});
    expect(vuelta.status).toBe(200);
    expect(vuelta.body.data.estado).toBe('Activo');

    expect(await auditRows(id, 'Cambio de estado de cuenta')).toHaveLength(2);
  });

  it('rechaza las transiciones que no están en el ciclo de vida', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const { response: activo } = await createUser(admin);
    const { response: limitado } = await createUser(admin, { estado: 'Limitado' });

    // Activo → Limitado: el prototipo lo ofrece en el selector, el master no lo permite.
    const degradar = await admin
      .patch(`/api/users/${activo.body.data.id}/state`)
      .send({ estado: 'Limitado' });
    expect(degradar.status).toBe(422);
    expect(degradar.body.error.code).toBe('INVALID_STATE_TRANSITION');

    // Limitado → Inactivo tampoco existe.
    const saltar = await admin
      .patch(`/api/users/${limitado.body.data.id}/state`)
      .send({ estado: 'Inactivo' });
    expect(saltar.status).toBe(422);
    expect(saltar.body.error.code).toBe('INVALID_STATE_TRANSITION');

    // Repetir el estado actual no es una transición.
    const repetir = await admin.post(`/api/users/${activo.body.data.id}/validate`).send({});
    expect(repetir.status).toBe(422);
    expect(repetir.body.error.code).toBe('INVALID_STATE_TRANSITION');
  });

  it('validate solo aplica a Limitado y reactivate solo a Inactivo', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { response: activo } = await createUser(admin);
    const id = activo.body.data.id as number;

    const validarActivo = await admin.post(`/api/users/${id}/validate`).send({});
    expect(validarActivo.status).toBe(422);

    const reactivarActivo = await admin.post(`/api/users/${id}/reactivate`).send({});
    expect(reactivarActivo.status).toBe(422);
    expect(reactivarActivo.body.error.code).toBe('INVALID_STATE_TRANSITION');
  });

  it('un estudiante no puede cambiar su estado ni validarse a sí mismo', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    const estado = await estudiante
      .patch(`/api/users/${estudiante.id}/state`)
      .send({ estado: 'Activo' });
    expect(estado.status).toBe(403);
    expect(estado.body.error.code).toBe('ROLE_NOT_ALLOWED');

    const validar = await estudiante.post(`/api/users/${estudiante.id}/validate`).send({});
    expect(validar.status).toBe(403);

    const editar = await estudiante
      .put(`/api/users/${estudiante.id}`)
      .send({ nombres: 'Otro' });
    expect(editar.status).toBe(403);
  });

  it('nadie cambia el estado de su propia cuenta', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin
      .patch(`/api/users/${admin.id}/state`)
      .send({ estado: 'Inactivo' });

    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('SELF_STATE_CHANGE_NOT_ALLOWED');
    expect((await userRow(admin.id)).estado).toBe('Activo');
  });

  it('el rechazo exige motivo, deja la cuenta Limitado y notifica', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { response: alta } = await createUser(admin, { estado: 'Limitado' });
    const id = alta.body.data.id as number;

    const sinMotivo = await admin.post(`/api/users/${id}/reject`).send({});
    expect(sinMotivo.status).toBe(400);
    expect(sinMotivo.body.error.code).toBe('VALIDATION_ERROR');

    const motivo = 'La asesoría inicial no se realizó';
    const response = await admin.post(`/api/users/${id}/reject`).send({ motivo });

    expect(response.status).toBe(200);
    expect((await userRow(id)).estado).toBe('Limitado');

    const audits = await auditRows(id, 'Rechazo de activación');
    expect(audits[0]!.valor_nuevo).toMatchObject({ estado: 'Limitado', motivo });

    const avisos = await notificationsOf(id);
    expect(avisos[0]!.mensaje).toContain(motivo);

    // Una cuenta que ya no está Limitado no se puede rechazar.
    await admin.post(`/api/users/${id}/validate`).send({}).expect(200);
    const tarde = await admin.post(`/api/users/${id}/reject`).send({ motivo });
    expect(tarde.status).toBe(422);
  });
});

/* =====================================================================================
 * Baja lógica
 * =================================================================================== */

describe('baja lógica', () => {
  it('marca fecha_eliminacion, sale de los listados y ya no permite iniciar sesión', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const student = await registerStudent();

    const antes = await admin.get('/api/users').query({ q: student.correoInstitucional });
    expect(antes.body.data.total).toBe(1);

    const response = await admin.del(`/api/users/${student.id}`);
    expect(response.status).toBe(200);

    const row = await userRow(student.id);
    expect(row.fecha_eliminacion).not.toBeNull();

    const despues = await admin.get('/api/users').query({ q: student.correoInstitucional });
    expect(despues.body.data.total).toBe(0);

    const detalle = await admin.get(`/api/users/${student.id}`);
    expect(detalle.status).toBe(404);

    const login = await post('/api/auth/login').send({
      correoInstitucional: student.correoInstitucional,
      password: student.password,
    });
    expect(login.status).toBe(401);
    expect(login.body.error.code).toBe('INVALID_CREDENTIALS');

    const audits = await auditRows(student.id, 'Baja lógica de usuario');
    expect(audits).toHaveLength(1);
    expect(audits[0]!.usuarios_id_usuarios).toBe(admin.id);
  });

  it('no permite darse de baja a sí mismo ni a un id inexistente', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const propio = await admin.del(`/api/users/${admin.id}`);
    expect(propio.status).toBe(422);
    expect(propio.body.error.code).toBe('SELF_DELETE_NOT_ALLOWED');

    const inexistente = await admin.del('/api/users/999999');
    expect(inexistente.status).toBe(404);
    expect(inexistente.body.error.code).toBe('NOT_FOUND');
  });
});

/* =====================================================================================
 * Perfil y edición
 * =================================================================================== */

describe('perfil y edición', () => {
  it('un estudiante solo puede leer su propia ficha: otro id responde 404', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    const propio = await estudiante.get(`/api/users/${estudiante.id}`);
    expect(propio.status).toBe(200);
    expect(propio.body.data.id).toBe(estudiante.id);
    expect(propio.body.data).not.toHaveProperty('password');

    // El id de otro estudiante existe, pero fuera de alcance se responde 404 (NFR-002).
    const { rows } = await query<{ id_usuarios: number }>(
      `SELECT id_usuarios FROM usuarios WHERE correo_institucional = 'estudiante.demo2@uniminuto.edu.co'`,
    );
    const ajeno = await estudiante.get(`/api/users/${rows[0]!.id_usuarios}`);
    expect(ajeno.status).toBe(404);
    expect(ajeno.body.error.code).toBe('NOT_FOUND');
  });

  it('el administrador lee cualquier ficha y un id no numérico da 400', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.get('/api/users/1');
    expect(response.status).toBe(200);
    expect(response.body.data.rol.id).toBe(1);

    const invalido = await admin.get('/api/users/abc');
    expect(invalido.status).toBe(400);
    expect(invalido.body.error.code).toBe('VALIDATION_ERROR');

    const inexistente = await admin.get('/api/users/999999');
    expect(inexistente.status).toBe(404);
  });

  it('PUT /users/me actualiza nombres y datos académicos', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    const response = await estudiante.put('/api/users/me').send({
      nombres: 'Nombre Editado',
      nivelAcademico: 'Posgrado',
      programaAcademicoId: 1,
    });

    expect(response.status).toBe(200);
    expect(response.body.data).toMatchObject({
      nombres: 'Nombre Editado',
      nivelAcademico: 'Posgrado',
      programaAcademicoId: 1,
    });

    const audit = await auditRows(estudiante.id, 'Edición de usuario');
    expect(audit[0]!.valor_anterior).toMatchObject({ nombres: 'Estudiante' });
    expect(audit[0]!.valor_nuevo).toMatchObject({ nombres: 'Nombre Editado' });
  });

  it('PUT /users/me no permite tocar correo, documento, rol ni estado', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    for (const extra of [
      { correoInstitucional: uniqueEmail('cambio') },
      { numeroDocumento: uniqueDocument() },
      { tipoDocumentoId: 2 },
      { rolId: 1 },
      { estado: 'Activo' },
      { codigo: '000000' },
    ]) {
      const response = await estudiante.put('/api/users/me').send(extra);
      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    }
  });

  it('el administrador edita a otro usuario y valida la unicidad', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const { response: alta } = await createUser(admin);
    const id = alta.body.data.id as number;

    const response = await admin.put(`/api/users/${id}`).send({
      nombres: 'Corregido',
      correoInstitucional: uniqueEmail('corregido'),
    });
    expect(response.status).toBe(200);
    expect(response.body.data.nombres).toBe('Corregido');

    const duplicado = await admin.put(`/api/users/${id}`).send({
      correoInstitucional: 'docente.demo1@uniminuto.edu.co',
    });
    expect(duplicado.status).toBe(409);
    expect(duplicado.body.error.code).toBe('EMAIL_TAKEN');

    // El rol no se cambia por esta vía: requiere una operación propia (P-18).
    const rol = await admin.put(`/api/users/${id}`).send({ rolId: 3 });
    expect(rol.status).toBe(400);
    expect(rol.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('una edición sin campos se rechaza', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const response = await admin.put('/api/users/1').send({});
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});

/* =====================================================================================
 * Listados, paginación y filtros
 * =================================================================================== */

describe('listados', () => {
  it('pagina y devuelve el total real', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const response = await admin.get('/api/users').query({ page: 1, pageSize: 2 });

    expect(response.status).toBe(200);
    expect(response.body.data.items).toHaveLength(2);
    expect(response.body.data.page).toBe(1);
    expect(response.body.data.pageSize).toBe(2);
    expect(response.body.data.total).toBeGreaterThanOrEqual(5);

    const segunda = await admin.get('/api/users').query({ page: 2, pageSize: 2 });
    expect(segunda.body.data.items).toHaveLength(2);
    const ids = new Set([
      ...response.body.data.items.map((item: { id: number }) => item.id),
      ...segunda.body.data.items.map((item: { id: number }) => item.id),
    ]);
    expect(ids.size).toBe(4);
  });

  it('filtra por rol, estado y texto', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const estudiantes = await admin.get('/api/users').query({ rol: 2, pageSize: 100 });
    expect(estudiantes.status).toBe(200);
    expect(estudiantes.body.data.items.length).toBeGreaterThan(0);
    expect(
      estudiantes.body.data.items.every((item: { rol: { id: number } }) => item.rol.id === 2),
    ).toBe(true);

    const inactivos = await admin.get('/api/users').query({ estado: 'Inactivo' });
    expect(
      inactivos.body.data.items.every(
        (item: { estado: string }) => item.estado === 'Inactivo',
      ),
    ).toBe(true);

    const porCorreo = await admin
      .get('/api/users')
      .query({ q: 'docente.demo1@uniminuto.edu.co' });
    expect(porCorreo.body.data.total).toBe(1);
    expect(porCorreo.body.data.items[0].rol.id).toBe(3);
  });

  it('/users/students y /users/teachers fijan el rol aunque se envíe otro', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const estudiantes = await admin.get('/api/users/students').query({ rol: 3, pageSize: 100 });
    expect(estudiantes.status).toBe(200);
    expect(
      estudiantes.body.data.items.every((item: { rol: { id: number } }) => item.rol.id === 2),
    ).toBe(true);

    const docentes = await admin.get('/api/users/teachers').query({ pageSize: 100 });
    expect(
      docentes.body.data.items.every((item: { rol: { id: number } }) => item.rol.id === 3),
    ).toBe(true);
  });

  it('rechaza parámetros de consulta desconocidos o fuera de rango', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');

    const orden = await admin.get('/api/users').query({ sort: 'password' });
    expect(orden.status).toBe(400);
    expect(orden.body.error.code).toBe('VALIDATION_ERROR');

    const tamano = await admin.get('/api/users').query({ pageSize: 500 });
    expect(tamano.status).toBe(400);

    const extra = await admin.get('/api/users').query({ includeDeleted: 'true' });
    expect(extra.status).toBe(400);
  });
});
