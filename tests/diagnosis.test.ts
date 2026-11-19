import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import type { Session } from './api.js';
import { createAccount, evidenceScenario, type Scenario } from './fixtures.js';

/**
 * T25 — diagnóstico de caracterización (FR-002).
 *
 * El caso central es la bandera de la rúbrica (AQ-09): con `rubrica_diagnostico_aprobada`
 * en `false` el instrumento se guarda y se envía, pero **no** se produce puntaje, no se
 * escriben `valoracion` ni `caracterizacion`, y cada lectura lo declara con
 * `RUBRIC_NOT_CONFIGURED`.
 */

beforeEach(async () => {
  resetRateLimits();
});

afterAll(async () => {
  await closePool();
});

interface Question {
  id: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string[];
}

interface DiagnosisBody {
  id: number;
  estado: string;
  fechaDiagnostico: string;
  puntajeTotal: number | null;
  urlInforme: string | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: { id: number; correoInstitucional: string };
  respuestas: { id: number; valor: string }[];
  totalPreguntas: number;
  respondidas: number;
  puntuacion: { disponible: boolean; motivo: string; mensaje: string };
}

async function loadForm(session: Session): Promise<Question[]> {
  const response = await session.get('/api/diagnosis/form');
  expect(response.status).toBe(200);
  expect(response.body.data.total).toBe(22);
  expect(response.body.data.secciones).toHaveLength(5);
  return response.body.data.preguntas as Question[];
}

/** Respuesta válida para cualquier pregunta: la primera opción o un texto libre. */
function answerFor(question: Question): string {
  return question.opciones[0] ?? 'Respuesta de prueba';
}

function allAnswers(questions: Question[]): { preguntaId: number; valor: string }[] {
  return questions.map((question) => ({
    preguntaId: question.id,
    valor: answerFor(question),
  }));
}

async function save(
  session: Session,
  emprendimientoId: number,
  respuestas: { preguntaId: number; valor: string }[],
  enviar = false,
) {
  return session.post('/api/diagnosis/me').send({
    emprendimientoId,
    respuestas,
    enviar,
  });
}

async function diagnosisCount(emprendimientoId: number): Promise<number> {
  const { rows } = await query<{ total: string }>(
    'SELECT COUNT(*)::text AS total FROM diagnosticos WHERE emprendimiento_id_emprendimiento = $1',
    [emprendimientoId],
  );
  return Number(rows[0]!.total);
}

/* =====================================================================================
 * T25 — instrumento, borrador y envío
 * =================================================================================== */

describe('T25 · diagnóstico sin rúbrica', () => {
  it('guarda el borrador, reutiliza la fila y no puntúa', async () => {
    const scenario = await evidenceScenario();
    const questions = await loadForm(scenario.student.session);

    const draft = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [{ preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) }],
    );

    expect(draft.status).toBe(200);
    const body = draft.body.data as DiagnosisBody;
    expect(body.estado).toBe('En progreso');
    expect(body.respondidas).toBe(1);
    expect(body.totalPreguntas).toBe(22);
    expect(body.puntajeTotal).toBeNull();
    expect(body.urlInforme).toBeNull();
    expect(body.puntuacion).toEqual({
      disponible: false,
      motivo: 'RUBRIC_NOT_CONFIGURED',
      mensaje: expect.stringContaining('no se produce puntaje'),
    });
    expect(body.respuestas).toHaveLength(1);

    // El segundo guardado reutiliza el mismo diagnóstico y actualiza la respuesta.
    const second = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [
        { preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) },
        { preguntaId: questions[1]!.id, valor: answerFor(questions[1]!) },
      ],
    );
    expect(second.status).toBe(200);
    expect(second.body.data.id).toBe(body.id);
    expect(second.body.data.respondidas).toBe(2);
    expect(await diagnosisCount(scenario.emprendimientoId)).toBe(1);

    const mine = await scenario.student.session.get('/api/diagnosis/me');
    expect(mine.status).toBe(200);
    expect(mine.body.data.id).toBe(body.id);
  });

  it('no envía un cuestionario incompleto y bloquea el envío definitivo', async () => {
    const scenario = await evidenceScenario();
    const questions = await loadForm(scenario.student.session);

    const incomplete = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [{ preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) }],
      true,
    );
    expect(incomplete.status).toBe(422);
    expect(incomplete.body.error.code).toBe('DIAGNOSIS_INCOMPLETE');
    expect(incomplete.body.error.fields.respuestas).toBeDefined();

    const sent = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      allAnswers(questions),
      true,
    );
    expect(sent.status).toBe(200);
    const body = sent.body.data as DiagnosisBody;
    expect(body.estado).toBe('Enviado');
    expect(body.respondidas).toBe(22);
    expect(body.puntajeTotal).toBeNull();

    // Sin rúbrica no hay filas de valoración ni de caracterización (AQ-09).
    const [valoracion, caracterizacion] = await Promise.all([
      query('SELECT 1 FROM valoracion WHERE diagnosticos_id_diagnosticos = $1', [body.id]),
      query('SELECT 1 FROM caracterizacion WHERE diagnosticos_id_diagnosticos = $1', [body.id]),
    ]);
    expect(valoracion.rowCount).toBe(0);
    expect(caracterizacion.rowCount).toBe(0);

    const again = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [{ preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) }],
    );
    expect(again.status).toBe(422);
    expect(again.body.error.code).toBe('DIAGNOSIS_ALREADY_SUBMITTED');

    const auditoria = await query<{ valor_nuevo: Record<string, unknown> }>(
      `SELECT valor_nuevo FROM auditoria_eventos
        WHERE entidad = 'diagnosticos' AND entidad_id = $1 AND accion = 'Envío de diagnóstico'`,
      [body.id],
    );
    expect(auditoria.rows[0]!.valor_nuevo).toMatchObject({
      estado: 'Enviado',
      respondidas: 22,
      puntajeTotal: null,
      motivo: 'RUBRIC_NOT_CONFIGURED',
    });
  });

  it('rechaza preguntas inexistentes, valores fuera de opciones y campos de más', async () => {
    const scenario = await evidenceScenario();
    const questions = await loadForm(scenario.student.session);
    const single = questions.find((question) => question.opciones.length > 0)!;

    const unknown = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [{ preguntaId: 999999, valor: 'x' }],
    );
    expect(unknown.status).toBe(400);
    expect(unknown.body.error.fields['respuestas.0.preguntaId']).toBeDefined();

    const invalid = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      [{ preguntaId: single.id, valor: 'No es una opción' }],
    );
    expect(invalid.status).toBe(400);
    expect(invalid.body.error.fields['respuestas.0.valor']).toBeDefined();

    const extra = await scenario.student.session.post('/api/diagnosis/me').send({
      emprendimientoId: scenario.emprendimientoId,
      respuestas: [{ preguntaId: questions[0]!.id, valor: 'x' }],
      puntajeTotal: 100,
    });
    expect(extra.status).toBe(400);

    const duplicate = await save(scenario.student.session, scenario.emprendimientoId, [
      { preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) },
      { preguntaId: questions[0]!.id, valor: answerFor(questions[0]!) },
    ]);
    expect(duplicate.status).toBe(400);
  });

  it('expone el informe y la caracterización sin puntaje', async () => {
    const scenario = await evidenceScenario();
    const questions = await loadForm(scenario.student.session);
    const sent = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      allAnswers(questions),
      true,
    );
    const id = sent.body.data.id as number;

    const report = await scenario.student.session.get(`/api/diagnosis/${id}/report`);
    expect(report.status).toBe(200);
    expect(report.body.data.diagnostico.id).toBe(id);
    expect(report.body.data.informe).toMatchObject({
      disponible: false,
      motivo: 'RUBRIC_NOT_CONFIGURED',
      urlInforme: null,
      valoracion: [],
    });
    expect(report.body.data.informe.secciones).toHaveLength(5);
    for (const section of report.body.data.informe.secciones) {
      expect(section.puntaje).toBeNull();
      expect(section.resultado).toBeNull();
    }

    const characterization = await scenario.student.session.get('/api/characterization/me');
    expect(characterization.status).toBe(200);
    expect(characterization.body.data).toMatchObject({
      diagnosticoId: id,
      estado: 'Enviado',
      respondidas: 22,
      totalPreguntas: 22,
      puntuacion: { disponible: false, motivo: 'RUBRIC_NOT_CONFIGURED' },
      valoracion: [],
    });
    expect(characterization.body.data.secciones).toHaveLength(5);
    expect(
      characterization.body.data.secciones.reduce(
        (sum: number, section: { respondidas: number }) => sum + section.respondidas,
        0,
      ),
    ).toBe(22);
  });
});

/* =====================================================================================
 * T25 — alcance por rol y cuenta Limitado
 * =================================================================================== */

describe('T25 · alcance del diagnóstico', () => {
  it('lo ven el administrador, el docente asignado y el dueño; nadie más', async () => {
    const scenario = await evidenceScenario();
    const questions = await loadForm(scenario.student.session);
    const sent = await save(
      scenario.student.session,
      scenario.emprendimientoId,
      allAnswers(questions),
      true,
    );
    const id = sent.body.data.id as number;

    for (const session of [scenario.admin, scenario.student.session, scenario.mentor.session]) {
      const response = await session.get(`/api/diagnosis/${id}`);
      expect(response.status).toBe(200);
      expect(response.body.data.id).toBe(id);
    }

    for (const session of [scenario.otherStudent.session, scenario.otherMentor.session]) {
      const response = await session.get(`/api/diagnosis/${id}`);
      expect(response.status).toBe(404);
    }

    const list = await scenario.admin.get('/api/diagnosis?pageSize=100');
    expect(list.status).toBe(200);
    expect(
      (list.body.data.items as { id: number }[]).some((item) => item.id === id),
    ).toBe(true);

    const asMentor = await scenario.mentor.session.get('/api/diagnosis?pageSize=100');
    expect(asMentor.status).toBe(200);
    expect(
      (asMentor.body.data.items as { id: number }[]).some((item) => item.id === id),
    ).toBe(true);

    const asOtherMentor = await scenario.otherMentor.session.get('/api/diagnosis?pageSize=100');
    expect(asOtherMentor.status).toBe(200);
    expect(asOtherMentor.body.data.total).toBe(0);
  });

  it('una cuenta Limitado no llega al instrumento', async () => {
    const scenario = await evidenceScenario();
    const limited = await createAccount(scenario.admin, 2, 'Limitado');

    const form = await limited.session.get('/api/diagnosis/form');
    expect(form.status).toBe(403);
    expect(form.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');

    const mine = await limited.session.get('/api/diagnosis/me');
    expect(mine.status).toBe(403);
    expect(mine.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });

  it('un estudiante sin emprendimiento recibe ENTREPRENEURSHIP_REQUIRED', async () => {
    const scenario = await evidenceScenario();
    const student = await createAccount(scenario.admin, 2);

    const mine = await student.session.get('/api/diagnosis/me');
    expect(mine.status).toBe(422);
    expect(mine.body.error.code).toBe('ENTREPRENEURSHIP_REQUIRED');

    const draft = await student.session
      .post('/api/diagnosis/me')
      .send({ respuestas: [{ preguntaId: 1, valor: 'x' }] });
    expect(draft.status).toBe(422);
    expect(draft.body.error.code).toBe('ENTREPRENEURSHIP_REQUIRED');
  });

  it('valida la paginación y el orden del listado', async () => {
    const scenario = await evidenceScenario();

    for (const path of [
      '/api/diagnosis?pageSize=101',
      '/api/diagnosis?sort=puntaje',
      '/api/diagnosis?order=random',
      '/api/diagnosis?orderBy=id',
    ]) {
      const response = await scenario.admin.get(path);
      expect(response.status).toBe(400);
    }
  });
});
