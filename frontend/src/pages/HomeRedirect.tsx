import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider.tsx';
import { SessionLoading } from '../auth/guards.tsx';
import { homeForUser } from '../navigation/nav.ts';

/**
 * Raíz `/`. Lleva a cada rol a su inicio; una cuenta `Limitado` o `Inactivo`
 * va al perfil, que es lo único que puede usar (AQ-07 opción A).
 */
export function HomeRedirect() {
  const { user, isLoading, error, refetch } = useAuth();

  if (isLoading) return <SessionLoading />;
  if (error) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <h1>No fue posible comprobar tu sesión</h1>
          <p className="acceso-nota">
            Revisa la conexión con el servidor y vuelve a intentarlo.
          </p>
          <button type="button" className="btn btn-primario" onClick={refetch}>
            Reintentar
          </button>
        </div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={homeForUser(user)} replace />;
}
