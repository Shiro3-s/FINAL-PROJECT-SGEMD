import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { createPortal } from 'react-dom';
import { Icon, type IconName } from './Icon.tsx';

type ToastTone = 'ok' | 'error' | 'info';

interface ToastItem {
  id: number;
  message: string;
  tone: ToastTone;
  leaving: boolean;
}

interface ToastApi {
  /** Muestra un aviso efímero; sustituye a los `alert()` del prototipo. */
  showToast: (message: string, tone?: ToastTone) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

const ICON_BY_TONE: Record<ToastTone, IconName> = {
  ok: 'check',
  error: 'alerta',
  info: 'bombilla',
};

/**
 * Pila de avisos. Los mensajes de éxito y error del sistema salen por aquí:
 * nunca se usa `window.alert`, que bloquea y no es accesible.
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const nextId = useRef(1);

  const showToast = useCallback((message: string, tone: ToastTone = 'info') => {
    const id = nextId.current++;
    setItems((current) => [...current, { id, message, tone, leaving: false }]);
    window.setTimeout(() => {
      setItems((current) =>
        current.map((item) => (item.id === id ? { ...item, leaving: true } : item)),
      );
    }, 3200);
    window.setTimeout(() => {
      setItems((current) => current.filter((item) => item.id !== id));
    }, 3700);
  }, []);

  const api = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      {items.length > 0
        ? createPortal(
            <div className="toast-pila" role="status" aria-live="polite">
              {items.map((item) => (
                <div
                  key={item.id}
                  className={`toast t-${item.tone}${item.leaving ? ' va-fuera' : ''}`}
                >
                  <Icon name={ICON_BY_TONE[item.tone]} size={16} />
                  <span>{item.message}</span>
                </div>
              ))}
            </div>,
            document.body,
          )
        : null}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast debe usarse dentro de <ToastProvider>');
  }
  return context;
}
