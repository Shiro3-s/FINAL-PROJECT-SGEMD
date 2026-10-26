import type { EventoEstado } from '@sgemd/shared';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { requireMentorAccess } from '../../services/entrepreneurshipAccess.js';
import { notify } from '../../services/notify.js';
import { resolveSchedule, type Schedule } from '../../services/schedule.js';
import type { SqlExecutor } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  CreateEventInput,
  CreateRecommendationInput,
  ListEventsQuery,
  ListRecommendationsQuery,
  UpdateEventInput,
} from './schemas.js';

/**
 * Eventos institucionales y recomendaciones (FR-021, T27).
 *
 * El administrador es el organizador: crea, edita, publica y da de baja. El docente
 * recomienda eventos **solo** a los emprendimientos que tiene asignados. El estudiante ve
 * los eventos publicados, se inscribe si el evento lo exige y recibe las recomendaciones
 * de su emprendimiento.
 *
 * `cupo` es el número de puestos **disponibles**: nace igual a `capacidad_maxima`, baja al
 * inscribirse y sube al cancelar. Se mueve dentro de una transacción con
 * `pg_advisory_xact_lock('evento:cupo:<id>')` para que dos inscripciones simultáneas no
 * vendan el mismo último puesto. Un evento sin `capacidad_maxima` no tiene tope y guarda
 * `cupo = NULL`.
 */

export interface EventItem {
  id: number;
  nombreEvento: string;
  descripcion: string | null;
  dirigidoA: string | null;
  capacidadMaxima: number | null;
  cupo: number | null;
  estado: EventoEstado;
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
  /** Si la sesión actual está inscrita. */
  inscrito: boolean;
}

export interface Recommendation {
  id: number;
  mensaje: string | null;
  estado: string;
  fecha: string;
  evento: { id: number; nombreEvento: string };
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: { id: number; nombres: string; apellidos: string } | null;
  docente: { id: number; nombres: string; apellidos: string };
}

type EventRow = {
  id_eventos: number;
  nombre_evento: string;
  descripcion: string | null;
  dirigido_a: string | null;
  capacidad_maxima: number | null;
  cupo: number | null;
  estado: string;
  requiere_registro: boolean;
  lugar: string | null;
  enlace: string | null;
  tipo_evento_id: number | null;
  tipo_evento_nombre: string | null;
  modalidad_id: number | null;
  modalidad_nombre: string | null;
  fecha: string | null;
  hora_inicio: string | null;
  hora_fin: string | null;
  organizador_id: number;
  organizador_nombres: string;
  organizador_apellidos: string;
  inscritos: number;
  inscrito: boolean;
};

type RecommendationRow = {
  id_recomendacion: number;
  mensaje: string | null;
  estado: string;
  fecha: Date;
  evento_id: number;
  evento_nombre: string;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  estudiante_id: number | null;
  estudiante_nombres: string | null;
  estudiante_apellidos: string | null;
  docente_id: number;
  docente_nombres: string;
  docente_apellidos: string;
};

/** El actor siempre va como parámetro: `inscrito` se resuelve en la misma consulta. */
function selectSql(actorParam: string): string {
  return `
  SELECT ev.id_eventos, ev.nombre_evento, ev.descripcion, ev.dirigido_a,
         ev.capacidad_maxima, ev.cupo, ev.estado, ev.requiere_registro,
         ev.lugar, ev.enlace,
         te.id_tipo_evento AS tipo_evento_id,
         te.nombre AS tipo_evento_nombre,
         m.id_modalidad AS modalidad_id,
         m.nombre AS modalidad_nombre,
         to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
         to_char(fyh.hora_inicio, 'HH24:MI') AS hora_inicio,
         to_char(fyh.hora_fin, 'HH24:MI') AS hora_fin,
         o.id_usuarios AS organizador_id,
         o.nombres AS organizador_nombres,
         o.apellidos AS organizador_apellidos,
         (SELECT COUNT(*)::int
            FROM usuarios_has_eventos uhe
           WHERE uhe.eventos_id_eventos = ev.id_eventos) AS inscritos,
         EXISTS (SELECT 1
                   FROM usuarios_has_eventos uhe
                  WHERE uhe.eventos_id_eventos = ev.id_eventos
                    AND uhe.usuarios_id_usuarios = ${actorParam}) AS inscrito
    FROM eventos ev
    JOIN usuarios o ON o.id_usuarios = ev.usuarios_id_organizador
    LEFT JOIN tipo_evento te ON te.id_tipo_evento = ev.tipo_evento_id_tipo_evento
    LEFT JOIN modalidad m ON m.id_modalidad = ev.modalidad_id_modalidad
    LEFT JOIN fecha_y_horarios fyh
      ON fyh.id_fecha_y_horarios = ev.fecha_y_horarios_id_fecha_y_horarios
`;
}

const SELECT_RECOMMENDATION = `
  SELECT r.id_recomendacion, r.mensaje, r.estado, r.fecha,
         ev.id_eventos AS evento_id, ev.nombre_evento AS evento_nombre,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         s.id_usuarios AS estudiante_id,
         s.nombres AS estudiante_nombres,
         s.apellidos AS estudiante_apellidos,
         d.id_usuarios AS docente_id,
         d.nombres AS docente_nombres,
         d.apellidos AS docente_apellidos
    FROM recomendaciones_evento r
    JOIN eventos ev ON ev.id_eventos = r.eventos_id_eventos
    JOIN emprendimiento e ON e.id_emprendimiento = r.emprendimiento_id_emprendimiento
    LEFT JOIN usuarios s ON s.id_usuarios = r.usuarios_id_estudiante
    JOIN usuarios d ON d.id_usuarios = r.usuarios_id_docente
`;

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El evento no existe.');
}

function mapEvent(row: EventRow): EventItem {
  return {
    id: row.id_eventos,
    nombreEvento: row.nombre_evento,
    descripcion: row.descripcion,
    dirigidoA: row.dirigido_a,
    capacidadMaxima: row.capacidad_maxima,
    cupo: row.cupo,
    estado: row.estado as EventoEstado,
    requiereRegistro: row.requiere_registro,
    lugar: row.lugar,
    enlace: row.enlace,
    tipoEvento:
      row.tipo_evento_id === null
        ? null
        : { id: row.tipo_evento_id, nombre: row.tipo_evento_nombre ?? '' },
    modalidad:
      row.modalidad_id === null
        ? null
        : { id: row.modalidad_id, nombre: row.modalidad_nombre ?? '' },
    fecha: row.fecha,
    horaInicio: row.hora_inicio,
    horaFin: row.hora_fin,
    organizador: {
      id: row.organizador_id,
      nombres: row.organizador_nombres,
      apellidos: row.organizador_apellidos,
    },
    inscritos: row.inscritos,
    inscrito: row.inscrito,
  };
}

function mapRecommendation(row: RecommendationRow): Recommendation {
  return {
    id: row.id_recomendacion,
    mensaje: row.mensaje,
    estado: row.estado,
    fecha: row.fecha.toISOString(),
    evento: { id: row.evento_id, nombreEvento: row.evento_nombre },
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
          },
    docente: {
      id: row.docente_id,
      nombres: row.docente_nombres,
      apellidos: row.docente_apellidos,
    },
  };
}

/**
 * Visibilidad (T27):
 *
 * - Admin: todos los eventos, publicados o no.
 * - Docente y estudiante: solo `Publicado`.
 *
 * Un evento en borrador responde `404` a quien no es administrador: no se revela el
 * borrador ni siquiera por id.
 */
function visibility(actor: SessionUser): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.DOCENTE || actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND ev.estado = 'Publicado'`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver eventos.');
}

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

async function assertCatalog(
  db: SqlExecutor,
  table: 'tipo_evento' | 'modalidad',
  column: string,
  id: number,
): Promise<void> {
  const { rows } = await db.query(`SELECT 1 FROM ${table} WHERE ${column} = $1`, [id]);
  if (!rows[0]) {
    throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos del evento.', {
      [table === 'tipo_evento' ? 'tipoEventoId' : 'modalidadId']:
        'El valor no existe en el catálogo',
    });
  }
}

async function loadEvent(
  db: SqlExecutor,
  id: number,
  actor: SessionUser,
  options: { forUpdate?: boolean } = {},
): Promise<EventRow> {
  const params: unknown[] = [id, actor.id];
  const { rows } = await db.query<EventRow>(
    `${selectSql('$2')}
      WHERE ev.id_eventos = $1
        AND ev.fecha_eliminacion IS NULL${visibility(actor)}
      ${options.forUpdate ? 'FOR UPDATE OF ev' : ''}`,
    params,
  );

  if (!rows[0]) throw notFound();
  return rows[0];
}

/* -------------------------------------------------------------------------------------
 * Lectura
 * ----------------------------------------------------------------------------------- */

const SORT_COLUMNS: Record<ListEventsQuery['sort'], string> = {
  fecha: 'fyh.fecha',
  nombre: 'ev.nombre_evento',
  estado: 'ev.estado',
  cupo: 'ev.cupo',
};

export async function listEvents(
  options: ListEventsQuery,
  actor: SessionUser,
): Promise<{ items: EventItem[]; total: number; page: number; pageSize: number }> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`ev.fecha_eliminacion IS NULL${visibility(actor)}`];

  if (options.estado) where.push(`ev.estado = ${bind(options.estado)}`);
  if (options.tipoEventoId !== undefined) {
    where.push(`ev.tipo_evento_id_tipo_evento = ${bind(options.tipoEventoId)}`);
  }
  if (options.modalidadId !== undefined) {
    where.push(`ev.modalidad_id_modalidad = ${bind(options.modalidadId)}`);
  }
  if (options.desde !== undefined) {
    where.push(`fyh.fecha >= ${bind(options.desde)}::date`);
  }
  if (options.hasta !== undefined) {
    where.push(`fyh.fecha <= ${bind(options.hasta)}::date`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(
      `(ev.nombre_evento ILIKE ${like} OR ev.descripcion ILIKE ${like}
        OR ev.lugar ILIKE ${like} OR ev.dirigido_a ILIKE ${like})`,
    );
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  // El `COUNT` no necesita el `inscrito` del actor: se queda con los filtros ya ligados.
  const countParams = [...params];

  // El id del actor va al final para que la consulta de página y la de conteo compartan
  // los mismos marcadores de los filtros.
  const actorParam = bind(actor.id);
  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction} NULLS LAST, ev.id_eventos ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM eventos ev
         LEFT JOIN fecha_y_horarios fyh
           ON fyh.id_fecha_y_horarios = ev.fecha_y_horarios_id_fecha_y_horarios
         ${whereSql}`,
      countParams,
    ),
    query<EventRow>(
      `${selectSql(actorParam)} ${whereSql}
        ORDER BY ${orderSql} LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapEvent),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

export async function getEvent(id: number, actor: SessionUser): Promise<EventItem> {
  return mapEvent(await loadEvent({ query }, id, actor));
}

/* -------------------------------------------------------------------------------------
 * Escritura del administrador
 * ----------------------------------------------------------------------------------- */

export async function createEvent(
  input: CreateEventInput,
  actor: SessionUser,
  ip: string | null,
): Promise<EventItem> {
  if (actor.rolId !== ROLES.ADMIN) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo el administrador crea eventos.');
  }

  const id = await withTransaction(async (db) => {
    if (input.tipoEventoId !== undefined && input.tipoEventoId !== null) {
      await assertCatalog(db, 'tipo_evento', 'id_tipo_evento', input.tipoEventoId);
    }
    if (input.modalidadId !== undefined && input.modalidadId !== null) {
      await assertCatalog(db, 'modalidad', 'id_modalidad', input.modalidadId);
    }

    const schedule = scheduleOf(input);
    const fechaYHorariosId = schedule ? await resolveSchedule(db, schedule) : null;
    const capacidad = input.capacidadMaxima ?? null;

    const { rows } = await db.query<{ id: number }>(
      `INSERT INTO eventos
         (nombre_evento, descripcion, dirigido_a, capacidad_maxima, cupo, estado,
          requiere_registro, lugar, enlace, usuarios_id_organizador,
          tipo_evento_id_tipo_evento, modalidad_id_modalidad,
          fecha_y_horarios_id_fecha_y_horarios)
       VALUES ($1, $2, $3, $4, $4, $5, $6, $7, $8, $9, $10, $11, $12)
       RETURNING id_eventos AS id`,
      [
        input.nombreEvento,
        input.descripcion ?? null,
        input.dirigidoA ?? null,
        capacidad,
        input.estado,
        input.requiereRegistro,
        input.lugar ?? null,
        input.enlace ?? null,
        actor.id,
        input.tipoEventoId ?? null,
        input.modalidadId ?? null,
        fechaYHorariosId,
      ],
    );

    const eventoId = rows[0]!.id;

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_EVENT,
      entidad: 'eventos',
      entidadId: eventoId,
      valorNuevo: {
        nombreEvento: input.nombreEvento,
        estado: input.estado,
        capacidadMaxima: capacidad,
        cupo: capacidad,
        requiereRegistro: input.requiereRegistro,
        fecha: schedule?.fecha ?? null,
        horaInicio: schedule?.horaInicio ?? null,
        horaFin: schedule?.horaFin ?? null,
      },
      usuarioId: actor.id,
      ip,
    });

    return eventoId;
  });

  return getEvent(id, actor);
}

export async function updateEvent(
  id: number,
  input: UpdateEventInput,
  actor: SessionUser,
  ip: string | null,
): Promise<EventItem> {
  if (actor.rolId !== ROLES.ADMIN) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo el administrador edita eventos.');
  }

  await withTransaction(async (db) => {
    const current = await loadEvent(db, id, actor, { forUpdate: true });

    if (input.tipoEventoId !== undefined && input.tipoEventoId !== null) {
      await assertCatalog(db, 'tipo_evento', 'id_tipo_evento', input.tipoEventoId);
    }
    if (input.modalidadId !== undefined && input.modalidadId !== null) {
      await assertCatalog(db, 'modalidad', 'id_modalidad', input.modalidadId);
    }

    const sets: string[] = [];
    const params: unknown[] = [];
    const set = (column: string, value: unknown): void => {
      params.push(value);
      sets.push(`${column} = $${params.length}`);
    };

    if (input.nombreEvento !== undefined) set('nombre_evento', input.nombreEvento);
    if (input.descripcion !== undefined) set('descripcion', input.descripcion);
    if (input.dirigidoA !== undefined) set('dirigido_a', input.dirigidoA);
    if (input.estado !== undefined) set('estado', input.estado);
    if (input.requiereRegistro !== undefined) set('requiere_registro', input.requiereRegistro);
    if (input.lugar !== undefined) set('lugar', input.lugar);
    if (input.enlace !== undefined) set('enlace', input.enlace);
    if (input.tipoEventoId !== undefined) {
      set('tipo_evento_id_tipo_evento', input.tipoEventoId);
    }
    if (input.modalidadId !== undefined) set('modalidad_id_modalidad', input.modalidadId);

    if (input.capacidadMaxima !== undefined) {
      const capacidad = input.capacidadMaxima;
      if (capacidad !== null && capacidad < current.inscritos) {
        throw new AppError(
          422,
          'EVENT_CAPACITY_BELOW_REGISTRATIONS',
          `El evento ya tiene ${current.inscritos} inscrito(s): la capacidad no puede ser menor.`,
          { capacidadMaxima: `Debe ser al menos ${current.inscritos}` },
        );
      }
      set('capacidad_maxima', capacidad);
      set('cupo', capacidad === null ? null : capacidad - current.inscritos);
    }

    const schedule = scheduleOf(input);
    if (schedule) {
      const fechaYHorariosId = await resolveSchedule(db, schedule);
      set('fecha_y_horarios_id_fecha_y_horarios', fechaYHorariosId);
    }

    params.push(id);
    await db.query(
      `UPDATE eventos SET ${sets.join(', ')} WHERE id_eventos = $${params.length}`,
      params,
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_EVENT,
      entidad: 'eventos',
      entidadId: id,
      valorAnterior: {
        nombreEvento: current.nombre_evento,
        estado: current.estado,
        capacidadMaxima: current.capacidad_maxima,
        cupo: current.cupo,
        requiereRegistro: current.requiere_registro,
        fecha: current.fecha,
        horaInicio: current.hora_inicio,
        horaFin: current.hora_fin,
      },
      valorNuevo: input,
      usuarioId: actor.id,
      ip,
    });
  });

  return getEvent(id, actor);
}

export async function deleteEvent(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  if (actor.rolId !== ROLES.ADMIN) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo el administrador da de baja eventos.');
  }

  await withTransaction(async (db) => {
    const current = await loadEvent(db, id, actor, { forUpdate: true });

    await db.query('UPDATE eventos SET fecha_eliminacion = now() WHERE id_eventos = $1', [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_EVENT,
      entidad: 'eventos',
      entidadId: id,
      valorAnterior: {
        nombreEvento: current.nombre_evento,
        estado: current.estado,
        inscritos: current.inscritos,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });
  });
}

/* -------------------------------------------------------------------------------------
 * Inscripción del estudiante
 * ----------------------------------------------------------------------------------- */

export async function registerForEvent(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<EventItem> {
  if (actor.rolId !== ROLES.ESTUDIANTE) {
    throw new AppError(
      403,
      'ROLE_NOT_ALLOWED',
      'Solo un estudiante puede inscribirse a un evento.',
    );
  }

  await withTransaction(async (db) => {
    await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [`evento:cupo:${id}`]);

    const current = await loadEvent(db, id, actor, { forUpdate: true });

    if (!current.requiere_registro) {
      throw new AppError(
        422,
        'EVENT_REGISTRATION_NOT_REQUIRED',
        'Este evento no requiere inscripción.',
      );
    }

    const existing = await db.query(
      `SELECT 1 FROM usuarios_has_eventos
        WHERE usuarios_id_usuarios = $1 AND eventos_id_eventos = $2`,
      [actor.id, id],
    );
    if (existing.rows[0]) {
      throw new AppError(409, 'EVENT_ALREADY_REGISTERED', 'Ya estás inscrito en este evento.');
    }

    if (current.cupo !== null && current.cupo <= 0) {
      throw new AppError(422, 'EVENT_FULL', 'El evento ya no tiene cupos disponibles.');
    }

    await db.query(
      `INSERT INTO usuarios_has_eventos (usuarios_id_usuarios, eventos_id_eventos)
       VALUES ($1, $2)`,
      [actor.id, id],
    );

    if (current.cupo !== null) {
      await db.query('UPDATE eventos SET cupo = cupo - 1 WHERE id_eventos = $1', [id]);
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.REGISTER_EVENT,
      entidad: 'eventos',
      entidadId: id,
      valorNuevo: { usuarioId: actor.id, cupoAnterior: current.cupo },
      usuarioId: actor.id,
      ip,
    });
  });

  return getEvent(id, actor);
}

export interface UnregisterResult {
  eventoId: number;
  inscrito: false;
  cupo: number | null;
}

export async function unregisterFromEvent(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<UnregisterResult> {
  if (actor.rolId !== ROLES.ESTUDIANTE) {
    throw new AppError(
      403,
      'ROLE_NOT_ALLOWED',
      'Solo un estudiante puede cancelar su inscripción.',
    );
  }

  return withTransaction(async (db) => {
    await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [`evento:cupo:${id}`]);

    const { rows } = await db.query<{
      capacidad_maxima: number | null;
      cupo: number | null;
    }>(
      `SELECT capacidad_maxima, cupo
         FROM eventos
        WHERE id_eventos = $1 AND fecha_eliminacion IS NULL
        FOR UPDATE`,
      [id],
    );

    const current = rows[0];
    if (!current) throw notFound();

    const deleted = await db.query(
      `DELETE FROM usuarios_has_eventos
        WHERE usuarios_id_usuarios = $1 AND eventos_id_eventos = $2`,
      [actor.id, id],
    );
    if (deleted.rowCount === 0) {
      throw new AppError(
        404,
        'EVENT_REGISTRATION_NOT_FOUND',
        'No estás inscrito en este evento.',
      );
    }

    let cupo = current.cupo;
    if (cupo !== null) {
      cupo = current.capacidad_maxima === null
        ? cupo + 1
        : Math.min(cupo + 1, current.capacidad_maxima);
      await db.query('UPDATE eventos SET cupo = $2 WHERE id_eventos = $1', [id, cupo]);
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.UNREGISTER_EVENT,
      entidad: 'eventos',
      entidadId: id,
      valorAnterior: { usuarioId: actor.id, cupo: current.cupo },
      valorNuevo: { usuarioId: actor.id, cupo },
      usuarioId: actor.id,
      ip,
    });

    return { eventoId: id, inscrito: false, cupo };
  });
}

/* -------------------------------------------------------------------------------------
 * Recomendaciones
 * ----------------------------------------------------------------------------------- */

function recommendationScope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.DOCENTE) {
    return ` AND r.usuarios_id_docente = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.ESTUDIANTE) {
    const me = bind(actor.id);
    return ` AND (r.usuarios_id_estudiante IS NULL OR r.usuarios_id_estudiante = ${me})
             AND EXISTS (SELECT 1 FROM emprendimiento e2
                          WHERE e2.id_emprendimiento = r.emprendimiento_id_emprendimiento
                            AND e2.usuarios_id_usuarios = ${me})`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver recomendaciones.');
}

export async function listRecommendations(
  eventId: number,
  options: ListRecommendationsQuery,
  actor: SessionUser,
): Promise<{ items: Recommendation[]; total: number; page: number; pageSize: number }> {
  // Valida visibilidad del evento: un borrador responde 404 al docente y al estudiante.
  await loadEvent({ query }, eventId, actor);

  const params: unknown[] = [eventId];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`r.eventos_id_eventos = $1${recommendationScope(actor, bind)}`];

  if (options.emprendimientoId !== undefined) {
    where.push(`r.emprendimiento_id_emprendimiento = ${bind(options.emprendimientoId)}`);
  }
  if (options.estudianteId !== undefined) {
    where.push(`r.usuarios_id_estudiante = ${bind(options.estudianteId)}`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM recomendaciones_evento r
         ${whereSql}`,
      countParams,
    ),
    query<RecommendationRow>(
      `${SELECT_RECOMMENDATION} ${whereSql}
        ORDER BY r.fecha DESC, r.id_recomendacion DESC
        LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapRecommendation),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

export async function createRecommendation(
  eventId: number,
  input: CreateRecommendationInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Recommendation> {
  if (actor.rolId !== ROLES.DOCENTE) {
    throw new AppError(
      403,
      'ROLE_NOT_ALLOWED',
      'Solo un docente recomienda eventos a sus emprendimientos asignados.',
    );
  }

  const id = await withTransaction(async (db) => {
    // Solo emprendimientos con asignación activa del docente (T27).
    const target = await requireMentorAccess(db, input.emprendimientoId, actor);

    const { rows: events } = await db.query<{
      id_eventos: number;
      nombre_evento: string;
    }>(
      `SELECT id_eventos, nombre_evento
         FROM eventos
        WHERE id_eventos = $1
          AND fecha_eliminacion IS NULL
          AND estado = 'Publicado'`,
      [eventId],
    );
    const event = events[0];
    if (!event) throw notFound();

    if (input.estudianteId !== undefined && input.estudianteId !== null) {
      if (input.estudianteId !== target.estudianteId) {
        throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos de la recomendación.', {
          estudianteId: 'El estudiante no es el propietario del emprendimiento',
        });
      }
    }

    const estudianteId = input.estudianteId ?? target.estudianteId;

    const inserted = await db.query<{ id: number }>(
      `INSERT INTO recomendaciones_evento
         (mensaje, estado, eventos_id_eventos, emprendimiento_id_emprendimiento,
          usuarios_id_estudiante, usuarios_id_docente)
       VALUES ($1, 'Pendiente', $2, $3, $4, $5)
       RETURNING id_recomendacion AS id`,
      [input.mensaje ?? null, eventId, target.id, estudianteId, actor.id],
    );

    const recomendacionId = inserted.rows[0]!.id;

    await audit(db, {
      accion: AUDIT_ACTIONS.RECOMMEND_EVENT,
      entidad: 'recomendaciones_evento',
      entidadId: recomendacionId,
      valorNuevo: {
        eventoId: eventId,
        emprendimientoId: target.id,
        estudianteId,
        mensaje: input.mensaje ?? null,
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: estudianteId,
      tipo: 'Evento',
      mensaje: `${actor.nombres} ${actor.apellidos} te recomendó el evento «${event.nombre_evento}»${
        input.mensaje ? `: ${input.mensaje}` : '.'
      }`,
      url: `/estudiante/eventos/${eventId}`,
      tipoObjeto: 'evento',
      objetoId: eventId,
    });

    return recomendacionId;
  });

  const { rows } = await query<RecommendationRow>(
    `${SELECT_RECOMMENDATION} WHERE r.id_recomendacion = $1`,
    [id],
  );

  if (!rows[0]) throw notFound();
  return mapRecommendation(rows[0]);
}
