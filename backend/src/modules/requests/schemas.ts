import { SOLICITUD_ESTADOS, SOLICITUD_TIPOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Bandeja única de solicitudes (R38): desbloqueos de cuenta, autorización de un
 * emprendimiento paralelo y citas de asesoría.
 *
 * El solicitante **nunca** se envía: es siempre la sesión actual. Un administrador que
 * quisiera crear una asesoría directamente tiene su propio módulo (Etapa 8).
 */
export const createRequestSchema = z
  .object({
    tipo: z.enum(SOLICITUD_TIPOS),
    detalle: z.string().trim().max(1000).nullable().optional(),
    /** Obligatorio para `Paralelo` y `Cita`; debe pertenecer al solicitante. */
    emprendimientoId: z.number().int().positive().nullable().optional(),
  })
  .strict();

/** Rechazo: el motivo es obligatorio (R38, T12). */
export const rejectRequestSchema = z
  .object({
    motivo: z.string().trim().min(1, 'Escribe el motivo del rechazo').max(500),
  })
  .strict();

/**
 * Aprobación. Solo una `Cita` usa los datos de programación: al aprobarla se crea la
 * asesoría en `Programada` (P-19), así que exige docente, tema y horario. Los demás tipos
 * se aprueban con un cuerpo vacío.
 */
const fecha = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
  .refine((value) => !Number.isNaN(Date.parse(`${value}T12:00:00Z`)), 'La fecha no es válida');

const hora = z
  .string()
  .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Usa el formato HH:MM (24 horas)');

export const approveRequestSchema = z
  .object({
    docenteId: z.number().int().positive().optional(),
    tema: z.string().trim().min(1).max(200).optional(),
    fecha: fecha.optional(),
    horaInicio: hora.optional(),
    horaFin: hora.optional(),
    modalidadId: z.number().int().positive().nullable().optional(),
    lugarEnlace: z.string().trim().max(500).nullable().optional(),
  })
  .strict()
  .superRefine((value, ctx) => {
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
  });

/** Filtros y paginación de la bandeja. `.strict()` cierra el `ORDER BY`. */
export const listRequestsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    tipo: z.enum(SOLICITUD_TIPOS).optional(),
    estado: z.enum(SOLICITUD_ESTADOS).optional(),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    sort: z.enum(['fecha', 'tipo', 'estado']).default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type CreateRequestInput = z.infer<typeof createRequestSchema>;
export type ApproveRequestInput = z.infer<typeof approveRequestSchema>;
export type RejectRequestInput = z.infer<typeof rejectRequestSchema>;
export type ListRequestsQuery = z.infer<typeof listRequestsQuerySchema>;
