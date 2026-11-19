import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Icon, type IconName } from './Icon.tsx';

type Variant = 'primario' | 'secundario' | 'acento' | 'peligro';
type Size = 'md' | 'sm';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  icon?: IconName;
  iconRight?: IconName;
  /** Muestra el estado ocupado y bloquea el doble envío. */
  loading?: boolean;
  children?: ReactNode;
}

/**
 * Botón del sistema. Altura 40 (32 en `sm`), radios y variantes de §10.5.
 *
 * `type="button"` por defecto: dentro de un `<form>` un botón sin tipo envía el
 * formulario, y eso ya provocó envíos accidentales en el prototipo. Los envíos
 * declaran `type="submit"` a propósito.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'secundario',
    size = 'md',
    icon,
    iconRight,
    loading = false,
    disabled,
    type = 'button',
    className,
    children,
    ...rest
  },
  ref,
) {
  const classes = [
    'btn',
    `btn-${variant}`,
    size === 'sm' ? 'btn-sm' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      {...rest}
      ref={ref}
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
    >
      {loading ? <Icon name="reloj" size={size === 'sm' ? 14 : 16} /> : null}
      {!loading && icon ? <Icon name={icon} size={size === 'sm' ? 14 : 16} /> : null}
      {children}
      {iconRight ? <Icon name={iconRight} size={size === 'sm' ? 14 : 16} /> : null}
    </button>
  );
});
