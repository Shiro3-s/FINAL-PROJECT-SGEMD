import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { roleKeyOf } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { useModalities } from '../../queries/catalogs.ts';
import { useCreateAdvice } from '../../queries/advice.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useUsers } from '../../queries/users.ts';

interface AdviceFormPageProps {
  basePath: string;
  roleLabel: string;
}

/**
 * Alta directa de una asesoría (docente asignado o administrador).
 *
 * El estudiante nunca usa esta vista: solicita una cita por la bandeja de
 * solicitudes y el administrador fija el docente y el bloque al aprobarla. El
 * horario es todo o nada: con bloque nace `Programada`; sin bloque, `Por agendar`.
 */
export function AdviceFormPage({ basePath, roleLabel }: AdviceFormPageProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const modalities = useModalities();
  const teachers = useUsers('teachers', { page: 1, pageSize: 100 });
  const create = useCreateAdvice();

  const [entrepreneurshipId, setEntrepreneurshipId] = useState('');
  const [docenteId, setDocenteId] = useState(role === 'docente' && user ? String(user.id) : '');
  const [tema, setTema] = useState('');
  const [modalidadId, setModalidadId] = useState('');
  const [lugarEnlace, setLugarEnlace] = useState('');
  const [fecha, setFecha] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFin, setHoraFin] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;

  return (
    <>
      <PageHeader
        title="Nueva asesoría"
        sub="Agenda una sesión de acompañamiento para un emprendimiento asignado."
        crumbs={[
          { label: roleLabel },
          { label: 'Asesorías', to: basePath },
          { label: 'Nueva' },
        ]}
      />

      <div className="grid g-2-1">
        <Card title="Datos de la sesión">
          <form
            onSubmit={(event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              setError(null);
              if (!entrepreneurshipId) {
                setError('Selecciona el emprendimiento.');
                return;
              }
              if (!docenteId) {
                setError('Selecciona el docente.');
                return;
              }
              if (tema.trim().length < 5) {
                setError('Escribe un tema de al menos 5 caracteres.');
                return;
              }
              const hasSomeTime = Boolean(fecha || horaInicio || horaFin);
              if (hasSomeTime && (!fecha || !horaInicio || !horaFin)) {
                setError('El horario se envía completo o no se envía.');
                return;
              }
              if (hasSomeTime && horaFin <= horaInicio) {
                setError('La hora de fin debe ser posterior a la de inicio.');
                return;
              }
              create.mutate(
                {
                  emprendimientoId: Number(entrepreneurshipId),
                  docenteId: Number(docenteId),
                  tema: tema.trim(),
                  ...(modalidadId ? { modalidadId: Number(modalidadId) } : {}),
                  ...(lugarEnlace.trim() ? { lugarEnlace: lugarEnlace.trim() } : {}),
                  ...(hasSomeTime ? { fecha, horaInicio, horaFin } : {}),
                },
                {
                  onSuccess: (advice) => {
                    showToast('Asesoría creada.', 'ok');
                    navigate(`${basePath}/${advice.id}`);
                  },
                  onError: (caught) => setError(errorMessage(caught)),
                },
              );
            }}
            noValidate
          >
            <SelectField
              label="Emprendimiento"
              required
              value={entrepreneurshipId}
              onChange={(event) => setEntrepreneurshipId(event.target.value)}
            >
              <option value="">Selecciona el emprendimiento</option>
              {(entrepreneurships.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.codigo} · {item.nombre}
                </option>
              ))}
            </SelectField>

            <SelectField
              label="Docente"
              required
              value={docenteId}
              onChange={(event) => setDocenteId(event.target.value)}
              hint={
                role === 'docente'
                  ? 'Un docente solo puede agendarse a sí mismo.'
                  : 'Solo docentes vigentes y activos.'
              }
              disabled={role === 'docente'}
            >
              <option value="">Selecciona el docente</option>
              {(teachers.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombres} {item.apellidos} · {item.codigo}
                </option>
              ))}
            </SelectField>

            <TextField
              label="Tema"
              required
              value={tema}
              onChange={(event) => setTema(event.target.value)}
              placeholder="Validación de la propuesta de valor"
            />

            <div className="grid g-2">
              <SelectField
                label="Modalidad"
                value={modalidadId}
                onChange={(event) => setModalidadId(event.target.value)}
              >
                <option value="">Sin modalidad</option>
                {(modalities.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.nombre}
                  </option>
                ))}
              </SelectField>
              <TextField
                label="Lugar o enlace"
                value={lugarEnlace}
                onChange={(event) => setLugarEnlace(event.target.value)}
                placeholder="https://meet.example.com/asesoria"
              />
            </div>

            <div className="grid g-3">
              <TextField
                label="Fecha"
                type="date"
                value={fecha}
                onChange={(event) => setFecha(event.target.value)}
              />
              <TextField
                label="Hora de inicio"
                type="time"
                value={horaInicio}
                onChange={(event) => setHoraInicio(event.target.value)}
              />
              <TextField
                label="Hora de fin"
                type="time"
                value={horaFin}
                onChange={(event) => setHoraFin(event.target.value)}
              />
            </div>

            {error ? (
              <div className="acceso-error" role="alert">
                {error}
              </div>
            ) : null}

            <div className="form-acciones">
              <Button variant="secundario" onClick={() => navigate(-1)}>
                Cancelar
              </Button>
              <Button type="submit" variant="primario" icon="calendar" loading={create.isPending}>
                Crear asesoría
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Reglas de agenda" hint="BR-002">
          <Callout icon="alerta">
            El servidor comprueba el solapamiento del docente y responde{' '}
            <code>ADVICE_SCHEDULE_CONFLICT</code>. Con horario, la asesoría nace{' '}
            <b>Programada</b> y el docente la confirma después.
          </Callout>
          <p className="ayuda">
            Una asesoría no se reprograma por el estudiante (P-1). Él solicita una cita nueva
            y el administrador la resuelve en la bandeja de solicitudes.
          </p>
        </Card>
      </div>
    </>
  );
}
