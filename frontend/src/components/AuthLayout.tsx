import type { ReactNode } from 'react';
import { Icon } from './Icon.tsx';

/**
 * Marco de las cuatro pantallas públicas.
 *
 * El panel navy desaparece por debajo de 1024 px; entonces la marca pasa al
 * panel blanco como barra compacta, exactamente como en el prototipo. En
 * escritorio el logo aparece una sola vez (panel izquierdo).
 */
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="auth">
      <aside className="auth-izq">
        <div>
          <span className="accede-logo">
            <img
              src="/brand/logo-blanco.png"
              width={600}
              height={286}
              decoding="async"
              alt="SGEMD, Emprendimiento Minuto de Dios"
            />
          </span>
        </div>
        <div>
          <h2 className="auth-titulo">Gestión de clases de emprendimiento</h2>
          <p className="auth-sub">
            Un solo lugar para diagnosticar, planificar, dar seguimiento y medir el avance
            de tu emprendimiento.
          </p>
          <ul className="auth-lista">
            <li>
              <Icon name="clipboard" size={16} />
              <span>Diagnóstico inicial y plan de trabajo por fases</span>
            </li>
            <li>
              <Icon name="trend" size={16} />
              <span>Seguimiento y tareas con evidencia adjunta</span>
            </li>
            <li>
              <Icon name="chat" size={16} />
              <span>Asesorías académicas y eventos de la institución</span>
            </li>
          </ul>
        </div>
        <p className="auth-pie">Institución Minuto de Dios · SGEMD</p>
      </aside>
      <main className="auth-panel">
        <div>
          <div
            className="auth-marca"
            role="img"
            aria-label="SGEMD, Emprendimiento Minuto de Dios"
          />
          {children}
        </div>
      </main>
    </div>
  );
}
