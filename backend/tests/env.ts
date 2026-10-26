/**
 * Variables de entorno de las pruebas. Valores ficticios, nunca secretos reales.
 *
 * Se aplican solo si no están definidas, para poder apuntar a otra base con
 * `DATABASE_URL=... npm test`. Se importa antes que cualquier módulo que lea `env.ts`.
 */
import { resolve } from 'node:path';

export function setTestEnv(): void {
  const defaults: Record<string, string> = {
    NODE_ENV: 'test',
    PORT: '3000',
    APP_ORIGIN: 'https://localhost',
    PROXY_MAX_BODY_MB: '500',
    COOKIE_SECURE: 'true',
    DATABASE_URL: 'postgres://sgemd:test@127.0.0.1:55432/sgemd_test',
    JWT_SECRET: 'test-jwt-secret-de-al-menos-32-caracteres',
    OTP_HMAC_SECRET: 'test-otp-secret-de-al-menos-32-caracteres',
    MAIL_TRANSPORT: 'file',
    MAIL_FROM: 'SGEMD <no-reply@uniminuto.edu>',
    // El transporte de archivo escribe en `storage/mail-test` (ignorado por git).
    MAIL_FILE_DIR: resolve(process.cwd(), '..', 'storage', 'mail-test'),
    STORAGE_DIR: resolve(process.cwd(), '..', 'storage'),
    BACKUPS_DIR: resolve(process.cwd(), '..', 'backups'),
    // El host de pruebas no tiene los binarios del sistema: el volcado usa un doble y la
    // instantánea cae al copiador con enlaces duros (P-45).
    PG_DUMP_BIN: resolve(process.cwd(), 'tests', 'fixtures', 'pg_dump'),
    RSYNC_BIN: resolve(process.cwd(), 'tests', 'fixtures', 'rsync-no-instalado'),
  };

  for (const [key, value] of Object.entries(defaults)) {
    if (!process.env[key]) process.env[key] = value;
  }
}
