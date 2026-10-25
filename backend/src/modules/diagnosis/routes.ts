import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth } from '../../middleware/auth.js';
import { query } from '../../db/pool.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { sendData } from '../../utils/respond.js';

export const diagnosisRouter = Router();

type QuestionRow = {
  id_pregunta: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string | null;
};

/**
 * `GET /api/diagnosis/form` — banco de preguntas activo.
 *
 * Se implementa ya (Etapa 3) porque es el endpoint **restringido** que exige T03: una
 * cuenta `Limitado` debe recibir `403 ACCOUNT_NOT_ACTIVE`. El resto del módulo de
 * diagnóstico llega en la Etapa 9.
 */
diagnosisRouter.get(
  '/diagnosis/form',
  requireAuth,
  requireActiveAccount,
  asyncHandler(async (_req, res) => {
    const { rows } = await query<QuestionRow>(
      `SELECT id_pregunta, seccion, orden, enunciado, tipo, opciones
         FROM preguntas_diagnostico
        WHERE activa = TRUE
        ORDER BY seccion, orden`,
    );

    sendData(res, {
      total: rows.length,
      preguntas: rows.map((row) => ({
        id: row.id_pregunta,
        seccion: row.seccion,
        orden: row.orden,
        enunciado: row.enunciado,
        tipo: row.tipo,
        opciones: row.opciones ? row.opciones.split('|') : [],
      })),
    });
  }),
);
