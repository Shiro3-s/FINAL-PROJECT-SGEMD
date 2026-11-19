import { request as httpRequest } from 'node:http';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { once } from 'node:events';
import request from 'supertest';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { app, loginSession, type Session } from './api.js';
import { createAccount, evidenceScenario } from './fixtures.js';

/**
 * T21 — bandeja de notificaciones y canal en tiempo real (FR-019).
 *
 * El caso central del canal es de aislamiento: un evento creado para A llega a la conexión
 * abierta de A y **nunca** a la de B. Para probarlo de verdad hace falta un servidor HTTP
 * real (`app.listen(0)`), porque supertest no expone un flujo que quede abierto.
 *
 * El evento `notification` no lleva el cuerpo del aviso: solo el id, el tipo y el contador
 * de no leídas. El cliente invalida su bandeja y pide el texto por la API normal.
 */

beforeEach(async () => {
  resetRateLimits();
});

afterAll(async () => {
  await closePool();
});

/* =====================================================================================
 * Utilidades de notificaciones
 * =================================================================================== */

let sequence = 0;

/** Inserta un aviso con fecha controlada para poder ordenar y filtrar sin ambigüedad. */
async function seedNotification(
  usuarioId: number,
  options: {
    tipo?: string;
    leida?: boolean;
    fecha?: string;
    mensaje?: string;
  } = {},
): Promise<number> {
  sequence += 1;

  const { rows } = await query<{ id: number }>(
    `INSERT INTO notificaciones
       (tipo, mensaje, url, tipo_objeto, objeto_id, leida, fecha, usuarios_id_usuarios)
     VALUES ($1, $2, NULL, NULL, NULL, $3, COALESCE($4::timestamptz, now()), $5)
     RETURNING id_notificaciones AS id`,
    [
      options.tipo ?? 'Sistema',
      options.mensaje ?? `Aviso de prueba ${sequence}`,
      options.leida ?? false,
      options.fecha ?? null,
      usuarioId,
    ],
  );

  return rows[0]!.id;
}

/* =====================================================================================
 * T21 — bandeja
 * =================================================================================== */

describe('T21 · bandeja de notificaciones', () => {
  it('solo devuelve las propias, con paginación, filtros y contador exacto', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const owner = await createAccount(admin, 2);
    const other = await createAccount(admin, 2);

    const tarea = await seedNotification(owner.id, {
      tipo: 'Tarea',
      fecha: '2026-01-01T10:00:00Z',
    });
    const sistema = await seedNotification(owner.id, {
      tipo: 'Sistema',
      fecha: '2026-01-02T10:00:00Z',
    });
    const asesoria = await seedNotification(owner.id, {
      tipo: 'Asesoría',
      leida: true,
      fecha: '2026-01-03T10:00:00Z',
    });
    const ajena = await seedNotification(other.id, { tipo: 'Tarea' });

    const page = await owner.session.get('/api/notifications');
    expect(page.status).toBe(200);
    expect(page.body.data).toMatchObject({
      total: 3,
      page: 1,
      pageSize: 25,
      sinLeer: 2,
    });
    // La más reciente primero.
    expect(page.body.data.items.map((item: { id: number }) => item.id)).toEqual([
      asesoria,
      sistema,
      tarea,
    ]);
    expect(
      page.body.data.items.some((item: { id: number }) => item.id === ajena),
    ).toBe(false);

    const noLeidas = await owner.session.get('/api/notifications').query({ leida: 'false' });
    expect(noLeidas.status).toBe(200);
    expect(noLeidas.body.data.items.map((item: { id: number }) => item.id)).toEqual([
      sistema,
      tarea,
    ]);
    // `sinLeer` cuenta las no leídas del tipo filtrado, no las del listado.
    expect(noLeidas.body.data.sinLeer).toBe(2);

    const leidas = await owner.session.get('/api/notifications').query({ leida: 'true' });
    expect(leidas.body.data.items.map((item: { id: number }) => item.id)).toEqual([
      asesoria,
    ]);
    expect(leidas.body.data.sinLeer).toBe(2);

    const soloTareas = await owner.session.get('/api/notifications').query({ tipo: 'Tarea' });
    expect(soloTareas.body.data.items.map((item: { id: number }) => item.id)).toEqual([tarea]);
    expect(soloTareas.body.data.sinLeer).toBe(1);

    const paginado = await owner.session
      .get('/api/notifications')
      .query({ page: 2, pageSize: 2 });
    expect(paginado.body.data.items.map((item: { id: number }) => item.id)).toEqual([tarea]);
    expect(paginado.body.data.total).toBe(3);
  });

  it('rechaza parámetros fuera del contrato (incluido un orden arbitrario)', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const owner = await createAccount(admin, 2);

    for (const queryString of [
      { pageSize: 101 },
      { tipo: 'No existe' },
      { leida: 'quizá' },
      { orderBy: 'mensaje' },
    ]) {
      const response = await owner.session.get('/api/notifications').query(queryString);
      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    }
  });

  it('marca una como leída de forma idempotente y la ajena responde 404', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const owner = await createAccount(admin, 2);
    const other = await createAccount(admin, 2);

    const primera = await seedNotification(owner.id, { tipo: 'Tarea' });
    await seedNotification(owner.id, { tipo: 'Sistema' });

    const marcada = await owner.session.put(`/api/notifications/${primera}/read`);
    expect(marcada.status).toBe(200);
    expect(marcada.body.data).toMatchObject({ id: primera, leida: true, sinLeer: 1 });

    const repetida = await owner.session.put(`/api/notifications/${primera}/read`);
    expect(repetida.status).toBe(200);
    expect(repetida.body.data).toMatchObject({ id: primera, leida: true, sinLeer: 1 });

    const ajena = await other.session.put(`/api/notifications/${primera}/read`);
    expect(ajena.status).toBe(404);
    expect(ajena.body.error.code).toBe('NOT_FOUND');

    const todas = await owner.session.put('/api/notifications/read-all');
    expect(todas.status).toBe(200);
    expect(todas.body.data).toEqual({ actualizadas: 1, sinLeer: 0 });

    const otraVez = await owner.session.put('/api/notifications/read-all');
    expect(otraVez.body.data).toEqual({ actualizadas: 0, sinLeer: 0 });
  });

  it('exige sesión para la bandeja y el flujo', async () => {
    const bandeja = await request(app).get('/api/notifications');
    expect(bandeja.status).toBe(401);

    const flujo = await request(app).get('/api/notifications/stream');
    expect(flujo.status).toBe(401);
  });

  it('una cuenta Limitado sí puede leer y marcar sus avisos (AQ-07 opción A)', async () => {
    // La cuenta sembrada `estudiante.demo2` está en `Limitado`.
    const limited = await loginSession('estudiante.demo2@uniminuto.edu.co');
    const aviso = await seedNotification(limited.id, {
      tipo: 'Solicitud',
      mensaje: 'Tu solicitud de desbloqueo fue aprobada',
    });

    const bandeja = await limited.get('/api/notifications');
    expect(bandeja.status).toBe(200);
    expect(
      bandeja.body.data.items.some((item: { id: number }) => item.id === aviso),
    ).toBe(true);

    const marcada = await limited.put(`/api/notifications/${aviso}/read`);
    expect(marcada.status).toBe(200);
    expect(marcada.body.data.leida).toBe(true);

    // Un módulo de trabajo sigue cerrado para esa misma cuenta.
    const asesorias = await limited.get('/api/advice');
    expect(asesorias.status).toBe(403);
    expect(asesorias.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });
});

/* =====================================================================================
 * T21 — canal en tiempo real (SSE)
 * =================================================================================== */

interface Frame {
  event: string;
  data: Record<string, unknown>;
}

interface Waiter {
  event: string;
  resolve: (frame: Frame) => void;
  timer: NodeJS.Timeout;
}

interface SseStream {
  frames: Frame[];
  waitFor(event: string, timeoutMs?: number): Promise<Frame>;
  expectNone(event: string, windowMs?: number): Promise<void>;
  close(): void;
}

/** Convierte un bloque SSE (`event: …\ndata: …`) en un frame; los latidos se ignoran. */
function parseFrame(raw: string): Frame | null {
  let event = 'message';
  const data: string[] = [];

  for (const line of raw.split('\n')) {
    if (line.startsWith(':') || line.trim() === '') continue;
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) data.push(line.slice(5).trim());
  }

  if (data.length === 0) return null;
  return { event, data: JSON.parse(data.join('\n')) as Record<string, unknown> };
}

function openStream(port: number, session: Session): Promise<SseStream> {
  return new Promise((resolve, reject) => {
    const frames: Frame[] = [];
    const waiters: Waiter[] = [];
    let buffer = '';

    const req = httpRequest(
      {
        host: '127.0.0.1',
        port,
        path: '/api/notifications/stream',
        method: 'GET',
        headers: { Cookie: session.cookie, Accept: 'text/event-stream' },
      },
      (res) => {
        if (res.statusCode !== 200) {
          res.resume();
          reject(new Error(`El flujo SSE respondió ${res.statusCode}`));
          return;
        }

        res.setEncoding('utf8');
        res.on('data', (chunk: string) => {
          buffer += chunk;

          for (;;) {
            const index = buffer.indexOf('\n\n');
            if (index === -1) break;

            const frame = parseFrame(buffer.slice(0, index));
            buffer = buffer.slice(index + 2);
            if (!frame) continue;

            frames.push(frame);

            const waiter = waiters.find((item) => item.event === frame.event);
            if (waiter) {
              clearTimeout(waiter.timer);
              waiters.splice(waiters.indexOf(waiter), 1);
              waiter.resolve(frame);
            }
          }
        });

        resolve({
          frames,
          waitFor(event, timeoutMs = 5_000) {
            const received = frames.find((frame) => frame.event === event);
            if (received) return Promise.resolve(received);

            return new Promise<Frame>((resolveFrame, rejectFrame) => {
              const timer = setTimeout(() => {
                const index = waiters.findIndex((item) => item.timer === timer);
                if (index >= 0) waiters.splice(index, 1);
                rejectFrame(new Error(`No llegó el evento «${event}» en ${timeoutMs} ms`));
              }, timeoutMs);

              waiters.push({ event, resolve: resolveFrame, timer });
            });
          },
          async expectNone(event, windowMs = 500) {
            await new Promise((resolveDelay) => setTimeout(resolveDelay, windowMs));
            const received = frames.find((frame) => frame.event === event);
            if (received) {
              throw new Error(
                `Llegó el evento «${event}» y no debía: ${JSON.stringify(received)}`,
              );
            }
          },
          close() {
            req.destroy();
          },
        });
      },
    );

    // Al cerrar el flujo, `destroy()` emite un error esperado que no debe propagarse.
    req.on('error', (error) => {
      if (!req.destroyed) reject(error);
    });
    req.end();
  });
}

describe('T21 · canal en tiempo real', () => {
  let server: Server;
  let port: number;
  const streams: SseStream[] = [];

  beforeAll(async () => {
    server = app.listen(0);
    await once(server, 'listening');
    port = (server.address() as AddressInfo).port;
  });

  afterEach(() => {
    for (const stream of streams.splice(0)) stream.close();
  });

  afterAll(async () => {
    await new Promise<void>((resolve) => {
      server.close(() => resolve());
      server.closeAllConnections();
    });
  });

  it('entrega el aviso a su dueño y nunca a otra conexión', async () => {
    const scenario = await evidenceScenario();

    // El escenario ya generó avisos (aprobación, asignación): se parte de cero.
    await scenario.student.session.put('/api/notifications/read-all').expect(200);
    await scenario.otherStudent.session.put('/api/notifications/read-all').expect(200);

    const owner = await openStream(port, scenario.student.session);
    streams.push(owner);
    const stranger = await openStream(port, scenario.otherStudent.session);
    streams.push(stranger);

    expect((await owner.waitFor('ready')).data).toEqual({ unreadCount: 0 });
    expect((await stranger.waitFor('ready')).data).toEqual({ unreadCount: 0 });

    // Una asesoría real dispara `notify()` para el estudiante dueño.
    const alta = await scenario.admin.post('/api/advice').send({
      emprendimientoId: scenario.emprendimientoId,
      docenteId: scenario.mentor.id,
      tema: 'Asesoría en vivo',
    });
    expect(alta.status).toBe(201);

    const event = await owner.waitFor('notification');

    // El evento es mínimo: identificador, tipo y contador. Nunca el cuerpo del aviso.
    expect(event.data).toEqual({
      notificationId: expect.any(Number),
      tipo: 'Asesoría',
      unreadCount: 1,
    });
    expect(event.data).not.toHaveProperty('mensaje');
    expect(event.data).not.toHaveProperty('message');
    expect(event.data).not.toHaveProperty('url');

    const { rows } = await query<{ tipo: string; mensaje: string }>(
      'SELECT tipo, mensaje FROM notificaciones WHERE id_notificaciones = $1',
      [event.data.notificationId],
    );
    expect(rows[0]!.tipo).toBe('Asesoría');
    expect(rows[0]!.mensaje).toContain('Asesoría en vivo');

    // La otra conexión no recibe nada, y su bandeja sigue vacía.
    await stranger.expectNone('notification');
    const ajena = await scenario.otherStudent.session.get('/api/notifications');
    expect(ajena.body.data.total).toBe(0);

    // El contador de la bandeja coincide con el que anunció el evento.
    const propia = await scenario.student.session.get('/api/notifications');
    expect(propia.body.data.sinLeer).toBe(1);

    // Una conexión nueva recibe el contador actualizado al abrirse.
    const reabierta = await openStream(port, scenario.student.session);
    streams.push(reabierta);
    expect((await reabierta.waitFor('ready')).data).toEqual({ unreadCount: 1 });
  });

  it('marca como leída desde la API y el contador del flujo baja al reconectar', async () => {
    const admin = await loginSession('admin.demo@uniminuto.edu.co');
    const owner = await createAccount(admin, 2);
    const aviso = await seedNotification(owner.id, { tipo: 'Sistema' });

    const first = await openStream(port, owner.session);
    streams.push(first);
    expect((await first.waitFor('ready')).data).toEqual({ unreadCount: 1 });

    await owner.session.put(`/api/notifications/${aviso}/read`).expect(200);

    const second = await openStream(port, owner.session);
    streams.push(second);
    expect((await second.waitFor('ready')).data).toEqual({ unreadCount: 0 });
  });
});
