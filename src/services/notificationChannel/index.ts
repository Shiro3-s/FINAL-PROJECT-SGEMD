import { sseNotificationChannel } from './sse.js';
import type { NotificationChannel } from './types.js';

export type { NotificationChannel, NotificationEvent } from './types.js';

/**
 * Canal activo de la aplicación. Es el único punto que los módulos importan: si mañana se
 * cambia SSE por otro transporte, solo cambia esta línea.
 */
export const notificationChannel: NotificationChannel = sseNotificationChannel;
