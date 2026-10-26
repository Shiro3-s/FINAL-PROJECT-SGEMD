import { Link } from 'react-router-dom';
import type { AgendaItem, TeacherDashboard } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import { useTeacherDashboard } from '../../queries/dashboards.ts';

/**
 * Inicio del docente.
 *
 * Una sola consulta agregada (`GET /dashboard/teacher`) alimenta las métricas,
 * el avance por emprendimiento, la agenda y la actividad reciente. El alcance
 * son las asignaciones activas: un docente sin asignaciones recibe ceros, no el
 * panorama de otro.
 */
export function TeacherDashboardPage() {
  const dashboard = useTeacherDashboard();

  return (
    <>
      <PageHeader
        title="Inicio"
        sub="Panorama de tus emprendimientos asignados y tu carga de trabajo."
        crumbs={[{ label: 'DOCENTE' }, { label: 'Inicio' }]}
        actions={
          <Link className="btn btn-primario" to="/docente/asesorias/nueva">
            Generar asesoría
          </Link>
        }
      />

      <QueryGate query={dashboard} loadingLabel="Cargando tu tablero…">
        {(data: TeacherDashboard) => (
          <>
            <div className="grid g-4">
              <Metric
                icon="maleta"
                label="Emprendimientos asignados"
                value={data.emprendimientos}
                to="/docente/emprendimientos"
              />
              <Metric
                icon="chat"
                label="Asesorías agendadas"
                value={data.asesorias.agendadas}
                to="/docente/asesorias"
              />
              <Metric
                icon="checklist"
                label="Tareas por revisar"
                value={data.tareasPorRevisar}
                to="/docente/tareas?f=En revisión"
              />
              <Metric
                icon="trend"
                label="Avances registrados"
                value={data.avancesRegistrados}
                to="/docente/avances"
              />
            </div>

            <div className="grid g-2-1 mt-14">
              <div className="grid">
                <Card title="Avance por emprendimiento" hint="Tus asignaciones activas">
                  {data.avancePorEmprendimiento.length === 0 ? (
                    <p className="ayuda" style={{ marginTop: 0 }}>
                      Todavía no tienes emprendimientos asignados. La asignación la hace el
                      administrador.
                    </p>
                  ) : (
                    data.avancePorEmprendimiento.map((item) => (
                      <div key={item.id} style={{ marginBottom: 14 }}>
                        <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                          <Link to={`/docente/emprendimientos/${item.id}`}>
                            <b>{item.nombre}</b>
                          </Link>
                          <span className="nota-foot" style={{ margin: 0 }}>
                            {item.codigo} · {item.avance}%
                          </span>
                        </div>
                        <p className="ayuda" style={{ margin: '2px 0 6px' }}>
                          {item.estudiante}
                        </p>
                        <ProgressBar value={item.avance} label={`Avance de ${item.nombre}`} />
                      </div>
                    ))
                  )}
                </Card>

                <Card title="Agenda" hint="Asesorías y eventos próximos" flush>
                  {data.agenda.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay compromisos próximos en tu agenda.
                    </p>
                  ) : (
                    data.agenda.map((item: AgendaItem, index) => (
                      <div className="aviso" key={`${item.tipo}-${item.fecha}-${index}`}>
                        <div style={{ flex: 1 }}>
                          <div className="fila-acciones" style={{ gap: 8, marginBottom: 4 }}>
                            <Badge tone="linea" icon="calendar">
                              {item.tipo}
                            </Badge>
                            <span className="nota-foot" style={{ margin: 0 }}>
                              {formatDate(`${item.fecha}T12:00:00`)}
                              {item.hora ? ` · ${item.hora}` : ''}
                            </span>
                          </div>
                          <b>{item.titulo}</b>
                          <p className="ayuda" style={{ margin: '4px 0 0' }}>
                            {item.detalle}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </Card>

                <Card title="Actividad reciente" hint="Últimos movimientos" flush>
                  {data.actividadReciente.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      Sin actividad registrada todavía.
                    </p>
                  ) : (
                    data.actividadReciente.map((item) => (
                      <div className="aviso" key={item.id}>
                        <div style={{ flex: 1 }}>
                          <b>{item.accion}</b>
                          <p className="ayuda" style={{ margin: '4px 0 0' }}>
                            {item.detalle ?? item.entidad} · {formatDateTime(item.fecha)}
                          </p>
                        </div>
                        <span className="nota-foot" style={{ margin: 0 }}>
                          {item.actor ?? 'Sistema'}
                        </span>
                      </div>
                    ))
                  )}
                </Card>
              </div>

              <div className="grid">
                <Card title="Acciones rápidas">
                  <div className="grid">
                    <Link className="btn btn-primario" to="/docente/avances/nuevo">
                      Registrar avance
                    </Link>
                    <Link className="btn btn-secundario" to="/docente/tareas?f=En revisión">
                      Calificar tareas
                    </Link>
                    <Link className="btn btn-secundario" to="/docente/diagnosticos">
                      Revisar diagnóstico
                    </Link>
                    <Link className="btn btn-secundario" to="/docente/asesorias/nueva">
                      Generar asesoría
                    </Link>
                  </div>
                </Card>

                <Card title="Carga de asesorías" hint="Estado actual">
                  <DefinitionList
                    items={[
                      { term: 'Agendadas', value: String(data.asesorias.agendadas) },
                      { term: 'Por agendar', value: String(data.asesorias.porAgendar) },
                      { term: 'Completadas', value: String(data.asesorias.completadas) },
                      { term: 'Tareas de prioridad alta', value: String(data.tareasAltaPrioridad) },
                      {
                        term: 'Avances con evidencia',
                        value: `${data.avancesConEvidencia} de ${data.avancesRegistrados}`,
                      },
                    ]}
                  />
                  <p className="ayuda">
                    Avance promedio de tu cartera: <b>{data.avancePromedio}%</b>.
                  </p>
                </Card>

                {data.emprendimientos === 0 ? (
                  <Card title="Sin asignaciones">
                    <Callout icon="bombilla">
                      Cuando el administrador te asigne un emprendimiento con acta aprobada,
                      aparecerá aquí y podrás registrar avances, tareas y asesorías.
                    </Callout>
                  </Card>
                ) : null}
              </div>
            </div>
          </>
        )}
      </QueryGate>
    </>
  );
}
