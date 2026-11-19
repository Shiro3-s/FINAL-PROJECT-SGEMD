import { useState } from 'react';
import { saveDownload } from '../../api/client.ts';
import type { ReportCatalogItem } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { SelectField, TextField } from '../../components/FormField.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { EmptyState, ErrorState, LoadingState, errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useExportReport, useReportCatalog } from '../../queries/admin.ts';
import { useUsers } from '../../queries/users.ts';

/**
 * Reportes institucionales (FR-017).
 *
 * La API publica cuatro reportes con sus formatos y columnas; la vista no
 * inventa ninguno más. El periodo y el filtro por docente se envían al servidor.
 * El reporte de emprendimientos rechaza `desde`/`hasta` (P-44), así que el
 * formulario oculta el periodo cuando ese reporte está elegido.
 */
export function AdminReportsPage() {
  const catalog = useReportCatalog();

  return (
    <>
      <PageHeader
        title="Reportes"
        sub="Exportación de la información del programa en CSV, XLSX o PDF."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Reportes' }]}
      />

      <Callout icon="bombilla">
        Los periodos usan fechas inclusivas. El reporte de emprendimientos no acepta periodo:
        la API lo rechaza (P-44) y el formulario lo oculta.
      </Callout>

      <div className="mt-14">
        {catalog.isPending ? (
          <LoadingState label="Cargando el catálogo de reportes…" />
        ) : catalog.isError ? (
          <ErrorState error={catalog.error} />
        ) : catalog.data.length === 0 ? (
          <EmptyState
            title="No hay reportes disponibles"
            text="El catálogo se configura en el servidor. No se inventan reportes en el cliente."
          />
        ) : (
          <div className="grid g-2">
            {catalog.data.map((report) => (
              <ReportCard key={report.id} report={report} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function ReportCard({ report }: { report: ReportCatalogItem }) {
  const { showToast } = useToast();
  const teachers = useUsers('teachers', { page: 1, pageSize: 100 });
  const exportReport = useExportReport();
  const [format, setFormat] = useState(report.formatos[0] ?? 'csv');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const [docenteId, setDocenteId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const usesPeriod = report.periodo;

  const run = (): void => {
    setError(null);
    if (usesPeriod && desde && hasta && hasta < desde) {
      setError('La fecha final no puede ser anterior a la inicial.');
      return;
    }
    exportReport.mutate(
      {
        id: report.id,
        format,
        ...(usesPeriod ? { desde: desde || undefined, hasta: hasta || undefined } : {}),
        ...(docenteId ? { docenteId: Number(docenteId) } : {}),
      },
      {
        onSuccess: (file) => {
          saveDownload(file);
          showToast(`Reporte «${report.nombre}» generado.`, 'ok');
        },
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  return (
    <Card
      title={report.nombre}
      hint={<Badge tone="linea" icon="download">{report.formatos.join(' · ')}</Badge>}
    >
      <p className="ayuda" style={{ marginTop: 0 }}>
        {report.descripcion}
      </p>

      <DefinitionList
        items={[
          {
            term: 'Periodo',
            value: report.periodo ? 'Acepta rango de fechas' : 'Sin periodo (P-44)',
          },
          {
            term: 'Última generación',
            value: report.ultimaGeneracion
              ? formatDateTime(report.ultimaGeneracion)
              : 'Sin generar',
          },
          {
            term: 'Columnas',
            value: report.columnas.map((column) => column.header).join(' · '),
          },
        ]}
      />

      <div className="grid g-2 mt-14">
        <SelectField
          label="Formato"
          value={format}
          onChange={(event) => setFormat(event.target.value)}
        >
          {report.formatos.map((item) => (
            <option key={item} value={item}>
              {item.toUpperCase()}
            </option>
          ))}
        </SelectField>
        {report.filtroDocente ? (
          <SelectField
            label="Docente"
            value={docenteId}
            onChange={(event) => setDocenteId(event.target.value)}
            placeholder="Todos los docentes"
          >
            {(teachers.data?.items ?? []).map((teacher) => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.nombres} {teacher.apellidos}
              </option>
            ))}
          </SelectField>
        ) : null}
      </div>

      {usesPeriod ? (
        <div className="grid g-2">
          <TextField
            label="Desde"
            type="date"
            value={desde}
            onChange={(event) => setDesde(event.target.value)}
          />
          <TextField
            label="Hasta"
            type="date"
            value={hasta}
            onChange={(event) => setHasta(event.target.value)}
          />
        </div>
      ) : null}

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      <Button
        variant="primario"
        icon="download"
        loading={exportReport.isPending}
        onClick={run}
      >
        Generar y descargar
      </Button>
    </Card>
  );
}
