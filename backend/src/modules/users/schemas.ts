import { CUENTA_ESTADOS, NIVELES_ACADEMICOS } from '@sgemd/shared';
import { z } from 'zod';

const nombres = z.string().trim().min(1, 'Los nombres son obligatorios').max(100);
const apellidos = z.string().trim().min(1, 'Los apellidos son obligatorios').max(100);
const correo = z.email('Escribe un correo válido').max(150);
const numeroDocumento = z
  .string()
  .trim()
  .min(3, 'El número de documento es obligatorio')
  .max(30);

/** Id de catálogo: `null` limpia el campo, omitirlo lo deja como está. */
const catalogo = z.number().int().positive().nullable().optional();
const nivelAcademico = z.enum(NIVELES_ACADEMICOS).nullable().optional();

/**
 * Alta de estudiante o docente por el administrador (R33, T06).
 *
 * El código no se envía: lo genera el servidor según el rol (`DOC-###` o 6 dígitos). La
 * contraseña tampoco: la cuenta nace con una clave aleatoria inservible y el usuario
 * establece la suya con el código de invitación que se le envía por correo.
 *
 * El prototipo pide además teléfono, área de conocimiento, sector y emprendimiento; esas
 * columnas no existen en `usuarios` (el emprendimiento es otra entidad, Etapa 5).
 */
export const createUserSchema = z
  .object({
    nombres,
    apellidos,
    numeroDocumento,
    correoInstitucional: correo,
    rolId: z
      .union([z.literal(2), z.literal(3)], {
        message: 'Solo se pueden crear cuentas de estudiante o docente',
      })
      .describe('2 = Estudiante, 3 = Docente'),
    tipoDocumentoId: z.number().int().positive('Selecciona el tipo de documento'),
    nivelAcademico,
    programaAcademicoId: catalogo,
    centroUniversitarioId: catalogo,
    municipioId: catalogo,
    tipoPoblacionId: catalogo,
    tipoUsuarioId: catalogo,
    // El prototipo ofrece Activo y Limitado al crear; Inactivo solo se alcanza después.
    estado: z.enum(['Activo', 'Limitado']).default('Activo'),
  })
  .strict();

/**
 * Edición por el administrador.
 *
 * `rolId`, `estado`, `codigo`, `verificado` y `password` no se editan aquí: el estado
 * tiene sus propios endpoints y el rol es inmutable (P-18).
 */
export const updateUserSchema = z
  .object({
    nombres: nombres.optional(),
    apellidos: apellidos.optional(),
    numeroDocumento: numeroDocumento.optional(),
    correoInstitucional: correo.optional(),
    tipoDocumentoId: z.number().int().positive().optional(),
    nivelAcademico,
    programaAcademicoId: catalogo,
    centroUniversitarioId: catalogo,
    municipioId: catalogo,
    tipoPoblacionId: catalogo,
    tipoUsuarioId: catalogo,
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

/**
 * Edición del propio perfil (FR-024).
 *
 * El correo, el documento, el tipo de documento, el rol y el estado no son editables por
 * el titular: `.strict()` los rechaza con 400.
 */
export const updateMeSchema = z
  .object({
    nombres: nombres.optional(),
    apellidos: apellidos.optional(),
    nivelAcademico,
    programaAcademicoId: catalogo,
    centroUniversitarioId: catalogo,
    municipioId: catalogo,
    tipoPoblacionId: catalogo,
    tipoUsuarioId: catalogo,
  })
  .strict()
  .refine((value) => Object.keys(value).length > 0, {
    message: 'Envía al menos un campo para actualizar',
  });

/** Selector genérico de estado de `admin/usuarios`. La transición la valida la política. */
export const stateSchema = z
  .object({
    estado: z.enum(CUENTA_ESTADOS),
  })
  .strict();

/**
 * Rechazo de la activación (UC-1). El motivo es obligatorio (misma regla que el rechazo
 * de emprendimientos y del acta), pero no se fija una longitud mínima: ningún requisito
 * la define (AQ-06 sigue abierta).
 */
export const rejectSchema = z
  .object({
    motivo: z.string().trim().min(1, 'Escribe el motivo del rechazo').max(500),
  })
  .strict();

/** Filtros y paginación de los listados. `.strict()` impide ordenar por otra columna. */
export const listUsersQuerySchema = z
  .object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(20),
    q: z
      .string()
      .max(100)
      .optional()
      .transform((value) => value?.trim() || undefined),
    rol: z.coerce.number().int().min(1).max(4).optional(),
    estado: z.enum(CUENTA_ESTADOS).optional(),
    sort: z
      .enum(['codigo', 'nombres', 'apellidos', 'correo', 'estado', 'ultimaActividad'])
      .default('apellidos'),
    order: z.enum(['asc', 'desc']).default('asc'),
  })
  .strict();

export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
export type UpdateMeInput = z.infer<typeof updateMeSchema>;
export type StateInput = z.infer<typeof stateSchema>;
export type RejectInput = z.infer<typeof rejectSchema>;
export type ListUsersQuery = z.infer<typeof listUsersQuerySchema>;
