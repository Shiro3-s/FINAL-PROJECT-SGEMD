import type { DiagnosticoEstado } from '@sgemd/shared';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { findEntrepreneurshipForActor } from '../../services/entrepreneurshipAccess.js';
import { notify } from '../../services/notify.js';
import { settingValue, type SqlExecutor } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type { ListDiagnosesQuery, SaveDiagnosisInput } from './schemas.js';

/**
 * Diagnóstico de caracterización (FR-002, T25).
 *
 * El instrumento son las 22 preguntas activas del prototipo. El estudiante guarda
 * borradores y, al enviar, las respuestas quedan bloqueadas (`Enviado`). La revisión
 * docente y el puntaje dependen de la rúbrica de AQ-09: mientras no esté cargada, no se
 * escribe `puntaje_total`, no se crean filas de `valoracion` ni de `caracterizacion` y la
 * API declara `RUBRIC_NOT_CONFIGURED` en cada lectura.
 *
 * Un emprendimiento tiene **un** diagnóstico inicial: el borrador se reutiliza hasta el
 * envío y, una vez enviado, no se abre otro (`422 DIAGNOSIS_ALREADY_SUBMITTED`).
 */

const SECTION_TITLES = [
  'Perfil del emprendimiento',
  'Problema o necesidad',
  'Propuesta de valor',
  'Mercado objetivo',
  'Capacidad operativa y financiera',
] as const;

export interface DiagnosisQuestion {
  id: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string[];
}

export interface DiagnosisAnswer extends DiagnosisQuestion {
  valor: string;
}

export interface RubricStatus {
  disponible: boolean;
  motivo: string;
  mensaje: string;
}

export interface Diagnosis {
  id: number;
  estado: DiagnosticoEstado;
  fechaDiagnostico: string;
  puntajeTotal: number | null;
  urlInforme: string | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: {
    id: number;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  };
  respuestas: DiagnosisAnswer[];
  totalPreguntas: number;
  respondidas: number;
  puntuacion: RubricStatus;
}

export interface DiagnosisSummary {
  id: number;
  estado: DiagnosticoEstado;
  fechaDiagnostico: string;
  puntajeTotal: number | null;
  respondidas: number;
  totalPreguntas: number;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: { id: number; nombres: string; apellidos: string };
  puntuacion: RubricStatus;
}

interface EntrepreneurshipRef {
  id: number;
  codigo: string;
  nombre: string;
  sectorId: number | null;
}

type QuestionRow = {
  id_pregunta: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string | null;
};

type DiagnosisRow = {
  id_diagnosticos: number;
  respondidas: number;
  estado: string;
  fecha_diagnostico: Date;
  puntaje_total: number | null;
  url_informe: string | null;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  estudiante_id: number;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_correo: string;
};

type AnswerRow = QuestionRow & { valor: string };

const SELECT_DIAGNOSIS = `
  SELECT d.id_diagnosticos, d.estado, d.fecha_diagnostico, d.puntaje_total, d.url_informe,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         u.id_usuarios AS estudiante_id,
         u.nombres AS estudiante_nombres,
         u.apellidos AS estudiante_apellidos,
         u.correo_institucional AS estudiante_correo,
         (SELECT COUNT(*)::int
            FROM respuestas_diagnostico r
           WHERE r.diagnosticos_id_diagnosticos = d.id_diagnosticos) AS respondidas
    FROM diagnosticos d
    JOIN emprendimiento e ON e.id_emprendimiento = d.emprendimiento_id_emprendimiento
    JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
`;

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El diagnóstico no existe.');
}

function optionsOf(raw: string | null): string[] {
  return raw ? raw.split('|') : [];
}

function mapQuestion(row: QuestionRow): DiagnosisQuestion {
  return {
    id: row.id_pregunta,
    seccion: row.seccion,
    orden: row.orden,
    enunciado: row.enunciado,
    tipo: row.tipo,
    opciones: optionsOf(row.opciones),
  };
}

/**
 * Estado de la rúbrica (AQ-09).
 *
 * La bandera `rubrica_diagnostico_aprobada` se lee para explicar el motivo, pero no basta
 * para puntuar: el repositorio no tiene dimensiones, pesos ni fórmula aprobados. Sin ellos
 * no se inventa un cálculo.
 */
export async function rubricStatus(db: SqlExecutor): Promise<RubricStatus> {
  const flag = await settingValue(db, 'rubrica_diagnostico_aprobada');
  const enabled = flag?.trim().toLowerCase() === 'true';

  return {
    disponible: false,
    motivo: 'RUBRIC_NOT_CONFIGURED',
    mensaje: enabled
      ? 'La rúbrica está marcada como aprobada, pero el instrumento de AQ-09 no está cargado: no se produce puntaje.'
      : 'La rúbrica del diagnóstico no está aprobada (AQ-09): se guardan las respuestas, pero no se produce puntaje.',
  };
}

/** Banco de preguntas activo, con el título de cada sección (copy del prototipo). */
export async function loadForm(db: SqlExecutor): Promise<{
  total: number;
  secciones: { numero: number; titulo: string }[];
  preguntas: DiagnosisQuestion[];
}> {
  const { rows } = await db.query<QuestionRow>(
    `SELECT id_pregunta, seccion, orden, enunciado, tipo, opciones
       FROM preguntas_diagnostico
      WHERE activa = TRUE
      ORDER BY seccion, orden`,
  );

  return {
    total: rows.length,
    secciones: SECTION_TITLES.map((titulo, index) => ({ numero: index + 1, titulo })),
    preguntas: rows.map(mapQuestion),
  };
}

async function loadAnswers(db: SqlExecutor, diagnosisId: number): Promise<DiagnosisAnswer[]> {
  const { rows } = await db.query<AnswerRow>(
    `SELECT r.preguntas_id_pregunta AS id_pregunta, r.valor,
            p.seccion, p.orden, p.enunciado, p.tipo, p.opciones
       FROM respuestas_diagnostico r
       JOIN preguntas_diagnostico p ON p.id_pregunta = r.preguntas_id_pregunta
      WHERE r.diagnosticos_id_diagnosticos = $1
      ORDER BY p.seccion, p.orden`,
    [diagnosisId],
  );

  return rows.map((row) => ({ ...mapQuestion(row), valor: row.valor }));
}

async function loadRow(db: SqlExecutor, id: number): Promise<DiagnosisRow> {
  const { rows } = await db.query<DiagnosisRow>(
    `${SELECT_DIAGNOSIS}
      WHERE d.id_diagnosticos = $1 AND e.fecha_eliminacion IS NULL`,
    [id],
  );

  if (!rows[0]) throw notFound();
  return rows[0];
}

/** Autoriza con la regla del expediente: admin, dueño o docente con asignación activa. */
async function authorize(db: SqlExecutor, row: DiagnosisRow, actor: SessionUser): Promise<void> {
  await findEntrepreneurshipForActor(db, row.emprendimiento_id, actor);
}

/** Emprendimiento del estudiante; si hay varios, el más reciente o el que se indique. */
async function findStudentEntrepreneurship(
  db: SqlExecutor,
  actor: SessionUser,
  emprendimientoId?: number,
): Promise<EntrepreneurshipRef> {
  const { rows } = await db.query<{
    id_emprendimiento: number;
    codigo: string;
    nombre: string;
    sector_economico_id_sector_economico: number | null;
  }>(
    `SELECT e.id_emprendimiento, e.codigo, e.nombre,
            e.sector_economico_id_sector_economico
       FROM emprendimiento e
      WHERE e.usuarios_id_usuarios = $1
        AND e.fecha_eliminacion IS NULL
        AND e.estado_aprobacion <> 'Rechazado'
        AND ($2::int IS NULL OR e.id_emprendimiento = $2)
      ORDER BY e.id_emprendimiento DESC
      LIMIT 1`,
    [actor.id, emprendimientoId ?? null],
  );

  const row = rows[0];
  if (!row) {
    if (emprendimientoId !== undefined) throw notFound();
    throw new AppError(
      422,
      'ENTREPRENEURSHIP_REQUIRED',
      'Necesitas un emprendimiento vigente para diligenciar el diagnóstico.',
    );
  }

  return {
    id: row.id_emprendimiento,
    codigo: row.codigo,
    nombre: row.nombre,
    sectorId: row.sector_economico_id_sector_economico,
  };
}

async function latestDiagnosis(
  db: SqlExecutor,
  emprendimientoId: number,
): Promise<{ id: number; estado: DiagnosticoEstado } | null> {
  const { rows } = await db.query<{ id: number; estado: DiagnosticoEstado }>(
    `SELECT id_diagnosticos AS id, estado
       FROM diagnosticos
      WHERE emprendimiento_id_emprendimiento = $1
      ORDER BY id_diagnosticos DESC
      LIMIT 1`,
    [emprendimientoId],
  );

  return rows[0] ?? null;
}

export async function getDiagnosis(id: number, actor: SessionUser): Promise<Diagnosis> {
  const row = await loadRow({ query }, id);
  await authorize({ query }, row, actor);

  const [answers, form, puntuacion] = await Promise.all([
    loadAnswers({ query }, id),
    loadForm({ query }),
    rubricStatus({ query }),
  ]);

  return {
    id: row.id_diagnosticos,
    estado: row.estado as DiagnosticoEstado,
    fechaDiagnostico: row.fecha_diagnostico.toISOString(),
    puntajeTotal: row.puntaje_total,
    urlInforme: row.url_informe,
    emprendimiento: {
      id: row.emprendimiento_id,
      codigo: row.emprendimiento_codigo,
      nombre: row.emprendimiento_nombre,
    },
    estudiante: {
      id: row.estudiante_id,
      nombres: row.estudiante_nombres,
      apellidos: row.estudiante_apellidos,
      correoInstitucional: row.estudiante_correo,
    },
    respuestas: answers,
    totalPreguntas: form.total,
    respondidas: answers.length,
    puntuacion,
  };
}

/** `GET /diagnosis/me`: el diagnóstico del emprendimiento del estudiante. */
export async function getMyDiagnosis(
  actor: SessionUser,
  emprendimientoId?: number,
): Promise<Diagnosis> {
  const entrepreneurship = await findStudentEntrepreneurship(
    { query },
    actor,
    emprendimientoId,
  );
  const latest = await latestDiagnosis({ query }, entrepreneurship.id);
  if (!latest) throw notFound();

  return getDiagnosis(latest.id, actor);
}

/** `POST /diagnosis/me`: guarda el borrador o envía y bloquea. */
export async function saveMyDiagnosis(
  actor: SessionUser,
  input: SaveDiagnosisInput,
  ip: string | null,
): Promise<Diagnosis> {
  const entrepreneurship = await findStudentEntrepreneurship(
    { query },
    actor,
    input.emprendimientoId,
  );
  const form = await loadForm({ query });
  const byId = new Map(form.preguntas.map((question) => [question.id, question]));

  input.respuestas.forEach((answer, index) => {
    const question = byId.get(answer.preguntaId);
    if (!question) {
      throw new AppError(
        400,
        'VALIDATION_ERROR',
        'Revisa las respuestas enviadas.',
        { [`respuestas.${index}.preguntaId`]: 'La pregunta no existe o no está activa' },
      );
    }
    if (question.opciones.length > 0 && !question.opciones.includes(answer.valor)) {
      throw new AppError(
        400,
        'VALIDATION_ERROR',
        'Revisa las respuestas enviadas.',
        { [`respuestas.${index}.valor`]: 'El valor no está entre las opciones de la pregunta' },
      );
    }
  });

  const id = await withTransaction(async (db) => {
    // Dos guardados simultáneos del mismo estudiante no pueden crear dos diagnósticos.
    await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
      `diagnostico:${actor.id}:${entrepreneurship.id}`,
    ]);

    const latest = await latestDiagnosis(db, entrepreneurship.id);
    let diagnosisId: number;

    if (latest) {
      if (latest.estado !== 'En progreso') {
        throw new AppError(
          422,
          'DIAGNOSIS_ALREADY_SUBMITTED',
          'El diagnóstico ya fue enviado: sus respuestas están bloqueadas.',
        );
      }
      diagnosisId = latest.id;
    } else {
      const inserted = await db.query<{ id: number }>(
        `INSERT INTO diagnosticos
           (estado, emprendimiento_id_emprendimiento,
            sector_economico_id_sector_economico)
         VALUES ('En progreso', $1, $2)
         RETURNING id_diagnosticos AS id`,
        [entrepreneurship.id, entrepreneurship.sectorId],
      );
      diagnosisId = inserted.rows[0]!.id;
    }

    for (const answer of input.respuestas) {
      await db.query(
        `INSERT INTO respuestas_diagnostico
           (valor, preguntas_id_pregunta, diagnosticos_id_diagnosticos)
         VALUES ($1, $2, $3)
         ON CONFLICT (preguntas_id_pregunta, diagnosticos_id_diagnosticos)
         DO UPDATE SET valor = EXCLUDED.valor, fecha_respuesta = now()`,
        [answer.valor, answer.preguntaId, diagnosisId],
      );
    }

    const counted = await db.query<{ total: number }>(
      `SELECT COUNT(*)::int AS total
         FROM respuestas_diagnostico
        WHERE diagnosticos_id_diagnosticos = $1`,
      [diagnosisId],
    );
    const respondidas = counted.rows[0]?.total ?? 0;

    if (input.enviar) {
      if (respondidas < form.total) {
        throw new AppError(
          422,
          'DIAGNOSIS_INCOMPLETE',
          `Faltan ${form.total - respondidas} respuesta(s) para enviar el diagnóstico.`,
          { respuestas: `Responde las ${form.total} preguntas activas` },
        );
      }

      await db.query(
        `UPDATE diagnosticos SET estado = 'Enviado' WHERE id_diagnosticos = $1`,
        [diagnosisId],
      );

      await audit(db, {
        accion: AUDIT_ACTIONS.SUBMIT_DIAGNOSIS,
        entidad: 'diagnosticos',
        entidadId: diagnosisId,
        valorAnterior: { estado: 'En progreso' },
        valorNuevo: {
          estado: 'Enviado',
          respondidas,
          puntajeTotal: null,
          motivo: 'RUBRIC_NOT_CONFIGURED',
        },
        usuarioId: actor.id,
        ip,
      });

      const mentors = await db.query<{ id: number }>(
        `SELECT DISTINCT usuarios_id_mentor AS id
           FROM asignaciones
          WHERE emprendimiento_id_emprendimiento = $1 AND estado = 'activa'`,
        [entrepreneurship.id],
      );

      for (const mentor of mentors.rows) {
        await notify(db, {
          usuarioId: mentor.id,
          tipo: 'Diagnóstico',
          mensaje: `${actor.nombres} ${actor.apellidos} envió el diagnóstico de «${entrepreneurship.nombre}».`,
          url: '/docente/diagnosticos',
          tipoObjeto: 'diagnostico',
          objetoId: diagnosisId,
        });
      }
    } else {
      await audit(db, {
        accion: AUDIT_ACTIONS.SAVE_DIAGNOSIS,
        entidad: 'diagnosticos',
        entidadId: diagnosisId,
        valorNuevo: { respondidas, enviar: false },
        usuarioId: actor.id,
        ip,
      });
    }

    return diagnosisId;
  });

  return getDiagnosis(id, actor);
}

/** `GET /diagnosis`: bandeja con el alcance del expediente. */
export async function listDiagnoses(
  options: ListDiagnosesQuery,
  actor: SessionUser,
): Promise<{
  items: DiagnosisSummary[];
  total: number;
  page: number;
  pageSize: number;
}> {
  const params: unknown[] = [];
  const where: string[] = ['e.fecha_eliminacion IS NULL'];

  if (actor.rolId === ROLES.ESTUDIANTE) {
    params.push(actor.id);
    where.push(`e.usuarios_id_usuarios = $${params.length}`);
  } else if (actor.rolId === ROLES.DOCENTE) {
    params.push(actor.id);
    where.push(`EXISTS (
      SELECT 1 FROM asignaciones a
       WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
         AND a.usuarios_id_mentor = $${params.length}
         AND a.estado = 'activa'
    )`);
  }

  if (options.estado) {
    params.push(options.estado);
    where.push(`d.estado = $${params.length}`);
  }
  if (options.emprendimientoId) {
    params.push(options.emprendimientoId);
    where.push(`d.emprendimiento_id_emprendimiento = $${params.length}`);
  }
  if (options.estudianteId) {
    params.push(options.estudianteId);
    where.push(`e.usuarios_id_usuarios = $${params.length}`);
  }
  if (options.q) {
    params.push(`%${options.q}%`);
    where.push(`(e.nombre ILIKE $${params.length}
      OR u.nombres ILIKE $${params.length}
      OR u.apellidos ILIKE $${params.length}
      OR u.correo_institucional ILIKE $${params.length})`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const orderBy = {
    fecha: 'd.fecha_diagnostico',
    estado: 'd.estado',
    emprendimiento: 'e.nombre',
    estudiante: 'u.apellidos',
  }[options.sort];

  params.push(options.pageSize);
  const limit = `$${params.length}`;
  params.push((options.page - 1) * options.pageSize);
  const offset = `$${params.length}`;

  const [count, page, form, puntuacion] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM diagnosticos d
         JOIN emprendimiento e ON e.id_emprendimiento = d.emprendimiento_id_emprendimiento
         JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
         ${whereSql}`,
      countParams,
    ),
    query<DiagnosisRow>(
      `${SELECT_DIAGNOSIS}
       WHERE ${where.join(' AND ')}
       ORDER BY ${orderBy} ${options.order.toUpperCase()}, d.id_diagnosticos DESC
       LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
    loadForm({ query }),
    rubricStatus({ query }),
  ]);

  return {
    items: page.rows.map((row) => ({
      id: row.id_diagnosticos,
      estado: row.estado as DiagnosticoEstado,
      fechaDiagnostico: row.fecha_diagnostico.toISOString(),
      puntajeTotal: row.puntaje_total,
      respondidas: row.respondidas,
      totalPreguntas: form.total,
      emprendimiento: {
        id: row.emprendimiento_id,
        codigo: row.emprendimiento_codigo,
        nombre: row.emprendimiento_nombre,
      },
      estudiante: {
        id: row.estudiante_id,
        nombres: row.estudiante_nombres,
        apellidos: row.estudiante_apellidos,
      },
      puntuacion,
    })),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

/** `GET /diagnosis/:id/report`: informe generado al vuelo, sin puntaje (P-3, AQ-09). */
export async function diagnosisReport(id: number, actor: SessionUser): Promise<unknown> {
  const diagnosis = await getDiagnosis(id, actor);

  return {
    diagnostico: diagnosis,
    informe: {
      disponible: false,
      motivo: 'RUBRIC_NOT_CONFIGURED',
      mensaje: diagnosis.puntuacion.mensaje,
      urlInforme: null,
      generadoEn: new Date().toISOString(),
      secciones: SECTION_TITLES.map((titulo, index) => ({
        numero: index + 1,
        titulo,
        puntaje: null,
        resultado: null,
        fortalezas: null,
        oportunidades: null,
      })),
      valoracion: [],
    },
  };
}

/** `GET /characterization/me`: secciones y respuestas, sin puntaje mientras no haya rúbrica. */
export async function getMyCharacterization(
  actor: SessionUser,
  emprendimientoId?: number,
): Promise<unknown> {
  const entrepreneurship = await findStudentEntrepreneurship(
    { query },
    actor,
    emprendimientoId,
  );
  const latest = await latestDiagnosis({ query }, entrepreneurship.id);
  if (!latest) throw notFound();

  const [form, answers, puntuacion] = await Promise.all([
    loadForm({ query }),
    loadAnswers({ query }, latest.id),
    rubricStatus({ query }),
  ]);

  const answeredBySection = new Map<number, number>();
  for (const answer of answers) {
    answeredBySection.set(
      answer.seccion,
      (answeredBySection.get(answer.seccion) ?? 0) + 1,
    );
  }

  const totalBySection = new Map<number, number>();
  for (const question of form.preguntas) {
    totalBySection.set(question.seccion, (totalBySection.get(question.seccion) ?? 0) + 1);
  }

  return {
    diagnosticoId: latest.id,
    estado: latest.estado,
    emprendimiento: {
      id: entrepreneurship.id,
      codigo: entrepreneurship.codigo,
      nombre: entrepreneurship.nombre,
    },
    respondidas: answers.length,
    totalPreguntas: form.total,
    puntuacion,
    secciones: SECTION_TITLES.map((titulo, index) => {
      const numero = index + 1;
      return {
        numero,
        titulo,
        respondidas: answeredBySection.get(numero) ?? 0,
        total: totalBySection.get(numero) ?? 0,
        puntaje: null,
        resultado: null,
        fortalezas: null,
        oportunidades: null,
      };
    }),
    valoracion: [],
  };
}
