import type { Response } from 'express';
import { logger } from '../../config/logger.js';
import type { NotificationChannel, NotificationEvent } from './types.js';

/**
 * Canal SSE (`text/event-stream`) sobre la instancia única del backend.
 *
 * Caddy ya está configurado con `flush_interval -1` para `/api/*` (D2), así que los
 * eventos llegan sin buffering. Cada usuario tiene su propio conjunto de conexiones: un
 * evento de A nunca se escribe en la conexión de B.
 *
 * Los latidos (`: keep-alive`) mantienen viva la conexión a través del proxy y permiten
 * detectar clientes muertos sin enviar datos de negocio.
 */

const HEARTBEAT_MS = 25_000;

interface Client {
  res: Response;
  heartbeat: NodeJS.Timeout;
}

const clients = new Map<number, Set<Client>>();

function frame(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
}

function write(client: Client, chunk: string): boolean {
  try {
    client.res.write(chunk);
    return true;
  } catch (error) {
    logger.debug({ err: error }, 'Se descartó una conexión SSE que ya no escribe');
    return false;
  }
}

function closeClient(usuarioId: number, client: Client): void {
  clearInterval(client.heartbeat);

  const set = clients.get(usuarioId);
  if (!set) return;

  set.delete(client);
  if (set.size === 0) clients.delete(usuarioId);
}

export const sseNotificationChannel: NotificationChannel = {
  subscribe(usuarioId, res, unreadCount) {
    res.status(200);
    res.setHeader('Content-Type', 'text/event-stream; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-transform');
    res.setHeader('Connection', 'keep-alive');
    // Nginx y algunos proxies bufferizan SSE salvo que se les diga lo contrario.
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders();

    const heartbeat = setInterval(() => {
      write(client, ': keep-alive\n\n');
    }, HEARTBEAT_MS);
    // Un latido no debe impedir que el proceso termine (tests, apagado ordenado).
    heartbeat.unref();

    const client: Client = { res, heartbeat };

    let set = clients.get(usuarioId);
    if (!set) {
      set = new Set();
      clients.set(usuarioId, set);
    }
    set.add(client);

    // El cliente conoce el contador al abrir el flujo sin tener que consultar la API.
    write(client, frame('ready', { unreadCount }));

    const close = (): void => closeClient(usuarioId, client);
    res.on('close', close);
    res.on('error', close);

    return close;
  },

  publish(usuarioId, event: NotificationEvent) {
    const set = clients.get(usuarioId);
    if (!set) return;

    const chunk = frame('notification', event);

    for (const client of [...set]) {
      if (!write(client, chunk)) closeClient(usuarioId, client);
    }
  },
};
