import { Link } from 'react-router-dom';
import type { AdminDashboard, Entrepreneurship } from '../../api/types.ts';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { EmptyState, ErrorState, LoadingState } from '../../components/States.tsx';
import { useAdminDashboard } from '../../queries/dashboards.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';

/**
 * Tablero de seguimiento institucional.
 *
 * No hay un endpoint de avance por fase para todo el programa: la API solo lo
 * calcula por emprendimiento (`/task/advance/entrepreneurship/:id`). Esta vista
 * no inventa ese agregado; usa el avance que ya trae cada emprendimiento y el
 * histórico mensual del tablero del administrador.
 */
export function AdminTrackingDashboardPage() {
  const dashboard = useAdminDashboard();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });

  const items = [...(entrepreneurships.data?.items ?? [])].sort(
    (a, b) => a.avance - b.avance,
  );
  const promedio =
    items.length === 0
      ? 0
      : Math.round(items.reduce((total, item) => total + item.avance, 0) / items.length);
  const enRiesgo = items.filter((item) => item.avance < 50).length;
  const completados = items.filter((item) => item.avance === 100).length;

  return (
    <>
      <PageHeader
        title="Tablero de seguimiento"
        sub="Avance agregado de los emprendimientos y ritmo de registro de avances."
        crumbs={[
          { label: 'ADMINISTRADOR' },
          { label: 'Seguimiento', to: '/admin/seguimiento' },
          { label: 'Tablero' },
        ]}
        actions={
          <Link className="btn btn-secundario" to="/admin/seguimiento">
            Ver registros
          </Link>
        }
      />

      {entrepreneurships.isPending ? (
        <LoadingState label="Calculando el avance…" />
      ) : entrepreneurships.isError ? (
        <ErrorState error={entrepreneurships.error} />
      ) : items.length === 0 ? (
        <EmptyState
          title="Todavía no hay emprendimientos"
          text="Cuando existan emprendimientos con plan de trabajo, aquí se verá su avance agregado."
          action={
            <Link className="btn btn-primario" to="/admin/emprendimientos">
              Ir a emprendimientos
            </Link>
          }
        />
      ) : (
        <>
          <div className="grid g-4">
            <Metric icon="trend" label="Avance promedio" value={promedio} unit="%" progress={promedio} />
            <Metric icon="maleta" label="Emprendimientos" value={items.length} />
            <Metric icon="alerta" label="Bajo el 50%" value={enRiesgo} />
            <Metric icon="check" label="Al 100%" value={completados} />
          </div>

          <div className="grid g-2-1 mt-14">
            <Card title="Avance por emprendimiento" hint="De menor a mayor" flush>
              {items.map((item: Entrepreneurship) => (
                <Link
                  key={item.id}
                  className="aviso"
                  to={`/admin/emprendimientos/${item.id}/plan`}
                  style={{ textDecoration: 'none', display: 'block' }}
                >
                  <div style={{ flex: 1 }}>
                    <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                      <b>{item.nombre}</b>
                      <span className="nota-foot" style={{ margin: 0 }}>
                        {item.avance}%
                      </span>
                    </div>
                    <span className="nota-foot" style={{ display: 'block', marginBottom: 6 }}>
                      {item.codigo} · {item.estudiante.nombres} {item.estudiante.apellidos}
                    </span>
                    <ProgressBar value={item.avance} label={`Avance de ${item.nombre}`} />
                  </div>
                </Link>
              ))}
            </Card>

            <div className="grid">
              <Card title="Ritmo de avances" hint="Últimos seis meses">
                <QueryGate query={dashboard} loadingLabel="Cargando el histórico…">
                  {(data: AdminDashboard) =>
                    data.avancePorMes.length === 0 ? (
                      <p className="ayuda" style={{ margin: 0 }}>
                        Sin avances registrados en el periodo.
                      </p>
                    ) : (
                      <DefinitionList
                        items={data.avancePorMes.map((row) => ({
                          term: row.etiqueta || row.mes,
                          value: `${row.avances} avances · ${
                            row.promedio === null ? 'sin promedio' : `${row.promedio}%`
                          }`,
                        }))}
                      />
                    )
                  }
                </QueryGate>
              </Card>

              <Card title="Por sede" hint="Emprendimientos">
                <QueryGate query={dashboard} loadingLabel="Cargando las sedes…">
                  {(data: AdminDashboard) =>
                    data.porSede.length === 0 ? (
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
                    )
                  }
                </QueryGate>
              </Card>

              <Callout icon="bombilla">
                El avance se calcula con las tareas completadas de cada emprendimiento. La API
                no entrega un agregado por fase para todo el programa; abre el plan de un
                emprendimiento para ver el detalle por fase.
              </Callout>
            </div>
          </div>
        </>
      )}
    </>
  );
}
