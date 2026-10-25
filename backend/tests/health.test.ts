import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { createApp } from '../src/app.js';

const app = createApp();

describe('GET /api/health', () => {
  it('responde 200 con la envoltura de la API y sin datos de negocio', async () => {
    const response = await request(app).get('/api/health');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.status).toBe('ok');
    expect(response.body.data.db).toBe('down');
    expect(Object.keys(response.body.data).sort()).toEqual(['db', 'status', 'uptimeSeconds']);
  });
});

describe('originCheck', () => {
  it('rechaza una mutación con Origin ajeno', async () => {
    const response = await request(app)
      .post('/api/health')
      .set('Origin', 'https://evil.example')
      .send({});

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ORIGIN_NOT_ALLOWED');
  });

  it('rechaza una mutación sin Origin (cliente no navegador)', async () => {
    const response = await request(app).post('/api/health').send({});

    expect(response.status).toBe(403);
  });

  it('acepta una mutación del mismo origen', async () => {
    const response = await request(app)
      .post('/api/health')
      .set('Origin', 'https://localhost')
      .send({});

    // El mismo origen pasa el control y llega al 404 de la ruta inexistente.
    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('NOT_FOUND');
  });
});
