import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { isApiError } from '../../api/client.ts';
import type { Diagnosis, DiagnosisForm, DiagnosisQuestion } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList, Steps } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { ErrorState, LoadingState, errorMessage } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { useToast } from '../../components/Toast.tsx';
import { SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import {
  useDiagnosisForm,
  useMyDiagnosis,
  useSaveMyDiagnosis,
} from '../../queries/diagnosis.ts';

/**
 * Cuestionario de diagnóstico del estudiante.
 *
 * Las 22 preguntas y sus cinco secciones vienen de `GET /diagnosis/form`; el
 * borrador y el envío usan `POST /diagnosis/me`. No se calcula ni se muestra
 * puntaje: la rúbrica no está aprobada (AQ-09, P-35) y la API declara
 * `RUBRIC_NOT_CONFIGURED`.
 */
export function StudentDiagnosisPage() {
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const items = entrepreneurships.data?.items ?? [];
  const [chosen, setChosen] = useState('');
  const entrepreneurshipId = chosen ? Number(chosen) : items[0]?.id;

  if (entrepreneurships.isPending) {
    return <LoadingState label="Cargando tu diagnóstico…" />;
  }
  if (entrepreneurships.isError) {
    return <ErrorState error={entrepreneurships.error} />;
  }

  return (
    <>
      <PageHeader
        title="Diagnóstico inicial"
        sub="Responde el cuestionario para que tu docente pueda construir el plan de trabajo."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Diagnóstico' }]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/diagnostico/resultado">
            Ver resultado
          </Link>
        }
      />

      {items.length === 0 ? (
        <Card title="Todavía no hay un emprendimiento registrado">
          <Callout icon="bombilla">
            El diagnóstico se responde sobre un emprendimiento y el alta la hace la
            coordinación (D4). Cuando esté registrado, podrás diligenciarlo aquí.
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

          <DiagnosisWizard entrepreneurshipId={entrepreneurshipId ?? null} />
        </>
      )}
    </>
  );
}

function DiagnosisWizard({ entrepreneurshipId }: { entrepreneurshipId: number | null }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const form = useDiagnosisForm();
  const diagnosis = useMyDiagnosis(entrepreneurshipId ?? undefined);
  const save = useSaveMyDiagnosis();

  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [active, setActive] = useState('1');
  const [error, setError] = useState<string | null>(null);

  const saved: Diagnosis | undefined = diagnosis.data;
  const locked = saved !== undefined && saved.estado !== 'En progreso';
  const diagnosisProblem =
    diagnosis.isError &&
    !(isApiError(diagnosis.error) && diagnosis.error.status === 404)
      ? errorMessage(diagnosis.error)
      : null;

  useEffect(() => {
    setAnswers({});
    setError(null);
  }, [entrepreneurshipId]);

  useEffect(() => {
    if (!diagnosis.data) return;
    const next: Record<number, string> = {};
    for (const answer of diagnosis.data.respuestas) {
      if (answer.valor !== null) next[answer.id] = answer.valor;
    }
    setAnswers(next);
    setError(null);
  }, [diagnosis.data]);

  if (form.isPending) return <LoadingState label="Cargando el cuestionario…" />;
  if (form.isError) return <ErrorState error={form.error} />;

  const data: DiagnosisForm = form.data;
  const total = data.preguntas.length;
  const answered = data.preguntas.filter((question) => (answers[question.id] ?? '').trim() !== '').length;
  const missing = total - answered;

  const submit = (enviar: boolean) => {
    setError(null);
    if (!entrepreneurshipId) {
      setError('No hay un emprendimiento para asociar al diagnóstico.');
      return;
    }
    if (enviar) {
      const firstMissing = data.preguntas.find(
        (question) => (answers[question.id] ?? '').trim() === '',
      );
      if (firstMissing) {
        setActive(String(firstMissing.seccion));
        setError(
          `Faltan ${missing} respuestas. Completa la sección ${firstMissing.seccion} para enviar el diagnóstico.`,
        );
        return;
      }
    }
    const respuestas = data.preguntas
      .filter((question) => (answers[question.id] ?? '').trim() !== '')
      .map((question) => ({ preguntaId: question.id, valor: answers[question.id].trim() }));

    save.mutate(
      { emprendimientoId: entrepreneurshipId, respuestas, enviar },
      {
        onSuccess: (result) => {
          if (enviar) {
            showToast('Diagnóstico enviado.', 'ok');
            if (result.id) navigate('/estudiante/diagnostico/resultado');
          } else {
            showToast('Borrador guardado.', 'ok');
          }
        },
        onError: (caught) => {
          if (isApiError(caught) && caught.code === 'DIAGNOSIS_INCOMPLETE') {
            setError('Faltan respuestas obligatorias. Revisa cada sección y vuelve a enviar.');
            return;
          }
          setError(errorMessage(caught));
        },
      },
    );
  };

  const onAnswer = (questionId: number, value: string): void => {
    setAnswers((current) => ({ ...current, [questionId]: value }));
  };

  return (
    <div className="grid g-2-1">
      <div className="grid">
        <Card flush>
          <div style={{ padding: '18px 20px 0' }}>
            {diagnosisProblem ? (
              <Callout icon="alerta">{diagnosisProblem}</Callout>
            ) : null}
            <Steps
              items={data.secciones.map((section) => ({ label: section.titulo }))}
              current={Math.max(0, data.secciones.findIndex((section) => String(section.numero) === active))}
            />
            <div className="mt-14">
              <div className="fila-acciones" style={{ justifyContent: 'space-between' }}>
                <span className="ayuda" style={{ margin: 0 }}>
                  Progreso: {answered} de {total} respuestas
                </span>
                <span className="nota-foot" style={{ margin: 0 }}>
                  {saved ? `Estado: ${saved.estado}` : 'Sin borrador guardado'}
                </span>
              </div>
              <ProgressBar value={total === 0 ? 0 : (answered / total) * 100} label="Progreso del diagnóstico" />
            </div>
          </div>

          <div style={{ padding: '0 20px' }}>
            <Tabs
              label="Secciones del diagnóstico"
              active={active}
              onChange={setActive}
              items={data.secciones.map((section) => ({
                id: String(section.numero),
                label: section.titulo,
              }))}
            />
          </div>

          {data.secciones.map((section) => (
            <TabPanel key={section.numero} id={String(section.numero)} active={active}>
              <div style={{ padding: '14px 20px 20px' }}>
                <h3 style={{ marginTop: 0 }}>
                  Sección {section.numero} de {data.secciones.length} · {section.titulo}
                </h3>
                {data.preguntas
                  .filter((question) => question.seccion === section.numero)
                  .sort((a, b) => a.orden - b.orden)
                  .map((question) => (
                    <QuestionField
                      key={question.id}
                      question={question}
                      value={answers[question.id] ?? ''}
                      disabled={locked || save.isPending}
                      onChange={(value) => onAnswer(question.id, value)}
                    />
                  ))}
              </div>
            </TabPanel>
          ))}

          <div style={{ padding: '0 20px 20px' }}>
            {error ? (
              <div className="acceso-error" role="alert">
                {error}
              </div>
            ) : null}
            <div className="form-acciones">
              <Button
                variant="secundario"
                icon="doc"
                loading={save.isPending && !locked}
                disabled={locked || save.isPending}
                onClick={() => submit(false)}
              >
                Guardar borrador
              </Button>
              <Button
                type="button"
                variant="acento"
                icon="enviar"
                loading={save.isPending}
                disabled={locked || save.isPending}
                onClick={() => submit(true)}
              >
                Enviar diagnóstico
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid">
        <Card title="Cómo va el cuestionario" hint="5 secciones">
          <DefinitionList
            items={data.secciones.map((section) => {
              const propias = data.preguntas.filter((question) => question.seccion === section.numero);
              const listas = propias.filter((question) => (answers[question.id] ?? '').trim() !== '');
              return {
                term: section.titulo,
                value: `${listas.length}/${propias.length}`,
              };
            })}
          />
        </Card>

        <Card title="Puedes pausar cuando quieras">
          <p className="ayuda" style={{ marginTop: 0 }}>
            Tus respuestas se guardan como <b>borrador</b>. Solo se envían al docente cuando
            completas las cinco secciones y pulsas <b>Enviar diagnóstico</b>.
          </p>
          {locked ? (
            <Callout icon="check">
              El diagnóstico ya fue enviado y sus respuestas están bloqueadas. Consulta el{' '}
              <Link to="/estudiante/diagnostico/resultado">resultado</Link>.
            </Callout>
          ) : (
            <Callout icon="alerta">
              La rúbrica del diagnóstico no está aprobada (AQ-09): se guardan las respuestas,
              pero no se produce puntaje. No verás una calificación que la API no calcula.
            </Callout>
          )}
        </Card>
      </div>
    </div>
  );
}

function QuestionField({
  question,
  value,
  disabled,
  onChange,
}: {
  question: DiagnosisQuestion;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  if (question.tipo === 'Selección única') {
    return (
      <SelectField
        label={question.enunciado}
        required
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Selecciona una opción"
      >
        {question.opciones.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </SelectField>
    );
  }
  if (question.tipo === 'Texto largo') {
    return (
      <TextAreaField
        label={question.enunciado}
        required
        rows={3}
        maxLength={2000}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }
  return (
    <TextField
      label={question.enunciado}
      required
      maxLength={500}
      value={value}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
