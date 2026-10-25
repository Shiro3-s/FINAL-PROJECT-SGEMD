import type { CuentaEstado } from '@sgemd/shared';
import { AppError } from '../utils/AppError.js';

/**
 * Transiciones válidas del ciclo de vida de una cuenta (BR-003, R34).
 *
 * ```
 * Limitado ──► Activo ──► Inactivo
 *                 ▲           │
 *                 └───────────┘
 * ```
 *
 * - `Limitado → Activo`: validación/activación por la coordinación (UC-1).
 * - `Inactivo → Activo`: reactivación manual (BR-005).
 * - `Activo → Inactivo`: desactivación por el administrador.
 *
 * Todo lo demás se rechaza, incluida la vuelta `Activo → Limitado` que el prototipo deja
 * elegir en el selector de estado: no existe en el ciclo de vida del master (FR-013) ni
 * en BR-003, y degradar una cuenta ya activa no está previsto. Queda registrado como
 * discrepancia.
 *
 * El estado se aísla aquí para que un cambio de regla no toque los servicios.
 */
export const ACCOUNT_TRANSITIONS: Readonly<Record<CuentaEstado, readonly CuentaEstado[]>> = {
  Limitado: ['Activo'],
  Activo: ['Inactivo'],
  Inactivo: ['Activo'],
};

export function canTransition(from: CuentaEstado, to: CuentaEstado): boolean {
  return ACCOUNT_TRANSITIONS[from].includes(to);
}

export function assertTransition(from: CuentaEstado, to: CuentaEstado): void {
  if (canTransition(from, to)) return;

  throw new AppError(
    422,
    'INVALID_STATE_TRANSITION',
    from === to
      ? `La cuenta ya está en estado ${to}.`
      : `No se puede pasar de ${from} a ${to}.`,
  );
}
