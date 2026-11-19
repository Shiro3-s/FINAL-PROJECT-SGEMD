import type { IconName } from '../components/Icon.tsx';
import { roleKeyOf, type RoleKey, type SessionUser } from '../api/types.ts';

/**
 * Menú lateral por rol.
 *
 * Estructura copiada de `prototype/lib_ui.py` (NAV): ítems planos y grupos
 * acordeón. Los destinos son rutas de React, no archivos `.html`.
 *
 * Los segmentos van en español porque la API ya emite esas rutas en
 * `Notificaciones.Url` (`/estudiante/asesorias/3`, `/admin/actas`, …). Cambiarlas
 * a inglés rompería 29 enlaces profundos ya guardados en la base; la desviación
 * de §17.1.8 queda registrada en `docs/decisions.md`.
 *
 * Diferencias deliberadas con el prototipo, todas anotadas en
 * `docs/design-parity.md`:
 * - «Actas de estudiantes» es nueva: `GET /acta` es una cola de revisión para el
 *   admin y no tenía entrada de menú.
 * - «Configuración» aparece en el grupo Institucional del admin: el prototipo
 *   ofrecía «Preferencias» sin vista, pero el módulo de configuración existe.
 * - «Asesorías» del estudiante conserva la lista; el detalle
 *   `/estudiante/asesorias/:id` existe porque las notificaciones apuntan ahí.
 */
export interface NavLeaf {
  label: string;
  icon: IconName;
  to: string;
  /** Marca el ítem como activo también en sus rutas hijas. */
  matchPrefix?: boolean;
  /** `true` en las rutas índice para no quedar activo en toda la sección. */
  end?: boolean;
}

export interface NavGroup {
  label: string;
  items: NavLeaf[];
}

export type NavEntry = NavLeaf | NavGroup;

export const isGroup = (entry: NavEntry): entry is NavGroup => 'items' in entry;

export const NAV: Record<RoleKey, NavEntry[]> = {
  estudiante: [
    { label: 'Inicio', icon: 'home', to: '/estudiante', end: true },
    {
      label: 'Mi emprendimiento',
      items: [
        {
          label: 'Mi emprendimiento',
          icon: 'maleta',
          to: '/estudiante/emprendimientos',
          matchPrefix: true,
        },
        {
          label: 'Diagnóstico',
          icon: 'clipboard',
          to: '/estudiante/diagnostico',
          matchPrefix: true,
        },
      ],
    },
    {
      label: 'Planificación y seguimiento',
      items: [
        { label: 'Estado de seguimiento', icon: 'trend', to: '/estudiante/estado' },
        { label: 'Plan de trabajo', icon: 'layers', to: '/estudiante/plan' },
        { label: 'Tareas', icon: 'checklist', to: '/estudiante/tareas', matchPrefix: true },
        {
          label: 'Seguimiento',
          icon: 'doc',
          to: '/estudiante/seguimiento',
          matchPrefix: true,
        },
      ],
    },
    {
      label: 'Acompañamiento y actividades',
      items: [
        { label: 'Asesorías', icon: 'chat', to: '/estudiante/asesorias', matchPrefix: true },
        { label: 'Eventos', icon: 'calendar', to: '/estudiante/eventos', matchPrefix: true },
      ],
    },
  ],
  docente: [
    { label: 'Inicio', icon: 'pie', to: '/docente', end: true },
    {
      label: 'Mis emprendimientos',
      items: [
        {
          label: 'Emprendimientos asignados',
          icon: 'maleta',
          to: '/docente/emprendimientos',
          matchPrefix: true,
        },
        {
          label: 'Diagnóstico',
          icon: 'clipboard',
          to: '/docente/diagnosticos',
          matchPrefix: true,
        },
        { label: 'Tareas', icon: 'checklist', to: '/docente/tareas', matchPrefix: true },
      ],
    },
    {
      label: 'Acompañamiento y actividades',
      items: [
        { label: 'Asesorías', icon: 'chat', to: '/docente/asesorias', matchPrefix: true },
        { label: 'Eventos', icon: 'calendar', to: '/docente/eventos', matchPrefix: true },
      ],
    },
  ],
  administrador: [
    { label: 'Inicio', icon: 'grid', to: '/admin', end: true },
    { label: 'Solicitudes', icon: 'checklist', to: '/admin/solicitudes' },
    {
      label: 'Usuarios y asignaciones',
      items: [
        { label: 'Gestión de perfiles', icon: 'users', to: '/admin/usuarios' },
        { label: 'Asignaciones', icon: 'sliders', to: '/admin/asignaciones' },
        { label: 'Actas de estudiantes', icon: 'doc', to: '/admin/actas' },
      ],
    },
    {
      label: 'Emprendimientos y seguimiento',
      items: [
        {
          label: 'Emprendimientos',
          icon: 'maleta',
          to: '/admin/emprendimientos',
          matchPrefix: true,
        },
        {
          label: 'Diagnósticos',
          icon: 'clipboard',
          to: '/admin/diagnosticos',
          matchPrefix: true,
        },
        { label: 'Seguimiento', icon: 'trend', to: '/admin/seguimiento', matchPrefix: true },
        { label: 'Tareas', icon: 'checklist', to: '/admin/tareas', matchPrefix: true },
      ],
    },
    {
      label: 'Acompañamiento y actividades',
      items: [
        { label: 'Asesorías', icon: 'chat', to: '/admin/asesorias', matchPrefix: true },
        { label: 'Eventos', icon: 'calendar', to: '/admin/eventos', matchPrefix: true },
      ],
    },
    {
      label: 'Institucional',
      items: [
        { label: 'Reportes', icon: 'download', to: '/admin/reportes' },
        { label: 'Respaldos', icon: 'bd', to: '/admin/respaldos' },
        { label: 'Configuración', icon: 'engranaje', to: '/admin/configuracion' },
      ],
    },
    { label: 'Notificaciones', icon: 'bell', to: '/admin/notificaciones' },
    { label: 'Perfil', icon: 'user', to: '/admin/perfil' },
  ],
};

/** Ruta de inicio de cada rol: destino de `/` y del login. */
export const HOME_BY_ROLE: Record<RoleKey, string> = {
  estudiante: '/estudiante',
  docente: '/docente',
  administrador: '/admin',
};

/** Ruta del menú de la cuenta (avatar), igual que el prototipo. */
export const PROFILE_BY_ROLE: Record<RoleKey, string> = {
  estudiante: '/estudiante/perfil',
  docente: '/docente/perfil',
  administrador: '/admin/perfil',
};

export const SETTINGS_BY_ROLE: Record<RoleKey, string | null> = {
  estudiante: '/estudiante/configuracion',
  docente: '/docente/configuracion',
  administrador: '/admin/configuracion',
};

/**
 * Destino tras iniciar sesión.
 *
 * Una cuenta `Limitado` o `Inactivo` no puede operar los módulos de trabajo
 * (AQ-07 opción A), así que su inicio es el perfil y no el tablero: llevarla al
 * tablero solo mostraría un bloqueo.
 */
export function homeForUser(user: SessionUser | null | undefined): string {
  const role = roleKeyOf(user);
  if (!role || !user) return '/login';
  if (user.estado !== 'Activo') return PROFILE_BY_ROLE[role];
  return HOME_BY_ROLE[role];
}

/** Etiqueta del rol tal como la muestra la interfaz (prototype/lib_ui.py ROLES). */
export const ROLE_LABEL: Record<RoleKey, string> = {
  estudiante: 'ESTUDIANTE',
  docente: 'DOCENTE',
  administrador: 'ADMINISTRADOR',
};
