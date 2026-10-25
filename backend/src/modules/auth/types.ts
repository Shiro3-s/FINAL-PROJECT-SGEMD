import type { CuentaEstado } from '@sgemd/shared';

/** Usuario resuelto en cada petición desde la fila de `usuarios` (nunca desde el JWT). */
export interface SessionUser {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional: string;
  numeroDocumento: string;
  nivelAcademico: string | null;
  verificado: boolean;
  estado: CuentaEstado;
  rolId: number;
  rolNombre: string;
  ultimaActividad: Date | null;
}

/** Usuario público: todo lo anterior menos cualquier dato sensible. */
export interface PublicUser {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional: string;
  numeroDocumento: string;
  nivelAcademico: string | null;
  verificado: boolean;
  estado: CuentaEstado;
  rol: { id: number; nombre: string };
  ultimaActividad: string | null;
}

export function toPublicUser(user: SessionUser): PublicUser {
  return {
    id: user.id,
    codigo: user.codigo,
    nombres: user.nombres,
    apellidos: user.apellidos,
    correoInstitucional: user.correoInstitucional,
    numeroDocumento: user.numeroDocumento,
    nivelAcademico: user.nivelAcademico,
    verificado: user.verificado,
    estado: user.estado,
    rol: { id: user.rolId, nombre: user.rolNombre },
    ultimaActividad: user.ultimaActividad ? user.ultimaActividad.toISOString() : null,
  };
}
