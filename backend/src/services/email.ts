import { getMailer } from '../adapters/mailer/index.js';
import { logger } from '../config/logger.js';
import { AppError } from '../utils/AppError.js';
import { OTP_TTL_MINUTES } from '../utils/otp.js';
import { query } from '../db/pool.js';

export interface MailContent {
  subject: string;
  text: string;
}

/* -------------------------------------------------------------------------------------
 * Dominio institucional
 * ----------------------------------------------------------------------------------- */

export function normalizeEmail(value: string): string {
  return value.trim().toLowerCase();
}

async function allowedDomains(): Promise<string[]> {
  const { rows } = await query<{ valor: string | null }>(
    `SELECT valor FROM configuracion_programa WHERE clave = 'correos_dominios_permitidos'`,
  );
  const raw = rows[0]?.valor ?? 'uniminuto.edu,uniminuto.edu.co';
  return raw
    .split(',')
    .map((domain) => domain.trim().toLowerCase())
    .filter(Boolean);
}

/**
 * Solo se aceptan correos de los dominios de `configuracion_programa` (D3). Vale tanto
 * para el registro público como para las altas del administrador.
 */
export async function assertInstitutionalEmail(correo: string): Promise<void> {
  const domains = await allowedDomains();
  const matches = domains.some((domain) => correo.endsWith(`@${domain}`));
  if (!matches) {
    throw new AppError(
      400,
      'EMAIL_DOMAIN_NOT_ALLOWED',
      `Usa tu correo institucional (${domains.map((d) => `@${d}`).join(' o ')}).`,
      { correoInstitucional: 'El dominio del correo no está permitido' },
    );
  }
}

/* -------------------------------------------------------------------------------------
 * Transporte
 * ----------------------------------------------------------------------------------- */

/** Envía el correo y traduce un fallo del transporte a un error controlado. */
export async function sendMail(to: string, content: MailContent): Promise<void> {
  const mailer = getMailer();
  try {
    await mailer.send({ to, ...content });
  } catch (error) {
    logger.error({ err: error, transport: mailer.transport }, 'No se pudo enviar el correo');
    throw new AppError(
      502,
      'MAIL_SEND_FAILED',
      'No fue posible enviar el correo. Intenta de nuevo en unos minutos.',
    );
  }
}

/**
 * Envío sin efecto sobre la respuesta.
 *
 * Se usa cuando el hecho de negocio ya está confirmado (la cuenta existe, el estado ya
 * cambió) y un fallo de correo no debe revertirlo ni convertir la operación en un error.
 * Queda en el registro del servidor.
 */
export async function sendMailBestEffort(
  to: string,
  content: MailContent,
  context: string,
): Promise<void> {
  try {
    await sendMail(to, content);
  } catch (error) {
    logger.warn({ err: error, correo: to }, `No se pudo enviar el correo de ${context}`);
  }
}

/* -------------------------------------------------------------------------------------
 * Plantillas
 * ----------------------------------------------------------------------------------- */

export function verificationMail(codigo: string): MailContent {
  return {
    subject: 'SGEMD · Verifica tu correo institucional',
    text: [
      'Hola,',
      '',
      'Recibimos tu registro en el Sistema de Gestión de Emprendimiento Minuto de Dios.',
      '',
      `Tu código de verificación es: ${codigo}`,
      '',
      `El código vence en ${OTP_TTL_MINUTES} minutos y solo se puede usar una vez.`,
      'Si no solicitaste este registro, ignora este mensaje.',
      '',
      'Coordinación del programa · Minuto de Dios',
    ].join('\n'),
  };
}

export function recoveryMail(codigo: string): MailContent {
  return {
    subject: 'SGEMD · Recupera tu contraseña',
    text: [
      'Hola,',
      '',
      'Recibimos una solicitud para restablecer tu contraseña.',
      '',
      `Tu código de recuperación es: ${codigo}`,
      '',
      `El código vence en ${OTP_TTL_MINUTES} minutos y solo se puede usar una vez.`,
      'Si no solicitaste el cambio, ignora este mensaje: tu contraseña sigue igual.',
      '',
      'Coordinación del programa · Minuto de Dios',
    ].join('\n'),
  };
}

/** Invitación de una cuenta creada por la coordinación: el usuario define su clave. */
export function invitationMail(codigo: string): MailContent {
  return {
    subject: 'SGEMD · Tu cuenta fue creada',
    text: [
      'Hola,',
      '',
      'La coordinación del programa creó tu cuenta en el Sistema de Gestión de Emprendimiento Minuto de Dios.',
      '',
      `Tu código para establecer tu contraseña es: ${codigo}`,
      '',
      `El código vence en ${OTP_TTL_MINUTES} minutos y solo se puede usar una vez.`,
      'Ingresa a la plataforma con tu correo institucional y este código en «Recuperar contraseña».',
      '',
      'Coordinación del programa · Minuto de Dios',
    ].join('\n'),
  };
}

/** Correo de bienvenida al pasar la cuenta a `Activo` (Etapa 4). */
export function welcomeMail(nombres: string): MailContent {
  return {
    subject: 'SGEMD · Tu cuenta está activa',
    text: [
      `Hola ${nombres},`,
      '',
      'Tu cuenta ya está activa. Desde ahora puedes usar los módulos de trabajo de la plataforma.',
      '',
      'Coordinación del programa · Minuto de Dios',
    ].join('\n'),
  };
}
