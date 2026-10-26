import { Button } from './Button.tsx';

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  /** Unidad para el resumen: «usuarios», «registros»… Se omite si no aplica. */
  unit?: string;
}

/**
 * Paginación de servidor. Muestra el rango real que devolvió la API y no
 * inventa páginas: si `total` es 0 no se pinta.
 */
export function Pagination({ page, pageSize, total, onPageChange, unit }: PaginationProps) {
  if (total <= 0) return null;

  const pages = Math.max(1, Math.ceil(total / pageSize));
  const current = Math.min(Math.max(1, page), pages);
  const from = (current - 1) * pageSize + 1;
  const to = Math.min(current * pageSize, total);

  return (
    <div className="paginacion">
      <span>
        Mostrando {from} a {to} de {total}
        {unit ? ` ${unit}` : ''}
      </span>
      <div className="pag">
        <Button
          size="sm"
          icon="izq"
          disabled={current <= 1}
          onClick={() => onPageChange(current - 1)}
          aria-label="Página anterior"
        >
          Anterior
        </Button>
        {Array.from({ length: pages }, (_, index) => index + 1).map((number) => (
          <Button
            key={number}
            size="sm"
            variant={number === current ? 'acento' : 'secundario'}
            aria-current={number === current ? 'page' : undefined}
            onClick={() => onPageChange(number)}
          >
            {number}
          </Button>
        ))}
        <Button
          size="sm"
          iconRight="der"
          disabled={current >= pages}
          onClick={() => onPageChange(current + 1)}
          aria-label="Página siguiente"
        >
          Siguiente
        </Button>
      </div>
    </div>
  );
}
