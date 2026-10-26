import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { roleKeyOf, type Task } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { EvidenceUploader } from '../../components/EvidenceUploader.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { TextAreaField, TextField } from '../../components/FormField.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import { useCompleteTask, useGradeTask, useTask, useUpdateTask } from '../../queries/tasks.ts';

interface TaskDetailPageProps {
  basePath: string;
  roleLabel: string;
  /** Ruta del formulario de devolución (solo docente/admin). */
  returnPath?: string;
}

/**
 * Detalle de una tarea.
 *
 * La misma tarea se ve distinto según el rol, pero las transiciones son las del
 * servidor: el estudiante entrega (con al menos una evidencia), el docente y el
 * administrador califican o devuelven. No hay un botón de "completar" para el
 * docente: eso lo hace la calificación.
 */
export function TaskDetailPage({ basePath, roleLabel, returnPath }: TaskDetailPageProps) {
  const { id } = useParams();
  const taskId = Number(id);
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const taskQuery = useTask(Number.isFinite(taskId) ? taskId : null);
  const complete = useCompleteTask();
  const update = useUpdateTask(taskId);
  const grade = useGradeTask();

  const [puntaje, setPuntaje] = useState('');
  const [retro, setRetro] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;
  const isStudent = role === 'estudiante';
  const canGrade = role === 'docente' || role === 'administrador';

  return (
    <>
      <PageHeader
        title="Detalle de la tarea"
        sub="Entrega, revisión y calificación."
        crumbs={[
          { label: roleLabel },
          { label: 'Tareas', to: basePath },
          { label: 'Detalle' },
        ]}
      />
      <QueryGate query={taskQuery} loadingLabel="Cargando la tarea…">
        {(task: Task) => (
          <div className="grid g-2-1">
            <div className="grid">
              <Card title={task.titulo} hint={`${task.emprendimiento.codigo} · ${task.emprendimiento.nombre}`}>
                <div className="fila-acciones" style={{ gap: 8, marginBottom: 14 }}>
                  <Badge state={task.estado}>{task.estado}</Badge>
                  <Badge state={task.prioridad}>{task.prioridad}</Badge>
                  <Badge state={task.estadoRevision}>{`Revisión: ${task.estadoRevision}`}</Badge>
                  {task.vencida && task.estado !== 'Completada' ? <Badge state="Vencida">Vencida</Badge> : null}
                </div>
                <DefinitionList
                  items={[
                    { term: 'Descripción', value: task.descripcion ?? 'Sin descripción.' },
                    { term: 'Fecha límite', value: task.fechaLimite ? formatDate(task.fechaLimite) : 'Sin fecha límite' },
                    { term: 'Fase', value: task.fase?.nombre ?? 'Sin fase' },
                    { term: 'Puntos', value: `${task.puntos} puntos` },
                    { term: 'Estudiante', value: `${task.estudiante.nombres} ${task.estudiante.apellidos}` },
                    { term: 'Asignada por', value: `${task.creador.nombres} ${task.creador.apellidos}` },
                    { term: 'Fecha de entrega', value: task.fechaEnvio ? formatDateTime(task.fechaEnvio) : 'Sin entregar' },
                    { term: 'Puntaje obtenido', value: task.puntajeObtenido === null ? 'Sin calificar' : `${task.puntajeObtenido} / ${task.puntos}` },
                    { term: 'Retroalimentación', value: task.retroalimentacion ?? '—' },
                    {
                      term: 'Evidencias',
                      value: `${task.evidencias} ${task.evidencias === 1 ? 'archivo' : 'archivos'}`,
                    },
                  ]}
                />
                {task.estado === 'Devuelta' ? (
                  <Callout icon="alerta">
                    <b>Devuelta:</b> {task.motivoDevolucion ?? 'Sin motivo registrado'}.
                    {task.observacionesDevolucion ? ` ${task.observacionesDevolucion}` : ''}
                  </Callout>
                ) : null}
                {task.estado === 'En revisión' && isStudent ? (
                  <Callout icon="reloj">
                    La tarea está en revisión. La evidencia queda congelada hasta que el
                    docente la califique o la devuelva.
                  </Callout>
                ) : null}
              </Card>

              <Card title="Evidencias" hint="La API expone el conteo">
                <EvidenceUploader
                  entity="task"
                  entityId={task.id}
                  count={task.evidencias}
                  disabled={
                    !isStudent ||
                    task.estado === 'En revisión' ||
                    task.estado === 'Completada' ||
                    complete.isPending
                  }
                  note={
                    isStudent
                      ? 'Solo JPG, PNG o PDF. Una tarea necesita al menos una evidencia antes de entregarse.'
                      : 'El estudiante carga las evidencias; la revisión se hace sobre ese material.'
                  }
                />
              </Card>
            </div>

            <div className="grid">
              {isStudent ? (
                <Card title="Entrega" hint="FR-023">
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    Entregar deja la tarea <b>En revisión</b>. El servidor exige al menos una
                    evidencia vigente; si no la hay, responde <code>TASK_EVIDENCE_REQUIRED</code>.
                  </p>
                  <div className="fila-acciones">
                    {task.estado === 'Pendiente' ? (
                      <Button
                        variant="secundario"
                        loading={update.isPending}
                        onClick={() =>
                          update.mutate(
                            { estado: 'En curso' },
                            {
                              onSuccess: () => showToast('Tarea marcada en curso.', 'ok'),
                              onError: (caught) => showToast(errorMessage(caught), 'error'),
                            },
                          )
                        }
                      >
                        Marcar en curso
                      </Button>
                    ) : null}
                    <Button
                      variant="primario"
                      icon="enviar"
                      loading={complete.isPending}
                      disabled={task.estado === 'En revisión' || task.estado === 'Completada' || task.evidencias === 0}
                      onClick={() =>
                        complete.mutate(task.id, {
                          onSuccess: () => showToast('Tarea entregada para revisión.', 'ok'),
                          onError: (caught) => showToast(errorMessage(caught), 'error'),
                        })
                      }
                    >
                      Entregar tarea
                    </Button>
                  </div>
                  {task.evidencias === 0 ? (
                    <p className="nota-foot">Sube al menos una evidencia para habilitar la entrega.</p>
                  ) : null}
                </Card>
              ) : null}

              {canGrade && task.estadoRevision === 'En revisión' ? (
                <Card title="Calificar" hint="0 a 100">
                  <form
                    onSubmit={(event: FormEvent<HTMLFormElement>) => {
                      event.preventDefault();
                      setError(null);
                      const value = Number(puntaje);
                      if (!Number.isFinite(value) || value < 0 || value > 100) {
                        setError('El puntaje debe estar entre 0 y 100.');
                        return;
                      }
                      if (retro.trim().length < 3) {
                        setError('Escribe una retroalimentación para el estudiante.');
                        return;
                      }
                      grade.mutate(
                        { id: task.id, puntajeObtenido: value, retroalimentacion: retro.trim() },
                        {
                          onSuccess: () => showToast('Tarea calificada.', 'ok'),
                          onError: (caught) => setError(errorMessage(caught)),
                        },
                      );
                    }}
                    noValidate
                  >
                    <TextField
                      label="Puntaje obtenido"
                      type="number"
                      min={0}
                      max={100}
                      required
                      value={puntaje}
                      onChange={(event) => setPuntaje(event.target.value)}
                      hint={`Sobre ${task.puntos} puntos de la tarea.`}
                    />
                    <TextAreaField
                      label="Retroalimentación"
                      required
                      rows={4}
                      value={retro}
                      onChange={(event) => setRetro(event.target.value)}
                    />
                    {error ? (
                      <div className="acceso-error" role="alert">
                        {error}
                      </div>
                    ) : null}
                    <div className="fila-acciones">
                      <Button type="submit" variant="primario" loading={grade.isPending}>
                        Guardar calificación
                      </Button>
                      {returnPath ? (
                        <Link className="btn btn-secundario" to={returnPath.replace(':id', String(task.id))}>
                          Devolver tarea
                        </Link>
                      ) : null}
                    </div>
                  </form>
                </Card>
              ) : null}
            </div>
          </div>
        )}
      </QueryGate>
    </>
  );
}
