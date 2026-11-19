import type { ReactNode } from 'react';
import { ApiError } from '../api/client.ts';
import { Button } from './Button.tsx';
import { Icon, type IconName } from './Icon.tsx';

/** Mensaje legible de cualquier error de la API. */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Ocurrió un error inesperado.';
}

/**
 * Carga. El prototipo es estático y no tenía estado de carga; el marcado sigue
 * el mismo tono sobrio del resto (icono + texto) y `role="status"` lo anuncia.
 */
export function LoadingState({ label = 'Cargando información…' }: { label?: string }) {
  return (
    <div className="estado-carga" role="status">
      <Icon name="reloj" size={18} />
      <span>{label}</span>
    </div>
  );
}

interface ErrorStateProps {
  error: unknown;
  onRetry?: () => void;
  title?: string;
}

/** Error de lectura, con reintento explícito (no hay sondeo automático). */
export function ErrorState({
  error,
  onRetry,
  title = 'No fue posible cargar la información',
}: ErrorStateProps) {
  return (
    <div className="vacio" role="alert">
      <Icon name="alerta" size={40} />
      <h3>{title}</h3>
      <p>{errorMessage(error)}</p>
      {onRetry ? (
        <Button variant="secundario" icon="rayo" onClick={onRetry}>
          Reintentar
        </Button>
      ) : null}
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  text: string;
  icon?: IconName;
  action?: ReactNode;
}

/** Lista vacía: explica por qué no hay filas y qué puede hacer el usuario. */
export function EmptyState({ title, text, icon = 'doc', action }: EmptyStateProps) {
  return (
    <div className="vacio">
      <Icon name={icon} size={40} />
      <h3>{title}</h3>
      <p>{text}</p>
      {action}
    </div>
  );
}
