import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Icon, type IconName } from './Icon.tsx';
import { ProgressBar } from './ProgressBar.tsx';

interface MetricProps {
  icon: IconName;
  label: string;
  value: ReactNode;
  /** Sufijo pequeño junto al número: «%», «/12»… */
  unit?: string;
  /** Porcentaje de la barra inferior; se omite si no aplica. */
  progress?: number;
  delta?: string;
  /** Envuelve la tarjeta en un enlace cuando la métrica lleva a otra vista. */
  to?: string;
}

/**
 * Tarjeta de métrica del tablero (`.metrica`). El prototipo la duplica como
 * enlace con vista previa; aquí basta con que toda la tarjeta sea navegable.
 */
export function Metric({ icon, label, value, unit, progress, delta, to }: MetricProps) {
  const body = (
    <>
      <div className="metrica-top">
        <span className="metrica-ico">
          <Icon name={icon} size={18} />
        </span>
        <div>
          <div className="metrica-lbl">{label}</div>
          <div className="metrica-val">
            {value}
            {unit ? <span className="u">{unit}</span> : null}
          </div>
        </div>
        {delta ? (
          <span className="metrica-delta">
            <Icon name="trend" size={13} /> {delta}
          </span>
        ) : null}
      </div>
      {progress === undefined ? null : <ProgressBar value={progress} label={label} />}
    </>
  );

  return (
    <div className="card metrica">
      {to ? (
        <Link to={to} className="metrica-enlace">
          {body}
        </Link>
      ) : (
        body
      )}
    </div>
  );
}
