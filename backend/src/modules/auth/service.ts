import { query, withTransaction } from '../../db/pool.js';
import { logger } from '../../config/logger.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { ROLES } from '../../policy/roles.js';
import { generateStudentCode } from '../../services/codes.js';
import {
  assertInstitutionalEmail,
  normalizeEmail,
  recoveryMail,
  sendMail,
  verificationMail,
} from '../../services/email.js';
import {
  assertResendAllowed,
  consumeOtp,
  issueOtp,
  otpFailure,
  type OtpResult,
} from '../../services/otpCodes.js';
import { findUserByEmailWithPassword } from '../users/repository.js';
import { AppError } from '../../utils/AppError.js';
import { hashPassword, verifyPassword } from '../../utils/password.js';
import type { PublicUser } from './types.js';
import { toPublicUser } from './types.js';
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
        ROLES.ESTUDIANTE,
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

  await sendMail(correo, verificationMail(created.plainCode));

  return {
    id: created.id,
    codigo: created.codigo,
    nombres: input.nombres,
    apellidos: input.apellidos,
    correoInstitucional: correo,
    numeroDocumento: input.numeroDocumento,
    tipoDocumentoId: input.tipoDocumentoId,
    nivelAcademico: null,
    programaAcademicoId: null,
    centroUniversitarioId: null,
    municipioId: null,
    tipoPoblacionId: null,
    tipoUsuarioId: null,
    verificado: false,
    estado: 'Limitado',
    rol: { id: ROLES.ESTUDIANTE, nombre: 'Estudiante' },
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

  await sendMail(correo, verificationMail(plainCode));
}

export interface LoginResult {
  token: string;
  user: PublicUser;
}

export async function login(input: LoginInput, ip: string | null): Promise<LoginResult> {
  const correo = normalizeEmail(input.correoInstitucional);
  const found = await findUserByEmailWithPassword(correo);

  // Mismo tiempo de respuesta exista o no la cuenta: no se filtra por temporización.
  const passwordOk = await verifyPassword(input.password, found?.password ?? DUMMY_HASH);

  if (!found || !passwordOk) {
    throw new AppError(401, 'INVALID_CREDENTIALS', 'Correo o contraseña incorrectos.');
  }

  const user = found.user;

  if (!user.verificado) {
    throw new AppError(
      403,
      'EMAIL_NOT_VERIFIED',
      'Debes verificar tu correo institucional antes de iniciar sesión.',
    );
  }

  await query('UPDATE usuarios SET ultima_actividad = now() WHERE id_usuarios = $1', [user.id]);

  const token = await signSession({ id: user.id, role: user.rolId });

  logger.info({ userId: user.id, rol: user.rolId, ip }, 'Inicio de sesión');

  return {
    token,
    user: toPublicUser({ ...user, ultimaActividad: new Date() }),
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

  await sendMail(correo, recoveryMail(plainCode));
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
