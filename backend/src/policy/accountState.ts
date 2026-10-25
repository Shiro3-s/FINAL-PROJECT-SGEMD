import type { CuentaEstado } from '@sgemd/shared';

/**
 * Política de estado de cuenta (master §15: aislada en un solo módulo para que AQ-07
 * se pueda resolver sin reescribir los servicios).
 *
 * **Decisión pendiente AQ-07.** Mientras no se confirme, se aplica la opción A del
 * dossier: una cuenta `Limitado` puede ver su perfil, su acta y sus notificaciones;
 * los módulos de trabajo (diagnóstico, emprendimiento, tareas, asesorías, seguimiento,
 * eventos, reportes) exigen `Activo`.
 *
 * `Inactivo` no puede operar ningún módulo; solo el administrador la reactiva (BR-005).
 */
export const OPERATIVE_STATES: readonly CuentaEstado[] = ['Activo'];

export function canOperate(estado: CuentaEstado): boolean {
  return OPERATIVE_STATES.includes(estado);
}

/** Motivo legible para la interfaz, sin exponer detalles internos. */
export function blockedReason(estado: CuentaEstado): string {
  return estado === 'Limitado'
    ? 'Tu cuenta está pendiente de activación por la coordinación del programa.'
    : 'Tu cuenta está inactiva. Contacta a la coordinación del programa.';
}
