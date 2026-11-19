import { useState, type FormEvent } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ApiError, apiSend } from '../../api/client.ts';
import { AuthLayout } from '../../components/AuthLayout.tsx';
import { Button } from '../../components/Button.tsx';
import { TextField } from '../../components/FormField.tsx';
import { OtpInput } from '../../components/OtpInput.tsx';
import { Steps } from '../../components/DefinitionList.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useCountdown } from '../../hooks/useCountdown.ts';

type Step = 1 | 2 | 3;

// La API usa un código de 8 dígitos, no un enlace con token: la vista se
// implementa como flujo de tres pasos sobre el mismo endpoint (§9.1 y P-6).
const STEPS = [{ label: 'Tu correo' }, { label: 'Código y contraseña' }, { label: 'Listo' }];

/**
 * Recuperación de contraseña.
 *
 * Paso 1 pide el correo; el backend responde siempre 200 para no revelar si
 * existe. Paso 2 canjea el OTP y fija la contraseña nueva. No hay endpoint
 * autenticado de cambio de contraseña: este es el único camino.
 */
export function RecoverPage() {
  const location = useLocation();
  const prefill = (location.state as { correo?: string } | null)?.correo ?? '';
  const [step, setStep] = useState<Step>(1);
  const [correo, setCorreo] = useState(prefill);
  const [codigo, setCodigo] = useState('');
  const [password, setPassword] = useState('');
  const [confirmacion, setConfirmacion] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [resending, setResending] = useState(false);
  const countdown = useCountdown(0);

  const askCode = async (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    setError(null);
    setSending(true);
    try {
      await apiSend<unknown>('POST', '/auth/forgot-password', {
        correoInstitucional: correo.trim(),
      });
      countdown.start(60);
      setStep(2);
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'RATE_LIMITED') {
        setError('Demasiadas solicitudes. Espera unos minutos y vuelve a intentar.');
      } else {
        setError(errorMessage(caught));
      }
    } finally {
      setSending(false);
    }
  };

  const reset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (codigo.length !== 8) {
      setError('Escribe los 8 dígitos del código que enviamos a tu correo.');
      return;
    }
    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (password !== confirmacion) {
      setError('Las dos contraseñas no coinciden.');
      return;
    }
    setSending(true);
    try {
      await apiSend<unknown>('POST', '/auth/reset-password', {
        correoInstitucional: correo.trim(),
        codigo,
        password,
      });
      setStep(3);
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'OTP_INVALID') {
        setError('El código no es válido o ya venció. Solicita uno nuevo.');
      } else if (caught instanceof ApiError && caught.code === 'OTP_ATTEMPTS_EXCEEDED') {
        setError('Se agotaron los intentos del código. Solicita uno nuevo.');
      } else if (caught instanceof ApiError && caught.code === 'RATE_LIMITED') {
        setError('Demasiados intentos. Espera unos minutos y vuelve a intentar.');
      } else {
        setError(errorMessage(caught));
      }
    } finally {
      setSending(false);
    }
  };

  const resend = async () => {
    setError(null);
    setResending(true);
    try {
      await apiSend<unknown>('POST', '/auth/forgot-password', {
        correoInstitucional: correo.trim(),
      });
      countdown.start(60);
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'RATE_LIMITED') {
        setError('Demasiadas solicitudes. Espera unos minutos y vuelve a intentar.');
      } else {
        setError(errorMessage(caught));
      }
    } finally {
      setResending(false);
    }
  };

  return (
    <AuthLayout>
      <h1>Recuperar contraseña</h1>
      <Steps items={STEPS} current={step} />

      {step === 1 ? (
        <>
          <p className="acceso-nota acceso-inicial">
            Escribe tu correo institucional. Si existe una cuenta asociada, enviamos un
            código de 8 dígitos para establecer una contraseña nueva.
          </p>
          <form onSubmit={askCode} noValidate>
            <TextField
              label="Correo institucional"
              type="email"
              required
              autoComplete="username"
              placeholder="nombre@uniminuto.edu.co"
              value={correo}
              onChange={(event) => setCorreo(event.target.value)}
            />
            <Button
              type="submit"
              variant="primario"
              className="ancho"
              loading={sending}
              disabled={!correo.trim()}
            >
              Enviar código
            </Button>
          </form>
        </>
      ) : null}

      {step === 2 ? (
        <>
          <p className="acceso-nota acceso-inicial">
            Si <b>{correo.trim()}</b> tiene una cuenta, el código ya va en camino. Vence a
            los 5 minutos y admite 5 intentos.
          </p>
          <form onSubmit={reset} noValidate>
            <div className="campo">
              <label htmlFor="codigo-recuperacion">
                Código de recuperación
                <span className="req" aria-hidden="true">
                  *
                </span>
              </label>
              <OtpInput
                value={codigo}
                onChange={setCodigo}
                label="Código de recuperación de 8 dígitos"
                disabled={sending}
              />
            </div>
            <TextField
              label="Nueva contraseña"
              type="password"
              required
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              placeholder="Mínimo 8 caracteres"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            <TextField
              label="Confirma la nueva contraseña"
              type="password"
              required
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              placeholder="Repite la contraseña"
              value={confirmacion}
              onChange={(event) => setConfirmacion(event.target.value)}
            />
            <Button type="submit" variant="primario" className="ancho" loading={sending}>
              Guardar contraseña
            </Button>
          </form>
          <div className="fila-botones mt-24">
            <Button
              variant="secundario"
              loading={resending}
              disabled={countdown.active}
              onClick={resend}
            >
              {countdown.active ? `Reenviar en ${countdown.seconds} s` : 'Reenviar código'}
            </Button>
            <Button
              variant="secundario"
              onClick={() => {
                setError(null);
                setStep(1);
              }}
            >
              Cambiar correo
            </Button>
          </div>
        </>
      ) : null}

      {step === 3 ? (
        <>
          <div className="acceso-ok" role="status">
            Contraseña actualizada. Ya puedes iniciar sesión con tu nueva contraseña.
          </div>
          <Link className="btn btn-primario ancho mt-24" to="/login">
            Iniciar sesión
          </Link>
        </>
      ) : null}

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      {step !== 3 ? (
        <p className="acceso-nota acceso-nota-centro">
          ¿Recuerdas tu contraseña?{' '}
          <Link to="/login">
            <b>Vuelve al inicio de sesión</b>
          </Link>
        </p>
      ) : null}
    </AuthLayout>
  );
}
