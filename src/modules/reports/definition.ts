import { query } from '../../db/pool.js';

/**
 * Catálogo de reportes (FR-010, FR-017, T22).
 *
 * Cada reporte es **una consulta SQL** que devuelve una fila por hecho exportable. El
 * mismo conjunto alimenta CSV, XLSX y PDF, de modo que las cifras del archivo y las de la
 * pantalla no pueden divergir: no hay cálculos en el exportador.
 *
 * El periodo (`desde`/`hasta`) se aplica a la fecha propia del reporte. `emprendimientos`
 * no lo admite porque `emprendimiento` no tiene columna de creación en el diagrama v2:
 * inventar una fecha sería un dato falso (P-44).
 */

export type ReportId = 'seguimiento' | 'asesorias' | 'emprendimientos' | 'diagnosticos';
export type ExportFormat = 'csv' | 'xlsx' | 'pdf';

export const REPORT_IDS: readonly ReportId[] = [
  'seguimiento',
  'asesorias',
  'emprendimientos',
  'diagnosticos',
];

export interface ReportFilters {
  desde?: string;
  hasta?: string;
  docenteId?: number;
}

export type ReportValue = string | number | null;
export type ReportRow = Record<string, ReportValue>;

export interface ReportColumn {
  key: string;
  header: string;
  /** Peso relativo en el PDF y ancho en caracteres para Excel. */
  width: number;
}

export interface ReportDefinition {
  id: ReportId;
  nombre: string;
  descripcion: string;
  formatos: readonly ExportFormat[];
  /** `false` cuando la entidad no tiene fecha propia (el filtro se oculta). */
  periodo: boolean;
  filtroDocente: boolean;
  columns: readonly ReportColumn[];
  rows(filters: ReportFilters): Promise<ReportRow[]>;
}

interface Bind {
  params: unknown[];
  bind: (value: unknown) => string;
}

function binder(): Bind {
  const params: unknown[] = [];
  return {
    params,
    bind: (value: unknown) => {
      params.push(value);
      return `$${params.length}`;
    },
  };
}

/** Condición del periodo sobre una fecha ya normalizada a `date` o `timestamptz`. */
function period(sql: Bind, column: string, filters: ReportFilters): string[] {
  const where: string[] = [];
  if (filters.desde) where.push(`${column} >= ${sql.bind(filters.desde)}::date`);
  if (filters.hasta) where.push(`${column} < (${sql.bind(filters.hasta)}::date + INTERVAL '1 day')`);
  return where;
}

const MENTOR_JOIN = `
  LEFT JOIN asignaciones asg
    ON asg.emprendimiento_id_emprendimiento = e.id_emprendimiento
   AND asg.estado = 'activa'
  LEFT JOIN usuarios mentor
    ON mentor.id_usuarios = asg.usuarios_id_mentor`;

const SEGUIMIENTO: ReportDefinition = {
  id: 'seguimiento',
  nombre: 'Seguimiento',
  descripcion: 'Avances de fase y comentarios con su calificación por emprendimiento.',
  formatos: ['csv', 'xlsx', 'pdf'],
  periodo: true,
  filtroDocente: true,
  columns: [
    { key: 'codigo', header: 'Código', width: 12 },
    { key: 'emprendimiento', header: 'Emprendimiento', width: 24 },
    { key: 'estudiante', header: 'Estudiante', width: 24 },
    { key: 'docente', header: 'Docente', width: 24 },
    { key: 'fase', header: 'Fase', width: 18 },
    { key: 'tipo', header: 'Tipo', width: 16 },
    { key: 'fecha', header: 'Fecha', width: 12 },
    { key: 'puntaje', header: 'Puntaje', width: 9 },
    { key: 'estadoRevision', header: 'Estado de revisión', width: 16 },
    { key: 'descripcion', header: 'Descripción', width: 40 },
  ],
  async rows(filters) {
    const sql = binder();
    const where = ['s.fecha_eliminacion IS NULL', 'e.fecha_eliminacion IS NULL'];
    where.push(...period(sql, 's.fecha_seguimiento', filters));
    if (filters.docenteId !== undefined) {
      where.push(`asg.usuarios_id_mentor = ${sql.bind(filters.docenteId)}`);
    }

    const { rows } = await query<ReportRow>(
      `SELECT e.codigo,
              e.nombre AS emprendimiento,
              est.nombres || ' ' || est.apellidos AS estudiante,
              mentor.nombres || ' ' || mentor.apellidos AS docente,
              fp.nombre AS fase,
              s.tipo_seguimiento AS tipo,
              to_char(s.fecha_seguimiento AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
              s.puntaje,
              s.estado_revision AS "estadoRevision",
              s.descripcion
         FROM seguimientos s
         JOIN emprendimiento e ON e.id_emprendimiento = s.emprendimiento_id_emprendimiento
         JOIN usuarios est ON est.id_usuarios = e.usuarios_id_usuarios
         ${MENTOR_JOIN}
         LEFT JOIN faseplan fp ON fp.id_faseplan = s.fase_plan_id_fase_plan
        WHERE ${where.join(' AND ')}
        ORDER BY s.fecha_seguimiento DESC, s.id_seguimientos DESC`,
      sql.params,
    );
    return rows;
  },
};

const ASESORIAS: ReportDefinition = {
  id: 'asesorias',
  nombre: 'Asesorías',
  descripcion: 'Uso y respuesta del servicio de asesorías, con docente y estado.',
  formatos: ['csv', 'xlsx', 'pdf'],
  periodo: true,
  filtroDocente: true,
  columns: [
    { key: 'codigo', header: 'Código', width: 12 },
    { key: 'tema', header: 'Tema', width: 32 },
    { key: 'estado', header: 'Estado', width: 14 },
    { key: 'fecha', header: 'Fecha', width: 12 },
    { key: 'horaInicio', header: 'Inicio', width: 8 },
    { key: 'horaFin', header: 'Fin', width: 8 },
    { key: 'modalidad', header: 'Modalidad', width: 14 },
    { key: 'docente', header: 'Docente', width: 24 },
    { key: 'estudiante', header: 'Estudiante', width: 24 },
    { key: 'emprendimiento', header: 'Emprendimiento', width: 24 },
    { key: 'lugarEnlace', header: 'Lugar o enlace', width: 26 },
  ],
  async rows(filters) {
    const sql = binder();
    const where = ['a.fecha_eliminacion IS NULL', 'e.fecha_eliminacion IS NULL'];
    where.push(...period(sql, 'a.fecha_asesoria', filters));
    if (filters.docenteId !== undefined) {
      where.push(`a.usuarios_id_docentes = ${sql.bind(filters.docenteId)}`);
    }

    const { rows } = await query<ReportRow>(
      `SELECT 'ASES-' || lpad(a.id_asesorias::text, 3, '0') AS codigo,
              a.tema,
              a.estado,
              to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
              to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'HH24:MI') AS "horaInicio",
              to_char(fyh.hora_fin, 'HH24:MI') AS "horaFin",
              m.nombre AS modalidad,
              doc.nombres || ' ' || doc.apellidos AS docente,
              est.nombres || ' ' || est.apellidos AS estudiante,
              e.nombre AS emprendimiento,
              a.lugar_enlace AS "lugarEnlace"
         FROM asesorias a
         JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
         JOIN usuarios est ON est.id_usuarios = a.usuarios_id_usuarios
         LEFT JOIN usuarios doc ON doc.id_usuarios = a.usuarios_id_docentes
         LEFT JOIN modalidad m ON m.id_modalidad = a.modalidad_id_modalidad
         LEFT JOIN fecha_y_horarios fyh
           ON fyh.id_fecha_y_horarios = a.fecha_y_horarios_id_fecha_y_horarios
        WHERE ${where.join(' AND ')}
        ORDER BY a.fecha_asesoria DESC NULLS LAST, a.id_asesorias DESC`,
      sql.params,
    );
    return rows;
  },
};

const EMPRENDIMIENTOS: ReportDefinition = {
  id: 'emprendimientos',
  nombre: 'Emprendimientos',
  descripcion: 'Inventario completo con sector, etapa, sede y docente asignado.',
  formatos: ['csv', 'xlsx', 'pdf'],
  periodo: false,
  filtroDocente: true,
  columns: [
    { key: 'codigo', header: 'Código', width: 12 },
    { key: 'nombre', header: 'Emprendimiento', width: 28 },
    { key: 'estado', header: 'Estado', width: 12 },
    { key: 'sector', header: 'Sector', width: 16 },
    { key: 'etapa', header: 'Etapa', width: 22 },
    { key: 'sede', header: 'Sede', width: 16 },
    { key: 'estudiante', header: 'Estudiante', width: 24 },
    { key: 'docente', header: 'Docente', width: 24 },
    { key: 'avance', header: 'Avance (%)', width: 10 },
    { key: 'paralelo', header: 'Paralelo', width: 9 },
  ],
  async rows(filters) {
    const sql = binder();
    const where = ['e.fecha_eliminacion IS NULL'];
    if (filters.docenteId !== undefined) {
      where.push(`asg.usuarios_id_mentor = ${sql.bind(filters.docenteId)}`);
    }

    const { rows } = await query<ReportRow>(
      `SELECT e.codigo,
              e.nombre,
              e.estado_aprobacion AS estado,
              sec.nombre AS sector,
              et.nombre AS etapa,
              cu.nombre AS sede,
              est.nombres || ' ' || est.apellidos AS estudiante,
              mentor.nombres || ' ' || mentor.apellidos AS docente,
              e.avance,
              CASE WHEN e.es_paralelo THEN 'Sí' ELSE 'No' END AS paralelo
         FROM emprendimiento e
         JOIN usuarios est ON est.id_usuarios = e.usuarios_id_usuarios
         ${MENTOR_JOIN}
         LEFT JOIN sectoreconomico sec
           ON sec.id_sectoreconomico = e.sector_economico_id_sector_economico
         LEFT JOIN etapaemprendimiento et
           ON et.id_etapaemprendimiento = e.etapa_emprendimiento_id_etapa_emprendimiento
         LEFT JOIN centrouniversitarios cu
           ON cu.id_centrouniversitarios = e.centro_universitarios_id_centro_universitarios
        WHERE ${where.join(' AND ')}
        ORDER BY e.codigo`,
      sql.params,
    );
    return rows;
  },
};

const DIAGNOSTICOS: ReportDefinition = {
  id: 'diagnosticos',
  nombre: 'Diagnósticos',
  descripcion:
    'Estado y avance del diagnóstico por estudiante. Sin rúbrica no hay puntaje (AQ-09).',
  formatos: ['csv', 'xlsx', 'pdf'],
  periodo: true,
  filtroDocente: true,
  columns: [
    { key: 'codigo', header: 'Código', width: 12 },
    { key: 'emprendimiento', header: 'Emprendimiento', width: 24 },
    { key: 'estudiante', header: 'Estudiante', width: 24 },
    { key: 'docente', header: 'Docente', width: 24 },
    { key: 'fecha', header: 'Fecha', width: 12 },
    { key: 'estado', header: 'Estado', width: 12 },
    { key: 'respondidas', header: 'Respondidas', width: 11 },
    { key: 'totalPreguntas', header: 'Total', width: 8 },
    { key: 'puntaje', header: 'Puntaje', width: 9 },
    { key: 'observacion', header: 'Observación', width: 34 },
  ],
  async rows(filters) {
    const sql = binder();
    const where = ['e.fecha_eliminacion IS NULL'];
    where.push(...period(sql, 'd.fecha_diagnostico', filters));
    if (filters.docenteId !== undefined) {
      where.push(`asg.usuarios_id_mentor = ${sql.bind(filters.docenteId)}`);
    }

    const { rows } = await query<ReportRow>(
      `SELECT e.codigo,
              e.nombre AS emprendimiento,
              est.nombres || ' ' || est.apellidos AS estudiante,
              mentor.nombres || ' ' || mentor.apellidos AS docente,
              to_char(d.fecha_diagnostico AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
              d.estado,
              (SELECT COUNT(*)::int
                 FROM respuestas_diagnostico r
                WHERE r.diagnosticos_id_diagnosticos = d.id_diagnosticos) AS respondidas,
              (SELECT COUNT(*)::int
                 FROM preguntas_diagnostico p
                WHERE p.activa = TRUE) AS "totalPreguntas",
              d.puntaje_total AS puntaje,
              CASE WHEN d.puntaje_total IS NULL
                   THEN 'Sin rúbrica configurada (AQ-09)' ELSE '' END AS observacion
         FROM diagnosticos d
         JOIN emprendimiento e ON e.id_emprendimiento = d.emprendimiento_id_emprendimiento
         JOIN usuarios est ON est.id_usuarios = e.usuarios_id_usuarios
         ${MENTOR_JOIN}
        WHERE ${where.join(' AND ')}
        ORDER BY d.fecha_diagnostico DESC, d.id_diagnosticos DESC`,
      sql.params,
    );
    return rows;
  },
};

export const REPORTS: Record<ReportId, ReportDefinition> = {
  seguimiento: SEGUIMIENTO,
  asesorias: ASESORIAS,
  emprendimientos: EMPRENDIMIENTOS,
  diagnosticos: DIAGNOSTICOS,
};
