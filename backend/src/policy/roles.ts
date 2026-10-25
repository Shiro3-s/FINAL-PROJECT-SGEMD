/**
 * Ids de `roles`, tal como los siembra `database/seed.sql`.
 *
 * No son un `enum` del diagrama: son filas de catálogo. Se declaran una sola vez aquí
 * para que ni los servicios ni los routers repitan números mágicos.
 */
export const ROLES = {
  ADMIN: 1,
  ESTUDIANTE: 2,
  DOCENTE: 3,
  AUDITOR: 4,
} as const;

export type RolId = (typeof ROLES)[keyof typeof ROLES];

/** Roles que el administrador puede dar de alta (R33: estudiantes y docentes). */
export const ROLES_CREABLES: readonly RolId[] = [ROLES.ESTUDIANTE, ROLES.DOCENTE];
