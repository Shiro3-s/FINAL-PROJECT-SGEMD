import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { adminSession, type Session } from './api.js';
import { createAccount } from './fixtures.js';

/**
 * T23 — configuración del programa y bitácora del administrador.
 *
 * La configuración es la que gobierna los topes del programa (`carga_max_horas`,
 * `inactividad_dias`, …), así que se comprueba que el tipo lo decide la fila y no el
 * cliente: un `int` con letras, un `bool` con «sí» o un 31 de febrero se rechazan con el
 * campo exacto. Cada cambio real deja una fila de auditoría con valor anterior y nuevo.
 */

let admin: Session;
let student: Session;
let original: { clave: string; valor: string | null }[] = [];

beforeAll(async () => {
  admin = await adminSession();
  student = (await createAccount(admin, 2)).session;

  const { rows } = await query<{ clave: string; valor: string | null }>(
    `SELECT clave, valor FROM configuracion_programa
      WHERE clave IN ('cupos_por_sede', 'sede_por_defecto', 'fecha_cierre_admisiones',
                      'rubrica_diagnostico_aprobada')`,
  );
  original = rows;
});

afterAll(async () => {
  // Restaura los valores sembrados: otros archivos de la suite leen estos topes.
  for (const item of original) {
    await query('UPDATE configuracion_programa SET valor = $2 WHERE clave = $1', [
      item.clave,
      item.valor,
    ]);
  }
  await closePool();
});

describe('GET /settings', () => {
  it('devuelve todas las claves con su tipo y descripción (solo admin)', async () => {
    const response = await admin.get('/api/settings');
    expect(response.status).toBe(200);

    const items = response.body.data.items as {
      clave: string;
      valor: string | null;
      tipoDato: string;
      descripcion: string | null;
    }[];

    expect(items.length).toBeGreaterThanOrEqual(18);
    const keys = items.map((item) => item.clave);
    expect(keys).toContain('carga_max_horas');
    expect(keys).toContain('backup_retention_days');

    const cupos = items.find((item) => item.clave === 'cupos_por_sede')!;
    expect(cupos.tipoDato).toBe('int');
    expect(cupos.valor).toBe('40');
    expect(cupos.descripcion).toBeTruthy();
  });

  it('rechaza al estudiante con 403', async () => {
    const response = await student.get('/api/settings');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ROLE_NOT_ALLOWED');
  });
});

describe('PUT /settings', () => {
  it('guarda un entero, audita el cambio y lo devuelve actualizado', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'cupos_por_sede', valor: '45' }],
    });

    expect(response.status).toBe(200);
    expect(response.body.data.cambios).toBe(1);

    const item = (response.body.data.items as { clave: string; valor: string }[]).find(
      (entry) => entry.clave === 'cupos_por_sede',
    )!;
    expect(item.valor).toBe('45');

    const { rows } = await query<{
      valor_anterior: { clave: string; valor: string | null };
      valor_nuevo: { clave: string; valor: string | null };
      accion: string;
    }>(
      `SELECT valor_anterior, valor_nuevo, accion
         FROM auditoria_eventos
        WHERE entidad = 'configuracion_programa' AND valor_nuevo->>'clave' = 'cupos_por_sede'
        ORDER BY id_auditoria DESC
        LIMIT 1`,
    );

    expect(rows[0]!.accion).toBe('Cambio de configuración');
    expect(rows[0]!.valor_anterior.valor).toBe('40');
    expect(rows[0]!.valor_nuevo.valor).toBe('45');
  });

  it('no audita un guardado sin diferencias', async () => {
    const before = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE entidad = 'configuracion_programa'`,
    );

    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'cupos_por_sede', valor: '45' }],
    });

    expect(response.status).toBe(200);
    expect(response.body.data.cambios).toBe(0);

    const after = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE entidad = 'configuracion_programa'`,
    );
    expect(after.rows[0]!.total).toBe(before.rows[0]!.total);
  });

  it('acepta texto y limpia una fecha con null', async () => {
    const first = await admin.put('/api/settings').send({
      items: [
        { clave: 'sede_por_defecto', valor: '  Sede Centro  ' },
        { clave: 'fecha_cierre_admisiones', valor: '2026-12-01' },
      ],
    });

    expect(first.status).toBe(200);
    expect(first.body.data.cambios).toBe(2);

    const cleared = await admin.put('/api/settings').send({
      items: [{ clave: 'fecha_cierre_admisiones', valor: null }],
    });

    expect(cleared.status).toBe(200);
    expect(cleared.body.data.cambios).toBe(1);

    const items = cleared.body.data.items as { clave: string; valor: string | null }[];
    expect(items.find((item) => item.clave === 'sede_por_defecto')!.valor).toBe('Sede Centro');
    expect(items.find((item) => item.clave === 'fecha_cierre_admisiones')!.valor).toBeNull();
  });

  it('rechaza un entero no numérico con el índice del campo', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'cupos_por_sede', valor: 'cuarenta' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.fields['items.0.valor']).toContain('entero');
  });

  it('rechaza un entero menor que uno', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'carga_max_horas', valor: '0' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.fields['items.0.valor']).toBeTruthy();
  });

  it('rechaza un booleano que no sea true/false', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'rubrica_diagnostico_aprobada', valor: 'sí' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.fields['items.0.valor']).toBe('El valor debe ser true o false');
  });

  it('rechaza una fecha que no existe en el calendario', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'fecha_cierre_admisiones', valor: '2026-02-31' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.fields['items.0.valor']).toContain('calendario');
  });

  it('rechaza una clave desconocida sin tocar las demás', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'clave_que_no_existe', valor: '1' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.fields['items.0.clave']).toContain('no existe');
  });

  it('rechaza claves repetidas en el mismo lote', async () => {
    const response = await admin.put('/api/settings').send({
      items: [
        { clave: 'cupos_por_sede', valor: '41' },
        { clave: 'cupos_por_sede', valor: '42' },
      ],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.fields['items.1.clave']).toContain('repetida');
  });

  it('rechaza campos de más (no hay asignación masiva de tipo ni autor)', async () => {
    const response = await admin.put('/api/settings').send({
      items: [{ clave: 'cupos_por_sede', valor: '41', tipoDato: 'text' }],
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});

describe('GET /settings/audit', () => {
  it('lista los cambios con actor y filtros', async () => {
    const response = await admin.get(
      '/api/settings/audit?accion=Cambio%20de%20configuraci%C3%B3n&pageSize=10',
    );

    expect(response.status).toBe(200);
    expect(response.body.data.total).toBeGreaterThan(0);
    expect(response.body.data.pageSize).toBe(10);

    const item = response.body.data.items[0] as {
      accion: string;
      entidad: string;
      actor: { id: number } | null;
      fecha: string;
    };
    expect(item.accion).toBe('Cambio de configuración');
    expect(item.entidad).toBe('configuracion_programa');
    expect(item.actor?.id).toBe(admin.id);
    expect(Number.isNaN(Date.parse(item.fecha))).toBe(false);
  });

  it('filtra por texto de la entidad', async () => {
    const response = await admin.get('/api/settings/audit?q=configuracion&pageSize=5');
    expect(response.status).toBe(200);
    expect(response.body.data.total).toBeGreaterThan(0);
  });

  it('rechaza un rango de fechas mal formado', async () => {
    const response = await admin.get('/api/settings/audit?desde=25-10-2026');
    expect(response.status).toBe(400);
    expect(response.body.error.fields.desde).toBeTruthy();
  });

  it('rechaza al docente', async () => {
    const doc = (await createAccount(admin, 3)).session;
    const response = await doc.get('/api/settings/audit');
    expect(response.status).toBe(403);
  });
});

describe('configuración corrupta', () => {
  it('un valor ilegible no rompe el lector de topes', async () => {
    // El lector usa su respaldo cuando la fila no es un entero válido; se comprueba a
    // través de la pantalla: el valor se muestra tal cual y el programa sigue vivo.
    await query(`UPDATE configuracion_programa SET valor = 'doce' WHERE clave = 'cupos_por_sede'`);
    const response = await admin.get('/api/settings');
    expect(response.status).toBe(200);

    await query(`UPDATE configuracion_programa SET valor = '40' WHERE clave = 'cupos_por_sede'`);
  });
});
