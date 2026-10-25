import type { RequestHandler } from 'express';
import { query } from '../db/pool.js';
import { SESSION_COOKIE, verifySession } from '../modules/auth/session.js';
import type { SessionUser } from '../modules/auth/types.js';
import { AppError } from '../utils/AppError.js';
import { asyncHandler } from '../utils/asyncHandler.js';

type UserRow = {
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
}

const USER_SELECT = `
  SELECT u.id_usuarios, u.codigo, u.nombres, u.apellidos, u.correo_institucional,
         u.numero_documento, u.nivel_academico, u.verificado, u.estado,
         u.ultima_actividad, u.roles_id_roles, r.nombre AS rol_nombre
    FROM usuarios u
    JOIN roles r ON r.id_roles = u.roles_id_roles
`;

export function mapUser(row: UserRow): SessionUser {
  return {
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
    ultimaActividad: row.ultima_actividad,
  };
}

export async function findUserById(id: number): Promise<SessionUser | null> {
  const { rows } = await query<UserRow>(
    `${USER_SELECT} WHERE u.id_usuarios = $1 AND u.fecha_eliminacion IS NULL`,
    [id],
  );
  return rows[0] ? mapUser(rows[0]) : null;
}

/**
 * Autenticación por cookie `sgemd_session`.
 *
 * El JWT solo aporta el `id`; el rol y el estado se leen de la fila **en cada petición**
 * (master §15). Así, desactivar o dar de baja a un usuario surte efecto de inmediato
 * aunque su token siga vigente (T04). Un usuario con baja lógica recibe `401`.
 */
export const requireAuth: RequestHandler = asyncHandler(async (req, _res, next) => {
  const token = req.cookies?.[SESSION_COOKIE];
  if (typeof token !== 'string' || token.length === 0) {
    throw new AppError(401, 'AUTH_REQUIRED', 'Debes iniciar sesión.');
  }

  let claims;
  try {
    claims = await verifySession(token);
  } catch {
    throw new AppError(401, 'AUTH_INVALID', 'La sesión no es válida o expiró. Inicia sesión de nuevo.');
  }

  const user = await findUserById(claims.id);
  if (!user) {
    throw new AppError(401, 'AUTH_INVALID', 'La sesión no es válida o expiró. Inicia sesión de nuevo.');
  }

  req.user = user;
  next();
});

/** Devuelve el usuario ya autenticado o falla: evita `req.user!` repartido por el código. */
export function requireUser(req: { user?: SessionUser }): SessionUser {
  if (!req.user) {
    throw new AppError(401, 'AUTH_REQUIRED', 'Debes iniciar sesión.');
  }
  return req.user;
}
