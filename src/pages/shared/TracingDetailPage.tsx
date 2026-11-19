import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { REVISION_ESTADOS } from '@sgemd/shared';
import { roleKeyOf, type Tracing } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { DefinitionList } from '../../components/DefinitionList.tsx';
import { EvidenceUploader } from '../../components/EvidenceUploader.tsx';
import { SelectField, TextAreaField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDate, formatDateTime } from '../../lib/format.ts';
import { useTracing, useUpdateTracing } from '../../queries/tracing.ts';

interface TracingDetailPageProps {
  roleLabel: string;
  basePath: string;
}

/**
 * Detalle de un avance o comentario.
 *
 * El estudiante solo lee y ve el conteo de evidencias. El autor y el
 * administrador pueden editar la descripción, el estado de revisión, el puntaje
 * y la retroalimentación; la API no permite cambiar el tipo ni el
 * emprendimiento.
 */
export function TracingDetailPage({ roleLabel, basePath }: TracingDetailPageProps) {
  const { id } = useParams();
  const tracingId = Number(id);
  const { user } = useAuth();
  const role = roleKeyOf(user);
  const { showToast } = useToast();
  const tracingQuery = useTracing(Number.isFinite(tracingId) ? tracingId : null);
  const update = useUpdateTracing(tracingId);

  const [descripcion, setDescripcion] = useState('');
  const [puntaje, setPuntaje] = useState('');
  const [estadoRevision, setEstadoRevision] = useState('');
  const [retro, setRetro] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!role) return null;
  const canManage = role === 'docente' || role === 'administrador';

  return (
    <>
      <PageHeader
        title="Detalle del seguimiento"
        sub="Avance de fase o comentario del acompañamiento."
        crumbs={[
          { label: roleLabel },
          { label: 'Seguimiento', to: basePath },
          { label: 'Detalle' },
        ]}
      />

      <QueryGate query={tracingQuery} loadingLabel="Cargando el seguimiento…">
        {(tracing: Tracing) => (
          <div className="grid g-2-1">
            <div className="grid">
              <Card title={tracing.tipo} hint={`${tracing.emprendimiento.codigo} · ${tracing.emprendimiento.nombre}`}>
                <div className="fila-acciones" style={{ gap: 8, marginBottom: 14 }}>
                  <Badge state={tracing.estadoRevision}>{tracing.estadoRevision}</Badge>
                  {tracing.fase ? <Badge tone="linea">{tracing.fase.nombre}</Badge> : null}
                </div>
                <DefinitionList
                  items={[
                    { term: 'Fecha', value: formatDate(tracing.fechaSeguimiento) },
                    {
                      term: 'Autor',
                      value: tracing.autor
                        ? `${tracing.autor.nombres} ${tracing.autor.apellidos}`
                        : 'Autor no disponible',
                    },
                    { term: 'Descripción', value: tracing.descripcion },
                    { term: 'Fase', value: tracing.fase?.nombre ?? 'Comentario sin fase' },
                    { term: 'Puntaje', value: tracing.puntaje === null ? 'Sin puntaje' : `${tracing.puntaje} / 100` },
                    { term: 'Retroalimentación', value: tracing.retroalimentacion ?? '—' },
                    { term: 'Evidencias', value: `${tracing.evidencias} archivos` },
                  ]}
                />
                {tracing.estadoRevision === 'Devuelta' ? (
                  <p className="ayuda">
                    Este registro fue devuelto. Revisa la retroalimentación del docente antes de
                    volver a cargar evidencias.
                  </p>
                ) : null}
              </Card>

              <Card title="Evidencias" hint="La API solo publica el conteo">
                <EvidenceUploader
                  entity="tracing"
                  entityId={tracing.id}
                  count={tracing.evidencias}
                  disabled={!canManage}
                  note={
                    canManage
                      ? 'JPG, PNG o PDF. La evidencia se enlaza al seguimiento y se borra con él.'
                      : 'La API no lista los archivos, solo el conteo; las descargas de evidencias anteriores no están disponibles.'
                  }
                />
              </Card>
            </div>

            <div className="grid">
              {canManage ? (
                <Card title="Editar seguimiento" hint="Autor o admin">
                  <form
                    onSubmit={(event: FormEvent<HTMLFormElement>) => {
                      event.preventDefault();
                      setError(null);
                      const body: Record<string, unknown> = {};
                      if (descripcion.trim()) body.descripcion = descripcion.trim();
                      if (puntaje.trim()) {
                        const value = Number(puntaje);
                        if (!Number.isFinite(value) || value < 0 || value > 100) {
                          setError('El puntaje debe estar entre 0 y 100.');
                          return;
                        }
                        body.puntaje = value;
                      }
                      if (estadoRevision) body.estadoRevision = estadoRevision;
                      if (retro.trim()) body.retroalimentacion = retro.trim();
                      if (Object.keys(body).length === 0) {
                        setError('No hay cambios para guardar.');
                        return;
                      }
                      update.mutate(body, {
                        onSuccess: () => showToast('Seguimiento actualizado.', 'ok'),
                        onError: (caught) => setError(errorMessage(caught)),
                      });
                    }}
                    noValidate
                  >
                    <TextAreaField
                      label="Descripción"
                      rows={4}
                      value={descripcion}
                      onChange={(event) => setDescripcion(event.target.value)}
                      hint={`Actual: ${tracing.descripcion}`}
                    />
                    <div className="grid g-2">
                      <TextField
                        label="Puntaje"
                        type="number"
                        min={0}
                        max={100}
                        value={puntaje}
                        onChange={(event) => setPuntaje(event.target.value)}
                        hint="0 a 100; vacío para no cambiarlo."
                      />
                      <SelectField
                        label="Estado de revisión"
                        value={estadoRevision}
                        onChange={(event) => setEstadoRevision(event.target.value)}
                        hint="Sin selección no se modifica."
                      >
                        <option value="">Sin cambios</option>
                        {REVISION_ESTADOS.map((item) => (
                          <option key={item} value={item}>
                            {item}
                          </option>
                        ))}
                      </SelectField>
                    </div>
                    <TextAreaField
                      label="Retroalimentación"
                      rows={3}
                      value={retro}
                      onChange={(event) => setRetro(event.target.value)}
                    />
                    {error ? (
                      <div className="acceso-error" role="alert">
                        {error}
                      </div>
                    ) : null}
                    <div className="fila-acciones">
                      <Button type="submit" variant="primario" loading={update.isPending}>
                        Guardar cambios
                      </Button>
                      <Link className="btn btn-secundario" to={basePath}>
                        Volver
                      </Link>
                    </div>
                  </form>
                  <p className="nota-foot">
                    Registrado {formatDateTime(tracing.fechaSeguimiento)}. El tipo y el
                    emprendimiento no se editan.
                  </p>
                </Card>
              ) : (
                <Card title="Registro de solo lectura" hint="Estudiante">
                  <p className="ayuda" style={{ marginTop: 0 }}>
                    El seguimiento lo registra el docente asignado. Si necesitas una corrección,
                    responde por la bandeja de asesorías o solicita una cita.
                  </p>
                  <Link className="btn btn-secundario" to="/estudiante/asesorias/solicitar">
                    Solicitar asesoría
                  </Link>
                </Card>
              )}
            </div>
          </div>
        )}
      </QueryGate>
    </>
  );
}
