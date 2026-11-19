import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatDate, formatRelative, formatTime } from '../../lib/format.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { EmptyState, ErrorState, LoadingState } from '../../components/States.tsx';
import { Toolbar } from '../../components/Toolbar.tsx';
import { useToast } from '../../components/Toast.tsx';
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from '../../queries/notifications.ts';

const TIPOS = ['Tarea', 'Asesoría', 'Seguimiento', 'Solicitud', 'Diagnóstico', 'Evento', 'Sistema'];

/**
 * Bandeja de notificaciones de cualquier rol.
 *
 * Los filtros se envían al servidor (`leida`, `tipo`); la lectura de una ajena
 * responde `404` y aquí se traduce a un aviso, no a una fila fantasma.
 */
export function NotificationsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [leida, setLeida] = useState<'todas' | 'sin-leer' | 'leidas'>('todas');
  const [tipo, setTipo] = useState('');
  const [page, setPage] = useState(1);

  const inbox = useNotifications({
    page,
    pageSize: 25,
    tipo: tipo || undefined,
    leida: leida === 'todas' ? undefined : leida === 'leidas',
  });
  const markRead = useMarkNotificationRead();
  const markAll = useMarkAllNotificationsRead();

  if (!user) return null;

  const open = async (id: number, url: string | null): Promise<void> => {
    try {
      await markRead.mutateAsync(id);
    } catch {
      // Se navega igual: el enlace sigue siendo útil.
    }
    if (url) navigate(url);
  };

  return (
    <>
      <PageHeader
        title="Notificaciones"
        sub="Avisos de tareas, asesorías, seguimiento, solicitudes, diagnóstico y eventos."
        actions={
          <Button
            variant="secundario"
            icon="check"
            loading={markAll.isPending}
            disabled={(inbox.data?.sinLeer ?? 0) === 0}
            onClick={async () => {
              try {
                const result = await markAll.mutateAsync();
                const actualizadas = (result as { actualizadas?: number } | undefined)?.actualizadas ?? 0;
                showToast(
                  actualizadas > 0
                    ? `${actualizadas} notificaciones marcadas como leídas.`
                    : 'No había notificaciones sin leer.',
                  'ok',
                );
              } catch {
                showToast('No fue posible marcar las notificaciones.', 'error');
              }
            }}
          >
            Marcar todo como leído
          </Button>
        }
      />

      <Toolbar>
        <select
          className="filtro"
          aria-label="Estado de lectura"
          value={leida}
          onChange={(event) => {
            setLeida(event.target.value as typeof leida);
            setPage(1);
          }}
        >
          <option value="todas">Todas</option>
          <option value="sin-leer">Sin leer</option>
          <option value="leidas">Leídas</option>
        </select>
        <select
          className="filtro"
          aria-label="Tipo de notificación"
          value={tipo}
          onChange={(event) => {
            setTipo(event.target.value);
            setPage(1);
          }}
        >
          <option value="">Todos los tipos</option>
          {TIPOS.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <span className="chip">{inbox.data?.sinLeer ?? 0} sin leer</span>
      </Toolbar>

      <Card flush>
        {inbox.isPending ? <LoadingState label="Cargando notificaciones…" /> : null}
        {inbox.isError ? (
          <ErrorState error={inbox.error} onRetry={() => void inbox.refetch()} />
        ) : null}
        {inbox.data && inbox.data.items.length === 0 ? (
          <EmptyState
            icon="bell"
            title="No hay notificaciones con este filtro"
            text="Cuando ocurra un cambio en tus tareas, asesorías o solicitudes, aparecerá aquí."
          />
        ) : null}
        {inbox.data && inbox.data.items.length > 0 ? (
          <div>
            {inbox.data.items.map((item) => (
              <div key={item.id} className={item.leida ? 'notif' : 'notif no-leida'}>
                <span className="notif-ico" aria-hidden="true">
                  <Badge state={item.tipo}>{item.tipo}</Badge>
                </span>
                <div className="notif-cuerpo">
                  {item.url ? (
                    <button
                      type="button"
                      className="enlace-texto"
                      onClick={() => void open(item.id, item.url)}
                    >
                      {item.mensaje}
                    </button>
                  ) : (
                    <p>{item.mensaje}</p>
                  )}
                  <time dateTime={item.fecha}>
                    {formatDate(item.fecha)} · {formatTime(item.fecha)} · {formatRelative(item.fecha)}
                  </time>
                </div>
                {!item.leida ? (
                  <Button
                    size="sm"
                    variant="secundario"
                    loading={markRead.isPending}
                    onClick={async () => {
                      try {
                        await markRead.mutateAsync(item.id);
                      } catch {
                        showToast('No fue posible marcar la notificación.', 'error');
                      }
                    }}
                  >
                    Marcar leída
                  </Button>
                ) : (
                  <Badge state="Activo">Leída</Badge>
                )}
              </div>
            ))}
          </div>
        ) : null}
      </Card>

      {inbox.data && inbox.data.total > inbox.data.pageSize ? (
        <div className="paginacion">
          <span>
            Mostrando {(inbox.data.page - 1) * inbox.data.pageSize + 1} a{' '}
            {Math.min(inbox.data.page * inbox.data.pageSize, inbox.data.total)} de{' '}
            {inbox.data.total} notificaciones
          </span>
          <div className="pag">
            <Button
              size="sm"
              icon="izq"
              disabled={inbox.data.page <= 1}
              onClick={() => setPage((value) => Math.max(1, value - 1))}
            >
              Anterior
            </Button>
            <Button
              size="sm"
              iconRight="der"
              disabled={inbox.data.page * inbox.data.pageSize >= inbox.data.total}
              onClick={() => setPage((value) => value + 1)}
            >
              Siguiente
            </Button>
          </div>
        </div>
      ) : null}
    </>
  );
}
