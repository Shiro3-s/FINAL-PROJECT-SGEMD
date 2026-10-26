import { useQuery } from '@tanstack/react-query';
import { apiGet } from '../api/client.ts';
import type { CatalogItem, DateTimeItem, MunicipalityItem } from '../api/types.ts';

/**
 * Catálogos de solo lectura (`GET /api/*` de la Etapa 5).
 *
 * Cambian muy poco y son la fuente de los `<select>` de todo el sistema, así
 * que se cachean indefinidamente dentro de la sesión y solo se invalidan al
 * recargar la aplicación. `type-doc` es público: el registro lo necesita antes
 * de que exista una cuenta.
 */
export const catalogKeys = {
  all: ['catalog'] as const,
  list: (path: string) => ['catalog', path] as const,
};

interface CatalogPage<T> {
  items: T[];
}

export function useCatalog<T extends CatalogItem>(path: string, enabled = true) {
  return useQuery({
    queryKey: catalogKeys.list(path),
    queryFn: async () => {
      const page = await apiGet<CatalogPage<T>>(path);
      return page.items;
    },
    staleTime: Number.POSITIVE_INFINITY,
    enabled,
  });
}

export const useRoles = () => useCatalog('/roles');
export const useTypeDocuments = () => useCatalog('/type-doc');
export const useTypeUsers = () => useCatalog('/type-users');
export const useUniversityCenters = () => useCatalog('/uni-centers');
export const usePopulationTypes = () => useCatalog('/type-pop');
export const useAcademicPrograms = () => useCatalog('/academic-programs');
export const useEntrepreneurshipStages = () => useCatalog('/entrep-stage');
export const usePlanPhases = () => useCatalog('/plan-phase');
export const useEconomicSectors = () => useCatalog('/econo-sector');
export const useModalities = () => useCatalog('/mode');
export const useEventTypes = () => useCatalog('/type-event');
export const useModules = () => useCatalog('/modules');

export function useMunicipalities() {
  return useQuery({
    queryKey: catalogKeys.list('/municipalities'),
    queryFn: async () => {
      const page = await apiGet<CatalogPage<MunicipalityItem>>('/municipalities');
      return page.items;
    },
    staleTime: Number.POSITIVE_INFINITY,
  });
}

export function useDateTimes() {
  return useQuery({
    queryKey: catalogKeys.list('/date-times'),
    queryFn: async () => {
      const page = await apiGet<CatalogPage<DateTimeItem>>('/date-times');
      return page.items;
    },
    staleTime: Number.POSITIVE_INFINITY,
  });
}
