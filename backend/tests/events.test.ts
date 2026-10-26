import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import type { Session } from './api.js';
import { createAccount, evidenceScenario, type Scenario } from './fixtures.js';

/**
 * T27 — eventos institucionales y recomendaciones (FR-021).
 *
 * Cada caso crea su propio evento con un nombre único para no depender de los tres
 * eventos del seed ni del orden de las suites. El escenario aporta un emprendimiento con
 * asignación activa, que es lo que el docente necesita para recomendar.
 */

beforeEach(async () => {
  resetRateLimits();
});

afterAll(async () => {
  await closePool();
});

let sequence = 0;
function uniqueName(prefix: string): string {
  sequence += 1;
  return `${prefix} ${Date.now()}-${sequence}`;
}

interface EventBody {
  id: number;
  nombreEvento: string;
  descripcion: string | null;
  dirigidoA: string | null;
  capacidadMaxima: number | null;
  cupo: number | null;
  estado: string;
  requiereRegistro: boolean;
  lugar: string | null;
  enlace: string | null;
  tipoEvento: { id: number; nombre: string } | null;
  modalidad: { id: number; nombre: string } | null;
  fecha: string | null;
  horaInicio: string | null;
  horaFin: string | null;
  organizador: { id: number; nombres: string; apellidos: string };
  inscritos: number;
  inscrito: boolean;
}

interface RecommendationBody {
  id: number;
  mensaje: string | null;
  estado: string;
  fecha: string;
  evento: { id: number; nombreEvento: string };
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: { id: number } | null;
  docente: { id: number };
}

function eventPayload(overrides: Record<string, unknown> = {}) {
  return {
    nombreEvento: uniqueName('Evento de prueba'),
    descripcion: 'Descripción del evento de prueba',
    dirigidoA: 'Todos los estudiantes',
    capacidadMaxima: 2,
    estado: 'Publicado',
    requiereRegistro: true,
    tipoEventoId: 2,
    modalidadId: 2,
    fecha: '2026-12-15',
    horaInicio: '10:00',
    horaFin: '12:00',
    ...overrides,
  };
}

async function createEvent(admin: Session, overrides: Record<string, unknown> = {}) {
  return admin.post('/api/event').send(eventPayload(overrides));
}

async function eventRow(id: number) {
  const { rows } = await query<{
    estado: string;
    cupo: number | null;
    capacidad_maxima: number | null;
    fecha_eliminacion: Date | null;
  }>(
    `SELECT estado, cupo, capacidad_maxima, fecha_eliminacion
       FROM eventos WHERE id_eventos = $1`,
    [id],
  );
  return rows[0]!;
}

/* =====================================================================================
 * T27 — CRUD del administrador
 * =================================================================================== */

describe('T27 · CRUD del administrador', () => {
  it('crea, lee, edita y da de baja un evento', async () => {
    const scenario = await evidenceScenario();
    const nombre = uniqueName('Startup de prueba');

    const created = await createEvent(scenario.admin, { nombreEvento: nombre });
    expect(created.status).toBe(201);
    const event = created.body.data as EventBody;
    expect(event).toMatchObject({
      nombreEvento: nombre,
      estado: 'Publicado',
      capacidadMaxima: 2,
      cupo: 2,
      requiereRegistro: true,
      fecha: '2026-12-15',
      horaInicio: '10:00',
      horaFin: '12:00',
      tipoEvento: { id: 2, nombre: 'Capacitación' },
      modalidad: { id: 2, nombre: 'Virtual' },
      organizador: { id: scenario.admin.id },
      inscritos: 0,
      inscrito: false,
    });

    const read = await scenario.admin.get(`/api/event/${event.id}`);
    expect(read.status).toBe(200);
    expect(read.body.data.id).toBe(event.id);

    const updated = await scenario.admin.put(`/api/event/${event.id}`).send({
      nombreEvento: `${nombre} (actualizado)`,
      capacidadMaxima: 5,
      estado: 'Pendiente',
      lugar: 'Auditorio',
    });
    expect(updated.status).toBe(200);
    expect(updated.body.data).toMatchObject({
      nombreEvento: `${nombre} (actualizado)`,
      capacidadMaxima: 5,
      cupo: 5,
      estado: 'Pendiente',
      lugar: 'Auditorio',
    });

    const deleted = await scenario.admin.del(`/api/event/${event.id}`);
    expect(deleted.status).toBe(200);
    expect(deleted.body.message).toBeTruthy();

    const gone = await scenario.admin.get(`/api/event/${event.id}`);
    expect(gone.status).toBe(404);

    const row = await eventRow(event.id);
    expect(row.fecha_eliminacion).not.toBeNull();
    expect(row.estado).toBe('Pendiente');
  });

  it('solo el administrador escribe eventos', async () => {
    const scenario = await evidenceScenario();
    const payload = eventPayload();

    for (const session of [scenario.student.session, scenario.mentor.session]) {
      const created = await session.post('/api/event').send(payload);
      expect(created.status).toBe(403);
      expect(created.body.error.code).toBe('ROLE_NOT_ALLOWED');
    }

    const event = (await createEvent(scenario.admin)).body.data as EventBody;

    for (const session of [scenario.student.session, scenario.mentor.session]) {
      const updated = await session.put(`/api/event/${event.id}`).send({ lugar: 'Otro' });
      expect(updated.status).toBe(403);
      const deleted = await session.del(`/api/event/${event.id}`);
      expect(deleted.status).toBe(403);
    }
  });
});

/* =====================================================================================
 * T27 — visibilidad: solo los publicados
 * =================================================================================== */

describe('T27 · visibilidad de los eventos', () => {
  it('el docente y el estudiante solo ven los publicados', async () => {
    const scenario = await evidenceScenario();
    const draftName = uniqueName('Borrador');
    const publishedName = uniqueName('Publicado');

    const draft = (await createEvent(scenario.admin, {
      nombreEvento: draftName,
      estado: 'Pendiente',
    })).body.data as EventBody;
    const published = (await createEvent(scenario.admin, {
      nombreEvento: publishedName,
      estado: 'Publicado',
    })).body.data as EventBody;

    const draftAsAdmin = await scenario.admin.get(`/api/event/${draft.id}`);
    expect(draftAsAdmin.status).toBe(200);

    for (const session of [scenario.student.session, scenario.mentor.session]) {
      const hidden = await session.get(`/api/event/${draft.id}`);
      expect(hidden.status).toBe(404);

      const visible = await session.get(`/api/event/${published.id}`);
      expect(visible.status).toBe(200);
    }

    const studentList = await scenario.student.session.get(
      `/api/event?q=${encodeURIComponent(draftName)}`,
    );
    expect(studentList.status).toBe(200);
    expect(studentList.body.data.total).toBe(0);

    const teacherList = await scenario.mentor.session.get(
      `/api/event?q=${encodeURIComponent(publishedName)}`,
    );
    expect(teacherList.status).toBe(200);
    expect(teacherList.body.data.total).toBe(1);

    const adminList = await scenario.admin.get(
      `/api/event?q=${encodeURIComponent(draftName)}&estado=Pendiente`,
    );
    expect(adminList.status).toBe(200);
    expect(adminList.body.data.total).toBe(1);
  });
});

/* =====================================================================================
 * T27 — inscripción y cupo
 * =================================================================================== */

describe('T27 · inscripción y cupo', () => {
  it('descuenta el cupo, rechaza duplicados y libera el puesto al cancelar', async () => {
    const scenario = await evidenceScenario();
    const third = await createAccount(scenario.admin, 2);

    const event = (await createEvent(scenario.admin, { capacidadMaxima: 2 }))
      .body.data as EventBody;

    const first = await scenario.student.session.post(`/api/event/${event.id}/register`);
    expect(first.status).toBe(200);
    expect(first.body.data).toMatchObject({
      id: event.id,
      cupo: 1,
      inscritos: 1,
      inscrito: true,
    });

    const duplicate = await scenario.student.session.post(`/api/event/${event.id}/register`);
    expect(duplicate.status).toBe(409);
    expect(duplicate.body.error.code).toBe('EVENT_ALREADY_REGISTERED');

    const second = await scenario.otherStudent.session.post(`/api/event/${event.id}/register`);
    expect(second.status).toBe(200);
    expect(second.body.data).toMatchObject({ cupo: 0, inscritos: 2 });

    const full = await third.session.post(`/api/event/${event.id}/register`);
    expect(full.status).toBe(422);
    expect(full.body.error.code).toBe('EVENT_FULL');

    // El docente y el administrador no se inscriben.
    for (const session of [scenario.mentor.session, scenario.admin]) {
      const denied = await session.post(`/api/event/${event.id}/register`);
      expect(denied.status).toBe(403);
    }

    const cancelled = await scenario.student.session.del(`/api/event/${event.id}/register`);
    expect(cancelled.status).toBe(200);
    expect(cancelled.body.data).toMatchObject({ eventoId: event.id, inscrito: false, cupo: 1 });

    const cancelledAgain = await scenario.student.session.del(`/api/event/${event.id}/register`);
    expect(cancelledAgain.status).toBe(404);
    expect(cancelledAgain.body.error.code).toBe('EVENT_REGISTRATION_NOT_FOUND');

    // El puesto liberado se reutiliza.
    const rejoin = await third.session.post(`/api/event/${event.id}/register`);
    expect(rejoin.status).toBe(200);
    expect(rejoin.body.data.cupo).toBe(0);

    // La capacidad no puede quedar por debajo de las inscripciones.
    const below = await scenario.admin
      .put(`/api/event/${event.id}`)
      .send({ capacidadMaxima: 1 });
    expect(below.status).toBe(422);
    expect(below.body.error.code).toBe('EVENT_CAPACITY_BELOW_REGISTRATIONS');

    const audit = await query<{ accion: string }>(
      `SELECT accion FROM auditoria_eventos
        WHERE entidad = 'eventos' AND entidad_id = $1
        ORDER BY id_auditoria`,
      [event.id],
    );
    const actions = audit.rows.map((row) => row.accion);
    expect(actions).toContain('Inscripción a evento');
    expect(actions).toContain('Cancelación de inscripción a evento');
  });

  it('un evento sin registro obligatorio no admite inscripción', async () => {
    const scenario = await evidenceScenario();
    const event = (await createEvent(scenario.admin, { requiereRegistro: false }))
      .body.data as EventBody;

    const response = await scenario.student.session.post(`/api/event/${event.id}/register`);
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('EVENT_REGISTRATION_NOT_REQUIRED');
  });

  it('un evento sin capacidad no tiene tope', async () => {
    const scenario = await evidenceScenario();
    const event = (await createEvent(scenario.admin, { capacidadMaxima: null }))
      .body.data as EventBody;
    expect(event.cupo).toBeNull();

    const first = await scenario.student.session.post(`/api/event/${event.id}/register`);
    expect(first.status).toBe(200);
    expect(first.body.data.cupo).toBeNull();
  });
});

/* =====================================================================================
 * T27 — recomendaciones del docente
 * =================================================================================== */

describe('T27 · recomendaciones', () => {
  it('el docente recomienda solo a sus emprendimientos y el estudiante lo ve', async () => {
    const scenario = await evidenceScenario();
    const event = (await createEvent(scenario.admin)).body.data as EventBody;

    const created = await scenario.mentor.session
      .post(`/api/event/${event.id}/recommendations`)
      .send({
        emprendimientoId: scenario.emprendimientoId,
        mensaje: 'Te servirá para el modelo de negocio.',
      });
    expect(created.status).toBe(201);
    const recommendation = created.body.data as RecommendationBody;
    expect(recommendation).toMatchObject({
      mensaje: 'Te servirá para el modelo de negocio.',
      estado: 'Pendiente',
      evento: { id: event.id, nombreEvento: event.nombreEvento },
      emprendimiento: { id: scenario.emprendimientoId },
      estudiante: { id: scenario.student.id },
      docente: { id: scenario.mentor.id },
    });

    const forStudent = await scenario.student.session.get(
      `/api/event/${event.id}/recommendations`,
    );
    expect(forStudent.status).toBe(200);
    expect(forStudent.body.data.total).toBe(1);
    expect(forStudent.body.data.items[0].id).toBe(recommendation.id);

    const forOtherStudent = await scenario.otherStudent.session.get(
      `/api/event/${event.id}/recommendations`,
    );
    expect(forOtherStudent.status).toBe(200);
    expect(forOtherStudent.body.data.total).toBe(0);

    const forMentor = await scenario.mentor.session.get(
      `/api/event/${event.id}/recommendations`,
    );
    expect(forMentor.status).toBe(200);
    expect(forMentor.body.data.total).toBe(1);

    const forOtherMentor = await scenario.otherMentor.session.get(
      `/api/event/${event.id}/recommendations`,
    );
    expect(forOtherMentor.status).toBe(200);
    expect(forOtherMentor.body.data.total).toBe(0);

    const forAdmin = await scenario.admin.get(`/api/event/${event.id}/recommendations`);
    expect(forAdmin.status).toBe(200);
    expect(forAdmin.body.data.total).toBe(1);

    const { rows: notifications } = await query<{
      tipo: string;
      mensaje: string;
      tipo_objeto: string | null;
      objeto_id: number | null;
    }>(
      `SELECT tipo, mensaje, tipo_objeto, objeto_id
         FROM notificaciones
        WHERE usuarios_id_usuarios = $1 AND tipo_objeto = 'evento' AND objeto_id = $2
        ORDER BY id_notificaciones DESC`,
      [scenario.student.id, event.id],
    );
    expect(notifications[0]).toMatchObject({ tipo: 'Evento', objeto_id: event.id });
    expect(notifications[0]!.mensaje).toContain(event.nombreEvento);
    expect(notifications[0]!.mensaje).toContain('modelo de negocio');
  });

  it('rechaza recomendaciones fuera de alcance y de roles no docentes', async () => {
    const scenario = await evidenceScenario();
    const event = (await createEvent(scenario.admin)).body.data as EventBody;

    const outsider = await scenario.otherMentor.session
      .post(`/api/event/${event.id}/recommendations`)
      .send({ emprendimientoId: scenario.emprendimientoId });
    expect(outsider.status).toBe(404);

    for (const session of [scenario.student.session, scenario.admin]) {
      const denied = await session
        .post(`/api/event/${event.id}/recommendations`)
        .send({ emprendimientoId: scenario.emprendimientoId });
      expect(denied.status).toBe(403);
    }

    const wrongStudent = await scenario.mentor.session
      .post(`/api/event/${event.id}/recommendations`)
      .send({
        emprendimientoId: scenario.emprendimientoId,
        estudianteId: scenario.otherStudent.id,
      });
    expect(wrongStudent.status).toBe(400);
    expect(wrongStudent.body.error.fields.estudianteId).toBeDefined();

    const draft = (await createEvent(scenario.admin, { estado: 'Pendiente' }))
      .body.data as EventBody;
    const onDraft = await scenario.mentor.session
      .post(`/api/event/${draft.id}/recommendations`)
      .send({ emprendimientoId: scenario.emprendimientoId });
    expect(onDraft.status).toBe(404);
  });
});

/* =====================================================================================
 * T27 — validaciones y listado
 * =================================================================================== */

describe('T27 · validaciones y listado', () => {
  it('valida el cuerpo y el horario del evento', async () => {
    const scenario = await evidenceScenario();

    const extra = await scenario.admin
      .post('/api/event')
      .send({ ...eventPayload(), organizadorId: scenario.student.id });
    expect(extra.status).toBe(400);

    const partial = await scenario.admin
      .post('/api/event')
      .send({ ...eventPayload(), horaFin: undefined });
    expect(partial.status).toBe(400);

    const backwards = await scenario.admin
      .post('/api/event')
      .send(eventPayload({ horaInicio: '12:00', horaFin: '10:00' }));
    expect(backwards.status).toBe(400);

    const zero = await scenario.admin
      .post('/api/event')
      .send(eventPayload({ capacidadMaxima: 0 }));
    expect(zero.status).toBe(400);

    const unknownCatalog = await scenario.admin
      .post('/api/event')
      .send(eventPayload({ tipoEventoId: 999999 }));
    expect(unknownCatalog.status).toBe(400);
    expect(unknownCatalog.body.error.fields.tipoEventoId).toBeDefined();

    const noName = await scenario.admin.post('/api/event').send(eventPayload({ nombreEvento: ' ' }));
    expect(noName.status).toBe(400);
  });

  it('valida la paginación, el orden y los filtros del listado', async () => {
    const scenario = await evidenceScenario();

    for (const path of [
      '/api/event?pageSize=101',
      '/api/event?sort=descripcion',
      '/api/event?order=random',
      '/api/event?orderBy=id',
      '/api/event?desde=2026-13-01',
    ]) {
      const response = await scenario.admin.get(path);
      expect(response.status).toBe(400);
    }

    const event = (await createEvent(scenario.admin, { tipoEventoId: 1, modalidadId: 1 }))
      .body.data as EventBody;

    const filtered = await scenario.admin.get(
      `/api/event?tipoEventoId=1&modalidadId=1&desde=2026-12-15&hasta=2026-12-15&q=${encodeURIComponent(
        event.nombreEvento,
      )}`,
    );
    expect(filtered.status).toBe(200);
    expect(filtered.body.data.total).toBe(1);
    expect(filtered.body.data.items[0].id).toBe(event.id);
  });
});
