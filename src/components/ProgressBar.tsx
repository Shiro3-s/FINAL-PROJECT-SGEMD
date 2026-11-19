/** Barra de progreso 0–100. Se usa en tableros y en subidas de evidencias. */
export function ProgressBar({
  value,
  label,
  yellow = false,
}: {
  value: number;
  label: string;
  yellow?: boolean;
}) {
  const safe = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <div
      className={yellow ? 'barra amarilla' : 'barra'}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={safe}
      aria-label={label}
    >
      <span style={{ width: `${safe}%` }} />
    </div>
  );
}
