import { existsSync } from 'node:fs';
import { config as loadEnv } from 'dotenv';
import { z } from 'zod';

// El `.env` vive en la raíz del repositorio. En desarrollo el proceso puede arrancar
// desde `backend/`, así que se buscan ambas ubicaciones.
loadEnv({ path: existsSync('.env') ? '.env' : '../.env' });

const optionalText = z
  .string()
  .optional()
  .transform((value) => (value === '' ? undefined : value));

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  APP_ORIGIN: z.string().url(),
  PROXY_MAX_BODY_MB: z.coerce.number().int().positive().default(500),
  COOKIE_SECURE: z
    .string()
    .default('true')
    .transform((value) => value === 'true'),
  DATABASE_URL: z.string().min(1),
  JWT_SECRET: z.string().min(32, 'JWT_SECRET debe tener al menos 32 caracteres'),
  OTP_HMAC_SECRET: z.string().min(32, 'OTP_HMAC_SECRET debe tener al menos 32 caracteres'),

  // Correo: solo `file` se ejercita en pruebas; relay/oauth2 necesitan credenciales de TI.
  MAIL_TRANSPORT: z.enum(['file', 'relay', 'oauth2']).default('file'),
  MAIL_FROM: z.string().default('SGEMD <no-reply@uniminuto.edu>'),
  MAIL_FILE_DIR: z.string().default('/app/storage/mail'),
  MAIL_SMTP_HOST: optionalText,
  MAIL_SMTP_PORT: z.coerce.number().int().positive().default(587),
  MAIL_SMTP_USER: optionalText,
  MAIL_SMTP_PASSWORD: optionalText,
  MAIL_OAUTH_CLIENT_ID: optionalText,
  MAIL_OAUTH_CLIENT_SECRET: optionalText,
  MAIL_OAUTH_REFRESH_TOKEN: optionalText,
  MAIL_OAUTH_TENANT_ID: optionalText,

  STORAGE_DIR: z.string().default('/app/storage'),
  BACKUPS_DIR: z.string().default('/app/backups'),
  // Binarios del respaldo. En la imagen Docker son los del sistema; la suite los apunta a
  // un doble porque el host de pruebas no tiene `pg_dump` ni `rsync` (P-45).
  PG_DUMP_BIN: z.string().default('pg_dump'),
  RSYNC_BIN: z.string().default('rsync'),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  const detail = parsed.error.issues
    .map((issue) => `  - ${issue.path.join('.')}: ${issue.message}`)
    .join('\n');
  // No se registra ningún valor: solo el nombre del campo y el motivo.
  throw new Error(`Configuración de entorno inválida:\n${detail}`);
}

export const env = parsed.data;
export type Env = typeof env;
