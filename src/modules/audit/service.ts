import { query } from '../../db/pool.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { maskDocument, maskEmail, maskName } from '../../services/masking.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import {
  exportReport,
  listReports,
  type ExportedFile,
  type ReportCatalogItem,
} from '../reports/service.js';
import type { ExportFormat } from '../reports/definition.js';
import type { AuditExpedientesQuery } from './schemas.js';

/**
 * Módulo del auditor (rol 4, P2): solo lectura y exportación.
 *
 * Cada consulta y cada exportación se escriben en `auditoria_eventos` (NFR-007). Los
 * nombres, documentos y correos viajan enmascarados (T38); las cifras son completas,
 * porque el auditor audita el programa, no a las personas.
 */

export interface AuditDashboard {
  generadoEn: string;
  usuarios: {
    total: number;
    porRol: Record<string, number>;
    porEstado: Record<string, number>;
  };
  emprendimientos: {
    total: number;
    porEstado: Record<string, number>;
    conDocente: number;
    sinDocente: number;
  };
  asignaciones: { activas: number; inactivas: number };
  tareas: { total: number; porEstado: Record<string, number> };
  asesorias: { total: number; porEstado: Record<string, number> };
  diagnosticos: { total: number; porEstado: Record<string, number> };
  actas: { total: number; porEstado: Record<string, number> };
  eventos: { total: number; publicados: number; pendientes: number };
  auditoria: { eventos: number; ultimo: string | null };
}

/** `GET /audit/dashboard`: métricas agregadas sin datos personales. */
export async function auditDashboard(): Promise<AuditDashboard> {
  const { rows } = await query<{ data: AuditDashboard }>(
    `SELECT json_build_object(
       'generadoEn', now(),
       'usuarios', json_build_object(
         'total', (SELECT COUNT(*)::int FROM usuarios WHERE fecha_eliminacion IS NULL),
         'porRol', (
           SELECT COALESCE(json_object_agg(r.nombre, COALESCE(x.total, 0)), '{}'::json)
             FROM roles r
             LEFT JOIN (
               SELECT roles_id_roles AS rol, COUNT(*)::int AS total
                 FROM usuarios
                WHERE fecha_eliminacion IS NULL
                GROUP BY 1
             ) x ON x.rol = r.id_roles),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('Activo'), ('Limitado'), ('Inactivo')) e(estado)
             LEFT JOIN (
               SELECT estado, COUNT(*)::int AS total
                 FROM usuarios
                WHERE fecha_eliminacion IS NULL
                GROUP BY 1
             ) x ON x.estado = e.estado)
       ),
       'emprendimientos', json_build_object(
         'total', (SELECT COUNT(*)::int FROM emprendimiento WHERE fecha_eliminacion IS NULL),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('Pendiente'), ('Aprobado'), ('Rechazado')) e(estado)
             LEFT JOIN (
               SELECT estado_aprobacion AS estado, COUNT(*)::int AS total
                 FROM emprendimiento
                WHERE fecha_eliminacion IS NULL
                GROUP BY 1
             ) x ON x.estado = e.estado),
         'conDocente', (
           SELECT COUNT(*)::int
             FROM emprendimiento e
            WHERE e.fecha_eliminacion IS NULL
              AND EXISTS (SELECT 1 FROM asignaciones a
                           WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                             AND a.estado = 'activa')),
         'sinDocente', (
           SELECT COUNT(*)::int
             FROM emprendimiento e
            WHERE e.fecha_eliminacion IS NULL
              AND NOT EXISTS (SELECT 1 FROM asignaciones a
                               WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                                 AND a.estado = 'activa'))
       ),
       'asignaciones', json_build_object(
         'activas', (SELECT COUNT(*)::int FROM asignaciones WHERE estado = 'activa'),
         'inactivas', (SELECT COUNT(*)::int FROM asignaciones WHERE estado = 'inactiva')
       ),
       'tareas', json_build_object(
         'total', (SELECT COUNT(*)::int FROM tareas WHERE fecha_eliminacion IS NULL),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('Pendiente'), ('En curso'), ('En revisión'), ('Completada'),
                          ('Vencida'), ('Devuelta')) e(estado)
             LEFT JOIN (
               SELECT estado, COUNT(*)::int AS total
                 FROM tareas WHERE fecha_eliminacion IS NULL GROUP BY 1
             ) x ON x.estado = e.estado)
       ),
       'asesorias', json_build_object(
         'total', (SELECT COUNT(*)::int FROM asesorias WHERE fecha_eliminacion IS NULL),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('Por agendar'), ('Programada'), ('Confirmada'), ('En curso'),
                          ('Completada'), ('Cancelada')) e(estado)
             LEFT JOIN (
               SELECT estado, COUNT(*)::int AS total
                 FROM asesorias WHERE fecha_eliminacion IS NULL GROUP BY 1
             ) x ON x.estado = e.estado)
       ),
       'diagnosticos', json_build_object(
         'total', (SELECT COUNT(*)::int FROM diagnosticos),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('En progreso'), ('Enviado'), ('Revisado')) e(estado)
             LEFT JOIN (
               SELECT estado, COUNT(*)::int AS total FROM diagnosticos GROUP BY 1
             ) x ON x.estado = e.estado)
       ),
       'actas', json_build_object(
         'total', (SELECT COUNT(*)::int FROM actas),
         'porEstado', (
           SELECT COALESCE(json_object_agg(e.estado, COALESCE(x.total, 0)), '{}'::json)
             FROM (VALUES ('En revisión'), ('Aprobada'), ('Rechazada')) e(estado)
             LEFT JOIN (
               SELECT estado, COUNT(*)::int AS total FROM actas GROUP BY 1
             ) x ON x.estado = e.estado)
       ),
       'eventos', json_build_object(
         'total', (SELECT COUNT(*)::int FROM eventos WHERE fecha_eliminacion IS NULL),
         'publicados', (SELECT COUNT(*)::int FROM eventos
                         WHERE fecha_eliminacion IS NULL AND estado = 'Publicado'),
         'pendientes', (SELECT COUNT(*)::int FROM eventos
                         WHERE fecha_eliminacion IS NULL AND estado = 'Pendiente')
       ),
       'auditoria', json_build_object(
         'eventos', (SELECT COUNT(*)::int FROM auditoria_eventos),
         'ultimo', (SELECT MAX(fecha) FROM auditoria_eventos)
       )
     ) AS data`,
  );

  return rows[0]!.data;
}

/** `GET /audit/reports`: el mismo catálogo del administrador, marcado como enmascarado. */
export async function auditReports(): Promise<{
  items: (ReportCatalogItem & { enmascarado: true })[];
}> {
  const catalog = await listReports();
  return { items: catalog.items.map((item) => ({ ...item, enmascarado: true as const })) };
}

/** `GET /audit/reports/:id/export`: exporta con nombres enmascarados y acción propia. */
export async function auditExport(
  id: string,
  format: ExportFormat,
  filters: { desde?: string; hasta?: string; docenteId?: number },
  actor: SessionUser,
  ip: string | null,
): Promise<ExportedFile> {
  return exportReport(id, format, filters, actor, ip, {
    maskPii: true,
    auditAction: AUDIT_ACTIONS.AUDIT_EXPORT,
  });
}

export interface AuditExpediente {
  id: number;
  codigo: string;
  nombre: string;
  estado: string;
  etapa: string | null;
  sector: string | null;
  sede: string | null;
  avance: number;
  estudiante: {
    nombres: string | null;
    apellidos: string | null;
    documento: string | null;
    correo: string | null;
  };
  docente: { nombres: string | null; apellidos: string | null } | null;
  tareas: { total: number; completadas: number };
  seguimientos: number;
  asesorias: number;
  diagnostico: { estado: string } | null;
  acta: { estado: string } | null;
}

interface ExpedienteRow {
  id_emprendimiento: number;
  codigo: string;
  nombre: string;
  estado_aprobacion: string;
  etapa: string | null;
  sector: string | null;
  sede: string | null;
  avance: number;
  est_nombres: string;
  est_apellidos: string;
  est_documento: string;
  est_correo: string;
  doc_nombres: string | null;
  doc_apellidos: string | null;
  tareas_total: number;
  tareas_completadas: number;
  seguimientos: number;
  asesorias: number;
  diagnostico_estado: string | null;
  acta_estado: string | null;
}

/** `GET /audit/expedientes`: consolidado por emprendimiento con PII enmascarada. */
export async function auditExpedientes(options: AuditExpedientesQuery): Promise<{
  items: AuditExpediente[];
  total: number;
  page: number;
  pageSize: number;
}> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = ['e.fecha_eliminacion IS NULL'];
  if (options.estado) where.push(`e.estado_aprobacion = ${bind(options.estado)}`);
  if (options.docenteId !== undefined) {
    where.push(`asg.usuarios_id_mentor = ${bind(options.docenteId)}`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(`(e.codigo ILIKE ${like} OR e.nombre ILIKE ${like})`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM emprendimiento e
         LEFT JOIN asignaciones asg
           ON asg.emprendimiento_id_emprendimiento = e.id_emprendimiento
          AND asg.estado = 'activa'
         ${whereSql}`,
      countParams,
    ),
    query<ExpedienteRow>(
      `SELECT e.id_emprendimiento, e.codigo, e.nombre, e.estado_aprobacion, e.avance,
              et.nombre AS etapa, sec.nombre AS sector, cu.nombre AS sede,
              est.nombres AS est_nombres, est.apellidos AS est_apellidos,
              est.numero_documento AS est_documento,
              est.correo_institucional AS est_correo,
              doc.nombres AS doc_nombres, doc.apellidos AS doc_apellidos,
              tar.total AS tareas_total, tar.completadas AS tareas_completadas,
              seg.total AS seguimientos, ase.total AS asesorias,
              dia.estado AS diagnostico_estado, act.estado AS acta_estado
         FROM emprendimiento e
         JOIN usuarios est ON est.id_usuarios = e.usuarios_id_usuarios
         LEFT JOIN asignaciones asg
           ON asg.emprendimiento_id_emprendimiento = e.id_emprendimiento
          AND asg.estado = 'activa'
         LEFT JOIN usuarios doc ON doc.id_usuarios = asg.usuarios_id_mentor
         LEFT JOIN etapaemprendimiento et
           ON et.id_etapaemprendimiento = e.etapa_emprendimiento_id_etapa_emprendimiento
         LEFT JOIN sectoreconomico sec
           ON sec.id_sectoreconomico = e.sector_economico_id_sector_economico
         LEFT JOIN centrouniversitarios cu
           ON cu.id_centrouniversitarios = e.centro_universitarios_id_centro_universitarios
         LEFT JOIN LATERAL (
           SELECT COUNT(*)::int AS total,
                  COUNT(*) FILTER (WHERE t.estado = 'Completada')::int AS completadas
             FROM tareas t
            WHERE t.emprendimiento_id_emprendimiento = e.id_emprendimiento
              AND t.fecha_eliminacion IS NULL
         ) tar ON TRUE
         LEFT JOIN LATERAL (
           SELECT COUNT(*)::int AS total
             FROM seguimientos s
            WHERE s.emprendimiento_id_emprendimiento = e.id_emprendimiento
              AND s.fecha_eliminacion IS NULL
         ) seg ON TRUE
         LEFT JOIN LATERAL (
           SELECT COUNT(*)::int AS total
             FROM asesorias a
            WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
              AND a.fecha_eliminacion IS NULL
         ) ase ON TRUE
         LEFT JOIN LATERAL (
           SELECT d.estado
             FROM diagnosticos d
            WHERE d.emprendimiento_id_emprendimiento = e.id_emprendimiento
            ORDER BY d.fecha_diagnostico DESC, d.id_diagnosticos DESC
            LIMIT 1
         ) dia ON TRUE
         LEFT JOIN LATERAL (
           SELECT a.estado
             FROM actas a
            WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
            ORDER BY a.fecha_carga DESC, a.id_acta DESC
            LIMIT 1
         ) act ON TRUE
         ${whereSql}
        ORDER BY e.codigo
        LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  const items = page.rows.map<AuditExpediente>((row) => ({
    id: row.id_emprendimiento,
    codigo: row.codigo,
    nombre: row.nombre,
    estado: row.estado_aprobacion,
    etapa: row.etapa,
    sector: row.sector,
    sede: row.sede,
    avance: row.avance,
    estudiante: {
      nombres: maskName(row.est_nombres),
      apellidos: maskName(row.est_apellidos),
      documento: maskDocument(row.est_documento),
      correo: maskEmail(row.est_correo),
    },
    docente:
      row.doc_nombres === null
        ? null
        : { nombres: maskName(row.doc_nombres), apellidos: maskName(row.doc_apellidos) },
    tareas: { total: row.tareas_total, completadas: row.tareas_completadas },
    seguimientos: row.seguimientos,
    asesorias: row.asesorias,
    diagnostico: row.diagnostico_estado === null ? null : { estado: row.diagnostico_estado },
    acta: row.acta_estado === null ? null : { estado: row.acta_estado },
  }));

  return {
    items,
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

/** Deja rastro de una lectura del auditor (NFR-007). */
export async function logAuditRead(
  actor: SessionUser,
  ip: string | null,
  ruta: string,
  filtros?: unknown,
): Promise<void> {
  await audit(
    { query },
    {
      accion: AUDIT_ACTIONS.AUDIT_READ,
      entidad: 'auditoria',
      entidadId: null,
      valorNuevo: { ruta, filtros: filtros ?? null },
      usuarioId: actor.id,
      ip,
    },
  );
}

/** Salvaguarda para que un id no numérico nunca llegue al servicio de reportes. */
export function assertReportId(id: string | string[] | undefined): string {
  const value = Array.isArray(id) ? id[0] : id;
  if (!value) throw new AppError(404, 'REPORT_NOT_FOUND', 'El reporte solicitado no existe.');
  return value;
}
