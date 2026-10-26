import type { PoolClient } from 'pg';

/**
 * Bloque de agenda (`fecha_y_horarios`).
 *
 * Asesorías y eventos comparten el mismo catálogo de bloques: dos registros con la misma
 * fecha y las mismas horas son el mismo bloque. El `advisory lock` por clave evita que dos
 * transacciones simultáneas inserten la fila duplicada (el catálogo no tiene índice único
 * por esas tres columnas).
 */
export interface Schedule {
  fecha: string;
  horaInicio: string;
  horaFin: string;
}

/** Devuelve el id del bloque, reutilizándolo si ya existe. */
export async function resolveSchedule(db: PoolClient, schedule: Schedule): Promise<number> {
  await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
    `fecha_y_horarios:${schedule.fecha}:${schedule.horaInicio}:${schedule.horaFin}`,
  ]);

  const { rows } = await db.query<{ id: number }>(
    `SELECT id_fecha_y_horarios AS id
       FROM fecha_y_horarios
      WHERE fecha = $1::date AND hora_inicio = $2::time AND hora_fin = $3::time
      ORDER BY id_fecha_y_horarios
      LIMIT 1`,
    [schedule.fecha, schedule.horaInicio, schedule.horaFin],
  );

  if (rows[0]) return rows[0].id;

  const inserted = await db.query<{ id: number }>(
    `INSERT INTO fecha_y_horarios (fecha, hora_inicio, hora_fin)
     VALUES ($1::date, $2::time, $3::time)
     RETURNING id_fecha_y_horarios AS id`,
    [schedule.fecha, schedule.horaInicio, schedule.horaFin],
  );

  return inserted.rows[0]!.id;
}
