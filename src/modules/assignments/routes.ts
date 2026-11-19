import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import {
  createAssignmentSchema,
  listAssignmentsQuerySchema,
  updateAssignmentSchema,
  type ListAssignmentsQuery,
} from './schemas.js';
import {
  createAssignment,
  deactivateAssignment,
  getAssignment,
  listAssignments,
  listAssignmentsByMentor,
  listAssignmentsByStudent,
  updateAssignment,
} from './service.js';

/**
 * Asignaciones docente ↔ emprendimiento (FR-016, R9–R11).
 *
 * Módulo de trabajo: sesión y cuenta `Activo` en todas las rutas. La lectura se filtra
 * por rol en el servicio (el docente ve las suyas, el estudiante las suyas); la escritura
 * es exclusiva del administrador (R9).
 */
export const assignmentsRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];
const admin = [requireAuth, requireRole(ROLES.ADMIN), requireActiveAccount];

assignmentsRouter.get(
  '/assignments',
  ...reader,
  validateQuery(listAssignmentsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listAssignments(queryOf<ListAssignmentsQuery>(res), requireUser(req)),
    );
  }),
);

// Las rutas con segmento fijo van antes de `/:id` para que «mentor» y «student» nunca se
// interpreten como un identificador.
assignmentsRouter.get(
  '/assignments/mentor/:id',
  ...reader,
  validateQuery(listAssignmentsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listAssignmentsByMentor(
        parseId(req, 'docente'),
        queryOf<ListAssignmentsQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

assignmentsRouter.get(
  '/assignments/student/:id',
  ...reader,
  validateQuery(listAssignmentsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listAssignmentsByStudent(
        parseId(req, 'estudiante'),
        queryOf<ListAssignmentsQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

assignmentsRouter.get(
  '/assignments/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getAssignment(parseId(req, 'asignación'), requireUser(req)));
  }),
);

assignmentsRouter.post(
  '/assignments',
  ...admin,
  validateBody(createAssignmentSchema),
  asyncHandler(async (req, res) => {
    sendData(res, await createAssignment(req.body, requireUser(req), req.ip ?? null), 201);
  }),
);

assignmentsRouter.put(
  '/assignments/:id',
  ...admin,
  validateBody(updateAssignmentSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateAssignment(
        parseId(req, 'asignación'),
        req.body,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

assignmentsRouter.delete(
  '/assignments/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    await deactivateAssignment(parseId(req, 'asignación'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Asignación dada de baja.');
  }),
);
