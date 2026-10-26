import type { CatalogItem } from '../api/types.ts';

/** Nombre de un ítem de catálogo por id; `—` si no está o no hay id. */
export function nameOf(items: CatalogItem[] | undefined, id: number | null): string {
  if (id === null || !items) return '—';
  return items.find((item) => item.id === id)?.nombre ?? '—';
}
