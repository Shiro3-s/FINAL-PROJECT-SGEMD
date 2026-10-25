import { randomInt } from 'node:crypto';
import type { PoolClient } from 'pg';
import { getMailer } from '../../adapters/mailer/index.js';
import { query, withTransaction } from '../../db/pool.js';
import { logger } from '../../config/logger.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { AppError } from '../../utils/AppError.js';
import {
  OTP_MAX_ATTEMPTS,
  OTP_RESEND_COOLDOWN_SECONDS,
  OTP_TTL_MINUTES,
  generateOtp,
  hashOtp,
  hmacMatches,
} from '../../utils/otp.js';
import { hashPassword, verifyPassword } from '../../utils/password.js';
import type { PublicUser, SessionUser } from './types.js';
import { signSession } from './session.js';
import type {
  ForgotPasswordInput,
  LoginInput,
  RegisterInput,
  ResendInput,
  ResetPasswordInput,
  VerifyInput,
} from './schemas.js';

/** Hash de relleno para igualar el tiempo de respuesta cuando el correo no existe. */
const DUMMY_HASH = '$2b$10$XBqjrKlxlpzDuqnMNQKRSenQ5qpX1jShrV8Jc5Wec3yQRL.gv8dhm';

const ROL_ESTUDIANTE = 2;

/* -------------------------------------------------------------------------------------
 * Utilidades internas
 * ----------------------------------------------------------------------------------- */

function normalizeEmail(value: string): string {
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

async function assertInstitutionalEmail(correo: string): Promise<void> {
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

/** Código de estudiante de 6 dígitos, único dentro de `usuarios`. */
async function generateStudentCode(db: PoolClient): Promise<string> {
  for (let attempt = 0; attempt < 25; attempt += 1) {
    const candidate = String(randomInt(0, 1_000_000)).padStart(6, '0');
    const { rows } = await db.query<{ exists: boolean }>(
      'SELECT EXISTS (SELECT 1 FROM usuarios WHERE codigo = $1) AS exists',
      [candidate],
    );
    if (!rows[0]?.exists) return candidate;
  }
  throw new AppError(500, 'CODE_GENERATION_FAILED', 'No fue posible generar el código de estudiante.');
}

interface OtpContext {
  correo: string;
  proposito: 'Verificación' | 'Recuperación';
  usuarioId: number | null;
}

/**
 * Emite un código nuevo y devuelve el valor en claro (solo para el correo).
 *
 * Invalida los anteriores para que en todo momento haya un único código válido. No hay
 * columna de fecha de creación: el cooldown se deriva de `expiracion - vigencia` (P-13).
 */
async function issueOtp(db: PoolClient, context: OtpContext): Promise<string> {
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

async function assertResendAllowed(correo: string, proposito: string): Promise<void> {
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

/** Resultado de consumir un código: se devuelve, no se lanza (ver `consumeOtp`). */
type OtpResult =
  | { ok: true }
  | { ok: false; reason: 'OTP_INVALID' | 'OTP_ATTEMPTS_EXCEEDED' };

/** Traduce el fallo de un código al error HTTP documentado. */
function otpFailure(reason: 'OTP_INVALID' | 'OTP_ATTEMPTS_EXCEEDED'): AppError {
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
async function consumeOtp(
  db: PoolClient,
  correo: string,
  proposito: 'Verificación' | 'Recuperación',
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

function buildVerificationMail(codigo: string): { subject: string; text: string } {
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

function buildRecoveryMail(codigo: string): { subject: string; text: string } {
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

/** Envía el correo y traduce un fallo del transporte a un error controlado. */
async function sendMail(
  to: string,
  content: { subject: string; text: string },
): Promise<void> {
  const mailer = getMailer();
  try {
    await mailer.send({ to, ...content });
  } catch (error) {
    logger.error({ err: error, transport: mailer.transport }, 'No se pudo enviar el correo');
    throw new AppError(
      502,
      'MAIL_SEND_FAILED',
      'No fue posible enviar el correo de verificación. Intenta de nuevo en unos minutos.',
    );
  }
}

/* -------------------------------------------------------------------------------------
 * Casos de uso
 * ----------------------------------------------------------------------------------- */

export async function register(input: RegisterInput, ip: string | null): Promise<PublicUser> {
  const correo = normalizeEmail(input.correoInstitucional);
  await assertInstitutionalEmail(correo);

  const passwordHash = await hashPassword(input.password);

  const created = await withTransaction(async (db) => {
    const duplicate = await db.query<{ correo: boolean; documento: boolean }>(
      `SELECT
         EXISTS (SELECT 1 FROM usuarios WHERE correo_institucional = $1) AS correo,
         EXISTS (SELECT 1 FROM usuarios WHERE numero_documento = $2) AS documento`,
      [correo, input.numeroDocumento],
    );

    if (duplicate.rows[0]?.correo) {
      throw new AppError(409, 'EMAIL_TAKEN', 'Ya existe una cuenta con ese correo institucional.', {
        correoInstitucional: 'Este correo ya está registrado',
      });
    }
    if (duplicate.rows[0]?.documento) {
      throw new AppError(409, 'DOCUMENT_TAKEN', 'Ya existe una cuenta con ese número de documento.', {
        numeroDocumento: 'Este documento ya está registrado',
      });
    }

    const tipoDocumento = await db.query<{ id: number }>(
      'SELECT id_tipodocumentos AS id FROM tipodocumentos WHERE id_tipodocumentos = $1',
      [input.tipoDocumentoId],
    );
    if (!tipoDocumento.rows[0]) {
      throw new AppError(400, 'VALIDATION_ERROR', 'El tipo de documento no existe.', {
        tipoDocumentoId: 'Selecciona un tipo de documento válido',
      });
    }

    const codigo = await generateStudentCode(db);

    const inserted = await db.query<{ id_usuarios: number }>(
      `INSERT INTO usuarios
         (codigo, nombres, apellidos, numero_documento, correo_institucional, password,
          verificado, estado, roles_id_roles, tipo_documentos_id_tipo_documentos)
       VALUES ($1, $2, $3, $4, $5, $6, FALSE, 'Limitado', $7, $8)
       RETURNING id_usuarios`,
      [
        codigo,
        input.nombres,
        input.apellidos,
        input.numeroDocumento,
        correo,
        passwordHash,
        ROL_ESTUDIANTE,
        input.tipoDocumentoId,
      ],
    );

    const id = inserted.rows[0]!.id_usuarios;
    const plainCode = await issueOtp(db, {
      correo,
      proposito: 'Verificación',
      usuarioId: id,
    });

    await audit(db, {
      accion: AUDIT_ACTIONS.REGISTER,
      entidad: 'usuarios',
      entidadId: id,
      valorNuevo: { correoInstitucional: correo, estado: 'Limitado', verificado: false },
      usuarioId: id,
      ip,
    });

    return { id, codigo, plainCode };
  });

  await sendMail(correo, buildVerificationMail(created.plainCode));

  return {
    id: created.id,
    codigo: created.codigo,
    nombres: input.nombres,
    apellidos: input.apellidos,
    correoInstitucional: correo,
    numeroDocumento: input.numeroDocumento,
    nivelAcademico: null,
    verificado: false,
    estado: 'Limitado',
    rol: { id: ROL_ESTUDIANTE, nombre: 'Estudiante' },
    ultimaActividad: null,
  };
}

export async function verifyEmail(input: VerifyInput, ip: string | null): Promise<void> {
  const correo = normalizeEmail(input.correoInstitucional);

  // La transacción confirma el consumo del código (y el contador de intentos) antes de
  // responder; el error se lanza después para que el incremento no se revierta.
  const result = await withTransaction<OtpResult>(async (db) => {
    const { rows } = await db.query<{ id_usuarios: number; verificado: boolean }>(
      `SELECT id_usuarios, verificado
         FROM usuarios
        WHERE correo_institucional = $1 AND fecha_eliminacion IS NULL`,
      [correo],
    );

    const user = rows[0];
    if (!user) {
      return { ok: false, reason: 'OTP_INVALID' };
    }

    const otp = await consumeOtp(db, correo, 'Verificación', input.codigo);
    if (!otp.ok) return otp;

    if (!user.verificado) {
      await db.query('UPDATE usuarios SET verificado = TRUE WHERE id_usuarios = $1', [
        user.id_usuarios,
      ]);
      await audit(db, {
        accion: AUDIT_ACTIONS.VERIFY_EMAIL,
        entidad: 'usuarios',
        entidadId: user.id_usuarios,
        valorAnterior: { verificado: false },
        valorNuevo: { verificado: true },
        usuarioId: user.id_usuarios,
        ip,
      });
    }

    return { ok: true };
  });

  if (!result.ok) throw otpFailure(result.reason);
}

/**
 * Reenvía el código de verificación. No revela si la cuenta existe: responde igual en
 * todos los casos y solo envía correo cuando hay una cuenta pendiente.
 */
export async function resendCode(input: ResendInput): Promise<void> {
  const correo = normalizeEmail(input.correoInstitucional);

  const { rows } = await query<{ id_usuarios: number; verificado: boolean }>(
    `SELECT id_usuarios, verificado
       FROM usuarios
      WHERE correo_institucional = $1 AND fecha_eliminacion IS NULL`,
    [correo],
  );

  const user = rows[0];
  if (!user || user.verificado) return;

  await assertResendAllowed(correo, 'Verificación');

  const plainCode = await withTransaction(async (db) =>
    issueOtp(db, { correo, proposito: 'Verificación', usuarioId: user.id_usuarios }),
  );

  await sendMail(correo, buildVerificationMail(plainCode));
}

export interface LoginResult {
  token: string;
  user: PublicUser;
}

export async function login(input: LoginInput, ip: string | null): Promise<LoginResult> {
  const correo = normalizeEmail(input.correoInstitucional);

  const { rows } = await query<{
    id_usuarios: number;
    codigo: string;
    nombres: string;
    apellidos: string;
    correo_institucional: string;
    numero_documento: string;
    nivel_academico: string | null;
    verificado: boolean;
    estado: string;
    ultima_actividad: Date | null;
    roles_id_roles: number;
    rol_nombre: string;
    password: string;
  }>(
    `SELECT u.id_usuarios, u.codigo, u.nombres, u.apellidos, u.correo_institucional,
            u.numero_documento, u.nivel_academico, u.verificado, u.estado,
            u.ultima_actividad, u.roles_id_roles, u.password, r.nombre AS rol_nombre
       FROM usuarios u
       JOIN roles r ON r.id_roles = u.roles_id_roles
      WHERE u.correo_institucional = $1 AND u.fecha_eliminacion IS NULL`,
    [correo],
  );

  const row = rows[0];

  // Mismo tiempo de respuesta exista o no la cuenta: no se filtra por temporización.
  const passwordOk = await verifyPassword(input.password, row?.password ?? DUMMY_HASH);

  if (!row || !passwordOk) {
    throw new AppError(401, 'INVALID_CREDENTIALS', 'Correo o contraseña incorrectos.');
  }

  if (!row.verificado) {
    throw new AppError(
      403,
      'EMAIL_NOT_VERIFIED',
      'Debes verificar tu correo institucional antes de iniciar sesión.',
    );
  }

  await query('UPDATE usuarios SET ultima_actividad = now() WHERE id_usuarios = $1', [
    row.id_usuarios,
  ]);

  const user: SessionUser = {
    id: row.id_usuarios,
    codigo: row.codigo,
    nombres: row.nombres,
    apellidos: row.apellidos,
    correoInstitucional: row.correo_institucional,
    numeroDocumento: row.numero_documento,
    nivelAcademico: row.nivel_academico,
    verificado: row.verificado,
    estado: row.estado as SessionUser['estado'],
    rolId: row.roles_id_roles,
    rolNombre: row.rol_nombre,
    ultimaActividad: new Date(),
  };

  const token = await signSession({ id: user.id, role: user.rolId });

  logger.info({ userId: user.id, rol: user.rolId, ip }, 'Inicio de sesión');

  return {
    token,
    user: {
      id: user.id,
      codigo: user.codigo,
      nombres: user.nombres,
      apellidos: user.apellidos,
      correoInstitucional: user.correoInstitucional,
      numeroDocumento: user.numeroDocumento,
      nivelAcademico: user.nivelAcademico,
      verificado: user.verificado,
      estado: user.estado,
      rol: { id: user.rolId, nombre: user.rolNombre },
      ultimaActividad: user.ultimaActividad?.toISOString() ?? null,
    },
  };
}

/**
 * Solicita el código de recuperación. La respuesta es siempre la misma para no revelar
 * qué correos están registrados; si la cuenta no existe o el cooldown está activo, no se
 * envía nada.
 */
export async function requestPasswordReset(input: ForgotPasswordInput): Promise<void> {
  const correo = normalizeEmail(input.correoInstitucional);

  const { rows } = await query<{ id_usuarios: number }>(
    `SELECT id_usuarios FROM usuarios WHERE correo_institucional = $1 AND fecha_eliminacion IS NULL`,
    [correo],
  );

  const user = rows[0];
  if (!user) return;

  try {
    await assertResendAllowed(correo, 'Recuperación');
  } catch (error) {
    // Cooldown activo: se responde igual y no se reenvía. Cualquier otro fallo sube.
    if (error instanceof AppError && error.code === 'OTP_COOLDOWN') return;
    throw error;
  }

  const plainCode = await withTransaction(async (db) =>
    issueOtp(db, { correo, proposito: 'Recuperación', usuarioId: user.id_usuarios }),
  );

  await sendMail(correo, buildRecoveryMail(plainCode));
}

export async function resetPassword(input: ResetPasswordInput, ip: string | null): Promise<void> {
  const correo = normalizeEmail(input.correoInstitucional);
  const passwordHash = await hashPassword(input.password);

  const result = await withTransaction<OtpResult>(async (db) => {
    const { rows } = await db.query<{ id_usuarios: number }>(
      `SELECT id_usuarios FROM usuarios WHERE correo_institucional = $1 AND fecha_eliminacion IS NULL`,
      [correo],
    );

    const user = rows[0];
    if (!user) {
      return { ok: false, reason: 'OTP_INVALID' };
    }

    const otp = await consumeOtp(db, correo, 'Recuperación', input.codigo);
    if (!otp.ok) return otp;

    await db.query('UPDATE usuarios SET password = $2 WHERE id_usuarios = $1', [
      user.id_usuarios,
      passwordHash,
    ]);

    // Nunca se guarda la contraseña (ni la anterior ni la nueva) en la auditoría.
    await audit(db, {
      accion: AUDIT_ACTIONS.PASSWORD_RESET,
      entidad: 'usuarios',
      entidadId: user.id_usuarios,
      valorNuevo: { password: '[cambiada]' },
      usuarioId: user.id_usuarios,
      ip,
    });

    return { ok: true };
  });

  if (!result.ok) throw otpFailure(result.reason);
}
