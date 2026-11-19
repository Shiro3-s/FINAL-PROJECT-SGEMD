import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { hashPassword } from '../src/utils/password.js';
import { adminSession, loginSession, type Session } from './api.js';
import { clearMailbox, uniqueEmail } from './helpers.js';

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
  await query(
    `UPDATE configuracion_programa
        SET valor = '12'
      WHERE clave IN ('carga_max_horas', 'max_emprendimientos_docente')`,
  );
});

afterAll(async () => {
  await query(
    `UPDATE configuracion_programa
        SET valor = '12'
      WHERE clave IN ('carga_max_horas', 'max_emprendimientos_docente')`,
  );
  await closePool();
});

/* -------------------------------------------------------------------------------------
 * Fixtures
 * ----------------------------------------------------------------------------------- */

let sequence = 0;
function nextLabel(prefix: string): string {
  sequence += 1;
  return `${prefix}-${Date.now()}-${sequence}`;
}

function uniqueDocument(): string {
  return `A${Date.now()}${Math.floor(Math.random() * 1_000_000)}`.slice(0, 30);
}

interface Account {
  id: number;
  correo: string;
  session: Session;
}

async function newAccount(admin: Session, rolId: 2 | 3): Promise<Account> {
  const correo = uniqueEmail(rolId === 3 ? 'asgdoc' : 'asgest');
  const response = await admin.post('/api/users').send({
    nombres: rolId === 3 ? 'Docente' : 'Estudiante',
    apellidos: 'Asignación',
    numeroDocumento: uniqueDocument(),
    correoInstitucional: correo,
    rolId,
    tipoDocumentoId: 1,
  });
  expect(response.status).toBe(201);

  await query('UPDATE usuarios SET password = $2 WHERE correo_institucional = $1', [
    correo,
    await hashPassword('Demo1234'),
  ]);

  return { id: response.body.data.id as number, correo, session: await loginSession(correo) };
}

async function newEntrepreneurship(admin: Session, estudianteId: number): Promise<number> {
  const response = await admin.post('/api/entrepreneurship').send({
    nombre: nextLabel('Proyecto'),
    descripcion: 'Emprendimiento de prueba para asignaciones',
    estudianteId,
    sectorId: 1,
    centroUniversitarioId: 1,
  });
  expect(response.status).toBe(201);

  const id = response.body.data.id as number;
  const approved = await admin.post(`/api/entrepreneurship/${id}/approve`).send({});
  expect(approved.status).toBe(200);
  return id;
}

async function addActa(
  emprendimientoId: number,
  estudianteId: number,
  estado = 'Aprobada',
): Promise<void> {
  await query(
    `INSERT INTO actas
       (estado, observaciones, fecha_carga, fecha_revision,
        emprendimiento_id_emprendimiento, usuarios_id_estudiante, usuarios_id_revisor)
     VALUES ($1, $2, now(), $3, $4, $5, 1)`,
    [
      estado,
      estado === 'Rechazada' ? 'Acta de prueba rechazada' : null,
      estado === 'Aprobada' ? new Date() : null,
      emprendimientoId,
      estudianteId,
    ],
  );
}

/**
 * Inserta emprendimientos aprobados con su acta aprobada, sin pasar por la API.
 * Solo para pruebas de tope que necesitan muchas filas rápido.
 */
async function seedEntrepreneurships(
  estudianteId: number,
  count: number,
): Promise<number[]> {
  const ids: number[] = [];

  for (let index = 0; index < count; index += 1) {
    const { rows } = await query<{ id_emprendimiento: number }>(
      `INSERT INTO emprendimiento (codigo, nombre, estado_aprobacion, usuarios_id_usuarios)
       VALUES ($1, $2, 'Aprobado', $3)
       RETURNING id_emprendimiento`,
      [nextLabel('FIX'), nextLabel('Proyecto de tope'), estudianteId],
    );
    const id = rows[0]!.id_emprendimiento;
    await addActa(id, estudianteId);
    ids.push(id);
  }

  return ids;
}

function assign(
  admin: Session,
  mentorId: number,
  emprendimientoId: number,
  horasSemanales = 2,
) {
  return admin.post('/api/assignments').send({ mentorId, emprendimientoId, horasSemanales });
}

interface Scenario {
  student: Account;
  mentor: Account;
  emprendimientoId: number;
  assignment: {
    id: number;
    estado: string;
    horasSemanales: number;
    mentor: { id: number };
    estudiante: { id: number };
    emprendimiento: { id: number };
  };
}

async function scenario(admin: Session): Promise<Scenario> {
  const student = await newAccount(admin, 2);
  const mentor = await newAccount(admin, 3);
  const emprendimientoId = await newEntrepreneurship(admin, student.id);
  await addActa(emprendimientoId, student.id);

  const response = await assign(admin, mentor.id, emprendimientoId);
  expect(response.status).toBe(201);

  return {
    student,
    mentor,
    emprendimientoId,
    assignment: response.body.data as Scenario['assignment'],
  };
}

async function auditRows(assignmentId: number, accion: string) {
  const { rows } = await query<{
    valor_anterior: Record<string, unknown> | null;
    valor_nuevo: Record<string, unknown> | null;
    usuarios_id_usuarios: number | null;
  }>(
    `SELECT valor_anterior, valor_nuevo, usuarios_id_usuarios
       FROM auditoria_eventos
      WHERE entidad = 'asignaciones' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [assignmentId, accion],
  );
  return rows;
}

async function assignmentNotifications(assignmentId: number) {
  const { rows } = await query<{
    usuarios_id_usuarios: number;
    tipo: string;
    mensaje: string;
    url: string | null;
    tipo_objeto: string | null;
    objeto_id: number | null;
  }>(
    `SELECT usuarios_id_usuarios, tipo, mensaje, url, tipo_objeto, objeto_id
       FROM notificaciones
      WHERE tipo_objeto = 'asignaciones' AND objeto_id = $1
      ORDER BY id_notificaciones ASC`,
    [assignmentId],
  );
  return rows;
}

/* =====================================================================================
 * T15 — el acta aprobada es precondición (BR-001)
 * =================================================================================== */

describe('T15 · acta de compromiso aprobada', () => {
  it('bloquea la asignación sin acta aprobada y la permite después', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const emprendimientoId = await newEntrepreneurship(admin, student.id);

    await addActa(emprendimientoId, student.id, 'Pendiente');

    const blocked = await assign(admin, mentor.id, emprendimientoId);
    expect(blocked.status).toBe(422);
    expect(blocked.body.error.code).toBe('ACTA_NOT_APPROVED');

    await query(
      `UPDATE actas
          SET estado = 'Aprobada', fecha_revision = now(), usuarios_id_revisor = 1
        WHERE emprendimiento_id_emprendimiento = $1`,
      [emprendimientoId],
    );

    const created = await assign(admin, mentor.id, emprendimientoId);
    expect(created.status).toBe(201);
    expect(created.body.data).toMatchObject({
      estado: 'activa',
      horasSemanales: 2,
      mentor: { id: mentor.id },
      estudiante: { id: student.id },
      emprendimiento: { id: emprendimientoId },
    });
  });

  it('un acta rechazada tampoco habilita la asignación', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const emprendimientoId = await newEntrepreneurship(admin, student.id);
    await addActa(emprendimientoId, student.id, 'Rechazada');

    const response = await assign(admin, mentor.id, emprendimientoId);
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('ACTA_NOT_APPROVED');
  });
});

/* =====================================================================================
 * T07 — ambos topes docentes
 * =================================================================================== */

describe('T07 · topes de carga docente', () => {
  it('acepta doce asignaciones de 1 h y rechaza la decimotercera', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const ids = await seedEntrepreneurships(student.id, 13);

    for (const id of ids.slice(0, 12)) {
      const response = await assign(admin, mentor.id, id, 1);
      expect(response.status).toBe(201);
    }

    const thirteenth = await assign(admin, mentor.id, ids[12]!, 1);
    expect(thirteenth.status).toBe(422);
    expect(thirteenth.body.error.code).toBe('TEACHER_HOURS_LIMIT_REACHED');

    const { rows } = await query<{ total: string; horas: string }>(
      `SELECT COUNT(*)::text AS total, COALESCE(SUM(horas_semanales), 0)::text AS horas
         FROM asignaciones
        WHERE usuarios_id_mentor = $1 AND estado = 'activa'`,
      [mentor.id],
    );
    expect(Number(rows[0]!.total)).toBe(12);
    expect(Number(rows[0]!.horas)).toBe(12);
  });

  it('rechaza una asignación que supera carga_max_horas', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const [first, second] = await seedEntrepreneurships(student.id, 2);

    await query(`UPDATE configuracion_programa SET valor = '4' WHERE clave = 'carga_max_horas'`);
    await query(
      `UPDATE configuracion_programa SET valor = '100' WHERE clave = 'max_emprendimientos_docente'`,
    );

    expect((await assign(admin, mentor.id, first!, 4)).status).toBe(201);

    const over = await assign(admin, mentor.id, second!, 1);
    expect(over.status).toBe(422);
    expect(over.body.error.code).toBe('TEACHER_HOURS_LIMIT_REACHED');
    expect(over.body.error.fields).toHaveProperty('horasSemanales');
  });

  it('rechaza una asignación que supera max_emprendimientos_docente', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const ids = await seedEntrepreneurships(student.id, 3);

    await query(`UPDATE configuracion_programa SET valor = '100' WHERE clave = 'carga_max_horas'`);
    await query(
      `UPDATE configuracion_programa SET valor = '2' WHERE clave = 'max_emprendimientos_docente'`,
    );

    expect((await assign(admin, mentor.id, ids[0]!, 1)).status).toBe(201);
    expect((await assign(admin, mentor.id, ids[1]!, 1)).status).toBe(201);

    const over = await assign(admin, mentor.id, ids[2]!, 1);
    expect(over.status).toBe(422);
    expect(over.body.error.code).toBe('TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED');
    expect(over.body.error.fields).toHaveProperty('mentorId');
  });
});

/* =====================================================================================
 * R11 — una sola asignación activa por emprendimiento
 * =================================================================================== */

describe('R11 · unicidad de la asignación activa', () => {
  it('rechaza una segunda asignación activa y la permite tras la baja', async () => {
    const admin = await adminSession();
    const { mentor, emprendimientoId, assignment } = await scenario(admin);
    const otherMentor = await newAccount(admin, 3);

    const duplicate = await assign(admin, otherMentor.id, emprendimientoId);
    expect(duplicate.status).toBe(409);
    expect(duplicate.body.error.code).toBe('ASSIGNMENT_ALREADY_ACTIVE');

    const removed = await admin.del(`/api/assignments/${assignment.id}`);
    expect(removed.status).toBe(200);

    const replacement = await assign(admin, otherMentor.id, emprendimientoId);
    expect(replacement.status).toBe(201);
    expect(replacement.body.data.mentor.id).toBe(otherMentor.id);

    const inactive = await admin.get(`/api/assignments/${assignment.id}`);
    expect(inactive.status).toBe(200);
    expect(inactive.body.data.estado).toBe('inactiva');
  });

  it('la baja libera el cupo del docente', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const mentor = await newAccount(admin, 3);
    const [first, second] = await seedEntrepreneurships(student.id, 2);

    await query(
      `UPDATE configuracion_programa SET valor = '1' WHERE clave = 'max_emprendimientos_docente'`,
    );

    const created = await assign(admin, mentor.id, first!, 1);
    expect(created.status).toBe(201);

    const full = await assign(admin, mentor.id, second!, 1);
    expect(full.status).toBe(422);
    expect(full.body.error.code).toBe('TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED');

    expect((await admin.del(`/api/assignments/${created.body.data.id}`)).status).toBe(200);

    const freed = await assign(admin, mentor.id, second!, 1);
    expect(freed.status).toBe(201);
  });
});

/* =====================================================================================
 * R9, R10 — escritura solo del admin y alcance de lectura
 * =================================================================================== */

describe('R9/R10 · autorización y alcance', () => {
  it('solo el administrador crea, reasigna y da de baja', async () => {
    const admin = await adminSession();
    const { mentor, student, emprendimientoId, assignment } = await scenario(admin);
    const otherMentor = await newAccount(admin, 3);

    for (const session of [mentor.session, student.session]) {
      const create = await session
        .post('/api/assignments')
        .send({ mentorId: otherMentor.id, emprendimientoId, horasSemanales: 2 });
      expect(create.status).toBe(403);
      expect(create.body.error.code).toBe('ROLE_NOT_ALLOWED');

      const update = await session
        .put(`/api/assignments/${assignment.id}`)
        .send({ horasSemanales: 3 });
      expect(update.status).toBe(403);

      const remove = await session.del(`/api/assignments/${assignment.id}`);
      expect(remove.status).toBe(403);
    }
  });

  it('el docente ve solo sus asignaciones y el estudiante solo las suyas', async () => {
    const admin = await adminSession();
    const first = await scenario(admin);
    const second = await scenario(admin);

    const teacherList = await first.mentor.session.get('/api/assignments');
    expect(teacherList.status).toBe(200);
    expect(teacherList.body.data.total).toBeGreaterThanOrEqual(1);
    for (const item of teacherList.body.data.items) {
      expect(item.mentor.id).toBe(first.mentor.id);
    }

    const studentList = await first.student.session.get('/api/assignments');
    expect(studentList.status).toBe(200);
    for (const item of studentList.body.data.items) {
      expect(item.estudiante.id).toBe(first.student.id);
    }

    const adminList = await admin.get('/api/assignments');
    const ids = (adminList.body.data.items as { id: number }[]).map((item) => item.id);
    expect(ids).toContain(first.assignment.id);
    expect(ids).toContain(second.assignment.id);
  });

  it('un detalle fuera de alcance responde 404', async () => {
    const admin = await adminSession();
    const first = await scenario(admin);
    const second = await scenario(admin);

    expect((await first.mentor.session.get(`/api/assignments/${second.assignment.id}`)).status).toBe(
      404,
    );
    expect(
      (await first.student.session.get(`/api/assignments/${second.assignment.id}`)).status,
    ).toBe(404);
    expect((await admin.get(`/api/assignments/${second.assignment.id}`)).status).toBe(200);
  });

  it('GET /assignments/mentor/:id respeta el alcance del docente', async () => {
    const admin = await adminSession();
    const first = await scenario(admin);
    const second = await scenario(admin);

    const own = await first.mentor.session.get(`/api/assignments/mentor/${first.mentor.id}`);
    expect(own.status).toBe(200);
    expect(own.body.data.items.length).toBeGreaterThanOrEqual(1);

    const other = await first.mentor.session.get(`/api/assignments/mentor/${second.mentor.id}`);
    expect(other.status).toBe(404);

    const asStudent = await first.student.session.get(
      `/api/assignments/mentor/${first.mentor.id}`,
    );
    expect(asStudent.status).toBe(403);

    const asAdmin = await admin.get(`/api/assignments/mentor/${second.mentor.id}`);
    expect(asAdmin.status).toBe(200);
    for (const item of asAdmin.body.data.items) {
      expect(item.mentor.id).toBe(second.mentor.id);
    }
  });

  it('GET /assignments/student/:id respeta el alcance de estudiante y docente', async () => {
    const admin = await adminSession();
    const first = await scenario(admin);
    const second = await scenario(admin);

    const own = await first.student.session.get(
      `/api/assignments/student/${first.student.id}`,
    );
    expect(own.status).toBe(200);

    const other = await first.student.session.get(
      `/api/assignments/student/${second.student.id}`,
    );
    expect(other.status).toBe(404);

    const mentorOwn = await first.mentor.session.get(
      `/api/assignments/student/${first.student.id}`,
    );
    expect(mentorOwn.status).toBe(200);
    for (const item of mentorOwn.body.data.items) {
      expect(item.mentor.id).toBe(first.mentor.id);
    }

    const mentorOther = await first.mentor.session.get(
      `/api/assignments/student/${second.student.id}`,
    );
    expect(mentorOther.status).toBe(404);

    expect(
      (await admin.get(`/api/assignments/student/${second.student.id}`)).status,
    ).toBe(200);
  });
});

/* =====================================================================================
 * Alta: validaciones y efectos
 * =================================================================================== */

describe('alta de asignación', () => {
  it('deriva el estudiante del emprendimiento y escribe auditoría y notificaciones', async () => {
    const admin = await adminSession();
    const { mentor, student, assignment } = await scenario(admin);

    expect(assignment.estudiante.id).toBe(student.id);
    expect(assignment.mentor.id).toBe(mentor.id);

    const [audit] = await auditRows(assignment.id, 'Alta de asignación');
    expect(audit).toBeDefined();
    expect(audit!.usuarios_id_usuarios).toBe(admin.id);
    expect(audit!.valor_nuevo).toMatchObject({
      mentorId: mentor.id,
      estudianteId: student.id,
      estado: 'activa',
      horasSemanales: 2,
    });

    const notifications = await assignmentNotifications(assignment.id);
    expect(notifications.map((row) => row.usuarios_id_usuarios).sort()).toEqual(
      [mentor.id, student.id].sort(),
    );
    expect(notifications.every((row) => row.tipo === 'Sistema')).toBe(true);
    expect(notifications.every((row) => row.url !== null)).toBe(true);
  });

  it('rechaza un mentor que no es docente o que no está activo', async () => {
    const admin = await adminSession();
    const student = await newAccount(admin, 2);
    const emprendimientoId = await newEntrepreneurship(admin, student.id);
    await addActa(emprendimientoId, student.id);

    const asStudent = await assign(admin, student.id, emprendimientoId);
    expect(asStudent.status).toBe(400);
    expect(asStudent.body.error.fields).toHaveProperty('mentorId');

    const inactive = await newAccount(admin, 3);
    await query(`UPDATE usuarios SET estado = 'Inactivo' WHERE id_usuarios = $1`, [inactive.id]);

    const blocked = await assign(admin, inactive.id, emprendimientoId);
    expect(blocked.status).toBe(422);
    expect(blocked.body.error.code).toBe('MENTOR_NOT_ACTIVE');
  });

  it('rechaza un emprendimiento inexistente, un cuerpo inválido y campos desconocidos', async () => {
    const admin = await adminSession();
    const mentor = await newAccount(admin, 3);

    const missing = await assign(admin, mentor.id, 999_999_999);
    expect(missing.status).toBe(400);
    expect(missing.body.error.fields).toHaveProperty('emprendimientoId');

    const noHours = await admin
      .post('/api/assignments')
      .send({ mentorId: mentor.id, emprendimientoId: 1 });
    expect(noHours.status).toBe(400);
    expect(noHours.body.error.fields).toHaveProperty('horasSemanales');

    const zeroHours = await admin
      .post('/api/assignments')
      .send({ mentorId: mentor.id, emprendimientoId: 1, horasSemanales: 0 });
    expect(zeroHours.status).toBe(400);

    const unknown = await admin
      .post('/api/assignments')
      .send({ mentorId: mentor.id, emprendimientoId: 1, horasSemanales: 2, estudianteId: 4 });
    expect(unknown.status).toBe(400);
    expect(unknown.body.error.code).toBe('VALIDATION_ERROR');
  });
});

/* =====================================================================================
 * Edición y baja
 * =================================================================================== */

describe('edición y baja de la asignación', () => {
  it('reasigna el mentor, revalida sus topes y audita el cambio', async () => {
    const admin = await adminSession();
    const { assignment, student } = await scenario(admin);
    const newMentor = await newAccount(admin, 3);

    const response = await admin
      .put(`/api/assignments/${assignment.id}`)
      .send({ mentorId: newMentor.id, horasSemanales: 3 });
    expect(response.status).toBe(200);
    expect(response.body.data).toMatchObject({
      mentor: { id: newMentor.id },
      estudiante: { id: student.id },
      horasSemanales: 3,
      estado: 'activa',
    });

    const [audit] = await auditRows(assignment.id, 'Edición de asignación');
    expect(audit!.valor_anterior).toMatchObject({
      mentorId: assignment.mentor.id,
      horasSemanales: assignment.horasSemanales,
    });
    expect(audit!.valor_nuevo).toMatchObject({ mentorId: newMentor.id, horasSemanales: 3 });
  });

  it('rechaza la reasignación si el docente destino está en el tope', async () => {
    const admin = await adminSession();
    const first = await scenario(admin);
    const second = await scenario(admin);
    const busy = await newAccount(admin, 3);
    const student = await newAccount(admin, 2);
    const [extra] = await seedEntrepreneurships(student.id, 1);

    await query(
      `UPDATE configuracion_programa SET valor = '1' WHERE clave = 'max_emprendimientos_docente'`,
    );

    expect((await assign(admin, busy.id, extra!, 1)).status).toBe(201);

    const response = await admin
      .put(`/api/assignments/${first.assignment.id}`)
      .send({ mentorId: busy.id });
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED');

    // La asignación original sigue intacta.
    const unchanged = await admin.get(`/api/assignments/${first.assignment.id}`);
    expect(unchanged.body.data.mentor.id).toBe(first.mentor.id);
    expect(second.assignment.id).not.toBe(first.assignment.id);
  });

  it('una asignación inactiva no se edita ni se vuelve a dar de baja', async () => {
    const admin = await adminSession();
    const { assignment } = await scenario(admin);
    const otherMentor = await newAccount(admin, 3);

    expect((await admin.del(`/api/assignments/${assignment.id}`)).status).toBe(200);

    const update = await admin
      .put(`/api/assignments/${assignment.id}`)
      .send({ mentorId: otherMentor.id });
    expect(update.status).toBe(422);
    expect(update.body.error.code).toBe('ASSIGNMENT_NOT_ACTIVE');

    const remove = await admin.del(`/api/assignments/${assignment.id}`);
    expect(remove.status).toBe(422);
    expect(remove.body.error.code).toBe('ASSIGNMENT_NOT_ACTIVE');
  });

  it('la baja escribe auditoría y avisa al docente y al estudiante', async () => {
    const admin = await adminSession();
    const { assignment, mentor, student } = await scenario(admin);

    expect((await admin.del(`/api/assignments/${assignment.id}`)).status).toBe(200);

    const [audit] = await auditRows(assignment.id, 'Baja de asignación');
    expect(audit!.valor_anterior).toMatchObject({ estado: 'activa' });
    expect(audit!.valor_nuevo).toMatchObject({ estado: 'inactiva' });

    const notifications = await assignmentNotifications(assignment.id);
    const recipients = notifications.map((row) => row.usuarios_id_usuarios);
    expect(recipients).toContain(mentor.id);
    expect(recipients).toContain(student.id);
  });
});

/* =====================================================================================
 * Listados: filtros, búsqueda y validación de la consulta
 * =================================================================================== */

describe('listado de asignaciones', () => {
  it('filtra por estado, mentor y búsqueda de texto', async () => {
    const admin = await adminSession();
    const { mentor, student, emprendimientoId, assignment } = await scenario(admin);

    const byMentor = await admin.get(`/api/assignments?mentorId=${mentor.id}`);
    expect(byMentor.status).toBe(200);
    expect(byMentor.body.data.total).toBe(1);
    expect(byMentor.body.data.items[0].id).toBe(assignment.id);

    const byStudent = await admin.get(`/api/assignments?estudianteId=${student.id}`);
    expect(byStudent.body.data.items[0].id).toBe(assignment.id);

    const byEntrepreneurship = await admin.get(
      `/api/assignments?emprendimientoId=${emprendimientoId}`,
    );
    expect(byEntrepreneurship.body.data.items[0].id).toBe(assignment.id);

    const byEmail = await admin.get(
      `/api/assignments?q=${encodeURIComponent(student.correo)}`,
    );
    expect(byEmail.body.data.items.map((item: { id: number }) => item.id)).toContain(
      assignment.id,
    );

    const active = await admin.get('/api/assignments?estado=activa');
    expect(
      active.body.data.items.every((item: { estado: string }) => item.estado === 'activa'),
    ).toBe(true);

    expect((await admin.del(`/api/assignments/${assignment.id}`)).status).toBe(200);

    const inactive = await admin.get(
      `/api/assignments?estado=inactiva&estudianteId=${student.id}`,
    );
    expect(inactive.body.data.total).toBe(1);
    expect(inactive.body.data.items[0].id).toBe(assignment.id);
  });

  it('valida identificadores y parámetros desconocidos', async () => {
    const admin = await adminSession();

    expect((await admin.get('/api/assignments/abc')).status).toBe(400);
    expect((await admin.get('/api/assignments/999999999')).status).toBe(404);
    expect((await admin.get('/api/assignments?pageSize=101')).status).toBe(400);
    expect((await admin.get('/api/assignments?sort=mentorId')).status).toBe(400);
    expect((await admin.get('/api/assignments?desconocido=1')).status).toBe(400);
    expect((await admin.get('/api/assignments/mentor/abc')).status).toBe(400);
    expect((await admin.get('/api/assignments/mentor/999999999')).status).toBe(404);
    expect((await admin.get('/api/assignments/student/999999999')).status).toBe(404);
  });
});
