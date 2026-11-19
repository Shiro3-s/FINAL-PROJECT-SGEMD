import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiError, apiSend } from '../../api/client.ts';
import { roleKeyOf } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, Steps } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { ROLE_LABEL } from '../../navigation/nav.ts';

/**
 * Cambio de contraseña de una sesión abierta.
 *
 * La API no ofrece `PUT /auth/password`: el camino real es pedir un código de
 * recuperación al correo de la sesión y canjearlo en `/recuperar`. Esta vista
 * explica el delta y dispara el envío; no inventa un formulario de contraseña
 * actual que el servidor no puede validar.
 */
export function PasswordPage() {
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user || !role) return null;

  const sendCode = async (): Promise<void> => {
    setError(null);
    setSending(true);
    try {
      await apiSend<unknown>('POST', '/auth/forgot-password', {
        correoInstitucional: user.correoInstitucional,
      });
      showToast('Enviamos un código a tu correo institucional.', 'ok');
      navigate('/recuperar', { state: { correo: user.correoInstitucional } });
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

  return (
    <>
      <PageHeader
        title="Cambiar contraseña"
        sub="El cambio se confirma con un código enviado a tu correo institucional."
        crumbs={[{ label: ROLE_LABEL[role] }, { label: 'Contraseña' }]}
      />

      <div className="grid g-2">
        <Card title="Cómo funciona" hint="Flujo por código">
          <Steps
            items={[
              { label: 'Solicitas el código' },
              { label: 'Escribes el código y la nueva contraseña' },
              { label: 'Inicias sesión con la nueva' },
            ]}
            current={1}
          />
          <Callout icon="lock">
            La sesión actual sigue abierta mientras haces el cambio. El código vence a los
            5 minutos, admite 5 intentos y el reenvío espera 60 segundos.
          </Callout>
        </Card>

        <Card title="Enviar el código" hint={user.correoInstitucional}>
          <p className="ayuda" style={{ marginTop: 0 }}>
            Enviaremos un código de 8 dígitos a <b>{user.correoInstitucional}</b>. Si no
            llega, revisa el correo institucional y la carpeta de spam.
          </p>
          {error ? (
            <div className="acceso-error" role="alert">
              {error}
            </div>
          ) : null}
          <div className="fila-acciones">
            <Button variant="primario" icon="mail" loading={sending} onClick={() => void sendCode()}>
              Enviar código de cambio
            </Button>
            <Link className="btn btn-secundario" to={`/${role}/perfil`}>
              Volver al perfil
            </Link>
          </div>
          <p className="nota-foot">
            ¿Prefieres hacerlo sin pasar por aquí? Entra a{' '}
            <Link to="/recuperar">recuperar contraseña</Link>.
          </p>
        </Card>
      </div>
    </>
  );
}
