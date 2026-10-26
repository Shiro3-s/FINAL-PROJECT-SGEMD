import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { Entrepreneurship } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import {
  useAcademicPrograms,
  useEconomicSectors,
  useEntrepreneurshipStages,
  useUniversityCenters,
} from '../../queries/catalogs.ts';
import {
  useCreateEntrepreneurship,
  useEntrepreneurship,
  useUpdateEntrepreneurship,
} from '../../queries/entrepreneurship.ts';
import { useUsers } from '../../queries/users.ts';

/**
 * Alta y edición de un emprendimiento por el administrador (FR-012, R37).
 *
 * El alta nace `Pendiente` y exige estudiante propietario; `esParalelo` es la
 * autorización expresa de BR-004, no un dato descriptivo. En edición el dueño no
 * se cambia y la API solo acepta nombre, descripción, redes, sector, etapa y
 * centro. El estado de aprobación se gestiona en el listado, no aquí.
 */
export function AdminEntrepreneurshipFormPage() {
  const { id } = useParams();
  const editing = id !== undefined;
  const entrepreneurshipId = Number(id);
  const query = useEntrepreneurship(
    editing && Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );

  return (
    <>
      <PageHeader
        title={editing ? 'Editar emprendimiento' : 'Nuevo emprendimiento'}
        sub={
          editing
            ? 'Actualiza los datos que dependen de la coordinación.'
            : 'Registra el emprendimiento de un estudiante. Nace Pendiente de aprobación.'
        }
        crumbs={[
          { label: 'ADMINISTRADOR' },
          { label: 'Emprendimientos', to: '/admin/emprendimientos' },
          { label: editing ? 'Editar' : 'Nuevo' },
        ]}
      />
      {editing ? (
        <QueryGate query={query} loadingLabel="Cargando el emprendimiento…">
          {(item: Entrepreneurship) => <EntrepreneurshipForm item={item} />}
        </QueryGate>
      ) : (
        <EntrepreneurshipForm item={null} />
      )}
    </>
  );
}

function EntrepreneurshipForm({ item }: { item: Entrepreneurship | null }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const editing = item !== null;
  const sectors = useEconomicSectors();
  const stages = useEntrepreneurshipStages();
  const centers = useUniversityCenters();
  const programs = useAcademicPrograms();
  const students = useUsers('students', { page: 1, pageSize: 100, estado: 'Activo' });
  const create = useCreateEntrepreneurship();
  const update = useUpdateEntrepreneurship(item?.id ?? 0);

  const [nombre, setNombre] = useState(item?.nombre ?? '');
  const [descripcion, setDescripcion] = useState(item?.descripcion ?? '');
  const [redes, setRedes] = useState(item?.redesSociales ?? '');
  const [estudianteId, setEstudianteId] = useState(
    item ? String(item.estudiante.id) : '',
  );
  const [sectorId, setSectorId] = useState(String(item?.sector?.id ?? ''));
  const [etapaId, setEtapaId] = useState(String(item?.etapa?.id ?? ''));
  const [centroId, setCentroId] = useState(String(item?.centroUniversitario?.id ?? ''));
  const [esParalelo, setEsParalelo] = useState(item?.esParalelo ?? false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!item) return;
    setNombre(item.nombre);
    setDescripcion(item.descripcion ?? '');
    setRedes(item.redesSociales ?? '');
    setEstudianteId(String(item.estudiante.id));
    setSectorId(String(item.sector?.id ?? ''));
    setEtapaId(String(item.etapa?.id ?? ''));
    setCentroId(String(item.centroUniversitario?.id ?? ''));
    setEsParalelo(item.esParalelo);
  }, [item]);

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    if (nombre.trim().length < 4) {
      setError('El nombre debe tener al menos 4 caracteres.');
      return;
    }
    if (!editing && !estudianteId) {
      setError('Selecciona el estudiante propietario.');
      return;
    }
    const base = {
      nombre: nombre.trim(),
      descripcion: descripcion.trim() ? descripcion.trim() : null,
      redesSociales: redes.trim() ? redes.trim() : null,
      sectorId: sectorId ? Number(sectorId) : null,
      etapaId: etapaId ? Number(etapaId) : null,
      centroUniversitarioId: centroId ? Number(centroId) : null,
    };
    if (editing) {
      update.mutate(base, {
        onSuccess: () => {
          showToast('Emprendimiento actualizado.', 'ok');
          navigate(`/admin/emprendimientos/${item.id}`);
        },
        onError: (caught) => setError(errorMessage(caught)),
      });
      return;
    }
    create.mutate(
      { ...base, estudianteId: Number(estudianteId), esParalelo },
      {
        onSuccess: (created) => {
          showToast('Emprendimiento creado en estado Pendiente.', 'ok');
          navigate(`/admin/emprendimientos/${created.id}`);
        },
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  const busy = create.isPending || update.isPending;

  return (
    <div className="grid g-2-1">
      <Card title={editing ? 'Datos editables' : 'Datos del emprendimiento'}>
        <form onSubmit={submit} noValidate>
          <TextField
            label="Nombre del emprendimiento"
            required
            value={nombre}
            maxLength={150}
            onChange={(event) => setNombre(event.target.value)}
            hint="Entre 4 y 150 caracteres."
          />
          <TextAreaField
            label="Descripción"
            value={descripcion}
            rows={5}
            maxLength={2000}
            onChange={(event) => setDescripcion(event.target.value)}
            placeholder="Describe qué vende, a quién y cómo lo hace"
          />
          <TextField
            label="Redes sociales"
            value={redes}
            maxLength={300}
            onChange={(event) => setRedes(event.target.value)}
            placeholder="@usuario, https://instagram.com/usuario"
          />

          {editing ? (
            <DefinitionList
              items={[
                { term: 'Propietario', value: `${item.estudiante.nombres} ${item.estudiante.apellidos}` },
                { term: 'Código', value: item.codigo },
                { term: 'Estado', value: item.estadoAprobacion },
              ]}
            />
          ) : (
            <>
              <SelectField
                label="Estudiante propietario"
                required
                value={estudianteId}
                onChange={(event) => setEstudianteId(event.target.value)}
                placeholder="Selecciona un estudiante activo"
              >
                {(students.data?.items ?? []).map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.nombres} {student.apellidos} — {student.codigo}
                  </option>
                ))}
              </SelectField>
              <label className="campo-check" style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                <input
                  type="checkbox"
                  checked={esParalelo}
                  onChange={(event) => setEsParalelo(event.target.checked)}
                />
                <span>
                  Autorizar como emprendimiento paralelo
                  <span className="nota-foot" style={{ display: 'block' }}>
                    BR-004: es la autorización expresa para un segundo emprendimiento del
                    mismo estudiante.
                  </span>
                </span>
              </label>
            </>
          )}

          <div className="grid g-2">
            <SelectField
              label="Sector económico"
              value={sectorId}
              onChange={(event) => setSectorId(event.target.value)}
              placeholder="Sin sector"
            >
              {(sectors.data ?? []).map((sector) => (
                <option key={sector.id} value={sector.id}>
                  {sector.nombre}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Etapa"
              value={etapaId}
              onChange={(event) => setEtapaId(event.target.value)}
              placeholder="Sin etapa"
            >
              {(stages.data ?? []).map((stage) => (
                <option key={stage.id} value={stage.id}>
                  {stage.nombre}
                </option>
              ))}
            </SelectField>
          </div>
          <SelectField
            label="Centro universitario"
            value={centroId}
            onChange={(event) => setCentroId(event.target.value)}
            placeholder="Sin centro"
          >
            {(centers.data ?? []).map((center) => (
              <option key={center.id} value={center.id}>
                {center.nombre}
              </option>
            ))}
          </SelectField>

          {error ? (
            <div className="acceso-error" role="alert">
              {error}
            </div>
          ) : null}

          <div className="form-acciones">
            <Button
              type="button"
              variant="secundario"
              onClick={() => navigate('/admin/emprendimientos')}
            >
              Cancelar
            </Button>
            <Button type="submit" variant="primario" icon="check" loading={busy}>
              {editing ? 'Guardar cambios' : 'Crear emprendimiento'}
            </Button>
          </div>
        </form>
      </Card>

      <Card title="Reglas de la coordinación">
        <Callout icon="alerta">
          Un emprendimiento nace <b>Pendiente</b>. Aprobarlo o rechazarlo se hace en el
          listado y el rechazo exige motivo. El propietario no se puede cambiar después del
          alta.
        </Callout>
        <p className="ayuda">
          El catálogo de programas académicos ({programs.data?.length ?? 0} programas) se usa
          en los perfiles; el emprendimiento no guarda programa, solo centro, sector y etapa.
        </p>
      </Card>
    </div>
  );
}
