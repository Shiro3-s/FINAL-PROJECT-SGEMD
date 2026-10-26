import { mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { env } from '../src/config/env.js';
import { closePool, pool, query } from '../src/db/pool.js';
import { adminSession, type Session } from './api.js';
import { createAccount } from './fixtures.js';

/**
 * T24 — respaldos (FR-018, D22) y exportación de la base (FR-009).
 *
 * La suite usa un doble de `pg_dump` y el copiador con enlaces duros (`tests/env.ts`), así
 * que el contrato completo se ejercita sin depender de binarios del sistema (P-45). Los
 * casos van en orden: el respaldo incremental necesita el anterior.
 */

const STORAGE_CASE = 'backup-test';

interface BackupItem {
  id: number;
  codigo: string;
  tipo: string;
  estado: string;
  fechaHora: string;
  tamanoLogicoMb: number | null;
  tamanoAnadidoMb: number | null;
  checksumManifiesto: string | null;
  destino: string | null;
  artefactos: { dump: boolean; snapshot: boolean };
}

interface BackupDetail extends BackupItem {
  manifiesto: {
    codigo: string;
    tipo: string;
    motor: string;
    base: string | null;
    totalBytes: number;
    archivos: number;
  } | null;
}

interface ManifestOnDisk {
  codigo: string;
  base: string | null;
  motor: string;
  totalBytes: number;
  archivos: { ruta: string; bytes: number; sha256: string }[];
}

let admin: Session;
let student: Session;
let first: BackupDetail;
let second: BackupDetail;
let third: BackupDetail;
let fourth: BackupDetail;
let partial: BackupDetail;
let addedFile: string;
let removedRelPath: string;

function caseFile(name: string): string {
  return join(env.STORAGE_DIR, STORAGE_CASE, name);
}

async function writeStorageFile(name: string, bytes: number, fill = 0x41): Promise<string> {
  const file = caseFile(name);
  await mkdir(join(env.STORAGE_DIR, STORAGE_CASE), { recursive: true });
  await writeFile(file, Buffer.alloc(bytes, fill));
  return file;
}

async function readDiskManifest(destino: string): Promise<ManifestOnDisk> {
  return JSON.parse(await readFile(join(destino, 'manifest.json'), 'utf8')) as ManifestOnDisk;
}

async function createBackup(tipo: 'Completo' | 'Parcial'): Promise<BackupDetail> {
  const response = await admin.post('/api/backups').send({ tipo });
  expect(response.status).toBe(201);
  return response.body.data as BackupDetail;
}

async function exists(path: string): Promise<boolean> {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Descarga binaria. Superagent elige el parser de texto para tipos que no conoce
 * (`application/zip`, xlsx), así que se fuerza un recolector de bytes.
 */
function collectBinary(
  response: NodeJS.ReadableStream,
  callback: (error: Error | null, body: Buffer) => void,
): void {
  const chunks: Buffer[] = [];
  response.on('data', (chunk: Buffer) => chunks.push(chunk));
  response.on('end', () => callback(null, Buffer.concat(chunks)));
}

async function download(session: Session, path: string) {
  return session.get(path).buffer(true).parse(collectBinary);
}

beforeAll(async () => {
  admin = await adminSession();
  student = (await createAccount(admin, 2)).session;

  // Archivos que nunca deben entrar: correo y subidas a medio escribir.
  await mkdir(join(env.STORAGE_DIR, 'mail-test'), { recursive: true });
  await mkdir(join(env.STORAGE_DIR, 'mail'), { recursive: true });
  await writeFile(join(env.STORAGE_DIR, 'mail-test', 'correo.eml'), 'no va al respaldo');
  await writeFile(join(env.STORAGE_DIR, 'mail', 'backup-test.eml'), 'no va al respaldo');

  await writeStorageFile('estable.jpg', 2048);
  await writeStorageFile('subida.part', 5);
});

afterAll(async () => {
  await rm(join(env.STORAGE_DIR, STORAGE_CASE), { recursive: true, force: true });
  await rm(join(env.STORAGE_DIR, 'mail', 'backup-test.eml'), { force: true });
  await closePool();
});

describe('POST /backups — respaldo completo', () => {
  it('produce volcado, instantánea y manifiesto en ese orden', async () => {
    first = await createBackup('Completo');

    expect(first.codigo).toMatch(/^BKP-\d{8}-\d{4}(-\d+)?$/);
    expect(first.tipo).toBe('Completo');
    expect(first.estado).toBe('Exitosa');
    expect(first.tamanoLogicoMb).toBeGreaterThanOrEqual(1);
    expect(first.tamanoAnadidoMb).toBeGreaterThanOrEqual(1);
    expect(first.checksumManifiesto).toMatch(/^[a-f0-9]{64}$/);
    expect(first.artefactos).toEqual({ dump: true, snapshot: true });
    expect(first.manifiesto?.motor).toBe('link');
    expect(first.manifiesto?.base).toBeNull();

    const destino = first.destino!;
    expect(await exists(join(destino, 'dump.pgdump'))).toBe(true);
    expect(await exists(join(destino, 'storage'))).toBe(true);

    const dump = await readFile(join(destino, 'dump.pgdump'), 'latin1');
    expect(dump.startsWith('PGDUMP-STUB')).toBe(true);

    const manifest = await readDiskManifest(destino);
    expect(manifest.codigo).toBe(first.codigo);
    expect(manifest.archivos.length).toBe(first.manifiesto!.archivos);

    const paths = manifest.archivos.map((file) => file.ruta);
    expect(paths).toContain(`${STORAGE_CASE}/estable.jpg`);
    expect(paths.some((path) => path.startsWith('mail-test/'))).toBe(false);
    expect(paths.some((path) => path.startsWith('mail/'))).toBe(false);
    expect(paths.some((path) => path.endsWith('.part'))).toBe(false);
    expect(await exists(join(destino, 'storage', 'mail-test'))).toBe(false);
    expect(await exists(join(destino, 'storage', 'mail'))).toBe(false);
    expect(await exists(join(destino, 'storage', STORAGE_CASE, 'subida.part'))).toBe(false);
  });

  it('audita el alta del respaldo', async () => {
    const { rows } = await query<{ valor_nuevo: { codigo: string; motor: string } }>(
      `SELECT valor_nuevo FROM auditoria_eventos
        WHERE accion = 'Alta de respaldo' AND entidad_id = $1`,
      [first.id],
    );
    expect(rows[0]!.valor_nuevo.codigo).toBe(first.codigo);
    expect(rows[0]!.valor_nuevo.motor).toBe('link');
  });
});

describe('respaldos incrementales con enlaces duros', () => {
  it('solo añade los archivos nuevos y comparte inodo con el anterior', async () => {
    addedFile = await writeStorageFile('nuevo.jpg', 4096, 0x42);

    second = await createBackup('Completo');

    expect(second.manifiesto?.base).toBe(first.codigo);
    expect(second.manifiesto!.totalBytes).toBe(
      first.manifiesto!.totalBytes + (await stat(addedFile)).size,
    );

    // Un archivo sin cambios comparte inodo: no ocupa disco nuevo.
    const before = await stat(join(first.destino!, 'storage', STORAGE_CASE, 'estable.jpg'));
    const after = await stat(join(second.destino!, 'storage', STORAGE_CASE, 'estable.jpg'));
    expect(after.ino).toBe(before.ino);

    // El nuevo sí es un archivo distinto.
    expect(await exists(join(second.destino!, 'storage', STORAGE_CASE, 'nuevo.jpg'))).toBe(true);

    // El tamaño añadido no puede crecer más que el volcado más el archivo nuevo.
    expect(second.tamanoAnadidoMb!).toBeLessThanOrEqual(first.tamanoAnadidoMb! + 1);
    expect(second.tamanoLogicoMb!).toBeGreaterThanOrEqual(second.tamanoAnadidoMb!);
  });

  it('borrar la instantánea anterior deja la nueva legible', async () => {
    await rm(first.destino!, { recursive: true, force: true });

    const content = await readFile(
      join(second.destino!, 'storage', STORAGE_CASE, 'estable.jpg'),
    );
    expect(content.length).toBe(2048);

    // La fila anterior sigue existiendo aunque su directorio ya no esté: el historial es
    // un registro, no una promesa de que el archivo siga en disco.
    const detail = await admin.get(`/api/backups/${first.id}`);
    expect(detail.status).toBe(200);
    expect(detail.body.data.artefactos).toEqual({ dump: false, snapshot: false });
  });

  it('un archivo eliminado desaparece del siguiente respaldo y sigue en los anteriores', async () => {
    removedRelPath = `${STORAGE_CASE}/nuevo.jpg`;
    await rm(addedFile, { force: true });

    third = await createBackup('Completo');

    const thirdManifest = await readDiskManifest(third.destino!);
    expect(thirdManifest.archivos.some((file) => file.ruta === removedRelPath)).toBe(false);
    expect(await exists(join(third.destino!, 'storage', removedRelPath))).toBe(false);

    // El respaldo anterior conserva el archivo: es la copia histórica.
    expect(await exists(join(second.destino!, 'storage', removedRelPath))).toBe(true);
  });
});

describe('verificación de integridad', () => {
  it('re-calcula los hashes y reporta Exitosa', async () => {
    const response = await admin.post(`/api/backups/${third.id}/verify`).send({});
    expect(response.status).toBe(200);

    const result = response.body.data as {
      estado: string;
      archivos: number;
      corruptos: unknown[];
    };
    expect(result.estado).toBe('Exitosa');
    expect(result.archivos).toBe(third.manifiesto!.archivos);
    expect(result.corruptos).toEqual([]);
  });

  it('marca Fallida cuando un archivo no coincide con el manifiesto', async () => {
    const target = join(third.destino!, 'storage', STORAGE_CASE, 'estable.jpg');
    // Se reemplaza la entrada del directorio (no se trunca el inodo compartido) para
    // corromper solo esta instantánea y dejar intactas las anteriores.
    await rm(target, { force: true });
    await writeFile(target, Buffer.alloc(64, 0x5a));

    const response = await admin.post(`/api/backups/${third.id}/verify`).send({});
    expect(response.status).toBe(200);

    const result = response.body.data as {
      estado: string;
      corruptos: { ruta: string; motivo: string }[];
    };
    expect(result.estado).toBe('Fallida');
    expect(result.corruptos).toHaveLength(1);
    expect(result.corruptos[0]!.ruta).toBe(`${STORAGE_CASE}/estable.jpg`);

    const { rows } = await query<{ estado: string }>(
      'SELECT estado FROM respaldos WHERE id_respaldo = $1',
      [third.id],
    );
    expect(rows[0]!.estado).toBe('Fallida');
  });

  it('un respaldo Fallida nunca es la base del siguiente', async () => {
    fourth = await createBackup('Completo');
    expect(fourth.manifiesto?.base).toBe(second.codigo);
  });
});

describe('respaldo parcial', () => {
  it('solo contiene el volcado, sin manifiesto', async () => {
    partial = await createBackup('Parcial');

    expect(partial.tipo).toBe('Parcial');
    expect(partial.estado).toBe('Exitosa');
    expect(partial.checksumManifiesto).toBeNull();
    expect(partial.manifiesto).toBeNull();
    expect(partial.artefactos).toEqual({ dump: true, snapshot: false });
    expect(await exists(join(partial.destino!, 'storage'))).toBe(false);
  });

  it('no se puede verificar ni descargar su instantánea', async () => {
    const verify = await admin.post(`/api/backups/${partial.id}/verify`).send({});
    expect(verify.status).toBe(422);
    expect(verify.body.error.code).toBe('BACKUP_MANIFEST_MISSING');

    const download = await admin.get(`/api/backups/${partial.id}/download?part=storage`);
    expect(download.status).toBe(404);
    expect(download.body.error.code).toBe('BACKUP_PART_MISSING');
  });
});

describe('fallos', () => {
  it('un volcado fallido deja una fila Fallida sin tamaños', async () => {
    process.env.PG_DUMP_STUB_FAIL = '1';

    try {
      const response = await admin.post('/api/backups').send({ tipo: 'Completo' });
      expect(response.status).toBe(500);
      expect(response.body.error.code).toBe('BACKUP_DUMP_FAILED');
    } finally {
      delete process.env.PG_DUMP_STUB_FAIL;
    }

    const { rows } = await query<{ estado: string; tamano_logico_mb: number | null }>(
      `SELECT estado, tamano_logico_mb FROM respaldos
        WHERE estado = 'Fallida' AND checksum_manifiesto IS NULL
        ORDER BY id_respaldo DESC LIMIT 1`,
    );
    expect(rows[0]!.estado).toBe('Fallida');
    expect(rows[0]!.tamano_logico_mb).toBeNull();
  });

  it('no admite dos respaldos simultáneos', async () => {
    const client = await pool.connect();
    try {
      await client.query(`SELECT pg_advisory_lock(hashtext('respaldos:ejecutar'))`);
      const response = await admin.post('/api/backups').send({ tipo: 'Parcial' });
      expect(response.status).toBe(409);
      expect(response.body.error.code).toBe('BACKUP_IN_PROGRESS');
    } finally {
      await client.query(`SELECT pg_advisory_unlock(hashtext('respaldos:ejecutar'))`);
      client.release();
    }
  });

  it('un respaldo Fallida no se descarga', async () => {
    const response = await admin.get(`/api/backups/${third.id}/download?part=dump`);
    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('BACKUP_NOT_DOWNLOADABLE');
  });
});

describe('retención', () => {
  it('borra solo los respaldos vencidos por su propia retención', async () => {
    const code = `BKP-VENCIDO-${Date.now()}`;
    const dir = join(env.BACKUPS_DIR, code);
    await mkdir(dir, { recursive: true });
    await writeFile(join(dir, 'dump.pgdump'), 'viejo');

    const inserted = await query<{ id_respaldo: number }>(
      `INSERT INTO respaldos
         (codigo, tipo, fecha_hora, tamano_logico_mb, tamano_anadido_mb, estado, destino,
          retencion_dias)
       VALUES ($1, 'Parcial', now() - INTERVAL '40 days', 1, 1, 'Exitosa', $2, 1)
       RETURNING id_respaldo`,
      [code, dir],
    );

    const fresh = await createBackup('Parcial');

    const { rows } = await query<{ total: string }>(
      'SELECT COUNT(*)::text AS total FROM respaldos WHERE id_respaldo = $1',
      [inserted.rows[0]!.id_respaldo],
    );
    expect(rows[0]!.total).toBe('0');
    expect(await exists(dir)).toBe(false);

    // El recién creado nunca se borra a sí mismo.
    expect(fresh.id).not.toBe(inserted.rows[0]!.id_respaldo);
    expect(await exists(join(fresh.destino!, 'dump.pgdump'))).toBe(true);
  });
});

describe('descarga y exportación', () => {
  it('descarga el volcado en streaming y lo audita', async () => {
    const response = await download(admin, `/api/backups/${fourth.id}/download?part=dump`);

    expect(response.status).toBe(200);
    expect(String(response.headers['content-type'])).toContain('application/octet-stream');
    expect(String(response.headers['content-disposition'])).toContain('dump.pgdump');
    expect(response.body.subarray(0, 11).toString('latin1')).toBe('PGDUMP-STUB');

    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Descarga de respaldo' AND entidad_id = $1
          AND valor_nuevo->>'parte' = 'dump'`,
      [fourth.id],
    );
    expect(Number(rows[0]!.total)).toBe(1);
  });

  it('descarga la instantánea como tar.gz', async () => {
    const response = await download(admin, `/api/backups/${fourth.id}/download?part=storage`);

    expect(response.status).toBe(200);
    expect(String(response.headers['content-type'])).toBe('application/gzip');
    expect(String(response.headers['content-disposition'])).toContain('-storage.tar.gz');

    const body = response.body;
    expect(body.subarray(0, 2).toString('hex')).toBe('1f8b');
  });

  it('exporta la base a CSV (ZIP de una tabla por archivo) y audita', async () => {
    const response = await download(admin, '/api/backups/export?format=csv');

    expect(response.status).toBe(200);
    expect(String(response.headers['content-type'])).toBe('application/zip');
    expect(response.body.subarray(0, 2).toString('latin1')).toBe('PK');

    const { rows } = await query<{ valor_nuevo: { tablas: number; formato: string } }>(
      `SELECT valor_nuevo FROM auditoria_eventos
        WHERE accion = 'Exportación de base de datos' AND valor_nuevo->>'formato' = 'csv'
        ORDER BY id_auditoria DESC LIMIT 1`,
    );
    expect(rows[0]!.valor_nuevo.tablas).toBeGreaterThanOrEqual(40);
  });

  it('exporta la base a XLSX con una hoja por tabla', async () => {
    const response = await download(admin, '/api/backups/export?format=xlsx');

    expect(response.status).toBe(200);
    expect(String(response.headers['content-type'])).toContain('spreadsheetml');
    expect(response.body.subarray(0, 2).toString('latin1')).toBe('PK');
  });

  it('exige formato de exportación válido', async () => {
    expect((await admin.get('/api/backups/export')).status).toBe(400);
    expect((await admin.get('/api/backups/export?format=pdf')).status).toBe(400);
  });

  it('ninguna de estas rutas es del estudiante', async () => {
    expect((await student.get('/api/backups')).status).toBe(403);
    expect((await student.post('/api/backups').send({ tipo: 'Parcial' })).status).toBe(403);
    expect((await student.get(`/api/backups/${fourth.id}/download?part=dump`)).status).toBe(403);
    expect((await student.get('/api/backups/export?format=csv')).status).toBe(403);
  });
});

describe('panel e historial', () => {
  it('informa el motor y la retención', async () => {
    const response = await admin.get('/api/backups/panel');
    expect(response.status).toBe(200);

    const data = response.body.data as {
      motor: string;
      retencionDias: number;
      respaldosEnDisco: number;
    };
    expect(data.motor).toBe('link');
    expect(data.retencionDias).toBe(30);
    expect(data.respaldosEnDisco).toBeGreaterThanOrEqual(1);
  });

  it('lista con filtros y tamaños lógicos y añadidos', async () => {
    const response = await admin.get('/api/backups?estado=Exitosa&pageSize=5');
    expect(response.status).toBe(200);
    expect(response.body.data.pageSize).toBe(5);
    expect(response.body.data.total).toBeGreaterThanOrEqual(1);

    for (const item of response.body.data.items as BackupItem[]) {
      expect(item.estado).toBe('Exitosa');
      expect(item.tamanoLogicoMb).toBeGreaterThanOrEqual(1);
      expect(item.tamanoAnadidoMb).toBeGreaterThanOrEqual(1);
      expect(item.tamanoAnadidoMb!).toBeLessThanOrEqual(item.tamanoLogicoMb!);
    }

    const byCode = await admin.get(`/api/backups?q=${encodeURIComponent(fourth.codigo)}`);
    expect(byCode.status).toBe(200);
    expect(
      (byCode.body.data.items as BackupItem[]).some((item) => item.codigo === fourth.codigo),
    ).toBe(true);
  });

  it('un id inexistente responde 404', async () => {
    const response = await admin.get('/api/backups/999999');
    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('BACKUP_NOT_FOUND');
  });
});
