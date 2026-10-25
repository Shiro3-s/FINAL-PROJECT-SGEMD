import type { CuentaEstado } from '@sgemd/shared';
import { query } from '../../db/pool.js';
import type { SessionUser } from '../auth/types.js';

/**
 * Lectura de la fila de `usuarios`.
 *
 * Vive en el módulo de usuarios y no en el middleware porque la usan tanto la
 * autenticación (una vez por petición) como los casos de uso de esta etapa. La consulta
 * es la única fuente del rol y del estado: el JWT solo aporta el `id` (§15).
 */
export type UserRow = {
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
  tipo_documentos_id_tipo_documentos: number;
  programa_academico_id_programa_academico: number | null;
  centro_universitarios_id_centro_universitarios: number | null;
  municipios_id_municipios: number | null;
  tipo_poblacion_id_tipo_poblacion: number | null;
  tipo_usuarios_id_tipo_usuarios: number | null;
};

const USER_COLUMNS = `
  u.id_usuarios, u.codigo, u.nombres, u.apellidos, u.correo_institucional,
  u.numero_documento, u.nivel_academico, u.verificado, u.estado,
  u.ultima_actividad, u.roles_id_roles, r.nombre AS rol_nombre,
  u.tipo_documentos_id_tipo_documentos,
  u.programa_academico_id_programa_academico,
  u.centro_universitarios_id_centro_universitarios,
  u.municipios_id_municipios,
  u.tipo_poblacion_id_tipo_poblacion,
  u.tipo_usuarios_id_tipo_usuarios`;

const USER_FROM = `
  FROM usuarios u
  JOIN roles r ON r.id_roles = u.roles_id_roles`;

export const USER_SELECT = `SELECT ${USER_COLUMNS}${USER_FROM}`;

export function mapUser(row: UserRow): SessionUser {
  return {
    id: row.id_usuarios,
    codigo: row.codigo,
    nombres: row.nombres,
    apellidos: row.apellidos,
    correoInstitucional: row.correo_institucional,
    numeroDocumento: row.numero_documento,
    tipoDocumentoId: row.tipo_documentos_id_tipo_documentos,
    nivelAcademico: row.nivel_academico,
    programaAcademicoId: row.programa_academico_id_programa_academico,
    centroUniversitarioId: row.centro_universitarios_id_centro_universitarios,
    municipioId: row.municipios_id_municipios,
    tipoPoblacionId: row.tipo_poblacion_id_tipo_poblacion,
    tipoUsuarioId: row.tipo_usuarios_id_tipo_usuarios,
    verificado: row.verificado,
    estado: row.estado as CuentaEstado,
    rolId: row.roles_id_roles,
    rolNombre: row.rol_nombre,
    ultimaActividad: row.ultima_actividad,
  };
}

/** Usuario vigente (sin baja lógica) por id. `null` si no existe o fue dado de baja. */
export async function findUserById(id: number): Promise<SessionUser | null> {
  const { rows } = await query<UserRow>(
    `${USER_SELECT} WHERE u.id_usuarios = $1 AND u.fecha_eliminacion IS NULL`,
    [id],
  );
  return rows[0] ? mapUser(rows[0]) : null;
}

/**
 * Usuario vigente por correo, con su hash de contraseña.
 *
 * Solo lo usa el inicio de sesión: el hash nunca sale de aquí ni se añade a
 * `SessionUser`.
 */
export async function findUserByEmailWithPassword(
  correo: string,
): Promise<{ user: SessionUser; password: string } | null> {
  const { rows } = await query<UserRow & { password: string }>(
    `SELECT ${USER_COLUMNS}, u.password${USER_FROM}
      WHERE u.correo_institucional = $1 AND u.fecha_eliminacion IS NULL`,
    [correo],
  );

  const row = rows[0];
  if (!row) return null;

  return { user: mapUser(row), password: row.password };
}
