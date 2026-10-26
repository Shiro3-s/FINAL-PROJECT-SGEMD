import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { hashPassword } from '../src/utils/password.js';
import { adminSession, loginSession, type Session } from './api.js';
import { createEntrepreneurship, createAccount } from './fixtures.js';
import { uniqueDocument, uniqueEmail } from './helpers.js';

/**
 * T38 — auditor (rol 4, P2): solo lectura, datos personales enmascarados y cada consulta
 * registrada (Ley 1581/2012, NFR-007).
 *
 * El auditor no existe en la semilla (no es un rol operativo del MVP), así que se crea por
 * SQL, igual que lo haría la coordinación al habilitar una consulta.
 */

let auditor: Session;
let admin: Session;
let studentId: number;
let emprendimientoId: number;
let document: string;
let correo: string;

async function createAuditor(): Promise<Session> {
  const email = uniqueEmail('auditor');
  const doc = uniqueDocument();

  await query(
    `INSERT INTO usuarios
       (codigo, nombres, apellidos, numero_documento, correo_institucional, password,
        verificado, estado, ultima_actividad,
        roles_id_roles, tipo_documentos_id_tipo_documentos)
     VALUES ($1, 'Auditor', 'De Prueba', $2, $3, $4, TRUE, 'Activo', now(), 4, 1)`,
    [`AUD-${Date.now()}`, doc, email, await hashPassword('Demo1234')],
  );

  return loginSession(email);
}

beforeAll(async () => {
  admin = await adminSession();
  auditor = await createAuditor();

  document = uniqueDocument();
  correo = uniqueEmail('ana');

  const created = await admin.post('/api/users').send({
    nombres: 'Ana Maria',
    apellidos: 'Restrepo Gomez',
    numeroDocumento: document,
    correoInstitucional: correo,
    rolId: 2,
    tipoDocumentoId: 1,
  });
  expect(created.status).toBe(201);
  studentId = created.body.data.id as number;

  emprendimientoId = await createEntrepreneurship(admin, studentId);
});

afterAll(async () => {
  await closePool();
});

describe('GET /audit/dashboard', () => {
  it('devuelve agregados por rol y estado sin datos personales', async () => {
    const response = await auditor.get('/api/audit/dashboard');
    expect(response.status).toBe(200);

    const data = response.body.data as {
      usuarios: { total: number; porRol: Record<string, number>; porEstado: Record<string, number> };
      emprendimientos: { total: number; porEstado: Record<string, number>; conDocente: number };
      asignaciones: { activas: number; inactivas: number };
      tareas: { total: number; porEstado: Record<string, number> };
      asesorias: { total: number; porEstado: Record<string, number> };
      diagnosticos: { total: number };
      actas: { total: number };
      eventos: { total: number; publicados: number };
      auditoria: { eventos: number; ultimo: string | null };
    };

    expect(data.usuarios.total).toBeGreaterThanOrEqual(5);
    expect(data.usuarios.porRol.Auditor).toBeGreaterThanOrEqual(1);
    expect(data.usuarios.porEstado.Activo).toBeGreaterThanOrEqual(1);
    expect(data.emprendimientos.total).toBeGreaterThanOrEqual(1);
    expect(data.asignaciones.activas).toBeGreaterThanOrEqual(0);
    expect(data.eventos.total).toBeGreaterThanOrEqual(0);
    expect(data.auditoria.eventos).toBeGreaterThanOrEqual(0);

    const serialized = JSON.stringify(data);
    expect(serialized).not.toContain('@uniminuto.edu.co');
  });

  it('registra la lectura en la auditoría', async () => {
    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Consulta de auditoría'
          AND usuarios_id_usuarios = $1
          AND valor_nuevo->>'ruta' = '/audit/dashboard'`,
      [auditor.id],
    );
    expect(Number(rows[0]!.total)).toBeGreaterThan(0);
  });

  it('rechaza al administrador (cada rol tiene su módulo)', async () => {
    const response = await admin.get('/api/audit/dashboard');
    expect(response.status).toBe(403);
  });
});

describe('GET /audit/expedientes', () => {
  it('enmascara nombres, documento y correo; conserva cifras y códigos', async () => {
    const { rows: codes } = await query<{ codigo: string }>(
      'SELECT codigo FROM emprendimiento WHERE id_emprendimiento = $1',
      [emprendimientoId],
    );
    const codigo = codes[0]!.codigo;

    const response = await auditor.get(
      `/api/audit/expedientes?pageSize=10&q=${encodeURIComponent(codigo)}`,
    );
    expect(response.status).toBe(200);

    const items = response.body.data.items as {
      id: number;
      codigo: string;
      nombre: string;
      avance: number;
      estudiante: {
        nombres: string;
        apellidos: string;
        documento: string;
        correo: string;
      };
      tareas: { total: number };
    }[];

    const item = items.find((entry) => entry.id === emprendimientoId);
    expect(item).toBeDefined();

    expect(item!.codigo).toMatch(/^EMP-\d{3}$/);
    expect(item!.estudiante.nombres).toBe('Ana M.');
    expect(item!.estudiante.apellidos).toBe('Restrepo G.');
    expect(item!.estudiante.documento).toBe(`${'*'.repeat(document.length - 3)}${document.slice(-3)}`);
    expect(item!.estudiante.correo).toBe(`a***${correo.slice(correo.indexOf('@'))}`);
    expect(typeof item!.tareas.total).toBe('number');

    const serialized = JSON.stringify(item);
    expect(serialized).not.toContain('Ana Maria');
    expect(serialized).not.toContain('Restrepo Gomez');
    expect(serialized).not.toContain(document);
    expect(serialized).not.toContain(correo);
  });

  it('pagina y filtra por estado', async () => {
    const response = await auditor.get('/api/audit/expedientes?estado=Aprobado&pageSize=1');
    expect(response.status).toBe(200);
    expect(response.body.data.pageSize).toBe(1);
    expect(response.body.data.items.length).toBeLessThanOrEqual(1);
    for (const item of response.body.data.items as { estado: string }[]) {
      expect(item.estado).toBe('Aprobado');
    }
  });

  it('registra la lectura con sus filtros', async () => {
    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Consulta de auditoría'
          AND usuarios_id_usuarios = $1
          AND valor_nuevo->>'ruta' = '/audit/expedientes'`,
      [auditor.id],
    );
    expect(Number(rows[0]!.total)).toBeGreaterThan(0);
  });
});

describe('GET /audit/reports', () => {
  it('marca el catálogo como enmascarado', async () => {
    const response = await auditor.get('/api/audit/reports');
    expect(response.status).toBe(200);

    const items = response.body.data.items as { id: string; enmascarado: boolean }[];
    expect(items).toHaveLength(4);
    expect(items.every((item) => item.enmascarado === true)).toBe(true);
  });

  it('exporta con nombres parciales y acción de auditoría propia', async () => {
    const response = await auditor.get('/api/audit/reports/emprendimientos/export?format=csv');
    expect(response.status).toBe(200);

    const text = String(response.text ?? '');
    expect(text).toContain('Ana G.');
    expect(text).not.toContain('Ana Maria');
    expect(text).not.toContain('Restrepo Gomez');

    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Exportación de auditoría'
          AND usuarios_id_usuarios = $1
          AND valor_nuevo->>'reporte' = 'emprendimientos'
          AND (valor_nuevo->>'enmascarado')::boolean = TRUE`,
      [auditor.id],
    );
    expect(Number(rows[0]!.total)).toBeGreaterThan(0);
  });

  it('rechaza el formato ausente', async () => {
    const response = await auditor.get('/api/audit/reports/emprendimientos/export');
    expect(response.status).toBe(400);
  });
});

describe('el auditor no escribe', () => {
  it('no existe ningún POST de auditoría', async () => {
    const response = await auditor.post('/api/audit/expedientes').send({});
    expect(response.status).toBe(404);
  });

  it('el administrador no puede exportar por la ruta del auditor', async () => {
    const response = await admin.get('/api/audit/reports/emprendimientos/export?format=csv');
    expect(response.status).toBe(403);
  });

  it('una cuenta Limitado no entra al módulo', async () => {
    const limited = (await createAccount(admin, 2, 'Limitado')).session;
    const response = await limited.get('/api/audit/dashboard');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });
});
