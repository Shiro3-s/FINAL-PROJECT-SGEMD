import request from 'supertest';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { app, loginSession, ORIGIN, post } from './api.js';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { clearMailbox, uniqueDocument, uniqueEmail } from './helpers.js';

/** Los 13 catálogos que exigen sesión (todos menos `/type-doc`). */
const PROTECTED = [
  '/api/roles',
  '/api/type-users',
  '/api/uni-centers',
  '/api/type-pop',
  '/api/municipalities',
  '/api/academic-programs',
  '/api/entrep-stage',
  '/api/plan-phase',
  '/api/econo-sector',
  '/api/mode',
  '/api/type-event',
  '/api/date-times',
  '/api/modules',
] as const;

/** Cuenta `Limitado` con contraseña conocida (el alta del admin no la expone). */
async function createLimitedStudent(): Promise<string> {
  const admin = await loginSession('admin.demo@uniminuto.edu.co');
  const correo = uniqueEmail('limitado.catalogos');

  const alta = await admin.post('/api/users').send({
    nombres: 'Limitado',
    apellidos: 'Catálogos',
    numeroDocumento: uniqueDocument(),
    correoInstitucional: correo,
    rolId: 2,
    tipoDocumentoId: 1,
    estado: 'Limitado',
  });
  expect(alta.status).toBe(201);

  const { hashPassword } = await import('../src/utils/password.js');
  await query('UPDATE usuarios SET password = $2 WHERE correo_institucional = $1', [
    correo,
    await hashPassword('Demo1234'),
  ]);

  return correo;
}

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
});

afterAll(async () => {
  await closePool();
});

describe('catálogos · lectura', () => {
  it('GET /type-doc es público: lo necesita el formulario de registro', async () => {
    const response = await request(app).get('/api/type-doc');

    expect(response.status).toBe(200);
    expect(response.body.data.items.map((item: { nombre: string }) => item.nombre)).toEqual([
      'CC',
      'CE',
      'TI',
    ]);
    for (const item of response.body.data.items) {
      expect(typeof item.id).toBe('number');
    }
  });

  it('los demás catálogos exigen sesión', async () => {
    for (const path of PROTECTED) {
      const response = await request(app).get(path);
      expect(response.status, path).toBe(401);
      expect(response.body.error.code).toBe('AUTH_REQUIRED');
    }
  });

  it('con sesión devuelve los 14 catálogos con id y nombre', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    for (const path of PROTECTED) {
      const response = await estudiante.get(path);
      expect(response.status, path).toBe(200);
      expect(Array.isArray(response.body.data.items), path).toBe(true);
      expect(response.body.data.items.length, path).toBeGreaterThan(0);

      for (const item of response.body.data.items) {
        expect(typeof item.id, path).toBe('number');
        expect(typeof item.nombre, path).toBe('string');
        expect(item.nombre.length, path).toBeGreaterThan(0);
      }
    }
  });

  it('municipios añade el departamento y los bloques de agenda sus horas', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    const municipios = await estudiante.get('/api/municipalities');
    expect(municipios.body.data.items[0]).toMatchObject({
      nombre: 'Bogotá D.C.',
      departamento: 'Cundinamarca',
    });

    const agenda = await estudiante.get('/api/date-times');
    expect(agenda.body.data.items[0]).toMatchObject({
      fecha: '2026-11-05',
      horaInicio: '09:00',
      horaFin: '11:00',
      nombre: '2026-11-05 09:00–11:00',
    });
  });

  it('una cuenta Limitado puede leer los catálogos que alimentan su perfil', async () => {
    const limitado = await loginSession(await createLimitedStudent());

    for (const path of [
      '/api/academic-programs',
      '/api/uni-centers',
      '/api/municipalities',
      '/api/type-pop',
      '/api/type-users',
    ]) {
      const response = await limitado.get(path);
      expect(response.status, path).toBe(200);
    }
  });

  it('los catálogos son de solo lectura y las rutas desconocidas dan 404', async () => {
    const estudiante = await loginSession('estudiante.demo1@uniminuto.edu.co');

    const escritura = await estudiante.post('/api/roles').set('Origin', ORIGIN).send({
      nombre: 'Otro',
    });
    expect(escritura.status).toBe(404);

    const inexistente = await estudiante.get('/api/no-existe');
    expect(inexistente.status).toBe(404);
    expect(inexistente.body.error.code).toBe('NOT_FOUND');

    // El endpoint público tampoco acepta escritura.
    const alta = await post('/api/type-doc').send({ nombre: 'Pasaporte' });
    expect(alta.status).toBe(404);
  });
});
