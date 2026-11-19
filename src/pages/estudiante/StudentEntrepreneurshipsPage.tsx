import { Link, useSearchParams } from 'react-router-dom';
import type { Entrepreneurship } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';

/**
 * Emprendimientos del estudiante.
 *
 * El alcance lo aplica el servidor: solo los propios. El alta no existe para el
 * estudiante (D4); la coordinación la hace. Un emprendimiento paralelo aparece
 * con su marca cuando la solicitud fue aprobada.
 */
export function StudentEntrepreneurshipsPage() {
  /** El buscador global del marco navega aquí con `?q=`. */
  const [params] = useSearchParams();
  const q = params.get('q')?.trim() ?? '';
  const entrepreneurships = useEntrepreneurships({ pageSize: 100, q: q || undefined });

  return (
    <>
      <PageHeader
        title="Mi emprendimiento"
        sub="Tu proyecto y sus emprendimientos paralelos autorizados."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Mi emprendimiento' }]}
        actions={
          <Link className="btn btn-secundario" to="/estudiante/plan">
            Plan de trabajo
          </Link>
        }
      />

      <QueryGate query={entrepreneurships} loadingLabel="Cargando tus emprendimientos…">
        {(data) => (
          <>
            {q ? (
              <Callout icon="search">
                Resultados para «{q}».{' '}
                <Link to="/estudiante/emprendimientos">Limpiar la búsqueda</Link>.
              </Callout>
            ) : null}
            {data.items.length === 0 ? (
              <Card
                title={
                  q
                    ? 'Sin coincidencias en tus emprendimientos'
                    : 'Aún no tienes un emprendimiento registrado'
                }
              >
                {q ? (
                  <p className="ayuda">
                    La búsqueda se aplica a tu propio emprendimiento y a los paralelos
                    autorizados. Prueba con otro término o limpia la búsqueda.
                  </p>
                ) : (
                  <Callout icon="bombilla">
                    El registro lo hace la coordinación del programa (D4). Cuando exista,
                    aparecerá aquí con su código, estado de aprobación y avance.
                  </Callout>
                )}
                <div className="fila-acciones">
                  {q ? (
                    <Link className="btn btn-primario" to="/estudiante/emprendimientos">
                      Limpiar la búsqueda
                    </Link>
                  ) : (
                    <>
                      <Link className="btn btn-primario" to="/estudiante/acta">
                        Cargar mi acta
                      </Link>
                      <Link className="btn btn-secundario" to="/estudiante/perfil">
                        Revisar mi perfil
                      </Link>
                    </>
                  )}
                </div>
              </Card>
            ) : (
              <div className="grid g-2">
                {data.items.map((item: Entrepreneurship) => (
                  <Card
                    key={item.id}
                    title={item.nombre}
                    hint={item.codigo}
                    action={<Badge state={item.estadoAprobacion}>{item.estadoAprobacion}</Badge>}
                  >
                    <DefinitionList
                      items={[
                        { term: 'Etapa', value: item.etapa?.nombre ?? 'Sin etapa' },
                        { term: 'Sector', value: item.sector?.nombre ?? 'Sin sector' },
                        { term: 'Descripción', value: item.descripcion ?? 'Sin descripción.' },
                        {
                          term: 'Avance',
                          value: (
                            <span>
                              {item.avance}%{' '}
                              <ProgressBar value={item.avance} label={`Avance de ${item.nombre}`} />
                            </span>
                          ),
                        },
                      ]}
                    />
                    <div className="fila-acciones">
                      <Link
                        className="btn btn-primario"
                        to={`/estudiante/emprendimientos/${item.id}`}
                      >
                        Abrir expediente
                      </Link>
                      <Link
                        className="btn btn-secundario"
                        to={`/estudiante/emprendimientos/${item.id}/editar`}
                      >
                        Editar datos
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </>
        )}
      </QueryGate>
    </>
  );
}
