import type { SessionUser } from '../modules/auth/types.js';

declare global {
  namespace Express {
    interface Request {
      /** Lo adjunta `requireAuth`; nunca lo escribe el cliente. */
      user?: SessionUser;
    }
  }
}

export {};
