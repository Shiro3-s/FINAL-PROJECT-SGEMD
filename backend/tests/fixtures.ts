import { resolve } from 'node:path';
import { access } from 'node:fs/promises';
import { expect } from 'vitest';
import { env } from '../src/config/env.js';
import { query } from '../src/db/pool.js';
import { hashPassword } from '../src/utils/password.js';
import { adminSession, loginSession, type Session } from './api.js';
import { uniqueDocument, uniqueEmail } from './helpers.js';

/**
 * Fixtures compartidas por las suites de tareas, seguimientos y evidencias.
 *
 * Crean las cuentas por la API (para ejercitar el alta real) y fijan la contraseña con
 * `hashPassword`, porque una cuenta creada por el administrador nace sin contraseña
 * utilizable. El emprendimiento se aprueba y recibe su acta: sin acta `Aprobada` no hay
 * asignación (BR-001) y sin asignación el docente no ve el expediente.
 */

export interface Account {
  id: number;
  correo: string;
  session: Session;
}

export interface Scenario {
  admin: Session;
  student: Account;
  otherStudent: Account;
  mentor: Account;
  otherMentor: Account;
  emprendimientoId: number;
  assignmentId: number;
}

let sequence = 0;
function label(prefix: string): string {
  sequence += 1;
  return `${prefix}-${Date.now()}-${sequence}`;
}

export async function createAccount(admin: Session, rolId: 2 | 3): Promise<Account> {
  const correo = uniqueEmail(rolId === 3 ? 'doc' : 'est');
  const response = await admin.post('/api/users').send({
    nombres: rolId === 3 ? 'Docente' : 'Estudiante',
    apellidos: label('Evidencia'),
    numeroDocumento: uniqueDocument(),
    correoInstitucional: correo,
    rolId,
    tipoDocumentoId: 1,
  });
  expect(response.status).toBe(201);

  await query('UPDATE usuarios SET password = $2 WHERE correo_institucional = $1', [
    correo,
    await hashPassword('Demo1234'),
  ]);

  return { id: response.body.data.id as number, correo, session: await loginSession(correo) };
}

export async function createEntrepreneurship(
  admin: Session,
  estudianteId: number,
): Promise<number> {
  const response = await admin.post('/api/entrepreneurship').send({
    nombre: label('Proyecto'),
    descripcion: 'Emprendimiento de prueba para tareas y evidencias',
    estudianteId,
    sectorId: 1,
    centroUniversitarioId: 1,
  });
  expect(response.status).toBe(201);

  const id = response.body.data.id as number;
  const approved = await admin.post(`/api/entrepreneurship/${id}/approve`).send({});
  expect(approved.status).toBe(200);

  return id;
}

export async function addApprovedActa(
  emprendimientoId: number,
  estudianteId: number,
): Promise<void> {
  await query(
    `INSERT INTO actas
       (estado, fecha_carga, fecha_revision,
        emprendimiento_id_emprendimiento, usuarios_id_estudiante, usuarios_id_revisor)
     VALUES ('Aprobada', now(), now(), $1, $2, 1)`,
    [emprendimientoId, estudianteId],
  );
}

/**
 * Escenario completo: dos estudiantes (el dueño y un ajeno), dos docentes (el asignado y
 * uno sin vínculo) y un emprendimiento aprobado con acta y asignación activa.
 */
export async function evidenceScenario(): Promise<Scenario> {
  const admin = await adminSession();
  const student = await createAccount(admin, 2);
  const otherStudent = await createAccount(admin, 2);
  const mentor = await createAccount(admin, 3);
  const otherMentor = await createAccount(admin, 3);

  const emprendimientoId = await createEntrepreneurship(admin, student.id);
  await addApprovedActa(emprendimientoId, student.id);

  const assignment = await admin.post('/api/assignments').send({
    mentorId: mentor.id,
    emprendimientoId,
    horasSemanales: 4,
  });
  expect(assignment.status).toBe(201);

  return {
    admin,
    student,
    otherStudent,
    mentor,
    otherMentor,
    emprendimientoId,
    assignmentId: assignment.body.data.id as number,
  };
}

/* -------------------------------------------------------------------------------------
 * Archivos de prueba
 * ----------------------------------------------------------------------------------- */

/** JPEG mínimo: la firma basta para el olfateo de MIME (`FF D8 FF`). */
export function jpegBuffer(size = 256): Buffer {
  const buffer = Buffer.alloc(size, 0x20);
  buffer[0] = 0xff;
  buffer[1] = 0xd8;
  buffer[2] = 0xff;
  buffer[3] = 0xe0;
  return buffer;
}

/** PNG mínimo: firma de 8 bytes. */
export function pngBuffer(size = 256): Buffer {
  const buffer = Buffer.alloc(size, 0x20);
  Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]).copy(buffer, 0);
  return buffer;
}

/** PDF mínimo: `%PDF-`. */
export function pdfBuffer(size = 256): Buffer {
  const buffer = Buffer.alloc(size, 0x20);
  buffer.write('%PDF-1.4\n', 0, 'latin1');
  return buffer;
}

export function uploadEvidence(
  session: Session,
  entity: 'task' | 'tracing',
  parentId: number,
  buffer: Buffer,
  filename = 'evidencia.jpg',
  contentType = 'image/jpeg',
) {
  return session
    .post(`/api/attachments/${entity}/${parentId}`)
    .attach('file', buffer, { filename, contentType });
}

/** Ruta absoluta del archivo guardado, leída de la fila (nunca del nombre original). */
export async function storedPath(attachmentId: number): Promise<string> {
  const { rows } = await query<{ ruta_archivo: string }>(
    'SELECT ruta_archivo FROM adjuntos WHERE id_adjunto = $1',
    [attachmentId],
  );
  return resolve(env.STORAGE_DIR, rows[0]!.ruta_archivo);
}

export async function fileExists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}
