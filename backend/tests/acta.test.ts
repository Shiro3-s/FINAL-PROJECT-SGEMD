import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { closePool, query } from '../src/db/pool.js';
import { resetRateLimits } from '../src/middleware/rateLimit.js';
import { adminSession, type Session } from './api.js';
import {
  createAccount,
  createEntrepreneurship,
  pdfBuffer,
} from './fixtures.js';

/**
 * T26 — acta de compromiso y confidencialidad (FR-003, BR-001, BR-009).
 *
 * El acta se prueba sobre un emprendimiento **sin** acta previa (el fixture
 * `evidenceScenario` ya trae una aprobada, que es lo que BR-001 necesita para asignar).
 * Cada caso crea su propio emprendimiento para no arrastrar el estado del anterior.
 */

beforeEach(async () => {
  resetRateLimits();
});

afterAll(async () => {
  await closePool();
});

interface ActaBody {
  id: number;
  estado: string;
  observaciones: string | null;
  fechaCarga: string | null;
  fechaRevision: string | null;
  emprendimiento: { id: number };
  estudiante: { id: number };
  revisor: { id: number } | null;
  adjunto: {
    id: number;
    nombreArchivo: string;
    tamanoBytes: number;
    tipoMime: string;
  } | null;
}

function upload(session: Session, buffer = pdfBuffer(512), filename = 'acta-firmada.pdf') {
  return session.post('/api/acta').attach('file', buffer, {
    filename,
    contentType: 'application/pdf',
  });
}

async function setupActa() {
  const admin = await adminSession();
  const student = await createAccount(admin, 2);
  const emprendimientoId = await createEntrepreneurship(admin, student.id);
  return { admin, student, emprendimientoId };
}

async function actasOf(emprendimientoId: number) {
  const { rows } = await query<{ id_acta: number; estado: string; adjuntos_id_adjunto: number }>(
    `SELECT id_acta, estado, adjuntos_id_adjunto
       FROM actas
      WHERE emprendimiento_id_emprendimiento = $1
      ORDER BY id_acta`,
    [emprendimientoId],
  );
  return rows;
}

/* =====================================================================================
 * T26 — carga, rechazo con motivo, reemplazo y aprobación
 * =================================================================================== */

describe('T26 · ciclo del acta', () => {
  it('sube, rechaza con motivo, permite reemplazarla y aprueba', async () => {
    const { admin, student, emprendimientoId } = await setupActa();

    const created = await upload(student.session);
    expect(created.status).toBe(201);
    const acta = created.body.data as ActaBody;
    expect(acta).toMatchObject({
      estado: 'En revisión',
      observaciones: null,
      emprendimiento: { id: emprendimientoId },
      estudiante: { id: student.id },
      revisor: null,
      adjunto: {
        nombreArchivo: 'acta-firmada.pdf',
        tipoMime: 'application/pdf',
        tamanoBytes: 512,
      },
    });
    expect(acta.fechaCarga).toBeTruthy();

    // Un acta pendiente no se reemplaza.
    const pending = await upload(student.session);
    expect(pending.status).toBe(409);
    expect(pending.body.error.code).toBe('ACTA_ALREADY_PENDING');

    // El rechazo exige motivo (BR-009) y solo se revisa una vez.
    const noMotive = await admin
      .put(`/api/acta/${acta.id}/review`)
      .send({ estado: 'Rechazada' });
    expect(noMotive.status).toBe(400);
    expect(noMotive.body.error.fields.observaciones).toBeDefined();

    const rejected = await admin.put(`/api/acta/${acta.id}/review`).send({
      estado: 'Rechazada',
      observaciones: 'La firma no coincide con el documento de identidad.',
    });
    expect(rejected.status).toBe(200);
    expect(rejected.body.data).toMatchObject({
      estado: 'Rechazada',
      observaciones: 'La firma no coincide con el documento de identidad.',
      revisor: { id: admin.id },
    });
    expect(rejected.body.data.fechaRevision).toBeTruthy();

    const reviewAgain = await admin
      .put(`/api/acta/${acta.id}/review`)
      .send({ estado: 'Aprobada' });
    expect(reviewAgain.status).toBe(422);
    expect(reviewAgain.body.error.code).toBe('ACTA_NOT_REVIEWABLE');

    // El aviso al estudiante lleva el motivo y el objeto del acta.
    const { rows: notifications } = await query<{
      tipo: string;
      mensaje: string;
      tipo_objeto: string | null;
      objeto_id: number | null;
    }>(
      `SELECT tipo, mensaje, tipo_objeto, objeto_id
         FROM notificaciones
        WHERE usuarios_id_usuarios = $1 AND tipo_objeto = 'acta' AND objeto_id = $2
        ORDER BY id_notificaciones DESC`,
      [student.id, acta.id],
    );
    expect(notifications[0]).toMatchObject({
      tipo: 'Sistema',
      tipo_objeto: 'acta',
      objeto_id: acta.id,
    });
    expect(notifications[0]!.mensaje).toContain('firma no coincide');

    // Rechazada permite una nueva versión.
    const reupload = await upload(student.session, pdfBuffer(600), 'acta-corregida.pdf');
    expect(reupload.status).toBe(201);
    const second = reupload.body.data as ActaBody;
    expect(second.id).not.toBe(acta.id);
    expect(second.estado).toBe('En revisión');

    const approved = await admin
      .put(`/api/acta/${second.id}/review`)
      .send({ estado: 'Aprobada', observaciones: 'Documento correcto.' });
    expect(approved.status).toBe(200);
    expect(approved.body.data.estado).toBe('Aprobada');

    // Una aprobada no se vuelve a subir.
    const afterApproved = await upload(student.session);
    expect(afterApproved.status).toBe(409);
    expect(afterApproved.body.error.code).toBe('ACTA_ALREADY_APPROVED');

    const rows = await actasOf(emprendimientoId);
    expect(rows.map((row) => row.estado)).toEqual(['Rechazada', 'Aprobada']);
    expect(rows.every((row) => row.adjuntos_id_adjunto !== null)).toBe(true);

    const audit = await query<{ accion: string }>(
      `SELECT accion FROM auditoria_eventos
        WHERE entidad = 'actas' AND entidad_id = ANY($1::int[])
        ORDER BY id_auditoria`,
      [[acta.id, second.id]],
    );
    const actions = audit.rows.map((row) => row.accion);
    expect(actions).toContain('Carga de acta');
    expect(actions).toContain('Revisión de acta');
  });

  it('declara el hueco de la plantilla legal y valida la revisión', async () => {
    const { admin, student } = await setupActa();

    const template = await student.session.get('/api/acta/template');
    expect(template.status).toBe(404);
    expect(template.body.error.code).toBe('ACTA_TEMPLATE_NOT_CONFIGURED');

    const unknownReview = await admin
      .put('/api/acta/999999/review')
      .send({ estado: 'Aprobada' });
    expect(unknownReview.status).toBe(404);

    const invalidState = await admin
      .put('/api/acta/1/review')
      .send({ estado: 'Publicada' });
    expect(invalidState.status).toBe(400);
  });
});

/* =====================================================================================
 * T26 — alcance, descarga y cuenta Limitado
 * =================================================================================== */

describe('T26 · alcance del acta y su archivo', () => {
  it('solo el administrador y el dueño ven y descargan el acta', async () => {
    const { admin, student } = await setupActa();
    const other = await createAccount(admin, 2);
    const teacher = await createAccount(admin, 3);

    const created = await upload(student.session);
    expect(created.status).toBe(201);
    const acta = created.body.data as ActaBody;
    const attachmentId = acta.adjunto!.id;

    const mine = await student.session.get(`/api/acta/${acta.id}`);
    expect(mine.status).toBe(200);

    const asAdmin = await admin.get(`/api/acta/${acta.id}`);
    expect(asAdmin.status).toBe(200);

    const foreign = await other.session.get(`/api/acta/${acta.id}`);
    expect(foreign.status).toBe(404);

    // El docente no participa del circuito del acta.
    const asTeacher = await teacher.session.get('/api/acta');
    expect(asTeacher.status).toBe(403);
    const teacherDownload = await teacher.session.get(`/api/attachments/${attachmentId}`);
    expect(teacherDownload.status).toBe(404);

    const download = await student.session.get(`/api/attachments/${attachmentId}`);
    expect(download.status).toBe(200);
    expect(download.headers['content-type']).toContain('application/pdf');
    expect(download.headers['content-disposition']).toContain('acta-firmada.pdf');

    const adminDownload = await admin.get(`/api/attachments/${attachmentId}`);
    expect(adminDownload.status).toBe(200);

    const foreignDownload = await other.session.get(`/api/attachments/${attachmentId}`);
    expect(foreignDownload.status).toBe(404);

    // El archivo del acta no se borra por la ruta de evidencias, ni siquiera el admin.
    const deniedDelete = await admin.del(`/api/attachments/${attachmentId}`);
    expect(deniedDelete.status).toBe(403);
    expect(deniedDelete.body.error.code).toBe('ROLE_NOT_ALLOWED');

    const studentDelete = await student.session.del(`/api/attachments/${attachmentId}`);
    expect(studentDelete.status).toBe(403);

    const list = await admin.get(`/api/acta?estudianteId=${student.id}&pageSize=100`);
    expect(list.status).toBe(200);
    expect(list.body.data.total).toBe(1);
    expect(list.body.data.items[0].id).toBe(acta.id);

    const ownList = await student.session.get('/api/acta');
    expect(ownList.status).toBe(200);
    expect(ownList.body.data.total).toBe(1);

    const otherList = await other.session.get('/api/acta');
    expect(otherList.status).toBe(200);
    expect(otherList.body.data.total).toBe(0);
  });

  it('la cuenta Limitado puede cargar su acta (AQ-07 opción A)', async () => {
    const admin = await adminSession();
    const limited = await createAccount(admin, 2, 'Limitado');
    await createEntrepreneurship(admin, limited.id);

    const created = await upload(limited.session);
    expect(created.status).toBe(201);
    expect(created.body.data.estado).toBe('En revisión');

    const list = await limited.session.get('/api/acta');
    expect(list.status).toBe(200);
    expect(list.body.data.total).toBe(1);
  });

  it('un estudiante sin emprendimiento recibe ENTREPRENEURSHIP_REQUIRED', async () => {
    const admin = await adminSession();
    const student = await createAccount(admin, 2);

    const response = await upload(student.session);
    expect(response.status).toBe(422);
    expect(response.body.error.code).toBe('ENTREPRENEURSHIP_REQUIRED');
  });

  it('valida la paginación y el orden del listado', async () => {
    const { admin } = await setupActa();

    for (const path of [
      '/api/acta?pageSize=101',
      '/api/acta?sort=nombres',
      '/api/acta?order=random',
      '/api/acta?orderBy=id',
    ]) {
      const response = await admin.get(path);
      expect(response.status).toBe(400);
    }
  });
});
