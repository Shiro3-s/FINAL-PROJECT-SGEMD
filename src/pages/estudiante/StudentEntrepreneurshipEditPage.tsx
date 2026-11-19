import { useEffect, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import type { Entrepreneurship } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import {
  useEntrepreneurship,
  useUpdateEntrepreneurship,
} from '../../queries/entrepreneurship.ts';

/**
 * Edición del emprendimiento por su dueño.
 *
 * El estudiante solo puede cambiar `nombre`, `descripcion` y `redesSociales`
 * (`docs/api.md` §Emprendimientos): si la vista enviara el sector o la etapa, la
 * API respondería `403 FIELD_NOT_ALLOWED`. Los campos que dependen de la
 * coordinación se muestran como lectura, no como controles deshabilitados que
 * confundan sobre quién los cambia.
 */
export function StudentEntrepreneurshipEditPage() {
  const { id } = useParams();
  const entrepreneurshipId = Number(id);
  const query = useEntrepreneurship(
    Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );

  return (
    <>
      <PageHeader
        title="Editar emprendimiento"
        sub="Actualiza la información que tienes permitido modificar."
        crumbs={[
          { label: 'ESTUDIANTE' },
          { label: 'Mi emprendimiento', to: '/estudiante/emprendimientos' },
          { label: 'Editar' },
        ]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/emprendimientos">
            Volver
          </Link>
        }
      />

      <QueryGate query={query} loadingLabel="Cargando el emprendimiento…">
        {(item: Entrepreneurship) => <EditForm item={item} />}
      </QueryGate>
    </>
  );
}

function EditForm({ item }: { item: Entrepreneurship }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const update = useUpdateEntrepreneurship(item.id);
  const [nombre, setNombre] = useState(item.nombre);
  const [descripcion, setDescripcion] = useState(item.descripcion ?? '');
  const [redesSociales, setRedesSociales] = useState(item.redesSociales ?? '');
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setNombre(item.nombre);
    setDescripcion(item.descripcion ?? '');
    setRedesSociales(item.redesSociales ?? '');
  }, [item]);

  const submit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setError(null);
    if (nombre.trim().length < 4) {
      setError('El nombre debe tener al menos 4 caracteres.');
      return;
    }
    if (nombre.trim().length > 150) {
      setError('El nombre no puede superar los 150 caracteres.');
      return;
    }
    if (descripcion.length > 2000) {
      setError('La descripción no puede superar los 2000 caracteres.');
      return;
    }
    if (redesSociales.length > 300) {
      setError('Las redes sociales no pueden superar los 300 caracteres.');
      return;
    }
    update.mutate(
      {
        nombre: nombre.trim(),
        descripcion: descripcion.trim() ? descripcion.trim() : null,
        redesSociales: redesSociales.trim() ? redesSociales.trim() : null,
      },
      {
        onSuccess: () => {
          setSaved(true);
          showToast('Emprendimiento actualizado.', 'ok');
          navigate(`/estudiante/emprendimientos/${item.id}`);
        },
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  return (
    <div className="grid g-2-1">
      <Card title="Datos que puedes editar">
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
            maxLength={2000}
            rows={5}
            onChange={(event) => setDescripcion(event.target.value)}
            hint="Describe qué vendes, a quién y cómo lo haces."
          />
          <TextField
            label="Redes sociales"
            value={redesSociales}
            maxLength={300}
            onChange={(event) => setRedesSociales(event.target.value)}
            placeholder="@usuario, https://instagram.com/usuario"
            hint="Un solo campo: el diagrama no separa redes por canal."
          />

          {error ? (
            <div className="acceso-error" role="alert">
              {error}
            </div>
          ) : null}
          {saved ? (
            <div className="aviso" role="status">
              Los cambios se guardaron.
            </div>
          ) : null}

          <div className="form-acciones">
            <Link className="btn btn-secundario" to={`/estudiante/emprendimientos/${item.id}`}>
              Cancelar
            </Link>
            <Button type="submit" variant="primario" icon="check" loading={update.isPending}>
              Guardar cambios
            </Button>
          </div>
        </form>
      </Card>

      <Card title="Campos a cargo de la coordinación">
        <DefinitionList
          items={[
            { term: 'Código', value: item.codigo },
            { term: 'Tipo de emprendimiento', value: item.esParalelo ? 'Paralelo autorizado' : 'Principal' },
            { term: 'Sector productivo', value: item.sector?.nombre ?? 'Sin sector' },
            { term: 'Etapa actual', value: item.etapa?.nombre ?? 'Sin etapa' },
            { term: 'Centro universitario', value: item.centroUniversitario?.nombre ?? '—' },
            {
              term: 'Estado de aprobación',
              value: item.estadoAprobacion,
            },
          ]}
        />
        <Callout icon="alerta">
          El sector, la etapa y el centro universitario los cambia el administrador. El acta
          de constitución se carga en <Link to="/estudiante/acta">Mi acta</Link> y la revisa
          la coordinación.
        </Callout>
      </Card>
    </div>
  );
}
