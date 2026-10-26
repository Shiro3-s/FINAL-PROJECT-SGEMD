import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { roleKeyOf, type Advice, type Diagnosis, type Entrepreneurship, type Task, type Tracing } from '../../api/types.ts';
import { ACTA_ESTADOS, DIAGNOSTICO_ESTADOS } from '@sgemd/shared';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { ReasonModal } from '../../components/ReasonModal.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import { useActas } from '../../queries/acta.ts';
import { useAdvices } from '../../queries/advice.ts';
import { useDiagnoses } from '../../queries/diagnosis.ts';
import {
  useApproveEntrepreneurship,
  useEntrepreneurship,
  useRejectEntrepreneurship,
} from '../../queries/entrepreneurship.ts';
import { useEntrepreneurshipTasks, useTaskAdvance } from '../../queries/tasks.ts';
import { useTracings } from '../../queries/tracing.ts';

interface ExpedientePageProps {
  basePath: string;
  roleLabel: string;
  /** Docente y admin ven el botón de registrar avance. */
  canManage: boolean;
}

/**
 * Expediente del emprendimiento, compartido por los tres roles.
 *
 * Consolida las consultas que la API expone por separado (tareas, avances,
 * asesorías, diagnósticos y actas del emprendimiento) en una sola vista con
 * pestañas. No inventa agregados: el avance sale de `GET /task/advance/...` y el
 * diagnóstico se muestra sin puntaje (AQ-09).
 */
export function ExpedientePage({ basePath, roleLabel, canManage }: ExpedientePageProps) {
  const { id } = useParams();
  const entrepreneurshipId = Number(id);
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const [tab, setTab] = useState('resumen');
  const [rejectOpen, setRejectOpen] = useState(false);

  const entrepreneurship = useEntrepreneurship(
    Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );
  const tasks = useEntrepreneurshipTasks(
    Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );
  const tracings = useTracings(Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null);
  const advices = useAdvices({
    emprendimientoId: Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : undefined,
    pageSize: 100,
  });
  const diagnoses = useDiagnoses({
    emprendimientoId: Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : undefined,
    pageSize: 100,
  });
  const actas = useActas({
    emprendimientoId: Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : undefined,
    pageSize: 20,
  });
  const advance = useTaskAdvance(
    Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );
  const approve = useApproveEntrepreneurship();
  const reject = useRejectEntrepreneurship();

  if (!role) return null;
  const isAdmin = role === 'administrador';
  const isTeacher = role === 'docente';
  const isStudent = role === 'estudiante';
  const canSeeActa = isAdmin || isStudent;
  const segment = isAdmin ? 'admin' : isTeacher ? 'docente' : 'estudiante';
  const taskPath = `/${segment}/tareas`;
  const tracingPath = isTeacher ? '/docente/avances' : `/${segment}/seguimiento`;
  const diagnosisPath = isStudent ? '/estudiante/diagnostico/resultado' : `/${segment}/diagnosticos`;
  const advicePath = `/${segment}/asesorias`;

  return (
    <>
      <PageHeader
        title="Expediente del emprendimiento"
        sub="Resumen, plan, diagnóstico, seguimiento y acompañamiento en un solo lugar."
        crumbs={[
          { label: roleLabel },
          { label: 'Emprendimientos', to: basePath },
          { label: 'Expediente' },
        ]}
      />

      <QueryGate query={entrepreneurship} loadingLabel="Cargando el expediente…">
        {(item: Entrepreneurship) => (
          <>
            <Card
              title={`${item.codigo} · ${item.nombre}`}
              hint={item.estudiante.nombres + ' ' + item.estudiante.apellidos}
              action={
                <div className="fila-acciones">
                  {item.estadoAprobacion === 'Pendiente' && isAdmin ? (
                    <>
                      <Button
                        variant="primario"
                        icon="check"
                        loading={approve.isPending}
                        onClick={() =>
                          approve.mutate(item.id, {
                            onSuccess: () => showToast('Emprendimiento aprobado.', 'ok'),
                            onError: (caught) => showToast(errorMessage(caught), 'error'),
                          })
                        }
                      >
                        Aprobar
                      </Button>
                      <Button variant="secundario" icon="x" onClick={() => setRejectOpen(true)}>
                        Rechazar
                      </Button>
                    </>
                  ) : null}
                  {isStudent || isAdmin ? (
                    <Link className="btn btn-secundario" to={`${basePath}/${item.id}/editar`}>
                      Editar
                    </Link>
                  ) : null}
                  {isAdmin ? (
                    <Link className="btn btn-secundario" to={`${basePath}/${item.id}/plan`}>
                      Ver plan
                    </Link>
                  ) : isStudent ? (
                    <Link className="btn btn-secundario" to="/estudiante/plan">
                      Ver plan
                    </Link>
                  ) : null}
                </div>
              }
            >
              <div className="fila-acciones" style={{ gap: 8, marginBottom: 12 }}>
                <Badge state={item.estadoAprobacion}>{item.estadoAprobacion}</Badge>
                {item.esParalelo ? <Badge state="Aprobada_Solicitud">Paralelo autorizado</Badge> : null}
                {isTeacher ? <span className="nota-foot" style={{ margin: 0 }}>Mentor asignado</span> : null}
              </div>
              <DefinitionList
                items={[
                  { term: 'Descripción', value: item.descripcion ?? 'Sin descripción.' },
                  { term: 'Redes sociales', value: item.redesSociales ?? '—' },
                  { term: 'Etapa', value: item.etapa?.nombre ?? 'Sin etapa' },
                  { term: 'Sector', value: item.sector?.nombre ?? 'Sin sector' },
                  { term: 'Centro universitario', value: item.centroUniversitario?.nombre ?? '—' },
                  {
                    term: 'Avance',
                    value: (
                      <span>
                        {item.avance}% <ProgressBar value={item.avance} label="Avance del emprendimiento" />
                      </span>
                    ),
                  },
                ]}
              />
              {item.motivoRechazo ? (
                <Callout icon="alerta">
                  <b>Motivo del rechazo:</b> {item.motivoRechazo}
                </Callout>
              ) : null}
            </Card>

            <div className="mt-14">
              <Tabs
                label="Secciones del expediente"
                active={tab}
                onChange={setTab}
                items={[
                  { id: 'resumen', label: 'Resumen' },
                  { id: 'tareas', label: `Tareas (${tasks.data?.total ?? 0})` },
                  { id: 'seguimiento', label: `Seguimiento (${tracings.data?.total ?? 0})` },
                  { id: 'diagnostico', label: `Diagnóstico (${diagnoses.data?.total ?? 0})` },
                  { id: 'asesorias', label: `Asesorías (${advices.data?.total ?? 0})` },
                  ...(canSeeActa ? [{ id: 'acta', label: 'Acta' }] : []),
                ]}
              />

              <TabPanel id="resumen" active={tab}>
                <div className="grid g-2">
                  <Card title="Avance por fase" hint="FR-022">
                    {advance.isPending ? <p className="ayuda">Cargando avance…</p> : null}
                    {advance.isError ? (
                      <p className="ayuda">{errorMessage(advance.error)}</p>
                    ) : null}
                    {advance.data ? (
                      <>
                        <p className="ayuda" style={{ marginTop: 0 }}>
                          {advance.data.completadas} de {advance.data.total} tareas completadas ·{' '}
                          {advance.data.avance}% de avance
                        </p>
                        <ProgressBar value={advance.data.avance} label="Avance total" />
                        <DefinitionList
                          items={advance.data.fases.map((phase) => ({
                            term: phase.fase ?? 'Sin fase',
                            value: (
                              <span>
                                {phase.completadas}/{phase.total} tareas · {phase.porcentaje}%
                              </span>
                            ),
                          }))}
                        />
                      </>
                    ) : null}
                  </Card>

                  <Card title="Ficha del estudiante" hint="Datos de la cuenta">
                    <DefinitionList
                      items={[
                        { term: 'Nombre', value: `${item.estudiante.nombres} ${item.estudiante.apellidos}` },
                        { term: 'Código', value: item.estudiante.codigo ?? '—' },
                        { term: 'Correo', value: item.estudiante.correoInstitucional ?? '—' },
                        {
                          term: 'Próximas asesorías',
                          value:
                            advices.data?.items
                              .filter(
                                (advice) =>
                                  advice.estado === 'Confirmada' || advice.estado === 'Programada',
                              )
                              .slice(0, 3)
                              .map((advice) => (
                                <div key={advice.id}>
                                  {advice.tema} ·{' '}
                                  {advice.fecha ? formatDate(`${advice.fecha}T12:00:00`) : 'Por agendar'}
                                </div>
                              )) ?? '—',
                        },
                      ]}
                    />
                    {canManage ? (
                      <div className="fila-acciones mt-14">
                        {isTeacher ? (
                          <Link className="btn btn-primario" to="/docente/avances/nuevo">
                            Registrar avance
                          </Link>
                        ) : null}
                        <Link className="btn btn-secundario" to={`${taskPath}/nueva`}>
                          Nueva tarea
                        </Link>
                      </div>
                    ) : null}
                  </Card>
                </div>
              </TabPanel>

              <TabPanel id="tareas" active={tab}>
                <Card flush>
                  {tasks.isPending ? <p className="ayuda" style={{ padding: 20 }}>Cargando tareas…</p> : null}
                  {tasks.data && tasks.data.items.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      El emprendimiento todavía no tiene tareas.
                    </p>
                  ) : null}
                  {tasks.data && tasks.data.items.length > 0 ? (
                    <div>
                      {tasks.data.items.map((task: Task) => (
                        <div className="aviso" key={task.id}>
                          <div style={{ flex: 1 }}>
                            <p style={{ margin: '0 0 4px' }}>
                              <b>{task.titulo}</b>
                            </p>
                            <div className="fila-acciones" style={{ gap: 8 }}>
                              <Badge state={task.estado}>{task.estado}</Badge>
                              <span className="nota-foot" style={{ margin: 0 }}>
                                Límite {formatDate(task.fechaLimite)} · {task.evidencias} evidencias
                              </span>
                            </div>
                          </div>
                          <Link className="btn btn-secundario btn-sm" to={`${taskPath}/${task.id}`}>
                            Ver
                          </Link>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </Card>
              </TabPanel>

              <TabPanel id="seguimiento" active={tab}>
                <Card flush>
                  {tracings.isPending ? <p className="ayuda" style={{ padding: 20 }}>Cargando avances…</p> : null}
                  {tracings.data && tracings.data.items.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay avances ni comentarios registrados.
                    </p>
                  ) : null}
                  {tracings.data && tracings.data.items.length > 0 ? (
                    <div>
                      {tracings.data.items.map((tracing: Tracing) => (
                        <div className="aviso" key={tracing.id}>
                          <div style={{ flex: 1 }}>
                            <div className="fila-acciones" style={{ gap: 8, marginBottom: 4 }}>
                              <Badge state={tracing.estadoRevision}>{tracing.estadoRevision}</Badge>
                              <span className="nota-foot" style={{ margin: 0 }}>
                                {formatDateTime(tracing.fechaSeguimiento)} ·{' '}
                                {tracing.autor
                                  ? `${tracing.autor.nombres} ${tracing.autor.apellidos}`
                                  : 'Autor no disponible'}
                              </span>
                            </div>
                            <p style={{ margin: '0 0 4px' }}>{tracing.descripcion}</p>
                            <span className="nota-foot" style={{ margin: 0 }}>
                              {tracing.tipo}
                              {tracing.fase ? ` · ${tracing.fase.nombre}` : ''}
                              {tracing.puntaje === null ? '' : ` · ${tracing.puntaje} puntos`}
                            </span>
                          </div>
                          <Link className="btn btn-secundario btn-sm" to={`${tracingPath}/${tracing.id}`}>
                            Ver
                          </Link>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </Card>
              </TabPanel>

              <TabPanel id="diagnostico" active={tab}>
                <Card flush>
                  {diagnoses.isPending ? <p className="ayuda" style={{ padding: 20 }}>Cargando diagnósticos…</p> : null}
                  {diagnoses.data && diagnoses.data.items.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay diagnóstico registrado.
                    </p>
                  ) : null}
                  {diagnoses.data && diagnoses.data.items.length > 0 ? (
                    <div>
                      {diagnoses.data.items.map((diagnosis: Diagnosis) => (
                        <div className="aviso" key={diagnosis.id}>
                          <div style={{ flex: 1 }}>
                            <div className="fila-acciones" style={{ gap: 8, marginBottom: 4 }}>
                              <Badge state={diagnosis.estado}>{diagnosis.estado}</Badge>
                              <span className="nota-foot" style={{ margin: 0 }}>
                                {diagnosis.respondidas}/{diagnosis.totalPreguntas} respuestas ·{' '}
                                {formatDateTime(diagnosis.fechaDiagnostico)}
                              </span>
                            </div>
                            <p className="ayuda" style={{ margin: 0 }}>
                              {diagnosis.puntuacion.disponible
                                ? `Puntaje ${diagnosis.puntajeTotal}`
                                : 'Sin puntaje: la rúbrica no está aprobada (AQ-09).'}
                            </p>
                          </div>
                          <Link
                            className="btn btn-secundario btn-sm"
                            to={
                              isStudent
                                ? '/estudiante/diagnostico/resultado'
                                : `${diagnosisPath}/${diagnosis.id}`
                            }
                          >
                            Ver
                          </Link>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </Card>
              </TabPanel>

              <TabPanel id="asesorias" active={tab}>
                <Card flush>
                  {advices.isPending ? <p className="ayuda" style={{ padding: 20 }}>Cargando asesorías…</p> : null}
                  {advices.data && advices.data.items.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay asesorías para este emprendimiento.
                    </p>
                  ) : null}
                  {advices.data && advices.data.items.length > 0 ? (
                    <div>
                      {advices.data.items.map((advice: Advice) => (
                        <div className="aviso" key={advice.id}>
                          <div style={{ flex: 1 }}>
                            <div className="fila-acciones" style={{ gap: 8, marginBottom: 4 }}>
                              <Badge state={advice.estado}>{advice.estado}</Badge>
                              <span className="nota-foot" style={{ margin: 0 }}>
                                {advice.fecha
                                  ? `${formatDate(`${advice.fecha}T12:00:00`)} · ${advice.horaInicio} a ${advice.horaFin}`
                                  : 'Por agendar'}
                              </span>
                            </div>
                            <p style={{ margin: '0 0 4px' }}>{advice.tema}</p>
                            <span className="nota-foot" style={{ margin: 0 }}>
                              {advice.docente
                                ? `${advice.docente.nombres} ${advice.docente.apellidos}`
                                : 'Sin docente asignado'}
                            </span>
                          </div>
                          <Link className="btn btn-secundario btn-sm" to={`${advicePath}/${advice.id}`}>
                            Ver
                          </Link>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </Card>
              </TabPanel>

              {canSeeActa ? (
                <TabPanel id="acta" active={tab}>
                  <Card flush>
                    {actas.isPending ? <p className="ayuda" style={{ padding: 20 }}>Cargando actas…</p> : null}
                    {actas.data && actas.data.items.length === 0 ? (
                      <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                        El emprendimiento no tiene acta cargada.
                      </p>
                    ) : null}
                    {actas.data && actas.data.items.length > 0 ? (
                      <div>
                        {actas.data.items.map((acta) => (
                          <div className="aviso" key={acta.id}>
                            <div style={{ flex: 1 }}>
                              <div className="fila-acciones" style={{ gap: 8, marginBottom: 4 }}>
                                <Badge state={acta.estado}>{acta.estado}</Badge>
                                <span className="nota-foot" style={{ margin: 0 }}>
                                  {acta.fechaCarga
                                    ? `Cargada ${formatDateTime(acta.fechaCarga)}`
                                    : 'Sin cargar'}
                                </span>
                              </div>
                              <p className="ayuda" style={{ margin: 0 }}>
                                {acta.adjunto?.nombreArchivo ?? 'Sin archivo adjunto'}
                                {acta.observaciones ? ` · ${acta.observaciones}` : ''}
                              </p>
                            </div>
                            {isAdmin && acta.estado === 'En revisión' ? (
                              <Link className="btn btn-secundario btn-sm" to="/admin/actas">
                                Revisar
                              </Link>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    ) : null}
                    {isAdmin ? (
                      <p className="ayuda" style={{ padding: '0 20px 20px' }}>
                        Los estados posibles del acta son {ACTA_ESTADOS.join(', ')}. La revisión
                        se hace en <Link to="/admin/actas">Actas de estudiantes</Link>.
                      </p>
                    ) : null}
                  </Card>
                </TabPanel>
              ) : null}
            </div>
          </>
        )}
      </QueryGate>

      <ReasonModal
        open={rejectOpen}
        title="Rechazar el emprendimiento"
        label="Motivo del rechazo"
        hint="El motivo se guarda y se muestra al estudiante en el expediente."
        confirmLabel="Rechazar"
        loading={reject.isPending}
        onClose={() => setRejectOpen(false)}
        onSubmit={(motivo) =>
          reject.mutate(
            { id: entrepreneurshipId, motivo },
            {
              onSuccess: () => {
                setRejectOpen(false);
                showToast('Emprendimiento rechazado.', 'ok');
              },
              onError: (caught) => showToast(errorMessage(caught), 'error'),
            },
          )
        }
      />

      <Callout icon="bombilla">
        Los estados del diagnóstico son {DIAGNOSTICO_ESTADOS.join(', ')}. La pestaña de acta
        solo aparece para el estudiante dueño y el administrador: el docente recibe{' '}
        <code>403</code> en <code>/acta</code>.
      </Callout>
    </>
  );
}
