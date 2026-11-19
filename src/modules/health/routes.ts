import { Router } from 'express';
import { pingDatabase } from '../../db/pool.js';
import { asyncHandler } from '../../utils/asyncHandler.js';

export const healthRouter = Router();

/**
 * `GET /api/health` — sin autenticación y sin datos de negocio (master §13.3).
 * `db` refleja si PostgreSQL responde; el proceso sigue en pie aunque la BD caiga.
 */
healthRouter.get(
  '/health',
  asyncHandler(async (_req, res) => {
    const databaseUp = await pingDatabase();
    res.status(200).json({
      success: true,
      data: {
        status: 'ok',
        db: databaseUp ? 'up' : 'down',
        uptimeSeconds: Math.round(process.uptime()),
      },
    });
  }),
);
