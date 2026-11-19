import pino from 'pino';
import { env } from './env.js';

/**
 * Log estructurado. Nunca se registran contraseñas, OTP, tokens ni PII completa.
 */
export const logger = pino({
  level: env.NODE_ENV === 'test' ? 'silent' : env.NODE_ENV === 'production' ? 'info' : 'debug',
  redact: {
    paths: [
      'req.headers.cookie',
      'req.headers.authorization',
      'res.headers["set-cookie"]',
      'password',
      '*.password',
      '*.passwordActual',
      '*.passwordNueva',
      'otp',
      '*.otp',
      '*.codigo',
      'token',
      '*.token',
    ],
    censor: '[redactado]',
  },
  base: { service: 'sgemd-backend' },
});
