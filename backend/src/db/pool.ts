import pg from 'pg';
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
