import { useEffect, useId, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from './Icon.tsx';

interface DrawerProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
  /** Pie fijo con la acción principal (p. ej. «Ver todas»). */
  footer?: ReactNode;
}

/**
 * Panel lateral derecho, igual que el drawer de notificaciones del prototipo
 * (`.sg-drawer`). Cierra con Escape y con clic en el velo.
 */
export function Drawer({ open, title, onClose, children, footer }: DrawerProps) {
  const titleId = useId();

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <>
      <div className="drawer-fondo" onClick={onClose} aria-hidden="true" />
      <aside className="sg-drawer" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <div className="sg-drawer-head">
          <h2 id={titleId}>{title}</h2>
          <button type="button" className="icon-btn" aria-label="Cerrar" onClick={onClose}>
            <Icon name="x" size={18} />
          </button>
        </div>
        {children}
        {footer ? <div className="sg-drawer-pie">{footer}</div> : null}
      </aside>
    </>,
    document.body,
  );
}
