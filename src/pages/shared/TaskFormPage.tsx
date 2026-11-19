import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { PRIORIDADES } from '@sgemd/shared';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { usePlanPhases } from '../../queries/catalogs.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useCreateTask } from '../../queries/tasks.ts';

interface TaskFormPageProps {
  basePath: string;
  roleLabel: string;
}

/**
 * Alta de tarea (FR-023).
 *
 * El servidor fija `estado`, `estadoRevision`, `evidenciaRequerida` y el
 * destinatario: no son campos del formulario. La tarea nace `Pendiente` y sin
 * evidencia; la compuerta se aplica en la entrega del estudiante.
 */
export function TaskFormPage({ basePath, roleLabel }: TaskFormPageProps) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const phases = usePlanPhases();
  const create = useCreateTask();

  const [entrepreneurshipId, setEntrepreneurshipId] = useState('');
  const [fasePlanId, setFasePlanId] = useState('');
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [fechaLimite, setFechaLimite] = useState('');
  const [prioridad, setPrioridad] = useState<string>(PRIORIDADES[1]);
  const [puntos, setPuntos] = useState('100');
  const [error, setError] = useState<string | null>(null);

  return (
    <>
      <PageHeader
        title="Nueva tarea"
        sub="Asigna una tarea con fecha límite y puntos al emprendimiento."
        crumbs={[
          { label: roleLabel },
          { label: 'Tareas', to: basePath },
          { label: 'Nueva' },
        ]}
      />

      <div className="grid g-2-1">
        <Card title="Datos de la tarea">
          <form
            onSubmit={(event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              setError(null);
              if (!entrepreneurshipId) {
                setError('Selecciona el emprendimiento.');
                return;
              }
              if (titulo.trim().length < 3) {
                setError('El título debe tener al menos 3 caracteres.');
                return;
              }
              const score = Number(puntos);
              if (!Number.isFinite(score) || score <= 0) {
                setError('Los puntos deben ser un número mayor que cero.');
                return;
              }
              create.mutate(
                {
                  emprendimientoId: Number(entrepreneurshipId),
                  titulo: titulo.trim(),
                  descripcion: descripcion.trim() || null,
                  ...(fasePlanId ? { fasePlanId: Number(fasePlanId) } : {}),
                  ...(fechaLimite ? { fechaLimite } : {}),
                  prioridad,
                  puntos: score,
                },
                {
                  onSuccess: (task) => {
                    showToast('Tarea creada.', 'ok');
                    navigate(`${basePath}/${task.id}`);
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
              hint="El estudiante destinatario se deriva del propietario del emprendimiento."
            >
              <option value="">Selecciona el emprendimiento</option>
              {(entrepreneurships.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.codigo} · {item.nombre}
                </option>
              ))}
            </SelectField>

            <TextField
              label="Título"
              required
              value={titulo}
              onChange={(event) => setTitulo(event.target.value)}
              placeholder="Subir evidencia fotográfica"
            />
            <TextAreaField
              label="Descripción"
              rows={4}
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
              hint="Qué debe entregar el estudiante y con qué criterio se califica."
            />

            <div className="grid g-2">
              <SelectField
                label="Fase del plan"
                value={fasePlanId}
                onChange={(event) => setFasePlanId(event.target.value)}
                hint="Opcional; sin fase la tarea se agrupa aparte."
              >
                <option value="">Sin fase</option>
                {(phases.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.nombre}
                  </option>
                ))}
              </SelectField>
              <TextField
                label="Fecha límite"
                type="date"
                value={fechaLimite}
                onChange={(event) => setFechaLimite(event.target.value)}
                hint="Opcional."
              />
            </div>

            <div className="grid g-2">
              <SelectField
                label="Prioridad"
                value={prioridad}
                onChange={(event) => setPrioridad(event.target.value)}
              >
                {PRIORIDADES.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </SelectField>
              <TextField
                label="Puntos"
                type="number"
                min={1}
                required
                value={puntos}
                onChange={(event) => setPuntos(event.target.value)}
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
              <Button type="submit" variant="primario" icon="check" loading={create.isPending}>
                Crear tarea
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Reglas de la tarea" hint="BR-007">
          <Callout icon="alerta">
            La tarea nace con <b>evidencia requerida</b>. El estudiante no puede entregarla
            sin al menos un archivo vigente: el servidor responde{' '}
            <code>TASK_EVIDENCE_REQUIRED</code>.
          </Callout>
          <p className="ayuda">
            Una vez entregada, la tarea no se edita. El docente califica de 0 a 100 o la
            devuelve con un motivo del vocabulario fijo.
          </p>
        </Card>
      </div>
    </>
  );
}
