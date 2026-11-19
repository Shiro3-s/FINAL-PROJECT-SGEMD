import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { EVENTO_ESTADOS } from '@sgemd/shared';
import type { EventItem } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { useEventTypes } from '../../queries/catalogs.ts';
import { useEvents } from '../../queries/events.ts';
import { formatDate } from '../../lib/format.ts';

interface EventsListPageProps {
  roleLabel: string;
  basePath: string;
  canCreate: boolean;
}

/**
 * Lista de eventos.
 *
 * El estudiante y el docente solo ven `Publicado` (lo impone el servidor); el
 * administrador ve también los borradores y puede publicarlos. El filtro de
 * estado solo se pinta para el administrador porque para los demás no aporta.
 */
export function EventsListPage({ roleLabel, basePath, canCreate }: EventsListPageProps) {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [estado, setEstado] = useState('');
  const [tipoEventoId, setTipoEventoId] = useState('');
  const eventTypes = useEventTypes();

  const events = useEvents({
    page,
    pageSize: 25,
    q: term,
    estado: canCreate ? estado : undefined,
    tipoEventoId: tipoEventoId ? Number(tipoEventoId) : undefined,
  });

  return (
    <>
      <PageHeader
        title="Eventos"
        sub={
          canCreate
            ? 'Agenda institucional: crea borradores, publica y revisa inscripciones.'
            : 'Actividades publicadas por la coordinación del programa.'
        }
        crumbs={[{ label: roleLabel }, { label: 'Eventos' }]}
        actions={
          canCreate ? (
            <Link className="btn btn-primario" to={`${basePath}/nuevo`}>
              Nuevo evento
            </Link>
          ) : undefined
        }
      />

      <Card flush>
        <Toolbar>
          <form
            className="crece"
            role="search"
            onSubmit={(event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              setTerm(q.trim());
              setPage(1);
            }}
          >
            <SearchBox value={q} onChange={setQ} placeholder="Buscar por nombre, lugar o audiencia" />
          </form>
          <SelectFilter
            label="Tipo de evento"
            value={tipoEventoId}
            onChange={(value) => {
              setTipoEventoId(value);
              setPage(1);
            }}
          >
            {(eventTypes.data ?? []).map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectFilter>
          {canCreate ? (
            <SelectFilter
              label="Estado"
              value={estado}
              onChange={(value) => {
                setEstado(value);
                setPage(1);
              }}
            >
              {EVENTO_ESTADOS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </SelectFilter>
          ) : null}
          <Button variant="secundario" icon="filter" onClick={() => setPage(1)}>
            Aplicar
          </Button>
        </Toolbar>

        <ListTable
          query={events}
          caption="Eventos"
          unit="eventos"
          emptyTitle="No hay eventos para mostrar"
          emptyText={
            canCreate
              ? 'Crea el primer evento de la agenda institucional.'
              : 'Cuando la coordinación publique un evento aparecerá aquí.'
          }
          onPageChange={setPage}
          rowKey={(event: EventItem) => event.id}
          columns={[
            {
              key: 'nombre',
              header: 'Evento',
              render: (event) => (
                <div>
                  <Link to={`${basePath}/${event.id}`}>
                    <b>{event.nombreEvento}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {event.tipoEvento?.nombre ?? 'Sin tipo'} · {event.modalidad?.nombre ?? 'Sin modalidad'}
                  </span>
                </div>
              ),
            },
            {
              key: 'fecha',
              header: 'Fecha',
              render: (event) =>
                event.fecha ? (
                  <span>
                    {formatDate(`${event.fecha}T12:00:00`)}
                    <span className="nota-foot" style={{ display: 'block' }}>
                      {event.horaInicio} a {event.horaFin}
                    </span>
                  </span>
                ) : (
                  'Por definir'
                ),
            },
            {
              key: 'lugar',
              header: 'Lugar o enlace',
              render: (event) => event.lugar ?? event.enlace ?? '—',
            },
            {
              key: 'cupo',
              header: 'Cupo',
              render: (event) =>
                event.cupo === null ? 'Sin tope' : `${event.cupo} de ${event.capacidadMaxima ?? '—'}`,
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (event) => <Badge state={event.estado}>{event.estado}</Badge>,
            },
            {
              key: 'acc',
              header: '',
              render: (event) => (
                <Link className="btn btn-secundario btn-sm" to={`${basePath}/${event.id}`}>
                  Ver
                </Link>
              ),
            },
          ]}
        />
      </Card>
    </>
  );
}
