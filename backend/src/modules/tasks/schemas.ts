import { PRIORIDADES, REVISION_ESTADOS, TAREA_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Tareas del plan de trabajo (FR-023, R19, BR-007).
 *
 * `estado`, `estadoRevision`, `puntajeObtenido`, `retroalimentacion`, `motivoDevolucion`,
 * `observacionesDevolucion`, `evidenciaRequerida` y las fechas de auditoría **no** se
 * aceptan en el alta ni en la edición: los mueven las acciones `/complete`, `/grade` y
 * `/return`. `.strict()` devuelve `400` si el cliente lo intenta.
 *
 * `evidenciaRequerida` es siempre `TRUE` (BR-007, §20.5 #13): el prototipo ofrece «Sin
 * evidencia» y «Permitir entrega fuera de fecha», pero ninguna regla los respalda (P-26).
 */

/** Fecha de calendario `AAAA-MM-DD`; se guarda en `DATE` y se devuelve igual. */
const fecha = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
  .refine((value) => !Number.isNaN(Date.parse(`${value}T12:00:00Z`)), 'La fecha no es válida');

const titulo = z
  .string()
  .trim()
  .min(1, 'El título de la tarea es obligatorio')
  .max(200);
const descripcion = z.string().trim().max(2000).nullable().optional();
const puntos = z
  .number()
  .int('Los puntos deben ser un número entero')
  .min(0, 'Los puntos no pueden ser negativos')
  .max(100, 'Los puntos no pueden superar 100');

/**
 * Motivos de devolución del prototipo (`docente/tarea-devolver.html`). No son un `CHECK`
 * de la tabla: `motivo_devolucion` es texto libre y el vocabulario se controla aquí.
 */
export const MOTIVOS_DEVOLUCION = [
  'Evidencia incompleta',
  'No cumple con lo solicitado',
  'Archivos ilegibles',
  'Entrega fuera de fecha',
  'Otro motivo',
] as const;

export const createTaskSchema = z
  .object({
    titulo,
    descripcion,
    /** El emprendimiento decide el estudiante destinatario (su propietario). */
    emprendimientoId: z.number().int().positive('Selecciona el emprendimiento'),
    fasePlanId: z.number().int().positive().nullable().optional(),
    fechaLimite: fecha.nullable().optional(),
    prioridad: z.enum(PRIORIDADES),
    puntos: puntos.nullable().optional(),
  })
  .strict();

/**
 * Edición de la tarea (docente asignado o administrador).
 *
 * `estado` solo admite `En curso`: es la transición que el docente usa para marcar que el
 * trabajo empezó (T16). Cualquier otro destino se rechaza aquí con `400`; una transición
 * incoherente desde el estado actual responde `422`.
 */
export const updateTaskSchema = z
  .object({
    titulo: titulo.optional(),
    descripcion,
    fasePlanId: z.number().int().positive().nullable().optional(),
    fechaLimite: fecha.nullable().optional(),
    prioridad: z.enum(PRIORIDADES).optional(),
    puntos: puntos.nullable().optional(),
    estado: z.literal('En curso').optional(),
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

/** Calificación: la escala del prototipo es 0–100 (`docente/tarea-detalle.html`). */
export const gradeTaskSchema = z
  .object({
    puntajeObtenido: z
      .number()
      .int('La calificación debe ser un número entero')
      .min(0, 'La calificación no puede ser negativa')
      .max(100, 'La calificación no puede superar 100'),
    retroalimentacion: z.string().trim().max(2000).nullable().optional(),
  })
  .strict();

/** R19b: devolver exige motivo; las observaciones son opcionales. */
export const returnTaskSchema = z
  .object({
    motivo: z.enum(MOTIVOS_DEVOLUCION),
    observaciones: z.string().trim().max(2000).nullable().optional(),
  })
  .strict();

/** Filtros y paginación. `.strict()` cierra el `ORDER BY`. */
export const listTasksQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(TAREA_ESTADOS).optional(),
    estadoRevision: z.enum(REVISION_ESTADOS).optional(),
    prioridad: z.enum(PRIORIDADES).optional(),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    fasePlanId: z.coerce.number().int().positive().optional(),
    sort: z.enum(['limite', 'prioridad', 'estado', 'titulo']).default('limite'),
    order: z.enum(['asc', 'desc']).default('asc'),
  })
  .strict();

export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type UpdateTaskInput = z.infer<typeof updateTaskSchema>;
export type GradeTaskInput = z.infer<typeof gradeTaskSchema>;
export type ReturnTaskInput = z.infer<typeof returnTaskSchema>;
export type ListTasksQuery = z.infer<typeof listTasksQuerySchema>;
