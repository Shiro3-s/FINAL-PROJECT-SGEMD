import type { Response } from 'express';

/** Envoltura única de éxito: `{ success: true, data }` (master §13.3). */
export function sendData<T>(res: Response, data: T, status = 200): void {
  res.status(status).json({ success: true, data });
}

/** Envoltura de éxito sin cuerpo útil: `{ success: true, message }`. */
export function sendMessage(res: Response, message: string, status = 200): void {
  res.status(status).json({ success: true, message });
}

/** Archivo descargable: nunca se cachea y el navegador no adivina el tipo. */
export function sendDownload(
  res: Response,
  file: { filename: string; contentType: string; body: Buffer },
): void {
  res.setHeader('Content-Type', file.contentType);
  res.setHeader('Content-Disposition', `attachment; filename="${file.filename}"`);
  res.setHeader('Content-Length', String(file.body.length));
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.end(file.body);
}
