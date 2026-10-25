import { Router } from 'express';
import { rateLimit } from '../../middleware/rateLimit.js';
import { validateBody } from '../../middleware/validate.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import { clearSessionCookie, setSessionCookie } from './session.js';
import {
  forgotPasswordSchema,
  loginSchema,
  registerSchema,
  resendSchema,
  resetPasswordSchema,
  verifySchema,
} from './schemas.js';
import {
  login,
  register,
  requestPasswordReset,
  resendCode,
  resetPassword,
  verifyEmail,
} from './service.js';

export const authRouter = Router();

const emailKey = (req: { body?: unknown }): string => {
  const body = req.body as { correoInstitucional?: unknown } | undefined;
  return typeof body?.correoInstitucional === 'string'
    ? body.correoInstitucional.trim().toLowerCase()
    : '';
};

/**
 * Límites por IP. Los umbrales no están en los requisitos: son la suposición P-12 y se
 * ajustan por entorno. El reenvío de OTP tiene además su propio cooldown (P-11).
 */
const limits = {
  register: rateLimit({ scope: 'register', windowMs: 60 * 60_000, max: 10 }),
  login: rateLimit({ scope: 'login', windowMs: 60_000, max: 10, extraKey: emailKey }),
  verify: rateLimit({ scope: 'otp-verify', windowMs: 60_000, max: 15 }),
  resend: rateLimit({ scope: 'otp-resend', windowMs: 60 * 60_000, max: 10 }),
  forgot: rateLimit({ scope: 'forgot', windowMs: 60 * 60_000, max: 10 }),
  reset: rateLimit({ scope: 'reset', windowMs: 60 * 60_000, max: 10 }),
};

authRouter.post(
  '/auth/register',
  limits.register,
  validateBody(registerSchema),
  asyncHandler(async (req, res) => {
    const user = await register(req.body, req.ip ?? null);
    sendData(res, user, 201);
  }),
);

authRouter.post(
  '/auth/verify',
  limits.verify,
  validateBody(verifySchema),
  asyncHandler(async (req, res) => {
    await verifyEmail(req.body, req.ip ?? null);
    sendMessage(
      res,
      'Correo verificado. Tu cuenta queda pendiente de activación por la coordinación del programa.',
    );
  }),
);

authRouter.post(
  '/auth/resend-code',
  limits.resend,
  validateBody(resendSchema),
  asyncHandler(async (req, res) => {
    await resendCode(req.body);
    sendMessage(
      res,
      'Si la cuenta existe y está pendiente de verificación, enviamos un nuevo código.',
    );
  }),
);

authRouter.post(
  '/auth/login',
  limits.login,
  validateBody(loginSchema),
  asyncHandler(async (req, res) => {
    const result = await login(req.body, req.ip ?? null);
    setSessionCookie(res, result.token);
    // El cuerpo lleva el usuario; el token solo viaja en la cookie HttpOnly.
    sendData(res, { usuario: result.user });
  }),
);

authRouter.post(
  '/auth/logout',
  asyncHandler(async (_req, res) => {
    clearSessionCookie(res);
    sendMessage(res, 'Sesión cerrada.');
  }),
);

authRouter.post(
  '/auth/forgot-password',
  limits.forgot,
  validateBody(forgotPasswordSchema),
  asyncHandler(async (req, res) => {
    await requestPasswordReset(req.body);
    sendMessage(
      res,
      'Si el correo está registrado, enviamos un código para restablecer la contraseña.',
    );
  }),
);

authRouter.post(
  '/auth/reset-password',
  limits.reset,
  validateBody(resetPasswordSchema),
  asyncHandler(async (req, res) => {
    await resetPassword(req.body, req.ip ?? null);
    sendMessage(res, 'Contraseña actualizada. Ya puedes iniciar sesión.');
  }),
);
