import { z } from 'zod';

/**
 * Configuración del programa (FR-016, R35).
 *
 * La escritura es **por lote**: la pantalla `admin/configuracion.html` guarda los campos
 * de una tarjeta a la vez, pero un solo `PUT` deja una sola transacción y una auditoría
 * por clave cambiada. El valor siempre viaja como texto; el tipo lo declara la fila
 * (`tipo_dato`) y el servicio lo valida, porque no se puede confiar en el cliente para
 * decidir si `12` es un entero o una fecha.
 *
 * `.strict()` rechaza campos de más: `tipoDato`, `descripcion` y `usuarios_id_usuarios`
 * no se aceptan del cliente.
 */
export const updateSettingsSchema = z
  .object({
    items: z
      .array(
        z
          .object({
            clave: z.string().trim().min(1, 'La clave es obligatoria').max(100),
            // `null` o cadena vacía limpian el valor (p. ej. fecha de cierre de admisiones).
            valor: z.string().max(1000).nullable(),
          })
          .strict(),
      )
      .min(1, 'Envía al menos una clave')
      .max(50, 'Envía como máximo 50 claves por vez'),
  })
  .strict()
  .superRefine((value, ctx) => {
    const vistas = new Set<string>();
    value.items.forEach((item, index) => {
      if (vistas.has(item.clave)) {
        ctx.addIssue({
          code: 'custom',
          path: ['items', index, 'clave'],
          message: 'La clave está repetida en la petición',
        });
      }
      vistas.add(item.clave);
    });
  });

export type UpdateSettingsInput = z.infer<typeof updateSettingsSchema>;

export const auditQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(25),
    accion: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    entidad: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
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

export type AuditQuery = z.infer<typeof auditQuerySchema>;
