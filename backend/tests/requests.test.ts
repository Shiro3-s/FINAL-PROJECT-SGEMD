import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { hashPassword } from '../src/utils/password.js';
import { adminSession, loginSession, type Session } from './api.js';
import { clearMailbox, uniqueDocument, uniqueEmail } from './helpers.js';

/**
 * T36 — bandeja única de solicitudes (FR-014, R38).
 *
 * Cada caso crea sus propias cuentas: la suite corre en paralelo contra la misma base y
 * los usuarios del seed (`estudiante.demo2`, en particular) son estado compartido que
 * otras suites también leen.
 */

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

let sequence = 0;

interface NewUser {
  id: number;
  correo: string;
  session: Session;
}

/** Alta por el administrador y contraseña conocida para poder iniciar sesión. */
async function newUser(
  admin: Session,
  overrides: Record<string, unknown> = {},
): Promise<NewUser> {
  const correo = uniqueEmail('solicitud');

  const response = await admin.post('/api/users').send({
    nombres: 'Solicitud',
    apellidos: 'Prueba',
    numeroDocumento: uniqueDocument(),
    correoInstitucional: correo,
    rolId: 2,
    tipoDocumentoId: 1,
    ...overrides,
  });
  expect(response.status).toBe(201);

  await query('UPDATE usuarios SET password = $2 WHERE correo_institucional = $1', [
    correo,
    await hashPassword('Demo1234'),
  ]);

  return {
    id: response.body.data.id as number,
    correo,
    session: await loginSession(correo),
  };
}

/** Estudiante `Activo` con un emprendimiento ya aprobado. */
async function studentWithApprovedEntrepreneurship(
  admin: Session,
  overrides: Record<string, unknown> = {},
): Promise<{ student: NewUser; emprendimientoId: number }> {
  const student = await newUser(admin, overrides);

  sequence += 1;
  const alta = await admin.post('/api/entrepreneurship').send({
    nombre: `Emprendimiento solicitud ${Date.now()}-${sequence}`,
    estudianteId: student.id,
    sectorId: 1,
    centroUniversitarioId: 1,
  });
  expect(alta.status).toBe(201);

  const id = alta.body.data.id as number;
  await admin.post(`/api/entrepreneurship/${id}/approve`).send({}).expect(200);

  return { student, emprendimientoId: id };
}

async function userRow(id: number) {
  const { rows } = await query<{ estado: string }>(
    'SELECT estado FROM usuarios WHERE id_usuarios = $1',
    [id],
  );
  return rows[0]!;
}

async function entrepreneurshipRow(id: number) {
  const { rows } = await query<{ es_paralelo: boolean; estado_aprobacion: string }>(
    `SELECT es_paralelo, estado_aprobacion
       FROM emprendimiento WHERE id_emprendimiento = $1`,
    [id],
  );
  return rows[0]!;
}

async function requestRow(id: number) {
  const { rows } = await query<{
    estado: string;
    motivo_rechazo: string | null;
    fecha_resolucion: Date | null;
    usuarios_id_resuelto_por: number | null;
  }>(
    `SELECT estado, motivo_rechazo, fecha_resolucion, usuarios_id_resuelto_por
       FROM solicitudes WHERE id_solicitud = $1`,
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
      WHERE entidad = 'solicitudes' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

async function notificationsOf(id: number) {
  const { rows } = await query<{ tipo: string; mensaje: string; url: string | null }>(
    `SELECT tipo, mensaje, url FROM notificaciones
      WHERE usuarios_id_usuarios = $1 ORDER BY id_notificaciones DESC`,
    [id],
  );
  return rows;
}

/** Notificación concreta de una solicitud: la coordinación recibe avisos de varias suites. */
async function notificationAbout(usuarioId: number, solicitudId: number) {
  const { rows } = await query<{ tipo: string; mensaje: string; url: string | null }>(
    `SELECT tipo, mensaje, url FROM notificaciones
      WHERE usuarios_id_usuarios = $1 AND tipo_objeto = 'solicitudes' AND objeto_id = $2
      ORDER BY id_notificaciones DESC`,
    [usuarioId, solicitudId],
  );
  return rows;
}

/* =====================================================================================
 * Desbloqueo de cuenta
 * =================================================================================== */

describe('T36 · desbloqueo de cuenta', () => {
  it('una cuenta Limitado pide el desbloqueo y la aprobación la activa una sola vez', async () => {
    const admin = await adminSession();
    const student = await newUser(admin, { estado: 'Limitado' });
    expect((await userRow(student.id)).estado).toBe('Limitado');

    const detalle = 'Cuenta limitada desde el registro';
    const alta = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle });

    expect(alta.status).toBe(201);
    expect(alta.body.data).toMatchObject({
      tipo: 'Desbloqueo',
      detalle,
      estado: 'Pendiente',
      motivoRechazo: null,
      fechaResolucion: null,
      emprendimiento: null,
      resueltoPor: null,
      solicitante: { id: student.id },
    });

    const id = alta.body.data.id as number;

    // La creación queda auditada y avisa a la coordinación.
    const creada = await auditRows(id, 'Solicitud creada');
    expect(creada).toHaveLength(1);
    expect(creada[0]!.usuarios_id_usuarios).toBe(student.id);
    expect(creada[0]!.valor_nuevo).toMatchObject({ tipo: 'Desbloqueo', estado: 'Pendiente' });

    const avisoAdmin = await notificationAbout(admin.id, id);
    expect(avisoAdmin[0]!).toMatchObject({ tipo: 'Solicitud', url: '/admin/solicitudes' });
    expect(avisoAdmin[0]!.mensaje).toMatch(/desbloqueo de cuenta/i);

    // La bandeja la muestra como pendiente.
    const bandeja = await admin.get('/api/requests').query({ estado: 'Pendiente', pageSize: 100 });
    expect(bandeja.status).toBe(200);
    expect(
      bandeja.body.data.items.some((item: { id: number }) => item.id === id),
    ).toBe(true);
    expect(bandeja.body.data.pendientes.Desbloqueo).toBeGreaterThanOrEqual(1);

    const aprobada = await admin.put(`/api/requests/${id}/approve`).send({});
    expect(aprobada.status).toBe(200);
    expect(aprobada.body.data).toMatchObject({
      id,
      estado: 'Aprobada',
      resueltoPor: { id: admin.id },
    });
    expect(aprobada.body.data.fechaResolucion).toEqual(expect.any(String));

    // Efecto de dominio: la cuenta quedó Activo.
    expect((await userRow(student.id)).estado).toBe('Activo');

    const row = await requestRow(id);
    expect(row.estado).toBe('Aprobada');
    expect(row.usuarios_id_resuelto_por).toBe(admin.id);
    expect(row.fecha_resolucion).not.toBeNull();

    // La transición de cuenta deja su propia auditoría, con el antes y el después.
    const transicion = await query<{
      valor_anterior: Record<string, unknown>;
      valor_nuevo: Record<string, unknown>;
    }>(
      `SELECT valor_anterior, valor_nuevo
         FROM auditoria_eventos
        WHERE entidad = 'usuarios' AND entidad_id = $1 AND accion = 'Cambio de estado de cuenta'
        ORDER BY id_auditoria DESC`,
      [student.id],
    );
    expect(transicion.rows[0]!.valor_anterior).toEqual({ estado: 'Limitado' });
    expect(transicion.rows[0]!.valor_nuevo).toEqual({ estado: 'Activo' });

    const resolucion = await auditRows(id, 'Solicitud aprobada');
    expect(resolucion).toHaveLength(1);
    expect(resolucion[0]!.valor_anterior).toMatchObject({ estado: 'Pendiente' });
    expect(resolucion[0]!.valor_nuevo).toMatchObject({ estado: 'Aprobada' });
    expect(resolucion[0]!.valor_nuevo!.efecto).toBe('Limitado → Activo');

    // Se notifica al solicitante.
    const avisoSolicitante = await notificationsOf(student.id);
    expect(avisoSolicitante[0]).toMatchObject({ tipo: 'Solicitud' });
    expect(avisoSolicitante[0]!.mensaje).toMatch(/aprobada/i);

    // Una segunda aprobación no vuelve a aplicar el efecto ni escribe auditoría.
    const repetida = await admin.put(`/api/requests/${id}/approve`).send({});
    expect(repetida.status).toBe(422);
    expect(repetida.body.error.code).toBe('REQUEST_ALREADY_RESOLVED');
    expect(await auditRows(id, 'Solicitud aprobada')).toHaveLength(1);
  });

  it('una cuenta Inactivo también puede pedir el desbloqueo y se reactiva', async () => {
    const admin = await adminSession();
    const student = await newUser(admin);

    await admin
      .patch(`/api/users/${student.id}/state`)
      .send({ estado: 'Inactivo' })
      .expect(200);
    expect((await userRow(student.id)).estado).toBe('Inactivo');

    // La sesión sigue siendo válida: el estado se lee de la fila en cada petición.
    const alta = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle: 'Inactividad prolongada' });
    expect(alta.status).toBe(201);

    const id = alta.body.data.id as number;
    await admin.put(`/api/requests/${id}/approve`).send({}).expect(200);

    expect((await userRow(student.id)).estado).toBe('Activo');
    expect((await requestRow(id)).estado).toBe('Aprobada');
  });

  it('una cuenta Activo no puede pedir un desbloqueo', async () => {
    const admin = await adminSession();
    const student = await newUser(admin);

    const response = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle: 'No aplica' });

    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('ACCOUNT_ALREADY_ACTIVE');
  });

  it('el desbloqueo no acepta un emprendimiento asociado', async () => {
    const admin = await adminSession();
    const student = await newUser(admin, { estado: 'Limitado' });

    const response = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', emprendimientoId: 1 });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.fields).toHaveProperty('emprendimientoId');
  });
});

/* =====================================================================================
 * Paralelo
 * =================================================================================== */

describe('T36 · emprendimiento paralelo', () => {
  it('la aprobación marca el emprendimiento como paralelo una sola vez', async () => {
    const admin = await adminSession();
    const { student, emprendimientoId } = await studentWithApprovedEntrepreneurship(admin);

    const alta = await student.session
      .post('/api/requests')
      .send({ tipo: 'Paralelo', emprendimientoId, detalle: 'Segundo proyecto' });
    expect(alta.status).toBe(201);
    expect(alta.body.data).toMatchObject({
      tipo: 'Paralelo',
      estado: 'Pendiente',
      emprendimiento: { id: emprendimientoId },
    });

    const id = alta.body.data.id as number;
    expect((await entrepreneurshipRow(emprendimientoId)).es_paralelo).toBe(false);

    const aprobada = await admin.put(`/api/requests/${id}/approve`).send({});
    expect(aprobada.status).toBe(200);
    expect(aprobada.body.data.estado).toBe('Aprobada');

    expect((await entrepreneurshipRow(emprendimientoId)).es_paralelo).toBe(true);

    const resolucion = await auditRows(id, 'Solicitud aprobada');
    expect(resolucion[0]!.valor_nuevo).toMatchObject({
      estado: 'Aprobada',
      efecto: 'esParalelo = TRUE',
    });

    // Idempotencia: la segunda aprobación no reaplica el efecto.
    const repetida = await admin.put(`/api/requests/${id}/approve`).send({});
    expect(repetida.status).toBe(422);
    expect(repetida.body.error.code).toBe('REQUEST_ALREADY_RESOLVED');
  });

  it('exige un emprendimiento propio y aprobado', async () => {
    const admin = await adminSession();
    const { student } = await studentWithApprovedEntrepreneurship(admin);

    // Sin emprendimiento.
    const sinEmprendimiento = await student.session.post('/api/requests').send({
      tipo: 'Paralelo',
      detalle: 'Sin referencia',
    });
    expect(sinEmprendimiento.status).toBe(400);
    expect(sinEmprendimiento.body.error.fields).toHaveProperty('emprendimientoId');

    // Un emprendimiento de otro estudiante, todavía en `Pendiente`.
    const ajeno = await newUser(admin);
    sequence += 1;
    const pendiente = await admin.post('/api/entrepreneurship').send({
      nombre: `Pendiente paralelo ${Date.now()}-${sequence}`,
      estudianteId: ajeno.id,
      sectorId: 1,
    });
    expect(pendiente.status).toBe(201);
    const pendienteId = pendiente.body.data.id as number;

    const noPropio = await student.session
      .post('/api/requests')
      .send({ tipo: 'Paralelo', emprendimientoId: pendienteId, detalle: 'Ajeno' });
    expect(noPropio.status).toBe(400);
    expect(noPropio.body.error.code).toBe('VALIDATION_ERROR');

    const noAprobado = await ajeno.session.post('/api/requests').send({
      tipo: 'Paralelo',
      emprendimientoId: pendienteId,
      detalle: 'Todavía sin aprobar',
    });
    expect(noAprobado.status).toBe(422);
    expect(noAprobado.body.error.code).toBe('ENTREPRENEURSHIP_NOT_APPROVED');
  });

  it('una cuenta Limitado no puede pedir un paralelo', async () => {
    const admin = await adminSession();
    const { student, emprendimientoId } = await studentWithApprovedEntrepreneurship(admin, {
      estado: 'Limitado',
    });

    const response = await student.session
      .post('/api/requests')
      .send({ tipo: 'Paralelo', emprendimientoId, detalle: 'No permitido' });

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });

  it('un docente no puede pedir un paralelo', async () => {
    const docente = await loginSession('docente.demo1@uniminuto.edu.co');

    const response = await docente
      .post('/api/requests')
      .send({ tipo: 'Paralelo', emprendimientoId: 1, detalle: 'No permitido' });

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ROLE_NOT_ALLOWED');
  });
});

/* =====================================================================================
 * Cita
 * =================================================================================== */

describe('T36 · cita de asesoría', () => {
  it('la aprobación crea la asesoría programada con docente y horario (P-19)', async () => {
    const admin = await adminSession();
    const { student, emprendimientoId } = await studentWithApprovedEntrepreneurship(admin);
    const docente = await newUser(admin, { rolId: 3 });

    const alta = await student.session.post('/api/requests').send({
      tipo: 'Cita',
      emprendimientoId,
      detalle: 'Prefiero el jueves en la mañana',
    });
    expect(alta.status).toBe(201);
    expect(alta.body.data).toMatchObject({ tipo: 'Cita', estado: 'Pendiente' });

    const id = alta.body.data.id as number;

    // Aprobar una cita sin docente ni horario no es posible: la asesoría nacería sin datos.
    const sinDatos = await admin.put(`/api/requests/${id}/approve`).send({});
    expect(sinDatos.status).toBe(400);
    expect(sinDatos.body.error.code).toBe('VALIDATION_ERROR');
    expect(sinDatos.body.error.fields).toHaveProperty('docenteId');
    expect((await requestRow(id)).estado).toBe('Pendiente');

    const aprobada = await admin.put(`/api/requests/${id}/approve`).send({
      docenteId: docente.id,
      tema: 'Validación de la propuesta de valor',
      fecha: '2026-12-03',
      horaInicio: '09:00',
      horaFin: '10:00',
      modalidadId: 2,
      lugarEnlace: 'https://meet.example.com/asesoria',
    });

    expect(aprobada.status).toBe(200);
    expect(aprobada.body.data).toMatchObject({
      id,
      estado: 'Aprobada',
      resueltoPor: { id: admin.id },
    });

    const { rows } = await query<{
      id_asesorias: number;
      estado: string;
      tema: string;
      usuarios_id_docentes: number;
      usuarios_id_usuarios: number;
      emprendimiento_id_emprendimiento: number;
      fecha: string;
      hora_inicio: string;
      hora_fin: string;
    }>(
      `SELECT a.id_asesorias, a.estado, a.tema, a.usuarios_id_docentes,
              a.usuarios_id_usuarios, a.emprendimiento_id_emprendimiento,
              to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
              to_char(fyh.hora_inicio, 'HH24:MI') AS hora_inicio,
              to_char(fyh.hora_fin, 'HH24:MI') AS hora_fin
         FROM asesorias a
         JOIN fecha_y_horarios fyh
           ON fyh.id_fecha_y_horarios = a.fecha_y_horarios_id_fecha_y_horarios
        WHERE a.emprendimiento_id_emprendimiento = $1`,
      [emprendimientoId],
    );

    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({
      estado: 'Programada',
      tema: 'Validación de la propuesta de valor',
      usuarios_id_docentes: docente.id,
      usuarios_id_usuarios: student.id,
      emprendimiento_id_emprendimiento: emprendimientoId,
      fecha: '2026-12-03',
      hora_inicio: '09:00',
      hora_fin: '10:00',
    });

    // La resolución deja su rastro y la creación de la asesoría, el suyo.
    const resolucion = await auditRows(id, 'Solicitud aprobada');
    expect(resolucion[0]!.valor_nuevo).toMatchObject({ estado: 'Aprobada' });
    expect(resolucion[0]!.valor_nuevo!.efecto).toMatch(/asesoría #\d+ creada \(Programada\)/);

    const altaAsesoria = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE entidad = 'asesorias' AND accion = 'Alta de asesoría' AND entidad_id = $1`,
      [rows[0]!.id_asesorias],
    );
    expect(Number(altaAsesoria.rows[0]!.total)).toBe(1);

    // Doble aprobación: no se crea una segunda asesoría.
    const repetida = await admin.put(`/api/requests/${id}/approve`).send({
      docenteId: docente.id,
      tema: 'Otra vez',
      fecha: '2026-12-04',
      horaInicio: '09:00',
      horaFin: '10:00',
    });
    expect(repetida.status).toBe(422);
    expect(repetida.body.error.code).toBe('REQUEST_ALREADY_RESOLVED');

    const total = await query<{ total: string }>(
      'SELECT COUNT(*)::text AS total FROM asesorias WHERE emprendimiento_id_emprendimiento = $1',
      [emprendimientoId],
    );
    expect(Number(total.rows[0]!.total)).toBe(1);
  });

  it('los datos de programación solo se aceptan en una cita', async () => {
    const admin = await adminSession();
    const student = await newUser(admin, { estado: 'Limitado' });

    const alta = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle: 'Solicito activación' });
    const id = alta.body.data.id as number;

    const response = await admin.put(`/api/requests/${id}/approve`).send({
      docenteId: 2,
      tema: 'No aplica',
      fecha: '2026-12-03',
      horaInicio: '09:00',
      horaFin: '10:00',
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect((await requestRow(id)).estado).toBe('Pendiente');
  });
});

/* =====================================================================================
 * Rechazo
 * =================================================================================== */

describe('T36 · rechazo de solicitudes', () => {
  it('exige motivo, lo guarda, notifica y no aplica el efecto', async () => {
    const admin = await adminSession();
    const student = await newUser(admin, { estado: 'Limitado' });

    const alta = await student.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle: 'Solicito activación' });
    const id = alta.body.data.id as number;

    const sinMotivo = await admin.put(`/api/requests/${id}/reject`).send({});
    expect(sinMotivo.status).toBe(400);
    expect(sinMotivo.body.error.code).toBe('VALIDATION_ERROR');
    expect(sinMotivo.body.error.fields).toHaveProperty('motivo');

    const vacio = await admin.put(`/api/requests/${id}/reject`).send({ motivo: '   ' });
    expect(vacio.status).toBe(400);

    const motivo = 'La cuenta no cumple los requisitos de activación';
    const response = await admin.put(`/api/requests/${id}/reject`).send({ motivo });

    expect(response.status).toBe(200);
    expect(response.body.data).toMatchObject({
      estado: 'Rechazada',
      motivoRechazo: motivo,
      resueltoPor: { id: admin.id },
    });

    const row = await requestRow(id);
    expect(row.estado).toBe('Rechazada');
    expect(row.motivo_rechazo).toBe(motivo);

    // El rechazo no activa la cuenta.
    expect((await userRow(student.id)).estado).toBe('Limitado');

    const resolucion = await auditRows(id, 'Solicitud rechazada');
    expect(resolucion[0]!.valor_nuevo).toMatchObject({ estado: 'Rechazada', motivo });

    const avisos = await notificationsOf(student.id);
    expect(avisos[0]!.mensaje).toContain(motivo);

    // Rechazar una solicitud ya resuelta también se rechaza.
    const repetido = await admin.put(`/api/requests/${id}/reject`).send({ motivo });
    expect(repetido.status).toBe(422);
    expect(repetido.body.error.code).toBe('REQUEST_ALREADY_RESOLVED');
  });
});

/* =====================================================================================
 * Bandeja, contadores y acceso
 * =================================================================================== */

describe('T36 · bandeja y acceso', () => {
  it('el contador de pendientes desglosa por tipo sobre toda la bandeja', async () => {
    const admin = await adminSession();
    const limitado = await newUser(admin, { estado: 'Limitado' });
    const { student, emprendimientoId } = await studentWithApprovedEntrepreneurship(admin);

    await limitado.session
      .post('/api/requests')
      .send({ tipo: 'Desbloqueo', detalle: 'Contador desbloqueo' })
      .expect(201);
    await student.session
      .post('/api/requests')
      .send({ tipo: 'Paralelo', emprendimientoId, detalle: 'Contador paralelo' })
      .expect(201);
    await student.session
      .post('/api/requests')
      .send({ tipo: 'Cita', emprendimientoId, detalle: 'Contador cita' })
      .expect(201);

    const response = await admin.get('/api/requests').query({ pageSize: 100 });
    expect(response.status).toBe(200);

    const { pendientes } = response.body.data as {
      pendientes: { total: number; Desbloqueo: number; Paralelo: number; Cita: number };
    };
    expect(pendientes.Desbloqueo).toBeGreaterThanOrEqual(1);
    expect(pendientes.Paralelo).toBeGreaterThanOrEqual(1);
    expect(pendientes.Cita).toBeGreaterThanOrEqual(1);
    expect(pendientes.total).toBe(
      pendientes.Desbloqueo + pendientes.Paralelo + pendientes.Cita,
    );

    // El filtro por tipo no altera el contador global.
    const soloCitas = await admin.get('/api/requests').query({ tipo: 'Cita', pageSize: 100 });
    expect(
      soloCitas.body.data.items.every(
        (item: { tipo: string }) => item.tipo === 'Cita',
      ),
    ).toBe(true);
    expect(soloCitas.body.data.pendientes.total).toBe(pendientes.total);
  });

  it('solo el administrador ve y resuelve la bandeja', async () => {
    const admin = await adminSession();
    const { student } = await studentWithApprovedEntrepreneurship(admin);
    const docente = await loginSession('docente.demo1@uniminuto.edu.co');

    for (const session of [student.session, docente]) {
      const lista = await session.get('/api/requests');
      expect(lista.status).toBe(403);
      expect(lista.body.error.code).toBe('ROLE_NOT_ALLOWED');

      const detalle = await session.get('/api/requests/1');
      expect(detalle.status).toBe(403);

      const aprobar = await session.put('/api/requests/1/approve').send({});
      expect(aprobar.status).toBe(403);

      const rechazar = await session.put('/api/requests/1/reject').send({ motivo: 'No' });
      expect(rechazar.status).toBe(403);
    }
  });

  it('un id no numérico da 400, uno inexistente 404 y un filtro desconocido 400', async () => {
    const admin = await adminSession();

    const invalido = await admin.get('/api/requests/abc');
    expect(invalido.status).toBe(400);
    expect(invalido.body.error.code).toBe('VALIDATION_ERROR');

    const inexistente = await admin.get('/api/requests/999999');
    expect(inexistente.status).toBe(404);
    expect(inexistente.body.error.code).toBe('NOT_FOUND');

    const filtro = await admin.get('/api/requests').query({ includeDeleted: 'true' });
    expect(filtro.status).toBe(400);
    expect(filtro.body.error.code).toBe('VALIDATION_ERROR');

    const orden = await admin.get('/api/requests').query({ sort: 'password' });
    expect(orden.status).toBe(400);

    const tamano = await admin.get('/api/requests').query({ pageSize: 500 });
    expect(tamano.status).toBe(400);
  });

  it('rechaza campos desconocidos al crear una solicitud', async () => {
    const admin = await adminSession();
    const student = await newUser(admin, { estado: 'Limitado' });

    const response = await student.session.post('/api/requests').send({
      tipo: 'Desbloqueo',
      detalle: 'Con campo de más',
      usuariosId: admin.id,
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});
