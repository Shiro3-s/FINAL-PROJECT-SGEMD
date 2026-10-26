import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { Paginated, SessionUser } from '../api/types.ts';
import { sessionKeys } from './session.ts';

/** Consultas y mutaciones de cuentas (`/users`, §7.5, §7.6, §7.7). */

export const userKeys = {
  all: ['users'] as const,
  list: (kind: string, filters: UserFilters) =>
    ['users', kind, filters] as const,
  detail: (id: number) => ['users', 'detail', id] as const,
};

export interface UserFilters {
  page: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  rol?: number;
  sort?: string;
  order?: string;
}

function toParams(filters: UserFilters): QueryParams {
  return {
    page: filters.page,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    rol: filters.rol,
    sort: filters.sort,
    order: filters.order,
  };
}

/** Listado por rol fijo: `/users/students` o `/users/teachers`. */
export function useUsers(kind: 'all' | 'students' | 'teachers', filters: UserFilters) {
  const path = kind === 'all' ? '/users' : `/users/${kind}`;
  return useQuery({
    queryKey: userKeys.list(kind, filters),
    queryFn: () => apiGet<Paginated<SessionUser>>(withQuery(path, toParams(filters))),
  });
}

export function useUser(id: number | null) {
  return useQuery({
    queryKey: userKeys.detail(id ?? 0),
    queryFn: () => apiGet<SessionUser>(`/users/${id}`),
    enabled: id !== null,
  });
}

export interface CreateUserBody {
  nombres: string;
  apellidos: string;
  numeroDocumento: string;
  correoInstitucional: string;
  rolId: number;
  tipoDocumentoId: number;
  nivelAcademico?: string | null;
  programaAcademicoId?: number | null;
  centroUniversitarioId?: number | null;
  municipioId?: number | null;
  tipoPoblacionId?: number | null;
  tipoUsuarioId?: number | null;
  estado?: 'Activo' | 'Limitado';
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateUserBody) => apiSend<SessionUser>('POST', '/users', body),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

export function useUpdateUser(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiSend<SessionUser>('PUT', `/users/${id}`, body),
    onSuccess: (user) => {
      queryClient.setQueryData(userKeys.detail(id), user);
      void queryClient.invalidateQueries({ queryKey: userKeys.all });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/users/${id}`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

/** `PATCH /users/:id/state` respeta la tabla de transiciones del backend. */
export function useChangeUserState() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: 'Activo' | 'Inactivo' }) =>
      apiSend<SessionUser>('PATCH', `/users/${id}/state`, { estado }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

export function useValidateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiSend<SessionUser>('POST', `/users/${id}/validate`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

export function useReactivateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiSend<SessionUser>('POST', `/users/${id}/reactivate`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

export function useRejectUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      apiSend<unknown>('POST', `/users/${id}/reject`, { motivo }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}

/** Edición del propio perfil; refresca la sesión para que el nombre cambie. */
export function useUpdateMe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiSend<SessionUser>('PUT', '/users/me', body),
    onSuccess: (user) => {
      queryClient.setQueryData(sessionKeys.me, user);
    },
  });
}
