import type {
  DownloadedFile,
  NotificationEventPayload,
} from './types.ts';

/**
 * Cliente de la API.
 *
 * Reglas que no se rompen aquí:
 * - La credencial es la cookie `sgemd_session`; este módulo nunca la lee ni la guarda.
 * - La envoltura `{ success, data }` se desarma en un solo sitio y el error se
 *   convierte en `ApiError` con su código estable (`docs/api.md` §Códigos).
 * - Las descargas y subidas no pasan por `fetch`/JSON: son binarias y necesitan
 *   progreso o nombre de archivo.
 */

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: { code: string; message: string; fields?: Record<string, string> };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields?: Record<string, string>;

  constructor(
    status: number,
    code: string,
    message: string,
    fields?: Record<string, string>,
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

function toApiError(status: number, body: ApiEnvelope<unknown> | null): ApiError {
  const error = body?.error;
  return new ApiError(
    status,
    error?.code ?? 'HTTP_ERROR',
    error?.message ?? 'No fue posible completar la solicitud.',
    error?.fields,
  );
}

function isJsonBody(body: BodyInit | null | undefined): boolean {
  return typeof body === 'string';
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    signal,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      ...(isJsonBody(init.body) ? { 'Content-Type': 'application/json' } : {}),
      ...init.headers,
    },
  });

  const body = (await response.json().catch(() => null)) as ApiEnvelope<T> | null;

  if (!response.ok || !body || body.success !== true) {
    throw toApiError(response.status, body);
  }

  // Algunas rutas responden solo `{ success, message }` (logout, marcar leídas).
  return body.data as T;
}

/** Parámetros de consulta; omite `undefined`, `null` y cadenas vacías. */
export type QueryParams = Record<string, string | number | boolean | null | undefined>;

export function withQuery(path: string, params?: QueryParams): string {
  if (!params) return path;
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return request<T>(path, { method: 'GET' }, signal);
}

export function apiSend<T>(
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  path: string,
  body?: unknown,
): Promise<T> {
  return request<T>(path, {
    method,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
}

/**
 * Subida de una evidencia (`multipart/form-data`, campo `file`).
 *
 * Se usa `XMLHttpRequest` y no `fetch` porque solo XHR informa el progreso, y una
 * evidencia puede pesar cientos de MB (D1). El error de la API llega igual como
 * `ApiError`, con su código y sus campos.
 */
export function apiUpload<T>(
  path: string,
  file: File,
  options: { onProgress?: (percent: number) => void; signal?: AbortSignal } = {},
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const form = new FormData();
    form.append('file', file, file.name);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api${path}`);
    xhr.responseType = 'text';
    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');

    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable || !options.onProgress) return;
      options.onProgress(Math.round((event.loaded / event.total) * 100));
    };

    const abort = (): void => xhr.abort();
    options.signal?.addEventListener('abort', abort, { once: true });

    const cleanup = (): void => {
      options.signal?.removeEventListener('abort', abort);
    };

    xhr.onerror = () => {
      cleanup();
      reject(new ApiError(0, 'NETWORK_ERROR', 'No fue posible subir el archivo.'));
    };

    xhr.onabort = () => {
      cleanup();
      reject(new ApiError(0, 'ABORTED', 'La subida se canceló.'));
    };

    xhr.onload = () => {
      cleanup();
      const body = parseJson(xhr.responseText);
      if (xhr.status >= 200 && xhr.status < 300 && body?.success === true) {
        resolve(body.data as T);
        return;
      }
      reject(toApiError(xhr.status, body));
    };

    xhr.send(form);
  });
}

function parseJson(text: string): ApiEnvelope<unknown> | null {
  try {
    return JSON.parse(text) as ApiEnvelope<unknown>;
  } catch {
    return null;
  }
}

/** Nombre del archivo según `Content-Disposition`, con `filename*` preferente. */
function filenameFrom(header: string | null, fallback: string): string {
  if (!header) return fallback;
  const utf8 = /filename\*=UTF-8''([^;]+)/i.exec(header);
  if (utf8?.[1]) {
    try {
      return decodeURIComponent(utf8[1].trim());
    } catch {
      return utf8[1].trim();
    }
  }
  const plain = /filename="?([^";]+)"?/i.exec(header);
  return plain?.[1]?.trim() || fallback;
}

/**
 * Descarga binaria (reportes, respaldos, exportaciones, evidencias).
 *
 * El servidor decide el nombre; si no lo envía, se usa el que propone la vista.
 */
export async function apiDownload(
  path: string,
  fallbackFilename = 'descarga',
): Promise<DownloadedFile> {
  const response = await fetch(`/api${path}`, {
    credentials: 'same-origin',
    headers: { Accept: '*/*' },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiEnvelope<unknown> | null;
    throw toApiError(response.status, body);
  }

  return {
    blob: await response.blob(),
    filename: filenameFrom(response.headers.get('Content-Disposition'), fallbackFilename),
  };
}

/** Entrega el archivo al navegador sin sacarlo del dominio de la aplicación. */
export function saveDownload(file: DownloadedFile): void {
  const url = URL.createObjectURL(file.blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = file.filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  // El objeto se libera en el siguiente ciclo para no cortar la descarga.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export interface NotificationStreamHandlers {
  onReady?: (unreadCount: number) => void;
  onNotification?: (event: NotificationEventPayload) => void;
  /** Se llama cuando el navegador pierde el flujo; EventSource reintenta solo. */
  onError?: () => void;
}

/**
 * Canal en tiempo real (SSE).
 *
 * El evento `ready` trae el contador inicial y cada `notification` solo el id, el
 * tipo y el contador (T21). El cliente no pide el texto por el flujo: invalida la
 * bandeja y la consulta normal trae el mensaje ya saneado.
 */
export function subscribeToNotifications(
  handlers: NotificationStreamHandlers,
): () => void {
  const source = new EventSource('/api/notifications/stream', { withCredentials: true });

  source.addEventListener('ready', (event) => {
    const payload = parseJson((event as MessageEvent<string>).data) as
      | { unreadCount?: number }
      | null;
    handlers.onReady?.(payload?.unreadCount ?? 0);
  });

  source.addEventListener('notification', (event) => {
    const payload = parseJson((event as MessageEvent<string>).data) as
      | NotificationEventPayload
      | null;
    if (payload) handlers.onNotification?.(payload);
  });

  source.addEventListener('error', () => {
    handlers.onError?.();
  });

  return () => source.close();
}
