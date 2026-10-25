import { ROLES } from '@sgemd/shared';

/**
 * Ids de `roles`, tal como los siembra `database/seed.sql`.
 *
 * No son un `enum` del diagrama: son filas de catálogo. La definición canónica vive en
 * `shared/src/enums.ts` (la comparten backend, frontend y pruebas); aquí solo se reexporta
 * para que los servicios no importen del paquete compartido por un detalle de estilo.
 */
export { ROLES };
export type RolId = (typeof ROLES)[keyof typeof ROLES];

/** Roles que el administrador puede dar de alta (R33: estudiantes y docentes). */
export const ROLES_CREABLES: readonly RolId[] = [ROLES.ESTUDIANTE, ROLES.DOCENTE];
