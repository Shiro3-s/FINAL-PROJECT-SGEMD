import { Router } from 'express';
import { query } from '../../db/pool.js';
import { requireAuth } from '../../middleware/auth.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData } from '../../utils/respond.js';

/**
 * Catálogos de solo lectura (master §13.1).
 *
 * Los 14 catálogos son datos de referencia: el cliente los pide para pintar selects y el
 * servidor los valida con `assertCatalogIds` antes de guardar un id. **No** se permite
 * escribir en ellos desde la API.
 *
 * Todos exigen sesión salvo `GET /type-doc`, que necesita el formulario de registro antes
 * de que exista una cuenta. Ninguno exige cuenta `Activo`: alimentan también la edición
 * del propio perfil, que AQ-07 opción A deja disponible a una cuenta `Limitado`.
 */
export const catalogsRouter = Router();

/**
 * Tabla, clave y etiqueta de cada catálogo simple (`id`, `nombre`).
 *
 * Son constantes del código: el nombre de la tabla nunca sale de la petición, así que no
 * hay forma de que un cliente consulte otra tabla por esta vía.
 */
const SIMPLE_CATALOGS = {
  '/roles': { table: 'roles', id: 'id_roles' },
  '/type-doc': { table: 'tipodocumentos', id: 'id_tipodocumentos' },
  '/type-users': { table: 'tipousuarios', id: 'id_tipousuarios' },
  '/uni-centers': { table: 'centrouniversitarios', id: 'id_centrouniversitarios' },
  '/type-pop': { table: 'tipopoblacion', id: 'id_tipopoblacion' },
  '/academic-programs': { table: 'programaacademico', id: 'id_programaacademico' },
  '/entrep-stage': { table: 'etapaemprendimiento', id: 'id_etapaemprendimiento' },
  '/plan-phase': { table: 'faseplan', id: 'id_faseplan' },
  '/econo-sector': { table: 'sectoreconomico', id: 'id_sectoreconomico' },
  '/mode': { table: 'modalidad', id: 'id_modalidad' },
  '/type-event': { table: 'tipo_evento', id: 'id_tipo_evento' },
  '/modules': { table: 'modulos', id: 'id_modulos' },
} as const;

type SimpleCatalogRoute = keyof typeof SIMPLE_CATALOGS;

function simpleCatalog(route: SimpleCatalogRoute) {
  const { table, id } = SIMPLE_CATALOGS[route];

  return asyncHandler(async (_req, res) => {
    const { rows } = await query<{ id: number; nombre: string }>(
      `SELECT ${id} AS id, nombre FROM ${table} ORDER BY nombre`,
    );
    sendData(res, { items: rows });
  });
}

// El único catálogo público: lo necesita el formulario de registro (D3).
catalogsRouter.get('/type-doc', simpleCatalog('/type-doc'));

// El resto exige sesión. Se registran en un solo punto para no repetir el middleware.
for (const route of Object.keys(SIMPLE_CATALOGS) as SimpleCatalogRoute[]) {
  if (route === '/type-doc') continue;
  catalogsRouter.get(route, requireAuth, simpleCatalog(route));
}

/**
 * `GET /municipalities` — residencia.
 *
 * `municipios` no tiene columna `nombre`: la etiqueta es la ciudad y el departamento va
 * aparte para que la interfaz pueda agrupar.
 */
catalogsRouter.get(
  '/municipalities',
  requireAuth,
  asyncHandler(async (_req, res) => {
    const { rows } = await query<{ id: number; nombre: string; departamento: string }>(
      `SELECT id_municipios AS id, ciudad AS nombre, departamento
         FROM municipios
        ORDER BY departamento, ciudad`,
    );
    sendData(res, { items: rows });
  }),
);

/** `GET /date-times` — bloques de agenda (`fecha_y_horarios`). */
catalogsRouter.get(
  '/date-times',
  requireAuth,
  asyncHandler(async (_req, res) => {
    const { rows } = await query<{
      id: number;
      fecha: string;
      hora_inicio: string;
      hora_fin: string;
    }>(
      `SELECT id_fecha_y_horarios AS id,
              to_char(fecha, 'YYYY-MM-DD') AS fecha,
              to_char(hora_inicio, 'HH24:MI') AS hora_inicio,
              to_char(hora_fin, 'HH24:MI') AS hora_fin
         FROM fecha_y_horarios
        ORDER BY fecha, hora_inicio`,
    );

    sendData(res, {
      items: rows.map((row) => ({
        id: row.id,
        nombre: `${row.fecha} ${row.hora_inicio}–${row.hora_fin}`,
        fecha: row.fecha,
        horaInicio: row.hora_inicio,
        horaFin: row.hora_fin,
      })),
    });
  }),
);
