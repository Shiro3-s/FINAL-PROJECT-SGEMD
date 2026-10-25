import { SignJWT, jwtVerify } from 'jose';
import type { Response } from 'express';
import { env } from '../../config/env.js';

/** Nombre y vigencia exigidos por el master §15 / NFR-003. */
export const SESSION_COOKIE = 'sgemd_session';
export const SESSION_MAX_AGE_SECONDS = 8 * 60 * 60;

const secret = new TextEncoder().encode(env.JWT_SECRET);

export interface SessionClaims {
  id: number;
  role: number;
}

/** Firma un JWT con **solo** `{ id, role }` (master §15). La expiración es de 8 h. */
export function signSession(claims: SessionClaims): Promise<string> {
  return new SignJWT({ id: claims.id, role: claims.role })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(`${SESSION_MAX_AGE_SECONDS}s`)
    .sign(secret);
}

/** Verifica firma y expiración. Lanza si el token no es válido. */
export async function verifySession(token: string): Promise<SessionClaims> {
  const { payload } = await jwtVerify(token, secret, { algorithms: ['HS256'] });
  const id = payload.id;
  const role = payload.role;

  if (typeof id !== 'number' || typeof role !== 'number') {
    throw new Error('El token no tiene los claims esperados');
  }

  return { id, role };
}

export function setSessionCookie(res: Response, token: string): void {
  res.cookie(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: env.COOKIE_SECURE,
    sameSite: 'strict',
    path: '/',
    maxAge: SESSION_MAX_AGE_SECONDS * 1000,
  });
}

export function clearSessionCookie(res: Response): void {
  res.clearCookie(SESSION_COOKIE, {
    httpOnly: true,
    secure: env.COOKIE_SECURE,
    sameSite: 'strict',
    path: '/',
  });
}
