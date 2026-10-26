import { z } from 'zod';
import { EMPRENDIMIENTO_ESTADOS } from '@sgemd/shared';

/**
 * Consultas del auditor (rol 4, solo lectura).
 *
 * No hay `POST`/`PUT`/`PATCH`/`DELETE` en este módulo (README §7): el auditor no edita
 * datos. `expedientes` pagina y filtra como cualquier lista; los filtros son los que la
 * pantalla necesita para encontrar un expediente sin exponer PII.
 */
export const auditExpedientesQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    estado: z.enum(EMPRENDIMIENTO_ESTADOS).optional(),
    docenteId: z.coerce.number().int().positive().optional(),
  })
  .strict();

export type AuditExpedientesQuery = z.infer<typeof auditExpedientesQuerySchema>;
