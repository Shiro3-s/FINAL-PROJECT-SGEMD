import { Link } from 'react-router-dom';
import { fullNameOf } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { formatDate } from '../../lib/format.ts';
import { useStudentDashboard } from '../../queries/dashboards.ts';

/**
 * Inicio del estudiante.
 *
 * Una sola consulta agregada (`GET /dashboard/student`) alimenta las métricas y
 * los bloques. Las tarjetas que llevan a listas usan `?f=` para que el filtro se
 * aplique en el servidor. Un estudiante sin emprendimiento ve la explicación de
 * D4: el alta la hace la coordinación, no él.
 */
export function StudentDashboardPage() {
  const { user } = useAuth();
  const dashboard = useStudentDashboard();

  return (
    <>
      <PageHeader
        title={`Hola, ${user?.nombres ?? 'estudiante'}`}
        sub="Este es el estado de tu emprendimiento y tus próximos compromisos."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Inicio' }]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/notificaciones">
            Ver notificaciones
          </Link>
        }
      />

      <QueryGate query={dashboard} loadingLabel="Cargando tu tablero…">
        {(data) => (
          <>
            {!data.emprendimiento ? (
              <Card title="Tu emprendimiento todavía no está registrado">
                <Callout icon="bombilla">
                  El alta del emprendimiento la hace la coordinación del programa (D4): no
                  existe una pantalla para que el estudiante lo cree. Cuando esté registrado,
                  aquí verás su avance, tus tareas y tus asesorías.
                </Callout>
                <p className="ayuda">
                  {fullNameOf(user ?? { nombres: '', apellidos: '' })} · Mientras tanto puedes
                  completar tu perfil y consultar tus notificaciones.
                </p>
                <div className="fila-acciones">
                  <Link className="btn btn-primario" to="/estudiante/perfil">
                    Completar mi perfil
                  </Link>
                  <Link className="btn btn-secundario" to="/estudiante/acta">
                    Ver mi acta
                  </Link>
                </div>
              </Card>
            ) : (
              <>
                <div className="grid g-4">
                  <Metric
                    icon="trend"
                    label="Avance del emprendimiento"
                    value={data.emprendimiento.avance}
                    unit="%"
                    progress={data.emprendimiento.avance}
                    to="/estudiante/estado"
                  />
                  <Metric
                    icon="checklist"
                    label="Tareas pendientes"
                    value={data.tareas.pendientes}
                    to="/estudiante/tareas?f=Pendiente"
                  />
                  <Metric
                    icon="check"
                    label="Tareas completadas"
                    value={data.tareas.completadas}
                    to="/estudiante/tareas?f=Completada"
                  />
                  <Metric
                    icon="chat"
                    label="Asesorías próximas"
                    value={data.asesorias.proximas}
                    to="/estudiante/asesorias"
                  />
                </div>

                <div className="grid g-2-1 mt-14">
                  <Card
                    title={data.emprendimiento.nombre}
                    hint={`${data.emprendimiento.codigo} · ${data.emprendimiento.estadoAprobacion}`}
                    action={
                      <Badge state={data.emprendimiento.estadoAprobacion}>
                        {data.emprendimiento.estadoAprobacion}
                      </Badge>
                    }
                  >
                    <DefinitionList
                      items={[
                        {
                          term: 'Diagnóstico',
                          value: data.diagnostico
                            ? `${data.diagnostico.estado} · sin puntaje mientras la rúbrica no esté aprobada (AQ-09)`
                            : 'Sin iniciar',
                        },
                        {
                          term: 'Acta',
                          value: data.acta?.estado ?? 'Sin cargar',
                        },
                        {
                          term: 'Asesorías realizadas',
                          value: `${data.asesorias.realizadas}`,
                        },
                        {
                          term: 'Notificaciones sin leer',
                          value: `${data.notificacionesSinLeer}`,
                        },
                      ]}
                    />
                    <div className="fila-acciones">
                      <Link className="btn btn-primario" to={`/estudiante/emprendimientos/${data.emprendimiento.id}`}>
                        Abrir expediente
                      </Link>
                      <Link className="btn btn-secundario" to="/estudiante/plan">
                        Plan de trabajo
                      </Link>
                    </div>
                  </Card>

                  <Card title="Avance por fase" hint="FR-022">
                    {data.fases.length === 0 ? (
                      <p className="ayuda" style={{ marginTop: 0 }}>
                        Todavía no hay fases con tareas.
                      </p>
                    ) : (
                      data.fases.map((phase) => (
                        <div key={`${phase.faseId ?? 'sin-fase'}`} style={{ marginBottom: 14 }}>
                          <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                            <b>{phase.fase ?? 'Sin fase'}</b>
                            <span className="nota-foot" style={{ margin: 0 }}>
                              {phase.completadas}/{phase.total}
                            </span>
                          </div>
                          <ProgressBar value={phase.porcentaje} label={phase.fase ?? 'Sin fase'} />
                        </div>
                      ))
                    )}
                  </Card>
                </div>

                <div className="grid g-2 mt-14">
                  <Card title="Tareas por completar" hint="Prioridad y fecha límite" flush>
                    {data.tareasPorCompletar.length === 0 ? (
                      <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                        No tienes tareas pendientes. Buen trabajo.
                      </p>
                    ) : (
                      <div>
                        {data.tareasPorCompletar.map((task) => (
                          <div className="aviso" key={task.id}>
                            <div style={{ flex: 1 }}>
                              <Link to={`/estudiante/tareas/${task.id}`}>
                                <b>{task.titulo}</b>
                              </Link>
                              <div className="fila-acciones" style={{ gap: 8, marginTop: 4 }}>
                                <Badge state={task.prioridad}>{task.prioridad}</Badge>
                                <span className="nota-foot" style={{ margin: 0 }}>
                                  Límite {formatDate(task.fechaLimite)}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </Card>

                  <Card title="Próximas asesorías" hint="Acompañamiento" flush>
                    {data.proximasAsesorias.length === 0 ? (
                      <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                        No hay asesorías agendadas.{' '}
                        <Link to="/estudiante/asesorias/solicitar">Solicita una cita</Link>.
                      </p>
                    ) : (
                      <div>
                        {data.proximasAsesorias.map((advice, index) => (
                          <div className="aviso" key={`${advice.fecha}-${advice.titulo}-${index}`}>
                            <div style={{ flex: 1 }}>
                              <b>{advice.titulo}</b>
                              <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                                {formatDate(advice.fecha)}
                                {advice.hora ? ` · ${advice.hora}` : ''}
                                {advice.detalle ? ` · ${advice.detalle}` : ''}
                              </span>
                            </div>
                            <Badge tone="neutra" icon="chat">
                              {advice.tipo}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </Card>
                </div>

                <Card title="Eventos publicados" hint="Agenda institucional" flush className="mt-14">
                  {data.eventos.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay eventos publicados por ahora.
                    </p>
                  ) : (
                    <div>
                      {data.eventos.map((event) => (
                        <div className="aviso" key={event.id}>
                          <div style={{ flex: 1 }}>
                            <Link to={`/estudiante/eventos/${event.id}`}>
                              <b>{event.nombre}</b>
                            </Link>
                            <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                              {formatDate(event.fecha)}
                              {event.hora ? ` · ${event.hora}` : ''} · {event.lugar ?? 'Sin lugar'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </>
            )}
          </>
        )}
      </QueryGate>
    </>
  );
}
