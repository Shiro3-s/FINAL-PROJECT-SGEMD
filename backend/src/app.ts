import cookieParser from 'cookie-parser';
import express from 'express';
import helmet from 'helmet';
import { errorHandler, notFound } from './middleware/error.js';
import { originCheck } from './middleware/originCheck.js';
import { authRouter } from './modules/auth/routes.js';
import { catalogsRouter } from './modules/catalogs/routes.js';
import { diagnosisRouter } from './modules/diagnosis/routes.js';
import { entrepreneurshipRouter } from './modules/entrepreneurship/routes.js';
import { healthRouter } from './modules/health/routes.js';
import { requestsRouter } from './modules/requests/routes.js';
import { usersRouter } from './modules/users/routes.js';

/**
 * Aplicación Express. Los routers se montan bajo `/api`; cada módulo decide su
 * autenticación y su autorización en el servicio, no en el cliente.
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
  app.use('/api', authRouter);
  app.use('/api', usersRouter);
  app.use('/api', catalogsRouter);
  app.use('/api', entrepreneurshipRouter);
  app.use('/api', requestsRouter);
  app.use('/api', diagnosisRouter);

  app.use(notFound);
  app.use(errorHandler);

  return app;
}
