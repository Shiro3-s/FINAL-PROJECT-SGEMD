import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

export interface Crumb {
  label: string;
  /** Sin `to` el nivel es solo contexto, igual que en el prototipo. */
  to?: string;
}

interface PageHeaderProps {
  title: string;
  sub?: ReactNode;
  crumbs?: Crumb[];
  actions?: ReactNode;
}

/**
 * Cabecera de vista: migas, título, subtítulo y acciones.
 *
 * Las migas intermedias solo son enlaces cuando existe una vista real
 * (hallazgo BT1 del prototipo): nunca se pinta un `href="#"`.
 */
export function PageHeader({ title, sub, crumbs, actions }: PageHeaderProps) {
  return (
    <>
      {crumbs && crumbs.length > 0 ? (
        <nav className="crumbs" aria-label="Ruta de navegación">
          {crumbs.map((crumb, index) => (
            <span key={`${crumb.label}-${index}`}>
              {index > 0 ? ' › ' : null}
              {index === crumbs.length - 1 ? (
                <b>{crumb.label}</b>
              ) : crumb.to ? (
                <Link to={crumb.to}>{crumb.label}</Link>
              ) : (
                <span className="miga-item">{crumb.label}</span>
              )}
            </span>
          ))}
        </nav>
      ) : null}
      <div className="page-head">
        <div>
          <h1>{title}</h1>
          {sub ? <p className="sub">{sub}</p> : null}
        </div>
        {actions ? <div className="acciones">{actions}</div> : null}
      </div>
    </>
  );
}
