import { useQuery } from '@tanstack/react-query';
import { apiGet } from './api/client.ts';

interface Health {
  status: string;
  db: 'up' | 'down';
  uptimeSeconds: number;
}

/**
 * Pantalla provisional de la Etapa 1: no es una vista del producto, solo comprueba que
 * la SPA y la API hablan por el mismo origen. Se sustituye en la Etapa 11.
 */
export function App() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<Health>('/health'),
    retry: false,
  });

  return (
    <main className="app-shell">
      <section className="card" aria-labelledby="titulo">
        <h1 id="titulo">SGEMD</h1>
        <p className="app-sub">Esqueleto del MVP — Etapa 1</p>

        {health.isPending && <p role="status">Comprobando la conexión con la API…</p>}

        {health.isError && (
          <p role="alert" className="app-error">
            No fue posible contactar la API. Revisa que el backend esté en marcha.
          </p>
        )}

        {health.data && (
          <dl className="app-status">
            <dt>API</dt>
            <dd>{health.data.status === 'ok' ? 'En línea' : 'Con problemas'}</dd>
            <dt>Base de datos</dt>
            <dd>{health.data.db === 'up' ? 'Conectada' : 'Sin conexión'}</dd>
            <dt>Encendido</dt>
            <dd>{health.data.uptimeSeconds} s</dd>
          </dl>
        )}
      </section>
    </main>
  );
}
