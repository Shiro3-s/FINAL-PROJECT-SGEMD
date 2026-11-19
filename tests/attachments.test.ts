import { rm } from 'node:fs/promises';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import {
  evidenceScenario,
  fileExists,
  jpegBuffer,
  pdfBuffer,
  pngBuffer,
  storedPath,
  uploadEvidence,
  type Scenario,
} from './fixtures.js';
import { clearMailbox } from './helpers.js';

beforeEach(async () => {
  resetRateLimits();
  await clearMailbox();
  await query(`UPDATE configuracion_programa SET valor = '500' WHERE clave = 'upload_max_mb'`);
  await query(
    `UPDATE configuracion_programa SET valor = '5' WHERE clave = 'upload_max_files_per_entity'`,
  );
});

afterAll(async () => {
  await query(`UPDATE configuracion_programa SET valor = '500' WHERE clave = 'upload_max_mb'`);
  await query(
    `UPDATE configuracion_programa SET valor = '5' WHERE clave = 'upload_max_files_per_entity'`,
  );
  await closePool();
});

async function taskFor(scenario: Scenario): Promise<number> {
  const created = await scenario.mentor.session.post('/api/task').send({
    titulo: 'Tarea con evidencia',
    emprendimientoId: scenario.emprendimientoId,
    prioridad: 'Media',
  });
  return created.body.data.id as number;
}

/* =====================================================================================
 * T19 — validación de la subida
 * =================================================================================== */

describe('T19 · validación de la subida', () => {
  it('acepta JPG, PNG y PDF y olfatea el MIME por contenido', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    const jpeg = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
      'punto-de-venta.jpg',
    );
    expect(jpeg.status).toBe(201);
    expect(jpeg.body.data).toMatchObject({
      nombreArchivo: 'punto-de-venta.jpg',
      tipoMime: 'image/jpeg',
      entidad: 'task',
      entidadId: taskId,
      subidoPor: { id: scenario.student.id },
    });

    // El cliente declara GIF y una extensión .jpg, pero el contenido es PNG: manda el
    // contenido, no la cabecera declarada ni el nombre.
    const disguised = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      pngBuffer(),
      'disfrazado.jpg',
      'image/gif',
    );
    expect(disguised.status).toBe(201);
    expect(disguised.body.data.tipoMime).toBe('image/png');

    const pdf = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      pdfBuffer(),
      'lienzo.pdf',
      'application/pdf',
    );
    expect(pdf.status).toBe(201);
    expect(pdf.body.data.tipoMime).toBe('application/pdf');
  });

  it('genera nombres de almacenamiento únicos aunque el nombre original se repita', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    const first = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
      'evidencia.jpg',
    );
    const second = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
      'evidencia.jpg',
    );

    expect(first.status).toBe(201);
    expect(second.status).toBe(201);

    const firstPath = await storedPath(first.body.data.id as number);
    const secondPath = await storedPath(second.body.data.id as number);

    expect(firstPath).not.toBe(secondPath);
    expect(firstPath.endsWith('.jpg')).toBe(true);
    expect(firstPath).not.toContain('evidencia.jpg');
    expect(firstPath).not.toContain('.part');
  });

  it('rechaza un archivo que supera el máximo configurado', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    await query(`UPDATE configuracion_programa SET valor = '1' WHERE clave = 'upload_max_mb'`);

    const response = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(1.5 * 1024 * 1024),
    );

    expect(response.status).toBe(413);
    expect(response.body.error.code).toBe('PAYLOAD_TOO_LARGE');
    expect(response.body.error.fields.file).toContain('1 MB');
  });

  it('rechaza contenido que no es JPG, PNG ni PDF', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    const gif = Buffer.concat([Buffer.from('GIF89a', 'latin1'), Buffer.alloc(64, 0)]);
    const response = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      gif,
      'animacion.gif',
      'image/gif',
    );

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('bloquea un nombre con travesía de rutas', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    // El cliente HTTP normaliza el nombre, así que se envía el multipart a mano para que
    // el servidor vea la travesía tal cual y la rechace (T19).
    const boundary = '----sgemd-travesia';
    const body = Buffer.concat([
      Buffer.from(`--${boundary}\r\n`),
      Buffer.from(
        'Content-Disposition: form-data; name="file"; filename="../../etc/passwd.jpg"\r\n',
      ),
      Buffer.from('Content-Type: image/jpeg\r\n\r\n'),
      jpegBuffer(),
      Buffer.from(`\r\n--${boundary}--\r\n`),
    ]);

    const response = await scenario.student.session
      .post(`/api/attachments/task/${taskId}`)
      .set('Content-Type', `multipart/form-data; boundary=${boundary}`)
      .send(body);

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('aplica el tope de archivos por entidad', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    await query(
      `UPDATE configuracion_programa SET valor = '2' WHERE clave = 'upload_max_files_per_entity'`,
    );

    expect((await uploadEvidence(scenario.student.session, 'task', taskId, jpegBuffer())).status).toBe(
      201,
    );
    expect((await uploadEvidence(scenario.student.session, 'task', taskId, jpegBuffer())).status).toBe(
      201,
    );

    const third = await uploadEvidence(scenario.student.session, 'task', taskId, jpegBuffer());
    expect(third.status).toBe(422);
    expect(third.body.error.code).toBe('ATTACHMENT_LIMIT_REACHED');
  });

  it('exige un archivo y una entidad admitida', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    const empty = await scenario.student.session
      .post(`/api/attachments/task/${taskId}`)
      .field('comentario', 'sin archivo');
    expect(empty.status).toBe(400);
    expect(empty.body.error.code).toBe('VALIDATION_ERROR');

    // `advice` ya es una entidad admitida: un padre inexistente responde 404 (fuera de
    // alcance), no 400.
    const advice = await uploadEvidence(
      scenario.mentor.session,
      'advice',
      999_999,
      jpegBuffer(),
    );
    expect(advice.status).toBe(404);
    expect(advice.body.error.code).toBe('NOT_FOUND');

    const unknown = await uploadEvidence(
      scenario.student.session,
      'usuario' as never,
      1,
      jpegBuffer(),
    );
    expect(unknown.status).toBe(400);
  });

  it('exige sesión', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);

    const { post } = await import('./api.js');
    const response = await post(`/api/attachments/task/${taskId}`).attach(
      'file',
      jpegBuffer(),
      { filename: 'foto.jpg', contentType: 'image/jpeg' },
    );
    expect(response.status).toBe(401);
  });
});

/* =====================================================================================
 * T40 — descarga, borrado y archivo ausente
 * =================================================================================== */

describe('T40 · descarga y borrado', () => {
  it('descarga con el MIME verificado y el nombre original', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      pdfBuffer(),
      'lienzo del modelo.pdf',
      'application/pdf',
    );
    const id = uploaded.body.data.id as number;

    const owner = await scenario.student.session.get(`/api/attachments/${id}`);
    expect(owner.status).toBe(200);
    expect(owner.headers['content-type']).toBe('application/pdf');
    expect(owner.headers['content-disposition']).toContain('attachment;');
    expect(owner.headers['content-disposition']).toContain("filename*=UTF-8''lienzo%20del%20modelo.pdf");
    expect(owner.headers['x-content-type-options']).toBe('nosniff');
    expect(Number(owner.headers['content-length'])).toBeGreaterThan(0);

    expect((await scenario.mentor.session.get(`/api/attachments/${id}`)).status).toBe(200);
    expect((await scenario.admin.get(`/api/attachments/${id}`)).status).toBe(200);

    expect((await scenario.otherStudent.session.get(`/api/attachments/${id}`)).status).toBe(404);
    expect((await scenario.otherMentor.session.get(`/api/attachments/${id}`)).status).toBe(404);
  });

  it('borra el archivo del disco y da de baja la fila', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
      'evidencia.jpg',
    );
    const id = uploaded.body.data.id as number;
    const path = await storedPath(id);
    expect(await fileExists(path)).toBe(true);

    const removed = await scenario.student.session.del(`/api/attachments/${id}`);
    expect(removed.status).toBe(200);

    expect(await fileExists(path)).toBe(false);
    expect((await scenario.student.session.get(`/api/attachments/${id}`)).status).toBe(404);

    const { rows } = await query<{ fecha_eliminacion: Date | null }>(
      'SELECT fecha_eliminacion FROM adjuntos WHERE id_adjunto = $1',
      [id],
    );
    expect(rows[0]!.fecha_eliminacion).not.toBeNull();

    const { rows: audit } = await query<{ accion: string }>(
      `SELECT accion FROM auditoria_eventos
        WHERE entidad = 'adjuntos' AND entidad_id = $1`,
      [id],
    );
    expect(audit.map((row) => row.accion)).toContain('Baja lógica de evidencia');
  });

  it('solo el dueño de la evidencia o el administrador la borran', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
    );
    const id = uploaded.body.data.id as number;

    expect((await scenario.otherStudent.session.del(`/api/attachments/${id}`)).status).toBe(404);
    expect((await scenario.mentor.session.del(`/api/attachments/${id}`)).status).toBe(403);
    expect((await scenario.admin.del(`/api/attachments/${id}`)).status).toBe(200);
  });

  it('congela la evidencia cuando la tarea está en revisión', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
    );
    const id = uploaded.body.data.id as number;

    await scenario.student.session.put(`/api/task/${taskId}/complete`).send({});

    const locked = await uploadEvidence(scenario.student.session, 'task', taskId, jpegBuffer());
    expect(locked.status).toBe(422);
    expect(locked.body.error.code).toBe('TASK_EVIDENCE_LOCKED');

    // El administrador puede retirar una evidencia ya entregada.
    expect((await scenario.admin.del(`/api/attachments/${id}`)).status).toBe(200);
  });

  it('un archivo ausente da un error controlado y el borrado es idempotente', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
    );
    const id = uploaded.body.data.id as number;
    const path = await storedPath(id);

    await rm(path, { force: true });

    const missing = await scenario.student.session.get(`/api/attachments/${id}`);
    expect(missing.status).toBe(404);
    expect(missing.body.error.code).toBe('ATTACHMENT_FILE_MISSING');

    expect((await scenario.student.session.del(`/api/attachments/${id}`)).status).toBe(200);
  });

  it('solo el autor del seguimiento adjunta su evidencia', async () => {
    const scenario = await evidenceScenario();
    const tracing = await scenario.mentor.session.post('/api/tracing').send({
      emprendimientoId: scenario.emprendimientoId,
      tipoSeguimiento: 'Comentario',
      descripcion: 'Comentario con evidencia.',
    });
    const tracingId = tracing.body.data.id as number;

    const author = await uploadEvidence(
      scenario.mentor.session,
      'tracing',
      tracingId,
      jpegBuffer(),
    );
    expect(author.status).toBe(201);

    const student = await uploadEvidence(
      scenario.student.session,
      'tracing',
      tracingId,
      jpegBuffer(),
    );
    expect(student.status).toBe(403);
  });
});

/* =====================================================================================
 * T37 — baja del emprendimiento: lógica en la fila, física en los archivos
 * =================================================================================== */

describe('T37 · baja del emprendimiento y sus archivos', () => {
  it('da de baja la fila y elimina las evidencias del disco', async () => {
    const scenario = await evidenceScenario();
    const taskId = await taskFor(scenario);
    const uploaded = await uploadEvidence(
      scenario.student.session,
      'task',
      taskId,
      jpegBuffer(),
    );
    const attachmentId = uploaded.body.data.id as number;
    const path = await storedPath(attachmentId);
    expect(await fileExists(path)).toBe(true);

    const removed = await scenario.admin.del(`/api/entrepreneurship/${scenario.emprendimientoId}`);
    expect(removed.status).toBe(200);

    expect(await fileExists(path)).toBe(false);

    const { rows } = await query<{
      emprendimiento_eliminado: Date | null;
      adjunto_eliminado: Date | null;
      tarea_eliminada: Date | null;
    }>(
      `SELECT e.fecha_eliminacion AS emprendimiento_eliminado,
              a.fecha_eliminacion AS adjunto_eliminado,
              t.fecha_eliminacion AS tarea_eliminada
         FROM emprendimiento e
         JOIN tareas t ON t.emprendimiento_id_emprendimiento = e.id_emprendimiento
         JOIN adjuntos_tareas at ON at.tareas_id_tareas = t.id_tareas
         JOIN adjuntos a ON a.id_adjunto = at.adjuntos_id_adjunto
        WHERE e.id_emprendimiento = $1 AND a.id_adjunto = $2`,
      [scenario.emprendimientoId, attachmentId],
    );

    expect(rows[0]!.emprendimiento_eliminado).not.toBeNull();
    expect(rows[0]!.adjunto_eliminado).not.toBeNull();
    // La tarea se conserva: la baja es lógica y el histórico sigue siendo legible.
    expect(rows[0]!.tarea_eliminada).toBeNull();
  });
});
