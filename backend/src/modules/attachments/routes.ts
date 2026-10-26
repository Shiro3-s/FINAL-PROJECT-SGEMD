import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import {
  deleteAttachment,
  downloadAttachment,
  parseEntity,
  uploadAttachment,
} from './service.js';

/**
 * Evidencias (FR-008, BR-006, BR-007).
 *
 * `POST` recibe `multipart/form-data` en streaming: el cuerpo **no** pasa por el
 * `express.json` de la aplicación ni por `validateBody`, porque el archivo nunca se
 * bufferiza en memoria. La autorización por entidad y por rol se resuelve en el servicio.
 *
 * `GET` transmite el archivo con su MIME verificado y el nombre original codificado. El
 * alcance es el del padre (tarea o seguimiento): fuera de alcance responde `404`.
 */
export const attachmentsRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];

attachmentsRouter.post(
  '/attachments/:entity/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    const raw = req.params.entity;
    const entity = parseEntity(typeof raw === 'string' ? raw : '');
    const attachment = await uploadAttachment(
      entity,
      parseId(req, 'entidad'),
      requireUser(req),
      req,
      req.ip ?? null,
    );

    sendData(res, attachment, 201);
  }),
);

attachmentsRouter.get(
  '/attachments/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    await downloadAttachment(parseId(req, 'evidencia'), requireUser(req), res);
  }),
);

attachmentsRouter.delete(
  '/attachments/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    await deleteAttachment(parseId(req, 'evidencia'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Evidencia eliminada.');
  }),
);
