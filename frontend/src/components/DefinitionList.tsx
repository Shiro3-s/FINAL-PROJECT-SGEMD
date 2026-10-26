import type { ReactNode } from 'react';
import { Icon, type IconName } from './Icon.tsx';

export interface DefinitionItem {
  term: string;
  value: ReactNode;
}

/** Lista de definición de dos columnas (`.lista-def` / `.def-row`). */
export function DefinitionList({ items }: { items: DefinitionItem[] }) {
  return (
    <dl className="lista-def">
      {items.map((item) => (
        <div className="def-row" key={item.term}>
          <dt>{item.term}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

interface CalloutProps {
  children: ReactNode;
  icon?: IconName;
}

/** Aviso en línea (`.callout`): contexto, límites o advertencias. */
export function Callout({ children, icon = 'alerta' }: CalloutProps) {
  return (
    <div className="callout">
      <Icon name={icon} size={18} />
      <div>{children}</div>
    </div>
  );
}

export interface StepItem {
  label: string;
}

/**
 * Pasos de un flujo lineal (registro, recuperación de contraseña).
 * `current` es 1-based; los anteriores quedan como hechos.
 */
export function Steps({ items, current }: { items: StepItem[]; current: number }) {
  return (
    <ol className="steps" aria-label="Pasos del proceso">
      {items.map((item, index) => {
        const number = index + 1;
        const state = number === current ? 'activo' : number < current ? 'hecho' : '';
        return (
          <li key={item.label} className={`step ${state}`.trim()} aria-current={number === current ? 'step' : undefined}>
            <i aria-hidden="true">{number < current ? <Icon name="check" size={14} /> : number}</i>
            <b>{item.label}</b>
            {index < items.length - 1 ? <span className="step-line" aria-hidden="true" /> : null}
          </li>
        );
      })}
    </ol>
  );
}
