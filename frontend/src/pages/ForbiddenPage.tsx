import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider.tsx';
import { Icon } from '../components/Icon.tsx';
import { homeForUser } from '../navigation/nav.ts';

/** Acceso denegado: el rol no tiene pantalla para esa ruta. */
export function ForbiddenPage() {
  const { user } = useAuth();

  return (
    <div className="auth-shell">
      <div className="auth-card" role="alert">
        <Icon name="lock" size={40} />
        <h1>No tienes acceso a esta vista</h1>
        <p className="acceso-nota">
          Tu rol no incluye esta pantalla. Si crees que es un error, comunícate con la
          coordinación del programa.
        </p>
        <Link className="btn btn-primario" to={homeForUser(user)}>
          Volver a mi inicio
        </Link>
      </div>
    </div>
  );
}
