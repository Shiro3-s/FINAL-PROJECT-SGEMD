import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { ApiError, apiSend } from '../../api/client.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { AuthLayout } from '../../components/AuthLayout.tsx';
import { Button } from '../../components/Button.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useTypeDocuments } from '../../queries/catalogs.ts';

interface RegisterResponse {
  id: number;
  correoInstitucional: string;
  verificado: boolean;
  estado: string;
}

/**
 * Registro público de estudiante.
 *
 * Solo los seis campos que existen en `usuarios` más la autorización de
 * tratamiento (P-14). El prototipo pedía correo personal, celular y una segunda
 * casilla: no hay columnas para ellos y no se inventan (discrepancia #18).
 */
export function RegisterPage() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const typeDocuments = useTypeDocuments();

  const [nombres, setNombres] = useState('');
  const [apellidos, setApellidos] = useState('');
  const [tipoDocumentoId, setTipoDocumentoId] = useState('');
  const [numeroDocumento, setNumeroDocumento] = useState('');
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [acepta, setAcepta] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [sending, setSending] = useState(false);

  if (!isLoading && user) return <Navigate to="/" replace />;

  const fieldError = (name: string): string | undefined => fields[name];

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setFields({});

    if (!acepta) {
      setError('Debes autorizar el tratamiento de tus datos para continuar.');
      return;
    }
    if (password.length < 8) {
      setFields({ password: 'La contraseña debe tener al menos 8 caracteres.' });
      return;
    }

    setSending(true);
    try {
      const created = await apiSend<RegisterResponse>('POST', '/auth/register', {
        nombres: nombres.trim(),
        apellidos: apellidos.trim(),
        tipoDocumentoId: Number(tipoDocumentoId),
        numeroDocumento: numeroDocumento.trim(),
        correoInstitucional: correo.trim(),
        password,
        aceptaTratamiento: true,
      });
      navigate('/verificar', {
        replace: true,
        state: {
          correo: created.correoInstitucional,
          notice:
            'Cuenta creada. Revisa tu correo institucional: enviamos un código de 8 dígitos.',
        },
      });
    } catch (caught) {
      if (caught instanceof ApiError && caught.fields) {
        setFields(caught.fields);
      }
      setError(errorMessage(caught));
    } finally {
      setSending(false);
    }
  };

  return (
    <AuthLayout>
      <h1>Crear mi cuenta</h1>
      <p className="acceso-nota acceso-inicial">
        Completa tus datos. Recibirás un código de verificación de 8 dígitos en tu correo
        institucional.
      </p>

      {typeDocuments.isError ? (
        <div className="acceso-error" role="alert">
          No fue posible cargar los tipos de documento. Recarga la página para volver a
          intentarlo.
        </div>
      ) : null}

      <form onSubmit={onSubmit} noValidate>
        <div className="grid g-2" style={{ gap: '0 16px' }}>
          <TextField
            label="Nombres"
            required
            maxLength={100}
            placeholder="Ej. Mariana"
            value={nombres}
            error={fieldError('nombres')}
            onChange={(event) => setNombres(event.target.value)}
          />
          <TextField
            label="Apellidos"
            required
            maxLength={100}
            placeholder="Ej. López Herrera"
            value={apellidos}
            error={fieldError('apellidos')}
            onChange={(event) => setApellidos(event.target.value)}
          />
        </div>

        <div className="grid g-2" style={{ gap: '0 16px' }}>
          <SelectField
            label="Tipo de documento"
            required
            placeholder={typeDocuments.isPending ? 'Cargando…' : 'Selecciona'}
            value={tipoDocumentoId}
            error={fieldError('tipoDocumentoId')}
            onChange={(event) => setTipoDocumentoId(event.target.value)}
          >
            {(typeDocuments.data ?? []).map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
          <TextField
            label="Número de documento"
            required
            maxLength={30}
            placeholder="1020304050"
            value={numeroDocumento}
            error={fieldError('numeroDocumento')}
            onChange={(event) => setNumeroDocumento(event.target.value)}
          />
        </div>

        <TextField
          label="Correo institucional"
          type="email"
          required
          maxLength={150}
          placeholder="nombre@uniminuto.edu.co"
          hint="Aquí recibirás las notificaciones del sistema."
          value={correo}
          error={fieldError('correoInstitucional')}
          onChange={(event) => setCorreo(event.target.value)}
        />

        <TextField
          label="Contraseña"
          type="password"
          required
          minLength={8}
          maxLength={128}
          autoComplete="new-password"
          placeholder="Mínimo 8 caracteres"
          hint="Mínimo 8 caracteres."
          value={password}
          error={fieldError('password')}
          onChange={(event) => setPassword(event.target.value)}
        />

        <label className="chk">
          <input
            type="checkbox"
            checked={acepta}
            onChange={(event) => setAcepta(event.target.checked)}
          />
          <span>
            Acepto el tratamiento de mis datos personales y la política de privacidad de la
            institución.
          </span>
        </label>

        <Button
          type="submit"
          variant="acento"
          className="ancho"
          loading={sending}
          disabled={typeDocuments.isPending}
        >
          Crear cuenta y verificarme
        </Button>
      </form>

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      <p className="acceso-nota acceso-nota-centro">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login">
          <b>Inicia sesión</b>
        </Link>
      </p>
    </AuthLayout>
  );
}
