import type { SolicitudEstado, SolicitudTipo } from '@sgemd/shared';
import type { PoolClient } from 'pg';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { blockedReason } from '../../policy/accountState.js';
import { applyAccountTransition } from '../../services/accountLifecycle.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { sendMailBestEffort, welcomeMail } from '../../services/email.js';
import { notify } from '../../services/notify.js';
import { settingInt } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import { insertAdvice } from '../advice/service.js';
import type { SessionUser } from '../auth/types.js';
import type {
  ApproveRequestInput,
  CreateRequestInput,
  ListRequestsQuery,
} from './schemas.js';

/**
 * Bandeja única de solicitudes (FR-014, R38, T36).
 *
 * Concentra los tres tipos que el prototipo resolvía por rutas sueltas: desbloqueo de
 * cuenta, autorización de un emprendimiento paralelo y cita de asesoría. Aprobar aplica
 * el efecto de dominio **en la misma transacción** que la resolución, de modo que no
 * puede quedar una solicitud aprobada sin su efecto ni un efecto sin su solicitud.
 */

/* -------------------------------------------------------------------------------------
 * Lectura
 * ----------------------------------------------------------------------------------- */

type RequestRow = {
  id_solicitud: number;
  tipo: string;
  detalle: string | null;
  estado: string;
  motivo_rechazo: string | null;
  fecha_solicitud: Date;
  fecha_resolucion: Date | null;
  emprendimiento_id_emprendimiento: number | null;
  solicitante_id: number;
  solicitante_codigo: string;
  solicitante_nombres: string;
  solicitante_apellidos: string;
  solicitante_correo: string;
  emprendimiento_codigo: string | null;
  emprendimiento_nombre: string | null;
  resuelto_por_id: number | null;
  resuelto_por_nombres: string | null;
  resuelto_por_apellidos: string | null;
};

export interface RequestDetail {
  id: number;
  tipo: SolicitudTipo;
  detalle: string | null;
  estado: SolicitudEstado;
  motivoRechazo: string | null;
  fechaSolicitud: string;
  fechaResolucion: string | null;
  solicitante: {
    id: number;
    codigo: string;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  };
  emprendimiento: { id: number; codigo: string; nombre: string } | null;
  resueltoPor: { id: number; nombres: string; apellidos: string } | null;
}

const SELECT = `
  SELECT s.id_solicitud, s.tipo, s.detalle, s.estado, s.motivo_rechazo,
         s.fecha_solicitud, s.fecha_resolucion,
         s.emprendimiento_id_emprendimiento,
         u.id_usuarios AS solicitante_id, u.codigo AS solicitante_codigo,
         u.nombres AS solicitante_nombres, u.apellidos AS solicitante_apellidos,
         u.correo_institucional AS solicitante_correo,
         e.codigo AS emprendimiento_codigo, e.nombre AS emprendimiento_nombre,
         r.id_usuarios AS resuelto_por_id,
         r.nombres AS resuelto_por_nombres, r.apellidos AS resuelto_por_apellidos
    FROM solicitudes s
    JOIN usuarios u ON u.id_usuarios = s.usuarios_id_usuarios
    LEFT JOIN emprendimiento e
      ON e.id_emprendimiento = s.emprendimiento_id_emprendimiento
    LEFT JOIN usuarios r ON r.id_usuarios = s.usuarios_id_resuelto_por
`;

function mapRow(row: RequestRow): RequestDetail {
  return {
    id: row.id_solicitud,
    tipo: row.tipo as SolicitudTipo,
    detalle: row.detalle,
    estado: row.estado as SolicitudEstado,
    motivoRechazo: row.motivo_rechazo,
    fechaSolicitud: row.fecha_solicitud.toISOString(),
    fechaResolucion: row.fecha_resolucion ? row.fecha_resolucion.toISOString() : null,
    solicitante: {
      id: row.solicitante_id,
      codigo: row.solicitante_codigo,
      nombres: row.solicitante_nombres,
      apellidos: row.solicitante_apellidos,
      correoInstitucional: row.solicitante_correo,
    },
    emprendimiento:
      row.emprendimiento_id_emprendimiento === null
        ? null
        : {
            id: row.emprendimiento_id_emprendimiento,
            codigo: row.emprendimiento_codigo ?? '',
            nombre: row.emprendimiento_nombre ?? '',
          },
    resueltoPor:
      row.resuelto_por_id === null
        ? null
        : {
            id: row.resuelto_por_id,
            nombres: row.resuelto_por_nombres ?? '',
            apellidos: row.resuelto_por_apellidos ?? '',
          },
  };
}

export interface RequestPage {
  items: RequestDetail[];
  total: number;
  page: number;
  pageSize: number;
  /** Contador de pendientes por tipo, sobre toda la bandeja (no sobre el filtro). */
  pendientes: {
    total: number;
    Desbloqueo: number;
    Paralelo: number;
    Cita: number;
  };
}

const SORT_COLUMNS: Record<ListRequestsQuery['sort'], string> = {
  fecha: 's.fecha_solicitud',
  tipo: 's.tipo',
  estado: 's.estado',
};

export async function listRequests(options: ListRequestsQuery): Promise<RequestPage> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where: string[] = ['TRUE'];

  if (options.tipo) where.push(`s.tipo = ${bind(options.tipo)}`);
  if (options.estado) where.push(`s.estado = ${bind(options.estado)}`);
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(
      `(u.nombres ILIKE ${like} OR u.apellidos ILIKE ${like} OR u.codigo ILIKE ${like}
        OR u.correo_institucional ILIKE ${like} OR s.detalle ILIKE ${like})`,
    );
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction}, s.id_solicitud ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page, pending] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM solicitudes s
         JOIN usuarios u ON u.id_usuarios = s.usuarios_id_usuarios
         ${whereSql}`,
      countParams,
    ),
    query<RequestRow>(
      `${SELECT} ${whereSql} ORDER BY ${orderSql} LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
    query<{ tipo: string; total: string }>(
      `SELECT tipo, COUNT(*)::text AS total
         FROM solicitudes
        WHERE estado = 'Pendiente'
        GROUP BY tipo`,
    ),
  ]);

  const pendientes = { total: 0, Desbloqueo: 0, Paralelo: 0, Cita: 0 };
  for (const row of pending.rows) {
    const total = Number(row.total);
    pendientes.total += total;
    if (row.tipo === 'Desbloqueo' || row.tipo === 'Paralelo' || row.tipo === 'Cita') {
      pendientes[row.tipo] = total;
    }
  }

  return {
    items: page.rows.map(mapRow),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
    pendientes,
  };
}

export async function getRequest(id: number): Promise<RequestDetail> {
  const { rows } = await query<RequestRow>(`${SELECT} WHERE s.id_solicitud = $1`, [id]);
  if (!rows[0]) {
    throw new AppError(404, 'NOT_FOUND', 'La solicitud no existe.');
  }
  return mapRow(rows[0]);
}

/* -------------------------------------------------------------------------------------
 * Creación
 * ----------------------------------------------------------------------------------- */

const TIPO_LABEL: Readonly<Record<SolicitudTipo, string>> = {
  Desbloqueo: 'desbloqueo de cuenta',
  Paralelo: 'emprendimiento paralelo',
  Cita: 'cita de asesoría',
};

/**
 * Crea una solicitud a nombre de la sesión actual.
 *
 * - `Desbloqueo`: la puede pedir una cuenta `Limitado` o `Inactivo` (es precisamente lo
 *   que necesita). Una cuenta `Activo` no tiene nada que desbloquear.
 * - `Paralelo` y `Cita`: son módulos de trabajo, así que exigen cuenta `Activo` y un
 *   emprendimiento del propio estudiante.
 *
 * El detalle es libre porque el diagrama solo tiene `detalle` (texto): el prototipo pide
 * «nuevo emprendimiento / sector» y «docente sugerido / fecha propuesta», que no tienen
 * columnas propias (P-20).
 */
export async function createRequest(
  input: CreateRequestInput,
  actor: SessionUser,
  ip: string | null,
): Promise<RequestDetail> {
  if (input.tipo === 'Desbloqueo') {
    if (actor.estado === 'Activo') {
      throw new AppError(422, 'ACCOUNT_ALREADY_ACTIVE', 'Tu cuenta ya está activa.');
    }
    if (input.emprendimientoId) {
      throw new AppError(
        400,
        'VALIDATION_ERROR',
        'El desbloqueo de cuenta no se refiere a un emprendimiento.',
        { emprendimientoId: 'No envíes este campo para un desbloqueo' },
      );
    }
  } else {
    if (actor.estado !== 'Activo') {
      throw new AppError(403, 'ACCOUNT_NOT_ACTIVE', blockedReason(actor.estado));
    }
    if (actor.rolId !== ROLES.ESTUDIANTE) {
      throw new AppError(
        403,
        'ROLE_NOT_ALLOWED',
        'Solo un estudiante puede solicitar un paralelo o una cita.',
      );
    }
    if (!input.emprendimientoId) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Selecciona el emprendimiento.', {
        emprendimientoId: 'El emprendimiento es obligatorio para este tipo de solicitud',
      });
    }
  }

  const id = await withTransaction(async (db) => {
    let emprendimientoId: number | null = null;

    if (input.tipo !== 'Desbloqueo') {
      const { rows } = await db.query<{ estado_aprobacion: string }>(
        `SELECT estado_aprobacion
           FROM emprendimiento
          WHERE id_emprendimiento = $1
            AND usuarios_id_usuarios = $2
            AND fecha_eliminacion IS NULL`,
        [input.emprendimientoId, actor.id],
      );

      const own = rows[0];
      if (!own) {
        throw new AppError(
          400,
          'VALIDATION_ERROR',
          'El emprendimiento no existe o no te pertenece.',
          { emprendimientoId: 'Selecciona uno de tus emprendimientos' },
        );
      }

      if (input.tipo === 'Paralelo' && own.estado_aprobacion !== 'Aprobado') {
        throw new AppError(
          422,
          'ENTREPRENEURSHIP_NOT_APPROVED',
          'Solo puedes solicitar un paralelo sobre un emprendimiento aprobado.',
        );
      }

      emprendimientoId = input.emprendimientoId ?? null;
    }

    const inserted = await db.query<{ id_solicitud: number }>(
      `INSERT INTO solicitudes
         (tipo, detalle, estado, usuarios_id_usuarios, emprendimiento_id_emprendimiento)
       VALUES ($1, $2, 'Pendiente', $3, $4)
       RETURNING id_solicitud`,
      [input.tipo, input.detalle ?? null, actor.id, emprendimientoId],
    );

    const nuevoId = inserted.rows[0]!.id_solicitud;

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_REQUEST,
      entidad: 'solicitudes',
      entidadId: nuevoId,
      valorNuevo: {
        tipo: input.tipo,
        emprendimientoId,
        estado: 'Pendiente',
      },
      usuarioId: actor.id,
      ip,
    });

    // La coordinación se entera en su bandeja: el contador de pendientes es la señal.
    const admins = await db.query<{ id: number }>(
      `SELECT id_usuarios AS id
         FROM usuarios
        WHERE roles_id_roles = $1 AND estado = 'Activo' AND fecha_eliminacion IS NULL`,
      [ROLES.ADMIN],
    );

    for (const admin of admins.rows) {
      await notify(db, {
        usuarioId: admin.id,
        tipo: 'Solicitud',
        mensaje: `Nueva solicitud de ${TIPO_LABEL[input.tipo]} de ${actor.nombres} ${actor.apellidos}.`,
        url: '/admin/solicitudes',
        tipoObjeto: 'solicitudes',
        objetoId: nuevoId,
      });
    }

    return nuevoId;
  });

  return getRequest(id);
}

/* -------------------------------------------------------------------------------------
 * Resolución (T36)
 * ----------------------------------------------------------------------------------- */

type LockedRequest = {
  id_solicitud: number;
  tipo: string;
  estado: string;
  usuarios_id_usuarios: number;
  emprendimiento_id_emprendimiento: number | null;
};

function alreadyResolved(): AppError {
  return new AppError(
    422,
    'REQUEST_ALREADY_RESOLVED',
    'La solicitud ya fue aprobada o rechazada.',
  );
}

/** Bloquea la solicitud y exige que siga `Pendiente`. */
async function lockPendingRequest(db: PoolClient, id: number): Promise<LockedRequest> {
  const { rows } = await db.query<LockedRequest>(
    `SELECT id_solicitud, tipo, estado, usuarios_id_usuarios,
            emprendimiento_id_emprendimiento
       FROM solicitudes
      WHERE id_solicitud = $1
      FOR UPDATE`,
    [id],
  );

  const row = rows[0];
  if (!row) throw new AppError(404, 'NOT_FOUND', 'La solicitud no existe.');
  if (row.estado !== 'Pendiente') throw alreadyResolved();
  return row;
}

/**
 * `PUT /requests/:id/approve` — resuelve y aplica el efecto exactamente una vez.
 *
 * | Tipo | Efecto |
 * |---|---|
 * | `Desbloqueo` | `Limitado`/`Inactivo → Activo`. Si ya estaba `Activo`, solo se resuelve |
 * | `Paralelo` | `es_paralelo = TRUE` en el emprendimiento (con el tope `paralelos_maximos`) |
 * | `Cita` | Crea la asesoría en `Programada` con el docente y el horario elegidos (P-19) |
 *
 * La solicitud se bloquea con `FOR UPDATE` y el `UPDATE` vuelve a condicionar por
 * `Pendiente`: dos aprobaciones simultáneas no pueden aplicar el efecto dos veces.
 */
export async function approveRequest(
  id: number,
  input: ApproveRequestInput,
  actor: SessionUser,
  ip: string | null,
): Promise<RequestDetail> {
  // El arreglo (en vez de `let … | null`) evita que TypeScript estreche a `never` la
  // variable asignada dentro del callback de la transacción.
  const activated: { correoInstitucional: string; nombres: string }[] = [];

  const schedulingKeys = [
    'docenteId',
    'tema',
    'fecha',
    'horaInicio',
    'horaFin',
    'modalidadId',
    'lugarEnlace',
  ] as const;
  const hasScheduling = schedulingKeys.some((key) => input[key] !== undefined);

  await withTransaction(async (db) => {
    const request = await lockPendingRequest(db, id);
    let efecto: string | null = null;

    if (request.tipo !== 'Cita' && hasScheduling) {
      throw new AppError(
        400,
        'VALIDATION_ERROR',
        'Solo una cita de asesoría usa los datos de programación.',
        { tipo: 'Esta solicitud no es una cita de asesoría' },
      );
    }

    if (request.tipo === 'Desbloqueo') {
      const { rows } = await db.query<{ estado: string }>(
        'SELECT estado FROM usuarios WHERE id_usuarios = $1 FOR UPDATE',
        [request.usuarios_id_usuarios],
      );

      const estado = rows[0]?.estado;
      if (!estado) {
        throw new AppError(422, 'REQUEST_TARGET_MISSING', 'La cuenta solicitante ya no existe.');
      }

      if (estado === 'Activo') {
        // Otra vía ya la activó: la solicitud se resuelve sin repetir la transición.
        efecto = 'sin cambio: la cuenta ya estaba Activo';
      } else {
        const result = await applyAccountTransition(db, {
          usuarioId: request.usuarios_id_usuarios,
          to: 'Activo',
          actorId: actor.id,
          ip,
          notifyAccount: false,
        });
        activated.push({
          correoInstitucional: result.correoInstitucional,
          nombres: result.nombres,
        });
        efecto = `${result.from} → Activo`;
      }
    }

    if (request.tipo === 'Paralelo') {
      if (!request.emprendimiento_id_emprendimiento) {
        throw new AppError(
          422,
          'REQUEST_TARGET_MISSING',
          'La solicitud no tiene un emprendimiento asociado.',
        );
      }

      const { rows } = await db.query<{ id: number; es_paralelo: boolean }>(
        `SELECT id_emprendimiento AS id, es_paralelo
           FROM emprendimiento
          WHERE id_emprendimiento = $1 AND fecha_eliminacion IS NULL
          FOR UPDATE`,
        [request.emprendimiento_id_emprendimiento],
      );

      const target = rows[0];
      if (!target) {
        throw new AppError(
          422,
          'REQUEST_TARGET_MISSING',
          'El emprendimiento de la solicitud ya no existe.',
        );
      }

      if (!target.es_paralelo) {
        const cap = await settingInt(db, 'paralelos_maximos', 1);
        const { rows: counted } = await db.query<{ total: string }>(
          `SELECT COUNT(*)::text AS total
             FROM emprendimiento
            WHERE usuarios_id_usuarios = $1
              AND es_paralelo = TRUE
              AND estado_aprobacion <> 'Rechazado'
              AND fecha_eliminacion IS NULL
              AND id_emprendimiento <> $2`,
          [request.usuarios_id_usuarios, target.id],
        );

        if (Number(counted[0]?.total ?? 0) >= cap) {
          throw new AppError(
            422,
            'PARALLEL_LIMIT_REACHED',
            `El estudiante ya alcanzó el máximo de ${cap} emprendimiento(s) paralelo(s).`,
          );
        }

        await db.query(
          'UPDATE emprendimiento SET es_paralelo = TRUE WHERE id_emprendimiento = $1',
          [target.id],
        );
        efecto = 'esParalelo = TRUE';
      } else {
        efecto = 'sin cambio: el emprendimiento ya estaba marcado como paralelo';
      }
    }

    // `Cita`: la aprobación es el momento en que la coordinación asigna docente y horario
    // (P-19). La asesoría nace `Programada`; el docente la confirma después con `accept`.
    if (request.tipo === 'Cita') {
      if (!request.emprendimiento_id_emprendimiento) {
        throw new AppError(
          422,
          'REQUEST_TARGET_MISSING',
          'La solicitud no tiene un emprendimiento asociado.',
        );
      }

      const missing: Record<string, string> = {};
      if (input.docenteId === undefined) missing.docenteId = 'Selecciona el docente';
      if (input.tema === undefined) missing.tema = 'Escribe el tema de la asesoría';
      if (input.fecha === undefined) missing.fecha = 'Selecciona la fecha';

      if (Object.keys(missing).length > 0) {
        throw new AppError(
          400,
          'VALIDATION_ERROR',
          'Para aprobar una cita indica el docente, el tema y el horario.',
          missing,
        );
      }

      const { rows } = await db.query<{ nombre: string }>(
        `SELECT nombre
           FROM emprendimiento
          WHERE id_emprendimiento = $1 AND fecha_eliminacion IS NULL`,
        [request.emprendimiento_id_emprendimiento],
      );

      const target = rows[0];
      if (!target) {
        throw new AppError(
          422,
          'REQUEST_TARGET_MISSING',
          'El emprendimiento de la solicitud ya no existe.',
        );
      }

      const created = await insertAdvice(
        db,
        {
          emprendimiento: {
            id: request.emprendimiento_id_emprendimiento,
            nombre: target.nombre,
            estudianteId: request.usuarios_id_usuarios,
          },
          docenteId: input.docenteId!,
          tema: input.tema!,
          modalidadId: input.modalidadId,
          lugarEnlace: input.lugarEnlace,
          schedule: {
            fecha: input.fecha!,
            horaInicio: input.horaInicio!,
            horaFin: input.horaFin!,
          },
        },
        actor,
        ip,
      );

      efecto = `asesoría #${created.id} creada (${created.estado})`;
    }

    const { rowCount } = await db.query(
      `UPDATE solicitudes
          SET estado = 'Aprobada', fecha_resolucion = now(), usuarios_id_resuelto_por = $2
        WHERE id_solicitud = $1 AND estado = 'Pendiente'`,
      [id, actor.id],
    );

    if (rowCount === 0) throw alreadyResolved();

    await audit(db, {
      accion: AUDIT_ACTIONS.APPROVE_REQUEST,
      entidad: 'solicitudes',
      entidadId: id,
      valorAnterior: { estado: request.estado, tipo: request.tipo },
      valorNuevo: { estado: 'Aprobada', efecto },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: request.usuarios_id_usuarios,
      tipo: 'Solicitud',
      mensaje: `Tu solicitud de ${TIPO_LABEL[request.tipo as SolicitudTipo]} fue aprobada.`,
      tipoObjeto: 'solicitudes',
      objetoId: id,
    });
  });

  const welcome = activated[0];
  if (welcome) {
    await sendMailBestEffort(
      welcome.correoInstitucional,
      welcomeMail(welcome.nombres),
      'bienvenida por desbloqueo',
    );
  }

  return getRequest(id);
}

/**
 * `PUT /requests/:id/reject` — rechazo con motivo obligatorio (R38, T12).
 *
 * No aplica ningún efecto de dominio: la cuenta, el emprendimiento y la agenda quedan
 * como estaban. El motivo se guarda y se envía al solicitante.
 */
export async function rejectRequest(
  id: number,
  motivo: string,
  actor: SessionUser,
  ip: string | null,
): Promise<RequestDetail> {
  await withTransaction(async (db) => {
    const request = await lockPendingRequest(db, id);

    const { rowCount } = await db.query(
      `UPDATE solicitudes
          SET estado = 'Rechazada', motivo_rechazo = $2, fecha_resolucion = now(),
              usuarios_id_resuelto_por = $3
        WHERE id_solicitud = $1 AND estado = 'Pendiente'`,
      [id, motivo, actor.id],
    );

    if (rowCount === 0) throw alreadyResolved();

    await audit(db, {
      accion: AUDIT_ACTIONS.REJECT_REQUEST,
      entidad: 'solicitudes',
      entidadId: id,
      valorAnterior: { estado: request.estado, tipo: request.tipo },
      valorNuevo: { estado: 'Rechazada', motivo },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: request.usuarios_id_usuarios,
      tipo: 'Solicitud',
      mensaje: `Tu solicitud de ${TIPO_LABEL[request.tipo as SolicitudTipo]} fue rechazada. Motivo: ${motivo}`,
      tipoObjeto: 'solicitudes',
      objetoId: id,
    });
  });

  return getRequest(id);
}
