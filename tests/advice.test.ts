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

/**
 * T20 y T35 — asesorías (FR-004, FR-015, BR-002).
 *
 * Cada caso monta su propio escenario (`evidenceScenario`): un emprendimiento aprobado,
 * un estudiante dueño, un docente con asignación activa y un docente ajeno. Así el
 * alcance por rol se prueba contra datos reales y no contra el seed compartido.
 */

beforeEach(async () => {
  resetRateLimits();
});

afterAll(async () => {
  await closePool();
});

const SCHEDULE = { fecha: '2026-12-01', horaInicio: '09:00', horaFin: '10:00' };

interface AdviceBody {
  id: number;
  codigo: string;
  tema: string;
  estado: string;
  fecha: string | null;
  horaInicio: string | null;
  horaFin: string | null;
  fechaAsesoria: string | null;
  lugarEnlace: string | null;
  modalidad: { id: number; nombre: string } | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: { id: number };
  docente: { id: number } | null;
  evidencias: number;
}

async function createAdvice(
  admin: Session,
  scenario: Scenario,
  overrides: Record<string, unknown> = {},
) {
  return admin.post('/api/advice').send({
    emprendimientoId: scenario.emprendimientoId,
    docenteId: scenario.mentor.id,
    tema: 'Revisión del modelo de negocio',
    modalidadId: 2,
    lugarEnlace: 'https://meet.example.com/asesoria',
    ...SCHEDULE,
    ...overrides,
  });
}

async function adviceRow(id: number) {
  const { rows } = await query<{
    estado: string;
    tema: string;
    lugar_enlace: string | null;
    usuarios_id_docentes: number | null;
    usuarios_id_usuarios: number;
    fecha_eliminacion: Date | null;
  }>(
    `SELECT estado, tema, lugar_enlace, usuarios_id_docentes, usuarios_id_usuarios,
            fecha_eliminacion
       FROM asesorias WHERE id_asesorias = $1`,
    [id],
  );
  return rows[0]!;
}

async function auditRows(entidadId: number, accion: string) {
  const { rows } = await query<{
    valor_anterior: Record<string, unknown> | null;
    valor_nuevo: Record<string, unknown> | null;
  }>(
    `SELECT valor_anterior, valor_nuevo
       FROM auditoria_eventos
      WHERE entidad = 'asesorias' AND entidad_id = $1 AND accion = $2
      ORDER BY id_auditoria DESC`,
    [entidadId, accion],
  );
  return rows;
}

async function notificationsAbout(usuarioId: number, asesoriaId: number) {
  const { rows } = await query<{ tipo: string; mensaje: string; url: string | null }>(
    `SELECT tipo, mensaje, url
       FROM notificaciones
      WHERE usuarios_id_usuarios = $1 AND tipo_objeto = 'asesorias' AND objeto_id = $2
      ORDER BY id_notificaciones DESC`,
    [usuarioId, asesoriaId],
  );
  return rows;
}

/* =====================================================================================
 * T20 — el estudiante no crea ni confirma
 * =================================================================================== */

describe('T20 · BR-002: el estudiante solicita, no agenda', () => {
  it('no puede crear, editar ni confirmar una asesoría', async () => {
    const scenario = await evidenceScenario();

    const creada = await createAdvice(scenario.admin, scenario);
    expect(creada.status).toBe(201);
    const advice = creada.body.data as AdviceBody;

    expect(advice).toMatchObject({
      estado: 'Programada',
      tema: 'Revisión del modelo de negocio',
      fecha: SCHEDULE.fecha,
      horaInicio: SCHEDULE.horaInicio,
      horaFin: SCHEDULE.horaFin,
      modalidad: { id: 2, nombre: 'Virtual' },
      emprendimiento: { id: scenario.emprendimientoId },
      estudiante: { id: scenario.student.id },
      docente: { id: scenario.mentor.id },
      evidencias: 0,
    });
    expect(advice.codigo).toMatch(/^ASES-\d{3,}$/);

    // El estudiante la ve (es suya) pero no la toca.
    const leida = await scenario.student.session.get(`/api/advice/${advice.id}`);
    expect(leida.status).toBe(200);

    for (const response of [
      await scenario.student.session.post('/api/advice').send({
        emprendimientoId: scenario.emprendimientoId,
        docenteId: scenario.mentor.id,
        tema: 'Intento de autoagenda',
      }),
      await scenario.student.session.put(`/api/advice/${advice.id}`).send({
        tema: 'Cambio no autorizado',
      }),
      await scenario.student.session.post(`/api/advice/${advice.id}/accept`).send({}),
      await scenario.student.session.post(`/api/advice/${advice.id}/reject`).send({
        motivo: 'No puedo',
      }),
      await scenario.student.session.del(`/api/advice/${advice.id}`),
    ]) {
      expect(response.status).toBe(403);
      expect(response.body.error.code).toBe('ROLE_NOT_ALLOWED');
    }

    expect((await adviceRow(advice.id)).estado).toBe('Programada');
  });

  it('un docente solo agenda para sí mismo y en sus emprendimientos asignados', async () => {
    const scenario = await evidenceScenario();

    const ajeno = await scenario.mentor.session.post('/api/advice').send({
      emprendimientoId: scenario.emprendimientoId,
      docenteId: scenario.otherMentor.id,
      tema: 'Para otro docente',
    });
    expect(ajeno.status).toBe(403);

    const propio = await scenario.mentor.session.post('/api/advice').send({
      emprendimientoId: scenario.emprendimientoId,
      docenteId: scenario.mentor.id,
      tema: 'Asesoría del mentor',
      ...SCHEDULE,
    });
    expect(propio.status).toBe(201);

    // Un docente sin asignación activa no ve el expediente: 404, no 403.
    const sinAsignacion = await scenario.otherMentor.session.post('/api/advice').send({
      emprendimientoId: scenario.emprendimientoId,
      docenteId: scenario.otherMentor.id,
      tema: 'Sin vínculo',
    });
    expect(sinAsignacion.status).toBe(404);
  });
});

/* =====================================================================================
 * Ciclo de vida
 * =================================================================================== */

describe('T20 · ciclo de vida de la asesoría', () => {
  it('Por agendar → Confirmada → En curso → Completada, con auditoría', async () => {
    const scenario = await evidenceScenario();

    const alta = await createAdvice(scenario.admin, scenario, {
      fecha: undefined,
      horaInicio: undefined,
      horaFin: undefined,
    });
    expect(alta.status).toBe(201);
    expect(alta.body.data).toMatchObject({
      estado: 'Por agendar',
      fecha: null,
      horaInicio: null,
      fechaAsesoria: null,
    });

    const id = alta.body.data.id as number;

    const sinHorario = await scenario.mentor.session.post(`/api/advice/${id}/accept`).send({});
    expect(sinHorario.status).toBe(422);
    expect(sinHorario.body.error.code).toBe('ADVICE_NOT_SCHEDULED');

    const confirmada = await scenario.mentor.session
      .post(`/api/advice/${id}/accept`)
      .send(SCHEDULE);
    expect(confirmada.status).toBe(200);
    expect(confirmada.body.data).toMatchObject({
      estado: 'Confirmada',
      fecha: SCHEDULE.fecha,
      horaInicio: SCHEDULE.horaInicio,
      horaFin: SCHEDULE.horaFin,
    });

    const enCurso = await scenario.mentor.session
      .put(`/api/advice/${id}`)
      .send({ estado: 'En curso' });
    expect(enCurso.status).toBe(200);
    expect(enCurso.body.data.estado).toBe('En curso');

    const completada = await scenario.mentor.session
      .put(`/api/advice/${id}`)
      .send({ estado: 'Completada' });
    expect(completada.status).toBe(200);
    expect(completada.body.data.estado).toBe('Completada');

    const repetida = await scenario.mentor.session
      .put(`/api/advice/${id}`)
      .send({ estado: 'En curso' });
    expect(repetida.status).toBe(422);
    expect(repetida.body.error.code).toBe('INVALID_ADVICE_TRANSITION');

    const rechazarCompletada = await scenario.mentor.session
      .post(`/api/advice/${id}/reject`)
      .send({ motivo: 'Ya terminó' });
    expect(rechazarCompletada.status).toBe(422);

    expect(await auditRows(id, 'Confirmación de asesoría')).toHaveLength(1);
    expect(await auditRows(id, 'Edición de asesoría')).toHaveLength(2);
    expect((await adviceRow(id)).estado).toBe('Completada');

    // El estudiante recibe los avisos del ciclo.
    const avisos = await notificationsAbout(scenario.student.id, id);
    expect(avisos.some((item) => /confirmada/i.test(item.mensaje))).toBe(true);
    expect(avisos.some((item) => /en curso/i.test(item.mensaje))).toBe(true);
    expect(avisos.some((item) => /completada/i.test(item.mensaje))).toBe(true);
  });

  it('propone otra fecha y rechaza con motivo obligatorio', async () => {
    const scenario = await evidenceScenario();
    const alta = await createAdvice(scenario.admin, scenario);
    const id = alta.body.data.id as number;

    const nueva = {
      fecha: '2026-12-04',
      horaInicio: '14:00',
      horaFin: '15:00',
    };

    const repropuesta = await scenario.mentor.session
      .post(`/api/advice/${id}/repropose`)
      .send(nueva);
    expect(repropuesta.status).toBe(200);
    expect(repropuesta.body.data).toMatchObject({
      estado: 'Programada',
      fecha: nueva.fecha,
      horaInicio: nueva.horaInicio,
      horaFin: nueva.horaFin,
    });

    const parcial = await scenario.mentor.session
      .post(`/api/advice/${id}/repropose`)
      .send({ fecha: '2026-12-05' });
    expect(parcial.status).toBe(400);

    const sinMotivo = await scenario.mentor.session
      .post(`/api/advice/${id}/reject`)
      .send({});
    expect(sinMotivo.status).toBe(400);
    expect(sinMotivo.body.error.fields).toHaveProperty('motivo');

    const motivo = 'El docente no tiene disponibilidad';
    const rechazada = await scenario.mentor.session
      .post(`/api/advice/${id}/reject`)
      .send({ motivo });

    expect(rechazada.status).toBe(200);
    expect(rechazada.body.data.estado).toBe('Cancelada');

    const auditoria = await auditRows(id, 'Cancelación de asesoría');
    expect(auditoria[0]!.valor_nuevo).toMatchObject({ estado: 'Cancelada', motivo });

    const aviso = await notificationsAbout(scenario.student.id, id);
    expect(aviso[0]!.mensaje).toContain(motivo);

    // Una cancelada ya no se reprograma ni se confirma.
    for (const response of [
      await scenario.mentor.session.post(`/api/advice/${id}/accept`).send(SCHEDULE),
      await scenario.mentor.session.post(`/api/advice/${id}/repropose`).send(nueva),
    ]) {
      expect(response.status).toBe(422);
      expect(response.body.error.code).toBe('INVALID_ADVICE_TRANSITION');
    }
  });
});

/* =====================================================================================
 * T35 — conflictos de horario
 * =================================================================================== */

describe('T35 · dos sesiones del mismo docente no se solapan', () => {
  it('rechaza el solapamiento, permite horarios contiguos y libera al cancelar', async () => {
    const scenario = await evidenceScenario();

    const primera = await createAdvice(scenario.admin, scenario, {
      tema: 'Primera',
      fecha: '2026-12-08',
      horaInicio: '09:00',
      horaFin: '11:00',
    });
    expect(primera.status).toBe(201);
    const primeraId = primera.body.data.id as number;

    const solapada = await createAdvice(scenario.admin, scenario, {
      tema: 'Solapada',
      fecha: '2026-12-08',
      horaInicio: '10:00',
      horaFin: '12:00',
    });
    expect(solapada.status).toBe(409);
    expect(solapada.body.error.code).toBe('ADVICE_SCHEDULE_CONFLICT');

    const contigua = await createAdvice(scenario.admin, scenario, {
      tema: 'Contigua',
      fecha: '2026-12-08',
      horaInicio: '11:00',
      horaFin: '12:00',
    });
    expect(contigua.status).toBe(201);

    // Otro docente a la misma hora sí puede.
    const otroDocente = await createAdvice(scenario.admin, scenario, {
      tema: 'Otro docente',
      docenteId: scenario.otherMentor.id,
      fecha: '2026-12-08',
      horaInicio: '09:00',
      horaFin: '11:00',
    });
    expect(otroDocente.status).toBe(201);

    // Mover una asesoría sobre otra del mismo docente también se rechaza.
    const contiguaId = contigua.body.data.id as number;
    const mover = await scenario.admin.put(`/api/advice/${contiguaId}`).send({
      fecha: '2026-12-08',
      horaInicio: '10:00',
      horaFin: '11:00',
    });
    expect(mover.status).toBe(409);

    // Reprogramarse a sí misma en el mismo horario no es un conflicto.
    const misma = await scenario.admin.put(`/api/advice/${primeraId}`).send({
      fecha: '2026-12-08',
      horaInicio: '09:00',
      horaFin: '11:00',
    });
    expect(misma.status).toBe(200);

    // Al cancelar, el horario queda libre.
    await scenario.mentor.session
      .post(`/api/advice/${primeraId}/reject`)
      .send({ motivo: 'Se cancela' })
      .expect(200);

    const reutilizado = await createAdvice(scenario.admin, scenario, {
      tema: 'Reutiliza el bloque',
      fecha: '2026-12-08',
      horaInicio: '09:00',
      horaFin: '11:00',
    });
    expect(reutilizado.status).toBe(201);
  });

  it('confirmar con un horario ocupado también falla', async () => {
    const scenario = await evidenceScenario();

    const ocupada = await createAdvice(scenario.admin, scenario, {
      fecha: '2026-12-09',
      horaInicio: '09:00',
      horaFin: '10:00',
    });
    expect(ocupada.status).toBe(201);

    const porAgendar = await createAdvice(scenario.admin, scenario, {
      fecha: undefined,
      horaInicio: undefined,
      horaFin: undefined,
    });
    expect(porAgendar.status).toBe(201);

    const conflicto = await scenario.mentor.session
      .post(`/api/advice/${porAgendar.body.data.id}/accept`)
      .send({ fecha: '2026-12-09', horaInicio: '09:30', horaFin: '10:30' });

    expect(conflicto.status).toBe(409);
    expect(conflicto.body.error.code).toBe('ADVICE_SCHEDULE_CONFLICT');
  });
});

/* =====================================================================================
 * Alcance
 * =================================================================================== */

describe('T20 · alcance de lectura', () => {
  it('el estudiante ajeno y el docente ajeno reciben 404', async () => {
    const scenario = await evidenceScenario();
    const alta = await createAdvice(scenario.admin, scenario);
    const id = alta.body.data.id as number;

    expect((await scenario.otherStudent.session.get(`/api/advice/${id}`)).status).toBe(404);
    expect((await scenario.otherMentor.session.get(`/api/advice/${id}`)).status).toBe(404);
    expect((await scenario.student.session.get(`/api/advice/${id}`)).status).toBe(200);
    expect((await scenario.mentor.session.get(`/api/advice/${id}`)).status).toBe(200);
    expect((await scenario.admin.get(`/api/advice/${id}`)).status).toBe(200);

    const listaEstudiante = await scenario.student.session.get('/api/advice');
    expect(listaEstudiante.status).toBe(200);
    expect(listaEstudiante.body.data.items).toHaveLength(1);
    expect(listaEstudiante.body.data.items[0].id).toBe(id);

    const listaAjeno = await scenario.otherStudent.session.get('/api/advice');
    expect(listaAjeno.body.data.items).toHaveLength(0);

    const listaDocente = await scenario.mentor.session.get('/api/advice');
    expect(listaDocente.body.data.items).toHaveLength(1);

    const listaOtroDocente = await scenario.otherMentor.session.get('/api/advice');
    expect(listaOtroDocente.body.data.items).toHaveLength(0);
  });

  it('filtra por estado, grupo Agendada, fechas y texto', async () => {
    const scenario = await evidenceScenario();

    await createAdvice(scenario.admin, scenario, {
      tema: 'Alfa programada',
      fecha: '2026-12-15',
      horaInicio: '09:00',
      horaFin: '10:00',
    });
    await createAdvice(scenario.admin, scenario, {
      tema: 'Beta por agendar',
      fecha: undefined,
      horaInicio: undefined,
      horaFin: undefined,
    });

    // El administrador ve las asesorías de todos los escenarios que ya corrió la suite:
    // cada consulta se acota al emprendimiento de este caso.
    const scope = { emprendimientoId: scenario.emprendimientoId };

    const agendadas = await scenario.admin
      .get('/api/advice')
      .query({ ...scope, grupo: 'Agendada' });
    expect(agendadas.status).toBe(200);
    expect(agendadas.body.data.items).toHaveLength(1);
    expect(agendadas.body.data.items[0].tema).toBe('Alfa programada');

    const porAgendar = await scenario.admin
      .get('/api/advice')
      .query({ ...scope, estado: 'Por agendar' });
    expect(porAgendar.body.data.items).toHaveLength(1);
    expect(porAgendar.body.data.items[0].tema).toBe('Beta por agendar');

    const rango = await scenario.admin
      .get('/api/advice')
      .query({ ...scope, desde: '2026-12-01', hasta: '2026-12-31' });
    expect(rango.body.data.items).toHaveLength(1);
    expect(rango.body.data.items[0].tema).toBe('Alfa programada');

    const texto = await scenario.admin
      .get('/api/advice')
      .query({ ...scope, q: 'Beta' });
    expect(texto.body.data.items).toHaveLength(1);
    expect(texto.body.data.items[0].tema).toBe('Beta por agendar');
  });
});

/* =====================================================================================
 * Evidencias
 * =================================================================================== */

describe('T20 · evidencias de la asesoría', () => {
  it('las sube el estudiante, el docente o el administrador; se congelan al completar', async () => {
    const scenario = await evidenceScenario();
    const alta = await createAdvice(scenario.admin, scenario);
    const id = alta.body.data.id as number;

    const delEstudiante = await uploadEvidence(
      scenario.student.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(delEstudiante.status).toBe(201);
    expect(delEstudiante.body.data).toMatchObject({ entidad: 'advice', entidadId: id });

    const delDocente = await uploadEvidence(
      scenario.mentor.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(delDocente.status).toBe(201);

    const ajeno = await uploadEvidence(
      scenario.otherStudent.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(ajeno.status).toBe(404);

    const docenteAjeno = await uploadEvidence(
      scenario.otherMentor.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(docenteAjeno.status).toBe(404);

    // Lectura y descarga dentro del alcance.
    const descarga = await scenario.student.session.get(
      `/api/attachments/${delDocente.body.data.id}`,
    );
    expect(descarga.status).toBe(200);
    expect(descarga.headers['content-type']).toBe('image/jpeg');

    const descargaAjena = await scenario.otherStudent.session.get(
      `/api/attachments/${delDocente.body.data.id}`,
    );
    expect(descargaAjena.status).toBe(404);

    // La sesión termina: la evidencia se congela para el estudiante, no para el admin.
    // Primero se confirma (la creación la dejó `Programada`); solo una confirmada pasa a
    // `En curso`.
    await scenario.mentor.session.post(`/api/advice/${id}/accept`).send({}).expect(200);
    await scenario.mentor.session
      .put(`/api/advice/${id}`)
      .send({ estado: 'En curso' })
      .expect(200);
    await scenario.mentor.session
      .put(`/api/advice/${id}`)
      .send({ estado: 'Completada' })
      .expect(200);

    const congelada = await uploadEvidence(
      scenario.student.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(congelada.status).toBe(422);
    expect(congelada.body.error.code).toBe('ADVICE_EVIDENCE_LOCKED');

    const ruta = await storedPath(delEstudiante.body.data.id as number);
    expect(await fileExists(ruta)).toBe(true);

    const borrada = await scenario.admin.del(
      `/api/attachments/${delEstudiante.body.data.id}`,
    );
    expect(borrada.status).toBe(200);
    expect(await fileExists(ruta)).toBe(false);
  });

  it('dar de baja la asesoría borra sus archivos y conserva la fila', async () => {
    const scenario = await evidenceScenario();
    const alta = await createAdvice(scenario.admin, scenario);
    const id = alta.body.data.id as number;

    const subida = await uploadEvidence(
      scenario.student.session,
      'advice',
      id,
      jpegBuffer(),
    );
    expect(subida.status).toBe(201);

    const ruta = await storedPath(subida.body.data.id as number);
    expect(await fileExists(ruta)).toBe(true);

    const baja = await scenario.admin.del(`/api/advice/${id}`);
    expect(baja.status).toBe(200);

    const row = await adviceRow(id);
    expect(row.fecha_eliminacion).not.toBeNull();
    expect(await fileExists(ruta)).toBe(false);

    const leida = await scenario.admin.get(`/api/advice/${id}`);
    expect(leida.status).toBe(404);

    expect(await auditRows(id, 'Baja lógica de asesoría')).toHaveLength(1);
  });
});
