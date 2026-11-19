import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { roleKeyOf, type Advice } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { EvidenceUploader } from '../../components/EvidenceUploader.tsx';
import { TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { ReasonModal } from '../../components/ReasonModal.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDate } from '../../lib/format.ts';
import {
  useAcceptAdvice,
  useAdvice,
  useRejectAdvice,
  useReproposeAdvice,
  useUpdateAdvice,
} from '../../queries/advice.ts';

interface AdviceDetailPageProps {
  basePath: string;
  roleLabel: string;
}

/**
 * Detalle de una asesoría.
 *
 * El estudiante solo lee y carga evidencias; el docente asignado y el
 * administrador confirman, reprograman, cancelan o cierran la sesión. La
 * reprogramación del estudiante no existe (P-1): él pide una cita nueva por la
 * bandeja de solicitudes.
 */
export function AdviceDetailPage({ basePath, roleLabel }: AdviceDetailPageProps) {
  const { id } = useParams();
  const adviceId = Number(id);
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const adviceQuery = useAdvice(Number.isFinite(adviceId) ? adviceId : null);
  const accept = useAcceptAdvice();
  const repropose = useReproposeAdvice();
  const reject = useRejectAdvice();
  const update = useUpdateAdvice(adviceId);

  const [fecha, setFecha] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFin, setHoraFin] = useState('');
  const [rejectOpen, setRejectOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;
  const isStudent = role === 'estudiante';
  const canManage = role === 'docente' || role === 'administrador';

  const schedule = (advice: Advice): Record<string, string> | null => {
    const blockFecha = fecha || advice.fecha || '';
    const blockInicio = horaInicio || advice.horaInicio || '';
    const blockFin = horaFin || advice.horaFin || '';
    if (!blockFecha || !blockInicio || !blockFin) {
      setError('Indica fecha, hora de inicio y hora de fin.');
      return null;
    }
    if (blockFin <= blockInicio) {
      setError('La hora de fin debe ser posterior a la de inicio.');
      return null;
    }
    setError(null);
    return { fecha: blockFecha, horaInicio: blockInicio, horaFin: blockFin };
  };

  return (
    <>
      <PageHeader
        title="Detalle de la asesoría"
        sub="Acompañamiento del docente al emprendimiento."
        crumbs={[
          { label: roleLabel },
          { label: 'Asesorías', to: basePath },
          { label: 'Detalle' },
        ]}
      />
      <QueryGate query={adviceQuery} loadingLabel="Cargando la asesoría…">
        {(advice: Advice) => (
          <div className="grid g-2-1">
            <div className="grid">
              <Card title={advice.tema} hint={`${advice.codigo} · ${advice.emprendimiento.nombre}`}>
                <div className="fila-acciones" style={{ gap: 8, marginBottom: 14 }}>
                  <Badge state={advice.estado}>{advice.estado}</Badge>
                  {advice.modalidad ? <Badge tone="linea">{advice.modalidad.nombre}</Badge> : null}
                </div>
                <DefinitionList
                  items={[
                    {
                      term: 'Horario',
                      value: advice.fecha
                        ? `${formatDate(`${advice.fecha}T12:00:00`)} · ${advice.horaInicio} a ${advice.horaFin}`
                        : 'Por agendar',
                    },
                    { term: 'Modalidad', value: advice.modalidad?.nombre ?? '—' },
                    {
                      term: 'Lugar o enlace',
                      value: advice.lugarEnlace ?? '—',
                    },
                    { term: 'Emprendimiento', value: `${advice.emprendimiento.codigo} · ${advice.emprendimiento.nombre}` },
                    { term: 'Estudiante', value: `${advice.estudiante.nombres} ${advice.estudiante.apellidos}` },
                    { term: 'Docente', value: advice.docente ? `${advice.docente.nombres} ${advice.docente.apellidos}` : 'Sin asignar' },
                    { term: 'Evidencias', value: `${advice.evidencias}` },
                  ]}
                />
                {advice.estado === 'Por agendar' ? (
                  <Callout icon="reloj">
                    La asesoría aún no tiene bloque. El administrador o el docente asignado
                    deben proponer fecha y confirmarla.
                  </Callout>
                ) : null}
              </Card>

              <Card title="Evidencias" hint="Solo se muestra el conteo">
                <EvidenceUploader
                  entity="advice"
                  entityId={advice.id}
                  count={advice.evidencias}
                  disabled={advice.estado === 'Completada' || advice.estado === 'Cancelada'}
                />
              </Card>
            </div>

            <div className="grid">
              {isStudent ? (
                <Card title="Reprogramar" hint="P-1">
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    El estudiante no mueve una asesoría ya agendada. Si necesitas otro
                    horario, crea una solicitud de cita desde Asesorías.
                  </p>
                  <Link className="btn btn-secundario" to={`${basePath}/solicitar`}>
                    Solicitar una asesoría
                  </Link>
                </Card>
              ) : null}

              {canManage ? (
                <Card title="Gestión de la sesión" hint="Docente asignado o admin">
                  {advice.estado === 'Por agendar' ||
                  advice.estado === 'Programada' ||
                  advice.estado === 'Confirmada' ? (
                    <>
                      <div className="grid g-3">
                        <TextField
                          label="Fecha"
                          type="date"
                          value={fecha || advice.fecha || ''}
                          onChange={(event) => setFecha(event.target.value)}
                        />
                        <TextField
                          label="Hora de inicio"
                          type="time"
                          value={horaInicio || advice.horaInicio || ''}
                          onChange={(event) => setHoraInicio(event.target.value)}
                        />
                        <TextField
                          label="Hora de fin"
                          type="time"
                          value={horaFin || advice.horaFin || ''}
                          onChange={(event) => setHoraFin(event.target.value)}
                        />
                      </div>
                      {error ? (
                        <div className="acceso-error" role="alert">
                          {error}
                        </div>
                      ) : null}
                      <div className="fila-acciones">
                        <Button
                          variant="primario"
                          icon="check"
                          loading={accept.isPending}
                          onClick={() => {
                            const block = schedule(advice);
                            if (!block) return;
                            accept.mutate(
                              { id: advice.id, block },
                              {
                                onSuccess: () => showToast('Asesoría confirmada.', 'ok'),
                                onError: (caught) => setError(errorMessage(caught)),
                              },
                            );
                          }}
                        >
                          Confirmar y notificar
                        </Button>
                        <Button
                          variant="secundario"
                          icon="calendar"
                          loading={repropose.isPending}
                          onClick={() => {
                            const block = schedule(advice);
                            if (!block) return;
                            repropose.mutate(
                              { id: advice.id, block },
                              {
                                onSuccess: () => showToast('Nueva fecha propuesta.', 'ok'),
                                onError: (caught) => setError(errorMessage(caught)),
                              },
                            );
                          }}
                        >
                          Proponer otra fecha
                        </Button>
                        <Button variant="secundario" icon="x" onClick={() => setRejectOpen(true)}>
                          Rechazar
                        </Button>
                      </div>
                    </>
                  ) : null}

                  {advice.estado === 'Confirmada' ? (
                    <div className="fila-acciones mt-14">
                      <Button
                        variant="secundario"
                        icon="play"
                        loading={update.isPending}
                        onClick={() =>
                          update.mutate(
                            { estado: 'En curso' },
                            {
                              onSuccess: () => showToast('Asesoría en curso.', 'ok'),
                              onError: (caught) => setError(errorMessage(caught)),
                            },
                          )
                        }
                      >
                        Marcar en curso
                      </Button>
                    </div>
                  ) : null}

                  {advice.estado === 'En curso' ? (
                    <div className="fila-acciones mt-14">
                      <Button
                        variant="primario"
                        icon="check"
                        loading={update.isPending}
                        onClick={() =>
                          update.mutate(
                            { estado: 'Completada' },
                            {
                              onSuccess: () => showToast('Asesoría completada.', 'ok'),
                              onError: (caught) => setError(errorMessage(caught)),
                            },
                          )
                        }
                      >
                        Completar asesoría
                      </Button>
                    </div>
                  ) : null}

                  {advice.estado === 'Completada' || advice.estado === 'Cancelada' ? (
                    <Callout icon="lock">
                      Esta asesoría está <b>{advice.estado.toLowerCase()}</b> y ya no admite
                      cambios de horario ni de estado.
                    </Callout>
                  ) : null}
                </Card>
              ) : null}
            </div>
          </div>
        )}
      </QueryGate>

      <ReasonModal
        open={rejectOpen}
        title="Cancelar la asesoría"
        label="Motivo de la cancelación"
        hint="El motivo se guarda en la auditoría y se envía al estudiante en el aviso; el diagrama no tiene una columna para mostrarlo después (P-29)."
        confirmLabel="Cancelar asesoría"
        loading={reject.isPending}
        onClose={() => setRejectOpen(false)}
        onSubmit={(motivo) =>
          reject.mutate(
            { id: adviceId, motivo },
            {
              onSuccess: () => {
                setRejectOpen(false);
                showToast('Asesoría cancelada.', 'ok');
              },
              onError: (caught) => setError(errorMessage(caught)),
            },
          )
        }
      />
    </>
  );
}
