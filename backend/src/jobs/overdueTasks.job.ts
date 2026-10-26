import { withTransaction } from '../db/pool.js';
import { AUDIT_ACTIONS, audit, type Queryable } from '../services/audit.js';
import { notify } from '../services/notify.js';

/**
 * Aviso de tareas vencidas.
 *
 * `Vencida` no se guarda (Stage 7): se deriva de `fecha_limite`. Este job avisa una sola
 * vez al estudiante dueño y al docente con asignación activa. La deduplicación se hace por
 * `(tipo_objeto = 'tarea_vencida', objeto_id, usuario)`, no por tarea: si el estudiante ya
 * fue avisado, el docente igual recibe el suyo.
 */
export interface OverdueRun {
  avisadas: number;
  ejecutadoEn: string;
}

interface OverdueTask {
  id_tareas: number;
  titulo: string;
  fecha_limite: string;
  emprendimiento: string;
  estudiante_id: number;
  mentor_id: number | null;
}

async function alreadyNotified(
  db: Queryable,
  taskId: number,
  userId: number,
): Promise<boolean> {
  const { rows } = await db.query<{ existe: boolean }>(
    `SELECT EXISTS (
       SELECT 1 FROM notificaciones
        WHERE tipo_objeto = 'tarea_vencida'
          AND objeto_id = $1
          AND usuarios_id_usuarios = $2
     ) AS existe`,
    [taskId, userId],
  );
  return rows[0]?.existe === true;
}

export async function runOverdueTasksJob(): Promise<OverdueRun> {
  return withTransaction(async (db) => {
    const { rows } = await db.query<OverdueTask>(
      `SELECT t.id_tareas, t.titulo, to_char(t.fecha_limite, 'YYYY-MM-DD') AS fecha_limite,
              e.nombre AS emprendimiento,
              e.usuarios_id_usuarios AS estudiante_id,
              asg.usuarios_id_mentor AS mentor_id
         FROM tareas t
         JOIN emprendimiento e
           ON e.id_emprendimiento = t.emprendimiento_id_emprendimiento
         LEFT JOIN asignaciones asg
           ON asg.emprendimiento_id_emprendimiento = e.id_emprendimiento
          AND asg.estado = 'activa'
        WHERE t.fecha_eliminacion IS NULL
          AND e.fecha_eliminacion IS NULL
          AND t.estado IN ('Pendiente', 'En curso', 'Devuelta')
          AND t.fecha_limite < (now() AT TIME ZONE 'America/Bogota')::date
        ORDER BY t.fecha_limite, t.id_tareas`,
    );

    let avisadas = 0;

    for (const task of rows) {
      if (!(await alreadyNotified(db, task.id_tareas, task.estudiante_id))) {
        await notify(db, {
          usuarioId: task.estudiante_id,
          tipo: 'Tarea',
          mensaje: `La tarea «${task.titulo}» de ${task.emprendimiento} venció el ${task.fecha_limite}.`,
          url: '/estudiante/tareas',
          tipoObjeto: 'tarea_vencida',
          objetoId: task.id_tareas,
        });
        avisadas += 1;
      }

      if (task.mentor_id !== null && !(await alreadyNotified(db, task.id_tareas, task.mentor_id))) {
        await notify(db, {
          usuarioId: task.mentor_id,
          tipo: 'Tarea',
          mensaje: `La tarea «${task.titulo}» de ${task.emprendimiento} está vencida desde el ${task.fecha_limite}.`,
          url: '/docente/tareas',
          tipoObjeto: 'tarea_vencida',
          objetoId: task.id_tareas,
        });
        avisadas += 1;
      }
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.RUN_OVERDUE_JOB,
      entidad: 'jobs',
      entidadId: null,
      valorNuevo: { tareasVencidas: rows.length, avisos: avisadas },
      usuarioId: null,
      ip: null,
    });

    return { avisadas, ejecutadoEn: new Date().toISOString() };
  });
}
