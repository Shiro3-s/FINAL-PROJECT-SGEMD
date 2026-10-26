import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendDownload } from '../../utils/respond.js';
import {
  createBackupSchema,
  downloadBackupQuerySchema,
  exportDatabaseQuerySchema,
  listBackupsQuerySchema,
  type CreateBackupInput,
  type DownloadBackupQuery,
  type ExportDatabaseQuery,
  type ListBackupsQuery,
} from './schemas.js';
import {
  backupPanel,
  createBackup,
  downloadBackup,
  exportDatabase,
  getBackup,
  listBackups,
  verifyBackup,
} from './service.js';

/**
 * Respaldos (FR-018, FR-009).
 *
 * Todo es del administrador: el historial con tamaños, la descarga, la verificación de
 * integridad, el disparo manual y la exportación completa de la base. Cada descarga y cada
 * exportación se audita (T24).
 */
export const backupsRouter = Router();

const admin = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN)];

backupsRouter.get(
  '/backups',
  ...admin,
  validateQuery(listBackupsQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listBackups(queryOf<ListBackupsQuery>(res)));
  }),
);

// Antes de `/backups/:id`: `panel` y `export` no son ids.
backupsRouter.get(
  '/backups/panel',
  ...admin,
  asyncHandler(async (_req, res) => {
    sendData(res, await backupPanel());
  }),
);

backupsRouter.get(
  '/backups/export',
  ...admin,
  validateQuery(exportDatabaseQuerySchema),
  asyncHandler(async (req, res) => {
    const options = queryOf<ExportDatabaseQuery>(res);
    const file = await exportDatabase(options.format, requireUser(req), req.ip ?? null);
    sendDownload(res, file);
  }),
);

backupsRouter.post(
  '/backups',
  ...admin,
  validateBody(createBackupSchema),
  asyncHandler(async (req, res) => {
    const body = req.body as CreateBackupInput;
    const backup = await createBackup({
      tipo: body.tipo,
      actor: requireUser(req),
      ip: req.ip ?? null,
    });
    sendData(res, backup, 201);
  }),
);

backupsRouter.get(
  '/backups/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(res, await getBackup(parseId(req, 'respaldo')));
  }),
);

backupsRouter.post(
  '/backups/:id/verify',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await verifyBackup(parseId(req, 'respaldo'), requireUser(req), req.ip ?? null),
    );
  }),
);

backupsRouter.get(
  '/backups/:id/download',
  ...admin,
  validateQuery(downloadBackupQuerySchema),
  asyncHandler(async (req, res) => {
    const options = queryOf<DownloadBackupQuery>(res);
    await downloadBackup(
      parseId(req, 'respaldo'),
      options.part,
      res,
      requireUser(req),
      req.ip ?? null,
    );
  }),
);
