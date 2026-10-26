import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { query } from '../../db/pool.js';
import { findEntrepreneurshipForActor } from '../../services/entrepreneurshipAccess.js';
import { progressByPhase } from '../../services/progress.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import {
  createTaskSchema,
  gradeTaskSchema,
  listTasksQuerySchema,
  returnTaskSchema,
  updateTaskSchema,
  type ListTasksQuery,
} from './schemas.js';
import {
  completeTask,
  createTask,
  deleteTask,
  getTask,
  gradeTask,
  listMyTasks,
  listTasks,
  listTasksByEntrepreneurship,
  returnTask,
  updateTask,
} from './service.js';

/**
 * Tareas del plan de trabajo (FR-023, R19).
 *
 * Módulo de trabajo: sesión y cuenta `Activo`. El docente asignado y el administrador
 * crean, editan, califican, devuelven y dan de baja; el estudiante lee las suyas y las
 * entrega. El alcance se resuelve en el servicio (R25).
 */
export const tasksRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];
const writer = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN, ROLES.DOCENTE)];

// Rutas con segmento fijo antes de `/:id` para que no se lean como identificadores.
tasksRouter.get(
  '/task',
  ...reader,
  validateQuery(listTasksQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(res, await listTasks(queryOf<ListTasksQuery>(res), requireUser(req)));
  }),
);

tasksRouter.get(
  '/task/my-task',
  ...reader,
  validateQuery(listTasksQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(res, await listMyTasks(queryOf<ListTasksQuery>(res), requireUser(req)));
  }),
);

tasksRouter.get(
  '/task/advance/entrepreneurship/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    const emprendimientoId = parseId(req, 'emprendimiento');
    await findEntrepreneurshipForActor({ query }, emprendimientoId, requireUser(req));
    sendData(res, await progressByPhase({ query }, emprendimientoId));
  }),
);

tasksRouter.get(
  '/task/entrepreneurship/:id',
  ...reader,
  validateQuery(listTasksQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listTasksByEntrepreneurship(
        parseId(req, 'emprendimiento'),
        queryOf<ListTasksQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

tasksRouter.get(
  '/task/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getTask(parseId(req, 'tarea'), requireUser(req)));
  }),
);

tasksRouter.post(
  '/task',
  ...writer,
  validateBody(createTaskSchema),
  asyncHandler(async (req, res) => {
    sendData(res, await createTask(req.body, requireUser(req), req.ip ?? null), 201);
  }),
);

tasksRouter.put(
  '/task/:id',
  ...writer,
  validateBody(updateTaskSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateTask(parseId(req, 'tarea'), req.body, requireUser(req), req.ip ?? null),
    );
  }),
);

// La entrega es del estudiante destinatario; el servicio comprueba la propiedad.
tasksRouter.put(
  '/task/:id/complete',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await completeTask(parseId(req, 'tarea'), requireUser(req), req.ip ?? null));
  }),
);

tasksRouter.put(
  '/task/:id/grade',
  ...writer,
  validateBody(gradeTaskSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await gradeTask(parseId(req, 'tarea'), req.body, requireUser(req), req.ip ?? null),
    );
  }),
);

tasksRouter.put(
  '/task/:id/return',
  ...writer,
  validateBody(returnTaskSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await returnTask(parseId(req, 'tarea'), req.body, requireUser(req), req.ip ?? null),
    );
  }),
);

tasksRouter.delete(
  '/task/:id',
  ...writer,
  asyncHandler(async (req, res) => {
    await deleteTask(parseId(req, 'tarea'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Tarea dada de baja.');
  }),
);
