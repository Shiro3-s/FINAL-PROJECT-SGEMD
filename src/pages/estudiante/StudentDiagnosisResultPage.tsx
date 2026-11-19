import { useState } from 'react';
import { Link } from 'react-router-dom';
import { isApiError } from '../../api/client.ts';
import type { Characterization, Diagnosis } from '../../api/types.ts';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { EmptyState, ErrorState, LoadingState } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useMyCharacterization, useMyDiagnosis } from '../../queries/diagnosis.ts';

/**
 * Resultado del diagnóstico propio.
 *
 * La API no produce puntaje ni PDF mientras la rúbrica no esté aprobada
 * (AQ-09/P-35 y P-3): la vista no dibuja barras ni calificaciones inventadas;
 * muestra el estado, el avance por sección y las respuestas guardadas, que es lo
 * que el servidor sí devuelve.
 */
export function StudentDiagnosisResultPage() {
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const items = entrepreneurships.data?.items ?? [];
  const [chosen, setChosen] = useState('');
  const entrepreneurshipId = chosen ? Number(chosen) : items[0]?.id;

  if (entrepreneurships.isPending) {
    return <LoadingState label="Cargando el resultado…" />;
  }
  if (entrepreneurships.isError) {
    return <ErrorState error={entrepreneurships.error} />;
  }

  return (
    <>
      <PageHeader
        title="Resultado del diagnóstico"
        sub="Estado del envío, avance por sección y respuestas registradas."
        crumbs={[
          { label: 'ESTUDIANTE' },
          { label: 'Diagnóstico', to: '/estudiante/diagnostico' },
          { label: 'Resultado' },
        ]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/diagnostico">
            Ir al cuestionario
          </Link>
        }
      />

      {items.length === 0 ? (
        <Card title="Todavía no hay un emprendimiento registrado">
          <Callout icon="bombilla">
            El diagnóstico se responde sobre un emprendimiento y el alta la hace la
            coordinación (D4).
          </Callout>
          <Link className="btn btn-primario" to="/estudiante/emprendimientos">
            Mi emprendimiento
          </Link>
        </Card>
      ) : (
        <>
          {items.length > 1 ? (
            <Card flush className="mb-14">
              <Toolbar>
                <SelectFilter
                  label="Emprendimiento"
                  value={chosen}
                  onChange={setChosen}
                  allLabel={`${items[0]?.codigo ?? ''} — ${items[0]?.nombre ?? ''} (el más reciente)`}
                >
                  {items.slice(1).map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.codigo} — {item.nombre}
                    </option>
                  ))}
                </SelectFilter>
              </Toolbar>
            </Card>
          ) : null}

          <ResultBody entrepreneurshipId={entrepreneurshipId ?? null} />
        </>
      )}
    </>
  );
}

function ResultBody({ entrepreneurshipId }: { entrepreneurshipId: number | null }) {
  const diagnosis = useMyDiagnosis(entrepreneurshipId ?? undefined);
  const characterization = useMyCharacterization(entrepreneurshipId ?? undefined);
  const [active, setActive] = useState('1');

  if (diagnosis.isPending) return <LoadingState label="Cargando el diagnóstico…" />;

  if (diagnosis.isError) {
    if (isApiError(diagnosis.error) && diagnosis.error.status === 404) {
      return (
        <EmptyState
          icon="clipboard"
          title="Todavía no has respondido el diagnóstico"
          text="Cuando guardes el cuestionario, aquí verás el estado del envío y tus respuestas."
          action={
            <Link className="btn btn-primario" to="/estudiante/diagnostico">
              Responder diagnóstico
            </Link>
          }
        />
      );
    }
    return <ErrorState error={diagnosis.error} />;
  }

  const data: Diagnosis = diagnosis.data;
  const sections = characterization.data?.secciones ?? [];
  const respondidas = data.respondidas;
  const total = data.totalPreguntas;
  const tabSections =
    sections.length > 0
      ? sections.map((section) => ({ numero: section.numero, titulo: section.titulo }))
      : [...new Set(data.respuestas.map((answer) => answer.seccion))].map((numero) => ({
          numero,
          titulo: `Sección ${numero}`,
        }));

  return (
    <>
      <div className="grid g-4">
        <Metric icon="enviar" label="Estado del envío" value={data.estado} />
        <Metric icon="check" label="Respuestas" value={`${respondidas}/${total}`} />
        <Metric
          icon="layers"
          label="Secciones completas"
          value={`${sections.filter((section) => section.respondidas === section.total && section.total > 0).length}/${sections.length || tabSections.length}`}
        />
        <Metric icon="medalla" label="Puntaje" value="No disponible" />
      </div>

      <div className="grid g-2-1 mt-14">
        <Card title="Avance por sección" hint="Respuestas registradas">
          {sections.length === 0 ? (
            <p className="ayuda" style={{ marginTop: 0 }}>
              La API aún no devuelve el detalle por sección.
            </p>
          ) : (
            sections.map((section: Characterization['secciones'][number]) => (
              <div key={section.numero} style={{ marginBottom: 14 }}>
                <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                  <b>{section.titulo}</b>
                  <span className="nota-foot" style={{ margin: 0 }}>
                    {section.respondidas}/{section.total}
                  </span>
                </div>
                <ProgressBar
                  value={section.total === 0 ? 0 : (section.respondidas / section.total) * 100}
                  label={`Avance de ${section.titulo}`}
                />
              </div>
            ))
          )}
          <p className="nota-foot" style={{ marginBottom: 0 }}>
            Guardado {formatDateTime(data.fechaDiagnostico)} · Emprendimiento{' '}
            {data.emprendimiento.codigo}
          </p>
        </Card>

        <Card title="Sin puntaje todavía" hint="AQ-09">
          <Callout icon="alerta">
            {characterization.data?.puntuacion.mensaje ?? data.puntuacion.mensaje}
          </Callout>
          <p className="ayuda">
            No hay PDF de diagnóstico (P-3): la API no genera el informe mientras no exista
            rúbrica. Esta pantalla muestra lo que sí está calculado.
          </p>
          <div className="fila-acciones">
            <button className="btn btn-secundario" type="button" disabled>
              Descargar PDF
            </button>
            {data.estado === 'En progreso' ? (
              <Link className="btn btn-primario" to="/estudiante/diagnostico">
                Continuar cuestionario
              </Link>
            ) : null}
          </div>
        </Card>
      </div>

      <div className="mt-14">
        <Tabs
          label="Respuestas por sección"
          active={active}
          onChange={setActive}
          items={tabSections.map((section) => ({
            id: String(section.numero),
            label: section.titulo,
          }))}
        />
        {tabSections.map((section) => (
          <TabPanel key={section.numero} id={String(section.numero)} active={active}>
            <Card title={section.titulo} hint="Tus respuestas">
              {data.respuestas.filter((answer) => answer.seccion === section.numero).length === 0 ? (
                <p className="ayuda" style={{ margin: 0 }}>
                  Esta sección no tiene respuestas guardadas.
                </p>
              ) : (
                <DefinitionList
                  items={data.respuestas
                    .filter((answer) => answer.seccion === section.numero)
                    .map((answer) => ({
                      term: answer.enunciado,
                      value: answer.valor ?? 'Sin responder',
                    }))}
                />
              )}
            </Card>
          </TabPanel>
        ))}
        {tabSections.length === 0 ? (
          <Card title="Respuestas">
            {data.respuestas.length === 0 ? (
              <p className="ayuda" style={{ margin: 0 }}>
                No hay respuestas guardadas.
              </p>
            ) : (
              <DefinitionList
                items={data.respuestas.map((answer) => ({
                  term: answer.enunciado,
                  value: answer.valor ?? 'Sin responder',
                }))}
              />
            )}
          </Card>
        ) : null}
      </div>

      <p className="nota-foot">
        {data.puntuacion.disponible
          ? `Puntaje informado por la API: ${data.puntajeTotal ?? '—'}`
          : `La API reporta ${data.puntuacion.motivo}.`}
      </p>
    </>
  );
}
