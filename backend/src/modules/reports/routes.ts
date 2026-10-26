import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData, sendDownload } from '../../utils/respond.js';
import { exportQuerySchema, type ExportQuery } from './schemas.js';
import { exportReport, listReports } from './service.js';

/**
 * Reportes del administrador (FR-010, FR-017).
 *
 * El catálogo y la exportación son solo del administrador. El auditor tiene las mismas
 * cifras en `/audit/reports`, con los nombres de personas enmascarados y su propio evento
 * de auditoría.
 */
export const reportsRouter = Router();

const admin = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN)];

reportsRouter.get(
  '/reports',
  ...admin,
  asyncHandler(async (_req, res) => {
    sendData(res, await listReports());
  }),
);

reportsRouter.get(
  '/reports/:id/export',
  ...admin,
  validateQuery(exportQuerySchema),
  asyncHandler(async (req, res) => {
    const options = queryOf<ExportQuery>(res);
    const id = req.params.id;
    const file = await exportReport(
      typeof id === 'string' ? id : '',
      options.format,
      { desde: options.desde, hasta: options.hasta, docenteId: options.docenteId },
      requireUser(req),
      req.ip ?? null,
    );
    sendDownload(res, file);
  }),
);
