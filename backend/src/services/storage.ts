import { randomUUID } from 'node:crypto';
import { createReadStream, createWriteStream } from 'node:fs';
import { mkdir, open, rename, rm, stat } from 'node:fs/promises';
import { join, resolve, sep } from 'node:path';
import { pipeline } from 'node:stream/promises';
import type { Readable } from 'node:stream';
import busboy from 'busboy';
import type { Request } from 'express';
import { TIPOS_MIME_ADJUNTO, type TipoMimeAdjunto } from '@sgemd/shared';
import { env } from '../config/env.js';
import { logger } from '../config/logger.js';
import { AppError } from '../utils/AppError.js';

/**
 * Almacenamiento de evidencias en el filesystem local (D13).
 *
 * Reglas de §15 que se cumplen aquí y no en el router:
 *
 * - **MIME por contenido**, no por extensión ni por la cabecera declarada: se leen los
 *   primeros bytes del archivo ya escrito y se compara con la lista blanca.
 * - **Nombre aleatorio** en disco (`<uuid>.<ext>`); el nombre original solo se guarda como
 *   metadato. Un nombre con separadores o `..` se rechaza antes de tocar el disco.
 * - **Temporal `*.part`**: se escribe con ese sufijo y se renombra al terminar, así un
 *   respaldo nunca copia una subida a medias y ningún `.part` se sirve jamás.
 * - **Límite de tamaño** leído de `configuracion_programa` (lo pasa el servicio).
 */

const ROOT = resolve(env.STORAGE_DIR);

/** Extensión canónica por MIME. Solo se usan los tres tipos de la lista blanca. */
const EXTENSION: Record<TipoMimeAdjunto, string> = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'application/pdf': 'pdf',
};

export interface StoredUpload {
  /** Nombre original, saneado; solo metadato. */
  nombreArchivo: string;
  /** Ruta **relativa** a `STORAGE_DIR` (la que se guarda en `adjuntos.ruta_archivo`). */
  rutaArchivo: string;
  tamanoBytes: number;
  tipoMime: TipoMimeAdjunto;
}

/**
 * Nombre original admisible.
 *
 * Rechaza separadores (`/`, `\`), byte nulo, caracteres de control y los nombres `.` y
 * `..`: una subida con nombre de travesía no llega a escribir nada (T19). El nombre nunca
 * se usa para construir la ruta.
 */
function safeOriginalName(raw: string): string | null {
  const name = raw.trim();
  if (name.length === 0 || name.length > 255) return null;
  if (name === '.' || name === '..') return null;
  if (name.includes('/') || name.includes('\\') || name.includes('\0')) return null;
  // eslint-disable-next-line no-control-regex
  if (/[\u0000-\u001f\u007f]/.test(name)) return null;
  return name;
}

/** MIME real a partir de la firma del archivo. `null` si no es de la lista blanca. */
function sniffMime(head: Buffer): TipoMimeAdjunto | null {
  if (head.length >= 3 && head[0] === 0xff && head[1] === 0xd8 && head[2] === 0xff) {
    return 'image/jpeg';
  }
  if (
    head.length >= 8 &&
    head[0] === 0x89 &&
    head[1] === 0x50 &&
    head[2] === 0x4e &&
    head[3] === 0x47 &&
    head[4] === 0x0d &&
    head[5] === 0x0a &&
    head[6] === 0x1a &&
    head[7] === 0x0a
  ) {
    return 'image/png';
  }
  if (head.length >= 5 && head.subarray(0, 5).toString('latin1') === '%PDF-') {
    return 'application/pdf';
  }
  return null;
}

/** Ruta absoluta de una ruta relativa guardada en la base, sin salir de `STORAGE_DIR`. */
export function absolutePath(rutaArchivo: string): string {
  const absolute = resolve(ROOT, rutaArchivo);
  if (absolute !== ROOT && !absolute.startsWith(`${ROOT}${sep}`)) {
    // Defensa en profundidad: una fila manipulada no puede escapar del almacenamiento.
    throw new AppError(404, 'ATTACHMENT_FILE_MISSING', 'El archivo no está disponible.');
  }
  return absolute;
}

/** Flujo de lectura del archivo almacenado. */
export function openStoredFile(rutaArchivo: string): Readable {
  return createReadStream(absolutePath(rutaArchivo));
}

/**
 * Borra el archivo del disco. Un archivo ya ausente no es un error: la fila se da de baja
 * igual y el efecto es idempotente (T40). Cualquier otro fallo se registra sin tumbar la
 * transacción que ya confirmó la baja lógica.
 */
export async function removeStoredFile(rutaArchivo: string): Promise<void> {
  try {
    await rm(absolutePath(rutaArchivo), { force: true });
  } catch (error) {
    logger.error({ err: error, rutaArchivo }, 'No se pudo borrar el archivo de una evidencia');
  }
}

interface BusboyFileStream extends Readable {
  truncated: boolean;
}

/**
 * Recibe **un** archivo `multipart/form-data` (campo `file`), lo escribe en `*.part` y,
 * cuando la firma es válida, lo renombra a su nombre definitivo.
 *
 * `entity` solo decide la carpeta (`attachments/<entity>/<año>/<mes>`); nunca viene del
 * nombre enviado. Los errores de tamaño y de tipo se lanzan **después** de borrar el
 * temporal, así no queda basura en disco.
 */
export function receiveUpload(
  req: Request,
  options: { entity: string; maxBytes: number },
): Promise<StoredUpload> {
  return new Promise<StoredUpload>((resolvePromise, rejectPromise) => {
    let parser: busboy.Busboy;

    try {
      parser = busboy({
        headers: req.headers,
        // `preservePath` deja el nombre tal cual llegó: así la travesía de rutas se
        // detecta y se rechaza explícitamente (T19) en vez de recortarse en silencio.
        preservePath: true,
        limits: { files: 1, fileSize: options.maxBytes, fields: 5, parts: 10 },
      });
    } catch {
      rejectPromise(
        new AppError(400, 'VALIDATION_ERROR', 'La petición debe ser multipart/form-data.', {
          file: 'Adjunta el archivo en el campo «file»',
        }),
      );
      return;
    }

    let failure: AppError | null = null;
    let stored: StoredUpload | null = null;
    let pending: Promise<void> | null = null;

    const fail = (error: AppError): void => {
      if (!failure) failure = error;
    };

    parser.on('file', (_field, stream: BusboyFileStream, info) => {
      if (stored || failure || pending) {
        // Solo se acepta un archivo por petición: el resto se descarta sin escribir.
        stream.resume();
        return;
      }

      const nombreArchivo = safeOriginalName(info.filename ?? '');
      if (nombreArchivo === null) {
        fail(
          new AppError(400, 'VALIDATION_ERROR', 'El nombre del archivo no es válido.', {
            file: 'El nombre no puede contener rutas ni caracteres de control',
          }),
        );
        stream.resume();
        return;
      }

      pending = writeUpload(stream, nombreArchivo, options)
        .then((value) => {
          stored = value;
        })
        .catch((error: unknown) => {
          fail(
            error instanceof AppError
              ? error
              : new AppError(400, 'VALIDATION_ERROR', 'No se pudo guardar el archivo.', {
                  file: 'Vuelve a intentarlo',
                }),
          );
        })
        .finally(() => {
          pending = null;
        });
    });

    parser.on('error', () => {
      fail(new AppError(400, 'VALIDATION_ERROR', 'No se pudo leer el archivo enviado.'));
    });

    parser.on('close', () => {
      const settle = async (): Promise<void> => {
        if (pending) await pending.catch(() => undefined);

        if (failure) {
          rejectPromise(failure);
          return;
        }
        if (!stored) {
          rejectPromise(
            new AppError(400, 'VALIDATION_ERROR', 'Adjunta un archivo de evidencia.', {
              file: 'El archivo es obligatorio',
            }),
          );
          return;
        }
        resolvePromise(stored);
      };

      void settle();
    });

    // Si el cliente corta la conexión, el parser no llega a `close`: se responde igual.
    req.on('close', () => {
      if (!req.complete) {
        fail(new AppError(400, 'VALIDATION_ERROR', 'La subida se interrumpió.'));
      }
    });

    req.pipe(parser);
  });
}

async function writeUpload(
  stream: BusboyFileStream,
  nombreArchivo: string,
  options: { entity: string; maxBytes: number },
): Promise<StoredUpload> {
  const now = new Date();
  const relativeDir = join(
    'attachments',
    options.entity,
    String(now.getUTCFullYear()),
    String(now.getUTCMonth() + 1).padStart(2, '0'),
  );
  const directory = join(ROOT, relativeDir);
  await mkdir(directory, { recursive: true });

  const identifier = randomUUID();
  const partPath = join(directory, `${identifier}.part`);

  try {
    await pipeline(stream, createWriteStream(partPath, { flags: 'wx', mode: 0o600 }));
  } catch (error) {
    await rm(partPath, { force: true });
    throw error;
  }

  // El tamaño se lee del archivo ya escrito: contar los trozos en un `data` extra
  // obligaría a consumir el flujo dos veces.
  const { size: bytes } = await stat(partPath);

  if (stream.truncated) {
    await rm(partPath, { force: true });
    const megabytes = Math.floor(options.maxBytes / (1024 * 1024));
    throw new AppError(
      413,
      'PAYLOAD_TOO_LARGE',
      `El archivo supera el máximo permitido (${megabytes} MB).`,
      { file: `El máximo por archivo es ${megabytes} MB` },
    );
  }

  if (bytes === 0) {
    await rm(partPath, { force: true });
    throw new AppError(400, 'VALIDATION_ERROR', 'El archivo está vacío.', {
      file: 'Adjunta un archivo con contenido',
    });
  }

  const handle = await open(partPath, 'r');
  const head = Buffer.alloc(8);
  try {
    await handle.read(head, 0, 8, 0);
  } finally {
    await handle.close();
  }

  const tipoMime = sniffMime(head);
  if (tipoMime === null) {
    await rm(partPath, { force: true });
    throw new AppError(
      400,
      'VALIDATION_ERROR',
      'Solo se aceptan archivos JPG, PNG o PDF.',
      { file: `Formatos admitidos: ${TIPOS_MIME_ADJUNTO.join(', ')}` },
    );
  }

  const rutaArchivo = join(relativeDir, `${identifier}.${EXTENSION[tipoMime]}`);
  await rename(partPath, join(ROOT, rutaArchivo));

  return {
    nombreArchivo,
    rutaArchivo,
    tamanoBytes: bytes,
    tipoMime,
  };
}
