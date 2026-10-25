import type { AsignacionEstado } from '@sgemd/shared';
import type { PoolClient } from 'pg';
import { query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { notify } from '../../services/notify.js';
import { settingInt } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  CreateAssignmentInput,
  ListAssignmentsQuery,
  UpdateAssignmentInput,
} from './schemas.js';

/**
 * Asignaciones docente ↔ emprendimiento (FR-016, R9–R11, BR-001).
 *
 * Solo el administrador escribe (R9). Una asignación `activa` es el vínculo vigente entre
 * un mentor, el estudiante propietario y su emprendimiento; el índice único parcial
 * `asignaciones_una_activa_por_emprendimiento` garantiza como máximo una por
 * emprendimiento (R11). La baja es `estado = 'inactiva'`: la tabla no tiene
 * `fecha_eliminacion` (diagrama v2).
 *
 * Los dos topes docentes se comprueban **dentro** de la transacción y bajo un lock por
 * mentor, para que dos altas simultáneas no puedan superar el mismo tope (T07, FR-016).
 */

/* -------------------------------------------------------------------------------------
 * Lectura
 * ----------------------------------------------------------------------------------- */

interface PersonRef {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional: string;
}

export interface Assignment {
  id: number;
  fechaAsignacion: string;
  estado: AsignacionEstado;
  horasSemanales: number;
  mentor: PersonRef;
  estudiante: PersonRef;
  emprendimiento: {
    id: number;
    codigo: string;
    nombre: string;
    estadoAprobacion: string;
  };
}

type AssignmentRow = {
  id_asignacion: number;
  fecha_asignacion: Date;
  estado: string;
  horas_semanales: number;
  mentor_id: number;
  mentor_codigo: string;
  mentor_nombres: string;
  mentor_apellidos: string;
  mentor_correo: string;
  estudiante_id: number;
  estudiante_codigo: string;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_correo: string;
  emprendimiento_id: number;
  emprendimiento_codigo: string;
  emprendimiento_nombre: string;
  emprendimiento_estado: string;
};

const SELECT = `
  SELECT a.id_asignacion, a.fecha_asignacion, a.estado, a.horas_semanales,
         m.id_usuarios AS mentor_id, m.codigo AS mentor_codigo,
         m.nombres AS mentor_nombres, m.apellidos AS mentor_apellidos,
         m.correo_institucional AS mentor_correo,
         s.id_usuarios AS estudiante_id, s.codigo AS estudiante_codigo,
         s.nombres AS estudiante_nombres, s.apellidos AS estudiante_apellidos,
         s.correo_institucional AS estudiante_correo,
         e.id_emprendimiento AS emprendimiento_id, e.codigo AS emprendimiento_codigo,
         e.nombre AS emprendimiento_nombre,
         e.estado_aprobacion AS emprendimiento_estado
    FROM asignaciones a
    JOIN usuarios m ON m.id_usuarios = a.usuarios_id_mentor
    JOIN usuarios s ON s.id_usuarios = a.usuarios_id_estudiante
    JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
`;

function mapRow(row: AssignmentRow): Assignment {
  return {
    id: row.id_asignacion,
    fechaAsignacion: row.fecha_asignacion.toISOString(),
    estado: row.estado as AsignacionEstado,
    horasSemanales: row.horas_semanales,
    mentor: {
      id: row.mentor_id,
      codigo: row.mentor_codigo,
      nombres: row.mentor_nombres,
      apellidos: row.mentor_apellidos,
      correoInstitucional: row.mentor_correo,
    },
    estudiante: {
      id: row.estudiante_id,
      codigo: row.estudiante_codigo,
      nombres: row.estudiante_nombres,
      apellidos: row.estudiante_apellidos,
      correoInstitucional: row.estudiante_correo,
    },
    emprendimiento: {
      id: row.emprendimiento_id,
      codigo: row.emprendimiento_codigo,
      nombre: row.emprendimiento_nombre,
      estadoAprobacion: row.emprendimiento_estado,
    },
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'La asignación no existe.');
}

/**
 * Condición de alcance por rol (R10, R25, NFR-002).
 *
 * - Admin: todas.
 * - Docente: solo las suyas como mentor.
 * - Estudiante: solo las suyas como estudiante.
 *
 * Devuelve la condición SQL y enlaza el id del actor como parámetro.
 */
function scope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.DOCENTE) {
    return ` AND a.usuarios_id_mentor = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND a.usuarios_id_estudiante = ${bind(actor.id)}`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver asignaciones.');
}

export interface AssignmentPage {
  items: Assignment[];
  total: number;
  page: number;
  pageSize: number;
}

const SORT_COLUMNS: Record<ListAssignmentsQuery['sort'], string> = {
  fecha: 'a.fecha_asignacion',
  mentor: 'm.apellidos',
  estudiante: 's.apellidos',
  emprendimiento: 'e.nombre',
  horas: 'a.horas_semanales',
};

export async function listAssignments(
  options: ListAssignmentsQuery,
  actor: SessionUser,
): Promise<AssignmentPage> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`TRUE${scope(actor, bind)}`];

  if (options.estado) where.push(`a.estado = ${bind(options.estado)}`);
  if (options.mentorId !== undefined) {
    where.push(`a.usuarios_id_mentor = ${bind(options.mentorId)}`);
  }
  if (options.estudianteId !== undefined) {
    where.push(`a.usuarios_id_estudiante = ${bind(options.estudianteId)}`);
  }
  if (options.emprendimientoId !== undefined) {
    where.push(`a.emprendimiento_id_emprendimiento = ${bind(options.emprendimientoId)}`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(
      `(m.nombres ILIKE ${like} OR m.apellidos ILIKE ${like}
        OR s.nombres ILIKE ${like} OR s.apellidos ILIKE ${like}
        OR s.correo_institucional ILIKE ${like} OR s.codigo ILIKE ${like}
        OR e.nombre ILIKE ${like} OR e.codigo ILIKE ${like})`,
    );
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction}, a.id_asignacion ${direction}`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total
         FROM asignaciones a
         JOIN usuarios m ON m.id_usuarios = a.usuarios_id_mentor
         JOIN usuarios s ON s.id_usuarios = a.usuarios_id_estudiante
         JOIN emprendimiento e ON e.id_emprendimiento = a.emprendimiento_id_emprendimiento
         ${whereSql}`,
      countParams,
    ),
    query<AssignmentRow>(
      `${SELECT} ${whereSql} ORDER BY ${orderSql} LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapRow),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

export async function getAssignment(id: number, actor: SessionUser): Promise<Assignment> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const { rows } = await query<AssignmentRow>(
    `${SELECT} WHERE a.id_asignacion = $1${scope(actor, bind)}`,
    params,
  );

  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/** Rol vigente de un usuario, para validar los listados por mentor o estudiante. */
async function roleOf(id: number): Promise<number | null> {
  const { rows } = await query<{ rol: number }>(
    `SELECT roles_id_roles AS rol
       FROM usuarios
      WHERE id_usuarios = $1 AND fecha_eliminacion IS NULL`,
    [id],
  );
  return rows[0]?.rol ?? null;
}

/**
 * `GET /assignments/mentor/:id` — asignaciones de un docente (R10).
 *
 * El admin consulta a cualquiera; un docente solo a sí mismo. Un id que no sea un docente
 * vigente responde `404` para no revelar cuentas de otros roles.
 */
export async function listAssignmentsByMentor(
  mentorId: number,
  options: ListAssignmentsQuery,
  actor: SessionUser,
): Promise<AssignmentPage> {
  if (actor.rolId === ROLES.ESTUDIANTE) {
    throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver asignaciones de docentes.');
  }

  if (actor.rolId === ROLES.DOCENTE && actor.id !== mentorId) throw notFound();

  if ((await roleOf(mentorId)) !== ROLES.DOCENTE) {
    throw new AppError(404, 'NOT_FOUND', 'El docente no existe.');
  }

  return listAssignments({ ...options, mentorId }, actor);
}

/**
 * `GET /assignments/student/:id` — asignaciones de un estudiante (R10).
 *
 * El admin consulta a cualquiera; el estudiante solo las propias; un docente solo las de
 * un estudiante con el que tenga alguna asignación. El alcance del listado sigue
 * limitando al docente a sus propias filas.
 */
export async function listAssignmentsByStudent(
  estudianteId: number,
  options: ListAssignmentsQuery,
  actor: SessionUser,
): Promise<AssignmentPage> {
  if (actor.rolId === ROLES.ESTUDIANTE && actor.id !== estudianteId) throw notFound();

  if ((await roleOf(estudianteId)) !== ROLES.ESTUDIANTE) {
    throw new AppError(404, 'NOT_FOUND', 'El estudiante no existe.');
  }

  if (actor.rolId === ROLES.DOCENTE) {
    const { rows } = await query<{ existe: boolean }>(
      `SELECT EXISTS (
         SELECT 1 FROM asignaciones
          WHERE usuarios_id_mentor = $1 AND usuarios_id_estudiante = $2
       ) AS existe`,
      [actor.id, estudianteId],
    );
    if (!rows[0]?.existe) throw notFound();
  }

  return listAssignments({ ...options, estudianteId }, actor);
}

/* -------------------------------------------------------------------------------------
 * Escritura
 * ----------------------------------------------------------------------------------- */

type RawAssignment = {
  id_asignacion: number;
  estado: string;
  horas_semanales: number;
  fecha_asignacion: Date;
  usuarios_id_mentor: number;
  usuarios_id_estudiante: number;
  emprendimiento_id_emprendimiento: number;
};

async function findRaw(
  db: PoolClient,
  id: number,
  forUpdate = false,
): Promise<RawAssignment | null> {
  const { rows } = await db.query<RawAssignment>(
    `SELECT id_asignacion, estado, horas_semanales, fecha_asignacion,
            usuarios_id_mentor, usuarios_id_estudiante,
            emprendimiento_id_emprendimiento
       FROM asignaciones
      WHERE id_asignacion = $1${forUpdate ? ' FOR UPDATE' : ''}`,
    [id],
  );
  return rows[0] ?? null;
}

type MentorRow = {
  id: number;
  rol: number;
  estado: string;
  fecha_eliminacion: Date | null;
  codigo: string;
  nombres: string;
  apellidos: string;
};

/**
 * Docente destinatario de la asignación.
 *
 * Debe existir, estar vigente y tener rol Docente (`400`). Además debe estar `Activo`:
 * asignarle trabajo a una cuenta que no puede entrar a los módulos de trabajo (AQ-07
 * opción A) dejaría el vínculo sin efecto posible.
 */
async function loadMentor(db: PoolClient, id: number): Promise<MentorRow> {
  const { rows } = await db.query<MentorRow>(
    `SELECT id_usuarios AS id, roles_id_roles AS rol, estado, fecha_eliminacion,
            codigo, nombres, apellidos
       FROM usuarios
      WHERE id_usuarios = $1`,
    [id],
  );

  const mentor = rows[0];
  if (!mentor || mentor.fecha_eliminacion !== null) {
    throw new AppError(400, 'VALIDATION_ERROR', 'El docente no existe.', {
      mentorId: 'Selecciona un docente registrado',
    });
  }
  if (mentor.rol !== ROLES.DOCENTE) {
    throw new AppError(400, 'VALIDATION_ERROR', 'La asignación debe ser para un docente.', {
      mentorId: 'El mentor debe tener rol Docente',
    });
  }
  if (mentor.estado !== 'Activo') {
    throw new AppError(
      422,
      'MENTOR_NOT_ACTIVE',
      'Solo se puede asignar un docente con la cuenta Activa.',
      { mentorId: 'Activa la cuenta del docente antes de asignarlo' },
    );
  }

  return mentor;
}

type TargetRow = {
  id: number;
  codigo: string;
  nombre: string;
  fecha_eliminacion: Date | null;
  estudiante_id: number;
  estudiante_nombres: string;
  estudiante_apellidos: string;
};

async function findEntrepreneurship(db: PoolClient, id: number): Promise<TargetRow | null> {
  const { rows } = await db.query<TargetRow>(
    `SELECT e.id_emprendimiento AS id, e.codigo, e.nombre, e.fecha_eliminacion,
            u.id_usuarios AS estudiante_id, u.nombres AS estudiante_nombres,
            u.apellidos AS estudiante_apellidos
       FROM emprendimiento e
       JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
      WHERE e.id_emprendimiento = $1`,
    [id],
  );
  return rows[0] ?? null;
}

/** Emprendimiento vigente al que se asigna el docente. */
async function requireEntrepreneurship(db: PoolClient, id: number): Promise<TargetRow> {
  const target = await findEntrepreneurship(db, id);
  if (!target || target.fecha_eliminacion !== null) {
    throw new AppError(400, 'VALIDATION_ERROR', 'El emprendimiento no existe.', {
      emprendimientoId: 'Selecciona un emprendimiento vigente',
    });
  }
  return target;
}

/**
 * BR-001: la asignación definitiva exige un acta de compromiso `Aprobada`.
 *
 * No hay bandera de omisión: la comprobación se aplica siempre (§20.5 #12). Las actas se
 * cargan y revisan en la Etapa 9; hasta entonces se usan fixtures.
 */
async function assertActaApproved(db: PoolClient, emprendimientoId: number): Promise<void> {
  const { rows } = await db.query<{ aprobada: boolean }>(
    `SELECT EXISTS (
       SELECT 1 FROM actas
        WHERE emprendimiento_id_emprendimiento = $1
          AND estado = 'Aprobada'
     ) AS aprobada`,
    [emprendimientoId],
  );

  if (!rows[0]?.aprobada) {
    throw new AppError(
      422,
      'ACTA_NOT_APPROVED',
      'El emprendimiento no tiene un acta de compromiso aprobada.',
    );
  }
}

function alreadyActive(): AppError {
  return new AppError(
    409,
    'ASSIGNMENT_ALREADY_ACTIVE',
    'El emprendimiento ya tiene una asignación activa. Reasigna la existente.',
  );
}

/** R11: como máximo una asignación `activa` por emprendimiento. */
async function assertNoActiveAssignment(
  db: PoolClient,
  emprendimientoId: number,
  excludeId: number,
): Promise<void> {
  const { rows } = await db.query<{ existe: boolean }>(
    `SELECT EXISTS (
       SELECT 1 FROM asignaciones
        WHERE emprendimiento_id_emprendimiento = $1
          AND estado = 'activa'
          AND id_asignacion <> $2
     ) AS existe`,
    [emprendimientoId, excludeId],
  );

  if (rows[0]?.existe) throw alreadyActive();
}

/**
 * Serializa las comprobaciones de tope del mismo mentor.
 *
 * `pg_advisory_xact_lock` se libera al confirmar o revertir. Los ids se bloquean en orden
 * ascendente para que una reasignación A→B y otra B→A no puedan interbloquearse.
 */
async function lockMentors(db: PoolClient, ids: number[]): Promise<void> {
  for (const id of [...new Set(ids)].sort((a, b) => a - b)) {
    await db.query('SELECT pg_advisory_xact_lock(hashtext($1))', [
      `asignaciones:mentor:${id}`,
    ]);
  }
}

/**
 * Los dos topes de FR-016/R35, sobre las asignaciones **activas** del mentor:
 *
 * - horas: `SUM(horas_semanales) + nuevas ≤ carga_max_horas`;
 * - emprendimientos: `COUNT(DISTINCT emprendimiento) + 1 ≤ max_emprendimientos_docente`.
 *
 * `excludeId` deja fuera la fila que se está editando, para que ajustar solo las horas no
 * cuente dos veces la misma asignación. Un valor no sustituye al otro.
 */
async function assertCaps(
  db: PoolClient,
  mentorId: number,
  horasSemanales: number,
  excludeId: number,
): Promise<void> {
  const horasCap = await settingInt(db, 'carga_max_horas', 12);
  const emprendimientosCap = await settingInt(db, 'max_emprendimientos_docente', 12);

  const { rows } = await db.query<{ horas: string; emprendimientos: string }>(
    `SELECT COALESCE(SUM(horas_semanales), 0)::text AS horas,
            COUNT(DISTINCT emprendimiento_id_emprendimiento)::text AS emprendimientos
       FROM asignaciones
      WHERE usuarios_id_mentor = $1
        AND estado = 'activa'
        AND id_asignacion <> $2`,
    [mentorId, excludeId],
  );

  const horas = Number(rows[0]?.horas ?? 0);
  const emprendimientos = Number(rows[0]?.emprendimientos ?? 0);

  if (horas + horasSemanales > horasCap) {
    throw new AppError(
      422,
      'TEACHER_HOURS_LIMIT_REACHED',
      `La asignación llevaría al docente a ${horas + horasSemanales} h semanales; el máximo del programa es ${horasCap} h.`,
      { horasSemanales: `El tope es ${horasCap} h semanales por docente` },
    );
  }

  if (emprendimientos + 1 > emprendimientosCap) {
    throw new AppError(
      422,
      'TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED',
      `La asignación llevaría al docente a ${emprendimientos + 1} emprendimientos; el máximo del programa es ${emprendimientosCap}.`,
      { mentorId: `El tope es ${emprendimientosCap} emprendimientos por docente` },
    );
  }
}

function isUniqueViolation(error: unknown): boolean {
  return (error as { code?: string } | null)?.code === '23505';
}

/**
 * Alta (R9, R11, BR-001, T07, T15).
 *
 * El estudiante sale del emprendimiento; el cliente nunca lo elige. La transacción
 * incluye acta, unicidad, topes, inserción, auditoría y notificaciones: si algo falla, no
 * queda ni asignación ni aviso.
 */
export async function createAssignment(
  input: CreateAssignmentInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Assignment> {
  const id = await withTransaction(async (db) => {
    const target = await requireEntrepreneurship(db, input.emprendimientoId);

    await lockMentors(db, [input.mentorId]);
    const mentor = await loadMentor(db, input.mentorId);

    await assertActaApproved(db, target.id);
    await assertNoActiveAssignment(db, target.id, 0);
    await assertCaps(db, mentor.id, input.horasSemanales, 0);

    let nuevoId: number;
    try {
      const inserted = await db.query<{ id_asignacion: number }>(
        `INSERT INTO asignaciones
           (estado, horas_semanales, usuarios_id_mentor, usuarios_id_estudiante,
            emprendimiento_id_emprendimiento)
         VALUES ('activa', $1, $2, $3, $4)
         RETURNING id_asignacion`,
        [input.horasSemanales, mentor.id, target.estudiante_id, target.id],
      );
      nuevoId = inserted.rows[0]!.id_asignacion;
    } catch (error) {
      // Carrera con otra alta del mismo emprendimiento: el índice parcial decide.
      if (isUniqueViolation(error)) throw alreadyActive();
      throw error;
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_ASSIGNMENT,
      entidad: 'asignaciones',
      entidadId: nuevoId,
      valorNuevo: {
        mentorId: mentor.id,
        estudianteId: target.estudiante_id,
        emprendimientoId: target.id,
        horasSemanales: input.horasSemanales,
        estado: 'activa',
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: mentor.id,
      tipo: 'Sistema',
      mensaje: `Se te asignó el emprendimiento «${target.nombre}» (${target.codigo}) de ${target.estudiante_nombres} ${target.estudiante_apellidos}, con ${input.horasSemanales} h semanales.`,
      url: '/docente/emprendimientos',
      tipoObjeto: 'asignaciones',
      objetoId: nuevoId,
    });

    await notify(db, {
      usuarioId: target.estudiante_id,
      tipo: 'Sistema',
      mensaje: `Tu emprendimiento «${target.nombre}» tiene como docente asignado a ${mentor.nombres} ${mentor.apellidos}.`,
      url: `/estudiante/emprendimientos/${target.id}`,
      tipoObjeto: 'asignaciones',
      objetoId: nuevoId,
    });

    return nuevoId;
  });

  return getAssignment(id, actor);
}

function notActive(): AppError {
  return new AppError(
    422,
    'ASSIGNMENT_NOT_ACTIVE',
    'La asignación ya está inactiva y no se puede modificar.',
  );
}

/**
 * Reasignación y ajuste de horas (R9).
 *
 * Solo una asignación `activa` se edita. Si cambia el mentor se revalidan **sus** dos
 * topes (la asignación que llega cuenta como un emprendimiento más) y el acta del
 * emprendimiento; el mentor anterior libera carga automáticamente.
 */
export async function updateAssignment(
  id: number,
  input: UpdateAssignmentInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Assignment> {
  await withTransaction(async (db) => {
    const locked = await findRaw(db, id, true);
    if (!locked) throw notFound();
    if (locked.estado !== 'activa') throw notActive();

    const target = await requireEntrepreneurship(db, locked.emprendimiento_id_emprendimiento);

    const mentorId = input.mentorId ?? locked.usuarios_id_mentor;
    const horasSemanales = input.horasSemanales ?? locked.horas_semanales;
    const mentorChanged = mentorId !== locked.usuarios_id_mentor;

    await lockMentors(db, [locked.usuarios_id_mentor, mentorId]);
    const mentor = await loadMentor(db, mentorId);

    await assertActaApproved(db, target.id);
    await assertCaps(db, mentorId, horasSemanales, id);

    await db.query(
      `UPDATE asignaciones
          SET usuarios_id_mentor = $2, horas_semanales = $3
        WHERE id_asignacion = $1`,
      [id, mentorId, horasSemanales],
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_ASSIGNMENT,
      entidad: 'asignaciones',
      entidadId: id,
      valorAnterior: {
        mentorId: locked.usuarios_id_mentor,
        horasSemanales: locked.horas_semanales,
      },
      valorNuevo: { mentorId, horasSemanales },
      usuarioId: actor.id,
      ip,
    });

    if (mentorChanged) {
      await notify(db, {
        usuarioId: locked.usuarios_id_mentor,
        tipo: 'Sistema',
        mensaje: `Ya no tienes asignado el emprendimiento «${target.nombre}» (${target.codigo}).`,
        url: '/docente/emprendimientos',
        tipoObjeto: 'asignaciones',
        objetoId: id,
      });

      await notify(db, {
        usuarioId: mentor.id,
        tipo: 'Sistema',
        mensaje: `Se te asignó el emprendimiento «${target.nombre}» (${target.codigo}) de ${target.estudiante_nombres} ${target.estudiante_apellidos}, con ${horasSemanales} h semanales.`,
        url: '/docente/emprendimientos',
        tipoObjeto: 'asignaciones',
        objetoId: id,
      });

      await notify(db, {
        usuarioId: target.estudiante_id,
        tipo: 'Sistema',
        mensaje: `Tu docente asignado para «${target.nombre}» ahora es ${mentor.nombres} ${mentor.apellidos}.`,
        url: `/estudiante/emprendimientos/${target.id}`,
        tipoObjeto: 'asignaciones',
        objetoId: id,
      });
    } else {
      await notify(db, {
        usuarioId: mentor.id,
        tipo: 'Sistema',
        mensaje: `Las horas semanales de tu asignación en «${target.nombre}» ahora son ${horasSemanales}.`,
        url: '/docente/emprendimientos',
        tipoObjeto: 'asignaciones',
        objetoId: id,
      });
    }
  });

  return getAssignment(id, actor);
}

/**
 * `DELETE /assignments/:id` — baja lógica del vínculo (R9).
 *
 * La tabla no tiene `fecha_eliminacion`: la baja es `estado = 'inactiva'`, que libera el
 * cupo del emprendimiento (índice parcial) y la carga del docente. Una asignación ya
 * inactiva responde `422 ASSIGNMENT_NOT_ACTIVE`; para volver a vincular se crea una nueva.
 */
export async function deactivateAssignment(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  await withTransaction(async (db) => {
    const locked = await findRaw(db, id, true);
    if (!locked) throw notFound();
    if (locked.estado !== 'activa') throw notActive();

    const { rowCount } = await db.query(
      `UPDATE asignaciones
          SET estado = 'inactiva'
        WHERE id_asignacion = $1 AND estado = 'activa'`,
      [id],
    );

    if (rowCount === 0) throw notActive();

    const target = await findEntrepreneurship(db, locked.emprendimiento_id_emprendimiento);

    await audit(db, {
      accion: AUDIT_ACTIONS.DEACTIVATE_ASSIGNMENT,
      entidad: 'asignaciones',
      entidadId: id,
      valorAnterior: {
        mentorId: locked.usuarios_id_mentor,
        horasSemanales: locked.horas_semanales,
        estado: 'activa',
      },
      valorNuevo: { estado: 'inactiva' },
      usuarioId: actor.id,
      ip,
    });

    if (!target) return;

    await notify(db, {
      usuarioId: locked.usuarios_id_mentor,
      tipo: 'Sistema',
      mensaje: `Ya no tienes asignado el emprendimiento «${target.nombre}» (${target.codigo}).`,
      url: '/docente/emprendimientos',
      tipoObjeto: 'asignaciones',
      objetoId: id,
    });

    await notify(db, {
      usuarioId: locked.usuarios_id_estudiante,
      tipo: 'Sistema',
      mensaje: `Tu emprendimiento «${target.nombre}» quedó sin docente asignado.`,
      url: `/estudiante/emprendimientos/${target.id}`,
      tipoObjeto: 'asignaciones',
      objetoId: id,
    });
  });
}
