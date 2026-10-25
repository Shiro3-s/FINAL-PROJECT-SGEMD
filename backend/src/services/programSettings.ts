import type { QueryResult, QueryResultRow } from 'pg';

/**
 * Lector de `configuracion_programa`.
 *
 * Los topes, plazos y banderas del programa viven en la tabla, no en el código (FR-016,
 * R35): un cambio de valor no debe exigir un despliegue. Aquí solo se leen; la escritura
 * llega con el módulo de configuración (Etapa 11).
 */
export interface SqlExecutor {
  query<R extends QueryResultRow = QueryResultRow>(
    text: string,
    params?: unknown[],
  ): Promise<QueryResult<R>>;
}

/** Valor en texto de una clave. `null` si la clave no existe o está vacía. */
export async function settingValue(db: SqlExecutor, clave: string): Promise<string | null> {
  const { rows } = await db.query<{ valor: string | null }>(
    'SELECT valor FROM configuracion_programa WHERE clave = $1',
    [clave],
  );

  const valor = rows[0]?.valor;
  return valor === undefined || valor === null || valor.trim() === '' ? null : valor;
}

/**
 * Valor entero de una clave. Si falta o no es un entero válido se usa `fallback`, para
 * que una configuración corrupta no tumbe la operación de negocio.
 */
export async function settingInt(
  db: SqlExecutor,
  clave: string,
  fallback: number,
): Promise<number> {
  const valor = await settingValue(db, clave);
  const parsed = valor === null ? Number.NaN : Number.parseInt(valor, 10);
  return Number.isInteger(parsed) ? parsed : fallback;
}
