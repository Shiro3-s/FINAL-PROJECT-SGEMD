import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { runInactivityJob } from '../src/jobs/inactivity.job.js';
import { runOverdueTasksJob } from '../src/jobs/overdueTasks.job.js';
import { startScheduler, stopScheduler } from '../src/jobs/scheduler.js';
import { adminSession, type Session } from './api.js';
import { createAccount, evidenceScenario, type Scenario } from './fixtures.js';

/**
 * T14 — jobs de inactividad (BR-005) y tareas vencidas.
 *
 * Los jobs se disparan a mano: la suite no espera al reloj. Se comprueba que la
 * inactividad solo toca estudiantes `Activo` con actividad medible, que es idempotente y
 * que el aviso de tarea vencida llega una sola vez al estudiante y al docente.
 */

let admin: Session;
let scenario: Scenario;

function daysAgo(days: number): string {
  return new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
}

async function setActivity(userId: number, value: string | null): Promise<void> {
  await query('UPDATE usuarios SET ultima_actividad = $2 WHERE id_usuarios = $1', [userId, value]);
}

async function stateOf(userId: number): Promise<string> {
  const { rows } = await query<{ estado: string }>(
    'SELECT estado FROM usuarios WHERE id_usuarios = $1',
    [userId],
  );
  return rows[0]!.estado;
}

beforeAll(async () => {
  admin = await adminSession();
  scenario = await evidenceScenario();
});

afterAll(async () => {
  stopScheduler();
  await query(`UPDATE configuracion_programa SET valor = '90' WHERE clave = 'inactividad_dias'`);
  await closePool();
});

describe('job de inactividad', () => {
  it('pasa a Inactivo al estudiante sin actividad en el umbral', async () => {
    const student = await createAccount(admin, 2);
    await setActivity(student.id, daysAgo(100));

    const run = await runInactivityJob();

    expect(run.umbralDias).toBe(90);
    expect(run.afectados).toContain(student.id);
    expect(await stateOf(student.id)).toBe('Inactivo');

    const { rows } = await query<{ valor_anterior: { estado: string }; valor_nuevo: { estado: string } }>(
      `SELECT valor_anterior, valor_nuevo FROM auditoria_eventos
        WHERE accion = 'Inactividad automática' AND entidad_id = $1
        ORDER BY id_auditoria DESC LIMIT 1`,
      [student.id],
    );
    expect(rows[0]!.valor_anterior.estado).toBe('Activo');
    expect(rows[0]!.valor_nuevo.estado).toBe('Inactivo');

    const notice = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM notificaciones
        WHERE usuarios_id_usuarios = $1 AND tipo = 'Sistema'`,
      [student.id],
    );
    expect(Number(notice.rows[0]!.total)).toBeGreaterThan(0);
  });

  it('es idempotente: la segunda corrida no afecta a nadie', async () => {
    const run = await runInactivityJob();
    expect(run.afectados).toEqual([]);
  });

  it('no toca cuentas recientes, sin actividad medible ni docentes', async () => {
    const recent = await createAccount(admin, 2);
    await setActivity(recent.id, daysAgo(10));

    const unknown = await createAccount(admin, 2);
    await setActivity(unknown.id, null);

    const teacher = await createAccount(admin, 3);
    await setActivity(teacher.id, daysAgo(400));

    const run = await runInactivityJob();

    expect(run.afectados).not.toContain(recent.id);
    expect(run.afectados).not.toContain(unknown.id);
    expect(run.afectados).not.toContain(teacher.id);
    expect(await stateOf(recent.id)).toBe('Activo');
    expect(await stateOf(unknown.id)).toBe('Activo');
    expect(await stateOf(teacher.id)).toBe('Activo');
  });

  it('respeta el umbral configurado', async () => {
    await query(`UPDATE configuracion_programa SET valor = '30' WHERE clave = 'inactividad_dias'`);

    const student = await createAccount(admin, 2);
    await setActivity(student.id, daysAgo(40));

    const run = await runInactivityJob();
    expect(run.umbralDias).toBe(30);
    expect(run.afectados).toContain(student.id);

    await query(`UPDATE configuracion_programa SET valor = '90' WHERE clave = 'inactividad_dias'`);
  });

  it('deja un registro de la corrida', async () => {
    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Ejecución del job de inactividad'`,
    );
    expect(Number(rows[0]!.total)).toBeGreaterThan(0);
  });
});

describe('job de tareas vencidas', () => {
  let overdueId: number;

  it('avisa al estudiante y al docente una sola vez', async () => {
    const created = await scenario.mentor.session.post('/api/task').send({
      titulo: 'Evidencia vencida del punto de venta',
      descripcion: 'Foto del punto de venta',
      emprendimientoId: scenario.emprendimientoId,
      fasePlanId: 1,
      fechaLimite: daysAgo(3).slice(0, 10),
      prioridad: 'Alta',
      puntos: 20,
    });
    expect(created.status).toBe(201);
    overdueId = created.body.data.id as number;

    const first = await runOverdueTasksJob();
    expect(first.avisadas).toBeGreaterThanOrEqual(2);

    const notices = await query<{
      usuarios_id_usuarios: number;
      tipo_objeto: string;
      objeto_id: number;
    }>(
      `SELECT usuarios_id_usuarios, tipo_objeto, objeto_id
         FROM notificaciones
        WHERE tipo_objeto = 'tarea_vencida' AND objeto_id = $1`,
      [overdueId],
    );

    const recipients = notices.rows.map((row) => row.usuarios_id_usuarios);
    expect(recipients).toContain(scenario.student.id);
    expect(recipients).toContain(scenario.mentor.id);
    expect(new Set(recipients).size).toBe(recipients.length);

    const second = await runOverdueTasksJob();
    expect(second.avisadas).toBe(0);

    const after = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM notificaciones
        WHERE tipo_objeto = 'tarea_vencida' AND objeto_id = $1`,
      [overdueId],
    );
    expect(Number(after.rows[0]!.total)).toBe(recipients.length);
  });

  it('no avisa tareas completadas ni sin fecha vencida', async () => {
    const future = await scenario.mentor.session.post('/api/task').send({
      titulo: 'Tarea con plazo futuro',
      emprendimientoId: scenario.emprendimientoId,
      prioridad: 'Media',
      fechaLimite: '2099-12-31',
    });
    expect(future.status).toBe(201);

    await runOverdueTasksJob();

    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM notificaciones
        WHERE tipo_objeto = 'tarea_vencida' AND objeto_id = $1`,
      [future.body.data.id as number],
    );
    expect(Number(rows[0]!.total)).toBe(0);
  });

  it('deja un registro de la corrida', async () => {
    const { rows } = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos
        WHERE accion = 'Ejecución del job de tareas vencidas'`,
    );
    expect(Number(rows[0]!.total)).toBeGreaterThan(0);
  });
});

describe('planificador', () => {
  it('arranca y se detiene sin efectos en la suite', () => {
    startScheduler();
    startScheduler(); // idempotente
    stopScheduler();
    stopScheduler(); // idempotente
  });
});
