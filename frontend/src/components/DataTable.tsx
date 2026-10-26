import type { ReactNode } from 'react';

export interface Column<T> {
  /** Identificador estable de la columna. */
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  /** Clases de la celda; `acc` agrupa los botones de acción. */
  className?: string;
  headerClassName?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
  caption: string;
  /** Selección por fila; si se omite no se pinta la columna de checkbox. */
  selection?: {
    selected: ReadonlySet<string | number>;
    onToggle: (id: string | number) => void;
    onToggleAll: () => void;
    label: string;
  };
  rowClassName?: (row: T) => string | undefined;
}

/**
 * Tabla de datos del sistema.
 *
 * Cada celda lleva `data-label` para que, por debajo de 768 px, el CSS la
 * convierta en tarjeta apilada (regla .tabla de components.css). Sin eso la
 * tabla de nueve columnas no cabe ni desplazándose.
 */
export function DataTable<T>({
  columns,
  rows,
  rowKey,
  caption,
  selection,
  rowClassName,
}: DataTableProps<T>) {
  const allSelected =
    selection !== undefined &&
    rows.length > 0 &&
    rows.every((row) => selection.selected.has(rowKey(row)));

  return (
    <div className="tabla-envoltura">
      <div className="tabla-scroll">
        <table className="tabla">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              {selection ? (
                <th className="sel" scope="col">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    aria-label={selection.label}
                    onChange={selection.onToggleAll}
                  />
                </th>
              ) : null}
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={column.headerClassName}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const id = rowKey(row);
              return (
                <tr key={id} className={rowClassName?.(row)}>
                  {selection ? (
                    <td className="sel" data-label="Seleccionar">
                      <input
                        type="checkbox"
                        checked={selection.selected.has(id)}
                        aria-label={`Seleccionar fila ${id}`}
                        onChange={() => selection.onToggle(id)}
                      />
                    </td>
                  ) : null}
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      data-label={column.header}
                      className={column.className}
                    >
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
