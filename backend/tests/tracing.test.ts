import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import type { Session } from './api.js';
import {
  evidenceScenario,
  fileExists,
  jpegBuffer,
  storedPath,
  uploadEvidence,
  type Scenario,
} from './fixtures.js';
import { clearMailbox } from './helpers.js';

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

function createTracing(
  actor: Session,
  emprendimientoId: number,
  overrides: Record<string, unknown> = {},
) {
  return actor.post('/api/tracing').send({
    emprendimientoId,
    tipoSeguimiento: 'Avance de fase',
    descripcion: 'Prototipo de empaque listo para 20 unidades.',
    fasePlanId: 2,
    puntaje: 80,
    ...overrides,
  });
}

async function auditRows(entidadId: number, accion: string) {
  const { rows } = await query<{ valor_nuevo: Record<string, unknown> | null }>(
    `SELECT valor_nuevo
       FROM auditoria_eventos
      WHERE entidad = 'seguimientos' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

describe('seguimientos · alta', () => {
  it('registra un avance de fase con su autor y avisa al estudiante', async () => {
    const scenario = await evidenceScenario();

    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    expect(created.status).toBe(201);
    expect(created.body.data).toMatchObject({
      descripcion: 'Prototipo de empaque listo para 20 unidades.',
      tipo: 'Avance de fase',
      puntaje: 80,
      estadoRevision: 'Pendiente',
      autor: { id: scenario.mentor.id },
      emprendimiento: { id: scenario.emprendimientoId },
      fase: { id: 2 },
      evidencias: 0,
    });

    const id = created.body.data.id as number;
    expect(await auditRows(id, 'Alta de seguimiento')).toHaveLength(1);

    const { rows } = await query<{ usuarios_id_usuarios: number; tipo: string; mensaje: string }>(
      `SELECT usuarios_id_usuarios, tipo, mensaje
         FROM notificaciones
        WHERE tipo_objeto = 'seguimientos' AND objeto_id = $1`,
      [id],
    );
    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({ usuarios_id_usuarios: scenario.student.id, tipo: 'Seguimiento' });
    expect(rows[0]!.mensaje).toContain('Prototipo de empaque');
  });

  it('exige la fase en un avance de fase y la omite en un comentario', async () => {
    const scenario = await evidenceScenario();

    const withoutPhase = await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      fasePlanId: null,
    });
    expect(withoutPhase.status).toBe(400);
    expect(withoutPhase.body.error.fields.fasePlanId).toBeTruthy();

    const comment = await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      tipoSeguimiento: 'Comentario',
      fasePlanId: null,
      puntaje: null,
      descripcion: 'Recuerda que las fotos deben incluir la fecha de toma.',
    });
    expect(comment.status).toBe(201);
    expect(comment.body.data).toMatchObject({ tipo: 'Comentario', fase: null, puntaje: null });
  });

  it('guarda la fecha del avance a mediodía de Bogotá', async () => {
    const scenario = await evidenceScenario();

    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      fechaSeguimiento: '2026-03-10',
    });
    expect(created.status).toBe(201);

    const localDate = new Date(created.body.data.fechaSeguimiento as string).toLocaleDateString(
      'en-CA',
      { timeZone: 'America/Bogota' },
    );
    expect(localDate).toBe('2026-03-10');
  });

  it('solo escribe el docente asignado o el administrador', async () => {
    const scenario = await evidenceScenario();

    expect(
      (await createTracing(scenario.student.session, scenario.emprendimientoId)).status,
    ).toBe(403);
    expect(
      (await createTracing(scenario.otherMentor.session, scenario.emprendimientoId)).status,
    ).toBe(404);
    expect(
      (await createTracing(scenario.admin, scenario.emprendimientoId)).status,
    ).toBe(201);
  });

  it('rechaza una fase que no existe en el catálogo', async () => {
    const scenario = await evidenceScenario();

    const response = await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      fasePlanId: 999,
    });
    expect(response.status).toBe(400);
    expect(response.body.error.fields.fasePlanId).toBeTruthy();
  });
});

describe('seguimientos · lectura', () => {
  it('lista por emprendimiento con alcance por rol', async () => {
    const scenario = await evidenceScenario();
    await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      tipoSeguimiento: 'Comentario',
      fasePlanId: null,
      descripcion: 'Comentario del docente.',
    });

    const mentorView = await scenario.mentor.session.get(
      `/api/tracing/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(mentorView.status).toBe(200);
    expect(mentorView.body.data.total).toBe(2);

    const studentView = await scenario.student.session.get(
      `/api/tracing/entrepreneurship/${scenario.emprendimientoId}`,
    );
    expect(studentView.body.data.total).toBe(2);

    expect(
      (
        await scenario.otherStudent.session.get(
          `/api/tracing/entrepreneurship/${scenario.emprendimientoId}`,
        )
      ).status,
    ).toBe(404);
    expect(
      (
        await scenario.otherMentor.session.get(
          `/api/tracing/entrepreneurship/${scenario.emprendimientoId}`,
        )
      ).status,
    ).toBe(404);
  });

  it('filtra por tipo y estado de revisión y valida la consulta', async () => {
    const scenario = await evidenceScenario();
    await createTracing(scenario.mentor.session, scenario.emprendimientoId, {
      tipoSeguimiento: 'Comentario',
      fasePlanId: null,
      estadoRevision: 'Calificada',
      descripcion: 'Comentario calificado.',
    });
    await createTracing(scenario.mentor.session, scenario.emprendimientoId);

    const filtered = await scenario.mentor.session.get(
      `/api/tracing/entrepreneurship/${scenario.emprendimientoId}?tipo=Comentario&estadoRevision=Calificada`,
    );
    expect(filtered.status).toBe(200);
    expect(filtered.body.data.total).toBe(1);

    const base = `/api/tracing/entrepreneurship/${scenario.emprendimientoId}`;
    expect((await scenario.mentor.session.get(`${base}?tipo=Inventado`)).status).toBe(400);
    expect((await scenario.mentor.session.get(`${base}?sort=descripcion`)).status).toBe(400);
    expect((await scenario.mentor.session.get(`${base}?pageSize=0`)).status).toBe(400);
  });

  it('un seguimiento ajeno responde 404', async () => {
    const scenario = await evidenceScenario();
    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    const id = created.body.data.id as number;

    expect((await scenario.mentor.session.get(`/api/tracing/${id}`)).status).toBe(200);
    expect((await scenario.otherStudent.session.get(`/api/tracing/${id}`)).status).toBe(404);
    expect((await scenario.otherMentor.session.get(`/api/tracing/${id}`)).status).toBe(404);
    expect((await scenario.admin.get(`/api/tracing/${id}`)).status).toBe(200);
  });
});

describe('seguimientos · edición y baja', () => {
  it('solo el autor o el administrador editan', async () => {
    const scenario = await evidenceScenario();
    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    const id = created.body.data.id as number;

    const byAuthor = await scenario.mentor.session
      .put(`/api/tracing/${id}`)
      .send({ puntaje: 95, retroalimentacion: 'Buen avance.' });
    expect(byAuthor.status).toBe(200);
    expect(byAuthor.body.data).toMatchObject({
      puntaje: 95,
      retroalimentacion: 'Buen avance.',
    });
    expect(await auditRows(id, 'Edición de seguimiento')).toHaveLength(1);

    const byAdmin = await scenario.admin
      .put(`/api/tracing/${id}`)
      .send({ estadoRevision: 'Calificada' });
    expect(byAdmin.status).toBe(200);
    expect(byAdmin.body.data.estadoRevision).toBe('Calificada');

    expect(
      (await scenario.otherMentor.session.put(`/api/tracing/${id}`).send({ puntaje: 10 })).status,
    ).toBe(404);
    expect(
      (await scenario.student.session.put(`/api/tracing/${id}`).send({ puntaje: 10 })).status,
    ).toBe(403);
  });

  it('la baja es lógica y borra la evidencia del disco (BR-006)', async () => {
    const scenario = await evidenceScenario();
    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    const id = created.body.data.id as number;

    const uploaded = await uploadEvidence(
      scenario.mentor.session,
      'tracing',
      id,
      jpegBuffer(),
      'ficha-tecnica.jpg',
    );
    expect(uploaded.status).toBe(201);
    const attachmentId = uploaded.body.data.id as number;
    const path = await storedPath(attachmentId);
    expect(await fileExists(path)).toBe(true);

    const removed = await scenario.mentor.session.del(`/api/tracing/${id}`);
    expect(removed.status).toBe(200);

    expect((await scenario.mentor.session.get(`/api/tracing/${id}`)).status).toBe(404);
    expect(await fileExists(path)).toBe(false);
    expect((await scenario.mentor.session.get(`/api/attachments/${attachmentId}`)).status).toBe(404);

    const { rows } = await query<{ fecha_eliminacion: Date | null }>(
      'SELECT fecha_eliminacion FROM seguimientos WHERE id_seguimientos = $1',
      [id],
    );
    expect(rows[0]!.fecha_eliminacion).not.toBeNull();
    expect(await auditRows(id, 'Baja lógica de seguimiento')).toHaveLength(1);
  });

  it('un docente ajeno no puede dar de baja el seguimiento', async () => {
    const scenario = await evidenceScenario();
    const created = await createTracing(scenario.mentor.session, scenario.emprendimientoId);
    const id = created.body.data.id as number;

    expect((await scenario.otherMentor.session.del(`/api/tracing/${id}`)).status).toBe(404);
    expect((await scenario.student.session.del(`/api/tracing/${id}`)).status).toBe(403);
  });
});
