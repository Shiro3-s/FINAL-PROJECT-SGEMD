import type { ReactNode } from 'react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import type { RoleKey } from '../api/types.ts';
import { Callout } from '../components/DefinitionList.tsx';
import { PageHeader } from '../components/PageHeader.tsx';
import { ErrorState, LoadingState } from '../components/States.tsx';
import { PROFILE_BY_ROLE } from '../navigation/nav.ts';
import { useAuth } from './AuthProvider.tsx';

/** Espera inicial de la sesión: logo y mensaje, sin barra de navegación. */
export function SessionLoading() {
  return (
    <div className="auth-shell">
      <div className="auth-card" role="status" aria-live="polite">
        <img
          className="auth-logo"
          src="/brand/logo-color.png"
          width={600}
          height={286}
          alt="SGEMD, Emprendimiento Minuto de Dios"
        />
        <LoadingState label="Comprobando tu sesión…" />
      </div>
    </div>
  );
}

/**
 * Exige sesión. Guarda la ruta de origen para volver después del login; si la
 * consulta falló por red (no por falta de sesión) muestra el error y no
 * redirige, para no perder el motivo.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, isLoading, error, refetch } = useAuth();
  const location = useLocation();

  if (isLoading) return <SessionLoading />;
  if (error) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <ErrorState error={error} onRetry={refetch} />
        </div>
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <>{children}</>;
}

/** Exige uno de los roles con pantalla. Auditor (P2) no tiene ninguna. */
export function RequireRole({
  roles,
  children,
}: {
  roles: RoleKey[];
  children: ReactNode;
}) {
  const { role } = useAuth();
  if (!role || !roles.includes(role)) {
    return <Navigate to="/403" replace />;
  }
  return <>{children}</>;
}

/**
 * Bloqueo de módulo para cuentas `Limitado` e `Inactivo` (AQ-07 opción A).
 *
 * No es un 403 de ruta: la cuenta sí tiene sesión y sí puede entrar a perfil,
 * acta y notificaciones. Se explica el estado y se ofrecen esos tres destinos.
 */
function AccountBlocked() {
  const { user, role } = useAuth();
  if (!user || !role) return null;

  const limited = user.estado === 'Limitado';

  return (
    <>
      <PageHeader
        title={limited ? 'Tu cuenta está limitada' : 'Tu cuenta está inactiva'}
        sub="Este módulo todavía no está disponible para tu cuenta."
      />
      <Callout icon="lock">
        {limited ? (
          <>
            <b>La coordinación del programa debe activar tu cuenta.</b> Mientras eso
            ocurre puedes completar tu perfil, descargar o cargar tu acta y revisar tus
            notificaciones.
          </>
        ) : (
          <>
            <b>Tu cuenta fue desactivada.</b> Si crees que es un error, comunícate con la
            coordinación del programa; mientras tanto solo puedes consultar tu perfil y
            tus notificaciones.
          </>
        )}
      </Callout>
      <div className="fila-acciones mt-14">
        <Link className="btn btn-primario" to={PROFILE_BY_ROLE[role]}>
          Ir a mi perfil
        </Link>
        <Link className="btn btn-secundario" to={`/${role}/notificaciones`}>
          Ver notificaciones
        </Link>
        {role === 'estudiante' ? (
          <Link className="btn btn-secundario" to="/estudiante/acta">
            Ver mi acta
          </Link>
        ) : null}
      </div>
    </>
  );
}

/** Exige cuenta `Activo` para los módulos de trabajo. */
export function RequireActive({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  if (user && user.estado !== 'Activo') return <AccountBlocked />;
  return <>{children}</>;
}
