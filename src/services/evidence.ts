import type { SqlExecutor } from './programSettings.js';

/**
 * Evidencias ligadas a una entidad (tareas, seguimientos y asesorías).
 *
 * Los tres pivotes de `docs/diagrama-clases.md` v2 tienen la misma forma, así que el
 * nombre de la tabla y de la columna son constantes del código: nunca llegan desde la
 * petición.
 */
export type EvidenceEntity = 'task' | 'tracing' | 'advice';

const PIVOT: Readonly<Record<EvidenceEntity, { table: string; column: string }>> = {
  task: { table: 'adjuntos_tareas', column: 'tareas_id_tareas' },
  tracing: { table: 'adjuntos_seguimientos', column: 'seguimientos_id_seguimientos' },
  advice: { table: 'adjuntos_asesorias', column: 'asesorias_id_asesorias' },
};

export interface EvidenceRow {
  id: number;
  ruta: string;
}

export function isEvidenceEntity(value: string): value is EvidenceEntity {
  return value === 'task' || value === 'tracing' || value === 'advice';
}

/** Evidencias vigentes de una entidad, con la ruta en disco de cada una. */
export async function listEvidence(
  db: SqlExecutor,
  entity: EvidenceEntity,
  parentId: number,
): Promise<EvidenceRow[]> {
  const pivot = PIVOT[entity];
  const { rows } = await db.query<{ id_adjunto: number; ruta_archivo: string }>(
    `SELECT a.id_adjunto, a.ruta_archivo
       FROM adjuntos a
       JOIN ${pivot.table} p ON p.adjuntos_id_adjunto = a.id_adjunto
      WHERE p.${pivot.column} = $1
        AND a.fecha_eliminacion IS NULL
      ORDER BY a.id_adjunto`,
    [parentId],
  );

  return rows.map((row) => ({ id: row.id_adjunto, ruta: row.ruta_archivo }));
}

/** Cuántas evidencias vigentes tiene una entidad (tope de archivos por entidad). */
export async function countEvidence(
  db: SqlExecutor,
  entity: EvidenceEntity,
  parentId: number,
): Promise<number> {
  const pivot = PIVOT[entity];
  const { rows } = await db.query<{ total: number }>(
    `SELECT COUNT(*)::int AS total
       FROM adjuntos a
       JOIN ${pivot.table} p ON p.adjuntos_id_adjunto = a.id_adjunto
      WHERE p.${pivot.column} = $1
        AND a.fecha_eliminacion IS NULL`,
    [parentId],
  );
  return rows[0]?.total ?? 0;
}

/**
 * Baja lógica de todas las evidencias de una entidad y devuelve las rutas a borrar del
 * disco. El llamador desvincula los archivos **después** de confirmar la transacción.
 */
export async function softDeleteEvidence(
  db: SqlExecutor,
  entity: EvidenceEntity,
  parentId: number,
): Promise<string[]> {
  const pivot = PIVOT[entity];
  const { rows } = await db.query<{ ruta_archivo: string }>(
    `UPDATE adjuntos a
        SET fecha_eliminacion = now()
       FROM ${pivot.table} p
      WHERE p.adjuntos_id_adjunto = a.id_adjunto
        AND p.${pivot.column} = $1
        AND a.fecha_eliminacion IS NULL
      RETURNING a.ruta_archivo`,
    [parentId],
  );

  return rows.map((row) => row.ruta_archivo);
}

/**
 * BR-006: al dar de baja un emprendimiento, sus evidencias desaparecen del disco.
 *
 * Cubre las cuatro vías por las que un archivo cuelga de un expediente: tareas,
 * seguimientos, asesorías y el acta de compromiso (que guarda el adjunto por FK directa).
 * La baja es lógica en la fila y **física** en el archivo; el diálogo de confirmación de la
 * interfaz lo advierte (BR-006, #17).
 */
export async function softDeleteEntrepreneurshipEvidence(
  db: SqlExecutor,
  emprendimientoId: number,
): Promise<string[]> {
  const { rows } = await db.query<{ ruta_archivo: string }>(
    `UPDATE adjuntos a
        SET fecha_eliminacion = now()
      WHERE a.fecha_eliminacion IS NULL
        AND (
          EXISTS (
            SELECT 1
              FROM adjuntos_tareas p
              JOIN tareas t ON t.id_tareas = p.tareas_id_tareas
             WHERE p.adjuntos_id_adjunto = a.id_adjunto
               AND t.emprendimiento_id_emprendimiento = $1
          )
          OR EXISTS (
            SELECT 1
              FROM adjuntos_seguimientos p
              JOIN seguimientos s ON s.id_seguimientos = p.seguimientos_id_seguimientos
             WHERE p.adjuntos_id_adjunto = a.id_adjunto
               AND s.emprendimiento_id_emprendimiento = $1
          )
          OR EXISTS (
            SELECT 1
              FROM adjuntos_asesorias p
              JOIN asesorias s ON s.id_asesorias = p.asesorias_id_asesorias
             WHERE p.adjuntos_id_adjunto = a.id_adjunto
               AND s.emprendimiento_id_emprendimiento = $1
          )
          OR EXISTS (
            SELECT 1
              FROM actas ac
             WHERE ac.adjuntos_id_adjunto = a.id_adjunto
               AND ac.emprendimiento_id_emprendimiento = $1
          )
        )
      RETURNING a.ruta_archivo`,
    [emprendimientoId],
  );

  return rows.map((row) => row.ruta_archivo);
}
