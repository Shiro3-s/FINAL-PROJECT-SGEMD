import { AsyncLocalStorage } from 'node:async_hooks';
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

type CommitHook = () => void | Promise<void>;

/**
 * Tareas que solo pueden ejecutarse **después** del `COMMIT`.
 *
 * El canal SSE (Etapa 8) no puede anunciar una notificación que todavía podría revertirse:
 * el cliente abriría la bandeja y no la encontraría. `notify()` registra aquí el aviso y
 * `withTransaction` lo publica cuando la transacción ya está confirmada.
 */
const transactionHooks = new AsyncLocalStorage<CommitHook[]>();

export function afterCommit(task: CommitHook): void {
  const hooks = transactionHooks.getStore();

  if (hooks) {
    hooks.push(task);
    return;
  }

  // Fuera de una transacción no hay nada que esperar. Se ejecuta en el siguiente turno
  // para no interrumpir al llamador y un fallo nunca propaga al flujo de negocio.
  void Promise.resolve()
    .then(task)
    .catch((error) => {
      logger.warn({ err: error }, 'Falló una tarea diferida fuera de una transacción');
    });
}

async function runHooks(hooks: CommitHook[]): Promise<void> {
  for (const hook of hooks) {
    try {
      await hook();
    } catch (error) {
      // El efecto de negocio ya está confirmado: un fallo al avisar no lo revierte.
      logger.warn({ err: error }, 'Falló una tarea diferida después del COMMIT');
    }
  }
}

/**
 * Ejecuta `fn` dentro de una transacción y confirma al terminar. Cualquier error hace
 * ROLLBACK: nunca se deja una escritura a medias (auditoría + efecto, topes, etc.).
 *
 * Las tareas registradas con `afterCommit` se ejecutan únicamente si el `COMMIT` tuvo
 * éxito; si la transacción falla se descartan.
 */
export async function withTransaction<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  const hooks: CommitHook[] = [];

  let result: T;
  try {
    await client.query('BEGIN');
    result = await transactionHooks.run(hooks, () => fn(client));
    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK').catch((rollbackError: unknown) => {
      logger.warn({ err: rollbackError }, 'Falló el ROLLBACK de una transacción');
    });
    throw error;
  } finally {
    client.release();
  }

  await runHooks(hooks);
  return result;
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
