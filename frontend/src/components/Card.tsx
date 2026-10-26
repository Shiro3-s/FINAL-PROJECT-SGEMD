import type { ReactNode } from 'react';

interface CardProps {
  title?: ReactNode;
  hint?: ReactNode;
  action?: ReactNode;
  /** Quita el padding del cuerpo (tablas y listas que van a sangre). */
  flush?: boolean;
  children: ReactNode;
  className?: string;
  id?: string;
}

/** Tarjeta blanca con borde y sombra suave (§10.5). */
export function Card({ title, hint, action, flush, children, className, id }: CardProps) {
  return (
    <section className={className ? `card ${className}` : 'card'} id={id}>
      {title || hint || action ? (
        <div className="card-head">
          {title ? <h3>{title}</h3> : null}
          {action}
          {hint ? <span className="hint">{hint}</span> : null}
        </div>
      ) : null}
      <div className={flush ? 'card-body sin-pad' : 'card-body'}>{children}</div>
    </section>
  );
}
