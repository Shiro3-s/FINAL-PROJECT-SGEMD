import { existsSync } from 'node:fs';
import { config as loadEnv } from 'dotenv';
import { z } from 'zod';

// El `.env` vive en la raíz del repositorio. En desarrollo el proceso puede arrancar
// desde `backend/`, así que se buscan ambas ubicaciones.
loadEnv({ path: existsSync('.env') ? '.env' : '../.env' });

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
  MAIL_TRANSPORT: z.enum(['file', 'relay', 'oauth2']).default('file'),
  MAIL_FROM: z.string().default('SGEMD <no-reply@uniminuto.edu>'),
  MAIL_FILE_DIR: z.string().default('/app/storage/mail'),
  STORAGE_DIR: z.string().default('/app/storage'),
  BACKUPS_DIR: z.string().default('/app/backups'),
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
