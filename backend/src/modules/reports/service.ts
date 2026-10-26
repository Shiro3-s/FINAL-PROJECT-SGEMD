import { query } from '../../db/pool.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { maskName } from '../../services/masking.js';
import { AppError } from '../../utils/AppError.js';
import { bogotaDateStamp, bogotaReadable } from '../../utils/dates.js';
import type { SessionUser } from '../auth/types.js';
import {
  REPORTS,
  REPORT_IDS,
  type ExportFormat,
  type ReportFilters,
  type ReportId,
  type ReportRow,
} from './definition.js';
import {
  contentTypeOf,
  extensionOf,
  toCsv,
  toPdf,
  toXlsx,
  type ExportMeta,
} from './exporters.js';

/**
 * Servicio de reportes (FR-010, FR-017).
 *
 * El catálogo declara qué reportes existen, qué formatos aceptan y si el periodo tiene
 * sentido. La exportación audita siempre: un archivo con datos de estudiantes no puede
 * salir del sistema sin rastro (NFR-007, T24).
 */

export interface ReportCatalogItem {
  id: ReportId;
  nombre: string;
  descripcion: string;
  formatos: readonly ExportFormat[];
  periodo: boolean;
  filtroDocente: boolean;
  columnas: { key: string; header: string }[];
  ultimaGeneracion: string | null;
}

export interface ExportedFile {
  filename: string;
  contentType: string;
  body: Buffer;
}

/** Columnas con nombre de persona: el auditor las recibe parcialmente enmascaradas (T38). */
const PERSON_COLUMNS = new Set(['estudiante', 'docente']);

function maskRows(rows: ReportRow[]): ReportRow[] {
  return rows.map((row) => {
    const masked: ReportRow = { ...row };
    for (const key of PERSON_COLUMNS) {
      const value = masked[key];
      if (typeof value === 'string' && value !== '') masked[key] = maskName(value);
    }
    return masked;
  });
}

/** `GET /reports`: catálogo con la fecha de la última exportación de cada reporte. */
export async function listReports(): Promise<{ items: ReportCatalogItem[] }> {
  const { rows } = await query<{ reporte: string; fecha: Date }>(
    `SELECT valor_nuevo->>'reporte' AS reporte, MAX(fecha) AS fecha
       FROM auditoria_eventos
      WHERE accion = ANY($1)
        AND valor_nuevo->>'reporte' IS NOT NULL
      GROUP BY 1`,
    [[AUDIT_ACTIONS.EXPORT_REPORT, AUDIT_ACTIONS.AUDIT_EXPORT]],
  );

  const last = new Map(rows.map((row) => [row.reporte, row.fecha.toISOString()]));

  return {
    items: REPORT_IDS.map((id) => {
      const definition = REPORTS[id];
      return {
        id: definition.id,
        nombre: definition.nombre,
        descripcion: definition.descripcion,
        formatos: definition.formatos,
        periodo: definition.periodo,
        filtroDocente: definition.filtroDocente,
        columnas: definition.columns.map((column) => ({
          key: column.key,
          header: column.header,
        })),
        ultimaGeneracion: last.get(id) ?? null,
      };
    }),
  };
}

interface TeacherRow {
  nombres: string;
  apellidos: string;
}

function filtersLabel(filters: ReportFilters, definitionPeriod: boolean, teacher: TeacherRow | null): string {
  const parts: string[] = [];

  if (definitionPeriod) {
    if (filters.desde && filters.hasta) parts.push(`Periodo ${filters.desde} a ${filters.hasta}`);
    else if (filters.desde) parts.push(`Desde ${filters.desde}`);
    else if (filters.hasta) parts.push(`Hasta ${filters.hasta}`);
    else parts.push('Todo el periodo');
  }

  parts.push(teacher ? `Docente ${teacher.nombres} ${teacher.apellidos}` : 'Todos los docentes');

  return parts.join(' · ');
}

export interface ExportOptions {
  /** El auditor ve nombres parciales y el evento de auditoría es distinto (T38). */
  maskPii?: boolean;
  /** Rol que exporta, solo para la acción de auditoría. */
  auditAction?: string;
}

/**
 * `GET /reports/:id/export` y `GET /audit/reports/:id/export`.
 *
 * Genera el archivo en memoria (los reportes del MVP son pequeños) y audita la salida.
 * Un periodo invertido o un `docenteId` que no es docente responde `400` antes de consultar.
 */
export async function exportReport(
  id: string,
  format: ExportFormat,
  filters: ReportFilters,
  actor: SessionUser,
  ip: string | null,
  options: ExportOptions = {},
): Promise<ExportedFile> {
  const definition = (REPORTS as Record<string, (typeof REPORTS)[ReportId] | undefined>)[id];
  if (!definition) {
    throw new AppError(404, 'REPORT_NOT_FOUND', 'El reporte solicitado no existe.');
  }

  if (!definition.formatos.includes(format)) {
    throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', {
      format: 'El formato no está disponible para este reporte',
    });
  }

  if (!definition.periodo && (filters.desde || filters.hasta)) {
    throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', {
      desde: 'Este reporte no admite periodo: la entidad no tiene fecha propia',
    });
  }

  if (filters.desde && filters.hasta && filters.desde > filters.hasta) {
    throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', {
      desde: 'La fecha inicial no puede ser posterior a la final',
    });
  }

  let teacher: TeacherRow | null = null;
  if (filters.docenteId !== undefined) {
    const { rows } = await query<TeacherRow>(
      `SELECT nombres, apellidos
         FROM usuarios
        WHERE id_usuarios = $1
          AND roles_id_roles = 3
          AND fecha_eliminacion IS NULL`,
      [filters.docenteId],
    );
    teacher = rows[0] ?? null;
    if (!teacher) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', {
        docenteId: 'El docente no existe',
      });
    }
  }

  const rawRows = await definition.rows(filters);
  const rows = options.maskPii ? maskRows(rawRows) : rawRows;

  const meta: ExportMeta = {
    titulo: definition.nombre,
    descripcion: definition.descripcion,
    filtros: filtersLabel(filters, definition.periodo, teacher),
    generadoEn: bogotaReadable(),
    actor: `${actor.nombres} ${actor.apellidos}`.trim(),
  };

  let body: Buffer;
  switch (format) {
    case 'csv':
      body = toCsv(definition.columns, rows);
      break;
    case 'xlsx':
      body = await toXlsx(definition.columns, rows, meta);
      break;
    case 'pdf':
      body = await toPdf(definition.columns, rows, meta);
      break;
  }

  await audit(
    { query },
    {
      accion: options.auditAction ?? AUDIT_ACTIONS.EXPORT_REPORT,
      entidad: 'reportes',
      entidadId: null,
      valorNuevo: {
        reporte: definition.id,
        formato: format,
        filtros: filters,
        filas: rows.length,
        enmascarado: options.maskPii === true,
      },
      usuarioId: actor.id,
      ip,
    },
  );

  return {
    filename: `reporte-${definition.id}-${bogotaDateStamp()}.${extensionOf(format)}`,
    contentType: contentTypeOf(format),
    body,
  };
}
