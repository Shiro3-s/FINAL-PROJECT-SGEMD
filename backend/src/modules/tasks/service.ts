import type { Prioridad, RevisionEstado, TareaEstado } from '@sgemd/shared';
import type { PoolClient } from 'pg';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { requireMentorAccess, findEntrepreneurshipForActor } from '../../services/entrepreneurshipAccess.js';
import { listEvidence, softDeleteEvidence } from '../../services/evidence.js';
import { notify } from '../../services/notify.js';
import { recomputeProgress } from '../../services/progress.js';
import { removeStoredFile } from '../../services/storage.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  CreateTaskInput,
  GradeTaskInput,
  ListTasksQuery,
  ReturnTaskInput,
  UpdateTaskInput,
} from './schemas.js';

/**
 * Tareas del plan de trabajo (FR-023, R19, BR-007).
 *
 * Ciclo de vida (T16):
 *
 * ```
 * Pendiente ──(PUT estado=En curso)──► En curso ──(complete, ≥1 evidencia)──► En revisión
 *      └──────────────────────────────(complete)──────────────────────────────┘
 * En revisión ──(grade)──► Completada        En revisión ──(return + motivo)──► Devuelta
 * Devuelta ──(complete, nueva evidencia)──► En revisión
 * ```
 *
 * `Vencida` **no se almacena**: se deriva de `fecha_limite` en cada lectura (master §13.3).
 * Las transiciones se evalúan sobre el estado guardado, así que una tarea vencida sigue
 * pudiendo entregarse. El avance del emprendimiento se recalcula en la misma transacción
 * (R21).
 */

export interface Task {
  id: number;
  titulo: string;
  descripcion: string | null;
  fechaLimite: string | null;
  prioridad: Prioridad;
  puntos: number | null;
  /** Estado efectivo: `Vencida` si la fecha pasó y sigue pendiente o en curso. */
  estado: TareaEstado;
  vencida: boolean;
  puntajeObtenido: number | null;
  retroalimentacion: string | null;
  estadoRevision: RevisionEstado;
  evidenciaRequerida: boolean;
  motivoDevolucion: string | null;
  observacionesDevolucion: string | null;
  evidencias: number;
  /** Fecha de la evidencia más reciente: el diagrama no tiene `FechaCompletado` (P-24). */
  fechaEnvio: string | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: {
    id: number;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  } | null;
  creador: { id: number; nombres: string; apellidos: string } | null;
  fase: { id: number; nombre: string } | null;
}

type TaskRow = {
  id_tareas: number;
  titulo: string;
  descripcion: string | null;
  fecha_limite: string | null;
  prioridad: string;
  puntos: number | null;
  estado: string;
  vencida: boolean;
  puntaje_obtenido: number | null;
  retroalimentacion: string | null;
  estado_revision: string;
  evidencia_requerida: boolean;
  motivo_devolucion: string | null;
  observaciones_devolucion: string | null;
  evidencias: number;
  fecha_envio: Date | null;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  estudiante_id: number | null;
  estudiante_nombres: string | null;
  estudiante_apellidos: string | null;
  estudiante_correo: string | null;
  creador_id: number | null;
  creador_nombres: string | null;
  creador_apellidos: string | null;
  fase_id: number | null;
  fase_nombre: string | null;
};

/** Una tarea está vencida si su fecha pasó y sigue pendiente o en curso. */
const VENCIDA = `(t.fecha_limite IS NOT NULL
                 AND t.fecha_limite < CURRENT_DATE
                 AND t.estado IN ('Pendiente', 'En curso'))`;

const SELECT = `
  SELECT t.id_tareas, t.titulo, t.descripcion,
         to_char(t.fecha_limite, 'YYYY-MM-DD') AS fecha_limite,
         t.prioridad, t.puntos, t.estado, ${VENCIDA} AS vencida,
         t.puntaje_obtenido, t.retroalimentacion, t.estado_revision,
         t.evidencia_requerida, t.motivo_devolucion, t.observaciones_devolucion,
         (SELECT COUNT(*)::int
            FROM adjuntos_tareas at
            JOIN adjuntos a ON a.id_adjunto = at.adjuntos_id_adjunto
           WHERE at.tareas_id_tareas = t.id_tareas
             AND a.fecha_eliminacion IS NULL) AS evidencias,
         (SELECT MAX(a.fecha_subida)
            FROM adjuntos_tareas at
            JOIN adjuntos a ON a.id_adjunto = at.adjuntos_id_adjunto
           WHERE at.tareas_id_tareas = t.id_tareas
             AND a.fecha_eliminacion IS NULL) AS fecha_envio,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         s.id_usuarios AS estudiante_id,
         s.nombres AS estudiante_nombres,
         s.apellidos AS estudiante_apellidos,
         s.correo_institucional AS estudiante_correo,
         c.id_usuarios AS creador_id,
         c.nombres AS creador_nombres,
         c.apellidos AS creador_apellidos,
         f.id_faseplan AS fase_id,
         f.nombre AS fase_nombre
    FROM tareas t
    JOIN emprendimiento e ON e.id_emprendimiento = t.emprendimiento_id_emprendimiento
    LEFT JOIN usuarios s ON s.id_usuarios = t.usuarios_id_usuarios
    LEFT JOIN usuarios c ON c.id_usuarios = t.usuarios_id_creador
    LEFT JOIN faseplan f ON f.id_faseplan = t.fase_plan_id_fase_plan
`;

function mapRow(row: TaskRow): Task {
  return {
    id: row.id_tareas,
    titulo: row.titulo,
    descripcion: row.descripcion,
    fechaLimite: row.fecha_limite,
    prioridad: row.prioridad as Prioridad,
    puntos: row.puntos,
    estado: (row.vencida ? 'Vencida' : row.estado) as TareaEstado,
    vencida: row.vencida,
    puntajeObtenido: row.puntaje_obtenido,
    retroalimentacion: row.retroalimentacion,
    estadoRevision: row.estado_revision as RevisionEstado,
    evidenciaRequerida: row.evidencia_requerida,
    motivoDevolucion: row.motivo_devolucion,
    observacionesDevolucion: row.observaciones_devolucion,
    evidencias: row.evidencias,
    fechaEnvio: row.fecha_envio === null ? null : row.fecha_envio.toISOString(),
    emprendimiento: {
      id: row.emprendimiento_id,
      codigo: row.emprendimiento_codigo,
      nombre: row.emprendimiento_nombre,
    },
    estudiante:
      row.estudiante_id === null
        ? null
        : {
            id: row.estudiante_id,
            nombres: row.estudiante_nombres ?? '',
            apellidos: row.estudiante_apellidos ?? '',
            correoInstitucional: row.estudiante_correo ?? '',
          },
    creador:
      row.creador_id === null
        ? null
        : {
            id: row.creador_id,
            nombres: row.creador_nombres ?? '',
            apellidos: row.creador_apellidos ?? '',
          },
    fase:
      row.fase_id === null ? null : { id: row.fase_id, nombre: row.fase_nombre ?? '' },
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'La tarea no existe.');
}

/**
 * Alcance de lectura (R25, NFR-002):
 *
 * - Admin: todas.
 * - Estudiante: solo las que tiene asignadas.
 * - Docente: las de los emprendimientos que tiene asignados con una asignación activa.
 */
function scope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND t.usuarios_id_usuarios = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.DOCENTE) {
    return ` AND EXISTS (
               SELECT 1 FROM asignaciones a
                WHERE a.emprendimiento_id_emprendimiento = t.emprendimiento_id_emprendimiento
                  AND a.usuarios_id_mentor = ${bind(actor.id)}
                  AND a.estado = 'activa'
             )`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver tareas.');
}

/** Condición del estado **efectivo**, para que el filtro `Vencida` funcione. */
function estadoCondition(estado: TareaEstado, bind: (value: unknown) => string): string {
  if (estado === 'Vencida') return VENCIDA;
  if (estado === 'Pendiente' || estado === 'En curso') {
    return `(t.estado = ${bind(estado)} AND NOT ${VENCIDA})`;
  }
  return `t.estado = ${bind(estado)}`;
}

export interface TaskPage {
  items: Task[];
  total: number;
  page: number;
  pageSize: number;
}

const SORT_COLUMNS: Record<ListTasksQuery['sort'], string> = {
  limite: 't.fecha_limite',
  prioridad: `CASE t.prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 ELSE 3 END`,
  estado: 't.estado',
  titulo: 't.titulo',
};

export async function listTasks(
  options: ListTasksQuery,
  actor: SessionUser,
): Promise<TaskPage> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`t.fecha_eliminacion IS NULL${scope(actor, bind)}`];

  if (options.estado) where.push(estadoCondition(options.estado, bind));
  if (options.estadoRevision) where.push(`t.estado_revision = ${bind(options.estadoRevision)}`);
  if (options.prioridad) where.push(`t.prioridad = ${bind(options.prioridad)}`);
  if (options.emprendimientoId !== undefined) {
    where.push(`t.emprendimiento_id_emprendimiento = ${bind(options.emprendimientoId)}`);
  }
  if (options.estudianteId !== undefined) {
    where.push(`t.usuarios_id_usuarios = ${bind(options.estudianteId)}`);
  }
  if (options.fasePlanId !== undefined) {
    where.push(`t.fase_plan_id_fase_plan = ${bind(options.fasePlanId)}`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(`(t.titulo ILIKE ${like} OR t.descripcion ILIKE ${like})`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction} NULLS LAST, t.id_tareas ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM tareas t
         JOIN emprendimiento e ON e.id_emprendimiento = t.emprendimiento_id_emprendimiento
         ${whereSql}`,
      countParams,
    ),
    query<TaskRow>(
      `${SELECT} ${whereSql} ORDER BY ${orderSql} LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapRow),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

/** `GET /task/my-task`: las tareas del propio estudiante (la sesión manda). */
export async function listMyTasks(
  options: ListTasksQuery,
  actor: SessionUser,
): Promise<TaskPage> {
  if (actor.rolId !== ROLES.ESTUDIANTE) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo un estudiante tiene tareas propias.');
  }

  return listTasks({ ...options, estudianteId: actor.id }, actor);
}

export async function getTask(id: number, actor: SessionUser): Promise<Task> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const { rows } = await query<TaskRow>(
    `${SELECT} WHERE t.id_tareas = $1 AND t.fecha_eliminacion IS NULL${scope(actor, bind)}`,
    params,
  );

  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/** `GET /task/entrepreneurship/:empId` — exige ver el expediente (404 si no). */
export async function listTasksByEntrepreneurship(
  emprendimientoId: number,
  options: ListTasksQuery,
  actor: SessionUser,
): Promise<TaskPage> {
  await findEntrepreneurshipForActor({ query }, emprendimientoId, actor);

  return listTasks({ ...options, emprendimientoId }, actor);
}

/* -------------------------------------------------------------------------------------
 * Escritura
 * ----------------------------------------------------------------------------------- */

type RawTask = {
  id_tareas: number;
  titulo: string;
  descripcion: string | null;
  fecha_limite: string | null;
  prioridad: string;
  puntos: number | null;
  estado: string;
  estado_revision: string;
  emprendimiento_id_emprendimiento: number;
  usuarios_id_usuarios: number | null;
  usuarios_id_creador: number | null;
  fase_plan_id_fase_plan: number | null;
};

async function findRaw(
  db: PoolClient,
  id: number,
  forUpdate = false,
): Promise<RawTask | null> {
  const { rows } = await db.query<RawTask>(
    `SELECT id_tareas, titulo, descripcion,
            to_char(fecha_limite, 'YYYY-MM-DD') AS fecha_limite,
            prioridad, puntos, estado, estado_revision,
            emprendimiento_id_emprendimiento, usuarios_id_usuarios,
            usuarios_id_creador, fase_plan_id_fase_plan
       FROM tareas
      WHERE id_tareas = $1 AND fecha_eliminacion IS NULL${forUpdate ? ' FOR UPDATE' : ''}`,
    [id],
  );
  return rows[0] ?? null;
}

/**
 * Docente con asignación activa al emprendimiento, o administrador.
 *
 * Se comprueba sobre `asignaciones`, no sobre quién creó la tarea: si el docente fue
 * reasignado, el nuevo mentor puede calificar y el anterior ya no.
 */
async function assertMentor(db: PoolClient, emprendimientoId: number, actor: SessionUser) {
  if (actor.rolId === ROLES.ADMIN) return;
  if (actor.rolId !== ROLES.DOCENTE) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para esta acción.');
  }

  const { rows } = await db.query<{ existe: boolean }>(
    `SELECT EXISTS (
       SELECT 1 FROM asignaciones
        WHERE emprendimiento_id_emprendimiento = $1
          AND usuarios_id_mentor = $2
          AND estado = 'activa'
     ) AS existe`,
    [emprendimientoId, actor.id],
  );

  if (!rows[0]?.existe) {
    throw new AppError(404, 'NOT_FOUND', 'El emprendimiento no existe.');
  }
}

async function assertFaseExists(db: PoolClient, fasePlanId: number): Promise<void> {
  const { rows } = await db.query<{ existe: boolean }>(
    'SELECT EXISTS (SELECT 1 FROM faseplan WHERE id_faseplan = $1) AS existe',
    [fasePlanId],
  );

  if (!rows[0]?.existe) {
    throw new AppError(400, 'VALIDATION_ERROR', 'La fase del plan no existe.', {
      fasePlanId: 'Selecciona una fase del catálogo',
    });
  }
}

/** Docentes con asignación activa: destinatarios del aviso de entrega. */
async function activeMentors(db: PoolClient, emprendimientoId: number): Promise<number[]> {
  const { rows } = await db.query<{ usuarios_id_mentor: number }>(
    `SELECT DISTINCT usuarios_id_mentor
       FROM asignaciones
      WHERE emprendimiento_id_emprendimiento = $1 AND estado = 'activa'`,
    [emprendimientoId],
  );
  return rows.map((row) => row.usuarios_id_mentor);
}

function invalidTransition(estado: string, accion: string): AppError {
  return new AppError(
    422,
    'INVALID_TASK_TRANSITION',
    `No se puede ${accion} una tarea en estado «${estado}».`,
  );
}

function notEditable(estado: string): AppError {
  return new AppError(
    422,
    'TASK_NOT_EDITABLE',
    `Una tarea en estado «${estado}» ya no se edita.`,
  );
}

/**
 * Alta de tarea (R19).
 *
 * El destinatario es el propietario del emprendimiento; no se acepta `estudianteId`
 * (el diagrama tiene un solo estudiante por tarea y el prototipo asigna «a todo el grupo»,
 * que no está modelado: #34). Nace `Pendiente` y con `evidencia_requerida = TRUE`.
 */
export async function createTask(
  input: CreateTaskInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Task> {
  const id = await withTransaction(async (db) => {
    const target = await requireMentorAccess(db, input.emprendimientoId, actor);

    if (input.fasePlanId !== undefined && input.fasePlanId !== null) {
      await assertFaseExists(db, input.fasePlanId);
    }

    const { rows } = await db.query<{ id_tareas: number }>(
      `INSERT INTO tareas
         (titulo, descripcion, fecha_limite, prioridad, puntos, estado, estado_revision,
          evidencia_requerida, emprendimiento_id_emprendimiento, usuarios_id_usuarios,
          usuarios_id_creador, fase_plan_id_fase_plan)
       VALUES ($1, $2, $3, $4, $5, 'Pendiente', 'Pendiente', TRUE, $6, $7, $8, $9)
       RETURNING id_tareas`,
      [
        input.titulo,
        input.descripcion ?? null,
        input.fechaLimite ?? null,
        input.prioridad,
        input.puntos ?? null,
        target.id,
        target.estudianteId,
        actor.id,
        input.fasePlanId ?? null,
      ],
    );

    const nuevoId = rows[0]!.id_tareas;

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_TASK,
      entidad: 'tareas',
      entidadId: nuevoId,
      valorNuevo: {
        titulo: input.titulo,
        emprendimientoId: target.id,
        estudianteId: target.estudianteId,
        prioridad: input.prioridad,
        fechaLimite: input.fechaLimite ?? null,
        estado: 'Pendiente',
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: target.estudianteId,
      tipo: 'Tarea',
      mensaje: `Se te asignó la tarea «${input.titulo}» en «${target.nombre}».`,
      url: `/estudiante/tareas/${nuevoId}`,
      tipoObjeto: 'tareas',
      objetoId: nuevoId,
    });

    // Una tarea nueva cambia el denominador del avance (R21).
    await recomputeProgress(db, target.id);

    return nuevoId;
  });

  return getTask(id, actor);
}

/**
 * Edición de la tarea. Solo mientras no esté en revisión ni completada.
 *
 * `estado: 'En curso'` es la única transición aceptada aquí y solo desde `Pendiente`
 * (T16). La entrega, la calificación y la devolución tienen sus propias rutas.
 */
export async function updateTask(
  id: number,
  input: UpdateTaskInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Task> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    await assertMentor(db, current.emprendimiento_id_emprendimiento, actor);

    if (current.estado === 'En revisión' || current.estado === 'Completada') {
      throw notEditable(current.estado);
    }

    if (input.estado !== undefined) {
      if (current.estado !== 'Pendiente') {
        throw invalidTransition(current.estado, 'pasar a «En curso»');
      }
    }

    if (input.fasePlanId !== undefined && input.fasePlanId !== null) {
      await assertFaseExists(db, input.fasePlanId);
    }

    const siguienteEstado = input.estado ?? current.estado;

    const assignments: string[] = [];
    const params: unknown[] = [id];
    const set = (column: string, value: unknown): void => {
      params.push(value);
      assignments.push(`${column} = $${params.length}`);
    };

    if (input.titulo !== undefined) set('titulo', input.titulo);
    if (input.descripcion !== undefined) set('descripcion', input.descripcion);
    if (input.fechaLimite !== undefined) set('fecha_limite', input.fechaLimite);
    if (input.prioridad !== undefined) set('prioridad', input.prioridad);
    if (input.puntos !== undefined) set('puntos', input.puntos);
    if (input.fasePlanId !== undefined) set('fase_plan_id_fase_plan', input.fasePlanId);
    if (input.estado !== undefined) set('estado', input.estado);

    await db.query(`UPDATE tareas SET ${assignments.join(', ')} WHERE id_tareas = $1`, params);

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_TASK,
      entidad: 'tareas',
      entidadId: id,
      valorAnterior: {
        titulo: current.titulo,
        fechaLimite: current.fecha_limite,
        prioridad: current.prioridad,
        puntos: current.puntos,
        estado: current.estado,
      },
      valorNuevo: {
        titulo: input.titulo ?? current.titulo,
        fechaLimite: input.fechaLimite ?? current.fecha_limite,
        prioridad: input.prioridad ?? current.prioridad,
        puntos: input.puntos ?? current.puntos,
        estado: siguienteEstado,
      },
      usuarioId: actor.id,
      ip,
    });
  });

  return getTask(id, actor);
}

/**
 * `PUT /task/:id/complete` — entrega del estudiante.
 *
 * BR-007 se cumple **en el servidor**: sin al menos una evidencia vigente la respuesta es
 * `422 TASK_EVIDENCE_REQUIRED` (T17). La compuerta de la interfaz es solo la primera capa.
 */
export async function completeTask(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<Task> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    if (actor.rolId !== ROLES.ADMIN) {
      if (actor.rolId !== ROLES.ESTUDIANTE || current.usuarios_id_usuarios !== actor.id) {
        throw new AppError(404, 'NOT_FOUND', 'La tarea no existe.');
      }
    }

    if (!['Pendiente', 'En curso', 'Devuelta'].includes(current.estado)) {
      throw invalidTransition(current.estado, 'entregar');
    }

    const evidencias = await listEvidence(db, 'task', id);
    if (evidencias.length === 0) {
      throw new AppError(
        422,
        'TASK_EVIDENCE_REQUIRED',
        'Adjunta al menos una evidencia antes de marcar la tarea como completada.',
      );
    }

    await db.query(
      `UPDATE tareas
          SET estado = 'En revisión', estado_revision = 'En revisión'
        WHERE id_tareas = $1`,
      [id],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.SUBMIT_TASK,
      entidad: 'tareas',
      entidadId: id,
      valorAnterior: { estado: current.estado, estadoRevision: current.estado_revision },
      valorNuevo: { estado: 'En revisión', estadoRevision: 'En revisión' },
      usuarioId: actor.id,
      ip,
    });

    const { rows } = await db.query<{ nombre: string }>(
      'SELECT nombre FROM emprendimiento WHERE id_emprendimiento = $1',
      [current.emprendimiento_id_emprendimiento],
    );

    for (const mentorId of await activeMentors(db, current.emprendimiento_id_emprendimiento)) {
      await notify(db, {
        usuarioId: mentorId,
        tipo: 'Tarea',
        mensaje: `Se entregó la tarea «${current.titulo}» de «${rows[0]?.nombre ?? 'un emprendimiento'}» y está por calificar.`,
        url: `/docente/tareas/${id}`,
        tipoObjeto: 'tareas',
        objetoId: id,
      });
    }
  });

  return getTask(id, actor);
}

/**
 * `PUT /task/:id/grade` — calificación (0–100).
 *
 * Solo desde `En revisión`: calificar es la decisión que cierra el ciclo y deja la tarea
 * `Completada` con `estado_revision = 'Calificada'`. Recalcula el avance en la misma
 * transacción.
 */
export async function gradeTask(
  id: number,
  input: GradeTaskInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Task> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    await assertMentor(db, current.emprendimiento_id_emprendimiento, actor);

    if (current.estado !== 'En revisión') {
      throw invalidTransition(current.estado, 'calificar');
    }

    await db.query(
      `UPDATE tareas
          SET estado = 'Completada', estado_revision = 'Calificada',
              puntaje_obtenido = $2, retroalimentacion = $3
        WHERE id_tareas = $1`,
      [id, input.puntajeObtenido, input.retroalimentacion ?? null],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.GRADE_TASK,
      entidad: 'tareas',
      entidadId: id,
      valorAnterior: { estado: current.estado, estadoRevision: current.estado_revision },
      valorNuevo: {
        estado: 'Completada',
        estadoRevision: 'Calificada',
        puntajeObtenido: input.puntajeObtenido,
        retroalimentacion: input.retroalimentacion ?? null,
      },
      usuarioId: actor.id,
      ip,
    });

    if (current.usuarios_id_usuarios !== null) {
      await notify(db, {
        usuarioId: current.usuarios_id_usuarios,
        tipo: 'Tarea',
        mensaje: `Tu tarea «${current.titulo}» fue calificada con ${input.puntajeObtenido}/100.`,
        url: `/estudiante/tareas/${id}`,
        tipoObjeto: 'tareas',
        objetoId: id,
      });
    }

    await recomputeProgress(db, current.emprendimiento_id_emprendimiento);
  });

  return getTask(id, actor);
}

/**
 * `PUT /task/:id/return` — devolución con motivo (R19b, T18).
 *
 * Solo desde `En revisión`. El motivo es obligatorio (el esquema lo exige y la tabla tiene
 * su `CHECK`), se guardan las observaciones y el estudiante recibe el aviso.
 */
export async function returnTask(
  id: number,
  input: ReturnTaskInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Task> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    await assertMentor(db, current.emprendimiento_id_emprendimiento, actor);

    if (current.estado !== 'En revisión') {
      throw invalidTransition(current.estado, 'devolver');
    }

    await db.query(
      `UPDATE tareas
          SET estado = 'Devuelta', estado_revision = 'Devuelta',
              motivo_devolucion = $2, observaciones_devolucion = $3
        WHERE id_tareas = $1`,
      [id, input.motivo, input.observaciones ?? null],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.RETURN_TASK,
      entidad: 'tareas',
      entidadId: id,
      valorAnterior: { estado: current.estado, estadoRevision: current.estado_revision },
      valorNuevo: {
        estado: 'Devuelta',
        estadoRevision: 'Devuelta',
        motivo: input.motivo,
        observaciones: input.observaciones ?? null,
      },
      usuarioId: actor.id,
      ip,
    });

    if (current.usuarios_id_usuarios !== null) {
      await notify(db, {
        usuarioId: current.usuarios_id_usuarios,
        tipo: 'Tarea',
        mensaje: `Tu tarea «${current.titulo}» fue devuelta: ${input.motivo}.`,
        url: `/estudiante/tareas/${id}`,
        tipoObjeto: 'tareas',
        objetoId: id,
      });
    }
  });

  return getTask(id, actor);
}

/**
 * `DELETE /task/:id` — baja lógica y borrado físico de sus evidencias (BR-006).
 *
 * La fila queda con `fecha_eliminacion` (el histórico se puede leer) y los archivos
 * desaparecen del disco después de confirmar. Recalcula el avance porque la tarea deja de
 * contar en el denominador.
 */
export async function deleteTask(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const rutas = await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    await assertMentor(db, current.emprendimiento_id_emprendimiento, actor);

    await db.query('UPDATE tareas SET fecha_eliminacion = now() WHERE id_tareas = $1', [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_TASK,
      entidad: 'tareas',
      entidadId: id,
      valorAnterior: {
        titulo: current.titulo,
        estado: current.estado,
        emprendimientoId: current.emprendimiento_id_emprendimiento,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });

    const removed = await softDeleteEvidence(db, 'task', id);
    await recomputeProgress(db, current.emprendimiento_id_emprendimiento);

    return removed;
  });

  await Promise.all(rutas.map((ruta) => removeStoredFile(ruta)));
}

/* -------------------------------------------------------------------------------------
 * Lectura para adjuntos
 * ----------------------------------------------------------------------------------- */

export interface TaskEvidenceTarget {
  id: number;
  titulo: string;
  estado: string;
  estudianteId: number | null;
  emprendimientoId: number;
}

/**
 * Tarea sobre la que se va a subir o borrar evidencia, con la autorización ya resuelta.
 *
 * Visible para el admin, el estudiante destinatario y el docente asignado; fuera de
 * alcance responde `404`. El llamador decide además quién puede **escribir**.
 */
export async function loadTaskEvidenceTarget(
  id: number,
  actor: SessionUser,
): Promise<TaskEvidenceTarget> {
  const { rows } = await query<{
    id_tareas: number;
    titulo: string;
    estado: string;
    usuarios_id_usuarios: number | null;
    emprendimiento_id_emprendimiento: number;
    autorizado: boolean;
  }>(
    `SELECT t.id_tareas, t.titulo, t.estado, t.usuarios_id_usuarios,
            t.emprendimiento_id_emprendimiento,
            CASE
              WHEN $2::int = $4::int THEN TRUE
              WHEN $2::int = $5::int THEN t.usuarios_id_usuarios = $3::int
              WHEN $2::int = $6::int THEN EXISTS (
                SELECT 1 FROM asignaciones a
                 WHERE a.emprendimiento_id_emprendimiento = t.emprendimiento_id_emprendimiento
                   AND a.usuarios_id_mentor = $3::int
                   AND a.estado = 'activa'
              )
              ELSE FALSE
            END AS autorizado
       FROM tareas t
      WHERE t.id_tareas = $1 AND t.fecha_eliminacion IS NULL`,
    [id, actor.rolId, actor.id, ROLES.ADMIN, ROLES.ESTUDIANTE, ROLES.DOCENTE],
  );

  const row = rows[0];
  if (!row || !row.autorizado) throw notFound();

  return {
    id: row.id_tareas,
    titulo: row.titulo,
    estado: row.estado,
    estudianteId: row.usuarios_id_usuarios,
    emprendimientoId: row.emprendimiento_id_emprendimiento,
  };
}
