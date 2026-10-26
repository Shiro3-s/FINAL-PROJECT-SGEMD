/**
 * Formatos de fecha, hora y tamaño.
 *
 * El backend guarda todo en UTC y el programa opera en `America/Bogota`; la
 * conversión se hace al pintar, nunca en la lógica de consulta. No se usa
 * `toLocaleString()` sin locale explícito: el resultado depende del navegador.
 */
const LOCALE = 'es-CO';
const TIME_ZONE = 'America/Bogota';

const DATE = new Intl.DateTimeFormat(LOCALE, {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  timeZone: TIME_ZONE,
});

const DATE_LONG = new Intl.DateTimeFormat(LOCALE, {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: TIME_ZONE,
});

const DATE_TIME = new Intl.DateTimeFormat(LOCALE, {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: TIME_ZONE,
});

const TIME = new Intl.DateTimeFormat(LOCALE, {
  hour: '2-digit',
  minute: '2-digit',
  timeZone: TIME_ZONE,
});

function parse(value: string | Date | null | undefined): Date | null {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** `12 nov 2024` */
export function formatDate(value: string | Date | null | undefined): string {
  const date = parse(value);
  return date ? DATE.format(date) : '—';
}

/** `12 de noviembre de 2024` */
export function formatDateLong(value: string | Date | null | undefined): string {
  const date = parse(value);
  return date ? DATE_LONG.format(date) : '—';
}

/** `12 nov 2024, 18:20` */
export function formatDateTime(value: string | Date | null | undefined): string {
  const date = parse(value);
  return date ? DATE_TIME.format(date) : '—';
}

/** `18:20` */
export function formatTime(value: string | Date | null | undefined): string {
  const date = parse(value);
  return date ? TIME.format(date) : '—';
}

/** `Hace 5 min`, `Hace 2 h`, `Hace 3 d`; a partir de una semana, la fecha. */
export function formatRelative(value: string | Date | null | undefined): string {
  const date = parse(value);
  if (!date) return '—';
  const minutes = Math.floor((Date.now() - date.getTime()) / 60_000);
  if (minutes < 1) return 'Ahora';
  if (minutes < 60) return `Hace ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `Hace ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `Hace ${days} d`;
  return formatDate(date);
}

const BYTE_UNITS = ['B', 'KB', 'MB', 'GB'];

/** `2,4 MB`. */
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return '—';
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < BYTE_UNITS.length - 1) {
    value /= 1024;
    unit += 1;
  }
  const decimals = unit === 0 ? 0 : 1;
  return `${value.toFixed(decimals).replace('.', ',')} ${BYTE_UNITS[unit]}`;
}
