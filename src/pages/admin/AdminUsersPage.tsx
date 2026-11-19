import { useEffect, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CUENTA_ESTADOS, NIVELES_ACADEMICOS } from '@sgemd/shared';
import type { CuentaEstado, NivelAcademico } from '@sgemd/shared';
import type { SessionUser } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { Modal } from '../../components/Modal.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { errorMessage } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { useToast } from '../../components/Toast.tsx';
import {
  useAcademicPrograms,
  usePopulationTypes,
  useTypeDocuments,
  useTypeUsers,
  useUniversityCenters,
  useMunicipalities,
} from '../../queries/catalogs.ts';
import {
  useChangeUserState,
  useCreateUser,
  useDeleteUser,
  useReactivateUser,
  useUpdateUser,
  useUsers,
  useValidateUser,
  type CreateUserBody,
} from '../../queries/users.ts';
import { nameOf } from '../../lib/labels.ts';
import { formatDateTime } from '../../lib/format.ts';

type Kind = 'students' | 'teachers';

const KIND_LABEL: Record<Kind, string> = {
  students: 'Estudiantes',
  teachers: 'Docentes',
};

/**
 * Gestión de perfiles (FR-011, R33, R36).
 *
 * Dos tablas, una por rol, porque la API separa `/users/students` y
 * `/users/teachers` y el alta solo admite esos dos roles. El alta no fija
 * contraseña: el servidor envía un código de recuperación al titular. La baja es
 * lógica y no se puede deshacer desde la API (P-16), así que la confirmación lo
 * advierte.
 */
export function AdminUsersPage() {
  const [kind, setKind] = useState<Kind>('students');
  const [page, setPage] = useState(1);
  /** El buscador global del marco navega aquí con `?q=`; se aplica a la pestaña activa. */
  const [params] = useSearchParams();
  const urlTerm = params.get('q')?.trim() ?? '';
  const [q, setQ] = useState(urlTerm);
  const [term, setTerm] = useState(urlTerm);
  const [estado, setEstado] = useState('');
  const [editing, setEditing] = useState<SessionUser | null>(null);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState<SessionUser | null>(null);

  useEffect(() => {
    if (!urlTerm) return;
    setQ(urlTerm);
    setTerm(urlTerm);
    setPage(1);
  }, [urlTerm]);

  const { showToast } = useToast();
  const docs = useTypeDocuments();
  const programs = useAcademicPrograms();
  const centers = useUniversityCenters();
  const municipalities = useMunicipalities();
  const population = usePopulationTypes();
  const typeUsers = useTypeUsers();

  const list = useUsers(kind, { page, pageSize: 25, q: term, estado });
  const create = useCreateUser();
  const update = useUpdateUser(editing?.id ?? 0);
  const remove = useDeleteUser();
  const changeState = useChangeUserState();
  const validate = useValidateUser();
  const reactivate = useReactivateUser();

  const catalog = {
    docs: docs.data ?? [],
    programs: programs.data ?? [],
    centers: centers.data ?? [],
    municipalities: municipalities.data ?? [],
    population: population.data ?? [],
    typeUsers: typeUsers.data ?? [],
  };

  return (
    <>
      <PageHeader
        title="Gestión de perfiles"
        sub="Altas, edición, estado y baja lógica de estudiantes y docentes."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Usuarios' }]}
        actions={
          <Button variant="primario" icon="plus" onClick={() => setCreating(true)}>
            Nuevo {kind === 'students' ? 'estudiante' : 'docente'}
          </Button>
        }
      />

      <Callout icon="escudo">
        El alta crea la cuenta verificada y envía al correo institucional un código para
        establecer la contraseña. La API no permite restaurar una cuenta dada de baja (P-16).
      </Callout>

      <div className="mt-14">
        <Tabs
          label="Tipo de cuenta"
          active={kind}
          onChange={(value) => {
            setKind(value as Kind);
            setPage(1);
          }}
          items={[
            { id: 'students', label: 'Estudiantes' },
            { id: 'teachers', label: 'Docentes' },
          ]}
        />
        {(['students', 'teachers'] as const).map((tab) => (
          <TabPanel key={tab} id={tab} active={kind}>
            {tab === kind ? (
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
                      placeholder="Buscar por nombre, código, correo o documento"
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
                    {CUENTA_ESTADOS.map((item) => (
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
                  caption={KIND_LABEL[tab]}
                  unit="cuentas"
                  emptyTitle="No hay cuentas para mostrar"
                  emptyText="Ajusta los filtros o crea la primera cuenta."
                  onPageChange={setPage}
                  rowKey={(user: SessionUser) => user.id}
                  columns={[
                    {
                      key: 'nombre',
                      header: 'Nombre',
                      render: (user) => (
                        <div>
                          <b>
                            {user.nombres} {user.apellidos}
                          </b>
                          <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                            {user.codigo} · {user.correoInstitucional}
                          </span>
                        </div>
                      ),
                    },
                    {
                      key: 'documento',
                      header: 'Documento',
                      render: (user) =>
                        `${nameOf(catalog.docs, user.tipoDocumentoId)} ${user.numeroDocumento ?? ''}`,
                    },
                    {
                      key: 'academico',
                      header: 'Datos académicos',
                      render: (user) => (
                        <div>
                          {user.nivelAcademico ?? 'Sin nivel'}
                          <span className="nota-foot" style={{ display: 'block' }}>
                            {nameOf(catalog.programs, user.programaAcademicoId)}
                          </span>
                        </div>
                      ),
                    },
                    {
                      key: 'estado',
                      header: 'Estado',
                      render: (user) => <Badge state={user.estado}>{user.estado}</Badge>,
                    },
                    {
                      key: 'actividad',
                      header: 'Última actividad',
                      render: (user) =>
                        user.ultimaActividad ? formatDateTime(user.ultimaActividad) : 'Sin acceso',
                    },
                    {
                      key: 'acc',
                      header: '',
                      render: (user) => (
                        <div className="fila-acciones">
                          <Button
                            size="sm"
                            variant="secundario"
                            icon="edit"
                            onClick={() => setEditing(user)}
                          >
                            Editar
                          </Button>
                          {user.estado === 'Limitado' ? (
                            <Button
                              size="sm"
                              variant="primario"
                              icon="check"
                              loading={validate.isPending}
                              onClick={() => {
                                validate.mutate(user.id, {
                                  onSuccess: () => showToast('Cuenta activada.', 'ok'),
                                  onError: (caught) => showToast(errorMessage(caught), 'error'),
                                });
                              }}
                            >
                              Activar
                            </Button>
                          ) : null}
                          {user.estado === 'Inactivo' ? (
                            <Button
                              size="sm"
                              variant="primario"
                              icon="check"
                              loading={reactivate.isPending}
                              onClick={() => {
                                reactivate.mutate(user.id, {
                                  onSuccess: () => showToast('Cuenta reactivada.', 'ok'),
                                  onError: (caught) => showToast(errorMessage(caught), 'error'),
                                });
                              }}
                            >
                              Reactivar
                            </Button>
                          ) : null}
                          {user.estado === 'Limitado' ? null : (
                            <Button
                              size="sm"
                              variant="secundario"
                              icon="lock"
                              onClick={() => {
                                const next: CuentaEstado =
                                  user.estado === 'Activo' ? 'Inactivo' : 'Activo';
                                changeState.mutate(
                                  { id: user.id, estado: next as 'Activo' | 'Inactivo' },
                                  {
                                    onSuccess: () =>
                                      showToast(`Cuenta en estado ${next}.`, 'ok'),
                                    onError: (caught) =>
                                      showToast(errorMessage(caught), 'error'),
                                  },
                                );
                              }}
                            >
                              {user.estado === 'Activo' ? 'Desactivar' : 'Activar'}
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="secundario"
                            icon="trash"
                            onClick={() => setDeleting(user)}
                          >
                            Dar de baja
                          </Button>
                        </div>
                      ),
                    },
                  ]}
                />
              </Card>
            ) : null}
          </TabPanel>
        ))}
      </div>

      <UserModal
        key={creating ? 'new' : `edit-${editing?.id ?? 'none'}`}
        open={creating || editing !== null}
        user={editing}
        fixedKind={kind}
        catalog={catalog}
        loading={create.isPending || update.isPending}
        onClose={() => {
          setCreating(false);
          setEditing(null);
        }}
        onSubmit={(body) => {
          if (editing) {
            update.mutate(body as unknown as Record<string, unknown>, {
              onSuccess: () => {
                setEditing(null);
                showToast('Cuenta actualizada.', 'ok');
              },
              onError: (caught) => showToast(errorMessage(caught), 'error'),
            });
            return;
          }
          create.mutate(body as CreateUserBody, {
            onSuccess: () => {
              setCreating(false);
              showToast('Cuenta creada. Se envió el código de acceso al correo.', 'ok');
            },
            onError: (caught) => showToast(errorMessage(caught), 'error'),
          });
        }}
      />

      <Modal
        open={deleting !== null}
        title="Dar de baja la cuenta"
        onClose={() => setDeleting(null)}
        footer={
          <>
            <Button variant="secundario" onClick={() => setDeleting(null)}>
              Cancelar
            </Button>
            <Button
              variant="primario"
              icon="trash"
              loading={remove.isPending}
              onClick={() => {
                if (!deleting) return;
                remove.mutate(deleting.id, {
                  onSuccess: () => {
                    setDeleting(null);
                    showToast('Cuenta dada de baja.', 'ok');
                  },
                  onError: (caught) => showToast(errorMessage(caught), 'error'),
                });
              }}
            >
              Dar de baja
            </Button>
          </>
        }
      >
        <p style={{ marginTop: 0 }}>
          <b>
            {deleting?.nombres} {deleting?.apellidos}
          </b>{' '}
          saldrá de todos los listados y no podrá iniciar sesión. La fila no se borra, pero
          la API no ofrece restauración (P-16).
        </p>
      </Modal>
    </>
  );
}

interface UserCatalog {
  docs: { id: number; nombre: string }[];
  programs: { id: number; nombre: string }[];
  centers: { id: number; nombre: string }[];
  municipalities: { id: number; nombre: string }[];
  population: { id: number; nombre: string }[];
  typeUsers: { id: number; nombre: string }[];
}

function UserModal({
  open,
  user,
  fixedKind,
  catalog,
  loading,
  onClose,
  onSubmit,
}: {
  open: boolean;
  user: SessionUser | null;
  fixedKind: Kind;
  catalog: UserCatalog;
  loading: boolean;
  onClose: () => void;
  onSubmit: (body: CreateUserBody) => void;
}) {
  const editing = user !== null;
  const [nombres, setNombres] = useState(user?.nombres ?? '');
  const [apellidos, setApellidos] = useState(user?.apellidos ?? '');
  const [documento, setDocumento] = useState(user?.numeroDocumento ?? '');
  const [correo, setCorreo] = useState(user?.correoInstitucional ?? '');
  const [tipoDocumentoId, setTipoDocumentoId] = useState(String(user?.tipoDocumentoId ?? ''));
  const [rolId, setRolId] = useState(
    String(user?.rol.id ?? (fixedKind === 'students' ? 2 : 3)),
  );
  const [estado, setEstado] = useState<'Activo' | 'Limitado'>(
    user?.estado === 'Limitado' ? 'Limitado' : 'Activo',
  );
  const [nivel, setNivel] = useState(user?.nivelAcademico ?? '');
  const [programaId, setProgramaId] = useState(String(user?.programaAcademicoId ?? ''));
  const [centroId, setCentroId] = useState(String(user?.centroUniversitarioId ?? ''));
  const [municipioId, setMunicipioId] = useState(String(user?.municipioId ?? ''));
  const [poblacionId, setPoblacionId] = useState(String(user?.tipoPoblacionId ?? ''));
  const [tipoUsuarioId, setTipoUsuarioId] = useState(String(user?.tipoUsuarioId ?? ''));
  const [error, setError] = useState<string | null>(null);

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    if (!nombres.trim() || !apellidos.trim()) {
      setError('Nombres y apellidos son obligatorios.');
      return;
    }
    if (!editing && (!documento.trim() || !correo.trim() || !tipoDocumentoId)) {
      setError('Documento, correo y tipo de documento son obligatorios.');
      return;
    }
    const base = {
      nombres: nombres.trim(),
      apellidos: apellidos.trim(),
      numeroDocumento: documento.trim(),
      correoInstitucional: correo.trim(),
      tipoDocumentoId: Number(tipoDocumentoId),
      nivelAcademico: (nivel || null) as NivelAcademico | null,
      programaAcademicoId: programaId ? Number(programaId) : null,
      centroUniversitarioId: centroId ? Number(centroId) : null,
      municipioId: municipioId ? Number(municipioId) : null,
      tipoPoblacionId: poblacionId ? Number(poblacionId) : null,
      tipoUsuarioId: tipoUsuarioId ? Number(tipoUsuarioId) : null,
    };
    if (editing) {
      onSubmit(base as CreateUserBody);
      return;
    }
    onSubmit({ ...base, rolId: Number(rolId), estado });
  };

  return (
    <Modal
      open={open}
      title={editing ? 'Editar cuenta' : 'Nueva cuenta'}
      onClose={onClose}
      wide
      footer={
        <>
          <Button variant="secundario" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="primario"
            type="submit"
            form="user-form"
            icon="check"
            loading={loading}
          >
            {editing ? 'Guardar cambios' : 'Crear cuenta'}
          </Button>
        </>
      }
    >
      <form id="user-form" onSubmit={submit} noValidate>
        <div className="grid g-2">
          <TextField
            label="Nombres"
            required
            value={nombres}
            onChange={(event) => setNombres(event.target.value)}
          />
          <TextField
            label="Apellidos"
            required
            value={apellidos}
            onChange={(event) => setApellidos(event.target.value)}
          />
        </div>
        <div className="grid g-2">
          <TextField
            label="Número de documento"
            required
            value={documento}
            onChange={(event) => setDocumento(event.target.value)}
          />
          <SelectField
            label="Tipo de documento"
            required
            value={tipoDocumentoId}
            onChange={(event) => setTipoDocumentoId(event.target.value)}
            placeholder="Selecciona"
          >
            {catalog.docs.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
        </div>
        <TextField
          label="Correo institucional"
          type="email"
          required
          value={correo}
          onChange={(event) => setCorreo(event.target.value)}
          hint="El dominio debe estar autorizado en la configuración del programa."
        />
        {!editing ? (
          <div className="grid g-2">
            <SelectField
              label="Rol"
              required
              value={rolId}
              onChange={(event) => setRolId(event.target.value)}
            >
              <option value="2">Estudiante</option>
              <option value="3">Docente</option>
            </SelectField>
            <SelectField
              label="Estado inicial"
              required
              value={estado}
              onChange={(event) => setEstado(event.target.value as 'Activo' | 'Limitado')}
            >
              <option value="Activo">Activo</option>
              <option value="Limitado">Limitado</option>
            </SelectField>
          </div>
        ) : null}

        <div className="grid g-2">
          <SelectField
            label="Nivel académico"
            value={nivel}
            onChange={(event) => setNivel(event.target.value as NivelAcademico | '')}
            placeholder="Sin nivel"
          >
            {NIVELES_ACADEMICOS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Programa académico"
            value={programaId}
            onChange={(event) => setProgramaId(event.target.value)}
            placeholder="Sin programa"
          >
            {catalog.programs.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
        </div>
        <div className="grid g-2">
          <SelectField
            label="Centro universitario"
            value={centroId}
            onChange={(event) => setCentroId(event.target.value)}
            placeholder="Sin centro"
          >
            {catalog.centers.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Municipio"
            value={municipioId}
            onChange={(event) => setMunicipioId(event.target.value)}
            placeholder="Sin municipio"
          >
            {catalog.municipalities.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
        </div>
        <div className="grid g-2">
          <SelectField
            label="Tipo de población"
            value={poblacionId}
            onChange={(event) => setPoblacionId(event.target.value)}
            placeholder="Sin tipo"
          >
            {catalog.population.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Tipo de usuario"
            value={tipoUsuarioId}
            onChange={(event) => setTipoUsuarioId(event.target.value)}
            placeholder="Sin tipo"
          >
            {catalog.typeUsers.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre}
              </option>
            ))}
          </SelectField>
        </div>

        {error ? (
          <div className="acceso-error" role="alert">
            {error}
          </div>
        ) : null}
        {!editing ? (
          <p className="nota-foot">
            El código lo genera el servidor y la contraseña se establece con el código que
            llega al correo.
          </p>
        ) : null}
      </form>
    </Modal>
  );
}
