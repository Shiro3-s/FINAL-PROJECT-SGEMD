import { query, withTransaction } from '../../db/pool.js';
import { AUDIT_ACTIONS, audit } from '../../services/audit.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type { AuditQuery, UpdateSettingsInput } from './schemas.js';

/**
 * Configuración del programa (FR-016, R35) y bitácora de auditoría del administrador.
 *
 * Los topes y plazos viven en `configuracion_programa`, no en el código: cambiar
 * `carga_max_horas` no exige un despliegue. La tabla no tiene `updated_at` (diagrama v2),
 * así que el «último cambio» se lee de `auditoria_eventos`, que es la fuente de verdad.
 */

export type TipoDato = 'int' | 'bool' | 'text' | 'date';

export interface SettingItem {
  clave: string;
  valor: string | null;
  tipoDato: TipoDato;
  descripcion: string | null;
  actualizadoPor: { id: number; nombres: string; apellidos: string } | null;
  fechaActualizacion: string | null;
}

export interface AuditEventItem {
  id: number;
  accion: string;
  entidad: string;
  entidadId: number | null;
  valorAnterior: unknown;
  valorNuevo: unknown;
  fecha: string;
  ip: string | null;
  actor: { id: number; nombres: string; apellidos: string } | null;
}

interface SettingRow {
  id_configuracion: number;
  clave: string;
  valor: string | null;
  tipo_dato: TipoDato;
  descripcion: string | null;
  actor_id: number | null;
  actor_nombres: string | null;
  actor_apellidos: string | null;
  fecha_actualizacion: Date | null;
}

const TIPOS: readonly TipoDato[] = ['int', 'bool', 'text', 'date'];

/**
 * Todos los enteros del programa son topes positivos (`carga_max_horas`,
 * `backup_retention_days`, `inactividad_dias`, …). Un `0` desactivaría el tope sin decirlo,
 * así que se rechaza; para «sin límite» la fila se deja en `null` donde el consumidor lo
 * admite.
 */
function normalizeInt(raw: string): string {
  if (!/^\d+$/.test(raw)) {
    throw new Error('El valor debe ser un número entero positivo');
  }
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isSafeInteger(parsed) || parsed < 1) {
    throw new Error('El valor debe ser un número entero mayor que cero');
  }
  return String(parsed);
}

function normalizeBool(raw: string): string {
  const value = raw.trim().toLowerCase();
  if (value !== 'true' && value !== 'false') {
    throw new Error('El valor debe ser true o false');
  }
  return value;
}

function normalizeDate(raw: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    throw new Error('Usa el formato AAAA-MM-DD');
  }
  const parsed = new Date(`${raw}T00:00:00Z`);
  // Rechaza 2026-02-31: `Date` la corre al 3 de marzo y el roundtrip ya no coincide.
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== raw) {
    throw new Error('La fecha no existe en el calendario');
  }
  return raw;
}

/**
 * Normaliza y valida el valor según el `tipo_dato` de la fila.
 *
 * `null` y la cadena vacía se guardan como `NULL`: es la forma de limpiar
 * `fecha_cierre_admisiones` o `acta_plazo_revision_dias`. Los lectores (`settingInt`,
 * `settingValue`) ya tratan `NULL` como «sin valor» y usan su respaldo.
 */
function normalizeValue(tipo: TipoDato, raw: string | null): string | null {
  if (raw === null || raw.trim() === '') return null;

  switch (tipo) {
    case 'int':
      return normalizeInt(raw.trim());
    case 'bool':
      return normalizeBool(raw);
    case 'date':
      return normalizeDate(raw.trim());
    case 'text':
      return raw.trim();
    default: {
      // Nunca se alcanza con el esquema actual; deja el error explícito si se añade un tipo.
      throw new Error(`Tipo de dato desconocido: ${String(tipo)}`);
    }
  }
}

function mapSetting(row: SettingRow): SettingItem {
  return {
    clave: row.clave,
    valor: row.valor,
    tipoDato: row.tipo_dato,
    descripcion: row.descripcion,
    actualizadoPor:
      row.actor_id === null
        ? null
        : {
            id: row.actor_id,
            nombres: row.actor_nombres ?? '',
            apellidos: row.actor_apellidos ?? '',
          },
    fechaActualizacion: row.fecha_actualizacion?.toISOString() ?? null,
  };
}

const SELECT_SETTINGS = `
  SELECT c.id_configuracion, c.clave, c.valor, c.tipo_dato, c.descripcion,
         u.id_usuarios AS actor_id, u.nombres AS actor_nombres,
         u.apellidos AS actor_apellidos, ultimo.fecha AS fecha_actualizacion
    FROM configuracion_programa c
    LEFT JOIN LATERAL (
      SELECT ae.fecha, ae.usuarios_id_usuarios
        FROM auditoria_eventos ae
       WHERE ae.entidad = 'configuracion_programa'
         AND ae.valor_nuevo->>'clave' = c.clave
       ORDER BY ae.fecha DESC, ae.id_auditoria DESC
       LIMIT 1
    ) ultimo ON TRUE
    LEFT JOIN usuarios u ON u.id_usuarios = ultimo.usuarios_id_usuarios`;

/** `GET /settings`: todas las claves con su tipo, descripción y último cambio. */
export async function listSettings(): Promise<{ items: SettingItem[] }> {
  const { rows } = await query<SettingRow>(`${SELECT_SETTINGS} ORDER BY c.id_configuracion`);
  return { items: rows.map(mapSetting) };
}

/**
 * `PUT /settings`: aplica el lote en una sola transacción.
 *
 * Las filas se bloquean en orden de clave para que dos administradores que guardan
 * tarjetas distintas no se bloqueen entre sí. Solo se audita lo que **cambia**: un guardado
 * sin diferencias no ensucia la bitácora. La respuesta trae la configuración completa ya
 * actualizada para que la pantalla no tenga que volver a pedirla.
 */
export async function updateSettings(
  input: UpdateSettingsInput,
  actor: SessionUser,
  ip: string | null,
): Promise<{ items: SettingItem[]; cambios: number }> {
  const cambios = await withTransaction(async (db) => {
    const claves = input.items.map((item) => item.clave);
    const { rows } = await db.query<SettingRow>(
      `SELECT id_configuracion, clave, valor, tipo_dato, descripcion,
              NULL::int AS actor_id, NULL::text AS actor_nombres,
              NULL::text AS actor_apellidos, NULL::timestamptz AS fecha_actualizacion
         FROM configuracion_programa
        WHERE clave = ANY($1)
        ORDER BY clave
          FOR UPDATE`,
      [claves],
    );

    const byClave = new Map(rows.map((row) => [row.clave, row]));

    const fields: Record<string, string> = {};
    const pending: { row: SettingRow; valor: string | null }[] = [];

    input.items.forEach((item, index) => {
      const row = byClave.get(item.clave);
      if (!row) {
        fields[`items.${index}.clave`] = 'La clave no existe en la configuración del programa';
        return;
      }
      if (!TIPOS.includes(row.tipo_dato)) {
        fields[`items.${index}.valor`] = 'La clave tiene un tipo de dato no soportado';
        return;
      }

      try {
        pending.push({ row, valor: normalizeValue(row.tipo_dato, item.valor) });
      } catch (error) {
        fields[`items.${index}.valor`] =
          error instanceof Error ? error.message : 'El valor no es válido';
      }
    });

    if (Object.keys(fields).length > 0) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', fields);
    }

    let applied = 0;
    for (const { row, valor } of pending) {
      if (row.valor === valor) continue;

      await db.query(
        'UPDATE configuracion_programa SET valor = $1 WHERE id_configuracion = $2',
        [valor, row.id_configuracion],
      );

      await audit(db, {
        accion: AUDIT_ACTIONS.UPDATE_SETTING,
        entidad: 'configuracion_programa',
        entidadId: row.id_configuracion,
        valorAnterior: { clave: row.clave, valor: row.valor },
        valorNuevo: { clave: row.clave, valor },
        usuarioId: actor.id,
        ip,
      });

      applied += 1;
    }

    return applied;
  });

  return { ...(await listSettings()), cambios };
}

interface AuditRow {
  id_auditoria: number;
  accion: string;
  entidad: string;
  entidad_id: number | null;
  valor_anterior: unknown;
  valor_nuevo: unknown;
  fecha: Date;
  ip: string | null;
  actor_id: number | null;
  actor_nombres: string | null;
  actor_apellidos: string | null;
}

function mapAudit(row: AuditRow): AuditEventItem {
  return {
    id: row.id_auditoria,
    accion: row.accion,
    entidad: row.entidad,
    entidadId: row.entidad_id,
    valorAnterior: row.valor_anterior,
    valorNuevo: row.valor_nuevo,
    fecha: row.fecha.toISOString(),
    ip: row.ip,
    actor:
      row.actor_id === null
        ? null
        : {
            id: row.actor_id,
            nombres: row.actor_nombres ?? '',
            apellidos: row.actor_apellidos ?? '',
          },
  };
}

/**
 * `GET /settings/audit`: bitácora de auditoría del administrador («Bitácora de
 * decisiones» del prototipo).
 *
 * Es de solo lectura y no se audita a sí misma: leer la bitácora no cambia el programa.
 * Los valores anterior/nuevo se devuelven tal como se guardaron (JSONB), que es lo que
 * permite reconstruir un cambio de tope o una aprobación.
 */
export async function listAudit(
  options: AuditQuery,
): Promise<{ items: AuditEventItem[]; total: number; page: number; pageSize: number }> {
  const params: unknown[] = [];
  const bind = (value: unknown): string => {
    params.push(value);
    return `$${params.length}`;
  };

  const where: string[] = [];

  if (options.accion) where.push(`a.accion = ${bind(options.accion)}`);
  if (options.entidad) where.push(`a.entidad = ${bind(options.entidad)}`);
  if (options.desde) where.push(`a.fecha >= ${bind(options.desde)}::date`);
  // `hasta` es inclusivo: se compara contra el inicio del día siguiente.
  if (options.hasta) where.push(`a.fecha < (${bind(options.hasta)}::date + INTERVAL '1 day')`);
  if (options.q) {
    const like = bind(`%${options.q}%`);
    where.push(`(a.accion ILIKE ${like} OR a.entidad ILIKE ${like})`);
  }

  const whereSql = where.length > 0 ? `WHERE ${where.join(' AND ')}` : '';
  const countParams = [...params];

  const limit = bind(options.pageSize);
  const offset = bind((options.page - 1) * options.pageSize);

  const [count, page] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM auditoria_eventos a ${whereSql}`,
      countParams,
    ),
    query<AuditRow>(
      `SELECT a.id_auditoria, a.accion, a.entidad, a.entidad_id, a.valor_anterior,
              a.valor_nuevo, a.fecha, a.ip,
              u.id_usuarios AS actor_id, u.nombres AS actor_nombres,
              u.apellidos AS actor_apellidos
         FROM auditoria_eventos a
         LEFT JOIN usuarios u ON u.id_usuarios = a.usuarios_id_usuarios
         ${whereSql}
        ORDER BY a.fecha DESC, a.id_auditoria DESC
        LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
  ]);

  return {
    items: page.rows.map(mapAudit),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
  };
}
