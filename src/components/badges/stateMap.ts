import type { IconName } from '../Icon.tsx';

/**
 * Mapa único `estado → (tono, icono)`.
 *
 * §17.1.7: se define UNA sola vez y ningún componente decide colores por su
 * cuenta. Los tonos son los cuatro del prototipo (`b-azul`, `b-amarillo`,
 * `b-neutra`, `b-linea`); no hay rojo, verde ni naranja, y el icono es lo que
 * distingue el estado además del texto (nunca color solo).
 *
 * Los valores salen de `prototype/paginas_*.py`; cuando el prototipo usaba dos
 * tonos para el mismo estado se conserva el más frecuente.
 */
export type BadgeTone = 'azul' | 'amarillo' | 'neutra' | 'linea';

export interface BadgeSpec {
  tone: BadgeTone;
  icon: IconName;
}

export const STATE_MAP: Record<string, BadgeSpec> = {
  // Cuenta
  Activo: { tone: 'azul', icon: 'check' },
  Limitado: { tone: 'amarillo', icon: 'lock' },
  Inactivo: { tone: 'neutra', icon: 'lock' },

  // Emprendimiento
  Aprobado: { tone: 'azul', icon: 'check' },
  Rechazado: { tone: 'neutra', icon: 'x' },

  // Tarea y revisión
  Pendiente: { tone: 'neutra', icon: 'reloj' },
  'En curso': { tone: 'amarillo', icon: 'engranaje' },
  'En revisión': { tone: 'amarillo', icon: 'reloj' },
  Completada: { tone: 'azul', icon: 'check' },
  Completado: { tone: 'azul', icon: 'check' },
  Vencida: { tone: 'neutra', icon: 'alerta' },
  Devuelta: { tone: 'neutra', icon: 'alerta' },
  Calificada: { tone: 'linea', icon: 'check' },

  // Prioridad
  Alta: { tone: 'amarillo', icon: 'alerta' },
  Media: { tone: 'linea', icon: 'reloj' },
  Baja: { tone: 'linea', icon: 'abajo' },

  // Asesoría
  'Por agendar': { tone: 'amarillo', icon: 'reloj' },
  Programada: { tone: 'amarillo', icon: 'reloj' },
  Confirmada: { tone: 'azul', icon: 'check' },
  Cancelada: { tone: 'neutra', icon: 'x' },

  // Acta
  Aprobada: { tone: 'azul', icon: 'check' },
  Rechazada: { tone: 'neutra', icon: 'x' },

  // Diagnóstico
  'En progreso': { tone: 'amarillo', icon: 'engranaje' },
  Enviado: { tone: 'neutra', icon: 'check' },
  Revisado: { tone: 'azul', icon: 'check' },

  // Evento
  Publicado: { tone: 'azul', icon: 'check' },

  // Solicitud
  Aprobada_Solicitud: { tone: 'azul', icon: 'check' },

  // Respaldo
  Exitosa: { tone: 'azul', icon: 'check' },
  Fallida: { tone: 'neutra', icon: 'alerta' },

  // Asignación
  activa: { tone: 'azul', icon: 'check' },
  inactiva: { tone: 'neutra', icon: 'x' },
};

const FALLBACK: BadgeSpec = { tone: 'neutra', icon: 'doc' };

export function badgeFor(value: string | null | undefined): BadgeSpec {
  if (!value) return FALLBACK;
  return STATE_MAP[value] ?? FALLBACK;
}
