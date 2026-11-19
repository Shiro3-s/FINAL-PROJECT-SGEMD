import { Link } from 'react-router-dom';
import type { AdminDashboard, AgendaItem } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import { useAdminDashboard } from '../../queries/dashboards.ts';

/**
 * Inicio del administrador.
 *
 * `GET /dashboard/admin` entrega todos los agregados en una sola consulta:
 * usuarios, emprendimientos, tareas, avance promedio, alertas, distribución por
 * sede y sector, agenda y actividad reciente. Las tarjetas de alerta enlazan al
 * listado con el filtro aplicado en el servidor.
 *
 * Las gráficas del prototipo se sustituyen por barras de progreso y listas
 * ordenadas: los mismos datos, sin biblioteca de charts ni colores fuera de la
 * paleta.
 */
export function AdminDashboardPage() {
  const dashboard = useAdminDashboard();

  return (
    <>
      <PageHeader
        title="Inicio"
        sub="Panorama del programa: usuarios, emprendimientos, tareas y alertas."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Inicio' }]}
        actions={
          <Link className="btn btn-primario" to="/admin/usuarios">
            Gestionar usuarios
          </Link>
        }
      />

      <QueryGate query={dashboard} loadingLabel="Cargando el tablero…">
        {(data: AdminDashboard) => (
          <>
            <div className="grid g-4">
              <Metric
                icon="users"
                label="Usuarios activos"
                value={data.usuariosActivos}
                to="/admin/usuarios"
              />
              <Metric
                icon="maleta"
                label="Emprendimientos"
                value={data.emprendimientos}
                to="/admin/emprendimientos"
              />
              <Metric icon="checklist" label="Tareas" value={data.tareas} to="/admin/tareas" />
              <Metric
                icon="check"
                label="Avance promedio"
                value={data.avancePromedio}
                unit="%"
                progress={data.avancePromedio}
              />
            </div>

            <div className="grid g-2-1 mt-14">
              <div className="grid">
                <Card title="Alertas" hint="Requieren revisión">
                  <div className="grid g-2">
                    <AlertLine
                      label="Solicitudes pendientes"
                      value={data.solicitudesPendientes}
                      to="/admin/solicitudes"
                    />
                    <AlertLine
                      label="Emprendimientos sin docente"
                      value={data.alertas.sinDocente}
                      to="/admin/asignaciones"
                    />
                    <AlertLine
                      label="Diagnósticos sin revisar"
                      value={data.alertas.diagnosticosSinRevisar}
                      to="/admin/diagnosticos"
                    />
                    <AlertLine
                      label="Tareas vencidas"
                      value={data.alertas.tareasVencidas}
                      to="/admin/tareas?f=Vencida"
                    />
                    <AlertLine
                      label="Eventos pendientes"
                      value={data.alertas.eventosPendientes}
                      to="/admin/eventos"
                    />
                    <AlertLine
                      label="Actas en revisión"
                      value={data.alertas.actasEnRevision}
                      to="/admin/actas"
                    />
                  </div>
                </Card>

                <Card title="Avance por mes" hint="Últimos seis meses">
                  {data.avancePorMes.length === 0 ? (
                    <p className="ayuda" style={{ margin: 0 }}>
                      Sin avances registrados en el periodo.
                    </p>
                  ) : (
                    data.avancePorMes.map((row) => (
                      <div key={row.mes} style={{ marginBottom: 12 }}>
                        <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                          <b>{row.etiqueta || row.mes}</b>
                          <span className="nota-foot" style={{ margin: 0 }}>
                            {row.avances} avances ·{' '}
                            {row.promedio === null ? 'sin promedio' : `${row.promedio}%`}
                          </span>
                        </div>
                        {row.promedio === null ? null : (
                          <ProgressBar
                            value={row.promedio}
                            label={`Promedio de ${row.etiqueta || row.mes}`}
                          />
                        )}
                      </div>
                    ))
                  )}
                </Card>

                <Card title="Agenda" hint="Próximos compromisos" flush>
                  {data.agenda.length === 0 ? (
                    <p className="ayuda" style={{ padding: 20, margin: 0 }}>
                      No hay compromisos próximos.
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

                <Card title="Actividad reciente" hint="Auditoría" flush>
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
                <Card title="Por sede" hint="Emprendimientos">
                  {data.porSede.length === 0 ? (
                    <p className="ayuda" style={{ margin: 0 }}>
                      Sin datos por sede.
                    </p>
                  ) : (
                    <DefinitionList
                      items={data.porSede.map((row) => ({
                        term: row.nombre,
                        value: String(row.total),
                      }))}
                    />
                  )}
                </Card>

                <Card title="Por sector" hint="Emprendimientos">
                  {data.porSector.length === 0 ? (
                    <p className="ayuda" style={{ margin: 0 }}>
                      Sin datos por sector.
                    </p>
                  ) : (
                    <DefinitionList
                      items={data.porSector.map((row) => ({
                        term: row.nombre,
                        value: String(row.total),
                      }))}
                    />
                  )}
                </Card>

                <Card title="Acciones rápidas">
                  <div className="grid">
                    <Link className="btn btn-primario" to="/admin/solicitudes">
                      Resolver solicitudes
                    </Link>
                    <Link className="btn btn-secundario" to="/admin/asignaciones">
                      Asignar docente
                    </Link>
                    <Link className="btn btn-secundario" to="/admin/reportes">
                      Generar reporte
                    </Link>
                    <Link className="btn btn-secundario" to="/admin/respaldos">
                      Crear respaldo
                    </Link>
                  </div>
                </Card>

                <Callout icon="bombilla">
                  El respaldo y la exportación de la base viven en{' '}
                  <Link to="/admin/respaldos">Respaldos</Link>; la restauración no forma parte
                  del MVP y no se ofrece como botón.
                </Callout>
              </div>
            </div>
          </>
        )}
      </QueryGate>
    </>
  );
}

function AlertLine({ label, value, to }: { label: string; value: number; to: string }) {
  return (
    <Link
      className="aviso"
      to={to}
      style={{ textDecoration: 'none', justifyContent: 'space-between' }}
    >
      <span>{label}</span>
      <b>{value}</b>
    </Link>
  );
}
