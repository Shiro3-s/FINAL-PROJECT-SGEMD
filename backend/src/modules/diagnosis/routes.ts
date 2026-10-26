import { Router } from 'express';
import { query } from '../../db/pool.js';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData } from '../../utils/respond.js';
import {
  diagnosisMeQuerySchema,
  listDiagnosesQuerySchema,
  saveDiagnosisSchema,
  type DiagnosisMeQuery,
  type ListDiagnosesQuery,
  type SaveDiagnosisInput,
} from './schemas.js';
import {
  diagnosisReport,
  getDiagnosis,
  getMyCharacterization,
  getMyDiagnosis,
  listDiagnoses,
  loadForm,
  saveMyDiagnosis,
} from './service.js';

/**
 * Diagnóstico de caracterización (FR-002, T25).
 *
 * Módulo de trabajo: sesión **y** cuenta `Activo`. El estudiante diligenia el suyo; el
 * administrador y el docente asignado lo leen. El banco de preguntas lo puede ver
 * cualquier sesión activa (el administrador tiene «Ver instrumento» en el prototipo).
 */
export const diagnosisRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];

diagnosisRouter.get(
  '/diagnosis/form',
  ...reader,
  asyncHandler(async (_req, res) => {
    sendData(res, await loadForm({ query }));
  }),
);

diagnosisRouter.get(
  '/diagnosis/me',
  ...reader,
  requireRole(ROLES.ESTUDIANTE),
  validateQuery(diagnosisMeQuerySchema),
  asyncHandler(async (req, res) => {
    const { emprendimientoId } = queryOf<DiagnosisMeQuery>(res);
    sendData(res, await getMyDiagnosis(requireUser(req), emprendimientoId));
  }),
);

diagnosisRouter.post(
  '/diagnosis/me',
  ...reader,
  requireRole(ROLES.ESTUDIANTE),
  validateBody(saveDiagnosisSchema),
  asyncHandler(async (req, res) => {
    const body = req.body as SaveDiagnosisInput;
    sendData(res, await saveMyDiagnosis(requireUser(req), body, req.ip ?? null));
  }),
);

diagnosisRouter.get(
  '/characterization/me',
  ...reader,
  requireRole(ROLES.ESTUDIANTE),
  validateQuery(diagnosisMeQuerySchema),
  asyncHandler(async (req, res) => {
    const { emprendimientoId } = queryOf<DiagnosisMeQuery>(res);
    sendData(res, await getMyCharacterization(requireUser(req), emprendimientoId));
  }),
);

diagnosisRouter.get(
  '/diagnosis',
  ...reader,
  validateQuery(listDiagnosesQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listDiagnoses(queryOf<ListDiagnosesQuery>(res), requireUser(req)),
    );
  }),
);

diagnosisRouter.get(
  '/diagnosis/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getDiagnosis(parseId(req, 'diagnóstico'), requireUser(req)));
  }),
);

diagnosisRouter.get(
  '/diagnosis/:id/report',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await diagnosisReport(parseId(req, 'diagnóstico'), requireUser(req)));
  }),
);
