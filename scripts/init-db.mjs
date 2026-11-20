#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { config as loadEnv } from 'dotenv';
import pg from 'pg';

loadEnv({ path: '.env.local' });
loadEnv({ path: '.env' });

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = new Set(process.argv.slice(2));
const withSeed = args.has('--seed');
const allowPooled = args.has('--allow-pooled');

const connectionString = process.env.DATABASE_URL_UNPOOLED || process.env.DATABASE_URL;
if (!connectionString) {
  console.error('Error: define DATABASE_URL_UNPOOLED (directa, sin -pooler) antes de ejecutar.');
  process.exit(1);
}

if (connectionString.includes('-pooler') && !allowPooled) {
  console.error(
    'Error: la URL contiene "-pooler". Usa DATABASE_URL_UNPOOLED (conexión directa de Neon) para aplicar schema.sql y seed.sql.',
  );
  process.exit(1);
}

const client = new pg.Client({ connectionString, connectionTimeoutMillis: 15_000 });
await client.connect();

try {
  const { rows } = await client.query(
    `SELECT COUNT(*)::int AS total
       FROM information_schema.tables
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'`,
  );
  const existing = rows[0]?.total ?? 0;

  if (existing > 0) {
    console.log(`La base de datos ya tiene ${existing} tablas en "public". No se realizaron cambios.`);
    process.exit(0);
  }

  const schemaSql = readFileSync(resolve(root, 'database/schema.sql'), 'utf8');
  await client.query(schemaSql);
  console.log('✓ database/schema.sql aplicado correctamente.');

  if (withSeed) {
    const seedSql = readFileSync(resolve(root, 'database/seed.sql'), 'utf8');
    await client.query(seedSql);
    console.log('✓ database/seed.sql aplicado correctamente.');
  }

  const verify = await client.query(
    `SELECT COUNT(*)::int AS total
       FROM information_schema.tables
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'`,
  );
  console.log(`✓ Verificación final: ${verify.rows[0]?.total ?? 0} tablas en el esquema public (esperadas: 41).`);
} finally {
  await client.end();
}
