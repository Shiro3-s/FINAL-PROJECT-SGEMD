import { EMPRENDIMIENTO_ESTADOS } from '@sgemd/shared';
import { z } from 'zod';

const nombre = z
  .string()
  .trim()
  .min(1, 'El nombre del emprendimiento es obligatorio')
  .max(150);
const descripcion = z.string().trim().max(2000).nullable().optional();
const redesSociales = z.string().trim().max(300).nullable().optional();

/** Id de catálogo: `null` limpia el campo, omitirlo lo deja como está. */
const catalogo = z.number().int().positive().nullable().optional();

/**
 * Alta de emprendimiento (FR-012, R37).
 *
 * El alta la hace el administrador y siempre nace `Pendiente`. `estadoAprobacion`,
 * `motivoRechazo`, `codigo` y `avance` no se aceptan: los decide el servidor (`.strict()`
 * responde `400` si el cliente los envía).
 *
 * `esParalelo` es la **autorización expresa** que exige BR-004 para un segundo
 * emprendimiento del mismo estudiante. No es un dato descriptivo: sin ella, el alta se
 * rechaza cuando el estudiante ya tiene uno vigente.
 */
export const createEntrepreneurshipSchema = z
  .object({
    nombre,
    descripcion,
    redesSociales,
    estudianteId: z.number().int().positive('Selecciona el estudiante propietario'),
    sectorId: catalogo,
    etapaId: z.number().int().positive().optional(),
    centroUniversitarioId: catalogo,
    esParalelo: z.boolean().default(false),
  })
  .strict();

/**
 * Edición.
 *
 * El administrador puede cambiar nombre, descripción, redes, sector, etapa y sede. El
 * estudiante propietario solo nombre, descripción y redes (master §13.2); el servicio
 * rechaza el resto con `403 FIELD_NOT_ALLOWED`. El propietario no se cambia.
 */
export const updateEntrepreneurshipSchema = z
  .object({
    nombre: nombre.optional(),
    descripcion,
    redesSociales,
    sectorId: catalogo,
    etapaId: catalogo,
    centroUniversitarioId: catalogo,
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

/** Rechazo: el motivo es obligatorio (BR-004, T12). */
export const rejectEntrepreneurshipSchema = z
  .object({
    motivo: z.string().trim().min(1, 'Escribe el motivo del rechazo').max(500),
  })
  .strict();

/** Filtros y paginación. `.strict()` impide ordenar por una columna arbitraria. */
export const listEntrepreneurshipQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(EMPRENDIMIENTO_ESTADOS).optional(),
    etapaId: z.coerce.number().int().positive().optional(),
    sectorId: z.coerce.number().int().positive().optional(),
    estudianteId: z.coerce.number().int().positive().optional(),
    paralelo: z
      .enum(['true', 'false'])
      .optional()
      .transform((value) => (value === undefined ? undefined : value === 'true')),
    sort: z
      .enum(['codigo', 'nombre', 'estadoAprobacion', 'avance', 'estudiante'])
      .default('codigo'),
    order: z.enum(['asc', 'desc']).default('asc'),
  })
  .strict();

export type CreateEntrepreneurshipInput = z.infer<typeof createEntrepreneurshipSchema>;
export type UpdateEntrepreneurshipInput = z.infer<typeof updateEntrepreneurshipSchema>;
export type RejectEntrepreneurshipInput = z.infer<typeof rejectEntrepreneurshipSchema>;
export type ListEntrepreneurshipQuery = z.infer<typeof listEntrepreneurshipQuerySchema>;
