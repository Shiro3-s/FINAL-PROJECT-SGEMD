import type { Response } from 'express';

/**
 * Evento mínimo que viaja por el canal en tiempo real.
 *
 * No lleva el cuerpo de la notificación (T21): solo el identificador, el tipo y el
 * contador de no leídas. El cliente invalida su consulta de la bandeja y pide el texto por
 * la API normal, donde el alcance y el saneamiento ya están resueltos.
 */
export interface NotificationEvent {
  notificationId: number;
  tipo: string;
  unreadCount: number;
}

/**
 * Transporte de notificaciones en tiempo real (D2).
 *
 * La implementación es SSE, pero los módulos solo conocen esta interfaz: sustituirla por
 * un WebSocket no toca ni la bandeja ni los servicios de negocio.
 */
export interface NotificationChannel {
  /** Abre el flujo del usuario y devuelve la función que lo cierra. */
  subscribe(usuarioId: number, res: Response, unreadCount: number): () => void;
  /** Publica un evento **solo** en las conexiones abiertas de ese usuario. */
  publish(usuarioId: number, event: NotificationEvent): void;
}
