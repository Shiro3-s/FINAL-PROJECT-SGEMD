import { ASIGNACION_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Horas semanales de una asignación.
 *
 * El diagrama solo exige `> 0`; el prototipo (`admin/asignaciones.html`) usa un campo
 * numérico `min=1 max=20`. Se conserva ese máximo de formulario. El tope real es el del
 * programa (`carga_max_horas`, 12 h por docente) y se valida sobre la suma de las
 * asignaciones activas, no sobre una fila aislada (FR-016, R35).
 */
const horasSemanales = z
  .number()
  .int('Las horas semanales deben ser un número entero')
  .min(1, 'Las horas semanales deben ser al menos 1')
  .max(20, 'Una asignación no puede superar las 20 horas semanales');

/**
 * Alta de asignación (FR-016, R9, R11).
 *
 * El estudiante **no** se envía: se deriva del propietario del emprendimiento. En el
 * prototipo los campos «Estudiante» y «Emprendimiento» del modal son de solo lectura y se
 * llenan desde la fila seleccionada, así que aceptar un `estudianteId` permitiría crear
 * una asignación incoherente con el expediente. `.strict()` rechaza el resto.
 */
export const createAssignmentSchema = z
  .object({
    mentorId: z.number().int().positive('Selecciona el docente'),
    emprendimientoId: z.number().int().positive('Selecciona el emprendimiento'),
    horasSemanales,
  })
  .strict();

/**
 * Reasignación y ajuste de horas (R9).
 *
 * Solo se editan `mentorId` y `horasSemanales`. El estado no se toca por aquí: la baja
 * tiene su propio `DELETE` y una asignación `inactiva` es un registro histórico que no se
 * reescribe. `estudianteId`, `emprendimientoId` y `estado` se rechazan con `400`.
 */
export const updateAssignmentSchema = z
  .object({
    mentorId: z.number().int().positive('Selecciona el docente').optional(),
    horasSemanales: horasSemanales.optional(),
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

/** Filtros y paginación. `.strict()` impide ordenar por una columna arbitraria. */
export const listAssignmentsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(ASIGNACION_ESTADOS).optional(),
    mentorId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    sort: z
      .enum(['fecha', 'mentor', 'estudiante', 'emprendimiento', 'horas'])
      .default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type CreateAssignmentInput = z.infer<typeof createAssignmentSchema>;
export type UpdateAssignmentInput = z.infer<typeof updateAssignmentSchema>;
export type ListAssignmentsQuery = z.infer<typeof listAssignmentsQuerySchema>;
