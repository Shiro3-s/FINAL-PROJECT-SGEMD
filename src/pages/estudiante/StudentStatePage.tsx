import { Link } from 'react-router-dom';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { useStudentDashboard } from '../../queries/dashboards.ts';
import { useTaskAdvance } from '../../queries/tasks.ts';

/**
 * Estado de seguimiento del estudiante.
 *
 * Dos fuentes que no se mezclan: el tablero trae el resumen del diagnóstico y
 * del acta, y `GET /task/advance/entrepreneurship/:id` trae las cuatro fases del
 * plan con su porcentaje. No hay un endpoint de «estado de seguimiento»
 * separado, así que la vista compone esas dos lecturas.
 */
export function StudentStatePage() {
  const dashboard = useStudentDashboard();
  const entrepreneurshipId = dashboard.data?.emprendimiento?.id ?? null;
  const advance = useTaskAdvance(entrepreneurshipId);

  return (
    <>
      <PageHeader
        title="Estado de seguimiento"
        sub="Cómo va tu emprendimiento por fase, con el diagnóstico y el acta a la vista."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Estado de seguimiento' }]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/plan">
            Ver plan de trabajo
          </Link>
        }
      />

      <QueryGate query={dashboard} loadingLabel="Cargando tu estado…">
        {(data) => (
          <>
            {!data.emprendimiento ? (
              <Card title="Sin emprendimiento registrado">
                <Callout icon="bombilla">
                  El estado de seguimiento aparece cuando la coordinación registra tu
                  emprendimiento y te asigna un docente (D4).
                </Callout>
              </Card>
            ) : (
              <div className="grid g-2-1">
                <Card title="Avance por fase" hint="Tareas completadas">
                  <QueryGate query={advance} loadingLabel="Calculando el avance…">
                    {(progress) => (
                      <>
                        <p className="ayuda" style={{ marginTop: 0 }}>
                          <b>{progress.completadas}</b> de <b>{progress.total}</b> tareas
                          completadas · <b>{progress.avance}%</b> de avance total.
                        </p>
                        <ProgressBar value={progress.avance} label="Avance total del emprendimiento" />
                        {progress.fases.map((phase) => (
                          <div key={phase.faseId ?? 'sin-fase'} style={{ marginTop: 16 }}>
                            <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                              <b>{phase.fase ?? 'Tareas sin fase'}</b>
                              <span className="nota-foot" style={{ margin: 0 }}>
                                {phase.completadas}/{phase.total} · {phase.porcentaje}%
                              </span>
                            </div>
                            <ProgressBar
                              value={phase.porcentaje}
                              label={phase.fase ?? 'Tareas sin fase'}
                            />
                          </div>
                        ))}
                      </>
                    )}
                  </QueryGate>
                </Card>

                <div className="grid">
                  <Card title="Diagnóstico" hint="AQ-09">
                    <DefinitionList
                      items={[
                        {
                          term: 'Estado',
                          value: data.diagnostico?.estado ? (
                            <Badge state={data.diagnostico.estado}>{data.diagnostico.estado}</Badge>
                          ) : (
                            'Sin iniciar'
                          ),
                        },
                        {
                          term: 'Referencia',
                          value: data.diagnostico ? `Diagnóstico #${data.diagnostico.id}` : '—',
                        },
                        {
                          term: 'Puntaje',
                          value: 'No disponible: la rúbrica no está aprobada (AQ-09).',
                        },
                      ]}
                    />
                    <Link className="btn btn-secundario" to="/estudiante/diagnostico">
                      Abrir diagnóstico
                    </Link>
                  </Card>

                  <Card title="Acta de compromiso" hint="FR-003">
                    <DefinitionList
                      items={[
                        {
                          term: 'Estado',
                          value: data.acta?.estado ? (
                            <Badge state={data.acta.estado}>{data.acta.estado}</Badge>
                          ) : (
                            'Sin cargar'
                          ),
                        },
                        {
                          term: 'Referencia',
                          value: data.acta ? `Acta #${data.acta.id}` : '—',
                        },
                      ]}
                    />
                    <Link className="btn btn-secundario" to="/estudiante/acta">
                      Gestionar acta
                    </Link>
                  </Card>
                </div>
              </div>
            )}
          </>
        )}
      </QueryGate>
    </>
  );
}
