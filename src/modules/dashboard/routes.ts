import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData } from '../../utils/respond.js';
import { adminDashboard, studentDashboard, teacherDashboard } from './service.js';

/**
 * Tableros por rol (FR-010).
 *
 * Tres rutas, tres consultas agregadas. El rol se exige en la ruta y el alcance se aplica
 * en el SQL: un docente no puede pedir el tablero del administrador (`403`) y el del
 * estudiante solo devuelve su emprendimiento.
 */
export const dashboardRouter = Router();

dashboardRouter.get(
  '/dashboard/admin',
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN),
  asyncHandler(async (_req, res) => {
    sendData(res, await adminDashboard());
  }),
);

dashboardRouter.get(
  '/dashboard/teacher',
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.DOCENTE),
  asyncHandler(async (req, res) => {
    sendData(res, await teacherDashboard(requireUser(req)));
  }),
);

dashboardRouter.get(
  '/dashboard/student',
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ESTUDIANTE),
  asyncHandler(async (req, res) => {
    sendData(res, await studentDashboard(requireUser(req)));
  }),
);
