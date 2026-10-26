import { useEffect, useState } from 'react';
import type { AuditEntry, SettingItem } from '../../api/types.ts';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { TextField, SelectField } from '../../components/FormField.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { EmptyState, ErrorState, LoadingState, errorMessage } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useSaveSettings, useSettings, useSettingsAudit } from '../../queries/admin.ts';

type Tab = 'parametros' | 'auditoria';

/** Los valores de la bitácora llegan como JSON: se muestran como texto, nunca como objeto. */
function auditValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return '—';
  }
}

/**
 * Nombre visible de cada clave. El servidor solo publica `clave` y
 * `descripcion`; la etiqueta se resuelve aquí para no mostrar snake_case en la
 * interfaz. Si apareciera una clave nueva, se cae a la descripción.
 */
const ETIQUETAS: Record<string, string> = {
  carga_max_horas: 'Carga máxima por docente (horas)',
  max_emprendimientos_docente: 'Emprendimientos máximos por docente',
  cupos_por_sede: 'Cupos por sede',
  paralelos_maximos: 'Emprendimientos paralelos permitidos',
  upload_max_mb: 'Tamaño máximo por archivo (MB)',
  upload_max_files_per_entity: 'Archivos por entidad',
  sede_por_defecto: 'Sede por defecto',
  etapa_inicial: 'Etapa inicial del programa',
  fecha_cierre_admisiones: 'Fecha de cierre de admisiones',
  correos_dominios_permitidos: 'Dominios de correo permitidos',
  inactividad_dias: 'Días de inactividad para pasar a Inactivo',
  rubrica_diagnostico_aprobada: 'Rúbrica de diagnóstico aprobada',
  checklist_activacion_aprobado: 'Checklist de activación aprobado',
  acta_plazo_revision_dias: 'Plazo de revisión del acta (días)',
  backup_retention_days: 'Retención de respaldos (días)',
  notif_tareas: 'Notificar tareas',
  notif_asesorias: 'Notificar asesorías',
  notif_seguimiento: 'Notificar seguimiento',
};

function labelOf(item: SettingItem): string {
  return ETIQUETAS[item.clave] ?? item.descripcion ?? item.clave;
}

const GRUPOS: { titulo: string; claves: string[] }[] = [
  {
    titulo: 'Topes y capacidad',
    claves: [
      'carga_max_horas',
      'max_emprendimientos_docente',
      'cupos_por_sede',
      'paralelos_maximos',
      'upload_max_mb',
      'upload_max_files_per_entity',
    ],
  },
  {
    titulo: 'Programa y admisiones',
    claves: [
      'sede_por_defecto',
      'etapa_inicial',
      'fecha_cierre_admisiones',
      'correos_dominios_permitidos',
      'inactividad_dias',
    ],
  },
  {
    titulo: 'Diagnóstico y activación',
    claves: ['rubrica_diagnostico_aprobada', 'checklist_activacion_aprobado', 'acta_plazo_revision_dias'],
  },
  { titulo: 'Respaldos', claves: ['backup_retention_days'] },
  {
    titulo: 'Notificaciones globales',
    claves: ['notif_tareas', 'notif_asesorias', 'notif_seguimiento'],
  },
];

/**
 * Configuración del programa y bitácora de cambios (FR-019, D22).
 *
 * Las 18 claves viven en `configuracion_programa`; la vista no crea ninguna.
 * Los tres `notif_*` son banderas globales del programa (P-31), no preferencias
 * por usuario. La bitácora es la que el servidor expone en
 * `/settings/audit`; solo se muestra, no se edita.
 */
export function AdminSettingsPage() {
  const [tab, setTab] = useState<Tab>('parametros');

  return (
    <>
      <PageHeader
        title="Configuración"
        sub="Parámetros del programa y bitácora de los cambios aplicados."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Configuración' }]}
      />
      <Tabs
        label="Secciones de configuración"
        active={tab}
        onChange={(value) => setTab(value as Tab)}
        items={[
          { id: 'parametros', label: 'Parámetros' },
          { id: 'auditoria', label: 'Bitácora' },
        ]}
      />
      <TabPanel id="parametros" active={tab}>
        <SettingsForm />
      </TabPanel>
      <TabPanel id="auditoria" active={tab}>
        <AuditTable />
      </TabPanel>
    </>
  );
}

function SettingsForm() {
  const { showToast } = useToast();
  const settings = useSettings();
  const save = useSaveSettings();
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const items = settings.data ?? [];

  useEffect(() => {
    if (!settings.data) return;
    const next: Record<string, string> = {};
    for (const item of settings.data) next[item.clave] = item.valor ?? '';
    setDraft(next);
  }, [settings.data]);

  if (settings.isPending) return <LoadingState label="Cargando la configuración…" />;
  if (settings.isError) return <ErrorState error={settings.error} />;
  if (items.length === 0) {
    return (
      <EmptyState
        title="No hay claves de configuración"
        text="El servidor no devolvió parámetros. No se inventan claves en el cliente."
      />
    );
  }

  const changed = items.filter((item) => (draft[item.clave] ?? '') !== (item.valor ?? ''));

  const submit = (): void => {
    setError(null);
    if (changed.length === 0) {
      showToast('No hay cambios por guardar.', 'ok');
      return;
    }
    save.mutate(
      changed.map((item) => ({
        clave: item.clave,
        valor: draft[item.clave] === '' ? null : draft[item.clave],
      })),
      {
        onSuccess: (result) => {
          showToast(`${result.cambios} cambios guardados.`, 'ok');
        },
        onError: (caught) => setError(errorMessage(caught)),
      },
    );
  };

  return (
    <>
      <Callout icon="escudo">
        La validación por tipo la aplica el servidor: enteros, booleanos, texto y fechas. Los
        tres <code>notif_*</code> son banderas <b>globales del programa</b>: si se apagan, se
        deja de avisar a todos los usuarios de ese tipo (P-31).
      </Callout>

      <div className="grid mt-14">
        {GRUPOS.map((grupo) => {
          const propias = items.filter((item) => grupo.claves.includes(item.clave));
          if (propias.length === 0) return null;
          return (
            <Card key={grupo.titulo} title={grupo.titulo}>
              <div className="grid g-2">
                {propias.map((item) => (
                  <SettingField
                    key={item.clave}
                    item={item}
                    value={draft[item.clave] ?? ''}
                    onChange={(value) =>
                      setDraft((current) => ({ ...current, [item.clave]: value }))
                    }
                    changed={(draft[item.clave] ?? '') !== (item.valor ?? '')}
                  />
                ))}
              </div>
            </Card>
          );
        })}
      </div>

      {error ? (
        <div className="acceso-error" role="alert">
          {error}
        </div>
      ) : null}

      <div className="form-acciones mt-14">
        <Button
          variant="secundario"
          onClick={() => {
            const next: Record<string, string> = {};
            for (const item of items) next[item.clave] = item.valor ?? '';
            setDraft(next);
            setError(null);
          }}
        >
          Descartar cambios
        </Button>
        <Button
          variant="primario"
          icon="check"
          loading={save.isPending}
          disabled={changed.length === 0}
          onClick={submit}
        >
          Guardar {changed.length > 0 ? `(${changed.length})` : ''}
        </Button>
      </div>
    </>
  );
}

function SettingField({
  item,
  value,
  changed,
  onChange,
}: {
  item: SettingItem;
  value: string;
  changed: boolean;
  onChange: (value: string) => void;
}) {
  if (item.tipoDato === 'bool') {
    return (
      <SelectField
        label={labelOf(item)}
        value={value === 'false' ? 'false' : 'true'}
        onChange={(event) => onChange(event.target.value)}
        hint={changed ? `Sin guardar · ${item.descripcion}` : item.descripcion}
      >
        <option value="true">Activo</option>
        <option value="false">Inactivo</option>
      </SelectField>
    );
  }

  return (
    <TextField
      label={labelOf(item)}
      type={item.tipoDato === 'int' ? 'number' : item.tipoDato === 'date' ? 'date' : 'text'}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      hint={
        changed
          ? `Sin guardar · ${item.descripcion}`
          : item.descripcion
      }
    />
  );
}

function AuditTable() {
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [accion, setAccion] = useState('');
  const [entidad, setEntidad] = useState('');
  const audit = useSettingsAudit({ page, pageSize: 25, q: term, accion, entidad });

  return (
    <Card flush>
      <Toolbar>
        <form
          className="crece"
          role="search"
          onSubmit={(event) => {
            event.preventDefault();
            setTerm(q.trim());
            setPage(1);
          }}
        >
          <SearchBox value={q} onChange={setQ} placeholder="Buscar por actor, acción o valor" />
        </form>
        <TextField
          label="Acción"
          value={accion}
          onChange={(event) => {
            setAccion(event.target.value);
            setPage(1);
          }}
          placeholder="Configuración actualizada"
        />
        <SelectFilter
          label="Entidad"
          value={entidad}
          onChange={(value) => {
            setEntidad(value);
            setPage(1);
          }}
          allLabel="Todas"
        >
          <option value="configuracion_programa">configuracion_programa</option>
        </SelectFilter>
        <Button variant="secundario" icon="filter" onClick={() => setPage(1)}>
          Aplicar
        </Button>
      </Toolbar>

      <ListTable
        query={audit}
        caption="Bitácora de configuración"
        unit="cambios"
        emptyTitle="Sin cambios registrados"
        emptyText="Cuando se guarde un parámetro, el cambio quedará en esta bitácora."
        onPageChange={setPage}
        rowKey={(entry: AuditEntry) => entry.id}
        columns={[
          {
            key: 'accion',
            header: 'Acción',
            render: (entry) => (
              <div>
                <b>{entry.accion}</b>
                <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                  {entry.entidad}
                  {entry.entidadId === null ? '' : ` #${entry.entidadId}`}
                </span>
              </div>
            ),
          },
          {
            key: 'cambio',
            header: 'Cambio',
            render: (entry) => (
              <div>
                <span className="nota-foot" style={{ margin: 0 }}>
                  Antes: {auditValue(entry.valorAnterior)}
                </span>
                <span className="nota-foot" style={{ display: 'block' }}>
                  Después: {auditValue(entry.valorNuevo)}
                </span>
              </div>
            ),
          },
          {
            key: 'actor',
            header: 'Actor',
            render: (entry) =>
              entry.actor ? `${entry.actor.nombres} ${entry.actor.apellidos}` : '—',
          },
          { key: 'fecha', header: 'Fecha', render: (entry) => formatDateTime(entry.fecha) },
          { key: 'ip', header: 'IP', render: (entry) => entry.ip ?? '—' },
        ]}
      />
    </Card>
  );
}
