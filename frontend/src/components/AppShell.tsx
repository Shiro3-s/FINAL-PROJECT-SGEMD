import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { initialsOf, fullNameOf } from '../api/types.ts';
import { useAuth } from '../auth/AuthProvider.tsx';
import { Icon } from './Icon.tsx';
import { NotificationDrawer } from './NotificationDrawer.tsx';
import { useLogout } from '../queries/session.ts';
import { useNotificationStream, useUnreadCount } from '../queries/notifications.ts';
import {
  NAV,
  PROFILE_BY_ROLE,
  ROLE_LABEL,
  SETTINGS_BY_ROLE,
  isGroup,
} from '../navigation/nav.ts';

/** Ruta del buscador global por rol: no hay endpoint de búsqueda global. */
const SEARCH_TARGET = {
  estudiante: '/estudiante/emprendimientos',
  docente: '/docente/emprendimientos',
  administrador: '/admin/usuarios',
} as const;

function isActive(to: string, matchPrefix: boolean | undefined, pathname: string): boolean {
  if (matchPrefix) return pathname === to || pathname.startsWith(`${to}/`);
  return pathname === to;
}

/**
 * Marco de la aplicación autenticada: menú lateral por rol, barra superior con
 * notificaciones y cuenta, y el contenido de la ruta.
 *
 * El menú se genera desde `navigation/nav.ts`; cada entrada es una ruta real, así
 * que no puede quedar un enlace muerto. En móvil el menú entra como drawer y el
 * botón hamburguesa lo abre.
 */
export function AppShell() {
  const { user, role } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useLogout();
  const unread = useUnreadCount();
  useNotificationStream(Boolean(user));

  const [menuOpen, setMenuOpen] = useState(false);
  const [whoOpen, setWhoOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [query, setQuery] = useState('');
  const sidebarRef = useRef<HTMLElement>(null);
  const whoRef = useRef<HTMLDivElement>(null);

  // El menú móvil y el de la cuenta se cierran al cambiar de ruta.
  useEffect(() => {
    setMenuOpen(false);
    setWhoOpen(false);
    setNotifOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!whoOpen) return;
    const onClick = (event: MouseEvent): void => {
      if (!whoRef.current?.contains(event.target as Node)) setWhoOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [whoOpen]);

  if (!user || !role) return null;

  const entries = NAV[role];
  const profile = PROFILE_BY_ROLE[role];
  const settings = SETTINGS_BY_ROLE[role];
  const label = ROLE_LABEL[role];

  const onLogout = async (): Promise<void> => {
    await logout.mutateAsync();
    navigate('/login', { replace: true });
  };

  const onSearch = (): void => {
    const term = query.trim();
    if (!term) return;
    navigate(`${SEARCH_TARGET[role]}?q=${encodeURIComponent(term)}`);
    setQuery('');
  };

  return (
    <div className="shell">
      <aside className={menuOpen ? 'sidebar abierto' : 'sidebar'} id="sb" ref={sidebarRef}>
        <div className="brand">
          <span className="brand-tile">
            <img
              src="/brand/logo-blanco.png"
              width={600}
              height={286}
              alt="SGEMD, Emprendimiento Minuto de Dios"
            />
          </span>
          <div className="brand-text">
            <div className="brand-name">SGEMD</div>
            <div className="brand-sub">Emprendimiento Minuto de Dios</div>
          </div>
        </div>

        <nav className="nav" aria-label="Menú principal">
          {entries.map((entry) => {
            if (!isGroup(entry)) {
              return (
                <NavLink
                  key={entry.to}
                  to={entry.to}
                  end={entry.end}
                  className={({ isActive: routerActive }) =>
                    routerActive || isActive(entry.to, entry.matchPrefix, location.pathname)
                      ? 'activo'
                      : undefined
                  }
                >
                  <Icon name={entry.icon} size={16} />
                  <span>{entry.label}</span>
                </NavLink>
              );
            }
            const open = entry.items.some((item) =>
              isActive(item.to, item.matchPrefix ?? true, location.pathname),
            );
            return (
              <details className="nav-group" key={entry.label} open={open}>
                <summary className="nav-label">
                  <span>{entry.label}</span>
                  <Icon name="abajo" size={12} />
                </summary>
                <div className="nav-hijos">
                  {entry.items.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive: routerActive }) =>
                        routerActive ||
                        isActive(item.to, item.matchPrefix, location.pathname)
                          ? 'activo'
                          : undefined
                      }
                    >
                      <Icon name={item.icon} size={16} />
                      <span>{item.label}</span>
                    </NavLink>
                  ))}
                </div>
              </details>
            );
          })}
        </nav>

        <div className="side-foot">
          <div className="side-card">
            <b>Institución Minuto de Dios</b>
            <span>Módulo {label}</span>
          </div>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button
            className="burger"
            type="button"
            aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((current) => !current)}
          >
            <Icon name="menu" size={20} />
          </button>
          <div className="topbar-mark" aria-hidden="true" />
          <form
            className="search"
            role="search"
            onSubmit={(event) => {
              event.preventDefault();
              onSearch();
            }}
          >
            <Icon name="search" size={16} />
            <input
              type="search"
              placeholder="Buscar en el sistema"
              aria-label="Buscar en el sistema"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </form>
          <div className="topbar-right">
            <button
              type="button"
              className="icon-btn"
              aria-label="Notificaciones"
              aria-haspopup="dialog"
              onClick={() => setNotifOpen(true)}
            >
              <Icon name="bell" size={18} />
              {unread.data ? <span className="count">{unread.data}</span> : null}
            </button>
            <div className="who" ref={whoRef}>
              <button
                type="button"
                className="who-btn"
                aria-haspopup="menu"
                aria-expanded={whoOpen}
                onClick={() => setWhoOpen((current) => !current)}
              >
                <span className="avatar" aria-hidden="true">
                  {initialsOf(user)}
                </span>
                <span className="who-text">
                  <span className="who-name">{fullNameOf(user)}</span>
                  <span className="who-role">{label}</span>
                </span>
              </button>
              {whoOpen ? (
                <div className="who-menu visible" role="menu">
                  <Link role="menuitem" to={profile}>
                    <Icon name="user" size={15} /> Mi perfil
                  </Link>
                  {settings ? (
                    <Link role="menuitem" to={settings}>
                      <Icon name="engranaje" size={15} /> Configuración
                    </Link>
                  ) : null}
                  <button
                    role="menuitem"
                    type="button"
                    disabled={logout.isPending}
                    onClick={onLogout}
                  >
                    <Icon name="salir" size={15} /> Cerrar sesión
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>

      <button
        type="button"
        className={menuOpen ? 'overlay visible' : 'overlay'}
        aria-hidden={!menuOpen}
        tabIndex={-1}
        aria-label="Cerrar menú"
        onClick={() => setMenuOpen(false)}
      />

      <NotificationDrawer open={notifOpen} onClose={() => setNotifOpen(false)} role={role} />
    </div>
  );
}
