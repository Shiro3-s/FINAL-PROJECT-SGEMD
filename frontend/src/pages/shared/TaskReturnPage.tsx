import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { roleKeyOf } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { useReturnTask, useTask } from '../../queries/tasks.ts';

const RETURN_REASONS = [
  'Evidencia incompleta',
  'No cumple con lo solicitado',
  'Archivos ilegibles',
  'Entrega fuera de fecha',
  'Otro motivo',
] as const;

interface TaskReturnPageProps {
  basePath: string;
  roleLabel: string;
}

/**
 * Devolución de una tarea al estudiante.
 *
 * Solo aplica sobre una tarea `En revisión`. El motivo pertenece al vocabulario
 * fijo del prototipo; las observaciones son opcionales. La evidencia original
 * sigue adjunta para que el estudiante corrija y vuelva a entregar.
 */
export function TaskReturnPage({ basePath, roleLabel }: TaskReturnPageProps) {
  const { id } = useParams();
  const taskId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const task = useTask(Number.isFinite(taskId) ? taskId : null);
  const returnTask = useReturnTask();
  const [motivo, setMotivo] = useState<string>(RETURN_REASONS[0]);
  const [observaciones, setObservaciones] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;

  return (
    <>
      <PageHeader
        title="Devolver tarea"
        sub="Explica qué debe corregir el estudiante antes de volver a entregar."
        crumbs={[
          { label: roleLabel },
          { label: 'Tareas', to: basePath },
          { label: 'Devolver' },
        ]}
      />

      <QueryGate query={task} loadingLabel="Cargando la tarea…">
        {(item) => (
          <div className="grid g-2-1">
            <Card title={item.titulo} hint={`${item.emprendimiento.codigo} · ${item.emprendimiento.nombre}`}>
              <form
                onSubmit={(event: FormEvent<HTMLFormElement>) => {
                  event.preventDefault();
                  setError(null);
                  returnTask.mutate(
                    {
                      id: item.id,
                      motivo,
                      ...(observaciones.trim() ? { observaciones: observaciones.trim() } : {}),
                    },
                    {
                      onSuccess: () => {
                        showToast('Tarea devuelta al estudiante.', 'ok');
                        navigate(`${basePath}/${item.id}`);
                      },
                      onError: (caught) => setError(errorMessage(caught)),
                    },
                  );
                }}
                noValidate
              >
                <SelectField
                  label="Motivo"
                  required
                  value={motivo}
                  onChange={(event) => setMotivo(event.target.value)}
                  hint="Vocabulario fijo del sistema."
                >
                  {RETURN_REASONS.map((reason) => (
                    <option key={reason} value={reason}>
                      {reason}
                    </option>
                  ))}
                </SelectField>
                <TextAreaField
                  label="Observaciones"
                  rows={5}
                  value={observaciones}
                  onChange={(event) => setObservaciones(event.target.value)}
                  hint="Opcional. Se envía al estudiante junto con el motivo."
                />
                {error ? (
                  <div className="acceso-error" role="alert">
                    {error}
                  </div>
                ) : null}
                <div className="form-acciones">
                  <Link className="btn btn-secundario" to={`${basePath}/${item.id}`}>
                    Cancelar
                  </Link>
                  <Button type="submit" variant="primario" icon="alerta" loading={returnTask.isPending}>
                    Devolver tarea
                  </Button>
                </div>
              </form>
            </Card>

            <Card title="Estado actual" hint="Transición">
              <Callout icon={item.estadoRevision === 'En revisión' ? 'check' : 'alerta'}>
                {item.estadoRevision === 'En revisión'
                  ? 'La tarea está en revisión y puede devolverse. Al hacerlo queda «Devuelta» y el estudiante recibe el aviso.'
                  : `La tarea está en «${item.estadoRevision}»: solo se devuelve desde «En revisión».`}
              </Callout>
              <p className="ayuda">
                Entrega: {item.fechaEnvio ?? 'sin entregar'} · Evidencias: {item.evidencias}
              </p>
            </Card>
          </div>
        )}
      </QueryGate>
    </>
  );
}
