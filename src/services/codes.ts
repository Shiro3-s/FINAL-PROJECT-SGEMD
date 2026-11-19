import { randomInt } from 'node:crypto';
import type { PoolClient } from 'pg';
import { ROLES } from '../policy/roles.js';
import { AppError } from '../utils/AppError.js';

/**
 * Generación de los códigos legibles del sistema.
 *
 * El diagrama no declara `usuarios.codigo` como única (P-10), así que la unicidad se
 * garantiza aquí, en la aplicación. Los prefijos salen del prototipo
 * (`admin/usuarios.html`, `admin/emprendimientos.html`): `ADM-###` para coordinación,
 * `DOC-###` para docentes, 6 dígitos para estudiantes y `EMP-###` para emprendimientos.
 */

const PREFIX_BY_ROLE: Readonly<Record<number, string>> = {
  [ROLES.ADMIN]: 'ADM',
  [ROLES.DOCENTE]: 'DOC',
};

/**
 * Siguiente código secuencial de un prefijo (`DOC-001`, `EMP-002`, …).
 *
 * `pg_advisory_xact_lock` serializa las altas del mismo prefijo dentro de la transacción:
 * sin él, dos altas simultáneas leerían el mismo máximo y producirían el mismo código. El
 * lock se libera solo al confirmar o revertir.
 *
 * La tabla y la columna son literales del código, nunca datos de la petición.
 */
async function nextSequential(
  db: PoolClient,
  table: 'usuarios' | 'emprendimiento',
  prefix: string,
  width = 3,
): Promise<string> {
  await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [`${table}:${prefix}`]);

  const { rows } = await db.query<{ codigo: string }>(
    `SELECT codigo FROM ${table} WHERE codigo LIKE $1`,
    [`${prefix}-%`],
  );

  const pattern = new RegExp(`^${prefix}-(\\d+)$`);
  const max = rows.reduce((highest, row) => {
    const match = pattern.exec(row.codigo);
    return match ? Math.max(highest, Number(match[1])) : highest;
  }, 0);

  return `${prefix}-${String(max + 1).padStart(width, '0')}`;
}

/** Código de estudiante de 6 dígitos, único dentro de `usuarios`. */
export async function generateStudentCode(db: PoolClient): Promise<string> {
  for (let attempt = 0; attempt < 25; attempt += 1) {
    const candidate = String(randomInt(0, 1_000_000)).padStart(6, '0');
    const { rows } = await db.query<{ exists: boolean }>(
      'SELECT EXISTS (SELECT 1 FROM usuarios WHERE codigo = $1) AS exists',
      [candidate],
    );
    if (!rows[0]?.exists) return candidate;
  }
  throw new AppError(
    500,
    'CODE_GENERATION_FAILED',
    'No fue posible generar el código de estudiante.',
  );
}

/** Código que corresponde al rol: secuencial con prefijo o aleatorio de 6 dígitos. */
export function userCode(db: PoolClient, rolId: number): Promise<string> {
  const prefix = PREFIX_BY_ROLE[rolId];
  return prefix ? nextSequential(db, 'usuarios', prefix) : generateStudentCode(db);
}

/** Código de emprendimiento `EMP-###` (FR-012). */
export function entrepreneurshipCode(db: PoolClient): Promise<string> {
  return nextSequential(db, 'emprendimiento', 'EMP');
}
