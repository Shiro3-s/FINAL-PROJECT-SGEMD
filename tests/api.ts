import request from 'supertest';
import type { Response, Test } from 'supertest';
import { expect } from 'vitest';
import { createApp } from '../src/app.js';
import { SESSION_COOKIE } from '../src/modules/auth/session.js';

/**
 * Utilidades compartidas por las suites de integración.
 *
 * La cookie de sesión es `Secure`, así que el jar de supertest no la reenvía por HTTP
 * plano: se extrae de `Set-Cookie` y se manda explícitamente en cada petición.
 */
export const app = createApp();

/** `originCheck` exige mismo origen en toda mutación (§15). */
export const ORIGIN = 'https://localhost';

export const post = (path: string) => request(app).post(path).set('Origin', ORIGIN);
export const put = (path: string) => request(app).put(path).set('Origin', ORIGIN);
export const patch = (path: string) => request(app).patch(path).set('Origin', ORIGIN);
export const del = (path: string) => request(app).delete(path).set('Origin', ORIGIN);

export interface Session {
  /** Valor completo de la cookie (`sgemd_session=…`). */
  cookie: string;
  id: number;
  get: (path: string) => Test;
  post: (path: string) => Test;
  put: (path: string) => Test;
  patch: (path: string) => Test;
  del: (path: string) => Test;
}

export function sessionCookie(response: Response): string {
  const headers = response.headers['set-cookie'] as unknown as string[] | undefined;
  const cookie = headers?.find((value) => value.startsWith(`${SESSION_COOKIE}=`));
  if (!cookie) throw new Error('La respuesta no trae la cookie de sesión');
  return cookie;
}

export async function loginSession(correo: string, password = 'Demo1234'): Promise<Session> {
  const response = await post('/api/auth/login').send({
    correoInstitucional: correo,
    password,
  });

  expect(response.status).toBe(200);

  const cookie = `${SESSION_COOKIE}=${decodeURIComponent(
    sessionCookie(response).split(';')[0]!.slice(SESSION_COOKIE.length + 1),
  )}`;

  const withCookie =
    (method: 'get' | 'post' | 'put' | 'patch' | 'delete') => (path: string) => {
      const test = request(app)[method](path).set('Cookie', cookie);
      return method === 'get' ? test : test.set('Origin', ORIGIN);
    };

  return {
    cookie,
    id: response.body.data.usuario.id as number,
    get: withCookie('get'),
    post: withCookie('post'),
    put: withCookie('put'),
    patch: withCookie('patch'),
    del: withCookie('delete'),
  };
}

/** Sesión de la coordinación sembrada por `database/seed.sql`. */
export function adminSession(): Promise<Session> {
  return loginSession('admin.demo@uniminuto.edu.co');
}
