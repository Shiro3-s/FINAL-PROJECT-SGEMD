import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import type { RequestItem } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { LoadingState, errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useCreateRequest } from '../../queries/requests.ts';

/**
 * Solicitud de cita de asesoría.
 *
 * No existe un endpoint para que el estudiante elija docente ni para reprogramar
 * (P-1): crea una solicitud `Cita` con sus preferencias en `detalle` (P-20) y el
 * administrador fija docente y bloque al aprobarla.
 */
export function StudentAdviceRequestPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const create = useCreateRequest();

  const [entrepreneurshipId, setEntrepreneurshipId] = useState('');
  const [fecha, setFecha] = useState('');
  const [hora, setHora] = useState('');
  const [temas, setTemas] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (entrepreneurships.isPending) {
    return <LoadingState label="Cargando tus emprendimientos…" />;
  }

  const items = entrepreneurships.data?.items ?? [];

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    const target = entrepreneurshipId || String(items[0]?.id ?? '');
    if (!target) {
      setError('Necesitas un emprendimiento registrado para solicitar una asesoría.');
      return;
    }
    if (!fecha) {
      setError('Indica la fecha preferida.');
      return;
    }
    if (!hora) {
      setError('Indica la hora preferida.');
      return;
    }
    if (temas.trim().length < 10) {
      setError('Describe los temas que quieres tratar (al menos 10 caracteres).');
      return;
    }

    const detalle = [
      `Fecha preferida: ${fecha}`,
      `Hora preferida: ${hora}`,
      '',
      temas.trim(),
    ].join('\n');

    create.mutate(
      { tipo: 'Cita', detalle, emprendimientoId: Number(target) },
      {
        onSuccess: (request: RequestItem) => {
          showToast(`Solicitud #${request.id} enviada.`, 'ok');
          navigate('/estudiante/asesorias');
        },
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  return (
    <>
      <PageHeader
        title="Solicitar asesoría"
        sub="Registra tu solicitud. El administrador confirmará docente, fecha y modalidad."
        crumbs={[
          { label: 'ESTUDIANTE' },
          { label: 'Asesorías', to: '/estudiante/asesorias' },
          { label: 'Solicitar' },
        ]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/asesorias">
            Volver
          </Link>
        }
      />

      {items.length === 0 ? (
        <Card title="Todavía no hay un emprendimiento registrado">
          <Callout icon="bombilla">
            La asesoría se solicita sobre un emprendimiento y el alta la hace la coordinación
            (D4).
          </Callout>
          <Link className="btn btn-primario" to="/estudiante/emprendimientos">
            Mi emprendimiento
          </Link>
        </Card>
      ) : (
        <div className="grid g-2-1">
          <Card title="Datos de la solicitud">
            <form onSubmit={submit} noValidate>
              <SelectField
                label="Emprendimiento"
                required
                value={entrepreneurshipId || String(items[0]?.id ?? '')}
                onChange={(event) => setEntrepreneurshipId(event.target.value)}
              >
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.codigo} — {item.nombre}
                  </option>
                ))}
              </SelectField>

              <div className="grid g-2">
                <TextField
                  label="Fecha preferida"
                  type="date"
                  required
                  value={fecha}
                  onChange={(event) => setFecha(event.target.value)}
                  hint="Es una preferencia; la fecha final la confirma la coordinación."
                />
                <TextField
                  label="Hora preferida"
                  type="time"
                  required
                  value={hora}
                  onChange={(event) => setHora(event.target.value)}
                  hint="Propuesta sujeta al bloque disponible del docente."
                />
              </div>

              <TextAreaField
                label="Temas a tratar"
                required
                rows={5}
                maxLength={1000}
                value={temas}
                onChange={(event) => setTemas(event.target.value)}
                placeholder="Describe los temas que quieres tratar en la asesoría"
                hint="Mientras más concreto, mejor podrá prepararse el docente."
              />

              <p className="nota-foot">
                La fecha y la hora viajan dentro del detalle de la solicitud: el modelo no
                tiene columnas propias para ellas (P-20). El docente se asigna según las
                reglas del programa, no lo elige el estudiante.
              </p>

              {error ? (
                <div className="acceso-error" role="alert">
                  {error}
                </div>
              ) : null}

              <div className="form-acciones">
                <Link className="btn btn-secundario" to="/estudiante/asesorias">
                  Cancelar
                </Link>
                <Button type="submit" variant="acento" icon="enviar" loading={create.isPending}>
                  Enviar solicitud
                </Button>
              </div>
            </form>
          </Card>

          <Card title="Cómo funciona">
            <DefinitionList
              items={[
                'Envías la solicitud con tus temas y preferencias.',
                'La coordinación la revisa y asigna docente y bloque.',
                'Se crea la asesoría y recibes la notificación.',
                'Asistes y la asesoría queda registrada.',
              ].map((text, index) => ({ term: `Paso ${index + 1}`, value: text }))}
            />
            <Callout icon="escudo">
              No puedes reprogramar una asesoría (P-1). Si necesitas otro horario, envía una
              solicitud nueva y la coordinación la resuelve en la bandeja.
            </Callout>
          </Card>
        </div>
      )}
    </>
  );
}
