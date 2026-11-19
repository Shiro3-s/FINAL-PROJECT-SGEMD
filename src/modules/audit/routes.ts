import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData, sendDownload } from '../../utils/respond.js';
import { exportQuerySchema, type ExportQuery } from '../reports/schemas.js';
import {
  auditExpedientesQuerySchema,
  type AuditExpedientesQuery,
} from './schemas.js';
import {
  assertReportId,
  auditDashboard,
  auditExpedientes,
  auditExport,
  auditReports,
  logAuditRead,
} from './service.js';

/**
 * Auditor (rol 4, P2): **solo** cuatro `GET`.
 *
 * No hay escritura: ni `POST`, ni `PUT`, ni `PATCH`, ni `DELETE`. Cada lectura y cada
 * exportación se audita, y los datos personales salen enmascarados (NFR-007, T38).
 */
export const auditRouter = Router();

const auditor = [requireAuth, requireActiveAccount, requireRole(ROLES.AUDITOR)];

auditRouter.get(
  '/audit/dashboard',
  ...auditor,
  asyncHandler(async (req, res) => {
    const data = await auditDashboard();
    await logAuditRead(requireUser(req), req.ip ?? null, '/audit/dashboard');
    sendData(res, data);
  }),
);

auditRouter.get(
  '/audit/reports',
  ...auditor,
  asyncHandler(async (req, res) => {
    const data = await auditReports();
    await logAuditRead(requireUser(req), req.ip ?? null, '/audit/reports');
    sendData(res, data);
  }),
);

auditRouter.get(
  '/audit/reports/:id/export',
  ...auditor,
  validateQuery(exportQuerySchema),
  asyncHandler(async (req, res) => {
    const options = queryOf<ExportQuery>(res);
    const file = await auditExport(
      assertReportId(req.params.id),
      options.format,
      { desde: options.desde, hasta: options.hasta, docenteId: options.docenteId },
      requireUser(req),
      req.ip ?? null,
    );
    sendDownload(res, file);
  }),
);

auditRouter.get(
  '/audit/expedientes',
  ...auditor,
  validateQuery(auditExpedientesQuerySchema),
  asyncHandler(async (req, res) => {
    const options = queryOf<AuditExpedientesQuery>(res);
    const data = await auditExpedientes(options);
    await logAuditRead(requireUser(req), req.ip ?? null, '/audit/expedientes', options);
    sendData(res, data);
  }),
);
