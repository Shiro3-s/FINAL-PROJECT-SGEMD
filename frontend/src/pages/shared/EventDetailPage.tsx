import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { roleKeyOf, type EventItem } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField } from '../../components/FormField.tsx';
import { Modal } from '../../components/Modal.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import {
  useDeleteEvent,
  useEvent,
  useEventRecommendations,
  useRecommendEvent,
  useRegisterEvent,
  useUnregisterEvent,
  useUpdateEvent,
} from '../../queries/events.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';

interface EventDetailPageProps {
  roleLabel: string;
  basePath: string;
}

/**
 * Detalle de un evento.
 *
 * Tres conductas distintas sobre el mismo registro: el estudiante se inscribe
 * (solo si `requiereRegistro` y hay cupo), el docente recomienda el evento a un
 * emprendimiento asignado y el administrador lo edita, publica o da de baja.
 * Las recomendaciones no tienen transición de estado (P-40).
 */
export function EventDetailPage({ roleLabel, basePath }: EventDetailPageProps) {
  const { id } = useParams();
  const eventId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const eventQuery = useEvent(Number.isFinite(eventId) ? eventId : null);
  const recommendations = useEventRecommendations(
    role === 'administrador' || role === 'docente' || role === 'estudiante'
      ? Number.isFinite(eventId)
        ? eventId
        : null
      : null,
  );
  const register = useRegisterEvent();
  const unregister = useUnregisterEvent();
  const update = useUpdateEvent(eventId);
  const remove = useDeleteEvent();
  const recommend = useRecommendEvent();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const [recommendOpen, setRecommendOpen] = useState(false);
  const [recommendTarget, setRecommendTarget] = useState('');
  const [recommendMessage, setRecommendMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;
  const isStudent = role === 'estudiante';
  const isTeacher = role === 'docente';
  const isAdmin = role === 'administrador';

  return (
    <>
      <PageHeader
        title="Detalle del evento"
        sub="Agenda institucional y recomendaciones del programa."
        crumbs={[
          { label: roleLabel },
          { label: 'Eventos', to: basePath },
          { label: 'Detalle' },
        ]}
        actions={
          isAdmin ? (
            <>
              <Link className="btn btn-secundario" to={`${basePath}/${eventId}/editar`}>
                Editar
              </Link>
              <Button
                variant="primario"
                loading={update.isPending}
                onClick={() =>
                  eventQuery.data?.estado === 'Publicado'
                    ? update.mutate(
                        { estado: 'Pendiente' },
                        {
                          onSuccess: () => showToast('Evento devuelto a borrador.', 'ok'),
                          onError: (caught) => showToast(errorMessage(caught), 'error'),
                        },
                      )
                    : update.mutate(
                        { estado: 'Publicado' },
                        {
                          onSuccess: () => showToast('Evento publicado.', 'ok'),
                          onError: (caught) => showToast(errorMessage(caught), 'error'),
                        },
                      )
                }
              >
                {eventQuery.data?.estado === 'Publicado' ? 'Despublicar' : 'Publicar'}
              </Button>
            </>
          ) : undefined
        }
      />

      <QueryGate query={eventQuery} loadingLabel="Cargando el evento…">
        {(event: EventItem) => (
          <div className="grid g-2-1">
            <div className="grid">
              <Card title={event.nombreEvento} hint={event.tipoEvento?.nombre ?? 'Evento'}>
                <div className="fila-acciones" style={{ gap: 8, marginBottom: 14 }}>
                  <Badge state={event.estado}>{event.estado}</Badge>
                  {event.modalidad ? <Badge tone="linea">{event.modalidad.nombre}</Badge> : null}
                  {event.inscrito ? <Badge state="Confirmada">Inscrito</Badge> : null}
                </div>
                <DefinitionList
                  items={[
                    { term: 'Descripción', value: event.descripcion ?? 'Sin descripción.' },
                    { term: 'Dirigido a', value: event.dirigidoA ?? 'Sin audiencia definida' },
                    {
                      term: 'Fecha y hora',
                      value: event.fecha
                        ? `${formatDate(`${event.fecha}T12:00:00`)} · ${event.horaInicio} a ${event.horaFin}`
                        : 'Por definir',
                    },
                    { term: 'Lugar', value: event.lugar ?? '—' },
                    {
                      term: 'Enlace',
                      value: event.enlace ? (
                        <a href={event.enlace} target="_blank" rel="noreferrer">
                          {event.enlace}
                        </a>
                      ) : (
                        '—'
                      ),
                    },
                    {
                      term: 'Cupo',
                      value:
                        event.cupo === null
                          ? 'Sin tope de inscripciones'
                          : `${event.cupo} disponibles de ${event.capacidadMaxima ?? '—'}`,
                    },
                    { term: 'Inscritos', value: String(event.inscritos) },
                    {
                      term: 'Organizador',
                      value: `${event.organizador.nombres} ${event.organizador.apellidos}`,
                    },
                  ]}
                />
                {event.estado === 'Pendiente' ? (
                  <Callout icon="reloj">
                    Este evento es un <b>borrador</b>: solo el administrador lo ve. Los demás
                    roles reciben <code>404</code> hasta que se publique.
                  </Callout>
                ) : null}
              </Card>

              <Card title="Recomendaciones" hint="P-40: sin transiciones">
                {recommendations.isPending ? (
                  <p className="ayuda">Cargando recomendaciones…</p>
                ) : null}
                {recommendations.isError ? (
                  <p className="ayuda">{errorMessage(recommendations.error)}</p>
                ) : null}
                {recommendations.data && recommendations.data.items.length === 0 ? (
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    Todavía no hay recomendaciones para este evento.
                  </p>
                ) : null}
                {recommendations.data && recommendations.data.items.length > 0 ? (
                  <div className="grid">
                    {recommendations.data.items.map((item) => (
                      <div className="aviso" key={item.id}>
                        <div style={{ flex: 1 }}>
                          <div className="fila-acciones" style={{ gap: 8, marginBottom: 6 }}>
                            <Badge state={item.estado}>{item.estado}</Badge>
                            <span className="nota-foot" style={{ margin: 0 }}>
                              {formatDateTime(item.fecha)}
                            </span>
                          </div>
                          <p style={{ margin: '0 0 4px' }}>
                            <b>{item.emprendimiento.codigo}</b> {item.emprendimiento.nombre} ·{' '}
                            {item.estudiante.nombres} {item.estudiante.apellidos}
                          </p>
                          <p className="ayuda" style={{ margin: 0 }}>
                            {item.mensaje ?? 'Sin mensaje adicional.'} —{' '}
                            {item.docente.nombres} {item.docente.apellidos}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : null}
              </Card>
            </div>

            <div className="grid">
              {isStudent ? (
                <Card title="Inscripción" hint="FR-021">
                  {event.requiereRegistro ? (
                    <>
                      <p className="ayuda" style={{ marginTop: 0 }}>
                        {event.inscrito
                          ? 'Ya tienes un puesto reservado. Puedes liberarlo si no vas a asistir.'
                          : 'La inscripción descuenta un puesto del cupo. El servidor evita que dos estudiantes tomen el último.'}
                      </p>
                      <div className="fila-acciones">
                        {event.inscrito ? (
                          <Button
                            variant="secundario"
                            icon="x"
                            loading={unregister.isPending}
                            onClick={() =>
                              unregister.mutate(event.id, {
                                onSuccess: () => showToast('Inscripción cancelada.', 'ok'),
                                onError: (caught) => showToast(errorMessage(caught), 'error'),
                              })
                            }
                          >
                            Cancelar mi inscripción
                          </Button>
                        ) : (
                          <Button
                            variant="primario"
                            icon="check"
                            loading={register.isPending}
                            disabled={event.cupo !== null && event.cupo <= 0}
                            onClick={() =>
                              register.mutate(event.id, {
                                onSuccess: () => showToast('Inscripción confirmada.', 'ok'),
                                onError: (caught) => showToast(errorMessage(caught), 'error'),
                              })
                            }
                          >
                            Inscribirme
                          </Button>
                        )}
                      </div>
                      {event.cupo !== null && event.cupo <= 0 && !event.inscrito ? (
                        <p className="nota-foot">El evento no tiene cupos disponibles.</p>
                      ) : null}
                    </>
                  ) : (
                    <Callout icon="bombilla">
                      Este evento no requiere inscripción: puedes asistir sin reservar cupo.
                    </Callout>
                  )}
                </Card>
              ) : null}

              {isTeacher ? (
                <Card title="Recomendar a un emprendimiento" hint="Solo asignados">
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    Envía el evento a uno de tus emprendimientos. La recomendación queda
                    <b> Pendiente</b> y avisa al estudiante; no hay endpoint para cambiarla (P-40).
                  </p>
                  <Button
                    variant="primario"
                    icon="enviar"
                    disabled={event.estado !== 'Publicado'}
                    onClick={() => setRecommendOpen(true)}
                  >
                    Recomendar evento
                  </Button>
                  {event.estado !== 'Publicado' ? (
                    <p className="nota-foot">Solo se recomiendan eventos publicados.</p>
                  ) : null}
                </Card>
              ) : null}

              {isAdmin ? (
                <Card title="Administración" hint="Baja lógica">
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    Dar de baja el evento lo retira de todas las lecturas y conserva el
                    histórico de inscripciones y recomendaciones.
                  </p>
                  <Button
                    variant="secundario"
                    icon="trash"
                    loading={remove.isPending}
                    onClick={() =>
                      remove.mutate(event.id, {
                        onSuccess: () => {
                          showToast('Evento dado de baja.', 'ok');
                          navigate(basePath);
                        },
                        onError: (caught) => showToast(errorMessage(caught), 'error'),
                      })
                    }
                  >
                    Dar de baja
                  </Button>
                </Card>
              ) : null}
            </div>
          </div>
        )}
      </QueryGate>

      <Modal
        open={recommendOpen}
        title="Recomendar este evento"
        onClose={() => setRecommendOpen(false)}
        footer={
          <>
            <Button variant="secundario" onClick={() => setRecommendOpen(false)}>
              Cancelar
            </Button>
            <Button
              variant="primario"
              loading={recommend.isPending}
              disabled={!recommendTarget}
              onClick={() => {
                setError(null);
                recommend.mutate(
                  {
                    id: eventId,
                    emprendimientoId: Number(recommendTarget),
                    mensaje: recommendMessage.trim() || undefined,
                  },
                  {
                    onSuccess: () => {
                      setRecommendOpen(false);
                      setRecommendTarget('');
                      setRecommendMessage('');
                      showToast('Recomendación enviada al estudiante.', 'ok');
                    },
                    onError: (caught) => setError(errorMessage(caught)),
                  },
                );
              }}
            >
              Enviar recomendación
            </Button>
          </>
        }
      >
        <SelectField
          label="Emprendimiento"
          required
          value={recommendTarget}
          onChange={(changeEvent) => setRecommendTarget(changeEvent.target.value)}
          hint="Solo aparecen los emprendimientos con asignación activa."
        >
          <option value="">Selecciona un emprendimiento</option>
          {(entrepreneurships.data?.items ?? []).map((item) => (
            <option key={item.id} value={item.id}>
              {item.codigo} · {item.nombre}
            </option>
          ))}
        </SelectField>
        <TextAreaField
          label="Mensaje para el estudiante"
          rows={3}
          value={recommendMessage}
          onChange={(changeEvent) => setRecommendMessage(changeEvent.target.value)}
          hint="Opcional. Se guarda tal cual en la recomendación."
        />
        {error ? (
          <div className="acceso-error" role="alert">
            {error}
          </div>
        ) : null}
      </Modal>
    </>
  );
}
