import type { SqlExecutor } from './programSettings.js';

/**
 * Avance del emprendimiento derivado de las tareas (R21, FR-022).
 *
 * `emprendimiento.avance` es una columna, pero **nunca** la escribe el cliente: se
 * recalcula desde las tareas no eliminadas cada vez que una operación puede cambiar el
 * número de completadas. La fórmula es el porcentaje de tareas `Completada` sobre el total;
 * sin tareas el avance es 0 (no se divide por cero).
 *
 * Se llama **dentro** de la transacción del cambio, para que el avance y la tarea no puedan
 * quedar desfasados.
 */
export async function recomputeProgress(db: SqlExecutor, emprendimientoId: number): Promise<number> {
  const { rows } = await db.query<{ avance: number }>(
    `WITH conteo AS (
       SELECT COUNT(*)::int AS total,
              COUNT(*) FILTER (WHERE estado = 'Completada')::int AS completadas
         FROM tareas
        WHERE emprendimiento_id_emprendimiento = $1
          AND fecha_eliminacion IS NULL
     )
     UPDATE emprendimiento e
        SET avance = CASE
              WHEN conteo.total = 0 THEN 0
              ELSE ROUND(100.0 * conteo.completadas / conteo.total)::int
            END
       FROM conteo
      WHERE e.id_emprendimiento = $1
      RETURNING e.avance`,
    [emprendimientoId],
  );

  return rows[0]?.avance ?? 0;
}

export interface PhaseProgress {
  /** `null` agrupa las tareas sin fase asignada. */
  faseId: number | null;
  fase: string | null;
  total: number;
  completadas: number;
  porcentaje: number;
}

export interface Progress {
  emprendimientoId: number;
  avance: number;
  total: number;
  completadas: number;
  fases: PhaseProgress[];
}

function percentage(completadas: number, total: number): number {
  return total === 0 ? 0 : Math.round((100 * completadas) / total);
}

/**
 * Progreso por fase del plan (FR-022): el estudiante ve el porcentaje de cada fase y el
 * total. Las cuatro fases del catálogo aparecen siempre, aunque no tengan tareas.
 */
export async function progressByPhase(
  db: SqlExecutor,
  emprendimientoId: number,
): Promise<Progress> {
  const { rows } = await db.query<{
    fase_id: number | null;
    fase: string | null;
    total: number;
    completadas: number;
  }>(
    `SELECT f.id_faseplan AS fase_id, f.nombre AS fase,
            COUNT(t.id_tareas)::int AS total,
            COUNT(t.id_tareas) FILTER (WHERE t.estado = 'Completada')::int AS completadas
       FROM faseplan f
       LEFT JOIN tareas t
         ON t.fase_plan_id_fase_plan = f.id_faseplan
        AND t.emprendimiento_id_emprendimiento = $1
        AND t.fecha_eliminacion IS NULL
      GROUP BY f.id_faseplan, f.nombre

      UNION ALL

     SELECT NULL AS fase_id, NULL AS fase,
            COUNT(*)::int AS total,
            COUNT(*) FILTER (WHERE t.estado = 'Completada')::int AS completadas
       FROM tareas t
      WHERE t.emprendimiento_id_emprendimiento = $1
        AND t.fecha_eliminacion IS NULL
        AND t.fase_plan_id_fase_plan IS NULL
     HAVING COUNT(*) > 0

      ORDER BY fase_id NULLS LAST`,
    [emprendimientoId],
  );

  const fases = rows.map((row) => ({
    faseId: row.fase_id,
    fase: row.fase,
    total: row.total,
    completadas: row.completadas,
    porcentaje: percentage(row.completadas, row.total),
  }));

  const total = fases.reduce((sum, fase) => sum + fase.total, 0);
  const completadas = fases.reduce((sum, fase) => sum + fase.completadas, 0);

  return {
    emprendimientoId,
    avance: percentage(completadas, total),
    total,
    completadas,
    fases,
  };
}
