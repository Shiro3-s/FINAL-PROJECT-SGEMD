import type { SqlExecutor } from './programSettings.js';
import { ROLES } from '../policy/roles.js';
import { AppError } from '../utils/AppError.js';
import type { SessionUser } from '../modules/auth/types.js';

/**
 * Acceso a un emprendimiento desde los módulos que cuelgan de él (tareas, seguimientos,
 * adjuntos).
 *
 * El módulo de emprendimientos ya tiene su propio `scope()`; este helper existe para que
 * los módulos nuevos no dupliquen la regla ni la dejen más laxa. La regla es la misma:
 *
 * - Admin: cualquiera.
 * - Estudiante: solo el propietario.
 * - Docente: solo si tiene una asignación **activa** al emprendimiento.
 *
 * Fuera de alcance y fila inexistente responden igual (`404`): no se revela si el
 * expediente existe (R25, NFR-002).
 */
export interface EntrepreneurshipRef {
  id: number;
  codigo: string;
  nombre: string;
  estadoAprobacion: string;
  estudianteId: number;
  estudianteNombres: string;
  estudianteApellidos: string;
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El emprendimiento no existe.');
}

export async function findEntrepreneurshipForActor(
  db: SqlExecutor,
  id: number,
  actor: SessionUser,
): Promise<EntrepreneurshipRef> {
  const { rows } = await db.query<{
    id_emprendimiento: number;
    codigo: string;
    nombre: string;
    estado_aprobacion: string;
    estudiante_id: number;
    estudiante_nombres: string;
    estudiante_apellidos: string;
    autorizado: boolean;
  }>(
    `SELECT e.id_emprendimiento, e.codigo, e.nombre, e.estado_aprobacion,
            e.usuarios_id_usuarios AS estudiante_id,
            u.nombres AS estudiante_nombres, u.apellidos AS estudiante_apellidos,
            CASE
              WHEN $2::int = $4::int THEN TRUE
              WHEN $2::int = $5::int THEN e.usuarios_id_usuarios = $3::int
              WHEN $2::int = $6::int THEN EXISTS (
                SELECT 1 FROM asignaciones a
                 WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                   AND a.usuarios_id_mentor = $3::int
                   AND a.estado = 'activa'
              )
              ELSE FALSE
            END AS autorizado
       FROM emprendimiento e
       JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
      WHERE e.id_emprendimiento = $1
        AND e.fecha_eliminacion IS NULL`,
    [id, actor.rolId, actor.id, ROLES.ADMIN, ROLES.ESTUDIANTE, ROLES.DOCENTE],
  );

  const row = rows[0];
  if (!row || !row.autorizado) throw notFound();

  return {
    id: row.id_emprendimiento,
    codigo: row.codigo,
    nombre: row.nombre,
    estadoAprobacion: row.estado_aprobacion,
    estudianteId: row.estudiante_id,
    estudianteNombres: row.estudiante_nombres,
    estudianteApellidos: row.estudiante_apellidos,
  };
}

/**
 * Escritura de un módulo de acompañamiento (tarea o seguimiento).
 *
 * Solo el administrador y el docente con asignación activa; el estudiante recibe `403`
 * (los routers ya lo restringen, esto es defensa en profundidad).
 */
export async function requireMentorAccess(
  db: SqlExecutor,
  id: number,
  actor: SessionUser,
): Promise<EntrepreneurshipRef> {
  if (actor.rolId !== ROLES.ADMIN && actor.rolId !== ROLES.DOCENTE) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para esta acción.');
  }

  return findEntrepreneurshipForActor(db, id, actor);
}
