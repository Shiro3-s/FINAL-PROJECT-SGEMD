import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ApiError, apiGet, apiSend } from '../api/client.ts';
import type { SessionUser } from '../api/types.ts';

/**
 * Sesión de la SPA.
 *
 * La cookie es `HttpOnly`: el cliente NUNCA sabe si existe hasta que
 * `GET /users/me` responde. Un `401` no es un fallo de la vista, es «no hay
 * sesión», y por eso la consulta devuelve `null` en lugar de lanzar.
 */
export const sessionKeys = {
  me: ['session', 'me'] as const,
};

export async function fetchSession(): Promise<SessionUser | null> {
  try {
    return await apiGet<SessionUser>('/users/me');
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

export function useSessionQuery() {
  return useQuery({
    queryKey: sessionKeys.me,
    queryFn: fetchSession,
    // La cookie dura 8 h; no se revalida en cada cambio de foco.
    staleTime: 5 * 60_000,
    retry: false,
  });
}

export interface LoginResponse {
  usuario: SessionUser;
}

export interface LoginBody {
  correoInstitucional: string;
  password: string;
}

/**
 * Inicio de sesión. El `POST` devuelve `{ usuario }` con la misma forma pública
 * de `GET /users/me`; sembramos la caché de inmediato tras limpiar el estado
 * anterior para que `useAuth()` y las guardas de ruta vean al usuario sin
 * depender de que una consulta `refetchQueries` esté montada.
 */
export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: LoginBody) =>
      apiSend<LoginResponse>('POST', '/auth/login', body),
    onSuccess: (data) => {
      // Purga cualquier caché previa y fija inmediatamente la nueva sesión.
      queryClient.clear();
      queryClient.setQueryData(sessionKeys.me, data.usuario);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiSend<unknown>('POST', '/auth/logout'),
    onSettled: () => {
      queryClient.setQueryData(sessionKeys.me, null);
      queryClient.removeQueries({ queryKey: ['notifications'] });
      queryClient.clear();
      queryClient.setQueryData(sessionKeys.me, null);
    },
  });
}
