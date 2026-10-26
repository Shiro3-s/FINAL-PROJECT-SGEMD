import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import type { Session } from './api.js';
import { evidenceScenario, jpegBuffer, uploadEvidence, type Scenario } from './fixtures.js';
import { clearMailbox } from './helpers.js';

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
  await query(
    `UPDATE configuracion_programa
        SET valor = '500'
      WHERE clave = 'upload_max_mb'`,
  );
  await query(
    `UPDATE configuracion_programa
        SET valor = '5'
      WHERE clave = 'upload_max_files_per_entity'`,
  );
});

afterAll(async () => {
  await query(
    `UPDATE configuracion_programa
        SET valor = '500'
      WHERE clave IN ('upload_max_mb')`,
  );
  await query(
    `UPDATE configuracion_programa
        SET valor = '5'
      WHERE clave = 'upload_max_files_per_entity'`,
  );
  await closePool();
});

function createTask(
  actor: Session,
  emprendimientoId: number,
  overrides: Record<string, unknown> = {},
) {
  return actor.post('/api/task').send({
    titulo: 'Subir evidencia fotográfica',
    descripcion: 'Adjunta las fotos del punto de venta.',
    emprendimientoId,
    prioridad: 'Alta',
    ...overrides,
  });
}

async function taskWithEvidence(
  scenario: Scenario,
  overrides: Record<string, unknown> = {},
): Promise<{ id: number; attachmentId: number }> {
  const created = await createTask(scenario.mentor.session, scenario.emprendimientoId, overrides);
  expect(created.status).toBe(201);

  const id = created.body.data.id as number;
  const uploaded = await uploadEvidence(
    scenario.student.session,
    'task',
    id,
    jpegBuffer(),
    'punto-de-venta.jpg',
  );
  expect(uploaded.status).toBe(201);

  return { id, attachmentId: uploaded.body.data.id as number };
}

async function auditRows(entidadId: number, accion: string) {
  const { rows } = await query<{
    valor_anterior: Record<string, unknown> | null;
    valor_nuevo: Record<string, unknown> | null;
    usuarios_id_usuarios: number | null;
  }>(
    `SELECT valor_anterior, valor_nuevo, usuarios_id_usuarios
       FROM auditoria_eventos
      WHERE entidad = 'tareas' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

async function taskNotifications(taskId: number) {
  const { rows } = await query<{ usuarios_id_usuarios: number; tipo: string; mensaje: string }>(
    `SELECT usuarios_id_usuarios, tipo, mensaje
       FROM notificaciones
      WHERE tipo_objeto = 'tareas' AND objeto_id = $1
      ORDER BY id_notificaciones ASC`,
    [taskId],
  );
  return rows;
}

/* =====================================================================================
 * T16 — ciclo de vida de la tarea
 * =================================================================================== */

describe('T16 · ciclo de vida de la tarea', () => {
  it('recorre Pendiente → En curso → En revisión → Completada', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId, {
      fechaLimite: '2026-12-31',
      fasePlanId: 1,
      puntos: 100,
    });

    expect(created.status).toBe(201);
    expect(created.body.data).toMatchObject({
      titulo: 'Subir evidencia fotográfica',
      estado: 'Pendiente',
      estadoRevision: 'Pendiente',
      evidenciaRequerida: true,
      prioridad: 'Alta',
      puntos: 100,
      emprendimiento: { id: scenario.emprendimientoId },
      estudiante: { id: scenario.student.id },
      creador: { id: scenario.mentor.id },
      fase: { id: 1 },
    });

    const taskId = created.body.data.id as number;

    const started = await scenario.mentor.session
      .put(`/api/task/${taskId}`)
      .send({ estado: 'En curso' });
    expect(started.status).toBe(200);
    expect(started.body.data.estado).toBe('En curso');

    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
      'punto-de-venta.jpg',
    );
    expect(uploaded.status).toBe(201);

    const submitted = await scenario.student.session.put(`/api/task/${taskId}/complete`).send({});
    expect(submitted.status).toBe(200);
    expect(submitted.body.data).toMatchObject({
      estado: 'En revisión',
      estadoRevision: 'En revisión',
      evidencias: 1,
    });
    expect(submitted.body.data.fechaEnvio).toEqual(expect.any(String));

    const graded = await scenario.mentor.session.put(`/api/task/${taskId}/grade`).send({
      puntajeObtenido: 85,
      retroalimentacion: 'Cumple con lo solicitado.',
    });
    expect(graded.status).toBe(200);
    expect(graded.body.data).toMatchObject({
      estado: 'Completada',
      estadoRevision: 'Calificada',
      puntajeObtenido: 85,
      retroalimentacion: 'Cumple con lo solicitado.',
    });

    expect(await auditRows(taskId, 'Alta de tarea')).toHaveLength(1);
    expect(await auditRows(taskId, 'Edición de tarea')).toHaveLength(1);
    expect(await auditRows(taskId, 'Entrega de tarea')).toHaveLength(1);
    expect(await auditRows(taskId, 'Calificación de tarea')).toHaveLength(1);

    const notifications = await taskNotifications(taskId);
    expect(notifications.some((row) => row.usuarios_id_usuarios === scenario.student.id)).toBe(
      true,
    );
    expect(
      notifications.some((row) => row.tipo === 'Tarea' && row.mensaje.includes('85/100')),
    ).toBe(true);
  });

  it('rechaza las transiciones ilegales', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId);
    const taskId = created.body.data.id as number;

    const gradedTooSoon = await scenario.mentor.session
      .put(`/api/task/${taskId}/grade`)
      .send({ puntajeObtenido: 90 });
    expect(gradedTooSoon.status).toBe(422);
    expect(gradedTooSoon.body.error.code).toBe('INVALID_TASK_TRANSITION');

    const returnedTooSoon = await scenario.mentor.session
      .put(`/api/task/${taskId}/return`)
      .send({ motivo: 'Evidencia incompleta' });
    expect(returnedTooSoon.status).toBe(422);
    expect(returnedTooSoon.body.error.code).toBe('INVALID_TASK_TRANSITION');

    const completedTooSoon = await scenario.student.session
      .put(`/api/task/${taskId}/complete`)
      .send({});
    expect(completedTooSoon.status).toBe(422);
    expect(completedTooSoon.body.error.code).toBe('TASK_EVIDENCE_REQUIRED');

    // `estado` solo admite «En curso» desde el alta; el resto es un error de validación.
    const illegalBody = await scenario.mentor.session
      .put(`/api/task/${taskId}`)
      .send({ estado: 'Completada' });
    expect(illegalBody.status).toBe(400);
  });

  it('no deja que el estudiante cree, edite, califique ni borre', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId);
    const taskId = created.body.data.id as number;

    expect(
      (await createTask(scenario.student.session, scenario.emprendimientoId)).status,
    ).toBe(403);
    expect(
      (await scenario.student.session.put(`/api/task/${taskId}`).send({ titulo: 'Otro' }))
        .status,
    ).toBe(403);
    expect(
      (
        await scenario.student.session
          .put(`/api/task/${taskId}/grade`)
          .send({ puntajeObtenido: 100 })
      ).status,
    ).toBe(403);
    expect((await scenario.student.session.del(`/api/task/${taskId}`)).status).toBe(403);
  });

  it('solo el estudiante destinatario entrega su tarea', async () => {
    const scenario = await evidenceScenario();
    const { id } = await taskWithEvidence(scenario);

    const other = await scenario.otherStudent.session.put(`/api/task/${id}/complete`).send({});
    expect(other.status).toBe(404);

    const mentor = await scenario.mentor.session.put(`/api/task/${id}/complete`).send({});
    expect(mentor.status).toBe(404);
  });

  it('un docente sin asignación no ve ni califica la tarea', async () => {
    const scenario = await evidenceScenario();
    const { id } = await taskWithEvidence(scenario);

    expect((await scenario.otherMentor.session.get(`/api/task/${id}`)).status).toBe(404);
    expect(
      (
        await scenario.otherMentor.session
          .put(`/api/task/${id}/grade`)
          .send({ puntajeObtenido: 70 })
      ).status,
    ).toBe(404);
  });
});

/* =====================================================================================
 * T17 — BR-007: no hay entrega sin evidencia
 * =================================================================================== */

describe('T17 · la evidencia es obligatoria en el servidor', () => {
  it('refusa completar sin evidencia y la acepta después de subirla', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId);
    const taskId = created.body.data.id as number;

    const blocked = await scenario.student.session.put(`/api/task/${taskId}/complete`).send({});
    expect(blocked.status).toBe(422);
    expect(blocked.body.error.code).toBe('TASK_EVIDENCE_REQUIRED');

    const still = await scenario.mentor.session.get(`/api/task/${taskId}`);
    expect(still.body.data.estado).toBe('Pendiente');

    const uploaded = await uploadEvidence(scenario.student.session, 'task', taskId, jpegBuffer());
    expect(uploaded.status).toBe(201);

    const completed = await scenario.student.session.put(`/api/task/${taskId}/complete`).send({});
    expect(completed.status).toBe(200);
    expect(completed.body.data.estado).toBe('En revisión');
  });

  it('vuelve a exigir evidencia si se borró la única que había', async () => {
    const scenario = await evidenceScenario();
    const { id, attachmentId } = await taskWithEvidence(scenario);

    const removed = await scenario.student.session.del(`/api/attachments/${attachmentId}`);
    expect(removed.status).toBe(200);

    const blocked = await scenario.student.session.put(`/api/task/${id}/complete`).send({});
    expect(blocked.status).toBe(422);
    expect(blocked.body.error.code).toBe('TASK_EVIDENCE_REQUIRED');
  });

  it('no acepta evidenciaRequerida ni otros campos de estado desde el cliente', async () => {
    const scenario = await evidenceScenario();

    for (const extra of [
      { evidenciaRequerida: false },
      { estado: 'Completada' },
      { estadoRevision: 'Calificada' },
      { puntajeObtenido: 100 },
      { usuariosId: scenario.otherStudent.id },
    ]) {
      const response = await createTask(
        scenario.mentor.session,
        scenario.emprendimientoId,
        extra,
      );
      expect(response.status).toBe(400);
    }
  });
});

/* =====================================================================================
 * T18 — devolución con motivo
 * =================================================================================== */

describe('T18 · devolución con motivo', () => {
  it('exige motivo, guarda observaciones y avisa al estudiante', async () => {
    const scenario = await evidenceScenario();
    const { id } = await taskWithEvidence(scenario);

    await scenario.student.session.put(`/api/task/${id}/complete`).send({});

    const withoutMotive = await scenario.mentor.session
      .put(`/api/task/${id}/return`)
      .send({ observaciones: 'Falta la fecha de toma' });
    expect(withoutMotive.status).toBe(400);

    const returned = await scenario.mentor.session.put(`/api/task/${id}/return`).send({
      motivo: 'Archivos ilegibles',
      observaciones: 'La foto está borrosa; vuelve a subirla.',
    });
    expect(returned.status).toBe(200);
    expect(returned.body.data).toMatchObject({
      estado: 'Devuelta',
      estadoRevision: 'Devuelta',
      motivoDevolucion: 'Archivos ilegibles',
      observacionesDevolucion: 'La foto está borrosa; vuelve a subirla.',
    });

    const notifications = await taskNotifications(id);
    expect(
      notifications.some(
        (row) =>
          row.usuarios_id_usuarios === scenario.student.id &&
          row.mensaje.includes('Archivos ilegibles'),
      ),
    ).toBe(true);
    expect(await auditRows(id, 'Devolución de tarea')).toHaveLength(1);

    // La evidencia sigue adjunta: el estudiante puede corregir y volver a entregar.
    const again = await scenario.student.session.put(`/api/task/${id}/complete`).send({});
    expect(again.status).toBe(200);
    expect(again.body.data.estado).toBe('En revisión');
  });

  it('un motivo fuera del vocabulario del prototipo es un error de validación', async () => {
    const scenario = await evidenceScenario();
    const { id } = await taskWithEvidence(scenario);
    await scenario.student.session.put(`/api/task/${id}/complete`).send({});

    const response = await scenario.mentor.session
      .put(`/api/task/${id}/return`)
      .send({ motivo: 'No me gustó' });
    expect(response.status).toBe(400);
  });
});

/* =====================================================================================
 * Vencida y avance derivado
 * =================================================================================== */

describe('Vencida y avance derivado', () => {
  it('deriva Vencida sin almacenarla y permite entregar igual', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId, {
      fechaLimite: '2020-01-01',
    });
    const id = created.body.data.id as number;

    const read = await scenario.student.session.get(`/api/task/${id}`);
    expect(read.status).toBe(200);
    expect(read.body.data).toMatchObject({ estado: 'Vencida', vencida: true });

    const listed = await scenario.student.session.get('/api/task/my-task?estado=Vencida');
    expect(listed.status).toBe(200);
    expect(listed.body.data.total).toBe(1);

    const { rows } = await query<{ estado: string }>(
      'SELECT estado FROM tareas WHERE id_tareas = $1',
      [id],
    );
    expect(rows[0]!.estado).toBe('Pendiente');

    await uploadEvidence(scenario.student.session, 'task', id, jpegBuffer());
    const submitted = await scenario.student.session.put(`/api/task/${id}/complete`).send({});
    expect(submitted.status).toBe(200);
    expect(submitted.body.data.estado).toBe('En revisión');
  });

  it('recalcula el avance del emprendimiento al calificar y al dar de baja', async () => {
    const scenario = await evidenceScenario();

    const first = await taskWithEvidence(scenario, { titulo: 'Primera' });
    const second = await createTask(scenario.mentor.session, scenario.emprendimientoId, {
      titulo: 'Segunda',
    });
    const secondId = second.body.data.id as number;

    await scenario.student.session.put(`/api/task/${first.id}/complete`).send({});
    const graded = await scenario.mentor.session
      .put(`/api/task/${first.id}/grade`)
      .send({ puntajeObtenido: 100 });
    expect(graded.status).toBe(200);

    const half = await scenario.student.session.get(
      `/api/task/advance/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(half.status).toBe(200);
    expect(half.body.data).toMatchObject({ avance: 50, total: 2, completadas: 1 });
    // Las cuatro fases del catálogo siempre están; las tareas sin fase añaden su fila.
    expect(half.body.data.fases).toHaveLength(5);
    const sinFase = half.body.data.fases.find(
      (fase: { faseId: number | null }) => fase.faseId === null,
    );
    expect(sinFase).toMatchObject({ total: 2, completadas: 1, porcentaje: 50 });

    // Al dar de baja la tarea pendiente, el denominador queda en 1/1.
    const removed = await scenario.mentor.session.del(`/api/task/${secondId}`);
    expect(removed.status).toBe(200);

    const full = await scenario.mentor.session.get(
      `/api/task/advance/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(full.body.data).toMatchObject({ avance: 100, total: 1, completadas: 1 });
    expect(await auditRows(secondId, 'Baja lógica de tarea')).toHaveLength(1);
  });

  it('devuelve 0 % cuando el emprendimiento no tiene tareas', async () => {
    const scenario = await evidenceScenario();

    const response = await scenario.mentor.session.get(
      `/api/task/advance/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(response.status).toBe(200);
    expect(response.body.data).toMatchObject({ avance: 0, total: 0, completadas: 0 });
    expect(response.body.data.fases).toHaveLength(4);
  });
});

/* =====================================================================================
 * Alcance y listados
 * =================================================================================== */

describe('alcance y listados', () => {
  it('respeta el alcance por rol en el detalle y en el listado', async () => {
    const scenario = await evidenceScenario();
    const created = await createTask(scenario.mentor.session, scenario.emprendimientoId);
    const id = created.body.data.id as number;

    expect((await scenario.student.session.get(`/api/task/${id}`)).status).toBe(200);
    expect((await scenario.otherStudent.session.get(`/api/task/${id}`)).status).toBe(404);
    expect((await scenario.otherMentor.session.get(`/api/task/${id}`)).status).toBe(404);
    expect((await scenario.admin.get(`/api/task/${id}`)).status).toBe(200);

    const own = await scenario.student.session.get('/api/task/my-task');
    expect(own.body.data.total).toBe(1);

    const foreign = await scenario.otherStudent.session.get('/api/task/my-task');
    expect(foreign.body.data.total).toBe(0);

    const byEntrepreneurship = await scenario.mentor.session.get(
      `/api/task/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(byEntrepreneurship.body.data.total).toBe(1);

    const foreignEntrepreneurship = await scenario.otherMentor.session.get(
      `/api/task/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(foreignEntrepreneurship.status).toBe(404);
  });

  it('filtra por estado, prioridad y texto, y valida la consulta', async () => {
    const scenario = await evidenceScenario();
    await createTask(scenario.mentor.session, scenario.emprendimientoId, {
      titulo: 'Levantar el modelo de negocio',
      prioridad: 'Alta',
    });
    await createTask(scenario.mentor.session, scenario.emprendimientoId, {
      titulo: 'Registrar costos',
      prioridad: 'Baja',
    });

    const filtered = await scenario.mentor.session.get(
      '/api/task?prioridad=Baja&q=costos',
    );
    expect(filtered.status).toBe(200);
    expect(filtered.body.data.total).toBe(1);
    expect(filtered.body.data.items[0].titulo).toBe('Registrar costos');

    expect((await scenario.mentor.session.get('/api/task?estado=Inventada')).status).toBe(400);
    expect((await scenario.mentor.session.get('/api/task?sort=password')).status).toBe(400);
    expect((await scenario.mentor.session.get('/api/task?pageSize=101')).status).toBe(400);
    expect((await scenario.mentor.session.get('/api/task/abc')).status).toBe(400);
  });

  it('no permite editar una tarea ya entregada', async () => {
    const scenario = await evidenceScenario();
    const { id } = await taskWithEvidence(scenario);
    await scenario.student.session.put(`/api/task/${id}/complete`).send({});

    const response = await scenario.mentor.session
      .put(`/api/task/${id}`)
      .send({ titulo: 'Título nuevo' });
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('TASK_NOT_EDITABLE');
  });
});
