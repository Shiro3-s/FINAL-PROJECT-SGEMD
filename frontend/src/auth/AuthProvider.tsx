import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { roleKeyOf, type RoleKey, type SessionUser } from '../api/types.ts';
import { useSessionQuery } from '../queries/session.ts';

interface AuthContextValue {
  user: SessionUser | null;
  role: RoleKey | null;
  /** `true` mientras se resuelve `GET /users/me` por primera vez. */
  isLoading: boolean;
  /** Error de red distinto de «no hay sesión». */
  error: unknown;
  refetch: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Estado de sesión de toda la SPA.
 *
 * No hay estado local de «logueado»: la única fuente es la consulta a
 * `/users/me`, que comparte caché con el resto de TanStack Query. Así, cerrar
 * sesión o expirar la cookie se refleja en las guardas sin sincronizar nada.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const session = useSessionQuery();

  const value = useMemo<AuthContextValue>(
    () => ({
      user: session.data ?? null,
      role: roleKeyOf(session.data),
      isLoading: session.isPending,
      error: session.error,
      refetch: () => {
        void session.refetch();
      },
    }),
    [session.data, session.isPending, session.error, session.refetch],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  }
  return context;
}
