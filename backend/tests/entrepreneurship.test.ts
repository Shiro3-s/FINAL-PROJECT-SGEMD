import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { hashPassword } from '../src/utils/password.js';
import { adminSession, loginSession, type Session } from './api.js';
import { clearMailbox, uniqueDocument, uniqueEmail } from './helpers.js';

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

let sequence = 0;
function nextName(): string {
  sequence += 1;
  return `Emprendimiento ${Date.now()}-${sequence}`;
}

interface NewUser {
  id: number;
  correo: string;
}

/** Alta de estudiante por el administrador, con contraseña conocida para iniciar sesión. */
async function newStudent(
  admin: Session,
  overrides: Record<string, unknown> = {},
): Promise<NewUser> {
  const correo = uniqueEmail('emp');

  const response = await admin.post('/api/users').send({
    nombres: 'Estudiante',
    apellidos: 'Emprendedor',
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

  return { id: response.body.data.id as number, correo };
}

function payload(estudianteId: number, overrides: Record<string, unknown> = {}) {
  return {
    nombre: nextName(),
    descripcion: 'Descripción de prueba',
    estudianteId,
    sectorId: 1,
    centroUniversitarioId: 1,
    ...overrides,
  };
}

async function createFor(admin: Session, estudianteId: number, overrides = {}) {
  const body = payload(estudianteId, overrides);
  const response = await admin.post('/api/entrepreneurship').send(body);
  return { body, response };
}

async function entrepreneurshipRow(id: number) {
  const { rows } = await query<{
    codigo: string;
    estado_aprobacion: string;
    motivo_rechazo: string | null;
    es_paralelo: boolean;
    avance: number;
    fecha_eliminacion: Date | null;
  }>(
    `SELECT codigo, estado_aprobacion, motivo_rechazo, es_paralelo, avance, fecha_eliminacion
       FROM emprendimiento WHERE id_emprendimiento = $1`,
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
      WHERE entidad = 'emprendimiento' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

async function notificationsOf(id: number) {
  const { rows } = await query<{ tipo: string; mensaje: string }>(
    `SELECT tipo, mensaje FROM notificaciones
      WHERE usuarios_id_usuarios = $1 ORDER BY id_notificaciones DESC`,
    [id],
  );
  return rows;
}

/* =====================================================================================
 * T11 — alta en Pendiente, aprobación exclusiva del admin y paralelos
 * =================================================================================== */

describe('T11 · alta y aprobación', () => {
  it('el administrador crea en Pendiente, con la etapa inicial y avance 0', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);
    const { body, response } = await createFor(admin, student.id);

    expect(response.status).toBe(201);
    expect(response.body.data).toMatchObject({
      nombre: body.nombre,
      descripcion: 'Descripción de prueba',
      estadoAprobacion: 'Pendiente',
      motivoRechazo: null,
      esParalelo: false,
      avance: 0,
      etapa: { id: 1, nombre: 'FASE 1 - Ideación' },
      sector: { id: 1, nombre: 'Alimentos' },
      centroUniversitario: { id: 1, nombre: 'Sede Norte' },
      estudiante: { id: student.id, correoInstitucional: student.correo },
    });
    expect(response.body.data.codigo).toMatch(/^EMP-\d{3}$/);

    const audits = await auditRows(response.body.data.id, 'Alta de emprendimiento');
    expect(audits).toHaveLength(1);
    expect(audits[0]!.usuarios_id_usuarios).toBe(admin.id);
    expect(audits[0]!.valor_nuevo).toMatchObject({
      estadoAprobacion: 'Pendiente',
      esParalelo: false,
      estudianteId: student.id,
    });

    const avisos = await notificationsOf(student.id);
    expect(avisos[0]).toMatchObject({ tipo: 'Sistema' });
    expect(avisos[0]!.mensaje).toMatch(/pendiente de aprobación/i);
  });

  it('solo el administrador aprueba; la aprobación audita y notifica', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);
    const { response: alta } = await createFor(admin, student.id);
    const id = alta.body.data.id as number;

    const estudiante = await loginSession(student.correo);
    const negado = await estudiante.post(`/api/entrepreneurship/${id}/approve`).send({});
    expect(negado.status).toBe(403);
    expect(negado.body.error.code).toBe('ROLE_NOT_ALLOWED');

    const docente = await loginSession('docente.demo1@uniminuto.edu.co');
    const negadoDocente = await docente.post(`/api/entrepreneurship/${id}/approve`).send({});
    expect(negadoDocente.status).toBe(403);

    const response = await admin.post(`/api/entrepreneurship/${id}/approve`).send({});
    expect(response.status).toBe(200);
    expect(response.body.data.estadoAprobacion).toBe('Aprobado');
    expect((await entrepreneurshipRow(id)).estado_aprobacion).toBe('Aprobado');

    const audits = await auditRows(id, 'Aprobación de emprendimiento');
    expect(audits).toHaveLength(1);
    expect(audits[0]!.valor_anterior).toEqual({ estadoAprobacion: 'Pendiente' });
    expect(audits[0]!.valor_nuevo).toEqual({ estadoAprobacion: 'Aprobado' });
    expect(audits[0]!.usuarios_id_usuarios).toBe(admin.id);

    const avisos = await notificationsOf(student.id);
    expect(avisos[0]!.mensaje).toMatch(/aprobado/i);
  });

  it('no se aprueba dos veces ni se aprueba un rechazado', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);
    const { response: alta } = await createFor(admin, student.id);
    const id = alta.body.data.id as number;

    await admin.post(`/api/entrepreneurship/${id}/approve`).send({}).expect(200);

    const otra = await admin.post(`/api/entrepreneurship/${id}/approve`).send({});
    expect(otra.status).toBe(422);
    expect(otra.body.error.code).toBe('INVALID_APPROVAL_STATE');
    expect(await auditRows(id, 'Aprobación de emprendimiento')).toHaveLength(1);

    // Un emprendimiento rechazado no se puede aprobar después.
    const { response: segundo } = await createFor(admin, student.id, { esParalelo: true });
    const idSegundo = segundo.body.data.id as number;
    await admin
      .post(`/api/entrepreneurship/${idSegundo}/reject`)
      .send({ motivo: 'No cumple los criterios' })
      .expect(200);

    const tarde = await admin.post(`/api/entrepreneurship/${idSegundo}/approve`).send({});
    expect(tarde.status).toBe(422);
    expect(tarde.body.error.code).toBe('INVALID_APPROVAL_STATE');
  });

  it('un segundo emprendimiento exige autorización de paralelo y respeta el tope', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);

    const primero = await createFor(admin, student.id);
    expect(primero.response.status).toBe(201);
    expect(primero.response.body.data.esParalelo).toBe(false);

    const sinParalelo = await createFor(admin, student.id);
    expect(sinParalelo.response.status).toBe(422);
    expect(sinParalelo.response.body.error.code).toBe('PARALLEL_REQUIRED');

    const segundo = await createFor(admin, student.id, { esParalelo: true });
    expect(segundo.response.status).toBe(201);
    expect(segundo.response.body.data.esParalelo).toBe(true);

    // `paralelos_maximos` = 1 en el seed (D5).
    const tercero = await createFor(admin, student.id, { esParalelo: true });
    expect(tercero.response.status).toBe(422);
    expect(tercero.response.body.error.code).toBe('PARALLEL_LIMIT_REACHED');
  });

  it('el primer emprendimiento no puede registrarse como paralelo', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);

    const { response } = await createFor(admin, student.id, { esParalelo: true });
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('NOT_A_PARALLEL');
  });

  it('un emprendimiento rechazado no ocupa cupo', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);

    const { response: alta } = await createFor(admin, student.id);
    await admin
      .post(`/api/entrepreneurship/${alta.body.data.id}/reject`)
      .send({ motivo: 'No cumple los criterios' })
      .expect(200);

    const segundo = await createFor(admin, student.id);
    expect(segundo.response.status).toBe(201);
    expect(segundo.response.body.data.esParalelo).toBe(false);
  });
});

/* =====================================================================================
 * T12 — rechazo con motivo
 * =================================================================================== */

describe('T12 · rechazo con motivo', () => {
  it('sin motivo 400; con motivo lo guarda y notifica al estudiante', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);
    const { response: alta } = await createFor(admin, student.id);
    const id = alta.body.data.id as number;

    const sinMotivo = await admin.post(`/api/entrepreneurship/${id}/reject`).send({});
    expect(sinMotivo.status).toBe(400);
    expect(sinMotivo.body.error.code).toBe('VALIDATION_ERROR');
    expect(sinMotivo.body.error.fields).toHaveProperty('motivo');

    const vacio = await admin.post(`/api/entrepreneurship/${id}/reject`).send({ motivo: '   ' });
    expect(vacio.status).toBe(400);

    const motivo = 'La propuesta no está suficientemente definida';
    const response = await admin.post(`/api/entrepreneurship/${id}/reject`).send({ motivo });

    expect(response.status).toBe(200);
    expect(response.body.data).toMatchObject({
      estadoAprobacion: 'Rechazado',
      motivoRechazo: motivo,
    });

    const row = await entrepreneurshipRow(id);
    expect(row.estado_aprobacion).toBe('Rechazado');
    expect(row.motivo_rechazo).toBe(motivo);

    const audits = await auditRows(id, 'Rechazo de emprendimiento');
    expect(audits[0]!.valor_nuevo).toMatchObject({ estadoAprobacion: 'Rechazado', motivo });

    const avisos = await notificationsOf(student.id);
    expect(avisos[0]!.mensaje).toContain(motivo);
  });
});

/* =====================================================================================
 * Alcance por rol
 * =================================================================================== */

describe('alcance por rol', () => {
  it('el estudiante ve solo los suyos y el docente solo los asignados', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin);
    const { response: alta } = await createFor(admin, student.id);
    const id = alta.body.data.id as number;

    const demo1 = await loginSession('estudiante.demo1@uniminuto.edu.co');
    const propios = await demo1.get('/api/entrepreneurship').query({ pageSize: 100 });
    expect(propios.status).toBe(200);
    expect(propios.body.data.items.length).toBeGreaterThan(0);
    expect(
      propios.body.data.items.every(
        (item: { estudiante: { id: number } }) => item.estudiante.id === demo1.id,
      ),
    ).toBe(true);

    // Un emprendimiento ajeno responde 404, no 403 (NFR-002).
    expect((await demo1.get(`/api/entrepreneurship/${id}`)).status).toBe(404);

    const mentor = await loginSession('docente.demo1@uniminuto.edu.co');
    const asignados = await mentor.get('/api/entrepreneurship').query({ pageSize: 100 });
    expect(asignados.status).toBe(200);
    expect(asignados.body.data.items.some((item: { id: number }) => item.id === 1)).toBe(true);

    // El docente 2 no tiene asignaciones en el seed.
    const otroDocente = await loginSession('docente.demo2@uniminuto.edu.co');
    const vacio = await otroDocente.get('/api/entrepreneurship');
    expect(vacio.body.data.total).toBe(0);
    expect((await otroDocente.get('/api/entrepreneurship/1')).status).toBe(404);

    // El administrador ve todo, incluido el recién creado.
    const todos = await admin.get('/api/entrepreneurship').query({ pageSize: 100 });
    expect(todos.body.data.items.some((item: { id: number }) => item.id === id)).toBe(true);
  });

  it('una cuenta Limitado no entra al módulo', async () => {
    const admin = await adminSession();
    const student = await newStudent(admin, { estado: 'Limitado' });
    const limitado = await loginSession(student.correo);

    const response = await limitado.get('/api/entrepreneurship');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });

  it('filtra por estado y rechaza un orden fuera de la lista blanca', async () => {
    const admin = await adminSession();

    const pendientes = await admin
      .get('/api/entrepreneurship')
      .query({ estado: 'Pendiente', pageSize: 100 });
    expect(pendientes.status).toBe(200);
    expect(
      pendientes.body.data.items.every(
        (item: { estadoAprobacion: string }) => item.estadoAprobacion === 'Pendiente',
      ),
    ).toBe(true);

    const orden = await admin.get('/api/entrepreneurship').query({ sort: 'password' });
    expect(orden.status).toBe(400);
    expect(orden.body.error.code).toBe('VALIDATION_ERROR');

    const tamano = await admin.get('/api/entrepreneurship').query({ pageSize: 500 });
    expect(tamano.status).toBe(400);

    const extra = await admin.get('/api/entrepreneurship').query({ includeDeleted: 'true' });
    expect(extra.status).toBe(400);
  });
});
