import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { adminSession, type Session } from './api.js';
import { createAccount, evidenceScenario, type Scenario } from './fixtures.js';

/**
 * T22 — tableros por rol (FR-010).
 *
 * Cada tablero es una sola consulta agregada: aquí se comprueba que las cifras coinciden
 * con la base, que el alcance se aplica en el servidor (un docente no ve emprendimientos
 * ajenos) y que un rol no puede pedir el tablero de otro.
 */

let admin: Session;
let scenario: Scenario;
let student: Session;
let limited: Session;

beforeAll(async () => {
  admin = await adminSession();
  scenario = await evidenceScenario();
  student = (await createAccount(admin, 2)).session;
  limited = (await createAccount(admin, 2, 'Limitado')).session;
});

afterAll(async () => {
  await closePool();
});

describe('GET /dashboard/admin', () => {
  it('devuelve el panorama con cifras que coinciden con la base', async () => {
    const response = await admin.get('/api/dashboard/admin');
    expect(response.status).toBe(200);

    const data = response.body.data as {
      usuariosActivos: number;
      emprendimientos: number;
      tareas: number;
      avancePromedio: number;
      solicitudesPendientes: number;
      alertas: Record<string, number>;
      avancePorMes: { mes: string; etiqueta: string; avances: number }[];
      porSede: { nombre: string; total: number }[];
      porSector: { nombre: string; total: number }[];
      agenda: unknown[];
      actividadReciente: unknown[];
    };

    const { rows } = await query<{
      usuarios: string;
      emprendimientos: string;
      tareas: string;
    }>(
      `SELECT (SELECT COUNT(*)::text FROM usuarios
                WHERE estado = 'Activo' AND fecha_eliminacion IS NULL) AS usuarios,
              (SELECT COUNT(*)::text FROM emprendimiento
                WHERE fecha_eliminacion IS NULL) AS emprendimientos,
              (SELECT COUNT(*)::text FROM tareas
                WHERE fecha_eliminacion IS NULL) AS tareas`,
    );

    expect(data.usuariosActivos).toBe(Number(rows[0]!.usuarios));
    expect(data.emprendimientos).toBe(Number(rows[0]!.emprendimientos));
    expect(data.tareas).toBe(Number(rows[0]!.tareas));
    expect(data.avancePromedio).toBeGreaterThanOrEqual(0);
    expect(data.avancePromedio).toBeLessThanOrEqual(100);
    expect(data.solicitudesPendientes).toBeGreaterThanOrEqual(0);

    // Seis meses, del más viejo al actual, con etiqueta localizada en español.
    expect(data.avancePorMes).toHaveLength(6);
    expect(data.avancePorMes[0]!.mes < data.avancePorMes[5]!.mes).toBe(true);
    expect(data.avancePorMes[5]!.etiqueta).toMatch(/^[a-z]{3}$/);

    expect(Array.isArray(data.porSede)).toBe(true);
    expect(Array.isArray(data.porSector)).toBe(true);
    expect(Array.isArray(data.agenda)).toBe(true);
    expect(Array.isArray(data.actividadReciente)).toBe(true);

    // La alerta de emprendimientos sin docente es coherente con la tabla.
    const sinDocente = await query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM emprendimiento e
        WHERE e.fecha_eliminacion IS NULL
          AND e.estado_aprobacion = 'Aprobado'
          AND NOT EXISTS (
            SELECT 1 FROM asignaciones a
             WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
               AND a.estado = 'activa')`,
    );
    expect(data.alertas.sinDocente).toBe(Number(sinDocente.rows[0]!.total));
  });

  it('rechaza a un docente y a un estudiante', async () => {
    expect((await scenario.mentor.session.get('/api/dashboard/admin')).status).toBe(403);
    expect((await student.get('/api/dashboard/admin')).status).toBe(403);
  });
});

describe('GET /dashboard/teacher', () => {
  it('solo cuenta los emprendimientos con asignación activa del docente', async () => {
    const own = await scenario.mentor.session.get('/api/dashboard/teacher');
    expect(own.status).toBe(200);

    const data = own.body.data as {
      emprendimientos: number;
      avancePromedio: number;
      tareasPorRevisar: number;
      tareasAltaPrioridad: number;
      avancesRegistrados: number;
      avancesConEvidencia: number;
      asesorias: { agendadas: number; porAgendar: number; completadas: number };
      avancePorEmprendimiento: { id: number; codigo: string; avance: number }[];
      agenda: unknown[];
      actividadReciente: unknown[];
    };

    expect(data.emprendimientos).toBe(1);
    expect(data.avancePorEmprendimiento).toHaveLength(1);
    expect(data.avancePorEmprendimiento[0]!.id).toBe(scenario.emprendimientoId);
    expect(data.avancePorEmprendimiento[0]!.codigo).toMatch(/^EMP-\d{3}$/);
    expect(data.tareasPorRevisar).toBeGreaterThanOrEqual(0);
    expect(data.asesorias.completadas).toBeGreaterThanOrEqual(0);
    expect(Array.isArray(data.agenda)).toBe(true);

    // Un docente sin asignaciones ve el tablero vacío, no el de su compañero.
    const other = await scenario.otherMentor.session.get('/api/dashboard/teacher');
    expect(other.status).toBe(200);
    expect(other.body.data.emprendimientos).toBe(0);
    expect(other.body.data.avancePorEmprendimiento).toEqual([]);
  });

  it('rechaza al administrador', async () => {
    expect((await admin.get('/api/dashboard/teacher')).status).toBe(403);
  });
});

describe('GET /dashboard/student', () => {
  it('devuelve el emprendimiento propio con las cuatro fases', async () => {
    const response = await scenario.student.session.get('/api/dashboard/student');
    expect(response.status).toBe(200);

    const data = response.body.data as {
      emprendimiento: { id: number; codigo: string; estadoAprobacion: string } | null;
      diagnostico: { estado: string } | null;
      acta: { estado: string } | null;
      tareas: { total: number; completadas: number; pendientes: number };
      asesorias: { realizadas: number; proximas: number };
      fases: { faseId: number | null; total: number; porcentaje: number }[];
      proximasAsesorias: unknown[];
      tareasPorCompletar: unknown[];
      eventos: unknown[];
      notificacionesSinLeer: number;
    };

    expect(data.emprendimiento?.id).toBe(scenario.emprendimientoId);
    expect(data.emprendimiento?.estadoAprobacion).toBe('Aprobado');
    expect(data.acta?.estado).toBe('Aprobada');
    expect(data.fases).toHaveLength(4);
    expect(data.fases.every((fase) => fase.faseId !== null)).toBe(true);
    expect(data.tareas.total).toBeGreaterThanOrEqual(0);
    expect(Array.isArray(data.eventos)).toBe(true);
    expect(data.notificacionesSinLeer).toBeGreaterThanOrEqual(0);
  });

  it('un estudiante sin emprendimiento recibe `null`, no un error', async () => {
    const response = await student.get('/api/dashboard/student');
    expect(response.status).toBe(200);
    expect(response.body.data.emprendimiento).toBeNull();
    expect(response.body.data.tareas.total).toBe(0);
    expect(response.body.data.fases).toEqual([]);
  });

  it('rechaza al docente', async () => {
    expect((await scenario.mentor.session.get('/api/dashboard/student')).status).toBe(403);
  });

  it('la cuenta Limitado no entra al tablero de trabajo', async () => {
    const response = await limited.get('/api/dashboard/student');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ACCOUNT_NOT_ACTIVE');
  });
});
