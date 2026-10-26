import { ACTA_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Acta de compromiso y confidencialidad (FR-003, BR-009, T26).
 *
 * La carga es `multipart/form-data` (campo `file`), así que no pasa por `validateBody`.
 * La revisión solo admite los dos destinos finales; el rechazo exige motivo (BR-009).
 */
export const reviewActaSchema = z
  .object({
    estado: z.enum(['Aprobada', 'Rechazada']),
    observaciones: z.string().trim().max(2000).nullable().optional(),
  })
  .strict()
  .superRefine((value, ctx) => {
    if (value.estado === 'Rechazada' && !value.observaciones) {
      ctx.addIssue({
        code: 'custom',
        path: ['observaciones'],
        message: 'El rechazo del acta exige un motivo',
      });
    }
  });

export type ReviewActaInput = z.infer<typeof reviewActaSchema>;

export const listActaQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(ACTA_ESTADOS).optional(),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    sort: z.enum(['fecha', 'estado', 'estudiante', 'emprendimiento']).default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type ListActaQuery = z.infer<typeof listActaQuerySchema>;
