/**
 * Error de aplicación con código estable y estado HTTP. Es el único tipo que el
 * manejador de errores traduce a la envoltura de la API.
 */
export class AppError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields?: Record<string, string>;
  /** Segundos para `Retry-After` en respuestas 429. */
  readonly retryAfter?: number;

  constructor(
    status: number,
    code: string,
    message: string,
    fields?: Record<string, string>,
    retryAfter?: number,
  ) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.code = code;
    this.fields = fields;
    this.retryAfter = retryAfter;
  }
}
