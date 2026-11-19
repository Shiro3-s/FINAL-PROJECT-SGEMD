import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { REVISION_ESTADOS, SEGUIMIENTO_TIPOS } from '@sgemd/shared';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { usePlanPhases } from '../../queries/catalogs.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useCreateTracing } from '../../queries/tracing.ts';

interface TracingFormPageProps {
  /** Prefijo del rol donde vive el avance: `/docente/avances` o `/admin/seguimiento`. */
  basePath?: string;
  roleLabel?: string;
}

/**
 * Registro de un avance de fase o comentario (FR-022).
 *
 * Un `Avance de fase` exige fase del plan; un `Comentario` no la lleva. El
 * autor es siempre la sesión y la API no acepta `usuariosId`. La evidencia se
 * sube después, en el detalle del seguimiento, porque la creación no es
 * multipart.
 */
export function TracingFormPage({
  basePath = '/docente/avances',
  roleLabel = 'DOCENTE',
}: TracingFormPageProps) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { user } = useAuth();
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const phases = usePlanPhases();
  const create = useCreateTracing();

  const [entrepreneurshipId, setEntrepreneurshipId] = useState('');
  const [tipo, setTipo] = useState<string>(SEGUIMIENTO_TIPOS[0]);
  const [fasePlanId, setFasePlanId] = useState('');
  const [fecha, setFecha] = useState(new Date().toISOString().slice(0, 10));
  const [descripcion, setDescripcion] = useState('');
  const [puntaje, setPuntaje] = useState('');
  const [estadoRevision, setEstadoRevision] = useState('Pendiente');
  const [error, setError] = useState<string | null>(null);

  const isAdvance = tipo === 'Avance de fase';

  return (
    <>
      <PageHeader
        title="Registrar avance"
        sub="Deja constancia del avance de fase o de un comentario para el estudiante."
        crumbs={[
          { label: roleLabel },
          { label: 'Acompañamiento', to: basePath },
          { label: 'Nuevo avance' },
        ]}
      />

      <div className="grid g-2-1">
        <Card title="Datos del seguimiento">
          <form
            onSubmit={(event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              setError(null);
              if (!entrepreneurshipId) {
                setError('Selecciona el emprendimiento.');
                return;
              }
              if (isAdvance && !fasePlanId) {
                setError('Un avance de fase necesita la fase del plan.');
                return;
              }
              if (descripcion.trim().length < 10) {
                setError('Describe el avance con al menos 10 caracteres.');
                return;
              }
              let score: number | undefined;
              if (puntaje.trim()) {
                score = Number(puntaje);
                if (!Number.isFinite(score) || score < 0 || score > 100) {
                  setError('El puntaje debe estar entre 0 y 100.');
                  return;
                }
              }
              create.mutate(
                {
                  emprendimientoId: Number(entrepreneurshipId),
                  tipoSeguimiento: tipo,
                  descripcion: descripcion.trim(),
                  ...(isAdvance ? { fasePlanId: Number(fasePlanId) } : {}),
                  ...(score === undefined ? {} : { puntaje: score }),
                  estadoRevision,
                  fechaSeguimiento: fecha,
                },
                {
                  onSuccess: (tracing) => {
                    showToast('Seguimiento registrado.', 'ok');
                    navigate(`${basePath}/${tracing.id}`);
                  },
                  onError: (caught) => setError(errorMessage(caught)),
                },
              );
            }}
            noValidate
          >
            <SelectField
              label="Emprendimiento"
              required
              value={entrepreneurshipId}
              onChange={(event) => setEntrepreneurshipId(event.target.value)}
              hint={
                user?.rol.nombre === 'Docente'
                  ? 'Solo aparecen los emprendimientos con asignación activa.'
                  : undefined
              }
            >
              <option value="">Selecciona el emprendimiento</option>
              {(entrepreneurships.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.codigo} · {item.nombre}
                </option>
              ))}
            </SelectField>

            <div className="grid g-2">
              <SelectField
                label="Tipo de seguimiento"
                required
                value={tipo}
                onChange={(event) => setTipo(event.target.value)}
                hint="Un comentario no lleva fase."
              >
                {SEGUIMIENTO_TIPOS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </SelectField>
              <TextField
                label="Fecha del seguimiento"
                type="date"
                required
                value={fecha}
                onChange={(event) => setFecha(event.target.value)}
              />
            </div>

            {isAdvance ? (
              <SelectField
                label="Fase del plan"
                required
                value={fasePlanId}
                onChange={(event) => setFasePlanId(event.target.value)}
              >
                <option value="">Selecciona la fase</option>
                {(phases.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.nombre}
                  </option>
                ))}
              </SelectField>
            ) : null}

            <TextAreaField
              label="Descripción"
              required
              rows={5}
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
              hint="Qué se hizo, qué quedó listo y qué falta."
            />

            <div className="grid g-2">
              <TextField
                label="Puntaje"
                type="number"
                min={0}
                max={100}
                value={puntaje}
                onChange={(event) => setPuntaje(event.target.value)}
                hint="Opcional, 0 a 100."
              />
              <SelectField
                label="Estado de revisión"
                value={estadoRevision}
                onChange={(event) => setEstadoRevision(event.target.value)}
              >
                {REVISION_ESTADOS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </SelectField>
            </div>

            {error ? (
              <div className="acceso-error" role="alert">
                {error}
              </div>
            ) : null}

            <div className="form-acciones">
              <Button variant="secundario" onClick={() => navigate(-1)}>
                Cancelar
              </Button>
              <Button type="submit" variant="primario" icon="check" loading={create.isPending}>
                Registrar seguimiento
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Cómo funciona" hint="FR-022">
          <Callout icon="bombilla">
            El avance de fase también se ve en el expediente del emprendimiento y en el
            tablero del administrador. La evidencia se carga desde el detalle, con el mismo
            flujo de adjuntos de tareas y asesorías.
          </Callout>
          <p className="ayuda">
            La API guarda la fecha a mediodía de Bogotá para que no se muestre el día
            anterior. El puntaje es opcional y no altera el porcentaje de avance: ese se
            calcula con las tareas completadas.
          </p>
        </Card>
      </div>
    </>
  );
}
