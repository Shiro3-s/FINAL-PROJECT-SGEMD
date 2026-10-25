import { randomBytes } from 'node:crypto';
import type { PoolClient } from 'pg';
import { query, withTransaction } from '../../db/pool.js';
import { assertTransition } from '../../policy/accountTransitions.js';
import { ROLES } from '../../policy/roles.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { userCode } from '../../services/codes.js';
import {
  assertInstitutionalEmail,
  invitationMail,
  normalizeEmail,
  sendMailBestEffort,
  welcomeMail,
} from '../../services/email.js';
import { notify } from '../../services/notify.js';
import { issueOtp } from '../../services/otpCodes.js';
import { AppError } from '../../utils/AppError.js';
import { hashPassword } from '../../utils/password.js';
import type { PublicUser, SessionUser } from '../auth/types.js';
import { toPublicUser } from '../auth/types.js';
import { USER_SELECT, findUserById, mapUser, type UserRow } from './repository.js';
import type {
  CreateUserInput,
  ListUsersQuery,
  StateInput,
  UpdateMeInput,
  UpdateUserInput,
} from './schemas.js';

/* -------------------------------------------------------------------------------------
 * Utilidades internas
 * ----------------------------------------------------------------------------------- */

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'El usuario no existe.');
}

/** Catálogos que el diagrama referencia desde `usuarios`, con su tabla y su columna. */
const CATALOGS: Record<string, { table: string; column: string; label: string }> = {
  tipoDocumentoId: {
    table: 'tipodocumentos',
    column: 'id_tipodocumentos',
    label: 'tipo de documento',
  },
  programaAcademicoId: {
    table: 'programaacademico',
    column: 'id_programaacademico',
    label: 'programa académico',
  },
  centroUniversitarioId: {
    table: 'centrouniversitarios',
    column: 'id_centrouniversitarios',
    label: 'centro universitario',
  },
  municipioId: { table: 'municipios', column: 'id_municipios', label: 'municipio' },
  tipoPoblacionId: {
    table: 'tipopoblacion',
    column: 'id_tipopoblacion',
    label: 'tipo de población',
  },
  tipoUsuarioId: { table: 'tipousuarios', column: 'id_tipousuarios', label: 'tipo de usuario' },
};

/** Los nombres de tabla y columna son constantes del código, nunca datos del cliente. */
async function assertCatalogIds(db: PoolClient, input: Record<string, unknown>): Promise<void> {
  for (const [field, catalog] of Object.entries(CATALOGS)) {
    const value = input[field];
    if (typeof value !== 'number') continue;

    const { rows } = await db.query<{ id: number }>(
      `SELECT ${catalog.column} AS id FROM ${catalog.table} WHERE ${catalog.column} = $1`,
      [value],
    );

    if (!rows[0]) {
      throw new AppError(400, 'VALIDATION_ERROR', `El ${catalog.label} no existe.`, {
        [field]: `Selecciona un ${catalog.label} válido`,
      });
    }
  }
}

/** Unicidad de correo y documento (FR-016, R35). `excludeId` deja fuera la propia fila. */
async function assertUnique(
  db: PoolClient,
  correo: string,
  documento: string,
  excludeId = 0,
): Promise<void> {
  const { rows } = await db.query<{ correo: boolean; documento: boolean }>(
    `SELECT
       EXISTS (SELECT 1 FROM usuarios WHERE correo_institucional = $1 AND id_usuarios <> $3) AS correo,
       EXISTS (SELECT 1 FROM usuarios WHERE numero_documento = $2 AND id_usuarios <> $3) AS documento`,
    [correo, documento, excludeId],
  );

  if (rows[0]?.correo) {
    throw new AppError(409, 'EMAIL_TAKEN', 'Ya existe una cuenta con ese correo institucional.', {
      correoInstitucional: 'Este correo ya está registrado',
    });
  }
  if (rows[0]?.documento) {
    throw new AppError(409, 'DOCUMENT_TAKEN', 'Ya existe una cuenta con ese número de documento.', {
      numeroDocumento: 'Este documento ya está registrado',
    });
  }
}

/** Columna de cada campo editable, en el orden en que se aplican los cambios. */
const UPDATE_COLUMNS: Record<string, string> = {
  nombres: 'nombres',
  apellidos: 'apellidos',
  numeroDocumento: 'numero_documento',
  correoInstitucional: 'correo_institucional',
  tipoDocumentoId: 'tipo_documentos_id_tipo_documentos',
  nivelAcademico: 'nivel_academico',
  programaAcademicoId: 'programa_academico_id_programa_academico',
  centroUniversitarioId: 'centro_universitarios_id_centro_universitarios',
  municipioId: 'municipios_id_municipios',
  tipoPoblacionId: 'tipo_poblacion_id_tipo_poblacion',
  tipoUsuarioId: 'tipo_usuarios_id_tipo_usuarios',
};

const CURRENT_VALUE: Record<string, (user: SessionUser) => unknown> = {
  nombres: (user) => user.nombres,
  apellidos: (user) => user.apellidos,
  numeroDocumento: (user) => user.numeroDocumento,
  correoInstitucional: (user) => user.correoInstitucional,
  tipoDocumentoId: (user) => user.tipoDocumentoId,
  nivelAcademico: (user) => user.nivelAcademico,
  programaAcademicoId: (user) => user.programaAcademicoId,
  centroUniversitarioId: (user) => user.centroUniversitarioId,
  municipioId: (user) => user.municipioId,
  tipoPoblacionId: (user) => user.tipoPoblacionId,
  tipoUsuarioId: (user) => user.tipoUsuarioId,
};

/* -------------------------------------------------------------------------------------
 * Lectura
 * ----------------------------------------------------------------------------------- */

const SORT_COLUMNS: Record<ListUsersQuery['sort'], string> = {
  codigo: 'u.codigo',
  nombres: 'u.nombres',
  apellidos: 'u.apellidos',
  correo: 'u.correo_institucional',
  estado: 'u.estado',
  ultimaActividad: 'u.ultima_actividad',
};

export interface UserPage {
  items: PublicUser[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * Listado paginado. `forcedRole` lo usan `/users/students` y `/users/teachers`, que no
 * aceptan el filtro `rol` del cliente.
 */
export async function listUsers(
  options: ListUsersQuery,
  forcedRole?: number,
): Promise<UserPage> {
  const where: string[] = ['u.fecha_eliminacion IS NULL'];
  const params: unknown[] = [];

  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const rol = forcedRole ?? options.rol;
  if (rol !== undefined) where.push(`u.roles_id_roles = ${bind(rol)}`);
  if (options.estado) where.push(`u.estado = ${bind(options.estado)}`);

  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(
      `(u.nombres ILIKE ${like} OR u.apellidos ILIKE ${like} OR u.correo_institucional ILIKE ${like}
        OR u.codigo ILIKE ${like} OR u.numero_documento ILIKE ${like})`,
    );
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  const direction = options.order === 'desc' ? 'DESC' : 'ASC';
  const orderSql = `${SORT_COLUMNS[options.sort]} ${direction}, u.id_usuarios ASC`;
  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(`SELECT COUNT(*)::text AS total FROM usuarios u ${whereSql}`, countParams),
    query<UserRow>(
      `${USER_SELECT} ${whereSql} ORDER BY ${orderSql} LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map((row) => toPublicUser(mapUser(row))),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}

/**
 * Detalle de un usuario. Un no administrador solo puede leer su propia fila; cualquier
 * otro id responde **404**, no 403, para no revelar que existe (NFR-002).
 */
export async function getUser(id: number, actor: SessionUser): Promise<PublicUser> {
  if (actor.rolId !== ROLES.ADMIN && actor.id !== id) throw notFound();

  const user = await findUserById(id);
  if (!user) throw notFound();
  return toPublicUser(user);
}

/* -------------------------------------------------------------------------------------
 * Alta y edición
 * ----------------------------------------------------------------------------------- */

/**
 * Alta de estudiante o docente (R33, T06).
 *
 * - El código lo genera el servidor según el rol.
 * - La cuenta nace verificada: la coordinación conoce el correo institucional y la
 *   invitación se envía a esa misma dirección, así que exigir el OTP de registro dejaría
 *   la cuenta inutilizable.
 * - La contraseña es aleatoria e inservible; el usuario establece la suya con el código
 *   de invitación (`Recuperación`). El código nunca se devuelve en la respuesta.
 * - Si el transporte de correo falla, la cuenta queda creada y el usuario puede pedir un
 *   código nuevo en `/auth/forgot-password`; no se revierte el alta.
 */
export async function createUser(
  input: CreateUserInput,
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  const correo = normalizeEmail(input.correoInstitucional);
  await assertInstitutionalEmail(correo);

  const passwordHash = await hashPassword(randomBytes(32).toString('hex'));

  const created = await withTransaction(async (db) => {
    await assertUnique(db, correo, input.numeroDocumento);
    await assertCatalogIds(db, input as Record<string, unknown>);

    const codigo = await userCode(db, input.rolId);

    const { rows } = await db.query<{ id_usuarios: number }>(
      `INSERT INTO usuarios
         (codigo, nombres, apellidos, numero_documento, correo_institucional, password,
          nivel_academico, verificado, estado, roles_id_roles,
          tipo_documentos_id_tipo_documentos,
          programa_academico_id_programa_academico,
          centro_universitarios_id_centro_universitarios,
          municipios_id_municipios,
          tipo_poblacion_id_tipo_poblacion,
          tipo_usuarios_id_tipo_usuarios)
       VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE, $8, $9, $10, $11, $12, $13, $14, $15)
       RETURNING id_usuarios`,
      [
        codigo,
        input.nombres,
        input.apellidos,
        input.numeroDocumento,
        correo,
        passwordHash,
        input.nivelAcademico ?? null,
        input.estado,
        input.rolId,
        input.tipoDocumentoId,
        input.programaAcademicoId ?? null,
        input.centroUniversitarioId ?? null,
        input.municipioId ?? null,
        input.tipoPoblacionId ?? null,
        input.tipoUsuarioId ?? null,
      ],
    );

    const id = rows[0]!.id_usuarios;

    const plainCode = await issueOtp(db, {
      correo,
      proposito: 'Recuperación',
      usuarioId: id,
    });

    await audit(db, {
      accion: AUDIT_ACTIONS.CREATE_USER,
      entidad: 'usuarios',
      entidadId: id,
      valorNuevo: {
        codigo,
        correoInstitucional: correo,
        rolId: input.rolId,
        estado: input.estado,
        verificado: true,
      },
      usuarioId: actor.id,
      ip,
    });

    return { id, plainCode };
  });

  await sendMailBestEffort(correo, invitationMail(created.plainCode), 'invitación de cuenta');

  const user = await findUserById(created.id);
  return toPublicUser(user!);
}

/**
 * Edición por el administrador. El rol y el estado no se tocan aquí (P-18): el estado
 * tiene endpoints propios y el rol afecta asignaciones, topes y auditoría.
 */
export async function updateUser(
  id: number,
  input: UpdateUserInput,
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  const existing = await findUserById(id);
  if (!existing) throw notFound();

  const changes = input as Record<string, unknown>;

  if (typeof changes.correoInstitucional === 'string') {
    const correo = normalizeEmail(changes.correoInstitucional);
    await assertInstitutionalEmail(correo);
    changes.correoInstitucional = correo;
  }

  const correo = (changes.correoInstitucional as string | undefined) ?? existing.correoInstitucional;
  const documento =
    (changes.numeroDocumento as string | undefined) ?? existing.numeroDocumento;

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
    await assertUnique(db, correo, documento, id);
    await assertCatalogIds(db, changes);

    const sets: string[] = [];
    const params: unknown[] = [];
    for (const field of changedFields) {
      params.push(changes[field]);
      sets.push(`${UPDATE_COLUMNS[field]} = $${params.length}`);
    }

    if (sets.length === 0) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', {
        _: 'No hay cambios que aplicar',
      });
    }

    params.push(id);
    await db.query(`UPDATE usuarios SET ${sets.join(', ')} WHERE id_usuarios = $${params.length}`, params);

    await audit(db, {
      accion: AUDIT_ACTIONS.UPDATE_USER,
      entidad: 'usuarios',
      entidadId: id,
      valorAnterior,
      valorNuevo,
      usuarioId: actor.id,
      ip,
    });
  });

  const user = await findUserById(id);
  return toPublicUser(user!);
}

/** Edición del propio perfil: comparte el camino del administrador con un esquema menor. */
export async function updateMe(
  actor: SessionUser,
  input: UpdateMeInput,
  ip: string | null,
): Promise<PublicUser> {
  return updateUser(actor.id, input, actor, ip);
}

/* -------------------------------------------------------------------------------------
 * Ciclo de vida
 * ----------------------------------------------------------------------------------- */

/**
 * Aplica una transición de estado (BR-003, R34, T13).
 *
 * - Solo el administrador llega hasta aquí: lo garantiza el router.
 * - Nadie cambia el estado de su propia cuenta: con un único administrador activo, un
 *   autodesplazamiento dejaría el sistema sin quien pueda revertirlo.
 * - El `UPDATE` condiciona por el estado leído, así que dos peticiones simultáneas no
 *   pueden aplicar la misma transición dos veces.
 * - La auditoría guarda el estado anterior y el nuevo, y la notificación va en la misma
 *   transacción. El correo de bienvenida se envía después, sin revertir el cambio si
 *   falla.
 */
async function applyTransition(
  id: number,
  to: StateInput['estado'],
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  if (id === actor.id) {
    throw new AppError(
      422,
      'SELF_STATE_CHANGE_NOT_ALLOWED',
      'No puedes cambiar el estado de tu propia cuenta.',
    );
  }

  const existing = await findUserById(id);
  if (!existing) throw notFound();

  assertTransition(existing.estado, to);

  await withTransaction(async (db) => {
    const { rowCount } = await db.query(
      'UPDATE usuarios SET estado = $3 WHERE id_usuarios = $1 AND estado = $2',
      [id, existing.estado, to],
    );

    if (rowCount === 0) {
      throw new AppError(
        422,
        'INVALID_STATE_TRANSITION',
        'La cuenta cambió de estado mientras se procesaba la solicitud. Vuelve a intentarlo.',
      );
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.STATE_CHANGE,
      entidad: 'usuarios',
      entidadId: id,
      valorAnterior: { estado: existing.estado },
      valorNuevo: { estado: to },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: id,
      tipo: 'Sistema',
      mensaje:
        to === 'Activo'
          ? 'Tu cuenta fue activada. Ya puedes usar los módulos de trabajo.'
          : 'Tu cuenta fue desactivada. Contacta a la coordinación del programa.',
      tipoObjeto: 'usuarios',
      objetoId: id,
    });
  });

  if (to === 'Activo') {
    await sendMailBestEffort(
      existing.correoInstitucional,
      welcomeMail(existing.nombres),
      'bienvenida',
    );
  }

  const user = await findUserById(id);
  return toPublicUser(user!);
}

/** `POST /users/:id/validate` — activación de una cuenta `Limitado` (UC-1). */
export async function validateUser(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  const existing = await findUserById(id);
  if (!existing) throw notFound();
  if (existing.estado !== 'Limitado') {
    throw new AppError(
      422,
      'INVALID_STATE_TRANSITION',
      'Solo se puede validar una cuenta en estado Limitado.',
    );
  }
  return applyTransition(id, 'Activo', actor, ip);
}

/** `POST /users/:id/reactivate` — reactivación manual de una cuenta `Inactivo` (BR-005). */
export async function reactivateUser(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  const existing = await findUserById(id);
  if (!existing) throw notFound();
  if (existing.estado !== 'Inactivo') {
    throw new AppError(
      422,
      'INVALID_STATE_TRANSITION',
      'Solo se puede reactivar una cuenta en estado Inactivo.',
    );
  }
  return applyTransition(id, 'Activo', actor, ip);
}

/** `PATCH /users/:id/state` — selector genérico de `admin/usuarios`. */
export async function changeState(
  id: number,
  input: StateInput,
  actor: SessionUser,
  ip: string | null,
): Promise<PublicUser> {
  return applyTransition(id, input.estado, actor, ip);
}

/**
 * `POST /users/:id/reject` — rechazo de la activación (UC-1).
 *
 * El diagrama no tiene un estado «Rechazado» para la cuenta, así que el rechazo deja la
 * cuenta en `Limitado`, guarda el motivo en la auditoría y notifica al titular. Los
 * criterios de validación siguen abiertos (AQ-06); este endpoint solo exige el motivo.
 */
export async function rejectActivation(
  id: number,
  motivo: string,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  const existing = await findUserById(id);
  if (!existing) throw notFound();
  if (existing.estado !== 'Limitado') {
    throw new AppError(
      422,
      'INVALID_STATE_TRANSITION',
      'Solo se puede rechazar la activación de una cuenta en estado Limitado.',
    );
  }

  await withTransaction(async (db) => {
    await audit(db, {
      accion: AUDIT_ACTIONS.REJECT_ACTIVATION,
      entidad: 'usuarios',
      entidadId: id,
      valorAnterior: { estado: existing.estado },
      valorNuevo: { estado: existing.estado, motivo },
      usuarioId: actor.id,
      ip,
    });

    await notify(db, {
      usuarioId: id,
      tipo: 'Sistema',
      mensaje: `Tu solicitud de activación no fue aprobada. Motivo: ${motivo}`,
      tipoObjeto: 'usuarios',
      objetoId: id,
    });
  });
}

/**
 * `DELETE /users/:id` — baja lógica (R36, BR-006).
 *
 * No borra la fila: marca `fecha_eliminacion`. El usuario desaparece de los listados y su
 * cookie deja de valer en la petición siguiente (T04). La reversión (restaurar) no tiene
 * endpoint en el master §13.3 y queda registrada como decisión pendiente.
 */
export async function deleteUser(
  id: number,
  actor: SessionUser,
  ip: string | null,
): Promise<void> {
  if (id === actor.id) {
    throw new AppError(422, 'SELF_DELETE_NOT_ALLOWED', 'No puedes dar de baja tu propia cuenta.');
  }

  const existing = await findUserById(id);
  if (!existing) throw notFound();

  await withTransaction(async (db) => {
    await db.query('UPDATE usuarios SET fecha_eliminacion = now() WHERE id_usuarios = $1', [id]);

    await audit(db, {
      accion: AUDIT_ACTIONS.DELETE_USER,
      entidad: 'usuarios',
      entidadId: id,
      valorAnterior: {
        estado: existing.estado,
        correoInstitucional: existing.correoInstitucional,
        codigo: existing.codigo,
      },
      valorNuevo: { fechaEliminacion: new Date().toISOString() },
      usuarioId: actor.id,
      ip,
    });
  });
}
