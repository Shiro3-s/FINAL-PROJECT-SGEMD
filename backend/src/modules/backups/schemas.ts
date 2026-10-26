import { RESPALDO_ESTADOS, RESPALDO_TIPOS } from '@sgemd/shared';
import { z } from 'zod';

/**
 * Respaldos (FR-018).
 *
 * El tipo por defecto es `Completo`: el panel del prototipo muestra «Base + evidencias» y
 * un respaldo sin evidencias no cumple FR-018. `Parcial` existe para el volcado rápido.
 */
export const createBackupSchema = z
  .object({
    tipo: z.enum(RESPALDO_TIPOS).default('Completo'),
  })
  .strict();

export type CreateBackupInput = z.infer<typeof createBackupSchema>;

export const listBackupsQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    estado: z.enum(RESPALDO_ESTADOS).optional(),
    tipo: z.enum(RESPALDO_TIPOS).optional(),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    desde: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
      .optional(),
    hasta: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
      .optional(),
  })
  .strict();

export type ListBackupsQuery = z.infer<typeof listBackupsQuerySchema>;

export const downloadBackupQuerySchema = z
  .object({
    part: z.enum(['dump', 'storage']),
  })
  .strict();

export type DownloadBackupQuery = z.infer<typeof downloadBackupQuerySchema>;

export const exportDatabaseQuerySchema = z
  .object({
    format: z.enum(['csv', 'xlsx']),
  })
  .strict();

export type ExportDatabaseQuery = z.infer<typeof exportDatabaseQuerySchema>;
