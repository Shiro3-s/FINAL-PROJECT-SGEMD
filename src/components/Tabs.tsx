export interface TabItem {
  id: string;
  label: string;
}

interface TabsProps {
  items: TabItem[];
  active: string;
  onChange: (id: string) => void;
  /** Etiqueta accesible del conjunto de pestañas. */
  label: string;
}

/**
 * Pestañas controladas (`.tabs` del prototipo). El panel lo dibuja la página
 * según `active`, porque cada vista decide si filtra en servidor o no.
 */
export function Tabs({ items, active, onChange, label }: TabsProps) {
  return (
    <div className="tabs" role="tablist" aria-label={label}>
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          role="tab"
          id={`tab-${item.id}`}
          aria-selected={item.id === active}
          aria-controls={`panel-${item.id}`}
          className={item.id === active ? 'activo' : undefined}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

export function TabPanel({
  id,
  active,
  children,
}: {
  id: string;
  active: string;
  children: React.ReactNode;
}) {
  if (id !== active) return null;
  return (
    <div role="tabpanel" id={`panel-${id}`} aria-labelledby={`tab-${id}`}>
      {children}
    </div>
  );
}
