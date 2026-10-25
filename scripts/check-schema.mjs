#!/usr/bin/env node
/**
 * Verificador de la Etapa 2 — contrato entre el diagrama de clases y la base de datos.
 *
 * No toca la base de datos: compara archivos. Tres comprobaciones:
 *
 *  1. Cada atributo de las 27 clases de negocio de `docs/diagrama-clases.md` tiene su
 *     columna en `database/schema.sql`, con el mapeo PascalCase -> snake_case.
 *  2. El esquema define exactamente 41 tablas: las 27 de negocio + los 14 catálogos.
 *  3. Cada `CHECK (columna IN (...))` coincide con la constante de `shared/src/enums.ts`
 *     que declara esos valores (fuente única de las cadenas canónicas).
 *
 * Si algo falla, imprime todas las diferencias y sale con código 1.
 * Uso: `npm run check:schema`
 */

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const DIAGRAM = resolve(root, 'docs/diagrama-clases.md');
const SCHEMA = resolve(root, 'database/schema.sql');
const ENUMS = resolve(root, 'shared/src/enums.ts');

/* -------------------------------------------------------------------------------------
 * 1. Diagrama: clases y atributos
 * ----------------------------------------------------------------------------------- */

/** Los 14 catálogos no se dibujan como clases; viven en la tabla Markdown del documento. */
const CATALOGS = [
  'roles',
  'tipodocumentos',
  'programaacademico',
  'centrouniversitarios',
  'municipios',
  'tipopoblacion',
  'tipousuarios',
  'etapaemprendimiento',
  'faseplan',
  'sectoreconomico',
  'modalidad',
  'tipo_evento',
  'fecha_y_horarios',
  'modulos',
];

/**
 * Nombre de clase -> nombre físico de tabla. El diagrama usa nombres lógicos en
 * PascalCase; la tabla es el mismo nombre en snake_case, salvo las excepciones que ya
 * fija el documento (`codigosverificacion` no lleva guion bajo).
 */
const TABLE_BY_CLASS = {
  Usuarios: 'usuarios',
  Emprendimiento: 'emprendimiento',
  Asignaciones: 'asignaciones',
  Seguimientos: 'seguimientos',
  Tareas: 'tareas',
  Asesorias: 'asesorias',
  Actas: 'actas',
  Comentarios: 'comentarios',
  Adjuntos: 'adjuntos',
  AdjuntosTareas: 'adjuntos_tareas',
  AdjuntosSeguimientos: 'adjuntos_seguimientos',
  AdjuntosAsesorias: 'adjuntos_asesorias',
  Diagnosticos: 'diagnosticos',
  PreguntasDiagnostico: 'preguntas_diagnostico',
  RespuestasDiagnostico: 'respuestas_diagnostico',
  Caracterizacion: 'caracterizacion',
  Valoracion: 'valoracion',
  Eventos: 'eventos',
  UsuariosHasEventos: 'usuarios_has_eventos',
  RecomendacionesEvento: 'recomendaciones_evento',
  CodigosVerificacion: 'codigosverificacion',
  Notificaciones: 'notificaciones',
  Habilitaciones: 'habilitaciones',
  Solicitudes: 'solicitudes',
  ConfiguracionPrograma: 'configuracion_programa',
  Respaldos: 'respaldos',
  AuditoriaEventos: 'auditoria_eventos',
};

/**
 * Atributo lógico -> columna física.
 * `NivelAcademico` -> `nivel_academico`; `TamanoLogicoMB` -> `tamano_logico_mb`
 * (la mayúscula tras minúscula abre palabra; una racha de mayúsculas no).
 */
function toSnakeCase(name) {
  return name
    .replace(/([a-z0-9])([A-Z])/g, '$1_$2')
    .replace(/__+/g, '_')
    .toLowerCase();
}

/** Extrae `class X { ... }` de un bloque Mermaid `classDiagram`. */
function parseMermaidClasses(block) {
  const classes = new Map();
  const classRe = /class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([\s\S]*?)\n\s*\}/g;
  let match;

  while ((match = classRe.exec(block))) {
    const [, name, body] = match;
    const attributes = [];

    for (const rawLine of body.split('\n')) {
      const line = rawLine.trim();
      if (!line || line.startsWith('<<')) continue; // estereotipo de referencia
      const attr = /^[-+~#]\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z]+)$/.exec(line);
      if (!attr) {
        throw new Error(`Atributo con formato inesperado en ${name}: "${line}"`);
      }
      attributes.push({ name: attr[1], type: attr[2] });
    }

    // Un bloque posterior puede repetir la clase solo como referencia.
    if (!classes.has(name) || attributes.length > classes.get(name).length) {
      classes.set(name, attributes);
    }
  }

  return classes;
}

function readDiagramClasses() {
  const markdown = readFileSync(DIAGRAM, 'utf8');
  const blocks = [...markdown.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)].map((m) => m[1]);
  const classes = new Map();

  for (const block of blocks) {
    if (!/classDiagram/.test(block)) continue;
    for (const [name, attributes] of parseMermaidClasses(block)) {
      if (attributes.length === 0) continue; // clase de referencia
      classes.set(name, attributes);
    }
  }

  return classes;
}

/* -------------------------------------------------------------------------------------
 * 2. Esquema: tablas y columnas
 * ----------------------------------------------------------------------------------- */

/** Divide el cuerpo de un CREATE TABLE por comas de primer nivel. */
function splitTopLevel(body) {
  const parts = [];
  let depth = 0;
  let inQuote = false;
  let current = '';

  for (let i = 0; i < body.length; i += 1) {
    const char = body[i];

    if (inQuote) {
      current += char;
      if (char === "'") {
        if (body[i + 1] === "'") {
          current += body[i + 1];
          i += 1;
        } else {
          inQuote = false;
        }
      }
      continue;
    }

    if (char === "'") {
      inQuote = true;
      current += char;
      continue;
    }
    if (char === '(') depth += 1;
    if (char === ')') depth -= 1;
    if (char === ',' && depth === 0) {
      parts.push(current);
      current = '';
      continue;
    }
    current += char;
  }

  if (current.trim()) parts.push(current);
  return parts;
}

/** Quita comentarios `-- ...` sin tocar el contenido de las cadenas. */
function stripSqlComments(sql) {
  let output = '';
  let inQuote = false;
  let inLineComment = false;

  for (let i = 0; i < sql.length; i += 1) {
    const char = sql[i];

    if (inLineComment) {
      if (char === '\n') {
        inLineComment = false;
        output += char;
      }
      continue;
    }

    if (inQuote) {
      output += char;
      if (char === "'") {
        if (sql[i + 1] === "'") {
          output += sql[i + 1];
          i += 1;
        } else {
          inQuote = false;
        }
      }
      continue;
    }

    if (char === "'") {
      inQuote = true;
      output += char;
      continue;
    }

    if (char === '-' && sql[i + 1] === '-') {
      inLineComment = true;
      i += 1;
      continue;
    }

    output += char;
  }

  return output;
}

function parseSchemaTables(sql) {
  const tables = new Map();
  const createRe = /CREATE TABLE\s+([a-z_][a-z0-9_]*)\s*\(/gi;
  let match;
  while ((match = createRe.exec(sql))) {
    const table = match[1].toLowerCase();
    const start = createRe.lastIndex;
    let depth = 1;
    let inQuote = false;
    let i = start;

    while (i < sql.length && depth > 0) {
      const char = sql[i];
      if (inQuote) {
        if (char === "'") {
          if (sql[i + 1] === "'") i += 1;
          else inQuote = false;
        }
      } else if (char === "'") {
        inQuote = true;
      } else if (char === '(') {
        depth += 1;
      } else if (char === ')') {
        depth -= 1;
      }
      i += 1;
    }

    const body = sql.slice(start, i - 1);
    const columns = new Map();

    for (const part of splitTopLevel(body)) {
      const definition = part.trim();
      if (!definition) continue;
      if (/^(CONSTRAINT|PRIMARY\s+KEY|UNIQUE|CHECK|FOREIGN\s+KEY|EXCLUDE)\b/i.test(definition)) {
        continue;
      }
      const columnMatch = /^([a-z_][a-z0-9_]*)\b/i.exec(definition);
      if (!columnMatch) {
        throw new Error(`Definición de columna inesperada en ${table}: "${definition}"`);
      }
      columns.set(columnMatch[1].toLowerCase(), definition);
    }

    tables.set(table, columns);
    createRe.lastIndex = i;
  }

  return tables;
}

/* -------------------------------------------------------------------------------------
 * 3. Enums: constantes de shared/src/enums.ts
 * ----------------------------------------------------------------------------------- */

function parseEnumConstants(source) {
  const constants = new Map();
  const constRe = /export const ([A-Z0-9_]+)\s*=\s*\[([\s\S]*?)\]\s*as const;/g;
  let match;

  while ((match = constRe.exec(source))) {
    const [, name, body] = match;
    const values = [...body.matchAll(/'((?:[^'\\]|\\.)*)'/g)].map((m) => m[1]);
    constants.set(name, values);
  }

  return constants;
}

/** Columnas con CHECK enumerado y la constante que debe coincidir. */
const ENUM_COLUMNS = [
  ['usuarios', 'estado', 'CUENTA_ESTADOS'],
  ['usuarios', 'nivel_academico', 'NIVELES_ACADEMICOS'],
  ['emprendimiento', 'estado_aprobacion', 'EMPRENDIMIENTO_ESTADOS'],
  ['asignaciones', 'estado', 'ASIGNACION_ESTADOS'],
  ['seguimientos', 'tipo_seguimiento', 'SEGUIMIENTO_TIPOS'],
  ['seguimientos', 'estado_revision', 'REVISION_ESTADOS'],
  ['tareas', 'prioridad', 'PRIORIDADES'],
  ['tareas', 'estado', 'TAREA_ESTADOS'],
  ['tareas', 'estado_revision', 'REVISION_ESTADOS'],
  ['asesorias', 'estado', 'ASESORIA_ESTADOS'],
  ['actas', 'estado', 'ACTA_ESTADOS'],
  ['diagnosticos', 'estado', 'DIAGNOSTICO_ESTADOS'],
  ['valoracion', 'banda', 'VALORACION_BANDAS'],
  ['eventos', 'estado', 'EVENTO_ESTADOS'],
  ['solicitudes', 'tipo', 'SOLICITUD_TIPOS'],
  ['solicitudes', 'estado', 'SOLICITUD_ESTADOS'],
  ['respaldos', 'tipo', 'RESPALDO_TIPOS'],
  ['respaldos', 'estado', 'RESPALDO_ESTADOS'],
  ['notificaciones', 'tipo', 'NOTIFICACION_TIPOS'],
  ['codigosverificacion', 'proposito', 'CODIGO_PROPOSITOS'],
  ['adjuntos', 'tipo_mime', 'TIPOS_MIME_ADJUNTO'],
  ['configuracion_programa', 'tipo_dato', 'TIPOS_DATO_CONFIGURACION'],
];

function checkValues(definition) {
  const match = /CHECK\s*\(\s*[a-z_][a-z0-9_]*\s+IN\s*\(([^)]*)\)\s*\)/i.exec(definition);
  if (!match) return null;
  return [...match[1].matchAll(/'((?:[^'\\]|\\.)*)'/g)].map((m) => m[1]);
}

/* -------------------------------------------------------------------------------------
 * Ejecución
 * ----------------------------------------------------------------------------------- */

const failures = [];
const fail = (message) => failures.push(message);
const sorted = (values) => [...values].sort((a, b) => a.localeCompare(b, 'es'));

const diagramClasses = readDiagramClasses();
const schemaTables = parseSchemaTables(stripSqlComments(readFileSync(SCHEMA, 'utf8')));
const enumConstants = parseEnumConstants(readFileSync(ENUMS, 'utf8'));

// --- 1. Clases de negocio: 27, cada una con su tabla y todas sus columnas ---------------

const expectedBusinessTables = [];
for (const [className, attributes] of diagramClasses) {
  const table = TABLE_BY_CLASS[className];
  if (!table) {
    fail(`Clase del diagrama sin mapeo a tabla: ${className}`);
    continue;
  }
  expectedBusinessTables.push(table);

  const columns = schemaTables.get(table);
  if (!columns) {
    fail(`Falta la tabla "${table}" (clase ${className})`);
    continue;
  }

  for (const attribute of attributes) {
    const column = toSnakeCase(attribute.name);
    if (!columns.has(column)) {
      fail(`${table}: falta la columna "${column}" (atributo ${className}.${attribute.name})`);
    }
  }

  const expectedColumns = new Set(attributes.map((a) => toSnakeCase(a.name)));
  for (const column of columns.keys()) {
    if (!expectedColumns.has(column)) {
      fail(`${table}: columna "${column}" no existe en la clase ${className}`);
    }
  }
}

const expectedTables = new Set([...expectedBusinessTables, ...CATALOGS]);
for (const table of expectedTables) {
  if (!schemaTables.has(table)) fail(`Falta la tabla esperada "${table}"`);
}
for (const table of schemaTables.keys()) {
  if (!expectedTables.has(table)) fail(`Tabla no declarada en el modelo: "${table}"`);
}

if (expectedBusinessTables.length !== 27) {
  fail(`Se esperaban 27 clases de negocio y se leyeron ${expectedBusinessTables.length}`);
}
if (schemaTables.size !== 41) {
  fail(`Se esperaban 41 tablas y el esquema define ${schemaTables.size}`);
}

// --- 2. Enums: CHECK del esquema == constante de shared/src/enums.ts -------------------

for (const [table, column, constant] of ENUM_COLUMNS) {
  const definition = schemaTables.get(table)?.get(column);
  if (!definition) {
    fail(`No se puede verificar el enum ${table}.${column}: la columna no existe`);
    continue;
  }

  const expected = enumConstants.get(constant);
  if (!expected) {
    fail(`Falta la constante ${constant} en shared/src/enums.ts`);
    continue;
  }

  const actual = checkValues(definition);
  if (!actual) {
    fail(`${table}.${column}: falta el CHECK con la lista de valores`);
    continue;
  }

  const missing = sorted(expected).filter((value) => !actual.includes(value));
  const extra = sorted(actual).filter((value) => !expected.includes(value));

  if (missing.length > 0) {
    fail(`${table}.${column}: el CHECK no incluye ${JSON.stringify(missing)} de ${constant}`);
  }
  if (extra.length > 0) {
    fail(`${table}.${column}: el CHECK tiene valores que ${constant} no declara: ${JSON.stringify(extra)}`);
  }
}

/* -------------------------------------------------------------------------------------
 * Resultado
 * ----------------------------------------------------------------------------------- */

if (failures.length > 0) {
  console.error(`\n✗ Verificación del esquema fallida (${failures.length} problema(s)):\n`);
  for (const message of failures) console.error(`  · ${message}`);
  console.error('');
  process.exit(1);
}

console.log('✓ Verificación del esquema');
console.log(`  · ${expectedBusinessTables.length} clases de negocio con todas sus columnas`);
console.log(`  · ${CATALOGS.length} catálogos`);
console.log(`  · ${schemaTables.size} tablas en total`);
console.log(`  · ${ENUM_COLUMNS.length} listas CHECK coinciden con shared/src/enums.ts`);
