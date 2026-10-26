import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { adminSession, type Session } from './api.js';
import { createAccount, evidenceScenario, type Scenario } from './fixtures.js';

/**
 * T22 — reportes (FR-010, FR-017) y exportadores (D6).
 *
 * El archivo se genera con las mismas filas que devuelve la consulta del reporte: aquí se
 * comprueba que el CSV lleva BOM y cabecera, que XLSX es un ZIP de Excel y que el PDF
 * empieza por `%PDF`; también que un periodo imposible o un `docenteId` que no es docente
 * se rechazan antes de consultar, y que cada exportación queda auditada.
 */

async function download(
  session: Session,
  path: string,
): Promise<{ status: number; contentType: string; disposition: string; body: Buffer }> {
  const response = await session.get(path);

  // `text/csv` llega en `response.text`; PDF/XLSX/ZIP como Buffer en `response.body`
  // (superagent usa el parser genérico para los tipos que no conoce).
  const body = Buffer.isBuffer(response.body)
    ? response.body
    : Buffer.from(typeof response.text === 'string' ? response.text : '', 'utf8');

  return {
    status: response.status,
    contentType: String(response.headers['content-type'] ?? ''),
    disposition: String(response.headers['content-disposition'] ?? ''),
    body,
  };
}

let admin: Session;
let scenario: Scenario;
let student: Session;

beforeAll(async () => {
  admin = await adminSession();
  scenario = await evidenceScenario();
  student = (await createAccount(admin, 2)).session;
});

afterAll(async () => {
  await closePool();
});

describe('GET /reports', () => {
  it('lista los cuatro reportes con formatos y columnas', async () => {
    const response = await admin.get('/api/reports');
    expect(response.status).toBe(200);

    const items = response.body.data.items as {
      id: string;
      nombre: string;
      formatos: string[];
      periodo: boolean;
      columnas: { key: string; header: string }[];
    }[];

    expect(items.map((item) => item.id).sort()).toEqual([
      'asesorias',
      'diagnosticos',
      'emprendimientos',
      'seguimiento',
    ]);

    for (const item of items) {
      expect(item.formatos).toEqual(['csv', 'xlsx', 'pdf']);
      expect(item.columnas.length).toBeGreaterThan(3);
    }

    expect(items.find((item) => item.id === 'emprendimientos')!.periodo).toBe(false);
    expect(items.find((item) => item.id === 'seguimiento')!.periodo).toBe(true);
  });

  it('rechaza al estudiante con 403', async () => {
    const response = await student.get('/api/reports');
    expect(response.status).toBe(403);
  });
});

describe('GET /reports/:id/export', () => {
  it('exporta CSV con BOM y cabecera en español', async () => {
    const file = await download(admin, '/api/reports/emprendimientos/export?format=csv');

    expect(file.status).toBe(200);
    expect(file.contentType).toContain('text/csv');
    expect(file.disposition).toContain('attachment');
    expect(file.disposition).toContain('reporte-emprendimientos-');

    const text = file.body.toString('utf8');
    expect(text.startsWith('\uFEFF')).toBe(true);
    expect(text).toContain('Código,Emprendimiento,Estado,Sector,Etapa,Sede');
    // El emprendimiento del escenario está aprobado y tiene docente asignado.
    expect(text).toContain('Aprobado');
    expect(text).toContain('Docente');
  });

  it('exporta XLSX como libro de Excel', async () => {
    const file = await download(admin, '/api/reports/emprendimientos/export?format=xlsx');

    expect(file.status).toBe(200);
    expect(file.contentType).toContain('spreadsheetml');
    // Firma `PK` de un ZIP (xlsx es un contenedor OOXML).
    expect(file.body.subarray(0, 2).toString('latin1')).toBe('PK');
    expect(file.body.length).toBeGreaterThan(1000);
  });

  it('exporta PDF válido', async () => {
    const file = await download(admin, '/api/reports/seguimiento/export?format=pdf');

    expect(file.status).toBe(200);
    expect(file.contentType).toBe('application/pdf');
    expect(file.body.subarray(0, 5).toString('latin1')).toBe('%PDF-');
  });

  it('aplica el periodo y el docente al reporte de seguimiento', async () => {
    const created = await scenario.mentor.session.post('/api/tracing').send({
      emprendimientoId: scenario.emprendimientoId,
      tipoSeguimiento: 'Avance de fase',
      descripcion: 'Seguimiento del periodo de prueba',
      fasePlanId: 1,
      puntaje: 85,
      estadoRevision: 'Calificada',
    });
    expect(created.status).toBe(201);

    const inside = await download(
      admin,
      `/api/reports/seguimiento/export?format=csv&desde=2026-01-01&hasta=2026-12-31&docenteId=${scenario.mentor.id}`,
    );
    expect(inside.status).toBe(200);
    expect(inside.body.toString('utf8')).toContain('Seguimiento del periodo de prueba');
    expect(inside.body.toString('utf8')).toContain('Calificada');

    const outside = await download(
      admin,
      `/api/reports/seguimiento/export?format=csv&desde=2020-01-01&hasta=2020-12-31&docenteId=${scenario.mentor.id}`,
    );
    expect(outside.status).toBe(200);
    expect(outside.body.toString('utf8')).not.toContain('Seguimiento del periodo de prueba');
  });

  it('exige el formato', async () => {
    const response = await admin.get('/api/reports/emprendimientos/export');
    expect(response.status).toBe(400);
    expect(response.body.error.fields.format).toBeTruthy();
  });

  it('rechaza un formato no soportado', async () => {
    const response = await admin.get('/api/reports/emprendimientos/export?format=docx');
    expect(response.status).toBe(400);
  });

  it('rechaza un reporte inexistente con 404', async () => {
    const response = await admin.get('/api/reports/inventado/export?format=csv');
    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('REPORT_NOT_FOUND');
  });

  it('rechaza periodo en un reporte sin fecha propia', async () => {
    const response = await admin.get(
      '/api/reports/emprendimientos/export?format=csv&desde=2026-01-01',
    );

    expect(response.status).toBe(400);
    expect(response.body.error.fields.desde).toContain('no admite periodo');
  });

  it('rechaza un rango invertido', async () => {
    const response = await admin.get(
      '/api/reports/seguimiento/export?format=csv&desde=2026-12-31&hasta=2026-01-01',
    );

    expect(response.status).toBe(400);
    expect(response.body.error.fields.desde).toContain('posterior');
  });

  it('rechaza un docenteId que no es docente', async () => {
    const response = await admin.get(
      `/api/reports/emprendimientos/export?format=csv&docenteId=${scenario.student.id}`,
    );

    expect(response.status).toBe(400);
    expect(response.body.error.fields.docenteId).toBe('El docente no existe');
  });

  it('audita cada exportación con reporte, formato y filas', async () => {
    await download(admin, '/api/reports/diagnosticos/export?format=csv');

    const { rows } = await query<{
      valor_nuevo: { reporte: string; formato: string; filas: number };
      usuarios_id_usuarios: number;
    }>(
      `SELECT valor_nuevo, usuarios_id_usuarios
         FROM auditoria_eventos
        WHERE accion = 'Exportación de reporte' AND valor_nuevo->>'reporte' = 'diagnosticos'
        ORDER BY id_auditoria DESC
        LIMIT 1`,
    );

    expect(rows[0]!.valor_nuevo.formato).toBe('csv');
    expect(typeof rows[0]!.valor_nuevo.filas).toBe('number');
    expect(rows[0]!.usuarios_id_usuarios).toBe(admin.id);
  });

  it('muestra la fecha de la última exportación en el catálogo', async () => {
    const response = await admin.get('/api/reports');
    const item = (
      response.body.data.items as { id: string; ultimaGeneracion: string | null }[]
    ).find((entry) => entry.id === 'diagnosticos')!;

    expect(item.ultimaGeneracion).not.toBeNull();
    expect(Number.isNaN(Date.parse(item.ultimaGeneracion!))).toBe(false);
  });

  it('rechaza al estudiante', async () => {
    const response = await student.get('/api/reports/emprendimientos/export?format=csv');
    expect(response.status).toBe(403);
  });
});
