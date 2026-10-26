import type { ActaEstado } from '@sgemd/shared';
import type { Request } from 'express';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { notify } from '../../services/notify.js';
import { settingInt, type SqlExecutor } from '../../services/programSettings.js';
import { receiveUpload, removeStoredFile } from '../../services/storage.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type { ListActaQuery, ReviewActaInput } from './schemas.js';

/**
 * Acta de compromiso y confidencialidad (FR-003, BR-009, T26).
 *
 * El estudiante descarga la plantilla institucional, la firma y sube el archivo. Cada
 * carga crea una **versión** del acta en `En revisión`; el administrador la aprueba o la
 * rechaza con motivo. Una versión rechazada se puede reemplazar; una pendiente o aprobada
 * no se vuelve a subir.
 *
 * BR-001 ya está implementado en el módulo de asignaciones: una asignación exige al menos
 * un acta `Aprobada`, así que la aprobación es la que habilita el mentor.
 */

export interface Acta {
  id: number;
  estado: ActaEstado;
  observaciones: string | null;
  fechaCarga: string | null;
  fechaRevision: string | null;
  emprendimiento: { id: number; codigo: string; nombre: string };
  estudiante: {
    id: number;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  };
  revisor: { id: number; nombres: string; apellidos: string } | null;
  adjunto: {
    id: number;
    nombreArchivo: string;
    tamanoBytes: number;
    tipoMime: string;
    fechaSubida: string;
  } | null;
}

type ActaRow = {
  id_acta: number;
  estado: string;
  observaciones: string | null;
  fecha_carga: Date | null;
  fecha_revision: Date | null;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  estudiante_id: number;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_correo: string;
  revisor_id: number | null;
  revisor_nombres: string | null;
  revisor_apellidos: string | null;
  adjunto_id: number | null;
  adjunto_nombre: string | null;
  adjunto_tamano: string | number | null;
  adjunto_mime: string | null;
  adjunto_fecha: Date | null;
};

const SELECT = `
  SELECT a.id_acta, a.estado, a.observaciones, a.fecha_carga, a.fecha_revision,
         e.id_emprendimiento AS emprendimiento_id,
         e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         u.id_usuarios AS estudiante_id,
         u.nombres AS estudiante_nombres,
         u.apellidos AS estudiante_apellidos,
         u.correo_institucional AS estudiante_correo,
         r.id_usuarios AS revisor_id,
         r.nombres AS revisor_nombres,
         r.apellidos AS revisor_apellidos,
         ad.id_adjunto AS adjunto_id,
         ad.nombre_archivo AS adjunto_nombre,
         ad.tamano_bytes AS adjunto_tamano,
         ad.tipo_mime AS adjunto_mime,
         ad.fecha_subida AS adjunto_fecha
    FROM actas a
    JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
    JOIN usuarios u ON u.id_usuarios = a.usuarios_id_estudiante
    LEFT JOIN usuarios r ON r.id_usuarios = a.usuarios_id_revisor
    LEFT JOIN adjuntos ad
      ON ad.id_adjunto = a.adjuntos_id_adjunto
     AND ad.fecha_eliminacion IS NULL
`;

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El acta no existe.');
}

function mapRow(row: ActaRow): Acta {
  return {
    id: row.id_acta,
    estado: row.estado as ActaEstado,
    observaciones: row.observaciones,
    fechaCarga: row.fecha_carga ? row.fecha_carga.toISOString() : null,
    fechaRevision: row.fecha_revision ? row.fecha_revision.toISOString() : null,
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
    revisor:
      row.revisor_id === null
        ? null
        : {
            id: row.revisor_id,
            nombres: row.revisor_nombres ?? '',
            apellidos: row.revisor_apellidos ?? '',
          },
    adjunto:
      row.adjunto_id === null
        ? null
        : {
            id: row.adjunto_id,
            nombreArchivo: row.adjunto_nombre ?? '',
            tamanoBytes: Number(row.adjunto_tamano ?? 0),
            tipoMime: row.adjunto_mime ?? '',
            fechaSubida: row.adjunto_fecha
              ? row.adjunto_fecha.toISOString()
              : new Date(0).toISOString(),
          },
  };
}

async function loadActa(id: number): Promise<Acta> {
  const { rows } = await query<ActaRow>(
    `${SELECT} WHERE a.id_acta = $1 AND e.fecha_eliminacion IS NULL`,
    [id],
  );

  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/** El acta solo la ven el administrador y su dueño; el docente recibe `404`. */
function authorize(acta: Acta, actor: SessionUser): void {
  const allowed =
    actor.rolId === ROLES.ADMIN ||
    (actor.rolId === ROLES.ESTUDIANTE && actor.id === acta.estudiante.id);

  if (!allowed) throw notFound();
}

export async function getActa(id: number, actor: SessionUser): Promise<Acta> {
  const acta = await loadActa(id);
  authorize(acta, actor);
  return acta;
}

/** Emprendimiento vigente del estudiante (el más reciente si tiene paralelos). */
async function findOwnedEntrepreneurship(
  db: SqlExecutor,
  actor: SessionUser,
): Promise<{ id: number; nombre: string }> {
  const { rows } = await db.query<{ id: number; nombre: string }>(
    `SELECT id_emprendimiento AS id, nombre
       FROM emprendimiento
      WHERE usuarios_id_usuarios = $1
        AND fecha_eliminacion IS NULL
        AND estado_aprobacion <> 'Rechazado'
      ORDER BY id_emprendimiento DESC
      LIMIT 1`,
    [actor.id],
  );

  if (!rows[0]) {
    throw new AppError(
      422,
      'ENTREPRENEURSHIP_REQUIRED',
      'Necesitas un emprendimiento vigente para cargar el acta.',
    );
  }

  return rows[0];
}

async function latestState(
  db: SqlExecutor,
  emprendimientoId: number,
): Promise<ActaEstado | null> {
  const { rows } = await db.query<{ estado: ActaEstado }>(
    `SELECT estado FROM actas
      WHERE emprendimiento_id_emprendimiento = $1
      ORDER BY id_acta DESC
      LIMIT 1`,
    [emprendimientoId],
  );

  return rows[0]?.estado ?? null;
}

/**
 * `GET /acta/template`: plantilla institucional para firmar.
 *
 * El repositorio no tiene el texto legal del acta (FR-003/AQ-12 no lo aportan). Servir un
 * documento inventado sería peor que declarar el hueco: la coordinación debe entregar la
 * plantilla y, mientras tanto, el estudiante puede subir la que reciba por otro canal.
 */
export function actaTemplate(): never {
  throw new AppError(
    404,
    'ACTA_TEMPLATE_NOT_CONFIGURED',
    'La plantilla del acta todavía no está configurada. Solicítala a la coordinación.',
  );
}

/** `POST /acta`: el estudiante sube el acta firmada (multipart, campo `file`). */
export async function uploadActa(
  actor: SessionUser,
  req: Request,
  ip: string | null,
): Promise<Acta> {
  const entrepreneurship = await findOwnedEntrepreneurship({ query }, actor);
  const maxMb = await settingInt({ query }, 'upload_max_mb', 500);

  const stored = await receiveUpload(req, {
    entity: 'acta',
    maxBytes: maxMb * 1024 * 1024,
  });

  let id: number;
  try {
    id = await withTransaction(async (db) => {
      await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
        `acta:${entrepreneurship.id}`,
      ]);

      const estado = await latestState(db, entrepreneurship.id);
      if (estado === 'En revisión') {
        throw new AppError(
          409,
          'ACTA_ALREADY_PENDING',
          'Ya hay un acta en revisión para este emprendimiento.',
        );
      }
      if (estado === 'Aprobada') {
        throw new AppError(
          409,
          'ACTA_ALREADY_APPROVED',
          'El acta de este emprendimiento ya fue aprobada.',
        );
      }

      const inserted = await db.query<{ id_adjunto: number }>(
        `INSERT INTO adjuntos
           (nombre_archivo, ruta_archivo, tamano_bytes, tipo_mime, usuarios_id_usuarios)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id_adjunto`,
        [stored.nombreArchivo, stored.rutaArchivo, stored.tamanoBytes, stored.tipoMime, actor.id],
      );

      const adjuntoId = inserted.rows[0]!.id_adjunto;

      const acta = await db.query<{ id_acta: number }>(
        `INSERT INTO actas
           (estado, fecha_carga, emprendimiento_id_emprendimiento,
            usuarios_id_estudiante, adjuntos_id_adjunto)
         VALUES ('En revisión', now(), $1, $2, $3)
         RETURNING id_acta`,
        [entrepreneurship.id, actor.id, adjuntoId],
      );

      const actaId = acta.rows[0]!.id_acta;

      await audit(db, {
        accion: AUDIT_ACTIONS.UPLOAD_ACTA,
        entidad: 'actas',
        entidadId: actaId,
        valorNuevo: {
          estado: 'En revisión',
          emprendimientoId: entrepreneurship.id,
          nombreArchivo: stored.nombreArchivo,
          tamanoBytes: stored.tamanoBytes,
          tipoMime: stored.tipoMime,
        },
        usuarioId: actor.id,
        ip,
      });

      const admins = await db.query<{ id: number }>(
        `SELECT id_usuarios AS id
           FROM usuarios
          WHERE roles_id_roles = $1
            AND estado = 'Activo'
            AND fecha_eliminacion IS NULL`,
        [ROLES.ADMIN],
      );

      for (const admin of admins.rows) {
        await notify(db, {
          usuarioId: admin.id,
          tipo: 'Sistema',
          mensaje: `${actor.nombres} ${actor.apellidos} cargó el acta de «${entrepreneurship.nombre}».`,
          url: '/admin/actas',
          tipoObjeto: 'acta',
          objetoId: actaId,
        });
      }

      return actaId;
    });
  } catch (error) {
    await removeStoredFile(stored.rutaArchivo);
    throw error;
  }

  return loadActa(id);
}

/** `PUT /acta/:id/review`: aprobar o rechazar con motivo (BR-009). */
export async function reviewActa(
  id: number,
  actor: SessionUser,
  input: ReviewActaInput,
  ip: string | null,
): Promise<Acta> {
  await withTransaction(async (db) => {
    await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [`acta:${id}`]);

    const { rows } = await db.query<{
      id_acta: number;
      estado: string;
      observaciones: string | null;
      emprendimiento_id: number;
      estudiante_id: number;
      emprendimiento_nombre: string;
    }>(
      `SELECT a.id_acta, a.estado, a.observaciones,
              a.emprendimiento_id_emprendimiento AS emprendimiento_id,
              a.usuarios_id_estudiante AS estudiante_id,
              e.nombre AS emprendimiento_nombre
         FROM actas a
         JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
        WHERE a.id_acta = $1 AND e.fecha_eliminacion IS NULL
        FOR UPDATE`,
      [id],
    );

    const row = rows[0];
    if (!row) throw notFound();

    if (row.estado !== 'En revisión') {
      throw new AppError(
        422,
        'ACTA_NOT_REVIEWABLE',
        'Solo se puede revisar un acta en estado «En revisión».',
      );
    }

    await db.query(
      `UPDATE actas
          SET estado = $2, observaciones = $3, usuarios_id_revisor = $4,
              fecha_revision = now()
        WHERE id_acta = $1`,
      [id, input.estado, input.observaciones ?? null, actor.id],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.REVIEW_ACTA,
      entidad: 'actas',
      entidadId: id,
      valorAnterior: { estado: row.estado, observaciones: row.observaciones },
      valorNuevo: {
        estado: input.estado,
        observaciones: input.observaciones ?? null,
        revisorId: actor.id,
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: row.estudiante_id,
      tipo: 'Sistema',
      mensaje:
        input.estado === 'Aprobada'
          ? `El acta de «${row.emprendimiento_nombre}» fue aprobada.`
          : `El acta de «${row.emprendimiento_nombre}» fue rechazada: ${input.observaciones}`,
      url: '/estudiante/acta',
      tipoObjeto: 'acta',
      objetoId: id,
    });
  });

  return loadActa(id);
}

/** `GET /acta`: bandeja del administrador o las actas del estudiante. */
export async function listActas(
  options: ListActaQuery,
  actor: SessionUser,
): Promise<{ items: Acta[]; total: number; page: number; pageSize: number }> {
  const params: unknown[] = [];
  const where: string[] = ['e.fecha_eliminacion IS NULL'];

  if (actor.rolId === ROLES.ESTUDIANTE) {
    params.push(actor.id);
    where.push(`a.usuarios_id_estudiante = $${params.length}`);
  }

  if (options.estado) {
    params.push(options.estado);
    where.push(`a.estado = $${params.length}`);
  }
  if (options.emprendimientoId) {
    params.push(options.emprendimientoId);
    where.push(`a.emprendimiento_id_emprendimiento = $${params.length}`);
  }
  if (options.estudianteId) {
    params.push(options.estudianteId);
    where.push(`a.usuarios_id_estudiante = $${params.length}`);
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
    fecha: 'a.fecha_carga',
    estado: 'a.estado',
    estudiante: 'u.apellidos',
    emprendimiento: 'e.nombre',
  }[options.sort];

  params.push(options.pageSize);
  const limit = `$${params.length}`;
  params.push((options.page - 1) * options.pageSize);
  const offset = `$${params.length}`;

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM actas a
         JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
         JOIN usuarios u ON u.id_usuarios = a.usuarios_id_estudiante
         ${whereSql}`,
      countParams,
    ),
    query<ActaRow>(
      `${SELECT} ${whereSql}
        ORDER BY ${orderBy} ${options.order.toUpperCase()}, a.id_acta DESC
        LIMIT ${limit} OFFSET ${offset}`,
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
