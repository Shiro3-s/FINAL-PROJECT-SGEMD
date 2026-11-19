import { createHmac, randomInt, timingSafeEqual } from 'node:crypto';
import { env } from '../config/env.js';

/** Longitud exigida por el master §15 y el prototipo. */
export const OTP_DIGITS = 8;

/** Vigencia del código (master §15: 5 minutos). */
export const OTP_TTL_MINUTES = 5;

/** Intentos permitidos por código antes de quemarlo (master §15: máximo 5). */
export const OTP_MAX_ATTEMPTS = 5;

/** Espera mínima entre reenvíos (decisión P-11; configurable por entorno). */
export const OTP_RESEND_COOLDOWN_SECONDS = Number(process.env.OTP_RESEND_COOLDOWN_SECONDS ?? 60);

/** 8 dígitos criptográficamente aleatorios, con ceros a la izquierda. */
export function generateOtp(): string {
  return String(randomInt(0, 10 ** OTP_DIGITS)).padStart(OTP_DIGITS, '0');
}

/**
 * HMAC-SHA256 del código, ligado al correo y al propósito (D20 + D23).
 *
 * Ligarlo al contexto evita que un código robado de una cuenta sirva en otra y que la
 * tabla se precalcule: el mismo código produce HMAC distinto por destinatario.
 */
export function hashOtp(correo: string, proposito: string, codigo: string): string {
  return createHmac('sha256', env.OTP_HMAC_SECRET)
    .update(`${correo.toLowerCase()}:${proposito}:${codigo}`)
    .digest('hex');
}

/** Comparación en tiempo constante de dos HMAC hexadecimales. */
export function hmacMatches(expectedHex: string, candidateHex: string): boolean {
  const expected = Buffer.from(expectedHex, 'hex');
  const candidate = Buffer.from(candidateHex, 'hex');
  if (expected.length !== candidate.length || expected.length === 0) return false;
  return timingSafeEqual(expected, candidate);
}
