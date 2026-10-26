import { DIAGNOSTICO_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Diagnóstico de caracterización (FR-002, T25).
 *
 * `estado`, `puntajeTotal`, `urlInforme` y las fechas **no** se aceptan del cliente: el
 * estado lo mueve el envío, y el puntaje depende de la rúbrica (AQ-09), que todavía no
 * está configurada. `.strict()` devuelve `400` si se intenta.
 *
 * El guardado es incremental («guardar borrador»): se pueden enviar solo las respuestas
 * nuevas o corregidas. El envío exige que todas las preguntas activas estén respondidas.
 */

const respuesta = z
  .object({
    preguntaId: z.number().int().positive('La pregunta no es válida'),
    valor: z
      .string()
      .trim()
      .min(1, 'La respuesta no puede estar vacía')
      .max(4000, 'La respuesta es demasiado larga'),
  })
  .strict();

function sinDuplicados(items: { preguntaId: number }[]): boolean {
  return new Set(items.map((item) => item.preguntaId)).size === items.length;
}

export const saveDiagnosisSchema = z
  .object({
    /** Opcional cuando el estudiante tiene un solo emprendimiento vigente. */
    emprendimientoId: z.number().int().positive().optional(),
    respuestas: z
      .array(respuesta)
      .min(1, 'Envía al menos una respuesta')
      .max(200, 'El cuestionario no tiene tantas preguntas'),
    /** `false` guarda el borrador; `true` envía y bloquea las respuestas. */
    enviar: z.boolean().default(false),
  })
  .strict()
  .refine((value) => sinDuplicados(value.respuestas), {
    message: 'Una pregunta no puede responderse dos veces en la misma petición',
    path: ['respuestas'],
  });

export type SaveDiagnosisInput = z.infer<typeof saveDiagnosisSchema>;

export const listDiagnosesQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(DIAGNOSTICO_ESTADOS).optional(),
    emprendimientoId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    sort: z.enum(['fecha', 'estado', 'emprendimiento', 'estudiante']).default('fecha'),
    order: z.enum(['asc', 'desc']).default('desc'),
  })
  .strict();

export type ListDiagnosesQuery = z.infer<typeof listDiagnosesQuerySchema>;

/** `GET /diagnosis/me` y `GET /characterization/me` aceptan el emprendimiento. */
export const diagnosisMeQuerySchema = z
  .object({
    emprendimientoId: z.coerce.number().int().positive().optional(),
  })
  .strict();

export type DiagnosisMeQuery = z.infer<typeof diagnosisMeQuerySchema>;
