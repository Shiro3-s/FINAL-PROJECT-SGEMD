import { useEffect, useState, type FormEvent } from 'react';
import { useLocation } from 'react-router-dom';
import { ASIGNACION_ESTADOS } from '@sgemd/shared';
import type { Assignment, Entrepreneurship } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { Modal } from '../../components/Modal.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDate } from '../../lib/format.ts';
import {
  useAssignments,
  useCreateAssignment,
  useDeleteAssignment,
  useUpdateAssignment,
} from '../../queries/assignments.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useUsers } from '../../queries/users.ts';

/**
 * Asignaciones mentor → emprendimiento (FR-013, BR-009, R34).
 *
 * Una asignación solo se puede crear si el acta del estudiante está aprobada
 * (`ACTA_NOT_APPROVED`). El servidor controla el tope de 12 emprendimientos por
 * docente y el de horas semanales; esta vista no los duplica, solo muestra las
 * reglas. Retirar deja la asignación `inactiva`: no se reactiva, se crea otra.
 *
 * El tablero enlaza a `#asignar-docente`; el ancla abre el alta directamente.
 */
export function AdminAssignmentsPage() {
  const location = useLocation();
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [estado, setEstado] = useState('activa');
  const [mentorId, setMentorId] = useState('');
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<Assignment | null>(null);
  const [retiring, setRetiring] = useState<Assignment | null>(null);

  const { showToast } = useToast();
  const list = useAssignments({
    page,
    pageSize: 25,
    q: term,
    estado: estado || undefined,
    mentorId: mentorId ? Number(mentorId) : undefined,
  });
  const teachers = useUsers('teachers', { page: 1, pageSize: 100, estado: 'Activo' });
  const remove = useDeleteAssignment();

  useEffect(() => {
    if (location.hash === '#asignar-docente') setCreating(true);
  }, [location.hash]);

  return (
    <>
      <PageHeader
        title="Asignaciones"
        sub="Docente mentor de cada emprendimiento, horas semanales y retiro del acompañamiento."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Asignaciones' }]}
        actions={
          <Button
            variant="primario"
            icon="plus"
            id="asignar-docente"
            onClick={() => setCreating(true)}
          >
            Asignar docente
          </Button>
        }
      />

      <Callout icon="escudo">
        Solo se asigna un docente a un emprendimiento con <b>acta aprobada</b>. El servidor
        aplica el tope de <b>12 emprendimientos</b> y el de horas semanales por docente
        (BR-009, R34). Retirar una asignación no la borra: la deja <b>inactiva</b> y se crea
        otra si hace falta.
      </Callout>

      <Card flush className="mt-14">
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
              placeholder="Buscar por emprendimiento, estudiante o docente"
            />
          </form>
          <SelectFilter
            label="Docente"
            value={mentorId}
            onChange={(value) => {
              setMentorId(value);
              setPage(1);
            }}
          >
            {(teachers.data?.items ?? []).map((teacher) => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.nombres} {teacher.apellidos}
              </option>
            ))}
          </SelectFilter>
          <SelectFilter
            label="Estado"
            value={estado}
            onChange={(value) => {
              setEstado(value);
              setPage(1);
            }}
            allLabel="Todas"
          >
            {ASIGNACION_ESTADOS.map((item) => (
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
          caption="Asignaciones"
          unit="asignaciones"
          emptyTitle="No hay asignaciones para mostrar"
          emptyText="Asigna un docente a un emprendimiento con acta aprobada."
          onPageChange={setPage}
          rowKey={(item: Assignment) => item.id}
          columns={[
            {
              key: 'emprendimiento',
              header: 'Emprendimiento',
              render: (item) => (
                <div>
                  <b>{item.emprendimiento.nombre}</b>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {item.emprendimiento.codigo}
                  </span>
                </div>
              ),
            },
            {
              key: 'estudiante',
              header: 'Estudiante',
              render: (item) => (
                <div>
                  {item.estudiante.nombres} {item.estudiante.apellidos}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.estudiante.codigo}
                  </span>
                </div>
              ),
            },
            {
              key: 'mentor',
              header: 'Docente',
              render: (item) => (
                <div>
                  {item.mentor.nombres} {item.mentor.apellidos}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.mentor.codigo}
                  </span>
                </div>
              ),
            },
            { key: 'horas', header: 'Horas semanales', render: (item) => String(item.horasSemanales) },
            { key: 'fecha', header: 'Asignada', render: (item) => formatDate(item.fechaAsignacion) },
            {
              key: 'estado',
              header: 'Estado',
              render: (item) => <Badge state={item.estado === 'activa' ? 'Activo' : 'Inactivo'}>{item.estado}</Badge>,
            },
            {
              key: 'acc',
              header: '',
              render: (item) => (
                <div className="fila-acciones">
                  {item.estado === 'activa' ? (
                    <>
                      <Button
                        size="sm"
                        variant="secundario"
                        icon="edit"
                        onClick={() => setEditing(item)}
                      >
                        Reasignar
                      </Button>
                      <Button
                        size="sm"
                        variant="secundario"
                        icon="x"
                        onClick={() => setRetiring(item)}
                      >
                        Retirar
                      </Button>
                    </>
                  ) : (
                    <span className="nota-foot" style={{ margin: 0 }}>
                      Histórica
                    </span>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>

      {creating ? (
        <AssignmentModal
          mode="create"
          teachers={teachers.data?.items ?? []}
          onClose={() => setCreating(false)}
          onCreate={(body) => {
            setCreating(false);
            showToast(`Asignación creada para ${body.nombre}.`, 'ok');
          }}
        />
      ) : null}

      {editing ? (
        <AssignmentModal
          mode="edit"
          assignment={editing}
          teachers={teachers.data?.items ?? []}
          onClose={() => setEditing(null)}
          onDone={() => {
            setEditing(null);
            showToast('Asignación actualizada.', 'ok');
          }}
        />
      ) : null}

      <Modal
        open={retiring !== null}
        title="Retirar la asignación"
        onClose={() => setRetiring(null)}
        footer={
          <>
            <Button variant="secundario" onClick={() => setRetiring(null)}>
              Cancelar
            </Button>
            <Button
              variant="primario"
              icon="x"
              loading={remove.isPending}
              onClick={() => {
                if (!retiring) return;
                remove.mutate(retiring.id, {
                  onSuccess: () => {
                    setRetiring(null);
                    showToast('Asignación retirada. Queda inactiva en el historial.', 'ok');
                  },
                  onError: (caught) => showToast(errorMessage(caught), 'error'),
                });
              }}
            >
              Retirar
            </Button>
          </>
        }
      >
        <p style={{ marginTop: 0 }}>
          <b>{retiring?.mentor.nombres} {retiring?.mentor.apellidos}</b> dejará de acompañar{' '}
          <b>{retiring?.emprendimiento.nombre}</b>. La fila queda <b>inactiva</b> y no se
          reactiva: si el emprendimiento vuelve a necesitar mentor se crea una asignación
          nueva.
        </p>
      </Modal>
    </>
  );
}

function AssignmentModal({
  mode,
  assignment,
  teachers,
  onClose,
  onCreate,
  onDone,
}: {
  mode: 'create' | 'edit';
  assignment?: Assignment;
  teachers: { id: number; nombres: string; apellidos: string; codigo: string }[];
  onClose: () => void;
  onCreate?: (body: { nombre: string }) => void;
  onDone?: () => void;
}) {
  const create = useCreateAssignment();
  const update = useUpdateAssignment(assignment?.id ?? 0);
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const active = useAssignments({ page: 1, pageSize: 100, estado: 'activa' });
  const [emprendimientoId, setEmprendimientoId] = useState('');
  const [mentorId, setMentorId] = useState(
    assignment ? String(assignment.mentor.id) : '',
  );
  const [horas, setHoras] = useState(String(assignment?.horasSemanales ?? 4));
  const [error, setError] = useState<string | null>(null);

  const assignedIds = new Set(
    (active.data?.items ?? []).map((item) => item.emprendimiento.id),
  );
  const available = (entrepreneurships.data?.items ?? []).filter(
    (item: Entrepreneurship) =>
      item.estadoAprobacion === 'Aprobado' && !assignedIds.has(item.id),
  );

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    const hours = Number(horas);
    if (!Number.isInteger(hours) || hours < 1 || hours > 40) {
      setError('Las horas semanales deben ser un entero entre 1 y 40.');
      return;
    }
    if (!mentorId) {
      setError('Selecciona el docente mentor.');
      return;
    }
    if (mode === 'create') {
      if (!emprendimientoId) {
        setError('Selecciona el emprendimiento.');
        return;
      }
      create.mutate(
        {
          mentorId: Number(mentorId),
          emprendimientoId: Number(emprendimientoId),
          horasSemanales: hours,
        },
        {
          onSuccess: () => {
            const item = entrepreneurships.data?.items.find(
              (row) => row.id === Number(emprendimientoId),
            );
            onCreate?.({ nombre: item?.nombre ?? 'el emprendimiento' });
          },
          onError: (caught) => setError(errorMessage(caught)),
        },
      );
      return;
    }
    update.mutate(
      { mentorId: Number(mentorId), horasSemanales: hours },
      {
        onSuccess: () => onDone?.(),
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  const busy = create.isPending || update.isPending;

  return (
    <Modal
      open
      wide
      title={mode === 'create' ? 'Asignar docente' : 'Reasignar acompañamiento'}
      onClose={onClose}
      footer={
        <>
          <Button variant="secundario" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="primario"
            type="submit"
            form="assignment-form"
            icon="check"
            loading={busy}
          >
            {mode === 'create' ? 'Crear asignación' : 'Guardar cambios'}
          </Button>
        </>
      }
    >
      <form id="assignment-form" onSubmit={submit} noValidate>
        {mode === 'create' ? (
          <SelectField
            label="Emprendimiento"
            required
            value={emprendimientoId}
            onChange={(event) => setEmprendimientoId(event.target.value)}
            hint="Solo aparecen emprendimientos aprobados y sin docente activo."
          >
            <option value="">Selecciona el emprendimiento</option>
            {available.map((item) => (
              <option key={item.id} value={item.id}>
                {item.codigo} · {item.nombre} — {item.estudiante.nombres}{' '}
                {item.estudiante.apellidos}
              </option>
            ))}
          </SelectField>
        ) : (
          <p className="ayuda" style={{ marginTop: 0 }}>
            <b>{assignment?.emprendimiento.nombre}</b> ({assignment?.emprendimiento.codigo}) ·{' '}
            {assignment?.estudiante.nombres} {assignment?.estudiante.apellidos}
          </p>
        )}

        <SelectField
          label="Docente mentor"
          required
          value={mentorId}
          onChange={(event) => setMentorId(event.target.value)}
        >
          <option value="">Selecciona el docente</option>
          {teachers.map((teacher) => (
            <option key={teacher.id} value={teacher.id}>
              {teacher.nombres} {teacher.apellidos} · {teacher.codigo}
            </option>
          ))}
        </SelectField>

        <TextField
          label="Horas semanales"
          type="number"
          min={1}
          max={40}
          required
          value={horas}
          onChange={(event) => setHoras(event.target.value)}
          hint="El servidor valida el tope de horas del docente."
        />

        <Callout icon="alerta">
          Si el acta del estudiante no está aprobada, la API responde{' '}
          <code>ACTA_NOT_APPROVED</code>. Si el docente ya tiene 12 emprendimientos o no le
          quedan horas, responde <code>TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED</code> o{' '}
          <code>TEACHER_HOURS_LIMIT_REACHED</code>.
        </Callout>

        {error ? (
          <div className="acceso-error" role="alert">
            {error}
          </div>
        ) : null}
      </form>
    </Modal>
  );
}
