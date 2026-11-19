import { Link, useParams } from 'react-router-dom';
import type { Diagnosis } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useDiagnosis, useDiagnosisReport } from '../../queries/diagnosis.ts';

interface DiagnosisDetailPageProps {
  roleLabel: string;
  basePath: string;
}

/**
 * Detalle del diagnóstico (docente y administrador).
 *
 * AQ-09 sigue abierta: no hay rúbrica, así que `puntajeTotal` es `null` y el
 * informe declara `RUBRIC_NOT_CONFIGURED`. No se calcula ni se muestra un
 * puntaje inventado (P-35). La descarga del PDF tampoco existe (P-3): el
 * informe se sirve como JSON y esta vista lo pinta por secciones.
 */
export function DiagnosisDetailPage({ roleLabel, basePath }: DiagnosisDetailPageProps) {
  const { id } = useParams();
  const diagnosisId = Number(id);
  const diagnosis = useDiagnosis(Number.isFinite(diagnosisId) ? diagnosisId : null);
  const report = useDiagnosisReport(Number.isFinite(diagnosisId) ? diagnosisId : null);

  const sectionTitle = (number: number): string =>
    report.data?.informe.secciones.find((section) => section.numero === number)?.titulo ??
    `Sección ${number}`;

  return (
    <>
      <PageHeader
        title="Detalle del diagnóstico"
        sub="Caracterización del emprendimiento, sin puntaje mientras AQ-09 esté abierta."
        crumbs={[
          { label: roleLabel },
          { label: 'Diagnósticos', to: basePath },
          { label: 'Detalle' },
        ]}
      />

      <QueryGate query={diagnosis} loadingLabel="Cargando el diagnóstico…">
        {(item: Diagnosis) => (
          <div className="grid g-2-1">
            <Card title={`Diagnóstico ${item.emprendimiento.codigo}`} hint={formatDateTime(item.fechaDiagnostico)}>
              <div className="fila-acciones" style={{ gap: 8, marginBottom: 14 }}>
                <Badge state={item.estado}>{item.estado}</Badge>
              </div>
              <DefinitionList
                items={[
                  { term: 'Emprendimiento', value: `${item.emprendimiento.codigo} · ${item.emprendimiento.nombre}` },
                  { term: 'Estudiante', value: `${item.estudiante.nombres} ${item.estudiante.apellidos}` },
                  { term: 'Respondidas', value: `${item.respondidas} de ${item.totalPreguntas}` },
                  {
                    term: 'Puntaje total',
                    value: item.puntajeTotal === null ? 'Sin puntaje (AQ-09)' : `${item.puntajeTotal}`,
                  },
                  { term: 'Informe', value: item.urlInforme ?? 'El PDF no se genera todavía (P-3)' },
                ]}
              />
              {!item.puntuacion.disponible ? (
                <Callout icon="alerta">
                  <b>Sin rúbrica aprobada.</b> {item.puntuacion.mensaje}
                </Callout>
              ) : null}
            </Card>

            <Card title="Resumen del informe" hint="JSON, sin PDF">
              {report.isPending ? <p className="ayuda">Cargando el informe…</p> : null}
              {report.isError ? (
                <p className="ayuda">No fue posible cargar el informe del diagnóstico.</p>
              ) : null}
              {report.data ? (
                <>
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    {report.data.informe.mensaje}
                  </p>
                  <DefinitionList
                    items={report.data.informe.secciones.map((section) => ({
                      term: section.titulo,
                      value:
                        section.puntaje === null
                          ? 'Sin puntaje'
                          : `${section.puntaje} · ${section.resultado ?? 'Sin banda'}`,
                    }))}
                  />
                </>
              ) : null}
            </Card>
          </div>
        )}
      </QueryGate>

      {diagnosis.data ? (
        <Card title="Respuestas" hint={`${diagnosis.data.respondidas} de ${diagnosis.data.totalPreguntas}`} flush>
          {diagnosis.data.respuestas.length === 0 ? (
            <p className="ayuda" style={{ padding: 20, margin: 0 }}>
              El diagnóstico no tiene respuestas guardadas todavía.
            </p>
          ) : (
            <div>
              {diagnosis.data.respuestas.map((answer) => (
                <div className="aviso" key={answer.id}>
                  <div style={{ flex: 1 }}>
                    <span className="nota-foot" style={{ display: 'block', marginBottom: 4 }}>
                      {sectionTitle(answer.seccion)} · Pregunta {answer.orden}
                    </span>
                    <p style={{ margin: '0 0 4px' }}>
                      <b>{answer.enunciado}</b>
                    </p>
                    <p className="ayuda" style={{ margin: 0 }}>
                      {answer.valor ?? 'Sin responder'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      ) : null}

      <div className="fila-acciones mt-14">
        <Link className="btn btn-secundario" to={basePath}>
          Volver al listado
        </Link>
      </div>
    </>
  );
}
