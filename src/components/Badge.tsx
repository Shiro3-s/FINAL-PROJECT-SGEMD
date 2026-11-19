import { Icon, type IconName } from './Icon.tsx';
import { badgeFor, type BadgeSpec, type BadgeTone } from './badges/stateMap.ts';

interface BadgeProps {
  children: string;
  /** Tono explícito; si se omite se resuelve por `stateMap`. */
  tone?: BadgeTone;
  icon?: IconName;
  /** Permite forzar un estado distinto del texto (p. ej. «Aprobada» de solicitud). */
  state?: string;
  className?: string;
}

/**
 * Insignia con icono y texto (§10.5). Nunca comunica el estado solo con color.
 * El tono se resuelve en `stateMap.ts` para que no exista una segunda copia del
 * mapeo en las páginas.
 */
export function Badge({ children, tone, icon, state, className }: BadgeProps) {
  const spec: BadgeSpec = state
    ? badgeFor(state)
    : tone
      ? { tone, icon: icon ?? 'doc' }
      : badgeFor(children);

  return (
    <span className={`badge b-${spec.tone}${className ? ` ${className}` : ''}`}>
      <Icon name={icon ?? spec.icon} size={12} />
      {children}
    </span>
  );
}
