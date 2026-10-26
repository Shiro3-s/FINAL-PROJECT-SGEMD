import { EVENTO_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Eventos y recomendaciones (FR-021, T27).
 *
 * El administrador crea y edita; el docente recomienda solo a sus emprendimientos
 * asignados; el estudiante ve los eventos publicados y sus recomendaciones.
 *
 * `estado` solo admite `Pendiente` (borrador) y `Publicado` en la escritura: el
 * administrador es el organizador, así que no hay un flujo de aprobación separado. Los
 * valores `Aprobado`/`Rechazado` del diagrama quedan reservados (P-37).
 */

const fecha = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
  .refine((value) => !Number.isNaN(Date.parse(`${value}T12:00:00Z`)), 'La fecha no es válida');

const hora = z
  .string()
  .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Usa el formato HH:MM');

const nombreEvento = z
  .string()
  .trim()
  .min(1, 'El nombre del evento es obligatorio')
  .max(200);
const texto = (max: number) => z.string().trim().max(max).nullable().optional();
const capacidadMaxima = z
  .number()
  .int('La capacidad debe ser un número entero')
  .positive('La capacidad debe ser mayor que cero')
  .nullable()
  .optional();

/** Bloque de agenda: si llega una parte, llegan las tres. */
const schedule = {
  fecha: fecha.optional(),
  horaInicio: hora.optional(),
  horaFin: hora.optional(),
};

type ScheduleInput = { fecha?: string; horaInicio?: string; horaFin?: string };

function checkSchedule(value: ScheduleInput, ctx: z.RefinementCtx): void {
  const parts = [value.fecha, value.horaInicio, value.horaFin];
  const present = parts.filter((part) => part !== undefined).length;

  if (present === 0) return;

  if (present !== 3) {
    ctx.addIssue({
      code: 'custom',
      path: ['fecha'],
      message: 'El horario se envía completo: fecha, hora de inicio y hora de fin',
    });
    return;
  }

  if (value.horaFin! <= value.horaInicio!) {
    ctx.addIssue({
      code: 'custom',
      path: ['horaFin'],
      message: 'La hora de fin debe ser posterior a la de inicio',
    });
  }
}

export const createEventSchema = z
  .object({
    nombreEvento,
    descripcion: texto(2000),
    dirigidoA: texto(200),
    capacidadMaxima,
    estado: z.enum(['Pendiente', 'Publicado']).default('Pendiente'),
    requiereRegistro: z.boolean().default(false),
    lugar: texto(200),
    enlace: texto(500),
    tipoEventoId: z.number().int().positive().nullable().optional(),
    modalidadId: z.number().int().positive().nullable().optional(),
    ...schedule,
  })
  .strict()
  .superRefine(checkSchedule);

export type CreateEventInput = z.infer<typeof createEventSchema>;

export const updateEventSchema = z
  .object({
    nombreEvento: nombreEvento.optional(),
    descripcion: texto(2000),
    dirigidoA: texto(200),
    capacidadMaxima,
    estado: z.enum(['Pendiente', 'Publicado']).optional(),
    requiereRegistro: z.boolean().optional(),
    lugar: texto(200),
    enlace: texto(500),
    tipoEventoId: z.number().int().positive().nullable().optional(),
    modalidadId: z.number().int().positive().nullable().optional(),
    ...schedule,
  })
  .strict()
  .superRefine(checkSchedule)
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

export type UpdateEventInput = z.infer<typeof updateEventSchema>;

export const listEventsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(EVENTO_ESTADOS).optional(),
    tipoEventoId: z.coerce.number().int().positive().optional(),
    modalidadId: z.coerce.number().int().positive().optional(),
    desde: fecha.optional(),
    hasta: fecha.optional(),
    sort: z.enum(['fecha', 'nombre', 'estado', 'cupo']).default('fecha'),
    order: z.enum(['asc', 'desc']).default('asc'),
  })
  .strict();

export type ListEventsQuery = z.infer<typeof listEventsQuerySchema>;

export const createRecommendationSchema = z
  .object({
    emprendimientoId: z.number().int().positive('Selecciona el emprendimiento'),
    /** Opcional: sin él, la recomendación es para todo el emprendimiento. */
    estudianteId: z.number().int().positive().nullable().optional(),
    mensaje: texto(1000),
  })
  .strict();

export type CreateRecommendationInput = z.infer<typeof createRecommendationSchema>;

export const listRecommendationsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
  })
  .strict();

export type ListRecommendationsQuery = z.infer<typeof listRecommendationsQuerySchema>;
