import type { NotificacionTipo } from '@sgemd/shared';
import type { Queryable } from './audit.js';

/**
 * Escritura de notificaciones (lado de escritura, Etapa 4).
 *
 * Los endpoints de listar y marcar como leídas llegan en la Etapa 8; aquí solo se deja el
 * helper que usan los cambios de estado de cuenta. Se llama **dentro** de la misma
 * transacción que el cambio que la origina, igual que la auditoría.
 *
 * Las preferencias `notif_tareas`, `notif_asesorias` y `notif_seguimiento` de
 * `configuracion_programa` no se aplican todavía: se respetan al construir la bandeja
 * (Etapa 8), que es donde el usuario puede consultarlas.
 */
export interface NotifyInput {
  usuarioId: number;
  tipo: NotificacionTipo;
  mensaje: string;
  url?: string | null;
  tipoObjeto?: string | null;
  objetoId?: number | null;
}

export async function notify(db: Queryable, input: NotifyInput): Promise<void> {
  await db.query(
    `INSERT INTO notificaciones (tipo, mensaje, url, tipo_objeto, objeto_id, usuarios_id_usuarios)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [
      input.tipo,
      input.mensaje,
      input.url ?? null,
      input.tipoObjeto ?? null,
      input.objetoId ?? null,
      input.usuarioId,
    ],
  );
}
