import { execFile, spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  copyFile,
  link,
  mkdir,
  readFile,
  readdir,
  rm,
  stat,
  utimes,
  writeFile,
} from 'node:fs/promises';
import { dirname, join, resolve, sep } from 'node:path';
import { promisify } from 'node:util';
import type { Response } from 'express';
import { env } from '../config/env.js';
import { logger } from '../config/logger.js';
import { AppError } from '../utils/AppError.js';

/**
 * Motor de respaldos (D22, §15, T24).
 *
 * Orden obligatorio: primero el volcado de PostgreSQL, después la instantánea de
 * evidencias. La instantánea es incremental con enlaces duros: cada respaldo es un árbol
 * completo y navegable, pero un archivo sin cambios comparte inodo con el respaldo
 * anterior y no ocupa disco nuevo.
 *
 * En la imagen Docker se usa `rsync -a --link-dest` (sin shell, con array de argumentos).
 * El host de pruebas no tiene `rsync`, así que el mismo contrato se implementa con
 * `fs.link`; el resultado es idéntico (mismos inodos, mismo tamaño añadido) y así la
 * suite puede verificar T24 sin depender de un binario del sistema (P-45).
 */

const execFileAsync = promisify(execFile);

const MB = 1024 * 1024;

export interface ManifestFile {
  ruta: string;
  bytes: number;
  sha256: string;
}

export interface Manifest {
  codigo: string;
  tipo: string;
  generadoEn: string;
  motor: 'rsync' | 'link';
  base: string | null;
  archivos: ManifestFile[];
  totalBytes: number;
}

export type ManifestSummary = Omit<Manifest, 'archivos'> & { archivos: number };

/** Nombres que nunca entran a la instantánea: correo y subidas a medio escribir. */
const EXCLUDED_TOP = new Set(['mail', 'mail-test']);
const PART_SUFFIX = '.part';

let rsyncAvailable: boolean | null = null;

export function hasRsync(): boolean {
  if (rsyncAvailable === null) {
    const probe = spawnSync(env.RSYNC_BIN, ['--version'], { stdio: 'ignore' });
    rsyncAvailable = probe.status === 0;
  }
  return rsyncAvailable;
}

function sha256(buffer: Buffer | string): string {
  return createHash('sha256').update(buffer).digest('hex');
}

export async function sha256File(file: string): Promise<string> {
  return sha256(await readFile(file));
}

/** Volcado `pg_dump --format=custom`; devuelve los bytes escritos. */
export async function runDump(file: string): Promise<number> {
  await mkdir(dirname(file), { recursive: true });

  try {
    await execFileAsync(
      env.PG_DUMP_BIN,
      ['--format=custom', '--no-owner', '--no-privileges', '--file', file, env.DATABASE_URL],
      { maxBuffer: 10 * MB },
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new AppError(500, 'BACKUP_DUMP_FAILED', `El volcado de la base falló: ${detail}`);
  }

  return (await stat(file)).size;
}

function isExcluded(rel: string, name: string): boolean {
  if (rel === '' && EXCLUDED_TOP.has(name)) return true;
  return name.endsWith(PART_SUFFIX);
}

async function quickEqual(source: string, candidate: string): Promise<boolean> {
  const [a, b] = await Promise.all([stat(source), stat(candidate)]);
  // rsync compara tamaño y mtime en segundos (`-a` conserva ambos).
  return a.size === b.size && Math.floor(a.mtimeMs / 1000) === Math.floor(b.mtimeMs / 1000);
}

async function copyTree(
  sourceRoot: string,
  destRoot: string,
  previousRoot: string | null,
  rel: string,
): Promise<void> {
  const entries = await readdir(join(sourceRoot, rel), { withFileTypes: true });

  for (const entry of entries) {
    const relPath = rel === '' ? entry.name : `${rel}/${entry.name}`;
    if (isExcluded(rel, entry.name)) continue;

    if (entry.isDirectory()) {
      await mkdir(join(destRoot, relPath), { recursive: true });
      await copyTree(sourceRoot, destRoot, previousRoot, relPath);
      continue;
    }

    if (!entry.isFile()) continue;

    const source = join(sourceRoot, relPath);
    const dest = join(destRoot, relPath);
    await mkdir(dirname(dest), { recursive: true });

    const previous = previousRoot === null ? null : join(previousRoot, relPath);
    if (previous !== null && (await quickEqual(source, previous).catch(() => false))) {
      try {
        await link(previous, dest);
        continue;
      } catch {
        // Si el enlace falla (otro sistema de archivos), se copia: el respaldo sigue válido.
      }
    }

    await copyFile(source, dest);
    // Conserva el mtime para que la próxima instantánea reconozca el archivo como igual.
    const info = await stat(source);
    await utimes(dest, info.atime, info.mtime);
  }
}

/**
 * Copia `STORAGE_DIR` a `dest` reutilizando los inodos del respaldo anterior.
 * Devuelve el motor usado, que queda en el manifiesto para diagnóstico.
 */
export async function snapshotStorage(
  dest: string,
  previous: string | null,
): Promise<{ motor: 'rsync' | 'link' }> {
  await mkdir(dest, { recursive: true });

  if (hasRsync()) {
    const args = ['-a', '--exclude', '/mail/', '--exclude', '/mail-test/', '--exclude', '*.part'];
    if (previous !== null) args.push('--link-dest', previous);
    args.push(`${resolve(env.STORAGE_DIR)}/`, `${resolve(dest)}/`);

    try {
      await execFileAsync(env.RSYNC_BIN, args, { maxBuffer: 10 * MB });
      return { motor: 'rsync' };
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      throw new AppError(500, 'BACKUP_SNAPSHOT_FAILED', `La instantánea de evidencias falló: ${detail}`);
    }
  }

  logger.warn({ rsync: env.RSYNC_BIN }, 'rsync no está disponible: se usa el copiador con enlaces duros');
  await copyTree(env.STORAGE_DIR, dest, previous, '');
  return { motor: 'link' };
}

interface WalkEntry {
  ruta: string;
  file: string;
  bytes: number;
  ino: number;
}

async function walk(root: string, rel = '', acc: WalkEntry[] = []): Promise<WalkEntry[]> {
  const entries = await readdir(join(root, rel), { withFileTypes: true });
  for (const entry of entries) {
    const relPath = rel === '' ? entry.name : `${rel}/${entry.name}`;
    if (entry.isDirectory()) {
      await walk(root, relPath, acc);
      continue;
    }
    if (!entry.isFile()) continue;
    const file = join(root, relPath);
    const info = await stat(file);
    acc.push({ ruta: relPath, file, bytes: info.size, ino: info.ino });
  }
  return acc;
}

/** Tamaño lógico del árbol y bytes que ocupan disco nuevo (archivos no enlazados). */
export async function treeStats(
  root: string,
  previous: string | null,
): Promise<{ totalBytes: number; addedBytes: number; archivos: number }> {
  const files = await walk(root);
  const previousInodes = new Map<string, number>();

  if (previous !== null) {
    for (const file of await walk(previous)) previousInodes.set(file.ruta, file.ino);
  }

  let totalBytes = 0;
  let addedBytes = 0;

  for (const file of files) {
    totalBytes += file.bytes;
    if (previousInodes.get(file.ruta) !== file.ino) addedBytes += file.bytes;
  }

  return { totalBytes, addedBytes, archivos: files.length };
}

/**
 * Manifiesto con ruta, tamaño y SHA-256. Solo se hashean los archivos nuevos: si el inodo
 * es el mismo del respaldo anterior, el contenido es necesariamente el mismo y se reutiliza
 * el hash ya calculado.
 */
export async function buildManifest(
  root: string,
  previous: string | null,
  previousManifest: Manifest | null,
  header: { codigo: string; tipo: string; motor: 'rsync' | 'link'; base: string | null },
): Promise<Manifest> {
  const files = await walk(root);
  const previousInodes = new Map<string, number>();
  const previousHashes = new Map<string, ManifestFile>();

  if (previous !== null) {
    for (const file of await walk(previous)) previousInodes.set(file.ruta, file.ino);
  }
  for (const file of previousManifest?.archivos ?? []) previousHashes.set(file.ruta, file);

  const archivos: ManifestFile[] = [];
  let totalBytes = 0;

  for (const file of files.sort((a, b) => a.ruta.localeCompare(b.ruta))) {
    totalBytes += file.bytes;
    const reused = previousHashes.get(file.ruta);
    const linked = previousInodes.get(file.ruta) === file.ino;

    archivos.push({
      ruta: file.ruta,
      bytes: file.bytes,
      sha256:
        linked && reused !== undefined && reused.bytes === file.bytes
          ? reused.sha256
          : await sha256File(file.file),
    });
  }

  return {
    codigo: header.codigo,
    tipo: header.tipo,
    generadoEn: new Date().toISOString(),
    motor: header.motor,
    base: header.base,
    archivos,
    totalBytes,
  };
}

export async function writeManifest(
  dir: string,
  manifest: Manifest,
): Promise<{ checksum: string; bytes: number }> {
  const body = `${JSON.stringify(manifest, null, 2)}\n`;
  const file = join(dir, 'manifest.json');
  await writeFile(file, body, 'utf8');
  return { checksum: sha256(body), bytes: Buffer.byteLength(body) };
}

export async function readManifest(dir: string): Promise<Manifest | null> {
  try {
    const raw = await readFile(join(dir, 'manifest.json'), 'utf8');
    return JSON.parse(raw) as Manifest;
  } catch {
    return null;
  }
}

export function summarizeManifest(manifest: Manifest): ManifestSummary {
  return {
    codigo: manifest.codigo,
    tipo: manifest.tipo,
    generadoEn: manifest.generadoEn,
    motor: manifest.motor,
    base: manifest.base,
    totalBytes: manifest.totalBytes,
    archivos: manifest.archivos.length,
  };
}

export async function removeDirectory(dir: string): Promise<void> {
  await rm(dir, { recursive: true, force: true });
}

/** Un directorio solo se borra si está dentro de `BACKUPS_DIR` (nunca una ruta arbitraria). */
export function isInsideBackups(dir: string): boolean {
  const root = resolve(env.BACKUPS_DIR);
  const target = resolve(dir);
  return target === root || target.startsWith(`${root}${sep}`);
}

export function megabytes(bytes: number): number {
  return Math.ceil(bytes / MB);
}

/** Transmite la instantánea como `tar.gz` sin escribir un archivo temporal. */
export function streamSnapshot(dir: string, res: Response, filename: string): Promise<void> {
  return new Promise((resolvePromise, reject) => {
    const tar = spawn('tar', ['-czf', '-', '-C', dir, '.'], { stdio: ['ignore', 'pipe', 'pipe'] });

    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');

    tar.stdout.pipe(res);

    tar.once('error', (error) => reject(error));
    tar.stderr.once('data', (chunk: Buffer) => {
      logger.warn({ stderr: chunk.toString() }, 'tar reportó un problema al empaquetar la instantánea');
    });
    res.once('close', () => tar.kill('SIGTERM'));
    tar.once('close', (code) => {
      if (code === 0) resolvePromise();
      else reject(new AppError(500, 'BACKUP_TAR_FAILED', 'No se pudo empaquetar la instantánea.'));
    });
  });
}
