import { Link, useNavigate } from 'react-router-dom';
import type { RoleKey } from '../api/types.ts';
import { formatRelative } from '../lib/format.ts';
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from '../queries/notifications.ts';
import { Badge } from './Badge.tsx';
import { Button } from './Button.tsx';
import { Drawer } from './Drawer.tsx';
import { Icon } from './Icon.tsx';
import { EmptyState, ErrorState, LoadingState } from './States.tsx';
import { useToast } from './Toast.tsx';

interface NotificationDrawerProps {
  open: boolean;
  onClose: () => void;
  role: RoleKey;
}

/**
 * Drawer de la campana. Reutiliza la bandeja real (`GET /notifications`) y el
 * contador del SSE: el evento solo invalida, el texto llega por la consulta.
 */
export function NotificationDrawer({ open, onClose, role }: NotificationDrawerProps) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const inbox = useNotifications({ page: 1, pageSize: 8 });
  const markRead = useMarkNotificationRead();
  const markAll = useMarkAllNotificationsRead();

  const openNotification = async (id: number, url: string | null): Promise<void> => {
    try {
      await markRead.mutateAsync(id);
    } catch {
      // Si falla el marcado, el enlace sigue siendo útil: no se bloquea la navegación.
    }
    onClose();
    if (url) navigate(url);
  };

  return (
    <Drawer
      open={open}
      title="Notificaciones"
      onClose={onClose}
      footer={
        <Link className="btn btn-secundario" to={`/${role}/notificaciones`} onClick={onClose}>
          Ver todas las notificaciones
        </Link>
      }
    >
      {inbox.isPending ? <LoadingState label="Cargando notificaciones…" /> : null}
      {inbox.isError ? (
        <div style={{ padding: 16 }}>
          <ErrorState error={inbox.error} onRetry={() => void inbox.refetch()} />
        </div>
      ) : null}
      {inbox.data && inbox.data.items.length === 0 ? (
        <div style={{ padding: 16 }}>
          <EmptyState
            icon="bell"
            title="Sin notificaciones"
            text="Aquí aparecerán los avisos de tareas, asesorías, seguimiento y solicitudes."
          />
        </div>
      ) : null}
      {inbox.data && inbox.data.items.length > 0 ? (
        <>
          <ul className="sg-drawer-lista">
            {inbox.data.items.map((item) => (
              <li key={item.id}>
                <Icon name="bell" size={15} />
                <div style={{ flex: 1 }}>
                  <div className="fila-acciones" style={{ justifyContent: 'space-between', gap: 8 }}>
                    <Badge>{item.tipo}</Badge>
                    <span className="nota-foot" style={{ margin: 0 }}>
                      {formatRelative(item.fecha)}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="enlace-texto"
                    onClick={() => void openNotification(item.id, item.url)}
                  >
                    {item.mensaje}
                  </button>
                </div>
                {!item.leida ? <span className="punto-no-leido" aria-label="Sin leer" /> : null}
              </li>
            ))}
          </ul>
          <div style={{ padding: '0 16px 12px' }}>
            <Button
              variant="secundario"
              size="sm"
              loading={markAll.isPending}
              disabled={inbox.data.sinLeer === 0}
              onClick={async () => {
                try {
                  await markAll.mutateAsync();
                  showToast('Notificaciones marcadas como leídas.', 'ok');
                } catch {
                  showToast('No fue posible marcar las notificaciones.', 'error');
                }
              }}
            >
              Marcar todas como leídas
            </Button>
          </div>
        </>
      ) : null}
    </Drawer>
  );
}
