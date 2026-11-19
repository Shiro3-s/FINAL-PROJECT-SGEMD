import type { ReactNode } from 'react';
import { Icon } from './Icon.tsx';

/** Contenedor de filtros y búsqueda de una lista. */
export function Toolbar({ children }: { children: ReactNode }) {
  return <div className="toolbar">{children}</div>;
}

interface SearchBoxProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
}

/**
 * Buscador de lista. El estado vive en la página para que la consulta a la API
 * se dispare con `useQuery`; el componente solo dibuja el campo.
 */
export function SearchBox({
  value,
  onChange,
  placeholder = 'Buscar',
  label = 'Buscar',
}: SearchBoxProps) {
  return (
    <div className="buscador crece">
      <Icon name="search" size={16} />
      <input
        type="search"
        value={value}
        placeholder={placeholder}
        aria-label={label}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

interface SelectFilterProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  children: ReactNode;
  /** Opción «Todos» con valor vacío. */
  allLabel?: string;
}

/** Filtro de una lista por catálogo o enumeración. */
export function SelectFilter({
  value,
  onChange,
  label,
  children,
  allLabel = 'Todos',
}: SelectFilterProps) {
  return (
    <select
      className="filtro"
      aria-label={label}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    >
      <option value="">{allLabel}</option>
      {children}
    </select>
  );
}
