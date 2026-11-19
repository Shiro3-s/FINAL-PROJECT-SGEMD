import { useState, type FormEvent } from 'react';
import { SOLICITUD_ESTADOS } from '@sgemd/shared';
import type { RequestItem } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { Modal } from '../../components/Modal.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ReasonModal } from '../../components/ReasonModal.tsx';
import { errorMessage } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { useToast } from '../../components/Toast.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useModalities } from '../../queries/catalogs.ts';
import { useApproveRequest, useRejectRequest, useRequests } from '../../queries/requests.ts';
import { useUsers } from '../../queries/users.ts';

const TABS = [
  { id: '', label: 'Todas' },
  { id: 'Desbloqueo', label: 'Desbloqueos' },
  { id: 'Paralelo', label: 'Paralelos' },
  { id: 'Cita', label: 'Citas' },
] as const;

/**
 * Bandeja de solicitudes (R38).
 *
 * Un único listado con el contador de pendientes de toda la bandeja. Aprobar un
 * desbloqueo o un paralelo solo confirma; aprobar una cita exige docente, tema y
 * bloque, que es el cuerpo con el que nace la asesoría (P-19). Rechazar siempre
 * pide motivo.
 */
export function AdminRequestsPage() {
  const [tipo, setTipo] = useState('');
  const [estado, setEstado] = useState('Pendiente');
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [approving, setApproving] = useState<RequestItem | null>(null);
  const [rejecting, setRejecting] = useState<RequestItem | null>(null);

  const { showToast } = useToast();
  const list = useRequests({
    page,
    pageSize: 25,
    tipo: tipo || undefined,
    estado: estado || undefined,
    q: term,
  });
  const approve = useApproveRequest();
  const reject = useRejectRequest();

  const pendientes = list.data?.pendientes;

  return (
    <>
      <PageHeader
        title="Solicitudes"
        sub="Desbloqueos de cuenta, autorización de paralelos y citas de asesoría."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Solicitudes' }]}
      />

      <Callout icon="bombilla">
        {pendientes ? (
          <>
            Hay <b>{pendientes.total}</b> solicitudes pendientes: {pendientes.Desbloqueo}{' '}
            desbloqueos, {pendientes.Paralelo} paralelos y {pendientes.Cita} citas de asesoría.
          </>
        ) : (
          'Cargando el contador de pendientes…'
        )}
      </Callout>

      <div className="mt-14">
        <Tabs
          label="Tipo de solicitud"
          active={tipo}
          onChange={(value) => {
            setTipo(value);
            setPage(1);
          }}
          items={TABS.map((tab) => ({
            id: tab.id,
            label:
              tab.id === ''
                ? tab.label
                : `${tab.label}${pendientes ? ` (${pendientes[tab.id as 'Desbloqueo' | 'Paralelo' | 'Cita']})` : ''}`,
          }))}
        />
        {TABS.map((tab) => (
          <TabPanel key={tab.id || 'all'} id={tab.id} active={tipo}>
            {tipo === tab.id ? (
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
                    <SearchBox
                      value={q}
                      onChange={setQ}
                      placeholder="Buscar por estudiante, código, correo o detalle"
                    />
                  </form>
                  <SelectFilter
                    label="Estado"
                    value={estado}
                    onChange={(value) => {
                      setEstado(value);
                      setPage(1);
                    }}
                  >
                    {SOLICITUD_ESTADOS.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </SelectFilter>
                  <Button variant="secundario" icon="filter" onClick={() => setPage(1)}>
                    Aplicar
                  </Button>
                </Toolbar>

                <ListTable
                  query={list}
                  caption="Solicitudes"
                  unit="solicitudes"
                  emptyTitle="No hay solicitudes en esta bandeja"
                  emptyText="Cuando un usuario envíe una solicitud aparecerá aquí."
                  onPageChange={setPage}
                  rowKey={(item: RequestItem) => item.id}
                  columns={[
                    {
                      key: 'tipo',
                      header: 'Tipo',
                      render: (item) => (
                        <Badge tone="linea" icon="clipboard">
                          {item.tipo}
                        </Badge>
                      ),
                    },
                    {
                      key: 'solicitante',
                      header: 'Solicitante',
                      render: (item) => (
                        <div>
                          <b>
                            {item.solicitante.nombres} {item.solicitante.apellidos}
                          </b>
                          <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                            {item.solicitante.correoInstitucional ?? item.solicitante.codigo}
                          </span>
                        </div>
                      ),
                    },
                    {
                      key: 'detalle',
                      header: 'Detalle',
                      render: (item) => (
                        <div>
                          <span style={{ whiteSpace: 'pre-line' }}>{item.detalle}</span>
                          {item.emprendimiento ? (
                            <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                              {item.emprendimiento.codigo} — {item.emprendimiento.nombre}
                            </span>
                          ) : null}
                        </div>
                      ),
                    },
                    {
                      key: 'fecha',
                      header: 'Enviada',
                      render: (item) => formatDateTime(item.fechaSolicitud),
                    },
                    {
                      key: 'estado',
                      header: 'Estado',
                      render: (item) => (
                        <div>
                          <Badge state={item.estado}>{item.estado}</Badge>
                          {item.motivoRechazo ? (
                            <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                              {item.motivoRechazo}
                            </span>
                          ) : null}
                        </div>
                      ),
                    },
                    {
                      key: 'acc',
                      header: '',
                      render: (item) =>
                        item.estado === 'Pendiente' ? (
                          <div className="fila-acciones">
                            <Button
                              size="sm"
                              variant="primario"
                              icon="check"
                              onClick={() => setApproving(item)}
                            >
                              Aprobar
                            </Button>
                            <Button
                              size="sm"
                              variant="secundario"
                              icon="x"
                              onClick={() => setRejecting(item)}
                            >
                              Rechazar
                            </Button>
                          </div>
                        ) : (
                          <span className="nota-foot" style={{ margin: 0 }}>
                            {item.fechaResolucion
                              ? `Resuelta ${formatDateTime(item.fechaResolucion)}`
                              : 'Sin resolver'}
                          </span>
                        ),
                    },
                  ]}
                />
              </Card>
            ) : null}
          </TabPanel>
        ))}
      </div>

      {approving ? (
        <ApproveRequestModal
          request={approving}
          loading={approve.isPending}
          onClose={() => setApproving(null)}
          onConfirm={(body) => {
            approve.mutate(
              { id: approving.id, body },
              {
                onSuccess: () => {
                  setApproving(null);
                  showToast(
                    approving.tipo === 'Cita'
                      ? 'Solicitud aprobada y asesoría programada.'
                      : 'Solicitud aprobada.',
                    'ok',
                  );
                },
                onError: (caught) => showToast(errorMessage(caught), 'error'),
              },
            );
          }}
        />
      ) : null}

      <ReasonModal
        open={rejecting !== null}
        title="Rechazar la solicitud"
        label="Motivo del rechazo"
        hint="El motivo se envía al solicitante en la notificación."
        confirmLabel="Rechazar"
        loading={reject.isPending}
        onClose={() => setRejecting(null)}
        onSubmit={(motivo) => {
          if (!rejecting) return;
          reject.mutate(
            { id: rejecting.id, motivo },
            {
              onSuccess: () => {
                setRejecting(null);
                showToast('Solicitud rechazada.', 'ok');
              },
              onError: (caught) => showToast(errorMessage(caught), 'error'),
            },
          );
        }}
      />
    </>
  );
}

function ApproveRequestModal({
  request,
  loading,
  onClose,
  onConfirm,
}: {
  request: RequestItem;
  loading: boolean;
  onClose: () => void;
  onConfirm: (body?: Record<string, unknown>) => void;
}) {
  const isAppointment = request.tipo === 'Cita';
  const teachers = useUsers('teachers', { page: 1, pageSize: 100, estado: 'Activo' });
  const modalities = useModalities();
  const [docenteId, setDocenteId] = useState('');
  const [tema, setTema] = useState(
    `Asesoría${request.emprendimiento ? ` — ${request.emprendimiento.nombre}` : ''}`,
  );
  const [fecha, setFecha] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFin, setHoraFin] = useState('');
  const [modalidadId, setModalidadId] = useState('');
  const [lugarEnlace, setLugarEnlace] = useState('');
  const [error, setError] = useState<string | null>(null);

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    if (!isAppointment) {
      onConfirm();
      return;
    }
    if (!docenteId || !tema.trim() || !fecha || !horaInicio || !horaFin) {
      setError('Docente, tema, fecha y bloque completo son obligatorios.');
      return;
    }
    if (horaFin <= horaInicio) {
      setError('La hora final debe ser posterior a la inicial.');
      return;
    }
    onConfirm({
      docenteId: Number(docenteId),
      tema: tema.trim(),
      fecha,
      horaInicio,
      horaFin,
      ...(modalidadId ? { modalidadId: Number(modalidadId) } : {}),
      ...(lugarEnlace.trim() ? { lugarEnlace: lugarEnlace.trim() } : {}),
    });
  };

  return (
    <Modal
      open
      wide
      title={isAppointment ? 'Aprobar cita de asesoría' : 'Aprobar solicitud'}
      onClose={onClose}
      footer={
        <>
          <Button variant="secundario" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="primario"
            type="submit"
            form="approve-form"
            icon="check"
            loading={loading}
          >
            Aprobar
          </Button>
        </>
      }
    >
      <DefinitionList
        items={[
          {
            term: 'Solicitante',
            value: `${request.solicitante.nombres} ${request.solicitante.apellidos}`,
          },
          { term: 'Tipo', value: request.tipo },
          ...(request.emprendimiento
            ? [
                {
                  term: 'Emprendimiento',
                  value: `${request.emprendimiento.codigo} — ${request.emprendimiento.nombre}`,
                },
              ]
            : []),
          { term: 'Detalle', value: request.detalle },
        ]}
      />
      <form id="approve-form" onSubmit={submit} noValidate className="mt-14">
        {isAppointment ? (
          <>
            <Callout icon="alerta">
              La asesoría nace <b>Programada</b> con el docente y el bloque que elijas. El
              docente la confirma después y el sistema controla el solapamiento.
            </Callout>
            <SelectField
              label="Docente"
              required
              value={docenteId}
              onChange={(event) => setDocenteId(event.target.value)}
              placeholder="Selecciona un docente activo"
            >
              {(teachers.data?.items ?? []).map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.nombres} {teacher.apellidos} — {teacher.codigo}
                </option>
              ))}
            </SelectField>
            <TextField
              label="Tema"
              required
              value={tema}
              onChange={(event) => setTema(event.target.value)}
              maxLength={150}
            />
            <div className="grid g-3">
              <TextField
                label="Fecha"
                type="date"
                required
                value={fecha}
                onChange={(event) => setFecha(event.target.value)}
              />
              <TextField
                label="Hora de inicio"
                type="time"
                required
                value={horaInicio}
                onChange={(event) => setHoraInicio(event.target.value)}
              />
              <TextField
                label="Hora de fin"
                type="time"
                required
                value={horaFin}
                onChange={(event) => setHoraFin(event.target.value)}
              />
            </div>
            <div className="grid g-2">
              <SelectField
                label="Modalidad"
                value={modalidadId}
                onChange={(event) => setModalidadId(event.target.value)}
                placeholder="Sin modalidad"
              >
                {(modalities.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.nombre}
                  </option>
                ))}
              </SelectField>
              <TextField
                label="Lugar o enlace"
                value={lugarEnlace}
                onChange={(event) => setLugarEnlace(event.target.value)}
                maxLength={300}
                placeholder="https://meet.example.com/asesoria"
              />
            </div>
          </>
        ) : (
          <p className="ayuda">
            {request.tipo === 'Desbloqueo'
              ? 'Al aprobar, la cuenta pasa de Limitado o Inactivo a Activo.'
              : 'Al aprobar, el emprendimiento queda autorizado como paralelo y se recalculan los topes.'}
          </p>
        )}
        {error ? (
          <div className="acceso-error" role="alert">
            {error}
          </div>
        ) : null}
      </form>
    </Modal>
  );
}
