import { ASESORIA_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Asesorías (FR-004, FR-015, BR-002, T20, T35).
 *
 * El estudiante **solicita** (bandeja de solicitudes); nunca crea ni confirma una sesión.
 * El administrador crea y asigna; el docente asignado acepta, rechaza o propone otra
 * fecha. El horario se expresa con la tripleta `fecha` + `horaInicio` + `horaFin`, que se
 * resuelve contra `fecha_y_horarios` (el diagrama guarda el bloque, no horas sueltas).
 */

const fecha = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
  .refine((value) => !Number.isNaN(Date.parse(`${value}T12:00:00Z`)), 'La fecha no es válida');

const hora = z
  .string()
  .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Usa el formato HH:MM (24 horas)');

const tema = z
  .string()
  .trim()
  .min(1, 'El tema de la asesoría es obligatorio')
  .max(200);

const lugarEnlace = z.string().trim().max(500).nullable().optional();

const modalidadId = z.number().int().positive().nullable().optional();

const schedule = {
  fecha: fecha.optional(),
  horaInicio: hora.optional(),
  horaFin: hora.optional(),
};

/**
 * El horario es todo o nada: media fecha no se puede guardar. Además `horaFin` debe ser
 * posterior a `horaInicio` (mismo `CHECK` que `fecha_y_horarios`).
 */
function checkSchedule(
  value: { fecha?: string; horaInicio?: string; horaFin?: string },
  ctx: z.RefinementCtx,
): void {
  const given = [value.fecha, value.horaInicio, value.horaFin].filter(
    (item) => item !== undefined,
  ).length;

  if (given !== 0 && given !== 3) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['fecha'],
      message: 'Envía fecha, hora de inicio y hora de fin juntas',
    });
    return;
  }

  if (
    value.horaInicio !== undefined &&
    value.horaFin !== undefined &&
    value.horaFin <= value.horaInicio
  ) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['horaFin'],
      message: 'La hora de fin debe ser posterior a la de inicio',
    });
  }
}

/**
 * Alta directa (administrador) o para un emprendimiento propio (docente asignado).
 * `docenteId` es obligatorio: el diagrama exige un docente en toda asesoría.
 */
export const createAdviceSchema = z
  .object({
    emprendimientoId: z.number().int().positive('Selecciona el emprendimiento'),
    docenteId: z.number().int().positive('Selecciona el docente'),
    tema,
    modalidadId,
    lugarEnlace,
    ...schedule,
  })
  .strict()
  .superRefine(checkSchedule);

/**
 * Edición. `docenteId` solo lo cambia el administrador (se comprueba en el servicio para
 * responder `403 FIELD_NOT_ALLOWED`, no `400`). `estado` solo admite las dos transiciones
 * del día de la sesión; el resto se mueve con `accept`, `repropose` o `reject`.
 */
export const updateAdviceSchema = z
  .object({
    tema: tema.optional(),
    modalidadId,
    lugarEnlace,
    docenteId: z.number().int().positive().optional(),
    estado: z.enum(['En curso', 'Completada']).optional(),
    ...schedule,
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  })
  .superRefine(checkSchedule);

/** Confirmar puede incluir un horario (si la sesión estaba «Por agendar»). */
export const acceptAdviceSchema = z.object({ ...schedule }).strict().superRefine(checkSchedule);

/** Proponer otra fecha exige el horario completo. */
export const reproposeAdviceSchema = z
  .object({
    fecha,
    horaInicio: hora,
    horaFin: hora,
  })
  .strict()
  .refine((value) => value.horaFin > value.horaInicio, {
    path: ['horaFin'],
    message: 'La hora de fin debe ser posterior a la de inicio',
  });

/** Rechazar exige motivo (el diagrama no tiene columna: va en auditoría y aviso, P-29). */
export const rejectAdviceSchema = z
  .object({
    motivo: z.string().trim().min(1, 'Escribe el motivo del rechazo').max(500),
  })
  .strict();

/**
 * Filtros del listado. `grupo=Agendada` es la etiqueta del prototipo docente: agrupa
 * Programada + Confirmada + En curso y **nunca** se guarda como estado (master §7.2).
 */
export const listAdviceQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    estado: z.enum(ASESORIA_ESTADOS).optional(),
    grupo: z.literal('Agendada').optional(),
    docenteId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    modalidadId: z.coerce.number().int().positive().optional(),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    desde: fecha.optional(),
    hasta: fecha.optional(),
    sort: z
      .enum(['fecha', 'estado', 'tema', 'emprendimiento', 'estudiante', 'docente'])
      .default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type CreateAdviceInput = z.infer<typeof createAdviceSchema>;
export type UpdateAdviceInput = z.infer<typeof updateAdviceSchema>;
export type AcceptAdviceInput = z.infer<typeof acceptAdviceSchema>;
export type ReproposeAdviceInput = z.infer<typeof reproposeAdviceSchema>;
export type RejectAdviceInput = z.infer<typeof rejectAdviceSchema>;
export type ListAdviceQuery = z.infer<typeof listAdviceQuerySchema>;
