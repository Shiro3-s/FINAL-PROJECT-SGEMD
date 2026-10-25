import type { EmprendimientoEstado } from '@sgemd/shared';
import type { PoolClient, Pool } from 'pg';
import { pool, query, withTransaction } from '../../db/pool.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { assertCatalogIds } from '../../services/catalogs.js';
import { entrepreneurshipCode } from '../../services/codes.js';
import { notify } from '../../services/notify.js';
import { settingInt, settingValue } from '../../services/programSettings.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type {
  CreateEntrepreneurshipInput,
  ListEntrepreneurshipQuery,
  UpdateEntrepreneurshipInput,
} from './schemas.js';

/**
 * Emprendimientos (FR-012, BR-004, R37).
 *
 * El alta la hace el administrador y siempre nace `Pendiente`; aprobar o rechazar es una
 * decisión exclusiva de la coordinación y el rechazo exige motivo. El avance (`avance`)
 * no se escribe aquí: se deriva de las tareas completadas (R21, Etapa 7), así que el
 * cliente nunca lo envía.
 */

/* -------------------------------------------------------------------------------------
 * Lectura
 * ----------------------------------------------------------------------------------- */

type EntrepreneurshipRow = {
  id_emprendimiento: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  redes_sociales: string | null;
  estado_aprobacion: string;
  motivo_rechazo: string | null;
  es_paralelo: boolean;
  avance: number;
  etapa_id: number | null;
  etapa_nombre: string | null;
  sector_id: number | null;
  sector_nombre: string | null;
  centro_id: number | null;
  centro_nombre: string | null;
  estudiante_id: number;
  estudiante_codigo: string;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_correo: string;
};

export interface Entrepreneurship {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  redesSociales: string | null;
  estadoAprobacion: EmprendimientoEstado;
  motivoRechazo: string | null;
  esParalelo: boolean;
  avance: number;
  etapa: { id: number; nombre: string } | null;
  sector: { id: number; nombre: string } | null;
  centroUniversitario: { id: number; nombre: string } | null;
  estudiante: {
    id: number;
    codigo: string;
    nombres: string;
    apellidos: string;
    correoInstitucional: string;
  };
}

const SELECT = `
  SELECT e.id_emprendimiento, e.codigo, e.nombre, e.descripcion, e.redes_sociales,
         e.estado_aprobacion, e.motivo_rechazo, e.es_paralelo, e.avance,
         e.etapa_emprendimiento_id_etapa_emprendimiento AS etapa_id,
         et.nombre AS etapa_nombre,
         e.sector_economico_id_sector_economico AS sector_id,
         se.nombre AS sector_nombre,
         e.centro_universitarios_id_centro_universitarios AS centro_id,
         cu.nombre AS centro_nombre,
         u.id_usuarios AS estudiante_id, u.codigo AS estudiante_codigo,
         u.nombres AS estudiante_nombres, u.apellidos AS estudiante_apellidos,
         u.correo_institucional AS estudiante_correo
    FROM emprendimiento e
    JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
    LEFT JOIN etapaemprendimiento et
      ON et.id_etapaemprendimiento = e.etapa_emprendimiento_id_etapa_emprendimiento
    LEFT JOIN sectoreconomico se
      ON se.id_sectoreconomico = e.sector_economico_id_sector_economico
    LEFT JOIN centrouniversitarios cu
      ON cu.id_centrouniversitarios = e.centro_universitarios_id_centro_universitarios
`;

function mapRow(row: EntrepreneurshipRow): Entrepreneurship {
  return {
    id: row.id_emprendimiento,
    codigo: row.codigo,
    nombre: row.nombre,
    descripcion: row.descripcion,
    redesSociales: row.redes_sociales,
    estadoAprobacion: row.estado_aprobacion as EmprendimientoEstado,
    motivoRechazo: row.motivo_rechazo,
    esParalelo: row.es_paralelo,
    avance: row.avance,
    etapa:
      row.etapa_id === null ? null : { id: row.etapa_id, nombre: row.etapa_nombre ?? '' },
    sector:
      row.sector_id === null ? null : { id: row.sector_id, nombre: row.sector_nombre ?? '' },
    centroUniversitario:
      row.centro_id === null
        ? null
        : { id: row.centro_id, nombre: row.centro_nombre ?? '' },
    estudiante: {
      id: row.estudiante_id,
      codigo: row.estudiante_codigo,
      nombres: row.estudiante_nombres,
      apellidos: row.estudiante_apellidos,
      correoInstitucional: row.estudiante_correo,
    },
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El emprendimiento no existe.');
}

/**
 * Condición de alcance por rol (R4, R5, R25).
 *
 * - Admin: todos.
 * - Estudiante: solo los propios (`usuarios_id_usuarios = yo`).
 * - Docente: solo los que tiene asignados con una asignación `activa`.
 *
 * Devuelve la condición SQL y enlaza el id del actor como parámetro. El router ya limita
 * los roles permitidos; un rol inesperado se deniega igualmente aquí.
 */
function scope(actor: SessionUser, bind: (value: unknown) => string): string {
  if (actor.rolId === ROLES.ADMIN) return '';
  if (actor.rolId === ROLES.ESTUDIANTE) {
    return ` AND e.usuarios_id_usuarios = ${bind(actor.id)}`;
  }
  if (actor.rolId === ROLES.DOCENTE) {
    const id = bind(actor.id);
    return ` AND EXISTS (
               SELECT 1 FROM asignaciones a
                WHERE a.emprendimiento_id_emprendimiento = e.id_emprendimiento
                  AND a.usuarios_id_mentor = ${id}
                  AND a.estado = 'activa')`;
  }
  throw new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para ver emprendimientos.');
}

export interface EntrepreneurshipPage {
  items: Entrepreneurship[];
  total: number;
  page: number;
  pageSize: number;
}

const SORT_COLUMNS: Record<ListEntrepreneurshipQuery['sort'], string> = {
  codigo: 'e.codigo',
  nombre: 'e.nombre',
  estadoAprobacion: 'e.estado_aprobacion',
  avance: 'e.avance',
  estudiante: 'u.apellidos',
};

export async function listEntrepreneurship(
  options: ListEntrepreneurshipQuery,
  actor: SessionUser,
): Promise<EntrepreneurshipPage> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where = [`e.fecha_eliminacion IS NULL${scope(actor, bind)}`];

  if (options.estado) where.push(`e.estado_aprobacion = ${bind(options.estado)}`);
  if (options.etapaId !== undefined) {
    where.push(`e.etapa_emprendimiento_id_etapa_emprendimiento = ${bind(options.etapaId)}`);
  }
  if (options.sectorId !== undefined) {
    where.push(`e.sector_economico_id_sector_economico = ${bind(options.sectorId)}`);
  }
  if (options.estudianteId !== undefined) {
    where.push(`e.usuarios_id_usuarios = ${bind(options.estudianteId)}`);
  }
  if (options.paralelo !== undefined) {
    where.push(`e.es_paralelo = ${bind(options.paralelo)}`);
  }
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(`(e.nombre ILIKE ${like} OR e.codigo ILIKE ${like})`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction}, e.id_emprendimiento ASC`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM emprendimiento e
         JOIN usuarios u ON u.id_usuarios = e.usuarios_id_usuarios
         ${whereSql}`,
      countParams,
    ),
    query<EntrepreneurshipRow>(
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

/**
 * Detalle con alcance. Un emprendimiento ajeno responde **404**, no 403, para no revelar
 * que existe (NFR-002).
 */
export async function getEntrepreneurship(
  id: number,
  actor: SessionUser,
): Promise<Entrepreneurship> {
  const params: unknown[] = [id];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };
  const where = `WHERE e.id_emprendimiento = $1 AND e.fecha_eliminacion IS NULL${scope(actor, bind)}`;

  const { rows } = await query<EntrepreneurshipRow>(`${SELECT} ${where}`, params);
  if (!rows[0]) throw notFound();
  return mapRow(rows[0]);
}

/* -------------------------------------------------------------------------------------
 * Escritura
 * ----------------------------------------------------------------------------------- */

type RawRow = {
  id_emprendimiento: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  redes_sociales: string | null;
  estado_aprobacion: string;
  motivo_rechazo: string | null;
  es_paralelo: boolean;
  etapa_emprendimiento_id_etapa_emprendimiento: number | null;
  sector_economico_id_sector_economico: number | null;
  centro_universitarios_id_centro_universitarios: number | null;
  usuarios_id_usuarios: number;
};

/** Fila cruda (sin alcance) para autorizar y auditar. Solo la usan rutas de escritura. */
async function findRaw(db: PoolClient | Pool, id: number): Promise<RawRow | null> {
  const { rows } = await db.query<RawRow>(
    `SELECT id_emprendimiento, codigo, nombre, descripcion, redes_sociales,
            estado_aprobacion, motivo_rechazo, es_paralelo,
            etapa_emprendimiento_id_etapa_emprendimiento,
            sector_economico_id_sector_economico,
            centro_universitarios_id_centro_universitarios,
            usuarios_id_usuarios
       FROM emprendimiento
      WHERE id_emprendimiento = $1 AND fecha_eliminacion IS NULL`,
    [id],
  );
  return rows[0] ?? null;
}

/** Etapa con la que nace un emprendimiento, según `configuracion_programa`. */
async function initialStageId(db: PoolClient): Promise<number> {
  const nombre = await settingValue(db, 'etapa_inicial');
  if (!nombre) {
    throw new AppError(
      422,
      'INITIAL_STAGE_NOT_CONFIGURED',
      'El programa no tiene una etapa inicial configurada.',
    );
  }

  const { rows } = await db.query<{ id: number }>(
    'SELECT id_etapaemprendimiento AS id FROM etapaemprendimiento WHERE nombre = $1',
    [nombre],
  );

  if (!rows[0]) {
    throw new AppError(
      422,
      'INITIAL_STAGE_NOT_CONFIGURED',
      'La etapa inicial configurada no existe en el catálogo de etapas.',
    );
  }
  return rows[0].id;
}

/**
 * BR-004 + D5: un emprendimiento activo y como máximo `paralelos_maximos` paralelos
 * pendientes o aprobados.
 *
 * Los `Rechazado` no cuentan: se conservan con su motivo, pero no ocupan cupo.
 */
async function assertParallelAllowed(
  db: PoolClient,
  estudianteId: number,
  esParalelo: boolean,
): Promise<void> {
  const { rows } = await db.query<{ total: string; paralelos: string }>(
    `SELECT COUNT(*)::text AS total,
            COUNT(*) FILTER (WHERE es_paralelo)::text AS paralelos
       FROM emprendimiento
      WHERE usuarios_id_usuarios = $1
        AND fecha_eliminacion IS NULL
        AND estado_aprobacion <> 'Rechazado'`,
    [estudianteId],
  );

  const total = Number(rows[0]?.total ?? 0);
  const paralelos = Number(rows[0]?.paralelos ?? 0);

  if (total === 0) {
    if (esParalelo) {
      throw new AppError(
        422,
        'NOT_A_PARALLEL',
        'El primer emprendimiento del estudiante no puede registrarse como paralelo.',
      );
    }
    return;
  }

  if (!esParalelo) {
    throw new AppError(
      422,
      'PARALLEL_REQUIRED',
      'El estudiante ya tiene un emprendimiento vigente. Un segundo requiere autorización de paralelo.',
    );
  }

  const cap = await settingInt(db, 'paralelos_maximos', 1);
  if (paralelos >= cap) {
    throw new AppError(
      422,
      'PARALLEL_LIMIT_REACHED',
      `El estudiante ya alcanzó el máximo de ${cap} emprendimiento(s) paralelo(s).`,
    );
  }
}

/**
 * Alta (FR-012, R37). Nace `Pendiente`; el propietario debe ser un estudiante vigente.
 *
 * `esParalelo` no describe el emprendimiento: es la autorización expresa de la
 * coordinación para el segundo. Por eso se valida contra los emprendimientos vigentes del
 * estudiante y no se acepta como un dato más.
 */
export async function createEntrepreneurship(
  input: CreateEntrepreneurshipInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Entrepreneurship> {
  const id = await withTransaction(async (db) => {
    const owner = await db.query<{ rol: number }>(
      `SELECT roles_id_roles AS rol
         FROM usuarios
        WHERE id_usuarios = $1 AND fecha_eliminacion IS NULL`,
      [input.estudianteId],
    );

    if (!owner.rows[0]) {
      throw new AppError(400, 'VALIDATION_ERROR', 'El estudiante propietario no existe.', {
        estudianteId: 'Selecciona un estudiante válido',
      });
    }
    if (owner.rows[0].rol !== ROLES.ESTUDIANTE) {
      throw new AppError(
        400,
        'VALIDATION_ERROR',
        'El propietario de un emprendimiento debe ser un estudiante.',
        { estudianteId: 'El propietario debe tener rol Estudiante' },
      );
    }

    await assertCatalogIds(db, input as Record<string, unknown>);
    const etapaId = input.etapaId ?? (await initialStageId(db));
    await assertParallelAllowed(db, input.estudianteId, input.esParalelo);

    const codigo = await entrepreneurshipCode(db);

    const inserted = await db.query<{ id_emprendimiento: number }>(
      `INSERT INTO emprendimiento
         (codigo, nombre, descripcion, redes_sociales, estado_aprobacion, es_paralelo,
          avance, etapa_emprendimiento_id_etapa_emprendimiento,
          sector_economico_id_sector_economico,
          centro_universitarios_id_centro_universitarios, usuarios_id_usuarios)
       VALUES ($1, $2, $3, $4, 'Pendiente', $5, 0, $6, $7, $8, $9)
       RETURNING id_emprendimiento`,
      [
        codigo,
        input.nombre,
        input.descripcion ?? null,
        input.redesSociales ?? null,
        input.esParalelo,
        etapaId,
        input.sectorId ?? null,
        input.centroUniversitarioId ?? null,
        input.estudianteId,
      ],
    );

    const nuevoId = inserted.rows[0]!.id_emprendimiento;

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_ENTREPRENEURSHIP,
      entidad: 'emprendimiento',
      entidadId: nuevoId,
      valorNuevo: {
        codigo,
        nombre: input.nombre,
        estudianteId: input.estudianteId,
        esParalelo: input.esParalelo,
        estadoAprobacion: 'Pendiente',
      },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: input.estudianteId,
      tipo: 'Sistema',
      mensaje: `Tu emprendimiento «${input.nombre}» quedó registrado y está pendiente de aprobación.`,
      tipoObjeto: 'emprendimiento',
      objetoId: nuevoId,
    });

    return nuevoId;
  });

  return getEntrepreneurship(id, actor);
}

/** Columnas editables y su valor actual, para auditar solo lo que cambió. */
const UPDATE_COLUMNS: Record<string, string> = {
  nombre: 'nombre',
  descripcion: 'descripcion',
  redesSociales: 'redes_sociales',
  sectorId: 'sector_economico_id_sector_economico',
  etapaId: 'etapa_emprendimiento_id_etapa_emprendimiento',
  centroUniversitarioId: 'centro_universitarios_id_centro_universitarios',
};

const CURRENT_VALUE: Record<string, (row: RawRow) => unknown> = {
  nombre: (row) => row.nombre,
  descripcion: (row) => row.descripcion,
  redesSociales: (row) => row.redes_sociales,
  sectorId: (row) => row.sector_economico_id_sector_economico,
  etapaId: (row) => row.etapa_emprendimiento_id_etapa_emprendimiento,
  centroUniversitarioId: (row) => row.centro_universitarios_id_centro_universitarios,
};

/**
 * Edición (master §13.2). El administrador cambia cualquier campo descriptivo; el
 * estudiante propietario solo nombre, descripción y redes sociales. El propietario, el
 * estado de aprobación, el motivo de rechazo, el paralelo y el avance no se editan aquí.
 */
export async function updateEntrepreneurship(
  id: number,
  input: UpdateEntrepreneurshipInput,
  actor: SessionUser,
  ip: string | null,
): Promise<Entrepreneurship> {
  const existing = await findRaw(pool, id);
  if (!existing) throw notFound();

  const isAdmin = actor.rolId === ROLES.ADMIN;
  const isOwner = existing.usuarios_id_usuarios === actor.id;
  if (!isAdmin && !isOwner) throw notFound();

  if (!isAdmin) {
    const blocked = ['sectorId', 'etapaId', 'centroUniversitarioId'].filter(
      (field) => field in (input as Record<string, unknown>),
    );
    if (blocked.length > 0) {
      throw new AppError(
        403,
        'FIELD_NOT_ALLOWED',
        'Como estudiante solo puedes editar el nombre, la descripción y las redes sociales.',
      );
    }
  }

  const changes = input as Record<string, unknown>;
  const valorAnterior: Record<string, unknown> = {};
  const valorNuevo: Record<string, unknown> = {};
  const changedFields: string[] = [];

  for (const field of Object.keys(UPDATE_COLUMNS)) {
    if (!(field in changes)) continue;
    changedFields.push(field);

    const before = CURRENT_VALUE[field]!(existing);
    const after = changes[field];
    if (before !== after) {
      valorAnterior[field] = before;
      valorNuevo[field] = after;
    }
  }

  await withTransaction(async (db) => {
    await assertCatalogIds(db, changes);

    const sets: string[] = [];
    const params: unknown[] = [];
    for (const field of changedFields) {
      params.push(changes[field]);
      sets.push(`${UPDATE_COLUMNS[field]} = $${params.length}`);
    }

    params.push(id);
    await db.query(
      `UPDATE emprendimiento SET ${sets.join(', ')} WHERE id_emprendimiento = $${params.length}`,
      params,
    );

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_ENTREPRENEURSHIP,
      entidad: 'emprendimiento',
      entidadId: id,
      valorAnterior,
      valorNuevo,
      usuarioId: actor.id,
      ip,
    });
  });

  return getEntrepreneurship(id, actor);
}

/**
 * `DELETE /entrepreneurship/:id` — baja lógica (BR-006, R36).
 *
 * Marca `fecha_eliminacion`: el emprendimiento sale de listados y detalles. El borrado
 * físico de adjuntos en cascada llegará con el módulo de adjuntos (Etapa 7).
 */
export async function deleteEntrepreneurship(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const existing = await findRaw(pool, id);
  if (!existing) throw notFound();

  await withTransaction(async (db) => {
    const { rowCount } = await db.query(
      `UPDATE emprendimiento
          SET fecha_eliminacion = now()
        WHERE id_emprendimiento = $1 AND fecha_eliminacion IS NULL`,
      [id],
    );

    if (rowCount === 0) throw notFound();

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_ENTREPRENEURSHIP,
      entidad: 'emprendimiento',
      entidadId: id,
      valorAnterior: {
        codigo: existing.codigo,
        nombre: existing.nombre,
        estadoAprobacion: existing.estado_aprobacion,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });
  });
}

/* -------------------------------------------------------------------------------------
 * Aprobación y rechazo (BR-004, T11, T12)
 * ----------------------------------------------------------------------------------- */

function invalidApprovalState(): AppError {
  return new AppError(
    422,
    'INVALID_APPROVAL_STATE',
    'Solo se puede aprobar o rechazar un emprendimiento en estado Pendiente.',
  );
}

/** Bloquea la fila y exige que siga `Pendiente`. */
async function lockPending(db: PoolClient, id: number): Promise<RawRow> {
  const { rows } = await db.query<RawRow>(
    `SELECT id_emprendimiento, codigo, nombre, descripcion, redes_sociales,
            estado_aprobacion, motivo_rechazo, es_paralelo,
            etapa_emprendimiento_id_etapa_emprendimiento,
            sector_economico_id_sector_economico,
            centro_universitarios_id_centro_universitarios,
            usuarios_id_usuarios
       FROM emprendimiento
      WHERE id_emprendimiento = $1 AND fecha_eliminacion IS NULL
      FOR UPDATE`,
    [id],
  );

  const row = rows[0];
  if (!row) throw notFound();
  if (row.estado_aprobacion !== 'Pendiente') throw invalidApprovalState();
  return row;
}

/**
 * `POST /entrepreneurship/:id/approve` — única vía a `Aprobado` (R37).
 *
 * El `UPDATE` condiciona por `Pendiente` además del bloqueo de fila: dos aprobaciones
 * simultáneas no pueden escribir dos veces. Auditoría y notificación van en la misma
 * transacción que el cambio.
 */
export async function approveEntrepreneurship(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<Entrepreneurship> {
  await withTransaction(async (db) => {
    const existing = await lockPending(db, id);

    const { rowCount } = await db.query(
      `UPDATE emprendimiento
          SET estado_aprobacion = 'Aprobado', motivo_rechazo = NULL
        WHERE id_emprendimiento = $1 AND estado_aprobacion = 'Pendiente'`,
      [id],
    );

    if (rowCount === 0) throw invalidApprovalState();

    await audit(db, {
      accion: AUDIT_ACTIONS.APPROVE_ENTREPRENEURSHIP,
      entidad: 'emprendimiento',
      entidadId: id,
      valorAnterior: { estadoAprobacion: existing.estado_aprobacion },
      valorNuevo: { estadoAprobacion: 'Aprobado' },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: existing.usuarios_id_usuarios,
      tipo: 'Sistema',
      mensaje: `Tu emprendimiento «${existing.nombre}» fue aprobado.`,
      tipoObjeto: 'emprendimiento',
      objetoId: id,
    });
  });

  return getEntrepreneurship(id, actor);
}

/**
 * `POST /entrepreneurship/:id/reject` — rechazo con motivo obligatorio (BR-004, T12).
 *
 * El motivo se guarda en `motivo_rechazo` (el `CHECK` de la tabla también lo exige) y se
 * envía al estudiante en la notificación.
 */
export async function rejectEntrepreneurship(
  id: number,
  motivo: string,
  actor: SessionUser,
  ip: string | null,
): Promise<Entrepreneurship> {
  await withTransaction(async (db) => {
    const existing = await lockPending(db, id);

    const { rowCount } = await db.query(
      `UPDATE emprendimiento
          SET estado_aprobacion = 'Rechazado', motivo_rechazo = $2
        WHERE id_emprendimiento = $1 AND estado_aprobacion = 'Pendiente'`,
      [id, motivo],
    );

    if (rowCount === 0) throw invalidApprovalState();

    await audit(db, {
      accion: AUDIT_ACTIONS.REJECT_ENTREPRENEURSHIP,
      entidad: 'emprendimiento',
      entidadId: id,
      valorAnterior: { estadoAprobacion: existing.estado_aprobacion },
      valorNuevo: { estadoAprobacion: 'Rechazado', motivo },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: existing.usuarios_id_usuarios,
      tipo: 'Sistema',
      mensaje: `Tu emprendimiento «${existing.nombre}» fue rechazado. Motivo: ${motivo}`,
      tipoObjeto: 'emprendimiento',
      objetoId: id,
    });
  });

  return getEntrepreneurship(id, actor);
}
