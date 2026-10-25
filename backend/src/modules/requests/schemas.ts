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
export type RejectRequestInput = z.infer<typeof rejectRequestSchema>;
export type ListRequestsQuery = z.infer<typeof listRequestsQuerySchema>;
