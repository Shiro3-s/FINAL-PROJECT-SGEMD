/**
 * Fechas del programa en `America/Bogota` (master §15: se guarda en UTC, se muestra en
 * Bogotá). Se usa `Intl` con la zona explícita, nunca la zona del contenedor, para que un
 * despliegue en otro huso no cambie el nombre de un respaldo ni la fecha de un reporte.
 */
export interface BogotaParts {
  year: string;
  month: string;
  day: string;
  hour: string;
  minute: string;
  second: string;
}

export function bogotaParts(date: Date = new Date()): BogotaParts {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  const values = new Map(
    formatter
      .formatToParts(date)
      .filter((part) => part.type !== 'literal')
      .map((part) => [part.type, part.value]),
  );

  return {
    year: values.get('year') ?? '0000',
    month: values.get('month') ?? '00',
    day: values.get('day') ?? '00',
    hour: values.get('hour') ?? '00',
    minute: values.get('minute') ?? '00',
    second: values.get('second') ?? '00',
  };
}

/** `YYYYMMDD` de Bogotá (nombres de archivo y códigos). */
export function bogotaDateStamp(date: Date = new Date()): string {
  const parts = bogotaParts(date);
  return `${parts.year}${parts.month}${parts.day}`;
}

/** `YYYYMMDD-HHMM` de Bogotá (código de respaldo `BKP-…`). */
export function bogotaMinuteStamp(date: Date = new Date()): string {
  const parts = bogotaParts(date);
  return `${parts.year}${parts.month}${parts.day}-${parts.hour}${parts.minute}`;
}

/** `YYYY-MM-DD HH:mm` de Bogotá (metadatos de un archivo exportado). */
export function bogotaReadable(date: Date = new Date()): string {
  const parts = bogotaParts(date);
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
}
