import { mkdir, readdir, readFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { env } from '../src/config/env.js';

/** Correo único por caso: evita colisiones entre archivos de prueba. */
let counter = 0;
export function uniqueEmail(prefix = 'estudiante'): string {
  counter += 1;
  return `${prefix}.${Date.now()}.${counter}@uniminuto.edu.co`;
}

export function uniqueDocument(): string {
  counter += 1;
  return `9${String(Date.now()).slice(-7)}${String(counter).padStart(2, '0')}`;
}

/** Vacía el buzón de archivo antes de cada caso. */
export async function clearMailbox(): Promise<void> {
  await rm(env.MAIL_FILE_DIR, { recursive: true, force: true });
  await mkdir(env.MAIL_FILE_DIR, { recursive: true });
}

async function latestMailFile(): Promise<string | null> {
  const files = (await readdir(env.MAIL_FILE_DIR).catch(() => [])).filter((file) =>
    file.endsWith('.eml'),
  );
  if (files.length === 0) return null;
  // Los nombres empiezan por la marca ISO, así que ordenar alfabéticamente es cronológico.
  files.sort();
  return join(env.MAIL_FILE_DIR, files[files.length - 1]!);
}

/** Lee el último `.eml` y devuelve el código de 8 dígitos que contiene. */
export async function readLatestOtp(): Promise<string> {
  const file = await latestMailFile();
  if (!file) throw new Error('No hay ningún correo en el buzón de pruebas');

  const content = await readFile(file, 'utf8');
  const match = /es:\s*(\d{8})/.exec(content);
  if (!match) throw new Error(`El correo no contiene un código de 8 dígitos:\n${content}`);

  return match[1]!;
}

export async function countMailFiles(): Promise<number> {
  const files = (await readdir(env.MAIL_FILE_DIR).catch(() => [])).filter((file) =>
    file.endsWith('.eml'),
  );
  return files.length;
}
