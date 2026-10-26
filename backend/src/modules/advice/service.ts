import type { AsesoriaEstado } from '@sgemd/shared';
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
import { resolveSchedule, type Schedule } from '../../services/schedule.js';
import { removeStoredFile } from '../../services/storage.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  AcceptAdviceInput,
  CreateAdviceInput,
  ListAdviceQuery,
  ReproposeAdviceInput,
  UpdateAdviceInput,
} from './schemas.js';

/**
 * Asesorías (FR-004, FR-015, BR-002, T20, T35).
 *
 * Ciclo de vida:
 *
 * ```
 * Por agendar ──(accept + horario)──► Confirmada ──(PUT estado)──► En curso ──► Completada
 *      │                                  │
 *      ├──(repropose)──► Programada ──────┘
 *      └──(reject)──────────────────────────────────────────────► Cancelada
 * ```
 *
 * BR-002: el estudiante **nunca** crea ni confirma una sesión. La creación directa es del
 * administrador (o del docente asignado, siempre para sí mismo) y la confirmación es del
 * docente asignado o del administrador.
 *
 * El horario vive en `fecha_y_horarios` (fecha + hora_inicio + hora_fin) y
 * `fecha_asesoria` se deriva del bloque en la zona del programa. T35 se resuelve con un
 * lock por docente y fecha: dos sesiones solapadas del mismo docente se rechazan con
 * `409 ADVICE_SCHEDULE_CONFLICT`.
 */

export interface Advice {
  id: number;
  codigo: string;
  tema: string;
  estado: AsesoriaEstado;
  fecha: string | null;
  horaInicio: string | null;
  horaFin: string | null;
  fechaAsesoria: string | null;
  lugarEnlace: string | null;
  modalidad: { id: number; nombre: string } | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: {
    id: number;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  };
  docente: {
    id: number;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  } | null;
  evidencias: number;
}

type AdviceRow = {
  id_asesorias: number;
  tema: string;
  estado: string;
  fecha: string | null;
  hora_inicio: string | null;
  hora_fin: string | null;
  fecha_asesoria: Date | null;
  lugar_enlace: string | null;
  modalidad_id: number | null;
  modalidad_nombre: string | null;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  estudiante_id: number;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_correo: string;
  docente_id: number | null;
  docente_nombres: string | null;
  docente_apellidos: string | null;
  docente_correo: string | null;
  evidencias: number;
};

const SELECT = `
  SELECT a.id_asesorias, a.tema, a.estado,
         to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
         to_char(fyh.hora_inicio, 'HH24:MI') AS hora_inicio,
         to_char(fyh.hora_fin, 'HH24:MI') AS hora_fin,
         a.fecha_asesoria, a.lugar_enlace,
         m.id_modalidad AS modalidad_id, m.nombre AS modalidad_nombre,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         s.id_usuarios AS estudiante_id,
         s.nombres AS estudiante_nombres,
         s.apellidos AS estudiante_apellidos,
         s.correo_institucional AS estudiante_correo,
         d.id_usuarios AS docente_id,
         d.nombres AS docente_nombres,
         d.apellidos AS docente_apellidos,
         d.correo_institucional AS docente_correo,
         (SELECT COUNT(*)::int
            FROM adjuntos_asesorias aa
            JOIN adjuntos ad ON ad.id_adjunto = aa.adjuntos_id_adjunto
           WHERE aa.asesorias_id_asesorias = a.id_asesorias
             AND ad.fecha_eliminacion IS NULL) AS evidencias
    FROM asesorias a
    JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
    JOIN usuarios s ON s.id_usuarios = a.usuarios_id_usuarios
    LEFT JOIN usuarios d ON d.id_usuarios = a.usuarios_id_docentes
    LEFT JOIN modalidad m ON m.id_modalidad = a.modalidad_id_modalidad
    LEFT JOIN fecha_y_horarios fyh
      ON fyh.id_fecha_y_horarios = a.fecha_y_horarios_id_fecha_y_horarios
`;

function codigo(id: number): string {
  return `ASES-${String(id).padStart(3, '0')}`;
}

function mapRow(row: AdviceRow): Advice {
  return {
    id: row.id_asesorias,
    codigo: codigo(row.id_asesorias),
    tema: row.tema,
    estado: row.estado as AsesoriaEstado,
    fecha: row.fecha,
    horaInicio: row.hora_inicio,
    horaFin: row.hora_fin,
    fechaAsesoria:
      row.fecha_asesoria === null ? null : row.fecha_asesoria.toISOString(),
    lugarEnlace: row.lugar_enlace,
    modalidad:
      row.modalidad_id === null
        ? null
        : { id: row.modalidad_id, nombre: row.modalidad_nombre ?? '' },
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
    docente:
      row.docente_id === null
        ? null
        : {
            id: row.docente_id,
            nombres: row.docente_nombres ?? '',
            apellidos: row.docente_apellidos ?? '',
            correoInstitucional: row.docente_correo ?? '',
          },
    evidencias: row.evidencias,
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'La asesoría no existe.');
}

/**
 * Alcance de lectura (R25, NFR-002):
 *
 * - Admin: todas.
 * - Docente: las que tiene asignadas (`usuarios_id_docentes`).
 * - Estudiante: las de su emprendimiento (`usuarios_id_usuarios`).
 */
function scope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.DOCENTE) {
    return ` AND a.usuarios_id_docentes = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND a.usuarios_id_usuarios = ${bind(actor.id)}`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver asesorías.');
}

export interface AdvicePage {
  items: Advice[];
  total: number;
  page: number;
  pageSize: number;
}

const SORT_COLUMNS: Record<ListAdviceQuery['sort'], string> = {
  fecha: 'a.fecha_asesoria',
  estado: 'a.estado',
  tema: 'a.tema',
  emprendimiento: 'e.nombre',
  estudiante: 's.apellidos',
  docente: 'd.apellidos',
};

export async function listAdvice(
  options: ListAdviceQuery,
  actor: SessionUser,
): Promise<AdvicePage> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`a.fecha_eliminacion IS NULL${scope(actor, bind)}`];

  if (options.estado) where.push(`a.estado = ${bind(options.estado)}`);
  // Etiqueta de filtro del prototipo docente; nunca se guarda como estado.
  if (options.grupo === 'Agendada') {
    where.push(`a.estado IN ('Programada', 'Confirmada', 'En curso')`);
  }
  if (options.docenteId !== undefined) {
    where.push(`a.usuarios_id_docentes = ${bind(options.docenteId)}`);
  }
  if (options.estudianteId !== undefined) {
    where.push(`a.usuarios_id_usuarios = ${bind(options.estudianteId)}`);
  }
  if (options.emprendimientoId !== undefined) {
    where.push(`a.emprendimiento_id_emprendimiento = ${bind(options.emprendimientoId)}`);
  }
  if (options.modalidadId !== undefined) {
    where.push(`a.modalidad_id_modalidad = ${bind(options.modalidadId)}`);
  }
  if (options.desde !== undefined) {
    where.push(
      `(a.fecha_asesoria AT TIME ZONE 'America/Bogota')::date >= ${bind(options.desde)}::date`,
    );
  }
  if (options.hasta !== undefined) {
    where.push(
      `(a.fecha_asesoria AT TIME ZONE 'America/Bogota')::date <= ${bind(options.hasta)}::date`,
    );
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(
      `(a.tema ILIKE ${like} OR e.nombre ILIKE ${like} OR e.codigo ILIKE ${like}
        OR s.nombres ILIKE ${like} OR s.apellidos ILIKE ${like}
        OR d.nombres ILIKE ${like} OR d.apellidos ILIKE ${like})`,
    );
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction} NULLS LAST, a.id_asesorias ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM asesorias a
         JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
         JOIN usuarios s ON s.id_usuarios = a.usuarios_id_usuarios
         LEFT JOIN usuarios d ON d.id_usuarios = a.usuarios_id_docentes
         ${whereSql}`,
      countParams,
    ),
    query<AdviceRow>(
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

export async function getAdvice(id: number, actor: SessionUser): Promise<Advice> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const { rows } = await query<AdviceRow>(
    `${SELECT} WHERE a.id_asesorias = $1 AND a.fecha_eliminacion IS NULL${scope(actor, bind)}`,
    params,
  );

  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/* -------------------------------------------------------------------------------------
 * Horario y conflictos (T35)
 * ----------------------------------------------------------------------------------- */

function scheduleOf(input: {
  fecha?: string;
  horaInicio?: string;
  horaFin?: string;
}): Schedule | null {
  if (input.fecha === undefined) return null;
  return {
    fecha: input.fecha,
    horaInicio: input.horaInicio!,
    horaFin: input.horaFin!,
  };
}

/**
 * T35: dos sesiones del mismo docente no pueden solaparse el mismo día.
 *
 * Se comparan los bloques (`hora_inicio`/`hora_fin`), no solo la hora de inicio: dos
 * sesiones de 09:00–11:00 y 10:00–12:00 se solapan aunque no empiecen a la misma hora.
 * Las canceladas y las dadas de baja liberan el horario.
 */
async function assertNoConflict(
  db: PoolClient,
  docenteId: number,
  schedule: Schedule,
  excludeId: number | null,
): Promise<void> {
  await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
    `asesorias:docente:${docenteId}:${schedule.fecha}`,
  ]);

  const params: unknown[] = [
    docenteId,
    schedule.fecha,
    schedule.horaInicio,
    schedule.horaFin,
  ];

  let exclude = '';
  if (excludeId !== null) {
    params.push(excludeId);
    exclude = ` AND a.id_asesorias <> $${params.length}`;
  }

  const { rows } = await db.query<{ id: number }>(
    `SELECT a.id_asesorias AS id
       FROM asesorias a
       JOIN fecha_y_horarios fyh
         ON fyh.id_fecha_y_horarios = a.fecha_y_horarios_id_fecha_y_horarios
      WHERE a.usuarios_id_docentes = $1
        AND a.fecha_eliminacion IS NULL
        AND a.estado <> 'Cancelada'
        AND fyh.fecha = $2::date
        AND fyh.hora_inicio < $4::time
        AND fyh.hora_fin > $3::time
        ${exclude}
      LIMIT 1`,
    params,
  );

  if (rows[0]) {
    throw new AppError(
      409,
      'ADVICE_SCHEDULE_CONFLICT',
      'El docente ya tiene una asesoría en ese horario.',
    );
  }
}

/* -------------------------------------------------------------------------------------
 * Escritura
 * ----------------------------------------------------------------------------------- */

type RawAdvice = {
  id_asesorias: number;
  tema: string;
  estado: string;
  lugar_enlace: string | null;
  emprendimiento_id_emprendimiento: number;
  usuarios_id_usuarios: number;
  usuarios_id_docentes: number | null;
  modalidad_id_modalidad: number | null;
  fecha_y_horarios_id_fecha_y_horarios: number | null;
  fecha: string | null;
  hora_inicio: string | null;
  hora_fin: string | null;
};

async function findRaw(
  db: PoolClient,
  id: number,
  forUpdate = false,
): Promise<RawAdvice | null> {
  const { rows } = await db.query<RawAdvice>(
    `SELECT a.id_asesorias, a.tema, a.estado, a.lugar_enlace,
            a.emprendimiento_id_emprendimiento, a.usuarios_id_usuarios,
            a.usuarios_id_docentes, a.modalidad_id_modalidad,
            a.fecha_y_horarios_id_fecha_y_horarios,
            to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
            to_char(fyh.hora_inicio, 'HH24:MI') AS hora_inicio,
            to_char(fyh.hora_fin, 'HH24:MI') AS hora_fin
       FROM asesorias a
       LEFT JOIN fecha_y_horarios fyh
         ON fyh.id_fecha_y_horarios = a.fecha_y_horarios_id_fecha_y_horarios
      WHERE a.id_asesorias = $1 AND a.fecha_eliminacion IS NULL
      ${forUpdate ? 'FOR UPDATE OF a' : ''}`,
    [id],
  );

  return rows[0] ?? null;
}

function scheduleOfRow(row: RawAdvice): Schedule | null {
  if (row.fecha === null || row.hora_inicio === null || row.hora_fin === null) return null;
  return { fecha: row.fecha, horaInicio: row.hora_inicio, horaFin: row.hora_fin };
}

function invalidTransition(estado: string, accion: string): AppError {
  return new AppError(
    422,
    'INVALID_ADVICE_TRANSITION',
    `No se puede ${accion} una asesoría en estado «${estado}».`,
  );
}

/**
 * El docente asignado o el administrador. Un docente ajeno recibe `404` (no se revela que
 * la asesoría existe), igual que un identificador inexistente.
 */
function assertWriter(row: RawAdvice, actor: SessionUser): void {
  if (actor.rolId === ROLES.ADMIN) return;
  if (actor.rolId === ROLES.DOCENTE && row.usuarios_id_docentes === actor.id) return;
  throw notFound();
}

/** Docente vigente, con rol Docente y cuenta `Activo`. */
async function assertDocente(
  db: PoolClient,
  docenteId: number,
): Promise<{ id: number; nombres: string; apellidos: string }> {
  const { rows } = await db.query<{
    id: number;
    nombres: string;
    apellidos: string;
    rol: number;
    estado: string;
    fecha_eliminacion: Date | null;
  }>(
    `SELECT id_usuarios AS id, nombres, apellidos, roles_id_roles AS rol, estado,
            fecha_eliminacion
       FROM usuarios
      WHERE id_usuarios = $1`,
    [docenteId],
  );

  const docente = rows[0];
  if (!docente || docente.fecha_eliminacion !== null) {
    throw new AppError(400, 'VALIDATION_ERROR', 'El docente no existe.', {
      docenteId: 'Selecciona un docente registrado',
    });
  }
  if (docente.rol !== ROLES.DOCENTE) {
    throw new AppError(400, 'VALIDATION_ERROR', 'La asesoría debe ser para un docente.', {
      docenteId: 'El docente debe tener rol Docente',
    });
  }
  if (docente.estado !== 'Activo') {
    throw new AppError(
      422,
      'MENTOR_NOT_ACTIVE',
      'Solo se puede agendar con un docente que tenga la cuenta Activa.',
      { docenteId: 'Activa la cuenta del docente antes de agendar' },
    );
  }

  return { id: docente.id, nombres: docente.nombres, apellidos: docente.apellidos };
}

async function assertModalidad(db: PoolClient, modalidadId: number): Promise<void> {
  const { rows } = await db.query<{ existe: boolean }>(
    'SELECT EXISTS (SELECT 1 FROM modalidad WHERE id_modalidad = $1) AS existe',
    [modalidadId],
  );

  if (!rows[0]?.existe) {
    throw new AppError(400, 'VALIDATION_ERROR', 'La modalidad no existe.', {
      modalidadId: 'Selecciona una modalidad del catálogo',
    });
  }
}

function dateLabel(schedule: Schedule): string {
  return `${schedule.fecha} de ${schedule.horaInicio} a ${schedule.horaFin}`;
}

export interface AdviceDraft {
  emprendimiento: { id: number; nombre: string; estudianteId: number };
  docenteId: number;
  tema: string;
  modalidadId?: number | null;
  lugarEnlace?: string | null;
  schedule?: Schedule | null;
}

/**
 * Inserta la asesoría dentro de una transacción ya abierta.
 *
 * Lo usan el alta directa (`POST /advice`) y la aprobación de una cita de la bandeja de
 * solicitudes (P-19), para que ambas vías apliquen exactamente las mismas reglas: docente
 * vigente y activo, modalidad válida, T35 y estado coherente con el horario.
 */
export async function insertAdvice(
  db: PoolClient,
  draft: AdviceDraft,
  actor: SessionUser,
  ip: string | null,
): Promise<{ id: number; estado: AsesoriaEstado }> {
  await assertDocente(db, draft.docenteId);

  if (draft.modalidadId !== undefined && draft.modalidadId !== null) {
    await assertModalidad(db, draft.modalidadId);
  }

  const schedule = draft.schedule ?? null;

  if (schedule) {
    await assertNoConflict(db, draft.docenteId, schedule, null);
  }

  const fechaYHorariosId = schedule ? await resolveSchedule(db, schedule) : null;
  const estado: AsesoriaEstado = schedule ? 'Programada' : 'Por agendar';

  const { rows } = await db.query<{ id: number }>(
    `INSERT INTO asesorias
       (tema, fecha_asesoria, estado, lugar_enlace,
        emprendimiento_id_emprendimiento, usuarios_id_usuarios, usuarios_id_docentes,
        modalidad_id_modalidad, fecha_y_horarios_id_fecha_y_horarios)
     VALUES ($1, ($2::date + $3::time) AT TIME ZONE 'America/Bogota', $4, $5, $6, $7, $8, $9, $10)
     RETURNING id_asesorias AS id`,
    [
      draft.tema,
      schedule?.fecha ?? null,
      schedule?.horaInicio ?? null,
      estado,
      draft.lugarEnlace ?? null,
      draft.emprendimiento.id,
      draft.emprendimiento.estudianteId,
      draft.docenteId,
      draft.modalidadId ?? null,
      fechaYHorariosId,
    ],
  );

  const id = rows[0]!.id;

  await audit(db, {
    accion: AUDIT_ACTIONS.CREATE_ADVICE,
    entidad: 'asesorias',
    entidadId: id,
    valorNuevo: {
      tema: draft.tema,
      emprendimientoId: draft.emprendimiento.id,
      estudianteId: draft.emprendimiento.estudianteId,
      docenteId: draft.docenteId,
      estado,
      fecha: schedule?.fecha ?? null,
      horaInicio: schedule?.horaInicio ?? null,
      horaFin: schedule?.horaFin ?? null,
    },
    usuarioId: actor.id,
    ip,
  });

  const cuando = schedule ? ` para el ${dateLabel(schedule)}` : '';
  await notify(db, {
    usuarioId: draft.emprendimiento.estudianteId,
    tipo: 'Asesoría',
    mensaje: `Se registró la asesoría «${draft.tema}» de «${draft.emprendimiento.nombre}»${cuando}.`,
    url: `/estudiante/asesorias/${id}`,
    tipoObjeto: 'asesorias',
    objetoId: id,
  });

  if (actor.id !== draft.docenteId) {
    await notify(db, {
      usuarioId: draft.docenteId,
      tipo: 'Asesoría',
      mensaje: `Se te asignó la asesoría «${draft.tema}» de «${draft.emprendimiento.nombre}»${cuando}.`,
      url: `/docente/asesorias/${id}`,
      tipoObjeto: 'asesorias',
      objetoId: id,
    });
  }

  return { id, estado };
}

/**
 * `POST /advice` — alta directa.
 *
 * El administrador puede agendar cualquier emprendimiento; el docente solo uno con
 * asignación activa y con él mismo como docente (BR-002). El estudiante recibe `403`.
 */
export async function createAdvice(
  input: CreateAdviceInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Advice> {
  if (actor.rolId !== ROLES.ADMIN && actor.rolId !== ROLES.DOCENTE) {
    throw new AppError(
      403,
      'ROLE_NOT_ALLOWED',
      'Solo el administrador o un docente pueden crear una asesoría.',
    );
  }

  const id = await withTransaction(async (db) => {
    const target =
      actor.rolId === ROLES.ADMIN
        ? await findEntrepreneurshipForActor(db, input.emprendimientoId, actor)
        : await requireMentorAccess(db, input.emprendimientoId, actor);

    if (actor.rolId === ROLES.DOCENTE && input.docenteId !== actor.id) {
      throw new AppError(
        403,
        'ROLE_NOT_ALLOWED',
        'Solo puedes agendar asesorías en las que tú eres el docente.',
      );
    }

    const created = await insertAdvice(
      db,
      {
        emprendimiento: {
          id: target.id,
          nombre: target.nombre,
          estudianteId: target.estudianteId,
        },
        docenteId: input.docenteId,
        tema: input.tema,
        modalidadId: input.modalidadId,
        lugarEnlace: input.lugarEnlace,
        schedule: scheduleOf(input),
      },
      actor,
      ip,
    );

    return created.id;
  });

  return getAdvice(id, actor);
}

/**
 * `POST /advice/:id/accept` — confirmación del docente asignado o del administrador.
 *
 * Puede traer el horario (una asesoría «Por agendar» se confirma al elegir fecha y hora).
 * Sin horario, ni en el cuerpo ni en la fila, responde `422 ADVICE_NOT_SCHEDULED`.
 */
export async function acceptAdvice(
  id: number,
  input: AcceptAdviceInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Advice> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();
    assertWriter(current, actor);

    if (current.estado !== 'Por agendar' && current.estado !== 'Programada') {
      throw invalidTransition(current.estado, 'confirmar');
    }

    const schedule = scheduleOf(input) ?? scheduleOfRow(current);
    if (!schedule) {
      throw new AppError(
        422,
        'ADVICE_NOT_SCHEDULED',
        'Selecciona la fecha y la hora antes de confirmar la asesoría.',
      );
    }

    if (current.usuarios_id_docentes === null) {
      throw new AppError(
        422,
        'ADVICE_NOT_SCHEDULED',
        'La asesoría no tiene un docente asignado.',
      );
    }

    await assertNoConflict(db, current.usuarios_id_docentes, schedule, id);
    const fechaYHorariosId = await resolveSchedule(db, schedule);

    await db.query(
      `UPDATE asesorias
          SET estado = 'Confirmada',
              fecha_asesoria = ($2::date + $3::time) AT TIME ZONE 'America/Bogota',
              fecha_y_horarios_id_fecha_y_horarios = $4
        WHERE id_asesorias = $1`,
      [id, schedule.fecha, schedule.horaInicio, fechaYHorariosId],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.ACCEPT_ADVICE,
      entidad: 'asesorias',
      entidadId: id,
      valorAnterior: {
        estado: current.estado,
        fecha: current.fecha,
        horaInicio: current.hora_inicio,
        horaFin: current.hora_fin,
      },
      valorNuevo: {
        estado: 'Confirmada',
        fecha: schedule.fecha,
        horaInicio: schedule.horaInicio,
        horaFin: schedule.horaFin,
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: current.usuarios_id_usuarios,
      tipo: 'Asesoría',
      mensaje: `Tu asesoría «${current.tema}» quedó confirmada para el ${dateLabel(schedule)}.`,
      url: `/estudiante/asesorias/${id}`,
      tipoObjeto: 'asesorias',
      objetoId: id,
    });
  });

  return getAdvice(id, actor);
}

/**
 * `POST /advice/:id/repropose` — el docente propone otra fecha.
 *
 * Exige el horario completo y deja la sesión en `Programada` (ya no está confirmada hasta
 * que el estudiante o la coordinación la acepten de nuevo). Se admite desde
 * `Por agendar`, `Programada` y `Confirmada`.
 */
export async function reproposeAdvice(
  id: number,
  input: ReproposeAdviceInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Advice> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();
    assertWriter(current, actor);

    if (!['Por agendar', 'Programada', 'Confirmada'].includes(current.estado)) {
      throw invalidTransition(current.estado, 'reprogramar');
    }

    if (current.usuarios_id_docentes === null) {
      throw new AppError(
        422,
        'ADVICE_NOT_SCHEDULED',
        'La asesoría no tiene un docente asignado.',
      );
    }

    const schedule: Schedule = {
      fecha: input.fecha,
      horaInicio: input.horaInicio,
      horaFin: input.horaFin,
    };

    await assertNoConflict(db, current.usuarios_id_docentes, schedule, id);
    const fechaYHorariosId = await resolveSchedule(db, schedule);

    await db.query(
      `UPDATE asesorias
          SET estado = 'Programada',
              fecha_asesoria = ($2::date + $3::time) AT TIME ZONE 'America/Bogota',
              fecha_y_horarios_id_fecha_y_horarios = $4
        WHERE id_asesorias = $1`,
      [id, schedule.fecha, schedule.horaInicio, fechaYHorariosId],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.REPROPOSE_ADVICE,
      entidad: 'asesorias',
      entidadId: id,
      valorAnterior: {
        estado: current.estado,
        fecha: current.fecha,
        horaInicio: current.hora_inicio,
        horaFin: current.hora_fin,
      },
      valorNuevo: {
        estado: 'Programada',
        fecha: schedule.fecha,
        horaInicio: schedule.horaInicio,
        horaFin: schedule.horaFin,
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: current.usuarios_id_usuarios,
      tipo: 'Asesoría',
      mensaje: `Se propuso una nueva fecha para tu asesoría «${current.tema}»: ${dateLabel(schedule)}.`,
      url: `/estudiante/asesorias/${id}`,
      tipoObjeto: 'asesorias',
      objetoId: id,
    });
  });

  return getAdvice(id, actor);
}

/**
 * `POST /advice/:id/reject` — cancelación con motivo.
 *
 * El diagrama no tiene columna de motivo (P-29): se guarda en la auditoría y se envía en
 * el aviso al estudiante. Una sesión ya iniciada o completada no se rechaza.
 */
export async function rejectAdvice(
  id: number,
  motivo: string,
  actor: SessionUser,
  ip: string | null,
): Promise<Advice> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();
    assertWriter(current, actor);

    if (!['Por agendar', 'Programada', 'Confirmada'].includes(current.estado)) {
      throw invalidTransition(current.estado, 'cancelar');
    }

    await db.query("UPDATE asesorias SET estado = 'Cancelada' WHERE id_asesorias = $1", [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.REJECT_ADVICE,
      entidad: 'asesorias',
      entidadId: id,
      valorAnterior: { estado: current.estado },
      valorNuevo: { estado: 'Cancelada', motivo },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: current.usuarios_id_usuarios,
      tipo: 'Asesoría',
      mensaje: `Tu asesoría «${current.tema}» fue cancelada. Motivo: ${motivo}`,
      url: `/estudiante/asesorias/${id}`,
      tipoObjeto: 'asesorias',
      objetoId: id,
    });
  });

  return getAdvice(id, actor);
}

/**
 * `PUT /advice/:id` — edición.
 *
 * - `docenteId` solo lo cambia el administrador (`403 FIELD_NOT_ALLOWED`).
 * - El horario se edita en bloque; si la sesión estaba «Por agendar» pasa a «Programada».
 * - `estado` solo acepta `En curso` (desde `Confirmada`) y `Completada` (desde `En curso`).
 * - Una asesoría completada o cancelada ya no se edita.
 */
export async function updateAdvice(
  id: number,
  input: UpdateAdviceInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Advice> {
  await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();
    assertWriter(current, actor);

    const contentKeys = [
      'tema',
      'modalidadId',
      'lugarEnlace',
      'docenteId',
      'fecha',
      'horaInicio',
      'horaFin',
    ] as const;
    const hasContent = contentKeys.some((key) => input[key] !== undefined);

    if (hasContent && (current.estado === 'Completada' || current.estado === 'Cancelada')) {
      throw new AppError(
        422,
        'ADVICE_NOT_EDITABLE',
        `Una asesoría en estado «${current.estado}» ya no se edita.`,
      );
    }

    if (input.docenteId !== undefined && actor.rolId !== ROLES.ADMIN) {
      throw new AppError(
        403,
        'FIELD_NOT_ALLOWED',
        'Solo el administrador puede cambiar el docente de una asesoría.',
        { docenteId: 'Este campo no lo puede modificar tu rol' },
      );
    }

    if (input.estado !== undefined) {
      const allowed =
        (current.estado === 'Confirmada' && input.estado === 'En curso') ||
        (current.estado === 'En curso' && input.estado === 'Completada');

      if (!allowed) {
        throw invalidTransition(current.estado, `pasar a «${input.estado}»`);
      }
    }

    if (input.docenteId !== undefined) await assertDocente(db, input.docenteId);
    if (input.modalidadId !== undefined && input.modalidadId !== null) {
      await assertModalidad(db, input.modalidadId);
    }

    const scheduleInput = scheduleOf(input);
    const docenteId = input.docenteId ?? current.usuarios_id_docentes;

    if (docenteId === null) {
      throw new AppError(
        422,
        'ADVICE_NOT_SCHEDULED',
        'La asesoría no tiene un docente asignado.',
      );
    }

    let fechaYHorariosId = current.fecha_y_horarios_id_fecha_y_horarios;

    if (scheduleInput) {
      if (current.estado === 'En curso') {
        throw new AppError(
          422,
          'ADVICE_NOT_EDITABLE',
          'La asesoría ya comenzó: no se puede cambiar el horario.',
        );
      }
      await assertNoConflict(db, docenteId, scheduleInput, id);
      fechaYHorariosId = await resolveSchedule(db, scheduleInput);
    } else if (input.docenteId !== undefined && input.docenteId !== current.usuarios_id_docentes) {
      const existing = scheduleOfRow(current);
      if (existing) await assertNoConflict(db, input.docenteId, existing, id);
    }

    const estado = input.estado ?? (scheduleInput && current.estado === 'Por agendar'
      ? 'Programada'
      : current.estado);

    const assignments: string[] = [];
    const params: unknown[] = [id];
    const set = (column: string, value: unknown): void => {
      params.push(value);
      assignments.push(`${column} = $${params.length}`);
    };

    if (input.tema !== undefined) set('tema', input.tema);
    if (input.lugarEnlace !== undefined) set('lugar_enlace', input.lugarEnlace);
    if (input.modalidadId !== undefined) set('modalidad_id_modalidad', input.modalidadId);
    if (input.docenteId !== undefined) set('usuarios_id_docentes', input.docenteId);
    if (input.estado !== undefined) set('estado', input.estado);
    else if (estado !== current.estado) set('estado', estado);

    if (scheduleInput) {
      params.push(scheduleInput.fecha);
      const dateIndex = params.length;
      params.push(scheduleInput.horaInicio);
      const timeIndex = params.length;
      assignments.push(
        `fecha_asesoria = ($${dateIndex}::date + $${timeIndex}::time) AT TIME ZONE 'America/Bogota'`,
      );
      set('fecha_y_horarios_id_fecha_y_horarios', fechaYHorariosId);
    }

    await db.query(`UPDATE asesorias SET ${assignments.join(', ')} WHERE id_asesorias = $1`, params);

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_ADVICE,
      entidad: 'asesorias',
      entidadId: id,
      valorAnterior: {
        tema: current.tema,
        estado: current.estado,
        docenteId: current.usuarios_id_docentes,
        modalidadId: current.modalidad_id_modalidad,
        fecha: current.fecha,
        horaInicio: current.hora_inicio,
        horaFin: current.hora_fin,
      },
      valorNuevo: {
        tema: input.tema ?? current.tema,
        estado,
        docenteId: input.docenteId ?? current.usuarios_id_docentes,
        modalidadId:
          input.modalidadId === undefined
            ? current.modalidad_id_modalidad
            : input.modalidadId,
        fecha: scheduleInput?.fecha ?? current.fecha,
        horaInicio: scheduleInput?.horaInicio ?? current.hora_inicio,
        horaFin: scheduleInput?.horaFin ?? current.hora_fin,
      },
      usuarioId: actor.id,
      ip,
    });

    if (input.docenteId !== undefined && input.docenteId !== current.usuarios_id_docentes) {
      const docente = await assertDocente(db, input.docenteId);

      await notify(db, {
        usuarioId: input.docenteId,
        tipo: 'Asesoría',
        mensaje: `Se te asignó la asesoría «${input.tema ?? current.tema}».`,
        url: `/docente/asesorias/${id}`,
        tipoObjeto: 'asesorias',
        objetoId: id,
      });

      await notify(db, {
        usuarioId: current.usuarios_id_usuarios,
        tipo: 'Asesoría',
        mensaje: `La asesoría «${input.tema ?? current.tema}» ahora la atiende ${docente.nombres} ${docente.apellidos}.`,
        url: `/estudiante/asesorias/${id}`,
        tipoObjeto: 'asesorias',
        objetoId: id,
      });
    }

    if (input.estado !== undefined) {
      const mensaje =
        input.estado === 'En curso'
          ? `Tu asesoría «${current.tema}» está en curso.`
          : `Tu asesoría «${current.tema}» fue completada.`;

      await notify(db, {
        usuarioId: current.usuarios_id_usuarios,
        tipo: 'Asesoría',
        mensaje,
        url: `/estudiante/asesorias/${id}`,
        tipoObjeto: 'asesorias',
        objetoId: id,
      });
    }
  });

  return getAdvice(id, actor);
}

/**
 * `DELETE /advice/:id` — baja lógica y borrado físico de sus evidencias (BR-006).
 *
 * La fila se conserva con `fecha_eliminacion` para que el histórico siga siendo legible;
 * los archivos desaparecen del disco después de confirmar la transacción.
 */
export async function deleteAdvice(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const rutas = await withTransaction(async (db) => {
    const current = await findRaw(db, id, true);
    if (!current) throw notFound();
    assertWriter(current, actor);

    await db.query('UPDATE asesorias SET fecha_eliminacion = now() WHERE id_asesorias = $1', [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_ADVICE,
      entidad: 'asesorias',
      entidadId: id,
      valorAnterior: {
        tema: current.tema,
        estado: current.estado,
        emprendimientoId: current.emprendimiento_id_emprendimiento,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: current.usuarios_id_usuarios,
      tipo: 'Asesoría',
      mensaje: `La asesoría «${current.tema}» fue eliminada de tu agenda.`,
      url: '/estudiante/asesorias',
      tipoObjeto: 'asesorias',
      objetoId: id,
    });

    return softDeleteEvidence(db, 'advice', id);
  });

  await Promise.all(rutas.map((ruta) => removeStoredFile(ruta)));
}

/* -------------------------------------------------------------------------------------
 * Lectura para adjuntos
 * ----------------------------------------------------------------------------------- */

export interface AdviceEvidenceTarget {
  id: number;
  estado: string;
  estudianteId: number;
  docenteId: number | null;
  emprendimientoId: number;
}

/**
 * Asesoría sobre la que se va a subir o borrar evidencia, con el alcance ya resuelto:
 * administrador, estudiante dueño o docente asignado. Fuera de alcance responde `404`.
 */
export async function loadAdviceEvidenceTarget(
  id: number,
  actor: SessionUser,
): Promise<AdviceEvidenceTarget> {
  const { rows } = await query<{
    id_asesorias: number;
    estado: string;
    usuarios_id_usuarios: number;
    usuarios_id_docentes: number | null;
    emprendimiento_id_emprendimiento: number;
  }>(
    `SELECT a.id_asesorias, a.estado, a.usuarios_id_usuarios, a.usuarios_id_docentes,
            a.emprendimiento_id_emprendimiento
       FROM asesorias a
      WHERE a.id_asesorias = $1
        AND a.fecha_eliminacion IS NULL
        AND (
          $2::int = $3::int
          OR ($2::int = $4::int AND a.usuarios_id_docentes = $5::int)
          OR ($2::int = $6::int AND a.usuarios_id_usuarios = $5::int)
        )`,
    [id, actor.rolId, ROLES.ADMIN, ROLES.DOCENTE, actor.id, ROLES.ESTUDIANTE],
  );

  const row = rows[0];
  if (!row) throw notFound();

  return {
    id: row.id_asesorias,
    estado: row.estado,
    estudianteId: row.usuarios_id_usuarios,
    docenteId: row.usuarios_id_docentes,
    emprendimientoId: row.emprendimiento_id_emprendimiento,
  };
}
