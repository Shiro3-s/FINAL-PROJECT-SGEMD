import type { PoolClient } from 'pg';
import { query } from '../db/pool.js';
import { AppError } from '../utils/AppError.js';
import {
  OTP_MAX_ATTEMPTS,
  OTP_RESEND_COOLDOWN_SECONDS,
  OTP_TTL_MINUTES,
  generateOtp,
  hashOtp,
  hmacMatches,
} from '../utils/otp.js';

/**
 * Emisión y consumo de códigos de `codigosverificacion`.
 *
 * Lo comparten la verificación de correo, la recuperación de contraseña y la invitación
 * de una cuenta creada por el administrador. El código en claro nunca se guarda (D20) ni
 * viaja en una respuesta HTTP.
 */
export type OtpPurpose = 'Verificación' | 'Recuperación';

export interface OtpContext {
  correo: string;
  proposito: OtpPurpose;
  usuarioId: number | null;
}

/** Resultado de consumir un código: se devuelve, no se lanza (ver `consumeOtp`). */
export type OtpResult =
  | { ok: true }
  | { ok: false; reason: 'OTP_INVALID' | 'OTP_ATTEMPTS_EXCEEDED' };

/**
 * Emite un código nuevo y devuelve el valor en claro (solo para el correo).
 *
 * Invalida los anteriores para que en todo momento haya un único código válido. No hay
 * columna de fecha de creación: el cooldown se deriva de `expiracion - vigencia` (P-13).
 */
export async function issueOtp(db: PoolClient, context: OtpContext): Promise<string> {
  const codigo = generateOtp();
  const hashed = hashOtp(context.correo, context.proposito, codigo);

  await db.query(
    `UPDATE codigosverificacion
        SET usado = TRUE
      WHERE correo_institucional = $1 AND proposito = $2 AND usado = FALSE`,
    [context.correo, context.proposito],
  );

  await db.query(
    `INSERT INTO codigosverificacion
       (correo_institucional, proposito, codigo, expiracion, usado, intentos, usuarios_id_usuarios)
     VALUES ($1, $2, $3, now() + ($4 || ' minutes')::interval, FALSE, 0, $5)`,
    [context.correo, context.proposito, hashed, String(OTP_TTL_MINUTES), context.usuarioId],
  );

  return codigo;
}

/** Impide pedir otro código antes del cooldown (P-11). */
export async function assertResendAllowed(correo: string, proposito: string): Promise<void> {
  const { rows } = await query<{ expiracion: Date }>(
    `SELECT expiracion
       FROM codigosverificacion
      WHERE correo_institucional = $1 AND proposito = $2 AND usado = FALSE AND expiracion > now()
      ORDER BY id_codigo DESC
      LIMIT 1`,
    [correo, proposito],
  );

  const row = rows[0];
  if (!row) return;

  const createdAt = new Date(row.expiracion).getTime() - OTP_TTL_MINUTES * 60_000;
  const readyAt = createdAt + OTP_RESEND_COOLDOWN_SECONDS * 1_000;
  const waitMs = readyAt - Date.now();

  if (waitMs > 0) {
    const seconds = Math.ceil(waitMs / 1_000);
    throw new AppError(
      429,
      'OTP_COOLDOWN',
      `Espera ${seconds} segundo${seconds === 1 ? '' : 's'} antes de pedir otro código.`,
      undefined,
      seconds,
    );
  }
}

/** Traduce el fallo de un código al error HTTP documentado. */
export function otpFailure(reason: 'OTP_INVALID' | 'OTP_ATTEMPTS_EXCEEDED'): AppError {
  return reason === 'OTP_ATTEMPTS_EXCEEDED'
    ? new AppError(
        429,
        'OTP_ATTEMPTS_EXCEEDED',
        'Superaste el número de intentos. Pide un nuevo código.',
        undefined,
        OTP_RESEND_COOLDOWN_SECONDS,
      )
    : new AppError(422, 'OTP_INVALID', 'El código no es válido o expiró. Pide uno nuevo.');
}

/**
 * Verifica y consume un código. Un código vencido, ya usado o inexistente produce el
 * mismo `OTP_INVALID`: no se revela cuál de los tres ocurrió.
 *
 * Devuelve el resultado en vez de lanzar a propósito: el incremento de `intentos` debe
 * **confirmarse** aunque el código sea incorrecto. Si se lanzara desde aquí, el ROLLBACK
 * del llamador borraría el contador y el límite de intentos nunca se alcanzaría (lo
 * detecta T05).
 */
export async function consumeOtp(
  db: PoolClient,
  correo: string,
  proposito: OtpPurpose,
  codigo: string,
): Promise<OtpResult> {
  const { rows } = await db.query<{ id_codigo: number; codigo: string; intentos: number }>(
    `SELECT id_codigo, codigo, intentos
       FROM codigosverificacion
      WHERE correo_institucional = $1
        AND proposito = $2
        AND usado = FALSE
        AND expiracion > now()
      ORDER BY id_codigo DESC
      LIMIT 1
      FOR UPDATE`,
    [correo, proposito],
  );

  const row = rows[0];
  if (!row) {
    return { ok: false, reason: 'OTP_INVALID' };
  }

  if (row.intentos >= OTP_MAX_ATTEMPTS) {
    await db.query('UPDATE codigosverificacion SET usado = TRUE WHERE id_codigo = $1', [
      row.id_codigo,
    ]);
    return { ok: false, reason: 'OTP_ATTEMPTS_EXCEEDED' };
  }

  if (!hmacMatches(row.codigo, hashOtp(correo, proposito, codigo))) {
    const intentos = row.intentos + 1;
    const exhausted = intentos >= OTP_MAX_ATTEMPTS;

    await db.query(
      'UPDATE codigosverificacion SET intentos = $2, usado = $3 WHERE id_codigo = $1',
      [row.id_codigo, intentos, exhausted],
    );

    return { ok: false, reason: exhausted ? 'OTP_ATTEMPTS_EXCEEDED' : 'OTP_INVALID' };
  }

  await db.query('UPDATE codigosverificacion SET usado = TRUE WHERE id_codigo = $1', [
    row.id_codigo,
  ]);

  return { ok: true };
}
