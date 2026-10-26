import type { ReactNode } from 'react';
import { ErrorState, LoadingState } from './States.tsx';

interface QueryLike<T> {
  isPending: boolean;
  isError: boolean;
  error: unknown;
  data: T | undefined;
  refetch: () => unknown;
}

/**
 * Resuelve carga y error de una consulta de detalle y entrega los datos ya
 * listos. Evita repetir el mismo bloque en las 30 vistas de detalle.
 */
export function QueryGate<T>({
  query,
  children,
  loadingLabel,
  errorTitle,
}: {
  query: QueryLike<T>;
  children: (data: T) => ReactNode;
  loadingLabel?: string;
  errorTitle?: string;
}) {
  if (query.isPending) return <LoadingState label={loadingLabel} />;
  if (query.isError) {
    return (
      <ErrorState
        error={query.error}
        title={errorTitle}
        onRetry={() => void query.refetch()}
      />
    );
  }
  if (!query.data) return <LoadingState label={loadingLabel} />;
  return <>{children(query.data)}</>;
}
