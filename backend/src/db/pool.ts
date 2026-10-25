import pg from 'pg';
import type { PoolClient, QueryResult, QueryResultRow } from 'pg';
import { env } from '../config/env.js';
import { logger } from '../config/logger.js';

const { Pool } = pg;

/**
 * Pool único de conexiones. Toda consulta usa marcadores `$1` (nunca interpolación).
 */
export const pool = new Pool({
  connectionString: env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

pool.on('error', (error) => {
  logger.error({ err: error }, 'Error en una conexión inactiva del pool');
});

/** Consulta suelta. Para operaciones que deben ser atómicas, usar `withTransaction`. */
export function query<T extends QueryResultRow>(
  text: string,
  params: readonly unknown[] = [],
): Promise<QueryResult<T>> {
  return pool.query<T>(text, params as unknown[]);
}

/**
 * Ejecuta `fn` dentro de una transacción y confirma al terminar. Cualquier error hace
 * ROLLBACK: nunca se deja una escritura a medias (auditoría + efecto, topes, etc.).
 */
export async function withTransaction<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await fn(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

/** Comprobación de salud de la base de datos (no lanza). */
export async function pingDatabase(): Promise<boolean> {
  try {
    await pool.query('SELECT 1');
    return true;
  } catch (error) {
    logger.warn({ err: error }, 'La base de datos no responde al healthcheck');
    return false;
  }
}

export async function closePool(): Promise<void> {
  await pool.end();
}
