import cookieParser from 'cookie-parser';
import express from 'express';
import helmet from 'helmet';
import { errorHandler, notFound } from './middleware/error.js';
import { originCheck } from './middleware/originCheck.js';
import { healthRouter } from './modules/health/routes.js';

/**
 * Aplicación Express. En esta etapa solo expone `GET /api/health`: cero endpoints de
 * negocio hasta que la Etapa 2 cree el esquema.
 */
export function createApp(): express.Express {
  const app = express();

  app.disable('x-powered-by');
  // Detrás de Caddy: rate limits y auditoría ven la IP real del cliente.
  app.set('trust proxy', 1);

  app.use(helmet());
  // Los JSON son pequeños; las evidencias suben por multipart en streaming (nunca por aquí).
  app.use(express.json({ limit: '1mb' }));
  app.use(cookieParser());
  app.use(originCheck);

  app.use('/api', healthRouter);

  app.use(notFound);
  app.use(errorHandler);

  return app;
}
