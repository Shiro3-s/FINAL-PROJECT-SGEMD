import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import {
  apiGet,
  apiSend,
  subscribeToNotifications,
  withQuery,
} from '../api/client.ts';
import type { NotificationItem } from '../api/types.ts';

/**
 * Bandeja y contador de notificaciones.
 *
 * El texto de un aviso NUNCA llega por SSE: el evento solo trae id, tipo y
 * contador. Al recibirlo se invalida la lista y la consulta normal trae el
 * mensaje ya saneado por el servidor (T21).
 */
export interface NotificationPage {
  items: NotificationItem[];
  total: number;
  page: number;
  pageSize: number;
  sinLeer: number;
}

export const notificationKeys = {
  all: ['notifications'] as const,
  list: (filters: NotificationFilters) => ['notifications', 'list', filters] as const,
  unread: ['notifications', 'unread'] as const,
};

export interface NotificationFilters {
  page: number;
  pageSize?: number;
  leida?: boolean;
  tipo?: string;
}

export function useNotifications(filters: NotificationFilters) {
  return useQuery({
    queryKey: notificationKeys.list(filters),
    queryFn: () =>
      apiGet<NotificationPage>(
        withQuery('/notifications', {
          page: filters.page,
          pageSize: filters.pageSize ?? 25,
          leida: filters.leida === undefined ? undefined : String(filters.leida),
          tipo: filters.tipo,
        }),
      ),
  });
}

/** Contador de la campana. Se hidrata con el evento `ready` del flujo SSE. */
export function useUnreadCount() {
  return useQuery({
    queryKey: notificationKeys.unread,
    queryFn: async () => {
      const page = await apiGet<NotificationPage>(
        withQuery('/notifications', { page: 1, pageSize: 1 }),
      );
      return page.sinLeer;
    },
    staleTime: 30_000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiSend<NotificationItem & { sinLeer: number }>(
        'PUT',
        `/notifications/${id}/read`,
      ),
    onSuccess: (notification) => {
      queryClient.setQueryData(notificationKeys.unread, notification.sinLeer);
      void queryClient.invalidateQueries({ queryKey: notificationKeys.all });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiSend<unknown>('PUT', '/notifications/read-all'),
    onSuccess: () => {
      queryClient.setQueryData(notificationKeys.unread, 0);
      void queryClient.invalidateQueries({ queryKey: notificationKeys.all });
    },
  });
}

/**
 * Abre el flujo SSE mientras haya sesión. El `EventSource` reintenta solo si la
 * conexión se cae; aquí solo se limpia al desmontar o cerrar sesión.
 */
export function useNotificationStream(enabled: boolean): void {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!enabled) return;
    const close = subscribeToNotifications({
      onReady: (unreadCount) => {
        queryClient.setQueryData(notificationKeys.unread, unreadCount);
      },
      onNotification: (event) => {
        queryClient.setQueryData(notificationKeys.unread, event.unreadCount);
        void queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      },
    });
    return close;
  }, [enabled, queryClient]);
}
