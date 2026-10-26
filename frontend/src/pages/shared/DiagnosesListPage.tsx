import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { DIAGNOSTICO_ESTADOS } from '@sgemd/shared';
import type { Diagnosis } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDate } from '../../lib/format.ts';
import { useDiagnoses } from '../../queries/diagnosis.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';

interface DiagnosesListPageProps {
  roleLabel: string;
  /** Prefijo del rol: `/docente` o `/admin`. */
  basePath: string;
}

/**
 * Bandeja de diagnósticos (docente y administrador).
 *
 * El alcance lo aplica el servidor: el docente solo ve los de sus asignaciones
 * activas y el administrador, todos. La API no tiene una acción para marcar el
 * diagnóstico como revisado, así que la vista es de solo lectura: abre el
 * detalle con las respuestas y el informe JSON.
 */
export function DiagnosesListPage({ roleLabel, basePath }: DiagnosesListPageProps) {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [estado, setEstado] = useState('');
  const [emprendimientoId, setEmprendimientoId] = useState('');
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });

  const list = useDiagnoses({
    page,
    pageSize: 25,
    q: term,
    estado,
    emprendimientoId: emprendimientoId ? Number(emprendimientoId) : undefined,
  });

  return (
    <>
      <PageHeader
        title="Diagnósticos"
        sub="Caracterización de los emprendimientos. Sin rúbrica aprobada no se produce puntaje (AQ-09)."
        crumbs={[{ label: roleLabel }, { label: 'Diagnósticos' }]}
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
            <SearchBox
              value={q}
              onChange={setQ}
              placeholder="Buscar por emprendimiento o estudiante"
            />
          </form>
          <SelectFilter
            label="Emprendimiento"
            value={emprendimientoId}
            onChange={(value) => {
              setEmprendimientoId(value);
              setPage(1);
            }}
          >
            {(entrepreneurships.data?.items ?? []).map((item) => (
              <option key={item.id} value={item.id}>
                {item.codigo} — {item.nombre}
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
          >
            {DIAGNOSTICO_ESTADOS.map((item) => (
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
          caption="Diagnósticos"
          unit="diagnósticos"
          emptyTitle="No hay diagnósticos para mostrar"
          emptyText="Cuando un estudiante responda el cuestionario aparecerá en esta bandeja."
          onPageChange={setPage}
          rowKey={(item: Diagnosis) => item.id}
          columns={[
            {
              key: 'emprendimiento',
              header: 'Emprendimiento',
              render: (item) => (
                <div>
                  <Link to={`${basePath}/${item.id}`}>
                    <b>{item.emprendimiento.nombre}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {item.emprendimiento.codigo}
                  </span>
                </div>
              ),
            },
            {
              key: 'estudiante',
              header: 'Estudiante',
              render: (item) => `${item.estudiante.nombres} ${item.estudiante.apellidos}`,
            },
            {
              key: 'avance',
              header: 'Respuestas',
              render: (item) => `${item.respondidas} de ${item.totalPreguntas}`,
            },
            {
              key: 'fecha',
              header: 'Última actualización',
              render: (item) => formatDate(item.fechaDiagnostico),
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (item) => <Badge state={item.estado}>{item.estado}</Badge>,
            },
            {
              key: 'puntaje',
              header: 'Puntaje',
              render: (item) =>
                item.puntajeTotal === null ? (
                  <span className="nota-foot" style={{ margin: 0 }}>
                    Sin puntaje (AQ-09)
                  </span>
                ) : (
                  String(item.puntajeTotal)
                ),
            },
            {
              key: 'acc',
              header: '',
              render: (item) => (
                <Link className="btn btn-secundario btn-sm" to={`${basePath}/${item.id}`}>
                  Ver detalle
                </Link>
              ),
            },
          ]}
        />
      </Card>
    </>
  );
}
