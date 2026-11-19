import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { useEventTypes, useModalities } from '../../queries/catalogs.ts';
import { useCreateEvent, useEvent, useUpdateEvent } from '../../queries/events.ts';

/**
 * Alta y edición de eventos institucionales.
 *
 * `Aprobado` y `Rechazado` están reservados (P-37): solo se guardan `Pendiente`
 * y `Publicado`. El horario es todo o nada. El borrador solo lo ve el
 * administrador; publicar lo hace visible a estudiante y docente.
 */
export function EventFormPage() {
  const { id } = useParams();
  const editing = id !== undefined;
  const eventId = Number(id);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const eventQuery = useEvent(editing && Number.isFinite(eventId) ? eventId : null);
  const create = useCreateEvent();
  const update = useUpdateEvent(Number.isFinite(eventId) ? eventId : 0);
  const eventTypes = useEventTypes();
  const modalities = useModalities();

  const [nombreEvento, setNombreEvento] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [dirigidoA, setDirigidoA] = useState('');
  const [capacidadMaxima, setCapacidadMaxima] = useState('');
  const [estado, setEstado] = useState<'Pendiente' | 'Publicado'>('Pendiente');
  const [requiereRegistro, setRequiereRegistro] = useState(true);
  const [lugar, setLugar] = useState('');
  const [enlace, setEnlace] = useState('');
  const [tipoEventoId, setTipoEventoId] = useState('');
  const [modalidadId, setModalidadId] = useState('');
  const [fecha, setFecha] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFin, setHoraFin] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const event = eventQuery.data;
    if (!event) return;
    setNombreEvento(event.nombreEvento);
    setDescripcion(event.descripcion ?? '');
    setDirigidoA(event.dirigidoA ?? '');
    setCapacidadMaxima(event.capacidadMaxima === null ? '' : String(event.capacidadMaxima));
    setEstado(event.estado === 'Publicado' ? 'Publicado' : 'Pendiente');
    setRequiereRegistro(event.requiereRegistro);
    setLugar(event.lugar ?? '');
    setEnlace(event.enlace ?? '');
    setTipoEventoId(event.tipoEvento ? String(event.tipoEvento.id) : '');
    setModalidadId(event.modalidad ? String(event.modalidad.id) : '');
    setFecha(event.fecha ?? '');
    setHoraInicio(event.horaInicio ?? '');
    setHoraFin(event.horaFin ?? '');
  }, [eventQuery.data]);

  const form = (
    <form
      onSubmit={(formEvent: FormEvent<HTMLFormElement>) => {
        formEvent.preventDefault();
        setError(null);
        if (nombreEvento.trim().length < 3) {
          setError('El nombre del evento debe tener al menos 3 caracteres.');
          return;
        }
        const hasSomeTime = Boolean(fecha || horaInicio || horaFin);
        if (hasSomeTime && (!fecha || !horaInicio || !horaFin)) {
          setError('El horario se envía completo: fecha, inicio y fin.');
          return;
        }
        if (hasSomeTime && horaFin <= horaInicio) {
          setError('La hora de fin debe ser posterior a la de inicio.');
          return;
        }
        const capacity = capacidadMaxima.trim() ? Number(capacidadMaxima) : null;
        if (capacity !== null && (!Number.isFinite(capacity) || capacity <= 0)) {
          setError('La capacidad debe ser un entero positivo.');
          return;
        }
        const body: Record<string, unknown> = {
          nombreEvento: nombreEvento.trim(),
          descripcion: descripcion.trim() || null,
          dirigidoA: dirigidoA.trim() || null,
          capacidadMaxima: capacity,
          estado,
          requiereRegistro,
          lugar: lugar.trim() || null,
          enlace: enlace.trim() || null,
          ...(tipoEventoId ? { tipoEventoId: Number(tipoEventoId) } : {}),
          ...(modalidadId ? { modalidadId: Number(modalidadId) } : {}),
          ...(hasSomeTime ? { fecha, horaInicio, horaFin } : {}),
        };
        if (editing) {
          update.mutate(body, {
            onSuccess: (event) => {
              showToast('Evento actualizado.', 'ok');
              navigate(`/admin/eventos/${event.id}`);
            },
            onError: (caught) => setError(errorMessage(caught)),
          });
        } else {
          create.mutate(body, {
            onSuccess: (event) => {
              showToast('Evento creado.', 'ok');
              navigate(`/admin/eventos/${event.id}`);
            },
            onError: (caught) => setError(errorMessage(caught)),
          });
        }
      }}
      noValidate
    >
      <TextField
        label="Nombre del evento"
        required
        value={nombreEvento}
        onChange={(changeEvent) => setNombreEvento(changeEvent.target.value)}
        placeholder="Startup Minuto de Dios"
      />
      <TextAreaField
        label="Descripción"
        rows={3}
        value={descripcion}
        onChange={(changeEvent) => setDescripcion(changeEvent.target.value)}
      />
      <div className="grid g-2">
        <TextField
          label="Dirigido a"
          value={dirigidoA}
          onChange={(changeEvent) => setDirigidoA(changeEvent.target.value)}
          placeholder="Todos los estudiantes"
        />
        <TextField
          label="Capacidad máxima"
          type="number"
          min={1}
          value={capacidadMaxima}
          onChange={(changeEvent) => setCapacidadMaxima(changeEvent.target.value)}
          hint="Vacío = sin tope de cupo."
        />
      </div>
      <div className="grid g-2">
        <SelectField
          label="Tipo de evento"
          value={tipoEventoId}
          onChange={(changeEvent) => setTipoEventoId(changeEvent.target.value)}
        >
          <option value="">Sin tipo</option>
          {(eventTypes.data ?? []).map((item) => (
            <option key={item.id} value={item.id}>
              {item.nombre}
            </option>
          ))}
        </SelectField>
        <SelectField
          label="Modalidad"
          value={modalidadId}
          onChange={(changeEvent) => setModalidadId(changeEvent.target.value)}
        >
          <option value="">Sin modalidad</option>
          {(modalities.data ?? []).map((item) => (
            <option key={item.id} value={item.id}>
              {item.nombre}
            </option>
          ))}
        </SelectField>
      </div>
      <div className="grid g-3">
        <TextField
          label="Fecha"
          type="date"
          value={fecha}
          onChange={(changeEvent) => setFecha(changeEvent.target.value)}
        />
        <TextField
          label="Hora de inicio"
          type="time"
          value={horaInicio}
          onChange={(changeEvent) => setHoraInicio(changeEvent.target.value)}
        />
        <TextField
          label="Hora de fin"
          type="time"
          value={horaFin}
          onChange={(changeEvent) => setHoraFin(changeEvent.target.value)}
        />
      </div>
      <div className="grid g-2">
        <TextField
          label="Lugar"
          value={lugar}
          onChange={(changeEvent) => setLugar(changeEvent.target.value)}
          placeholder="Auditorio principal"
        />
        <TextField
          label="Enlace"
          value={enlace}
          onChange={(changeEvent) => setEnlace(changeEvent.target.value)}
          placeholder="https://…"
        />
      </div>
      <div className="grid g-2">
        <SelectField
          label="Estado"
          value={estado}
          onChange={(changeEvent) =>
            setEstado(changeEvent.target.value === 'Publicado' ? 'Publicado' : 'Pendiente')
          }
          hint="Aprobado y Rechazado están reservados (P-37)."
        >
          <option value="Pendiente">Pendiente (borrador)</option>
          <option value="Publicado">Publicado</option>
        </SelectField>
        <SelectField
          label="Inscripción"
          value={requiereRegistro ? 'si' : 'no'}
          onChange={(changeEvent) => setRequiereRegistro(changeEvent.target.value === 'si')}
        >
          <option value="si">Requiere inscripción</option>
          <option value="no">Asistencia libre</option>
        </SelectField>
      </div>

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      <div className="form-acciones">
        <Button variant="secundario" onClick={() => navigate(editing ? `/admin/eventos/${eventId}` : '/admin/eventos')}>
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="primario"
          icon="check"
          loading={editing ? update.isPending : create.isPending}
        >
          {editing ? 'Guardar cambios' : 'Crear evento'}
        </Button>
      </div>
    </form>
  );

  return (
    <>
      <PageHeader
        title={editing ? 'Editar evento' : 'Nuevo evento'}
        sub="Agenda institucional del programa de emprendimiento."
        crumbs={[
          { label: 'ADMINISTRADOR' },
          { label: 'Eventos', to: '/admin/eventos' },
          { label: editing ? 'Editar' : 'Nuevo' },
        ]}
      />

      <div className="grid g-2-1">
        <Card title="Datos del evento">
          {editing ? (
            <QueryGate query={eventQuery} loadingLabel="Cargando el evento…">
              {() => form}
            </QueryGate>
          ) : (
            form
          )}
        </Card>

        <Card title="Publicación" hint="Visibilidad">
          <Callout icon="bombilla">
            Un evento <b>Pendiente</b> es un borrador: estudiante y docente reciben{' '}
            <code>404</code>. Al publicarlo aparece en su agenda y, si requiere registro, se
            habilita la inscripción con control de cupo.
          </Callout>
          <p className="ayuda">
            Rebajar la capacidad por debajo de las inscripciones actuales responde{' '}
            <code>EVENT_CAPACITY_BELOW_REGISTRATIONS</code>.
          </p>
        </Card>
      </div>
    </>
  );
}
