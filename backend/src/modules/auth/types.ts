import type { CuentaEstado } from '@sgemd/shared';

/** Usuario resuelto en cada petición desde la fila de `usuarios` (nunca desde el JWT). */
export interface SessionUser {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional: string;
  numeroDocumento: string;
  /** Catálogos del diagrama de clases: se devuelven como ids, no como objetos. */
  tipoDocumentoId: number;
  nivelAcademico: string | null;
  programaAcademicoId: number | null;
  centroUniversitarioId: number | null;
  municipioId: number | null;
  tipoPoblacionId: number | null;
  tipoUsuarioId: number | null;
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
  tipoDocumentoId: number;
  nivelAcademico: string | null;
  programaAcademicoId: number | null;
  centroUniversitarioId: number | null;
  municipioId: number | null;
  tipoPoblacionId: number | null;
  tipoUsuarioId: number | null;
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
    tipoDocumentoId: user.tipoDocumentoId,
    nivelAcademico: user.nivelAcademico,
    programaAcademicoId: user.programaAcademicoId,
    centroUniversitarioId: user.centroUniversitarioId,
    municipioId: user.municipioId,
    tipoPoblacionId: user.tipoPoblacionId,
    tipoUsuarioId: user.tipoUsuarioId,
    verificado: user.verificado,
    estado: user.estado,
    rol: { id: user.rolId, nombre: user.rolNombre },
    ultimaActividad: user.ultimaActividad ? user.ultimaActividad.toISOString() : null,
  };
}
