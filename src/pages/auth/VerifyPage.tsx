import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ApiError, apiSend } from '../../api/client.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { AuthLayout } from '../../components/AuthLayout.tsx';
import { Button } from '../../components/Button.tsx';
import { TextField } from '../../components/FormField.tsx';
import { OtpInput } from '../../components/OtpInput.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useCountdown } from '../../hooks/useCountdown.ts';

interface VerifyState {
  correo?: string;
  notice?: string;
}

/**
 * Verificación del correo con código OTP de 8 dígitos.
 *
 * El código vence a los 5 minutos y admite 5 intentos; el reenvío tiene un
 * cooldown de 60 s. La cuenta atrás es una ayuda, no una regla: si el servidor
 * responde `OTP_COOLDOWN` se muestra su mensaje igualmente.
 */
export function VerifyPage() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state ?? null) as VerifyState | null;
  const countdown = useCountdown(state?.notice ? 60 : 0);

  const [correo, setCorreo] = useState(state?.correo ?? '');
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [resending, setResending] = useState(false);

  if (!isLoading && user) return <Navigate to="/" replace />;

  const onVerify = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setOk(null);
    if (codigo.length !== 8) {
      setError('Escribe los 8 dígitos del código que enviamos a tu correo.');
      return;
    }
    setSending(true);
    try {
      await apiSend<unknown>('POST', '/auth/verify', {
        correoInstitucional: correo.trim(),
        codigo,
      });
      navigate('/login', {
        replace: true,
        state: {
          correo: correo.trim(),
          notice:
            'Correo verificado. Tu cuenta queda pendiente de activación por la coordinación del programa.',
        },
      });
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'OTP_INVALID') {
        setError('El código no es válido o ya venció. Solicita uno nuevo.');
      } else if (caught instanceof ApiError && caught.code === 'OTP_ATTEMPTS_EXCEEDED') {
        setError('Se agotaron los 5 intentos. Solicita un código nuevo.');
      } else if (caught instanceof ApiError && caught.code === 'RATE_LIMITED') {
        setError('Demasiados intentos seguidos. Espera unos minutos y vuelve a intentar.');
      } else {
        setError(errorMessage(caught));
      }
    } finally {
      setSending(false);
    }
  };

  const onResend = async () => {
    setError(null);
    setOk(null);
    setResending(true);
    try {
      await apiSend<unknown>('POST', '/auth/resend-code', {
        correoInstitucional: correo.trim(),
      });
      countdown.start(60);
      setOk('Si la cuenta existe y sigue sin verificar, enviamos un código nuevo.');
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'OTP_COOLDOWN') {
        countdown.start(60);
        setError('Espera un minuto antes de pedir otro código.');
      } else {
        setError(errorMessage(caught));
      }
    } finally {
      setResending(false);
    }
  };

  return (
    <AuthLayout>
      <h1>Verifica tu cuenta</h1>
      <p className="acceso-nota acceso-inicial">
        Enviamos un código de 8 dígitos a tu correo institucional. Vence a los 5 minutos y
        admite 5 intentos.
      </p>

      {state?.notice ? (
        <div className="acceso-ok" role="status">
          {state.notice}
        </div>
      ) : null}

      <form onSubmit={onVerify} noValidate>
        <TextField
          label="Correo institucional"
          type="email"
          required
          autoComplete="username"
          placeholder="nombre@uniminuto.edu.co"
          value={correo}
          onChange={(event) => setCorreo(event.target.value)}
        />

        <div className="campo">
          <label htmlFor="codigo-verificacion">
            Código de verificación
            <span className="req" aria-hidden="true">
              *
            </span>
          </label>
          <OtpInput
            value={codigo}
            onChange={setCodigo}
            label="Código de verificación de 8 dígitos"
            disabled={sending}
          />
          <span className="ayuda">
            Pégalo completo o escríbelo dígito por dígito.
          </span>
        </div>

        <Button type="submit" variant="primario" className="ancho" loading={sending}>
          Verificar mi correo
        </Button>
      </form>

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}
      {ok ? (
        <div className="acceso-ok" role="status">
          {ok}
        </div>
      ) : null}

      <div className="fila-botones mt-24">
        <Button
          variant="secundario"
          loading={resending}
          disabled={countdown.active || !correo.trim()}
          onClick={onResend}
        >
          {countdown.active ? `Reenviar en ${countdown.seconds} s` : 'Reenviar código'}
        </Button>
        <Link className="btn btn-secundario" to="/login">
          Volver a iniciar sesión
        </Link>
      </div>

      <p className="acceso-nota acceso-nota-centro">
        Al verificar, tu cuenta queda en estado <b>Limitado</b> hasta que la coordinación
        del programa la active.
      </p>
    </AuthLayout>
  );
}
