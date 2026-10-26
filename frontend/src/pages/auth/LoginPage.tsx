import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/client.ts';
import { SessionLoading } from '../../auth/guards.tsx';
import { AuthLayout } from '../../components/AuthLayout.tsx';
import { Button } from '../../components/Button.tsx';
import { errorMessage } from '../../components/States.tsx';
import { TextField } from '../../components/FormField.tsx';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { useLogin } from '../../queries/session.ts';

interface LoginState {
  from?: string;
  notice?: string;
  correo?: string;
}

/**
 * Inicio de sesión.
 *
 * Tres desenlaces distintos, no uno:
 * - credenciales válidas → al inicio del rol (o a la ruta de origen);
 * - `EMAIL_NOT_VERIFIED` → al paso de verificación con el correo ya escrito;
 * - credenciales inválidas → aviso en la propia tarjeta.
 */
export function LoginPage() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state ?? null) as LoginState | null;
  const login = useLogin();

  const [correo, setCorreo] = useState(state?.correo ?? '');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (isLoading) return <SessionLoading />;
  if (user) return <Navigate to="/" replace />;

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await login.mutateAsync({ correoInstitucional: correo.trim(), password });
      navigate(state?.from && state.from !== '/login' ? state.from : '/', {
        replace: true,
      });
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'EMAIL_NOT_VERIFIED') {
        navigate('/verificar', {
          replace: true,
          state: {
            correo: correo.trim(),
            notice: 'Tu contraseña es correcta, pero falta verificar el correo.',
          },
        });
        return;
      }
      if (caught instanceof ApiError && caught.code === 'INVALID_CREDENTIALS') {
        setError('El correo o la contraseña no coinciden.');
        return;
      }
      if (caught instanceof ApiError && caught.code === 'RATE_LIMITED') {
        setError('Demasiados intentos seguidos. Espera un momento y vuelve a intentar.');
        return;
      }
      setError(errorMessage(caught));
    }
  };

  return (
    <AuthLayout>
      <h1>Iniciar sesión</h1>
      <p className="acceso-nota">
        Ingresa con tu correo institucional y tu contraseña. Tu rol se determina
        automáticamente y abre el panel que le corresponde.
      </p>

      {state?.notice ? (
        <div className="acceso-ok" role="status">
          {state.notice}
        </div>
      ) : null}

      <form onSubmit={onSubmit} noValidate>
        <TextField
          label="Correo institucional"
          type="email"
          required
          autoComplete="username"
          placeholder="nombre@uniminuto.edu.co"
          value={correo}
          onChange={(event) => setCorreo(event.target.value)}
        />
        <TextField
          label="Contraseña"
          type="password"
          required
          autoComplete="current-password"
          placeholder="Tu contraseña"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <div className="fila-recordar">
          <span />
          <Link to="/recuperar">Olvidé mi contraseña</Link>
        </div>
        <Button
          type="submit"
          variant="primario"
          className="ancho"
          loading={login.isPending}
        >
          Ingresar al sistema
        </Button>
      </form>

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      <p className="acceso-nota">
        ¿No tienes cuenta?{' '}
        <Link to="/registro">
          <b>Regístrate aquí</b>
        </Link>
      </p>
      <p className="acceso-nota acceso-nota-centro">
        ¿Ya verificaste tu correo y sigues sin poder entrar?{' '}
        <Link to="/verificar">
          <b>Verifica tu cuenta</b>
        </Link>
      </p>
    </AuthLayout>
  );
}
