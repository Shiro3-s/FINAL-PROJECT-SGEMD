import type { Request, Response } from 'express';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import {
  countEvidence,
  isEvidenceEntity,
  type EvidenceEntity,
} from '../../services/evidence.js';
import { settingInt } from '../../services/programSettings.js';
import { openStoredFile, receiveUpload, removeStoredFile } from '../../services/storage.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import {
  loadAdviceEvidenceTarget,
  type AdviceEvidenceTarget,
} from '../advice/service.js';
import {
  loadTaskEvidenceTarget,
  type TaskEvidenceTarget,
} from '../tasks/service.js';
import {
  loadTracingEvidenceTarget,
  type TracingEvidenceTarget,
} from '../tracing/service.js';

/**
 * Evidencias (FR-008, BR-006, BR-007).
 *
 * Un adjunto cuelga de una tarea, un seguimiento o una asesoría mediante su pivote. Aquí
 * se resuelve **quién** puede subir, descargar y borrar cada archivo; las reglas de disco
 * (MIME por contenido, nombre aleatorio, `*.part`, tamaño) viven en `services/storage.ts`.
 *
 * Cada entidad resuelve su alcance con el servicio dueño del registro, de modo que la
 * regla de acceso nunca se duplica ni queda más laxa que en su módulo.
 */

type EvidenceTarget = TaskEvidenceTarget | TracingEvidenceTarget | AdviceEvidenceTarget;

const ENTITY_LABEL: Readonly<Record<EvidenceEntity, string>> = {
  task: 'tarea',
  tracing: 'seguimiento',
  advice: 'asesoría',
};

export interface Attachment {
  id: number;
  nombreArchivo: string;
  tamanoBytes: number;
  tipoMime: string;
  fechaSubida: string;
  subidoPor: { id: number; nombres: string; apellidos: string } | null;
  entidad: EvidenceEntity;
  entidadId: number;
}

type AttachmentRow = {
  id_adjunto: number;
  nombre_archivo: string;
  ruta_archivo: string;
  tamano_bytes: string | number;
  tipo_mime: string;
  fecha_subida: Date;
  usuarios_id_usuarios: number;
  subido_nombres: string | null;
  subido_apellidos: string | null;
  tarea_id: number | null;
  seguimiento_id: number | null;
  asesoria_id: number | null;
};

const SELECT_ATTACHMENT = `
  SELECT a.id_adjunto, a.nombre_archivo, a.ruta_archivo, a.tamano_bytes, a.tipo_mime,
         a.fecha_subida, a.usuarios_id_usuarios,
         u.nombres AS subido_nombres, u.apellidos AS subido_apellidos,
         (SELECT p.tareas_id_tareas FROM adjuntos_tareas p
           WHERE p.adjuntos_id_adjunto = a.id_adjunto) AS tarea_id,
         (SELECT p.seguimientos_id_seguimientos FROM adjuntos_seguimientos p
           WHERE p.adjuntos_id_adjunto = a.id_adjunto) AS seguimiento_id,
         (SELECT p.asesorias_id_asesorias FROM adjuntos_asesorias p
           WHERE p.adjuntos_id_adjunto = a.id_adjunto) AS asesoria_id
    FROM adjuntos a
    LEFT JOIN usuarios u ON u.id_usuarios = a.usuarios_id_usuarios
`;

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'La evidencia no existe.');
}

function entityOf(row: AttachmentRow): { entity: EvidenceEntity; parentId: number } {
  if (row.tarea_id !== null) return { entity: 'task', parentId: row.tarea_id };
  if (row.seguimiento_id !== null) return { entity: 'tracing', parentId: row.seguimiento_id };
  if (row.asesoria_id !== null) return { entity: 'advice', parentId: row.asesoria_id };
  throw notFound();
}

function mapRow(row: AttachmentRow): Attachment {
  const { entity, parentId } = entityOf(row);

  return {
    id: row.id_adjunto,
    nombreArchivo: row.nombre_archivo,
    tamanoBytes: Number(row.tamano_bytes),
    tipoMime: row.tipo_mime,
    fechaSubida: row.fecha_subida.toISOString(),
    subidoPor: {
      id: row.usuarios_id_usuarios,
      nombres: row.subido_nombres ?? '',
      apellidos: row.subido_apellidos ?? '',
    },
    entidad: entity,
    entidadId: parentId,
  };
}

/** Entidad de la ruta: las tres que tienen servicio de autorización. */
export function parseEntity(raw: string): EvidenceEntity {
  if (!isEvidenceEntity(raw)) {
    throw new AppError(400, 'VALIDATION_ERROR', 'La entidad de la evidencia no es válida.', {
      entity: 'Valores admitidos: task, tracing, advice',
    });
  }
  return raw;
}

async function loadTarget(
  entity: EvidenceEntity,
  parentId: number,
  actor: SessionUser,
): Promise<EvidenceTarget> {
  if (entity === 'task') return loadTaskEvidenceTarget(parentId, actor);
  if (entity === 'tracing') return loadTracingEvidenceTarget(parentId, actor);
  return loadAdviceEvidenceTarget(parentId, actor);
}

async function loadRow(id: number): Promise<AttachmentRow> {
  const { rows } = await query<AttachmentRow>(
    `${SELECT_ATTACHMENT} WHERE a.id_adjunto = $1 AND a.fecha_eliminacion IS NULL`,
    [id],
  );

  const row = rows[0];
  if (!row) throw notFound();
  return row;
}

/** Autoriza la **lectura** resolviendo el padre con su propio alcance (404 si no). */
async function authorizeRead(
  row: AttachmentRow,
  actor: SessionUser,
): Promise<{ entity: EvidenceEntity; parentId: number }> {
  const { entity, parentId } = entityOf(row);
  await loadTarget(entity, parentId, actor);
  return { entity, parentId };
}

/**
 * Autoriza la **escritura**.
 *
 * - Tarea: el estudiante destinatario (sube su evidencia) o el administrador. El docente
 *   califica, no sube evidencia.
 * - Seguimiento: el autor del registro o el administrador.
 * - Asesoría: el estudiante dueño, el docente asignado o el administrador.
 *
 * Una tarea en revisión o completada tiene la evidencia congelada
 * (`422 TASK_EVIDENCE_LOCKED`); una asesoría completada o cancelada, también
 * (`422 ADVICE_EVIDENCE_LOCKED`). El administrador puede borrar en ambos casos.
 */
function authorizeWrite(
  entity: EvidenceEntity,
  target: EvidenceTarget,
  actor: SessionUser,
  mode: 'upload' | 'delete',
): void {
  if (entity === 'task') {
    const task = target as TaskEvidenceTarget;
    const isAdmin = actor.rolId === ROLES.ADMIN;
    const isOwner = task.estudianteId !== null && actor.id === task.estudianteId;

    if (mode === 'upload' && !isAdmin && !isOwner) {
      throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo el estudiante entrega la evidencia.');
    }
    if (mode === 'delete' && !isAdmin && !isOwner) {
      throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo quien subió la evidencia puede borrarla.');
    }

    const locked = task.estado === 'En revisión' || task.estado === 'Completada';
    if (locked && (mode === 'upload' || !isAdmin)) {
      throw new AppError(
        422,
        'TASK_EVIDENCE_LOCKED',
        'La tarea ya fue entregada: su evidencia no se puede modificar.',
      );
    }
    return;
  }

  if (entity === 'tracing') {
    const tracing = target as TracingEvidenceTarget;
    if (actor.rolId !== ROLES.ADMIN && actor.id !== tracing.autorId) {
      throw new AppError(403, 'ROLE_NOT_ALLOWED', 'Solo el autor del seguimiento puede adjuntar.');
    }
    return;
  }

  const advice = target as AdviceEvidenceTarget;
  const isAdmin = actor.rolId === ROLES.ADMIN;
  const isStudent = actor.id === advice.estudianteId;
  const isTeacher = advice.docenteId !== null && actor.id === advice.docenteId;

  if (!isAdmin && !isStudent && !isTeacher) {
    throw new AppError(
      403,
      'ROLE_NOT_ALLOWED',
      'Solo el estudiante, el docente asignado o el administrador adjuntan evidencias a la asesoría.',
    );
  }

  const locked = advice.estado === 'Completada' || advice.estado === 'Cancelada';
  if (locked && (mode === 'upload' || !isAdmin)) {
    throw new AppError(
      422,
      'ADVICE_EVIDENCE_LOCKED',
      'La asesoría ya terminó: su evidencia no se puede modificar.',
    );
  }
}

/**
 * `POST /attachments/:entity/:id` — subida de una evidencia.
 *
 * Orden: autorización → tope de archivos → escritura en disco → transacción (lock, tope
 * otra vez, fila, pivote, auditoría). Si la transacción falla, el archivo recién escrito se
 * borra para no dejar basura.
 */
export async function uploadAttachment(
  entity: EvidenceEntity,
  parentId: number,
  actor: SessionUser,
  req: Request,
  ip: string | null,
): Promise<Attachment> {
  const target = await loadTarget(entity, parentId, actor);

  authorizeWrite(entity, target, actor, 'upload');

  const [maxMb, maxFiles] = await Promise.all([
    settingInt({ query }, 'upload_max_mb', 500),
    settingInt({ query }, 'upload_max_files_per_entity', 5),
  ]);

  const current = await countEvidence({ query }, entity, parentId);
  if (current >= maxFiles) {
    throw new AppError(
      422,
      'ATTACHMENT_LIMIT_REACHED',
      `Una ${ENTITY_LABEL[entity]} admite como máximo ${maxFiles} archivos de evidencia.`,
      { file: `Ya hay ${current} archivo(s) adjunto(s)` },
    );
  }

  const stored = await receiveUpload(req, {
    entity,
    maxBytes: maxMb * 1024 * 1024,
  });

  let id: number;
  try {
    id = await withTransaction(async (db) => {
      // Serializa las subidas de la misma entidad: sin el lock, dos archivos simultáneos
      // podrían superar el tope de archivos por entidad.
      await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
        `attachments:${entity}:${parentId}`,
      ]);

      const total = await countEvidence(db, entity, parentId);
      if (total >= maxFiles) {
        throw new AppError(
          422,
          'ATTACHMENT_LIMIT_REACHED',
          `Una ${ENTITY_LABEL[entity]} admite como máximo ${maxFiles} archivos de evidencia.`,
          { file: `Ya hay ${total} archivo(s) adjunto(s)` },
        );
      }

      const inserted = await db.query<{ id_adjunto: number }>(
        `INSERT INTO adjuntos
           (nombre_archivo, ruta_archivo, tamano_bytes, tipo_mime, usuarios_id_usuarios)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id_adjunto`,
        [stored.nombreArchivo, stored.rutaArchivo, stored.tamanoBytes, stored.tipoMime, actor.id],
      );

      const nuevoId = inserted.rows[0]!.id_adjunto;

      const pivot =
        entity === 'task'
          ? { table: 'adjuntos_tareas', column: 'tareas_id_tareas' }
          : entity === 'tracing'
            ? { table: 'adjuntos_seguimientos', column: 'seguimientos_id_seguimientos' }
            : { table: 'adjuntos_asesorias', column: 'asesorias_id_asesorias' };

      await db.query(
        `INSERT INTO ${pivot.table} (adjuntos_id_adjunto, ${pivot.column}) VALUES ($1, $2)`,
        [nuevoId, parentId],
      );

      await audit(db, {
        accion: AUDIT_ACTIONS.UPLOAD_ATTACHMENT,
        entidad: 'adjuntos',
        entidadId: nuevoId,
        valorNuevo: {
          nombreArchivo: stored.nombreArchivo,
          tamanoBytes: stored.tamanoBytes,
          tipoMime: stored.tipoMime,
          entidad: entity,
          entidadId: parentId,
        },
        usuarioId: actor.id,
        ip,
      });

      return nuevoId;
    });
  } catch (error) {
    await removeStoredFile(stored.rutaArchivo);
    throw error;
  }

  return getAttachment(id, actor);
}

export async function getAttachment(id: number, actor: SessionUser): Promise<Attachment> {
  const row = await loadRow(id);
  await authorizeRead(row, actor);
  return mapRow(row);
}

/**
 * `GET /attachments/:id` — descarga con alcance.
 *
 * El archivo se transmite en streaming; el nombre original va en
 * `Content-Disposition` (codificado) y el MIME es el verificado al subirlo. Un archivo que
 * ya no está en disco responde `404 ATTACHMENT_FILE_MISSING`, nunca un stack trace (T40).
 */
export async function downloadAttachment(
  id: number,
  actor: SessionUser,
  res: Response,
): Promise<void> {
  const row = await loadRow(id);
  await authorizeRead(row, actor);

  const stream = openStoredFile(row.ruta_archivo);

  await new Promise<void>((resolve, reject) => {
    stream.once('open', () => resolve());
    stream.once('error', () => {
      reject(new AppError(404, 'ATTACHMENT_FILE_MISSING', 'El archivo no está disponible.'));
    });
  });

  const fallback = row.nombre_archivo.replace(/[^\x20-\x7e]/g, '_').replace(/"/g, "'");

  res.setHeader('Content-Type', row.tipo_mime);
  res.setHeader('Content-Length', String(row.tamano_bytes));
  res.setHeader(
    'Content-Disposition',
    `attachment; filename="${fallback}"; filename*=UTF-8''${encodeURIComponent(row.nombre_archivo)}`,
  );
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Un fallo de lectura a mitad del envío no puede tumbar el proceso: se corta la
  // respuesta (el cliente ve una descarga truncada, nunca un stack trace).
  stream.on('error', () => res.destroy());

  stream.pipe(res);
}

/**
 * `DELETE /attachments/:id` — baja lógica de la fila y borrado físico del archivo.
 *
 * El archivo no se recupera (BR-006); la fila se conserva con `fecha_eliminacion` para que
 * la auditoría siga siendo legible. Un archivo ya ausente no impide la baja (T40).
 */
export async function deleteAttachment(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const row = await loadRow(id);
  const { entity, parentId } = await authorizeRead(row, actor);

  const target = await loadTarget(entity, parentId, actor);

  authorizeWrite(entity, target, actor, 'delete');

  await withTransaction(async (db) => {
    const { rowCount } = await db.query(
      `UPDATE adjuntos SET fecha_eliminacion = now()
        WHERE id_adjunto = $1 AND fecha_eliminacion IS NULL`,
      [id],
    );

    if (rowCount === 0) throw notFound();

    await db.query('DELETE FROM adjuntos_tareas WHERE adjuntos_id_adjunto = $1', [id]);
    await db.query('DELETE FROM adjuntos_seguimientos WHERE adjuntos_id_adjunto = $1', [id]);
    await db.query('DELETE FROM adjuntos_asesorias WHERE adjuntos_id_adjunto = $1', [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_ATTACHMENT,
      entidad: 'adjuntos',
      entidadId: id,
      valorAnterior: {
        nombreArchivo: row.nombre_archivo,
        tamanoBytes: Number(row.tamano_bytes),
        tipoMime: row.tipo_mime,
        entidad: entity,
        entidadId: parentId,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });
  });

  await removeStoredFile(row.ruta_archivo);
}
