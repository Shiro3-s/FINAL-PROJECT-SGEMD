import { createApp } from './app.js';
import { env } from './config/env.js';
import { logger } from './config/logger.js';
import { closePool } from './db/pool.js';
import { startScheduler, stopScheduler } from './jobs/scheduler.js';

const app = createApp();

const server = app.listen(env.PORT, () => {
  logger.info({ port: env.PORT, env: env.NODE_ENV }, 'Backend SGEMD escuchando');
});

// Los jobs solo existen en un proceso real: en la suite cada prueba dispara su job a mano
// para no depender del reloj.
if (env.NODE_ENV !== 'test') startScheduler();

async function shutdown(signal: string): Promise<void> {
  logger.info({ signal }, 'Cerrando el servidor');
  stopScheduler();
  server.close(async (error) => {
    if (error) {
      logger.error({ err: error }, 'Error al cerrar el servidor HTTP');
      process.exitCode = 1;
    }
    await closePool();
    process.exit();
  });
}

process.on('SIGTERM', () => void shutdown('SIGTERM'));
process.on('SIGINT', () => void shutdown('SIGINT'));
