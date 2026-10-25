import { z } from 'zod';

const correo = z.email('Escribe un correo válido').max(150);
const codigo = z
  .string()
  .trim()
  .regex(/^\d{8}$/, 'El código debe tener 8 dígitos');
const password = z
  .string()
  .min(8, 'La contraseña debe tener al menos 8 caracteres')
  .max(128, 'La contraseña es demasiado larga');

/**
 * Registro público de estudiante.
 *
 * Solo los campos que el diagrama de clases puede almacenar. El prototipo pide además
 * correo personal y celular, pero `usuarios` no tiene esas columnas (discrepancia #18):
 * no se inventan. `aceptaTratamiento` es obligatorio y hoy **no se persiste** (P-14).
 */
export const registerSchema = z
  .object({
    nombres: z.string().trim().min(1, 'Los nombres son obligatorios').max(100),
    apellidos: z.string().trim().min(1, 'Los apellidos son obligatorios').max(100),
    tipoDocumentoId: z.number().int().positive('Selecciona el tipo de documento'),
    numeroDocumento: z.string().trim().min(3, 'El número de documento es obligatorio').max(30),
    correoInstitucional: correo,
    password,
    aceptaTratamiento: z.literal(true, {
      message: 'Debes autorizar el tratamiento de datos para continuar',
    }),
  })
  .strict();

export const verifySchema = z
  .object({
    correoInstitucional: correo,
    codigo,
  })
  .strict();

export const resendSchema = z
  .object({
    correoInstitucional: correo,
  })
  .strict();

export const loginSchema = z
  .object({
    correoInstitucional: correo,
    password: z.string().min(1, 'Escribe tu contraseña').max(128),
  })
  .strict();

export const forgotPasswordSchema = z
  .object({
    correoInstitucional: correo,
  })
  .strict();

export const resetPasswordSchema = z
  .object({
    correoInstitucional: correo,
    codigo,
    password,
  })
  .strict();

export type RegisterInput = z.infer<typeof registerSchema>;
export type VerifyInput = z.infer<typeof verifySchema>;
export type ResendInput = z.infer<typeof resendSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;
