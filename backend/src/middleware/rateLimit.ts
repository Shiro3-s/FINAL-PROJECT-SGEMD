import type { RequestHandler } from 'express';
import { AppError } from '../utils/AppError.js';

interface Bucket {
  hits: number[];
}

/**
 * Límite de peticiones en memoria, por clave (IP real detrás de Caddy + ruta).
 *
 * El master §15 exige límites en login, registro, verificación/reenvío de OTP y
 * recuperación de contraseña, pero **no fija umbrales**: los valores son la suposición
 * P-12 y se ajustan por entorno. Una sola instancia de backend (§12), así que la memoria
 * es suficiente; si algún día hay réplicas, se sustituye por un almacén compartido.
 */
export interface RateLimitOptions {
  windowMs: number;
  max: number;
  /** Prefijo para separar cubos de endpoints distintos. */
  scope: string;
  /** Añade algo a la clave además de la IP (por ejemplo el correo). */
  extraKey?: (req: { body?: unknown }) => string | undefined;
}

const buckets = new Map<string, Bucket>();

/** Limpieza perezosa: evita que el mapa crezca sin control en un proceso largo. */
function prune(now: number, windowMs: number): void {
  for (const [key, bucket] of buckets) {
    bucket.hits = bucket.hits.filter((hit) => now - hit < windowMs);
    if (bucket.hits.length === 0) buckets.delete(key);
  }
}

export function rateLimit(options: RateLimitOptions): RequestHandler {
  const { windowMs, max, scope, extraKey } = options;

  return (req, res, next) => {
    const now = Date.now();
    prune(now, windowMs);

    const extra = extraKey?.(req) ?? '';
    const key = `${scope}:${req.ip ?? 'desconocida'}:${extra}`;
    const bucket = buckets.get(key) ?? { hits: [] };

    bucket.hits = bucket.hits.filter((hit) => now - hit < windowMs);

    if (bucket.hits.length >= max) {
      const oldest = bucket.hits[0] ?? now;
      const retryAfter = Math.max(1, Math.ceil((windowMs - (now - oldest)) / 1000));
      buckets.set(key, bucket);
      res.setHeader('Retry-After', String(retryAfter));
      next(
        new AppError(
          429,
          'RATE_LIMITED',
          'Demasiados intentos. Espera un momento y vuelve a intentarlo.',
        ),
      );
      return;
    }

    bucket.hits.push(now);
    buckets.set(key, bucket);
    next();
  };
}

/** Solo para pruebas: vacía los cubos entre casos. */
export function resetRateLimits(): void {
  buckets.clear();
}
