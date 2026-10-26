import type { RevisionEstado, SeguimientoTipo } from '@sgemd/shared';
import type { PoolClient } from 'pg';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import {
  findEntrepreneurshipForActor,
  requireMentorAccess,
} from '../../services/entrepreneurshipAccess.js';
import { softDeleteEvidence } from '../../services/evidence.js';
import { notify } from '../../services/notify.js';
import { removeStoredFile } from '../../services/storage.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  CreateTracingInput,
  ListTracingQuery,
  UpdateTracingInput,
} from './schemas.js';

/**
 * Seguimientos (avances de fase y comentarios del docente).
 *
 * El estudiante los **lee**; los escribe el docente asignado o el administrador. Cada
 * registro documenta un avance concreto y es la fuente de la frecuencia de acompañamiento
 * (FR-022). El autor es siempre la sesión y solo él (o el administrador) puede editarlo o
 * darlo de baja.
 */

export interface Tracing {
  id: number;
  descripcion: string;
  tipo: SeguimientoTipo;
  puntaje: number | null;
  estadoRevision: RevisionEstado;
  fechaSeguimiento: string;
  retroalimentacion: string | null;
  evidencias: number;
  emprendimiento: { id: number; codigo: string; nombre: string };
  autor: { id: number; nombres: string; apellidos: string } | null;
  fase: { id: number; nombre: string } | null;
}

type TracingRow = {
  id_seguimientos: number;
  descripcion: string;
  tipo_seguimiento: string;
  puntaje: number | null;
  estado_revision: string;
  fecha_seguimiento: Date;
  retroalimentacion: string | null;
  evidencias: number;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  autor_id: number | null;
  autor_nombres: string | null;
  autor_apellidos: string | null;
  fase_id: number | null;
  fase_nombre: string | null;
};

const SELECT = `
  SELECT s.id_seguimientos, s.descripcion, s.tipo_seguimiento, s.puntaje,
         s.estado_revision, s.fecha_seguimiento, s.retroalimentacion,
         (SELECT COUNT(*)::int
            FROM adjuntos_seguimientos asg
            JOIN adjuntos a ON a.id_adjunto = asg.adjuntos_id_adjunto
           WHERE asg.seguimientos_id_seguimientos = s.id_seguimientos
             AND a.fecha_eliminacion IS NULL) AS evidencias,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         u.id_usuarios AS autor_id,
         u.nombres AS autor_nombres,
         u.apellidos AS autor_apellidos,
         f.id_faseplan AS fase_id,
         f.nombre AS fase_nombre
    FROM seguimientos s
    JOIN emprendimiento e ON e.id_emprendimiento = s.emprendimiento_id_emprendimiento
    LEFT JOIN usuarios u ON u.id_usuarios = s.usuarios_id_usuarios
    LEFT JOIN faseplan f ON f.id_faseplan = s.fase_plan_id_fase_plan
`;

function mapRow(row: TracingRow): Tracing {
  return {
    id: row.id_seguimientos,
    descripcion: row.descripcion,
    tipo: row.tipo_seguimiento as SeguimientoTipo,
    puntaje: row.puntaje,
    estadoRevision: row.estado_revision as RevisionEstado,
    fechaSeguimiento: row.fecha_seguimiento.toISOString(),
    retroalimentacion: row.retroalimentacion,
    evidencias: row.evidencias,
    emprendimiento: {
      id: row.emprendimiento_id,
      codigo: row.emprendimiento_codigo,
      nombre: row.emprendimiento_nombre,
    },
    autor:
      row.autor_id === null
        ? null
        : {
            id: row.autor_id,
            nombres: row.autor_nombres ?? '',
            apellidos: row.autor_apellidos ?? '',
          },
    fase:
      row.fase_id === null ? null : { id: row.fase_id, nombre: row.fase_nombre ?? '' },
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El seguimiento no existe.');
}

/** Alcance de lectura: el mismo del emprendimiento (R25). */
function scope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND e.usuarios_id_usuarios = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.DOCENTE) {
    return ` AND EXISTS (
               SELECT 1 FROM asignaciones a
                WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                  AND a.usuarios_id_mentor = ${bind(actor.id)}
                  AND a.estado = 'activa'
             )`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver seguimientos.');
}

export interface TracingPage {
  items: Tracing[];
  total: number;
  page: number;
  pageSize: number;
}

const SORT_COLUMNS: Record<ListTracingQuery['sort'], string> = {
  fecha: 's.fecha_seguimiento',
  tipo: 's.tipo_seguimiento',
  estado: 's.estado_revision',
};

export async function listTracing(
  emprendimientoId: number,
  options: ListTracingQuery,
  actor: SessionUser,
): Promise<TracingPage> {
  await findEntrepreneurshipForActor({ query }, emprendimientoId, actor);

  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [
    `s.fecha_eliminacion IS NULL AND s.emprendimiento_id_emprendimiento = ${bind(emprendimientoId)}${scope(actor, bind)}`,
  ];

  if (options.tipo) where.push(`s.tipo_seguimiento = ${bind(options.tipo)}`);
  if (options.estadoRevision) where.push(`s.estado_revision = ${bind(options.estadoRevision)}`);
  if (options.fasePlanId !== undefined) {
    where.push(`s.fase_plan_id_fase_plan = ${bind(options.fasePlanId)}`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(`(s.descripcion ILIKE ${like} OR s.retroalimentacion ILIKE ${like})`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction}, s.id_seguimientos ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM seguimientos s
         JOIN emprendimiento e ON e.id_emprendimiento = s.emprendimiento_id_emprendimiento
         ${whereSql}`,
      countParams,
    ),
    query<TracingRow>(
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

export async function getTracing(id: number, actor: SessionUser): Promise<Tracing> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const { rows } = await query<TracingRow>(
    `${SELECT} WHERE s.id_seguimientos = $1 AND s.fecha_eliminacion IS NULL${scope(actor, bind)}`,
    params,
  );

  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/* -------------------------------------------------------------------------------------
 * Escritura
 * ----------------------------------------------------------------------------------- */

type RawTracing = {
  id_seguimientos: number;
  descripcion: string;
  tipo_seguimiento: string;
  puntaje: number | null;
  estado_revision: string;
  fecha_seguimiento: Date;
  retroalimentacion: string | null;
  emprendimiento_id_emprendimiento: number;
  usuarios_id_usuarios: number;
  fase_plan_id_fase_plan: number | null;
};

async function findRaw(
  db: PoolClient,
  id: number,
  forUpdate = false,
): Promise<RawTracing | null> {
  const { rows } = await db.query<RawTracing>(
    `SELECT id_seguimientos, descripcion, tipo_seguimiento, puntaje, estado_revision,
            fecha_seguimiento, retroalimentacion, emprendimiento_id_emprendimiento,
            usuarios_id_usuarios, fase_plan_id_fase_plan
       FROM seguimientos
      WHERE id_seguimientos = $1 AND fecha_eliminacion IS NULL${forUpdate ? ' FOR UPDATE' : ''}`,
    [id],
  );
  return rows[0] ?? null;
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

/** La fase es obligatoria para un avance de fase: el prototipo la marca con asterisco. */
function requirePhaseForAdvance(tipo: string, fasePlanId: number | null | undefined): void {
  if (tipo === 'Avance de fase' && (fasePlanId === undefined || fasePlanId === null)) {
    throw new AppError(400, 'VALIDATION_ERROR', 'Selecciona la fase alcanzada.', {
      fasePlanId: 'La fase es obligatoria para un avance de fase',
    });
  }
}

/**
 * La fecha del avance puede ser anterior a hoy («Fecha del avance» del prototipo).
 *
 * Se guarda a mediodía de Bogotá: una fecha sin hora interpretada como UTC medianoche se
 * mostraría como el día anterior en la zona del programa.
 */
function noonInBogota(value: string | null | undefined): string | null {
  return value === undefined || value === null ? null : value;
}

export async function createTracing(
  input: CreateTracingInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Tracing> {
  const id = await withTransaction(async (db) => {
    const target = await requireMentorAccess(db, input.emprendimientoId, actor);

    requirePhaseForAdvance(input.tipoSeguimiento, input.fasePlanId);

    if (input.fasePlanId !== undefined && input.fasePlanId !== null) {
      await assertFaseExists(db, input.fasePlanId);
    }

    const fecha = noonInBogota(input.fechaSeguimiento);

    const { rows } = await db.query<{ id_seguimientos: number }>(
      `INSERT INTO seguimientos
         (descripcion, tipo_seguimiento, puntaje, estado_revision, fecha_seguimiento,
          retroalimentacion, emprendimiento_id_emprendimiento, usuarios_id_usuarios,
          fase_plan_id_fase_plan)
       VALUES ($1, $2, $3, $4,
               COALESCE(($5::date + time '12:00') AT TIME ZONE 'America/Bogota', now()),
               $6, $7, $8, $9)
       RETURNING id_seguimientos`,
      [
        input.descripcion,
        input.tipoSeguimiento,
        input.puntaje ?? null,
        input.estadoRevision ?? 'Pendiente',
        fecha,
        input.retroalimentacion ?? null,
        target.id,
        actor.id,
        input.fasePlanId ?? null,
      ],
    );

    const nuevoId = rows[0]!.id_seguimientos;

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_TRACING,
      entidad: 'seguimientos',
      entidadId: nuevoId,
      valorNuevo: {
        emprendimientoId: target.id,
        tipo: input.tipoSeguimiento,
        descripcion: input.descripcion,
        fasePlanId: input.fasePlanId ?? null,
        puntaje: input.puntaje ?? null,
        estadoRevision: input.estadoRevision ?? 'Pendiente',
      },
      usuarioId: actor.id,
      ip,
    });

    const resumen =
      input.descripcion.length > 160
        ? `${input.descripcion.slice(0, 157)}…`
        : input.descripcion;

    await notify(db, {
      usuarioId: target.estudianteId,
      tipo: 'Seguimiento',
      mensaje: `Se registró un seguimiento en «${target.nombre}»: ${resumen}`,
      url: `/estudiante/seguimiento/${nuevoId}`,
      tipoObjeto: 'seguimientos',
      objetoId: nuevoId,
    });

    return nuevoId;
  });

  return getTracing(id, actor);
}

/** Edición: el autor del registro o el administrador. */
export async function updateTracing(
  id: number,
  input: UpdateTracingInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Tracing> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    if (actor.rolId !== ROLES.ADMIN && current.usuarios_id_usuarios !== actor.id) {
      // Un docente ajeno recibe el mismo 404 que un registro inexistente: no se revela
      // que el seguimiento existe (R25, NFR-002).
      throw notFound();
    }

    if (current.tipo_seguimiento === 'Avance de fase') {
      requirePhaseForAdvance(
        current.tipo_seguimiento,
        input.fasePlanId === undefined ? current.fase_plan_id_fase_plan : input.fasePlanId,
      );
    }

    if (input.fasePlanId !== undefined && input.fasePlanId !== null) {
      await assertFaseExists(db, input.fasePlanId);
    }

    const assignments: string[] = [];
    const params: unknown[] = [id];
    const set = (column: string, value: unknown): void => {
      params.push(value);
      assignments.push(`${column} = $${params.length}`);
    };

    if (input.descripcion !== undefined) set('descripcion', input.descripcion);
    if (input.fasePlanId !== undefined) set('fase_plan_id_fase_plan', input.fasePlanId);
    if (input.puntaje !== undefined) set('puntaje', input.puntaje);
    if (input.estadoRevision !== undefined) set('estado_revision', input.estadoRevision);
    if (input.retroalimentacion !== undefined) set('retroalimentacion', input.retroalimentacion);
    if (input.fechaSeguimiento !== undefined) {
      params.push(input.fechaSeguimiento);
      assignments.push(
        `fecha_seguimiento = ($${params.length}::date + time '12:00') AT TIME ZONE 'America/Bogota'`,
      );
    }

    await db.query(
      `UPDATE seguimientos SET ${assignments.join(', ')} WHERE id_seguimientos = $1`,
      params,
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_TRACING,
      entidad: 'seguimientos',
      entidadId: id,
      valorAnterior: {
        descripcion: current.descripcion,
        fasePlanId: current.fase_plan_id_fase_plan,
        puntaje: current.puntaje,
        estadoRevision: current.estado_revision,
      },
      valorNuevo: {
        descripcion: input.descripcion ?? current.descripcion,
        fasePlanId:
          input.fasePlanId === undefined ? current.fase_plan_id_fase_plan : input.fasePlanId,
        puntaje: input.puntaje === undefined ? current.puntaje : input.puntaje,
        estadoRevision: input.estadoRevision ?? current.estado_revision,
      },
      usuarioId: actor.id,
      ip,
    });
  });

  return getTracing(id, actor);
}

/** Baja lógica + borrado físico de sus evidencias (BR-006). */
export async function deleteTracing(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const rutas = await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();

    if (actor.rolId !== ROLES.ADMIN && current.usuarios_id_usuarios !== actor.id) {
      throw notFound();
    }

    await db.query('UPDATE seguimientos SET fecha_eliminacion = now() WHERE id_seguimientos = $1', [
      id,
    ]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_TRACING,
      entidad: 'seguimientos',
      entidadId: id,
      valorAnterior: {
        descripcion: current.descripcion,
        tipo: current.tipo_seguimiento,
        emprendimientoId: current.emprendimiento_id_emprendimiento,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });

    return softDeleteEvidence(db, 'tracing', id);
  });

  await Promise.all(rutas.map((ruta) => removeStoredFile(ruta)));
}

/* -------------------------------------------------------------------------------------
 * Lectura para adjuntos
 * ----------------------------------------------------------------------------------- */

export interface TracingEvidenceTarget {
  id: number;
  autorId: number;
  emprendimientoId: number;
}

/** Seguimiento visible para el actor; fuera de alcance responde `404`. */
export async function loadTracingEvidenceTarget(
  id: number,
  actor: SessionUser,
): Promise<TracingEvidenceTarget> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const { rows } = await query<{
    id_seguimientos: number;
    usuarios_id_usuarios: number;
    emprendimiento_id_emprendimiento: number;
  }>(
    `SELECT s.id_seguimientos, s.usuarios_id_usuarios,
            s.emprendimiento_id_emprendimiento
       FROM seguimientos s
       JOIN emprendimiento e ON e.id_emprendimiento = s.emprendimiento_id_emprendimiento
      WHERE s.id_seguimientos = $1 AND s.fecha_eliminacion IS NULL${scope(actor, bind)}`,
    params,
  );

  const row = rows[0];
  if (!row) throw notFound();

  return {
    id: row.id_seguimientos,
    autorId: row.usuarios_id_usuarios,
    emprendimientoId: row.emprendimiento_id_emprendimiento,
  };
}
