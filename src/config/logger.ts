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
      'password',
      '*.password',
      'otp',
      '*.otp',
      'token',
      '*.token',
    ],
    censor: '[redactado]',
  },
  base: { service: 'sgemd-backend' },
});
