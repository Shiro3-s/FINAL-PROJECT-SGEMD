/**
 * Preparación global de la suite de integración.
 *
 * Recrea la base de pruebas desde `database/schema.sql` + `database/seed.sql` en cada
 * ejecución, para que ningún test dependa de lo que dejó el anterior (§18.1: nunca
 * contra mocks, siempre contra PostgreSQL real). La base vive en el contenedor de
 * `docker-compose.test.yml` (`make test-db`).
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import pg from 'pg';
import { setTestEnv } from './env.js';

export default async function globalSetup(): Promise<void> {
  setTestEnv();

  const root = resolve(process.cwd(), '..');
  const schema = readFileSync(resolve(root, 'database/schema.sql'), 'utf8');
  const seed = readFileSync(resolve(root, 'database/seed.sql'), 'utf8');

  const client = new pg.Client({ connectionString: process.env.DATABASE_URL });

  try {
    await client.connect();
  } catch (error) {
    throw new Error(
      'No se pudo conectar a la base de pruebas. Ejecuta `make test-db` y reintenta.\n' +
        `DATABASE_URL=${process.env.DATABASE_URL}\n${String(error)}`,
    );
  }

  try {
    // Esquema limpio en cada ejecución: el volumen de pruebas es desechable.
    await client.query('DROP SCHEMA IF EXISTS public CASCADE');
    await client.query('CREATE SCHEMA public');
    await client.query(schema);
    await client.query(seed);
  } finally {
    await client.end();
  }
}
