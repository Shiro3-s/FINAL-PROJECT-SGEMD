import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider.tsx';
import { Icon } from '../components/Icon.tsx';
import { homeForUser } from '../navigation/nav.ts';

/** Ruta inexistente. No revela nada más que el hecho de que no hay vista. */
export function NotFoundPage() {
  const { user } = useAuth();

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <Icon name="search" size={40} />
        <h1>No encontramos esta página</h1>
        <p className="acceso-nota">
          La dirección no corresponde a ninguna vista del sistema. Revisa el enlace o vuelve
          a tu inicio.
        </p>
        <Link className="btn btn-primario" to={user ? homeForUser(user) : '/login'}>
          {user ? 'Volver a mi inicio' : 'Ir al inicio de sesión'}
        </Link>
      </div>
    </div>
  );
}
