import { createReadStream, existsSync } from 'node:fs';
import { readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';
import type { Response } from 'express';
import archiver from 'archiver';
import ExcelJS from 'exceljs';
import type { RespaldoEstado, RespaldoTipo } from '@sgemd/shared';
import { env } from '../../config/env.js';
import { pool, query } from '../../db/pool.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import {
  buildManifest,
  hasRsync,
  isInsideBackups,
  megabytes,
  readManifest,
  removeDirectory,
  runDump,
  sha256File,
  snapshotStorage,
  streamSnapshot,
  summarizeManifest,
  treeStats,
  writeManifest,
  type Manifest,
  type ManifestSummary,
} from '../../services/backupFiles.js';
import { settingInt } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import { bogotaMinuteStamp, bogotaReadable } from '../../utils/dates.js';
import type { SessionUser } from '../auth/types.js';

/**
 * Respaldos (FR-018, D22, T24).
 *
 * `Completo` = volcado de la base + instantánea incremental de evidencias. `Parcial` =
 * solo el volcado. El orden es obligatorio: si la instantánea falla, el respaldo entero
 * queda `Fallida` y nunca se usa como base del siguiente. Los tamaños se guardan en MB
 * enteros (redondeo hacia arriba) para que «añadido» nunca muestre 0 cuando hubo bytes.
 */

export interface BackupItem {
  id: number;
  codigo: string;
  tipo: RespaldoTipo;
  fechaHora: string;
  tamanoLogicoMb: number | null;
  tamanoAnadidoMb: number | null;
  estado: RespaldoEstado;
  destino: string | null;
  retencionDias: number | null;
  checksumManifiesto: string | null;
  ejecutadoPor: { id: number; nombres: string; apellidos: string } | null;
  artefactos: { dump: boolean; snapshot: boolean };
}

export interface BackupDetail extends BackupItem {
  manifiesto: ManifestSummary | null;
}

interface BackupRow {
  id_respaldo: number;
  codigo: string;
  tipo: RespaldoTipo;
  fecha_hora: Date;
  tamano_logico_mb: number | null;
  tamano_anadido_mb: number | null;
  estado: RespaldoEstado;
  destino: string | null;
  retencion_dias: number | null;
  checksum_manifiesto: string | null;
  actor_id: number | null;
  actor_nombres: string | null;
  actor_apellidos: string | null;
}

function artifacts(destino: string | null): { dump: boolean; snapshot: boolean } {
  if (destino === null) return { dump: false, snapshot: false };
  return {
    dump: existsSync(join(destino, 'dump.pgdump')),
    snapshot: existsSync(join(destino, 'storage')),
  };
}

function mapBackup(row: BackupRow): BackupItem {
  return {
    id: row.id_respaldo,
    codigo: row.codigo,
    tipo: row.tipo,
    fechaHora: row.fecha_hora.toISOString(),
    tamanoLogicoMb: row.tamano_logico_mb,
    tamanoAnadidoMb: row.tamano_anadido_mb,
    estado: row.estado,
    destino: row.destino,
    retencionDias: row.retencion_dias,
    checksumManifiesto: row.checksum_manifiesto,
    ejecutadoPor:
      row.actor_id === null
        ? null
        : {
            id: row.actor_id,
            nombres: row.actor_nombres ?? '',
            apellidos: row.actor_apellidos ?? '',
          },
    artefactos: artifacts(row.destino),
  };
}

const SELECT_BACKUP = `
  SELECT r.id_respaldo, r.codigo, r.tipo, r.fecha_hora, r.tamano_logico_mb,
         r.tamano_anadido_mb, r.estado, r.destino, r.retencion_dias,
         r.checksum_manifiesto,
         u.id_usuarios AS actor_id, u.nombres AS actor_nombres,
         u.apellidos AS actor_apellidos
    FROM respaldos r
    LEFT JOIN usuarios u ON u.id_usuarios = r.usuarios_id_usuarios`;

export interface ListBackupsQuery {
  page: number;
  pageSize: number;
  estado?: RespaldoEstado;
  tipo?: RespaldoTipo;
  q?: string;
  desde?: string;
  hasta?: string;
}

export async function listBackups(options: ListBackupsQuery): Promise<{
  items: BackupItem[];
  total: number;
  page: number;
  pageSize: number;
}> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where: string[] = [];
  if (options.estado) where.push(`r.estado = ${bind(options.estado)}`);
  if (options.tipo) where.push(`r.tipo = ${bind(options.tipo)}`);
  if (options.desde) where.push(`r.fecha_hora >= ${bind(options.desde)}::date`);
  if (options.hasta) {
    where.push(`r.fecha_hora < (${bind(options.hasta)}::date + INTERVAL '1 day')`);
  }
  if (options.q) where.push(`r.codigo ILIKE ${bind(`%${options.q}%`)}`);

  const whereSql = where.length > 0 ? `WHERE ${where.join(' AND ')}` : '';
  const countParams = [...params];
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM respaldos r ${whereSql}`,
      countParams,
    ),
    query<BackupRow>(
      `${SELECT_BACKUP} ${whereSql}
        ORDER BY r.fecha_hora DESC, r.id_respaldo DESC
        LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapBackup),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

async function loadBackup(id: number): Promise<BackupRow> {
  const { rows } = await query<BackupRow>(`${SELECT_BACKUP} WHERE r.id_respaldo = $1`, [id]);
  const row = rows[0];
  if (!row) throw new AppError(404, 'BACKUP_NOT_FOUND', 'El respaldo no existe.');
  return row;
}

export async function getBackup(id: number): Promise<BackupDetail> {
  const row = await loadBackup(id);
  const manifest = row.destino === null ? null : await readManifest(row.destino);

  return {
    ...mapBackup(row),
    manifiesto: manifest === null ? null : summarizeManifest(manifest),
  };
}

/** Código único `BKP-YYYYMMDD-HHMM`; dos respaldos en el mismo minuto llevan sufijo. */
async function nextCode(base: string): Promise<string> {
  const { rows } = await query<{ codigo: string }>(
    'SELECT codigo FROM respaldos WHERE codigo = $1 OR codigo LIKE $2',
    [base, `${base}-%`],
  );
  const used = new Set(rows.map((row) => row.codigo));

  // El código también es el nombre del directorio: un residuo en disco (una fila borrada
  // a mano, una prueba anterior) no puede reutilizarse o la instantánea se mezclaría con
  // archivos viejos.
  const free = (candidate: string): boolean =>
    !used.has(candidate) && !existsSync(join(env.BACKUPS_DIR, candidate));

  if (free(base)) return base;

  for (let index = 2; index < 100; index += 1) {
    const candidate = `${base}-${index}`;
    if (free(candidate)) return candidate;
  }

  throw new AppError(409, 'BACKUP_CODE_COLLISION', 'No se pudo asignar un código al respaldo.');
}

async function previousSuccessful(excludeCode: string): Promise<{
  codigo: string;
  dir: string;
  manifest: Manifest | null;
} | null> {
  const { rows } = await query<{ codigo: string; destino: string }>(
    `SELECT codigo, destino
       FROM respaldos
      WHERE estado = 'Exitosa'
        AND tipo = 'Completo'
        AND destino IS NOT NULL
        AND codigo <> $1
      ORDER BY fecha_hora DESC, id_respaldo DESC
      LIMIT 20`,
    [excludeCode],
  );

  // Se recorre el historial: una fila `Exitosa` cuyo directorio ya no está (retención
  // manual, disco limpiado) no puede servir de base, pero no debe impedir usar la anterior.
  for (const row of rows) {
    if (!existsSync(join(row.destino, 'storage'))) continue;
    return {
      codigo: row.codigo,
      dir: join(row.destino, 'storage'),
      manifest: await readManifest(row.destino),
    };
  }

  return null;
}

/** Borra solo los respaldos vencidos por su propia retención; nunca el recién creado. */
async function applyRetention(keepId: number): Promise<number> {
  const { rows } = await query<{ id_respaldo: number; destino: string | null }>(
    `SELECT id_respaldo, destino
       FROM respaldos
      WHERE id_respaldo <> $1
        AND retencion_dias IS NOT NULL
        AND fecha_hora < now() - (retencion_dias || ' days')::interval`,
    [keepId],
  );

  for (const row of rows) {
    if (row.destino !== null && isInsideBackups(row.destino)) {
      await removeDirectory(row.destino).catch(() => undefined);
    }
    await query('DELETE FROM respaldos WHERE id_respaldo = $1', [row.id_respaldo]);
  }

  return rows.length;
}

interface CreateBackupOptions {
  tipo: RespaldoTipo;
  actor: SessionUser | null;
  ip: string | null;
}

/**
 * `POST /backups` y el job diario de las 09:00.
 *
 * Un lock de sesión (`pg_try_advisory_lock`) impide dos respaldos simultáneos: dos
 * `rsync` sobre el mismo árbol producirían una instantánea inconsistente. El lock se
 * libera al terminar o al caer la conexión.
 */
export async function createBackup(options: CreateBackupOptions): Promise<BackupDetail> {
  const client = await pool.connect();
  let locked = false;

  try {
    const lock = await client.query<{ ok: boolean }>(
      `SELECT pg_try_advisory_lock(hashtext('respaldos:ejecutar')) AS ok`,
    );
    locked = lock.rows[0]?.ok === true;

    if (!locked) {
      throw new AppError(409, 'BACKUP_IN_PROGRESS', 'Ya hay un respaldo en ejecución.');
    }

    const base = `BKP-${bogotaMinuteStamp()}`;
    const codigo = await nextCode(base);
    const dir = join(env.BACKUPS_DIR, codigo);
    const retention = await settingInt({ query }, 'backup_retention_days', 30);

    let dumpBytes = 0;
    let logicalBytes = 0;
    let addedBytes = 0;
    let checksum: string | null = null;
    let manifest: Manifest | null = null;
    let motor: 'rsync' | 'link' | null = null;

    try {
      dumpBytes = await runDump(join(dir, 'dump.pgdump'));
      logicalBytes = dumpBytes;
      addedBytes = dumpBytes;

      if (options.tipo === 'Completo') {
        const previous = await previousSuccessful(codigo);
        const snapshotDir = join(dir, 'storage');
        const result = await snapshotStorage(snapshotDir, previous?.dir ?? null);
        motor = result.motor;

        manifest = await buildManifest(snapshotDir, previous?.dir ?? null, previous?.manifest ?? null, {
          codigo,
          tipo: options.tipo,
          motor: result.motor,
          base: previous?.codigo ?? null,
        });
        const written = await writeManifest(dir, manifest);
        checksum = written.checksum;

        const stats = await treeStats(snapshotDir, previous?.dir ?? null);
        logicalBytes = dumpBytes + stats.totalBytes;
        addedBytes = dumpBytes + stats.addedBytes;
      }

      const { rows } = await query<{ id_respaldo: number }>(
        `INSERT INTO respaldos
           (codigo, tipo, tamano_logico_mb, tamano_anadido_mb, estado, destino,
            retencion_dias, checksum_manifiesto, usuarios_id_usuarios)
         VALUES ($1, $2, $3, $4, 'Exitosa', $5, $6, $7, $8)
         RETURNING id_respaldo`,
        [
          codigo,
          options.tipo,
          megabytes(logicalBytes),
          megabytes(addedBytes),
          dir,
          retention,
          checksum,
          options.actor?.id ?? null,
        ],
      );

      const id = rows[0]!.id_respaldo;

      await audit(
        { query },
        {
          accion: AUDIT_ACTIONS.CREATE_BACKUP,
          entidad: 'respaldos',
          entidadId: id,
          valorNuevo: {
            codigo,
            tipo: options.tipo,
            motor,
            archivos: manifest?.archivos.length ?? 0,
            tamanoLogicoMb: megabytes(logicalBytes),
            tamanoAnadidoMb: megabytes(addedBytes),
          },
          usuarioId: options.actor?.id ?? null,
          ip: options.ip,
        },
      );

      await applyRetention(id);
      return getBackup(id);
    } catch (error) {
      // El respaldo fallido se conserva como evidencia, pero jamás se usa como base.
      const { rows } = await query<{ id_respaldo: number }>(
        `INSERT INTO respaldos
           (codigo, tipo, tamano_logico_mb, tamano_anadido_mb, estado, destino,
            retencion_dias, checksum_manifiesto, usuarios_id_usuarios)
         VALUES ($1, $2, NULL, NULL, 'Fallida', $3, $4, NULL, $5)
         RETURNING id_respaldo`,
        [codigo, options.tipo, dir, retention, options.actor?.id ?? null],
      );

      await audit(
        { query },
        {
          accion: AUDIT_ACTIONS.CREATE_BACKUP,
          entidad: 'respaldos',
          entidadId: rows[0]?.id_respaldo ?? null,
          valorNuevo: {
            codigo,
            tipo: options.tipo,
            estado: 'Fallida',
            motivo: error instanceof Error ? error.message : String(error),
          },
          usuarioId: options.actor?.id ?? null,
          ip: options.ip,
        },
      ).catch(() => undefined);

      throw error;
    }
  } finally {
    if (locked) {
      await client
        .query(`SELECT pg_advisory_unlock(hashtext('respaldos:ejecutar'))`)
        .catch(() => undefined);
    }
    client.release();
  }
}

export interface VerifyResult {
  id: number;
  codigo: string;
  estado: RespaldoEstado;
  archivos: number;
  corruptos: { ruta: string; motivo: string }[];
  verificadoEn: string;
}

/**
 * `POST /backups/:id/verify`: re-calcula el SHA-256 de cada archivo contra el manifiesto.
 *
 * Si algo no coincide, el respaldo pasa a `Fallida` y deja de ser base de los siguientes.
 * Un respaldo `Fallida` no se «resucita» automáticamente: la verificación informa, pero el
 * estado de creación no se reescribe al alza.
 */
export async function verifyBackup(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<VerifyResult> {
  const row = await loadBackup(id);
  if (row.destino === null) {
    throw new AppError(422, 'BACKUP_MANIFEST_MISSING', 'El respaldo no tiene manifiesto.');
  }

  const manifest = await readManifest(row.destino);
  if (manifest === null) {
    throw new AppError(
      422,
      'BACKUP_MANIFEST_MISSING',
      'El respaldo no tiene manifiesto: un respaldo parcial solo contiene el volcado.',
    );
  }

  const corruptos: { ruta: string; motivo: string }[] = [];

  for (const file of manifest.archivos) {
    const path = join(row.destino, 'storage', file.ruta);
    try {
      const info = await stat(path);
      if (info.size !== file.bytes) {
        corruptos.push({ ruta: file.ruta, motivo: 'El tamaño no coincide con el manifiesto' });
        continue;
      }
      const hash = await sha256File(path);
      if (hash !== file.sha256) {
        corruptos.push({ ruta: file.ruta, motivo: 'El SHA-256 no coincide con el manifiesto' });
      }
    } catch {
      corruptos.push({ ruta: file.ruta, motivo: 'El archivo no está en la instantánea' });
    }
  }

  const estado: RespaldoEstado = corruptos.length === 0 ? 'Exitosa' : 'Fallida';

  if (estado === 'Fallida' && row.estado !== 'Fallida') {
    await query(`UPDATE respaldos SET estado = 'Fallida' WHERE id_respaldo = $1`, [id]);
  }

  await audit(
    { query },
    {
      accion: AUDIT_ACTIONS.VERIFY_BACKUP,
      entidad: 'respaldos',
      entidadId: id,
      valorNuevo: { codigo: row.codigo, estado, archivos: manifest.archivos.length, corruptos: corruptos.length },
      usuarioId: actor.id,
      ip,
    },
  );

  return {
    id,
    codigo: row.codigo,
    estado,
    archivos: manifest.archivos.length,
    corruptos,
    verificadoEn: new Date().toISOString(),
  };
}

/** `GET /backups/:id/download?part=dump|storage`: solo admin, solo respaldos exitosos. */
export async function downloadBackup(
  id: number,
  part: 'dump' | 'storage',
  res: Response,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const row = await loadBackup(id);

  if (row.estado !== 'Exitosa') {
    throw new AppError(
      409,
      'BACKUP_NOT_DOWNLOADABLE',
      'Un respaldo fallido no se puede descargar.',
    );
  }
  if (row.destino === null) {
    throw new AppError(404, 'BACKUP_PART_MISSING', 'El respaldo no tiene archivos.');
  }

  const snapshotDir = join(row.destino, 'storage');
  const dumpFile = join(row.destino, 'dump.pgdump');

  if (part === 'dump' && !existsSync(dumpFile)) {
    throw new AppError(404, 'BACKUP_PART_MISSING', 'El volcado de la base no está disponible.');
  }
  if (part === 'storage' && !existsSync(snapshotDir)) {
    throw new AppError(404, 'BACKUP_PART_MISSING', 'La instantánea de evidencias no está disponible.');
  }

  await audit(
    { query },
    {
      accion: AUDIT_ACTIONS.DOWNLOAD_BACKUP,
      entidad: 'respaldos',
      entidadId: id,
      valorNuevo: { codigo: row.codigo, parte: part },
      usuarioId: actor.id,
      ip,
    },
  );

  if (part === 'storage') {
    await streamSnapshot(snapshotDir, res, `${row.codigo}-storage.tar.gz`);
    return;
  }

  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="${row.codigo}-dump.pgdump"`);
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  await new Promise<void>((resolve, reject) => {
    const stream = createReadStream(dumpFile);
    stream.once('error', reject);
    stream.once('end', resolve);
    stream.pipe(res);
  });
}

interface TableColumn {
  table_name: string;
  column_name: string;
}

/** Lista blanca: los nombres vienen de `information_schema`, nunca del cliente. */
function quoteIdentifier(name: string): string {
  if (!/^[a-zA-Z0-9_]+$/.test(name)) {
    throw new AppError(500, 'EXPORT_TABLE_INVALID', 'Nombre de tabla no válido.');
  }
  return `"${name}"`;
}

function csvCell(value: unknown): string {
  if (value === null || value === undefined) return '';
  const raw =
    value instanceof Date
      ? value.toISOString()
      : typeof value === 'object'
        ? JSON.stringify(value)
        : String(value);
  if (/[",\r\n]/.test(raw)) return `"${raw.replace(/"/g, '""')}"`;
  return raw;
}

function exportValue(value: unknown): string | number | boolean {
  if (value === null || value === undefined) return '';
  if (value instanceof Date) return value.toISOString();
  if (typeof value === 'number' || typeof value === 'boolean') return value;
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

/**
 * `GET /backups/export?format=csv|xlsx` (FR-009, T24): la base completa.
 *
 * XLSX lleva una hoja por tabla. CSV lleva un ZIP con un CSV por tabla, porque un solo CSV
 * no puede representar 41 tablas con columnas distintas; la desviación está en §5.11.
 */
export async function exportDatabase(
  format: 'csv' | 'xlsx',
  actor: SessionUser,
  ip: string | null,
): Promise<{ filename: string; contentType: string; body: Buffer }> {
  const tables = await query<{ table_name: string }>(
    `SELECT table_name
       FROM information_schema.tables
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
      ORDER BY table_name`,
  );
  const columns = await query<TableColumn>(
    `SELECT table_name, column_name
       FROM information_schema.columns
      WHERE table_schema = 'public'
      ORDER BY table_name, ordinal_position`,
  );

  const columnsByTable = new Map<string, string[]>();
  for (const column of columns.rows) {
    const list = columnsByTable.get(column.table_name) ?? [];
    list.push(column.column_name);
    columnsByTable.set(column.table_name, list);
  }

  const names = tables.rows.map((row) => row.table_name).filter((name) => /^[a-zA-Z0-9_]+$/.test(name));
  const stamp = bogotaReadable().replace(/[-: ]/g, '').slice(0, 12);

  if (format === 'csv') {
    const archive = archiver('zip', { zlib: { level: 9 } });
    const chunks: Buffer[] = [];
    archive.on('data', (chunk: Buffer) => chunks.push(chunk));

    const done = new Promise<Buffer>((resolve, reject) => {
      archive.once('end', () => resolve(Buffer.concat(chunks)));
      archive.once('error', reject);
    });

    for (const table of names) {
      const { rows } = await query<Record<string, unknown>>(`SELECT * FROM ${quoteIdentifier(table)}`);
      const headers = columnsByTable.get(table) ?? [];
      const lines = [
        headers.map(csvCell).join(','),
        ...rows.map((row) => headers.map((header) => csvCell(row[header])).join(',')),
      ];
      archive.append(`\uFEFF${lines.join('\r\n')}\r\n`, { name: `${table}.csv` });
    }

    await archive.finalize();
    const body = await done;

    await audit(
      { query },
      {
        accion: AUDIT_ACTIONS.EXPORT_DATABASE,
        entidad: 'respaldos',
        entidadId: null,
        valorNuevo: { formato: 'csv', tablas: names.length, bytes: body.length },
        usuarioId: actor.id,
        ip,
      },
    );

    return {
      filename: `sgemd-base-${stamp}.zip`,
      contentType: 'application/zip',
      body,
    };
  }

  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'SGEMD';
  workbook.created = new Date();

  const used = new Set<string>();
  for (const table of names) {
    const { rows } = await query<Record<string, unknown>>(`SELECT * FROM ${quoteIdentifier(table)}`);
    const headers = columnsByTable.get(table) ?? [];

    let sheetName = table.replace(/[[\]:*?/\\]/g, '_').slice(0, 31);
    let suffix = 2;
    while (used.has(sheetName)) {
      sheetName = `${table.slice(0, 28)}_${suffix}`;
      suffix += 1;
    }
    used.add(sheetName);

    const sheet = workbook.addWorksheet(sheetName);
    sheet.addRow(headers).font = { bold: true };
    for (const row of rows) {
      sheet.addRow(headers.map((header) => exportValue(row[header])));
    }
  }

  const body = Buffer.from(await workbook.xlsx.writeBuffer());

  await audit(
    { query },
    {
      accion: AUDIT_ACTIONS.EXPORT_DATABASE,
      entidad: 'respaldos',
      entidadId: null,
      valorNuevo: { formato: 'xlsx', tablas: names.length, bytes: body.length },
      usuarioId: actor.id,
      ip,
    },
  );

  return {
    filename: `sgemd-base-${stamp}.xlsx`,
    contentType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    body,
  };
}

/** Diagnóstico del panel: motor de instantánea y respaldos en disco. */
export async function backupPanel(): Promise<{
  motor: 'rsync' | 'link';
  retencionDias: number;
  respaldosEnDisco: number;
}> {
  const entries = await readdir(env.BACKUPS_DIR).catch(() => []);
  return {
    motor: hasRsync() ? 'rsync' : 'link',
    retencionDias: await settingInt({ query }, 'backup_retention_days', 30),
    respaldosEnDisco: entries.length,
  };
}
