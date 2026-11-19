import type { PoolClient } from 'pg';
import { AppError } from '../utils/AppError.js';

/**
 * Verificación de ids de catálogo antes de escribir.
 *
 * Las claves foráneas ya impedirían guardar un id inexistente, pero con un error de base
 * de datos (`500`). Aquí se traduce a un `400 VALIDATION_ERROR` con el campo señalado, que
 * es lo que la interfaz puede mostrar junto al select.
 *
 * Los nombres de tabla y columna son constantes del código; nunca salen de la petición.
 */
export interface CatalogRef {
  table: string;
  column: string;
  label: string;
}

export const CATALOG_REFS: Readonly<Record<string, CatalogRef>> = {
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
  sectorId: {
    table: 'sectoreconomico',
    column: 'id_sectoreconomico',
    label: 'sector económico',
  },
  etapaId: {
    table: 'etapaemprendimiento',
    column: 'id_etapaemprendimiento',
    label: 'etapa del emprendimiento',
  },
};

/**
 * Comprueba cada campo del objeto que corresponda a un catálogo y traiga un número.
 * Los campos ausentes o `null` se ignoran: limpiar un catálogo opcional es válido.
 */
export async function assertCatalogIds(
  db: PoolClient,
  input: Record<string, unknown>,
): Promise<void> {
  for (const [field, ref] of Object.entries(CATALOG_REFS)) {
    const value = input[field];
    if (typeof value !== 'number') continue;

    const { rows } = await db.query<{ id: number }>(
      `SELECT ${ref.column} AS id FROM ${ref.table} WHERE ${ref.column} = $1`,
      [value],
    );

    if (!rows[0]) {
      throw new AppError(400, 'VALIDATION_ERROR', `El ${ref.label} no existe.`, {
        [field]: `Selecciona un ${ref.label} válido`,
      });
    }
  }
}
