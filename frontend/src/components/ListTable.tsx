import type { Paginated } from '../api/types.ts';
import { Button } from './Button.tsx';
import { DataTable, type Column } from './DataTable.tsx';
import { Pagination } from './Pagination.tsx';
import { EmptyState, ErrorState, LoadingState } from './States.tsx';

interface QueryLike<T> {
  isPending: boolean;
  isError: boolean;
  error: unknown;
  data: Paginated<T> | undefined;
  refetch: () => unknown;
}

interface ListTableProps<T> {
  query: QueryLike<T>;
  columns: Column<T>[];
  rowKey: (row: T) => string | number;
  caption: string;
  /** Qué se está listando, en plural y minúsculas: «tareas», «usuarios»… */
  unit: string;
  emptyTitle: string;
  emptyText: string;
  onPageChange: (page: number) => void;
  emptyAction?: React.ReactNode;
  flush?: boolean;
}

/**
 * Tabla paginada con los tres estados obligatorios.
 *
 * Todas las listas del sistema comparten aquí la carga, el error con reintento,
 * el vacío explicativo y la paginación de servidor. Cada página solo declara sus
 * columnas y sus filtros.
 */
export function ListTable<T>({
  query,
  columns,
  rowKey,
  caption,
  unit,
  emptyTitle,
  emptyText,
  onPageChange,
  emptyAction,
}: ListTableProps<T>) {
  if (query.isPending) return <LoadingState />;
  if (query.isError) {
    return <ErrorState error={query.error} onRetry={() => void query.refetch()} />;
  }
  const data = query.data;
  if (!data) return <LoadingState />;
  if (data.items.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        text={emptyText}
        action={
          emptyAction ?? (
            <Button variant="secundario" icon="rayo" onClick={() => void query.refetch()}>
              Volver a consultar
            </Button>
          )
        }
      />
    );
  }

  return (
    <>
      <DataTable columns={columns} rows={data.items} rowKey={rowKey} caption={caption} />
      <Pagination
        page={data.page}
        pageSize={data.pageSize}
        total={data.total}
        onPageChange={onPageChange}
        unit={unit}
      />
    </>
  );
}
