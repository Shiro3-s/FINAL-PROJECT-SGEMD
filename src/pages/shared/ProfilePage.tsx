import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiError, apiSend } from '../../api/client.ts';
import { fullNameOf, roleKeyOf } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { nameOf } from '../../lib/labels.ts';
import {
  useAcademicPrograms,
  useMunicipalities,
  usePopulationTypes,
  useTypeUsers,
  useUniversityCenters,
} from '../../queries/catalogs.ts';
import { useUpdateMe } from '../../queries/users.ts';
import { ROLE_LABEL } from '../../navigation/nav.ts';

/**
 * Perfil propio. Es la vista que también usa una cuenta `Limitado` o
 * `Inactivo`: por eso no depende de ningún módulo de trabajo y solo edita los
 * campos que `PUT /users/me` admite.
 */
export function ProfilePage() {
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const updateMe = useUpdateMe();
  const [error, setError] = useState<string | null>(null);
  const [sendingCode, setSendingCode] = useState(false);

  const programs = useAcademicPrograms();
  const centers = useUniversityCenters();
  const municipalities = useMunicipalities();
  const population = usePopulationTypes();
  const typeUsers = useTypeUsers();

  if (!user || !role) return null;

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    const data = new FormData(event.currentTarget);
    const body = {
      nombres: String(data.get('nombres') ?? '').trim(),
      apellidos: String(data.get('apellidos') ?? '').trim(),
      nivelAcademico: (String(data.get('nivelAcademico') ?? '') || null) as string | null,
      programaAcademicoId: Number(data.get('programaAcademicoId')) || null,
      centroUniversitarioId: Number(data.get('centroUniversitarioId')) || null,
      municipioId: Number(data.get('municipioId')) || null,
      tipoPoblacionId: Number(data.get('tipoPoblacionId')) || null,
      tipoUsuarioId: Number(data.get('tipoUsuarioId')) || null,
    };
    updateMe.mutate(body, {
      onSuccess: () => showToast('Perfil actualizado.', 'ok'),
      onError: (caught) => setError(errorMessage(caught)),
    });
  };

  const sendPasswordCode = async (): Promise<void> => {
    setSendingCode(true);
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
      setSendingCode(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Mi perfil"
        sub="Datos de tu cuenta y tu información académica."
        crumbs={[{ label: ROLE_LABEL[role] }, { label: 'Perfil' }]}
        actions={<Badge state={user.estado}>{user.estado}</Badge>}
      />

      <div className="grid g-2">
        <Card title="Datos de la cuenta" hint="No editables desde aquí">
          <DefinitionList
            items={[
              { term: 'Nombre', value: fullNameOf(user) },
              { term: 'Código', value: user.codigo },
              { term: 'Correo institucional', value: user.correoInstitucional },
              { term: 'Documento', value: user.numeroDocumento ?? '—' },
              { term: 'Rol', value: user.rol.nombre },
              { term: 'Estado', value: <Badge state={user.estado}>{user.estado}</Badge> },
              {
                term: 'Correo verificado',
                value: user.verificado ? <Badge state="Activo">Verificado</Badge> : 'No',
              },
              { term: 'Última actividad', value: formatDateTime(user.ultimaActividad) },
            ]}
          />
          <Callout icon="lock">
            El correo, el documento, el rol y el estado los cambia la coordinación del programa.
          </Callout>
        </Card>

        <Card title="Datos académicos y de contacto" hint="Editables">
          <form onSubmit={onSubmit} noValidate>
            <TextField label="Nombres" name="nombres" required defaultValue={user.nombres} />
            <TextField label="Apellidos" name="apellidos" required defaultValue={user.apellidos} />
            <SelectField label="Nivel académico" name="nivelAcademico" defaultValue={user.nivelAcademico ?? ''}>
              <option value="">Sin definir</option>
              <option value="Pregrado">Pregrado</option>
              <option value="Posgrado">Posgrado</option>
              <option value="Egresado">Egresado</option>
            </SelectField>
            <SelectField
              label="Programa académico"
              name="programaAcademicoId"
              defaultValue={user.programaAcademicoId ?? ''}
            >
              <option value="">Sin definir</option>
              {(programs.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Centro universitario"
              name="centroUniversitarioId"
              defaultValue={user.centroUniversitarioId ?? ''}
            >
              <option value="">Sin definir</option>
              {(centers.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Municipio"
              name="municipioId"
              defaultValue={user.municipioId ?? ''}
              hint="El listado viene del catálogo de municipios del programa."
            >
              <option value="">Sin definir</option>
              {(municipalities.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre} ({item.departamento})
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Tipo de población"
              name="tipoPoblacionId"
              defaultValue={user.tipoPoblacionId ?? ''}
            >
              <option value="">Sin definir</option>
              {(population.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Tipo de usuario"
              name="tipoUsuarioId"
              defaultValue={user.tipoUsuarioId ?? ''}
            >
              <option value="">Sin definir</option>
              {(typeUsers.data ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </SelectField>

            {error ? (
              <div className="acceso-error" role="alert">
                {error}
              </div>
            ) : null}

            <div className="fila-acciones">
              <Button type="submit" variant="primario" loading={updateMe.isPending}>
                Guardar cambios
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Contraseña" hint="Flujo por código">
          <p className="ayuda" style={{ marginTop: 0 }}>
            La API no tiene un cambio de contraseña autenticado: se envía un código de 8
            dígitos al correo de la sesión y se fija la nueva en el flujo de recuperación.
          </p>
          <Button variant="secundario" icon="mail" loading={sendingCode} onClick={() => void sendPasswordCode()}>
            Enviar código a {user.correoInstitucional}
          </Button>
          <p className="nota-foot">
            También puedes entrar directamente a <Link to="/recuperar">recuperar contraseña</Link>.
          </p>
        </Card>

        {role === 'estudiante' ? (
          <Card title="Acta de compromiso" hint="FR-003">
            <p className="ayuda" style={{ marginTop: 0 }}>
              El acta firmada habilita tu asignación de docente. Una cuenta limitada puede
              cargarla y descargarla aunque no tenga acceso al resto de módulos.
            </p>
            <Link className="btn btn-secundario" to="/estudiante/acta">
              Ir a mi acta
            </Link>
          </Card>
        ) : null}

        <Card title="Resumen de catálogos" hint="Solo lectura">
          <DefinitionList
            items={[
              { term: 'Programa', value: nameOf(programs.data, user.programaAcademicoId) },
              { term: 'Centro', value: nameOf(centers.data, user.centroUniversitarioId) },
              {
                term: 'Municipio',
                value:
                  municipalities.data?.find((item) => item.id === user.municipioId)?.nombre ?? '—',
              },
              { term: 'Tipo de población', value: nameOf(population.data, user.tipoPoblacionId) },
              { term: 'Tipo de usuario', value: nameOf(typeUsers.data, user.tipoUsuarioId) },
            ]}
          />
        </Card>
      </div>
    </>
  );
}
