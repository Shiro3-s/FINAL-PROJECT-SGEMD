import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { ASESORIA_ESTADOS } from '@sgemd/shared';
import type { Advice } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDate } from '../../lib/format.ts';
import { useAdvices } from '../../queries/advice.ts';

interface AdviceListPageProps {
  title: string;
  sub: string;
  roleLabel: string;
  basePath: string;
  canCreate: boolean;
  /** El docente usa la etiqueta agrupada «Agendada» del prototipo. */
  groupedFilter?: boolean;
}

/**
 * Lista de asesorías compartida.
 *
 * El estado `Agendada` no existe en la base: es una etiqueta de filtro que el
 * servidor traduce a `Programada + Confirmada + En curso`. El estudiante solo
 * lee; el docente y el administrador confirman y programan.
 */
export function AdviceListPage({
  title,
  sub,
  roleLabel,
  basePath,
  canCreate,
  groupedFilter = false,
}: AdviceListPageProps) {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [estado, setEstado] = useState('');
  const [grupo, setGrupo] = useState('');

  const advices = useAdvices({
    page,
    pageSize: 25,
    q: term,
    estado: grupo ? undefined : estado,
    grupo: grupo === 'Agendada' ? 'Agendada' : undefined,
  });

  return (
    <>
      <PageHeader
        title={title}
        sub={sub}
        crumbs={[{ label: roleLabel }, { label: 'Asesorías' }]}
        actions={
          canCreate ? (
            <Link className="btn btn-primario" to={`${basePath}/nueva`}>
              Nueva asesoría
            </Link>
          ) : (
            <Link className="btn btn-secundario" to={`${basePath}/solicitar`}>
              Solicitar asesoría
            </Link>
          )
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
            <SearchBox value={q} onChange={setQ} placeholder="Buscar por tema, emprendimiento o docente" />
          </form>
          {groupedFilter ? (
            <SelectFilter
              label="Grupo de estado"
              value={grupo}
              onChange={(value) => {
                setGrupo(value);
                setEstado('');
                setPage(1);
              }}
              allLabel="Todos los estados"
            >
              <option value="Agendada">Agendada</option>
            </SelectFilter>
          ) : null}
          <SelectFilter
            label="Estado"
            value={estado}
            onChange={(value) => {
              setEstado(value);
              setGrupo('');
              setPage(1);
            }}
          >
            {ASESORIA_ESTADOS.map((item) => (
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
          query={advices}
          caption="Asesorías"
          unit="asesorías"
          emptyTitle="No hay asesorías con estos filtros"
          emptyText="Prueba con otro estado o consulta de nuevo más tarde."
          onPageChange={setPage}
          rowKey={(advice: Advice) => advice.id}
          columns={[
            {
              key: 'tema',
              header: 'Asesoría',
              render: (advice) => (
                <div>
                  <Link to={`${basePath}/${advice.id}`}>
                    <b>{advice.tema}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {advice.codigo} · {advice.emprendimiento.codigo} {advice.emprendimiento.nombre}
                  </span>
                </div>
              ),
            },
            {
              key: 'estudiante',
              header: 'Estudiante',
              render: (advice) => `${advice.estudiante.nombres} ${advice.estudiante.apellidos}`,
            },
            {
              key: 'docente',
              header: 'Docente',
              render: (advice) =>
                advice.docente
                  ? `${advice.docente.nombres} ${advice.docente.apellidos}`
                  : 'Sin asignar',
            },
            {
              key: 'horario',
              header: 'Horario',
              render: (advice) =>
                advice.fecha ? (
                  <span>
                    {formatDate(`${advice.fecha}T12:00:00`)}
                    <span className="nota-foot" style={{ display: 'block' }}>
                      {advice.horaInicio} a {advice.horaFin}
                    </span>
                  </span>
                ) : (
                  'Por agendar'
                ),
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (advice) => <Badge state={advice.estado}>{advice.estado}</Badge>,
            },
            {
              key: 'acc',
              header: '',
              render: (advice) => (
                <Link className="btn btn-secundario btn-sm" to={`${basePath}/${advice.id}`}>
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
