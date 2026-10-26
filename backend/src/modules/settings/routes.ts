import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData } from '../../utils/respond.js';
import {
  auditQuerySchema,
  updateSettingsSchema,
  type AuditQuery,
  type UpdateSettingsInput,
} from './schemas.js';
import { listAudit, listSettings, updateSettings } from './service.js';

/**
 * Configuración del programa (FR-016) y bitácora del administrador.
 *
 * Solo el administrador: son los topes que gobiernan todo el programa y la traza de quién
 * los cambió. El auditor tiene su propio módulo de solo lectura (`/audit/*`) con datos
 * personales enmascarados; aquí se ven los valores anteriores y nuevos completos porque
 * son configuración, no PII.
 */
export const settingsRouter = Router();

const admin = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN)];

settingsRouter.get(
  '/settings',
  ...admin,
  asyncHandler(async (_req, res) => {
    sendData(res, await listSettings());
  }),
);

settingsRouter.put(
  '/settings',
  ...admin,
  validateBody(updateSettingsSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateSettings(
        req.body as UpdateSettingsInput,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

settingsRouter.get(
  '/settings/audit',
  ...admin,
  validateQuery(auditQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listAudit(queryOf<AuditQuery>(res)));
  }),
);
