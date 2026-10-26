import { REVISION_ESTADOS, SEGUIMIENTO_TIPOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Seguimientos del emprendimiento (FR-022, R21).
 *
 * El autor es siempre la sesión: no se acepta `usuariosId`. El emprendimiento decide a qué
 * expediente pertenece el registro. `.strict()` rechaza el resto.
 */
const fecha = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
  .refine((value) => !Number.isNaN(Date.parse(`${value}T12:00:00Z`)), 'La fecha no es válida');

const descripcion = z
  .string()
  .trim()
  .min(1, 'La descripción del seguimiento es obligatoria')
  .max(2000);

const puntaje = z
  .number()
  .int('El puntaje debe ser un número entero')
  .min(0, 'El puntaje no puede ser negativo')
  .max(100, 'El puntaje no puede superar 100');

export const createTracingSchema = z
  .object({
    emprendimientoId: z.number().int().positive('Selecciona el emprendimiento'),
    tipoSeguimiento: z.enum(SEGUIMIENTO_TIPOS),
    descripcion,
    /** Obligatoria para `Avance de fase` (el formulario del prototipo la exige). */
    fasePlanId: z.number().int().positive().nullable().optional(),
    puntaje: puntaje.nullable().optional(),
    estadoRevision: z.enum(REVISION_ESTADOS).optional(),
    fechaSeguimiento: fecha.nullable().optional(),
    retroalimentacion: z.string().trim().max(2000).nullable().optional(),
  })
  .strict();

/**
 * Edición del seguimiento (autor o administrador).
 *
 * `tipoSeguimiento` y `emprendimientoId` no se editan: cambiar el tipo dejaría un
 * «Comentario» con fase y puntaje, o un «Avance de fase» sin ella.
 */
export const updateTracingSchema = z
  .object({
    descripcion: descripcion.optional(),
    fasePlanId: z.number().int().positive().nullable().optional(),
    puntaje: puntaje.nullable().optional(),
    estadoRevision: z.enum(REVISION_ESTADOS).optional(),
    fechaSeguimiento: fecha.nullable().optional(),
    retroalimentacion: z.string().trim().max(2000).nullable().optional(),
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

export const listTracingQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    tipo: z.enum(SEGUIMIENTO_TIPOS).optional(),
    estadoRevision: z.enum(REVISION_ESTADOS).optional(),
    fasePlanId: z.coerce.number().int().positive().optional(),
    sort: z.enum(['fecha', 'tipo', 'estado']).default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type CreateTracingInput = z.infer<typeof createTracingSchema>;
export type UpdateTracingInput = z.infer<typeof updateTracingSchema>;
export type ListTracingQuery = z.infer<typeof listTracingQuerySchema>;
