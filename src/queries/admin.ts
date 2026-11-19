import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiDownload, apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type {
  AuditEntry,
  Backup,
  BackupPanel,
  Paginated,
  ReportCatalogItem,
  SettingItem,
} from '../api/types.ts';

/** Administración institucional: reportes, configuración y respaldos (§7.10). */

// --- Reportes ----------------------------------------------------------------

export const reportKeys = {
  all: ['reports'] as const,
  catalog: ['reports', 'catalog'] as const,
};

export function useReportCatalog() {
  return useQuery({
    queryKey: reportKeys.catalog,
    queryFn: async () => {
      const page = await apiGet<{ items: ReportCatalogItem[] }>('/reports');
      return page.items;
    },
  });
}

export interface ExportReportBody {
  id: string;
  format: string;
  desde?: string;
  hasta?: string;
  docenteId?: number;
}

export function useExportReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, format, desde, hasta, docenteId }: ExportReportBody) =>
      apiDownload(
        withQuery(`/reports/${id}/export`, { format, desde, hasta, docenteId }),
        `${id}.${format}`,
      ),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: reportKeys.all }),
  });
}

// --- Configuración -----------------------------------------------------------

export const settingsKeys = {
  all: ['settings'] as const,
  list: ['settings', 'list'] as const,
  audit: (filters: QueryParams) => ['settings', 'audit', filters] as const,
};

export function useSettings() {
  return useQuery({
    queryKey: settingsKeys.list,
    queryFn: async () => {
      const page = await apiGet<{ items: SettingItem[] }>('/settings');
      return page.items;
    },
  });
}

export function useSaveSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (items: { clave: string; valor: string | null }[]) =>
      apiSend<{ cambios: number }>('PUT', '/settings', { items }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: settingsKeys.all }),
  });
}

export interface AuditFilters {
  page?: number;
  pageSize?: number;
  accion?: string;
  entidad?: string;
  q?: string;
  desde?: string;
  hasta?: string;
}

export function useSettingsAudit(filters: AuditFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    accion: filters.accion,
    entidad: filters.entidad,
    q: filters.q,
    desde: filters.desde,
    hasta: filters.hasta,
  };
  return useQuery({
    queryKey: settingsKeys.audit(params),
    queryFn: () => apiGet<Paginated<AuditEntry>>(withQuery('/settings/audit', params)),
  });
}

// --- Respaldos ---------------------------------------------------------------

export const backupKeys = {
  all: ['backups'] as const,
  list: (filters: QueryParams) => ['backups', 'list', filters] as const,
  panel: ['backups', 'panel'] as const,
  detail: (id: number) => ['backups', 'detail', id] as const,
};

export interface BackupFilters {
  page?: number;
  pageSize?: number;
  estado?: string;
  tipo?: string;
  q?: string;
  desde?: string;
  hasta?: string;
}

export function useBackups(filters: BackupFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    estado: filters.estado,
    tipo: filters.tipo,
    q: filters.q,
    desde: filters.desde,
    hasta: filters.hasta,
  };
  return useQuery({
    queryKey: backupKeys.list(params),
    queryFn: () => apiGet<Paginated<Backup>>(withQuery('/backups', params)),
  });
}

export function useBackupPanel() {
  return useQuery({
    queryKey: backupKeys.panel,
    queryFn: () => apiGet<BackupPanel>('/backups/panel'),
  });
}

export interface BackupManifest {
  codigo: string;
  tipo: string;
  motor: string;
  base: string;
  totalBytes: number;
  archivos: unknown[];
}

export interface BackupDetail extends Backup {
  manifiesto: BackupManifest | null;
}

export function useBackup(id: number | null) {
  return useQuery({
    queryKey: backupKeys.detail(id ?? 0),
    queryFn: () => apiGet<BackupDetail>(`/backups/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

export function useCreateBackup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tipo: 'Completo' | 'Parcial') =>
      apiSend<Backup>('POST', '/backups', { tipo }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: backupKeys.all }),
  });
}

export interface VerifyResult {
  estado: string;
  archivos: number;
  corruptos: { ruta: string; motivo: string }[];
}

export function useVerifyBackup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiSend<VerifyResult>('POST', `/backups/${id}/verify`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: backupKeys.all }),
  });
}

export function useDownloadBackup() {
  return useMutation({
    mutationFn: ({ id, part }: { id: number; part: 'dump' | 'storage' }) =>
      apiDownload(
        withQuery(`/backups/${id}/download`, { part }),
        part === 'dump' ? 'respaldo.dump' : 'evidencias.tar.gz',
      ),
  });
}

export function useExportDatabase() {
  return useMutation({
    mutationFn: (format: 'csv' | 'xlsx') =>
      apiDownload(withQuery('/backups/export', { format }), `base-sgemd.${format === 'csv' ? 'zip' : 'xlsx'}`),
  });
}
