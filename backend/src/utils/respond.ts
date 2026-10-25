import type { Response } from 'express';

/** Envoltura única de éxito: `{ success: true, data }` (master §13.3). */
export function sendData<T>(res: Response, data: T, status = 200): void {
  res.status(status).json({ success: true, data });
}

/** Envoltura de éxito sin cuerpo útil: `{ success: true, message }`. */
export function sendMessage(res: Response, message: string, status = 200): void {
  res.status(status).json({ success: true, message });
}
