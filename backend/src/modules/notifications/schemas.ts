import { NOTIFICACION_TIPOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Bandeja de notificaciones (FR-019, T21).
 *
 * El destinatario es siempre la sesión: no se acepta `usuariosId`. `.strict()` rechaza
 * cualquier otro parámetro, incluido un `ORDER BY` arbitrario (no se expone: la bandeja
 * siempre va de la más reciente a la más antigua).
 */
export const listNotificationsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    /** `true`/`false` en texto: `z.coerce.boolean()` convertiría "false" en `true`. */
    leida: z
      .enum(['true', 'false'])
      .transform((value) => value === 'true')
      .optional(),
    tipo: z.enum(NOTIFICACION_TIPOS).optional(),
  })
  .strict();

export type ListNotificationsQuery = z.infer<typeof listNotificationsQuerySchema>;
