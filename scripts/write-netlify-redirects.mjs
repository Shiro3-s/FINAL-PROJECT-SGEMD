#!/usr/bin/env node
import { writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const rawOrigin = process.env.BACKEND_ORIGIN?.trim();

if (!rawOrigin) {
  if (process.env.NETLIFY === 'true') {
    console.error(
      'Error: falta la variable de entorno BACKEND_ORIGIN en Netlify (ej. https://sgemd-backend.onrender.com).',
    );
    process.exit(1);
  }
  console.log('BACKEND_ORIGIN no definida (build local): se omite dist/_redirects.');
  process.exit(0);
}

let parsed;
try {
  parsed = new URL(rawOrigin);
} catch {
  console.error(`Error: BACKEND_ORIGIN no es una URL válida: "${rawOrigin}"`);
  process.exit(1);
}

if (parsed.protocol !== 'https:' && parsed.hostname !== 'localhost') {
  console.error(`Error: BACKEND_ORIGIN debe usar HTTPS en producción: "${rawOrigin}"`);
  process.exit(1);
}

const target = `${parsed.origin}/api/:splat`;
const content = `# Generado automáticamente en build de Netlify desde BACKEND_ORIGIN\n/api/*  ${target}  200!\n`;
const outPath = resolve(root, 'dist/_redirects');

writeFileSync(outPath, content, 'utf8');
console.log(`✓ dist/_redirects generado: /api/* -> ${target} (200!)`);
