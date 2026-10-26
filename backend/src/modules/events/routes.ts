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
  createEventSchema,
  createRecommendationSchema,
  listEventsQuerySchema,
  listRecommendationsQuerySchema,
  updateEventSchema,
  type CreateEventInput,
  type CreateRecommendationInput,
  type ListEventsQuery,
  type ListRecommendationsQuery,
  type UpdateEventInput,
} from './schemas.js';
import {
  createEvent,
  createRecommendation,
  deleteEvent,
  getEvent,
  listEvents,
  listRecommendations,
  registerForEvent,
  unregisterFromEvent,
  updateEvent,
} from './service.js';

/**
 * Eventos institucionales (FR-021, T27).
 *
 * Todos los roles leen (el docente y el estudiante solo los publicados); el administrador
 * escribe el evento, el docente recomienda y el estudiante se inscribe. Las rutas siguen
 * el nombre singular de §13.3 (`/event`).
 */
export const eventsRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];
const admin = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN)];
const teacher = [requireAuth, requireActiveAccount, requireRole(ROLES.DOCENTE)];
const student = [requireAuth, requireActiveAccount, requireRole(ROLES.ESTUDIANTE)];

eventsRouter.get(
  '/event',
  ...reader,
  validateQuery(listEventsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(res, await listEvents(queryOf<ListEventsQuery>(res), requireUser(req)));
  }),
);

eventsRouter.get(
  '/event/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getEvent(parseId(req, 'evento'), requireUser(req)));
  }),
);

eventsRouter.post(
  '/event',
  ...admin,
  validateBody(createEventSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await createEvent(req.body as CreateEventInput, requireUser(req), req.ip ?? null),
      201,
    );
  }),
);

eventsRouter.put(
  '/event/:id',
  ...admin,
  validateBody(updateEventSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateEvent(
        parseId(req, 'evento'),
        req.body as UpdateEventInput,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

eventsRouter.delete(
  '/event/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    await deleteEvent(parseId(req, 'evento'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Evento dado de baja.');
  }),
);

eventsRouter.post(
  '/event/:id/register',
  ...student,
  asyncHandler(async (req, res) => {
    sendData(res, await registerForEvent(parseId(req, 'evento'), requireUser(req), req.ip ?? null));
  }),
);

eventsRouter.delete(
  '/event/:id/register',
  ...student,
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await unregisterFromEvent(parseId(req, 'evento'), requireUser(req), req.ip ?? null),
    );
  }),
);

eventsRouter.get(
  '/event/:id/recommendations',
  ...reader,
  validateQuery(listRecommendationsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listRecommendations(
        parseId(req, 'evento'),
        queryOf<ListRecommendationsQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

eventsRouter.post(
  '/event/:id/recommendations',
  ...teacher,
  validateBody(createRecommendationSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await createRecommendation(
        parseId(req, 'evento'),
        req.body as CreateRecommendationInput,
        requireUser(req),
        req.ip ?? null,
      ),
      201,
    );
  }),
);
