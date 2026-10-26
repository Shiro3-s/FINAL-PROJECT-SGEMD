import { logger } from '../config/logger.js';
import { createBackup } from '../modules/backups/service.js';
import { bogotaParts } from '../utils/dates.js';
import { runInactivityJob } from './inactivity.job.js';
import { runOverdueTasksJob } from './overdueTasks.job.js';

/**
 * Planificador de los jobs del programa.
 *
 * Se comprueba la hora de Bogotá cada 30 segundos y cada job corre **una vez al día** como
 * máximo (mapa `ultimaCorrida`). No se recuperan ejecuciones perdidas: si el proceso estaba
 * caído a las 09:00, el respaldo no se dispara al arrancar, para no sorprender con un
 * `pg_dump` en un reinicio. El disparo manual del panel cubre ese caso.
 */
interface ScheduledJob {
  nombre: string;
  hora: string;
  minuto: string;
  run: () => Promise<unknown>;
}

const SCHEDULE: readonly ScheduledJob[] = [
  { nombre: 'inactividad', hora: '06', minuto: '00', run: runInactivityJob },
  { nombre: 'tareas-vencidas', hora: '06', minuto: '10', run: runOverdueTasksJob },
  {
    nombre: 'respaldo',
    hora: '09',
    minuto: '00',
    run: () => createBackup({ tipo: 'Completo', actor: null, ip: null }),
  },
];

let timer: NodeJS.Timeout | null = null;
const lastRun = new Map<string, string>();

async function tick(): Promise<void> {
  const parts = bogotaParts();
  const today = `${parts.year}${parts.month}${parts.day}`;

  for (const job of SCHEDULE) {
    if (parts.hour !== job.hora || parts.minute !== job.minuto) continue;
    if (lastRun.get(job.nombre) === today) continue;

    lastRun.set(job.nombre, today);
    try {
      const result = await job.run();
      logger.info({ job: job.nombre, result }, 'Job programado ejecutado');
    } catch (error) {
      logger.error({ err: error, job: job.nombre }, 'El job programado falló');
    }
  }
}

export function startScheduler(): void {
  if (timer !== null) return;

  timer = setInterval(() => void tick(), 30_000);
  // No mantiene vivo el proceso: el servidor HTTP es quien decide cuándo terminar.
  timer.unref();
  logger.info(
    { jobs: SCHEDULE.map((job) => `${job.nombre}@${job.hora}:${job.minuto}`) },
    'Planificador de jobs iniciado (America/Bogota)',
  );
}

export function stopScheduler(): void {
  if (timer !== null) clearInterval(timer);
  timer = null;
}
