import { query } from '../../db/pool.js';
import type { SessionUser } from '../auth/types.js';

/**
 * Tableros por rol (FR-010, T22).
 *
 * **Una sola consulta agregada por tablero.** Nada se cuenta en JavaScript ni se pide una
 * fila por emprendimiento: cada cifra sale de un `COUNT`/`AVG` de PostgreSQL, y el
 * resultado viaja como un único objeto JSON. Así el tablero no puede divergir de la base y
 * no hay N+1 (T22 cuenta las consultas).
 *
 * El alcance se resuelve en el `WHERE`, no en el cliente: el docente solo ve lo asignado,
 * el estudiante solo lo suyo.
 */

const MONTH_LABELS = [
  'ene',
  'feb',
  'mar',
  'abr',
  'may',
  'jun',
  'jul',
  'ago',
  'sep',
  'oct',
  'nov',
  'dic',
];

export interface AgendaItem {
  tipo: string;
  titulo: string;
  fecha: string;
  hora: string | null;
  detalle: string | null;
}

export interface ActivityItem {
  id: number;
  accion: string;
  entidad: string;
  entidadId: number | null;
  detalle: string | null;
  fecha: string;
  actor: string | null;
}

export interface AdminDashboard {
  usuariosActivos: number;
  emprendimientos: number;
  tareas: number;
  avancePromedio: number;
  solicitudesPendientes: number;
  alertas: {
    sinDocente: number;
    diagnosticosSinRevisar: number;
    tareasVencidas: number;
    eventosPendientes: number;
    actasEnRevision: number;
  };
  avancePorMes: { mes: string; etiqueta: string; avances: number; promedio: number | null }[];
  porSede: { nombre: string; total: number }[];
  porSector: { nombre: string; total: number }[];
  agenda: AgendaItem[];
  actividadReciente: ActivityItem[];
}

export interface TeacherDashboard {
  emprendimientos: number;
  avancePromedio: number;
  tareasPorRevisar: number;
  tareasAltaPrioridad: number;
  avancesRegistrados: number;
  avancesConEvidencia: number;
  asesorias: {
    agendadas: number;
    porAgendar: number;
    completadas: number;
    proxima: AgendaItem | null;
  };
  avancePorEmprendimiento: {
    id: number;
    codigo: string;
    nombre: string;
    avance: number;
    estudiante: string;
  }[];
  agenda: AgendaItem[];
  actividadReciente: ActivityItem[];
}

export interface StudentDashboard {
  emprendimiento: {
    id: number;
    codigo: string;
    nombre: string;
    estadoAprobacion: string;
    avance: number;
    etapa: string | null;
  } | null;
  diagnostico: { id: number; estado: string } | null;
  acta: { id: number; estado: string } | null;
  tareas: {
    total: number;
    completadas: number;
    pendientes: number;
    vencidas: number;
    enRevision: number;
  };
  asesorias: { realizadas: number; proximas: number };
  fases: {
    faseId: number | null;
    fase: string | null;
    total: number;
    completadas: number;
    porcentaje: number;
  }[];
  proximasAsesorias: AgendaItem[];
  tareasPorCompletar: {
    id: number;
    titulo: string;
    prioridad: string;
    fechaLimite: string | null;
    vencida: boolean;
  }[];
  eventos: { id: number; nombre: string; fecha: string | null; hora: string | null; lugar: string | null }[];
  notificacionesSinLeer: number;
}

interface RawAdmin extends Omit<AdminDashboard, 'avancePorMes'> {
  avancePorMes: { mes: string; avances: number; promedio: number | null }[];
}

/** `GET /dashboard/admin`: panorama institucional completo. */
export async function adminDashboard(): Promise<AdminDashboard> {
  const { rows } = await query<{ data: RawAdmin }>(
    `WITH meses AS (
       SELECT generate_series(
                date_trunc('month', (now() AT TIME ZONE 'America/Bogota'))::date - INTERVAL '5 months',
                date_trunc('month', (now() AT TIME ZONE 'America/Bogota'))::date,
                INTERVAL '1 month'
              )::date AS mes
     )
     SELECT json_build_object(
       'usuariosActivos', (
         SELECT COUNT(*)::int FROM usuarios
          WHERE estado = 'Activo' AND fecha_eliminacion IS NULL),
       'emprendimientos', (
         SELECT COUNT(*)::int FROM emprendimiento WHERE fecha_eliminacion IS NULL),
       'tareas', (
         SELECT COUNT(*)::int FROM tareas WHERE fecha_eliminacion IS NULL),
       'avancePromedio', (
         SELECT COALESCE(ROUND(AVG(avance))::int, 0)
           FROM emprendimiento WHERE fecha_eliminacion IS NULL),
       'solicitudesPendientes', (
         SELECT COUNT(*)::int FROM solicitudes WHERE estado = 'Pendiente'),
       'alertas', json_build_object(
         'sinDocente', (
           SELECT COUNT(*)::int
             FROM emprendimiento e
            WHERE e.fecha_eliminacion IS NULL
              AND e.estado_aprobacion = 'Aprobado'
              AND NOT EXISTS (
                SELECT 1 FROM asignaciones a
                 WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                   AND a.estado = 'activa')),
         'diagnosticosSinRevisar', (
           SELECT COUNT(*)::int FROM diagnosticos WHERE estado = 'Enviado'),
         'tareasVencidas', (
           SELECT COUNT(*)::int
             FROM tareas
            WHERE fecha_eliminacion IS NULL
              AND estado IN ('Pendiente', 'En curso', 'Devuelta')
              AND fecha_limite < (now() AT TIME ZONE 'America/Bogota')::date),
         'eventosPendientes', (
           SELECT COUNT(*)::int
             FROM eventos
            WHERE fecha_eliminacion IS NULL AND estado = 'Pendiente'),
         'actasEnRevision', (
           SELECT COUNT(*)::int FROM actas WHERE estado = 'En revisión')
       ),
       'avancePorMes', (
         SELECT COALESCE(json_agg(json_build_object(
                  'mes', to_char(m.mes, 'YYYY-MM'),
                  'avances', COALESCE(s.avances, 0),
                  'promedio', s.promedio
                ) ORDER BY m.mes), '[]'::json)
           FROM meses m
           LEFT JOIN LATERAL (
             SELECT COUNT(*)::int AS avances, ROUND(AVG(sg.puntaje))::int AS promedio
               FROM seguimientos sg
              WHERE sg.fecha_eliminacion IS NULL
                AND sg.tipo_seguimiento = 'Avance de fase'
                AND sg.fecha_seguimiento >= m.mes
                AND sg.fecha_seguimiento < m.mes + INTERVAL '1 month'
           ) s ON TRUE),
       'porSede', (
         SELECT COALESCE(json_agg(json_build_object('nombre', COALESCE(cu.nombre, 'Sin sede'), 'total', x.total) ORDER BY x.total DESC, 1), '[]'::json)
           FROM (
             SELECT e.centro_universitarios_id_centro_universitarios AS sede, COUNT(*)::int AS total
               FROM emprendimiento e
              WHERE e.fecha_eliminacion IS NULL
              GROUP BY 1
           ) x
           LEFT JOIN centrouniversitarios cu
             ON cu.id_centrouniversitarios = x.sede),
       'porSector', (
         SELECT COALESCE(json_agg(json_build_object('nombre', COALESCE(sec.nombre, 'Sin sector'), 'total', x.total) ORDER BY x.total DESC, 1), '[]'::json)
           FROM (
             SELECT e.sector_economico_id_sector_economico AS sector, COUNT(*)::int AS total
               FROM emprendimiento e
              WHERE e.fecha_eliminacion IS NULL
              GROUP BY 1
           ) x
           LEFT JOIN sectoreconomico sec
             ON sec.id_sectoreconomico = x.sector),
       'agenda', (
         SELECT COALESCE(json_agg(json_build_object(
                  'tipo', x.tipo, 'titulo', x.titulo, 'fecha', x.fecha,
                  'hora', x.hora, 'detalle', x.detalle
                ) ORDER BY x.orden), '[]'::json)
           FROM (
             SELECT 'Asesoría' AS tipo, a.tema AS titulo,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'HH24:MI') AS hora,
                    e.nombre AS detalle, a.fecha_asesoria AS orden
               FROM asesorias a
               JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
              WHERE a.fecha_eliminacion IS NULL
                AND a.fecha_asesoria >= now()
                AND a.estado IN ('Programada', 'Confirmada', 'En curso')

             UNION ALL

             SELECT 'Evento' AS tipo, ev.nombre_evento AS titulo,
                    to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
                    to_char(fyh.hora_inicio, 'HH24:MI') AS hora,
                    ev.lugar AS detalle,
                    (fyh.fecha + fyh.hora_inicio) AT TIME ZONE 'America/Bogota' AS orden
               FROM eventos ev
               JOIN fecha_y_horarios fyh
                 ON fyh.id_fecha_y_horarios = ev.fecha_y_horarios_id_fecha_y_horarios
              WHERE ev.fecha_eliminacion IS NULL
                AND ev.estado = 'Publicado'
                AND (fyh.fecha + fyh.hora_inicio) >= (now() AT TIME ZONE 'America/Bogota')
           ) x
           LIMIT 6),
       'actividadReciente', (
         SELECT COALESCE(json_agg(json_build_object(
                  'id', a.id_auditoria, 'accion', a.accion, 'entidad', a.entidad,
                  'entidadId', a.entidad_id,
                  'detalle', COALESCE(a.valor_nuevo->>'titulo', a.valor_nuevo->>'nombre',
                                      a.valor_nuevo->>'nombreEvento', a.valor_nuevo->>'tema',
                                      a.valor_nuevo->>'clave'),
                  'fecha', a.fecha,
                  'actor', CASE WHEN u.id_usuarios IS NULL THEN NULL
                                ELSE u.nombres || ' ' || u.apellidos END
                ) ORDER BY a.fecha DESC, a.id_auditoria DESC), '[]'::json)
           FROM (
             SELECT * FROM auditoria_eventos
              ORDER BY fecha DESC, id_auditoria DESC
              LIMIT 6
           ) a
           LEFT JOIN usuarios u ON u.id_usuarios = a.usuarios_id_usuarios)
     ) AS data`,
  );

  const data = rows[0]!.data;
  return {
    ...data,
    avancePorMes: data.avancePorMes.map((month) => ({
      ...month,
      etiqueta: MONTH_LABELS[Number(month.mes.slice(5, 7)) - 1] ?? month.mes,
    })),
  };
}

/** `GET /dashboard/teacher`: solo los emprendimientos con asignación activa del docente. */
export async function teacherDashboard(actor: SessionUser): Promise<TeacherDashboard> {
  const { rows } = await query<{ data: TeacherDashboard }>(
    `WITH mis AS (
       SELECT a.emprendimiento_id_emprendimiento AS id
         FROM asignaciones a
        WHERE a.usuarios_id_mentor = $1
          AND a.estado = 'activa'
     )
     SELECT json_build_object(
       'emprendimientos', (SELECT COUNT(*)::int FROM mis),
       'avancePromedio', (
         SELECT COALESCE(ROUND(AVG(e.avance))::int, 0)
           FROM emprendimiento e JOIN mis ON mis.id = e.id_emprendimiento),
       'tareasPorRevisar', (
         SELECT COUNT(*)::int
           FROM tareas t JOIN mis ON mis.id = t.emprendimiento_id_emprendimiento
          WHERE t.fecha_eliminacion IS NULL AND t.estado = 'En revisión'),
       'tareasAltaPrioridad', (
         SELECT COUNT(*)::int
           FROM tareas t JOIN mis ON mis.id = t.emprendimiento_id_emprendimiento
          WHERE t.fecha_eliminacion IS NULL AND t.estado = 'En revisión'
            AND t.prioridad = 'Alta'),
       'avancesRegistrados', (
         SELECT COUNT(*)::int
           FROM seguimientos s
          WHERE s.usuarios_id_usuarios = $1 AND s.fecha_eliminacion IS NULL),
       'avancesConEvidencia', (
         SELECT COUNT(*)::int
           FROM seguimientos s
          WHERE s.usuarios_id_usuarios = $1 AND s.fecha_eliminacion IS NULL
            AND EXISTS (
              SELECT 1 FROM adjuntos_seguimientos asg
               WHERE asg.seguimientos_id_seguimientos = s.id_seguimientos)),
       'asesorias', json_build_object(
         'agendadas', (
           SELECT COUNT(*)::int FROM asesorias
            WHERE usuarios_id_docentes = $1 AND fecha_eliminacion IS NULL
              AND estado IN ('Programada', 'Confirmada')
              AND fecha_asesoria >= now()),
         'porAgendar', (
           SELECT COUNT(*)::int FROM asesorias
            WHERE usuarios_id_docentes = $1 AND fecha_eliminacion IS NULL
              AND estado = 'Por agendar'),
         'completadas', (
           SELECT COUNT(*)::int FROM asesorias
            WHERE usuarios_id_docentes = $1 AND fecha_eliminacion IS NULL
              AND estado = 'Completada'),
         'proxima', (
           SELECT json_build_object(
                    'tipo', 'Asesoría', 'titulo', a.tema,
                    'fecha', to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD'),
                    'hora', to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'HH24:MI'),
                    'detalle', e.nombre)
             FROM asesorias a
             JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
            WHERE a.usuarios_id_docentes = $1 AND a.fecha_eliminacion IS NULL
              AND a.estado IN ('Programada', 'Confirmada')
              AND a.fecha_asesoria >= now()
            ORDER BY a.fecha_asesoria
            LIMIT 1)
       ),
       'avancePorEmprendimiento', (
         SELECT COALESCE(json_agg(json_build_object(
                  'id', x.id, 'codigo', x.codigo, 'nombre', x.nombre,
                  'avance', x.avance, 'estudiante', x.estudiante
                ) ORDER BY x.avance DESC, x.codigo), '[]'::json)
           FROM (
             SELECT e.id_emprendimiento AS id, e.codigo, e.nombre, e.avance,
                    u.nombres || ' ' || u.apellidos AS estudiante
               FROM emprendimiento e
               JOIN mis ON mis.id = e.id_emprendimiento
               JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
              WHERE e.fecha_eliminacion IS NULL
           ) x),
       'agenda', (
         SELECT COALESCE(json_agg(json_build_object(
                  'tipo', x.tipo, 'titulo', x.titulo, 'fecha', x.fecha,
                  'hora', x.hora, 'detalle', x.detalle
                ) ORDER BY x.orden), '[]'::json)
           FROM (
             SELECT 'Asesoría' AS tipo, a.tema AS titulo,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'HH24:MI') AS hora,
                    e.nombre AS detalle, a.fecha_asesoria AS orden
               FROM asesorias a
               JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
              WHERE a.usuarios_id_docentes = $1 AND a.fecha_eliminacion IS NULL
                AND a.fecha_asesoria >= now()
                AND a.estado IN ('Programada', 'Confirmada', 'En curso')

             UNION ALL

             SELECT 'Tarea' AS tipo, t.titulo,
                    to_char(t.fecha_limite, 'YYYY-MM-DD') AS fecha,
                    NULL AS hora,
                    e.nombre AS detalle,
                    t.fecha_limite::timestamp AS orden
               FROM tareas t
               JOIN mis ON mis.id = t.emprendimiento_id_emprendimiento
               JOIN emprendimiento e ON e.id_emprendimiento = t.emprendimiento_id_emprendimiento
              WHERE t.fecha_eliminacion IS NULL
                AND t.estado = 'En revisión'
           ) x
           LIMIT 8),
       'actividadReciente', (
         SELECT COALESCE(json_agg(json_build_object(
                  'id', a.id_auditoria, 'accion', a.accion, 'entidad', a.entidad,
                  'entidadId', a.entidad_id,
                  'detalle', COALESCE(a.valor_nuevo->>'titulo', a.valor_nuevo->>'nombre',
                                      a.valor_nuevo->>'tema', a.valor_nuevo->>'clave'),
                  'fecha', a.fecha,
                  'actor', u.nombres || ' ' || u.apellidos
                ) ORDER BY a.fecha DESC, a.id_auditoria DESC), '[]'::json)
           FROM (
             SELECT * FROM auditoria_eventos
              WHERE usuarios_id_usuarios = $1
              ORDER BY fecha DESC, id_auditoria DESC
              LIMIT 6
           ) a
           JOIN usuarios u ON u.id_usuarios = a.usuarios_id_usuarios)
     ) AS data`,
    [actor.id],
  );

  return rows[0]!.data;
}

/** `GET /dashboard/student`: el emprendimiento vigente del estudiante y su día a día. */
export async function studentDashboard(actor: SessionUser): Promise<StudentDashboard> {
  const { rows } = await query<{ data: StudentDashboard }>(
    `WITH emp AS (
       SELECT e.id_emprendimiento, e.codigo, e.nombre, e.estado_aprobacion, e.avance,
              et.nombre AS etapa
         FROM emprendimiento e
         LEFT JOIN etapaemprendimiento et
           ON et.id_etapaemprendimiento = e.etapa_emprendimiento_id_etapa_emprendimiento
        WHERE e.usuarios_id_usuarios = $1
          AND e.fecha_eliminacion IS NULL
        ORDER BY (e.estado_aprobacion = 'Aprobado') DESC, e.id_emprendimiento DESC
        LIMIT 1
     )
     SELECT json_build_object(
       'emprendimiento', (
         SELECT json_build_object(
                  'id', id_emprendimiento, 'codigo', codigo, 'nombre', nombre,
                  'estadoAprobacion', estado_aprobacion, 'avance', avance, 'etapa', etapa)
           FROM emp),
       'diagnostico', (
         SELECT json_build_object('id', d.id_diagnosticos, 'estado', d.estado)
           FROM diagnosticos d
          WHERE d.emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
          ORDER BY d.fecha_diagnostico DESC, d.id_diagnosticos DESC
          LIMIT 1),
       'acta', (
         SELECT json_build_object('id', a.id_acta, 'estado', a.estado)
           FROM actas a
          WHERE a.emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
          ORDER BY a.fecha_carga DESC, a.id_acta DESC
          LIMIT 1),
       'tareas', json_build_object(
         'total', (
           SELECT COUNT(*)::int FROM tareas
            WHERE emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
              AND fecha_eliminacion IS NULL),
         'completadas', (
           SELECT COUNT(*)::int FROM tareas
            WHERE emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
              AND fecha_eliminacion IS NULL AND estado = 'Completada'),
         'pendientes', (
           SELECT COUNT(*)::int FROM tareas
            WHERE emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
              AND fecha_eliminacion IS NULL
              AND estado IN ('Pendiente', 'En curso', 'Devuelta')),
         'vencidas', (
           SELECT COUNT(*)::int FROM tareas
            WHERE emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
              AND fecha_eliminacion IS NULL
              AND estado IN ('Pendiente', 'En curso', 'Devuelta')
              AND fecha_limite < (now() AT TIME ZONE 'America/Bogota')::date),
         'enRevision', (
           SELECT COUNT(*)::int FROM tareas
            WHERE emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
              AND fecha_eliminacion IS NULL AND estado = 'En revisión')
       ),
       'asesorias', json_build_object(
         'realizadas', (
           SELECT COUNT(*)::int FROM asesorias
            WHERE usuarios_id_usuarios = $1 AND fecha_eliminacion IS NULL
              AND estado = 'Completada'),
         'proximas', (
           SELECT COUNT(*)::int FROM asesorias
            WHERE usuarios_id_usuarios = $1 AND fecha_eliminacion IS NULL
              AND estado IN ('Programada', 'Confirmada')
              AND fecha_asesoria >= now())
       ),
       'fases', (
         SELECT COALESCE(json_agg(json_build_object(
                  'faseId', x.fase_id, 'fase', x.fase, 'total', x.total,
                  'completadas', x.completadas,
                  'porcentaje', CASE WHEN x.total = 0 THEN 0
                                     ELSE ROUND(100.0 * x.completadas / x.total)::int END
                ) ORDER BY x.fase_id NULLS LAST), '[]'::json)
           FROM (
             SELECT f.id_faseplan AS fase_id, f.nombre AS fase,
                    COUNT(t.id_tareas)::int AS total,
                    COUNT(t.id_tareas) FILTER (WHERE t.estado = 'Completada')::int AS completadas
               FROM faseplan f
               LEFT JOIN tareas t
                 ON t.fase_plan_id_fase_plan = f.id_faseplan
                AND t.emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
                AND t.fecha_eliminacion IS NULL
              WHERE (SELECT id_emprendimiento FROM emp) IS NOT NULL
              GROUP BY f.id_faseplan, f.nombre

             UNION ALL

             SELECT NULL AS fase_id, NULL AS fase,
                    COUNT(*)::int AS total,
                    COUNT(*) FILTER (WHERE t.estado = 'Completada')::int AS completadas
               FROM tareas t
              WHERE t.emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
                AND t.fecha_eliminacion IS NULL
                AND t.fase_plan_id_fase_plan IS NULL
             HAVING COUNT(*) > 0
           ) x),
       'proximasAsesorias', (
         SELECT COALESCE(json_agg(json_build_object(
                  'tipo', 'Asesoría', 'titulo', x.tema, 'fecha', x.fecha,
                  'hora', x.hora, 'detalle', x.detalle
                ) ORDER BY x.orden), '[]'::json)
           FROM (
             SELECT a.tema,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'YYYY-MM-DD') AS fecha,
                    to_char(a.fecha_asesoria AT TIME ZONE 'America/Bogota', 'HH24:MI') AS hora,
                    COALESCE(m.nombre, 'Sin modalidad') AS detalle,
                    a.fecha_asesoria AS orden
               FROM asesorias a
               LEFT JOIN modalidad m ON m.id_modalidad = a.modalidad_id_modalidad
              WHERE a.usuarios_id_usuarios = $1 AND a.fecha_eliminacion IS NULL
                AND a.estado IN ('Programada', 'Confirmada')
                AND a.fecha_asesoria >= now()
              ORDER BY a.fecha_asesoria
              LIMIT 3
           ) x),
       'tareasPorCompletar', (
         SELECT COALESCE(json_agg(json_build_object(
                  'id', x.id_tareas, 'titulo', x.titulo, 'prioridad', x.prioridad,
                  'fechaLimite', x.fecha_limite, 'vencida', x.vencida
                ) ORDER BY x.fecha_limite NULLS LAST, x.id_tareas), '[]'::json)
           FROM (
             SELECT t.id_tareas, t.titulo, t.prioridad,
                    to_char(t.fecha_limite, 'YYYY-MM-DD') AS fecha_limite,
                    (t.fecha_limite IS NOT NULL
                     AND t.fecha_limite < (now() AT TIME ZONE 'America/Bogota')::date) AS vencida
               FROM tareas t
              WHERE t.emprendimiento_id_emprendimiento = (SELECT id_emprendimiento FROM emp)
                AND t.fecha_eliminacion IS NULL
                AND t.estado IN ('Pendiente', 'En curso', 'Devuelta')
              ORDER BY t.fecha_limite NULLS LAST, t.id_tareas
              LIMIT 5
           ) x),
       'eventos', (
         SELECT COALESCE(json_agg(json_build_object(
                  'id', x.id_eventos, 'nombre', x.nombre_evento,
                  'fecha', x.fecha, 'hora', x.hora, 'lugar', x.lugar
                ) ORDER BY x.orden), '[]'::json)
           FROM (
             SELECT ev.id_eventos, ev.nombre_evento, ev.lugar,
                    to_char(fyh.fecha, 'YYYY-MM-DD') AS fecha,
                    to_char(fyh.hora_inicio, 'HH24:MI') AS hora,
                    (fyh.fecha + fyh.hora_inicio) AS orden
               FROM eventos ev
               JOIN fecha_y_horarios fyh
                 ON fyh.id_fecha_y_horarios = ev.fecha_y_horarios_id_fecha_y_horarios
              WHERE ev.fecha_eliminacion IS NULL AND ev.estado = 'Publicado'
                AND (fyh.fecha + fyh.hora_inicio) >= (now() AT TIME ZONE 'America/Bogota')
              ORDER BY fyh.fecha, fyh.hora_inicio
              LIMIT 3
           ) x),
       'notificacionesSinLeer', (
         SELECT COUNT(*)::int FROM notificaciones
          WHERE usuarios_id_usuarios = $1 AND leida = FALSE)
     ) AS data`,
    [actor.id],
  );

  return rows[0]!.data;
}
