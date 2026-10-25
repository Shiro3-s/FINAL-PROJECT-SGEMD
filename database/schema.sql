-- =====================================================================================
-- SGEMD — Esquema de la base de datos (PostgreSQL 17)
--
-- Fuente: `docs/diagrama-clases.md` v2 (27 entidades de negocio + 14 catálogos).
-- Regla de nombres: el atributo lógico PascalCase del diagrama se escribe en snake_case.
--   Usuarios_idMentor            -> usuarios_id_mentor
--   FasePlan_idFasePlan          -> fase_plan_id_fase_plan
--   CorreoInstitucional          -> correo_institucional
-- El mapeo es explícito y lo verifica `scripts/check-schema.mjs` contra los bloques
-- Mermaid del documento: si una columna desaparece, la Etapa 2 falla.
--
-- Enumeraciones: las cadenas son las canónicas (master §7.2). La lista vive una sola vez
-- en `shared/src/enums.ts`; aquí se repiten como CHECK y el script comprueba que coinciden.
--
-- Borrado lógico (BR-006): `fecha_eliminacion` nula = fila vigente, en las siete entidades
-- que se pueden eliminar desde la aplicación.
-- =====================================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================================================
-- Catálogos (14, solo lectura)
-- =====================================================================================

CREATE TABLE roles (
  id_roles    SERIAL PRIMARY KEY,
  nombre      TEXT NOT NULL UNIQUE,
  descripcion TEXT
);

CREATE TABLE tipodocumentos (
  id_tipodocumentos SERIAL PRIMARY KEY,
  nombre            TEXT NOT NULL UNIQUE
);

CREATE TABLE programaacademico (
  id_programaacademico SERIAL PRIMARY KEY,
  nombre               TEXT NOT NULL UNIQUE
);

CREATE TABLE centrouniversitarios (
  id_centrouniversitarios SERIAL PRIMARY KEY,
  nombre                  TEXT NOT NULL UNIQUE
);

CREATE TABLE municipios (
  id_municipios SERIAL PRIMARY KEY,
  departamento  TEXT NOT NULL,
  ciudad        TEXT NOT NULL,
  UNIQUE (departamento, ciudad)
);

CREATE TABLE tipopoblacion (
  id_tipopoblacion SERIAL PRIMARY KEY,
  nombre           TEXT NOT NULL UNIQUE
);

CREATE TABLE tipousuarios (
  id_tipousuarios SERIAL PRIMARY KEY,
  nombre          TEXT NOT NULL UNIQUE
);

CREATE TABLE etapaemprendimiento (
  id_etapaemprendimiento SERIAL PRIMARY KEY,
  nombre                 TEXT NOT NULL UNIQUE
);

CREATE TABLE faseplan (
  id_faseplan SERIAL PRIMARY KEY,
  nombre      TEXT NOT NULL UNIQUE
);

CREATE TABLE sectoreconomico (
  id_sectoreconomico SERIAL PRIMARY KEY,
  nombre             TEXT NOT NULL UNIQUE
);

CREATE TABLE modalidad (
  id_modalidad SERIAL PRIMARY KEY,
  nombre       TEXT NOT NULL UNIQUE
);

CREATE TABLE tipo_evento (
  id_tipo_evento SERIAL PRIMARY KEY,
  nombre         TEXT NOT NULL UNIQUE
);

CREATE TABLE fecha_y_horarios (
  id_fecha_y_horarios SERIAL PRIMARY KEY,
  fecha               DATE NOT NULL,
  hora_inicio         TIME NOT NULL,
  hora_fin            TIME NOT NULL,
  CHECK (hora_fin > hora_inicio)
);

CREATE TABLE modulos (
  id_modulos SERIAL PRIMARY KEY,
  nombre     TEXT NOT NULL UNIQUE
);

-- =====================================================================================
-- Bloque 1 — Expediente del emprendimiento (12 clases)
-- =====================================================================================

CREATE TABLE usuarios (
  id_usuarios                    SERIAL PRIMARY KEY,
  codigo                         TEXT NOT NULL,
  nombres                        TEXT NOT NULL,
  apellidos                      TEXT NOT NULL,
  numero_documento               TEXT NOT NULL UNIQUE,
  correo_institucional           TEXT NOT NULL UNIQUE,
  password                       TEXT NOT NULL,
  nivel_academico                TEXT CHECK (nivel_academico IN ('Pregrado', 'Posgrado', 'Egresado')),
  verificado                     BOOLEAN NOT NULL DEFAULT FALSE,
  estado                         TEXT NOT NULL DEFAULT 'Limitado'
                                   CHECK (estado IN ('Limitado', 'Activo', 'Inactivo')),
  ultima_actividad               TIMESTAMPTZ,
  fecha_eliminacion              TIMESTAMPTZ,
  roles_id_roles                 INT NOT NULL REFERENCES roles (id_roles),
  tipo_documentos_id_tipo_documentos
                                 INT NOT NULL REFERENCES tipodocumentos (id_tipodocumentos),
  programa_academico_id_programa_academico
                                 INT REFERENCES programaacademico (id_programaacademico),
  centro_universitarios_id_centro_universitarios
                                 INT REFERENCES centrouniversitarios (id_centrouniversitarios),
  municipios_id_municipios       INT REFERENCES municipios (id_municipios),
  tipo_poblacion_id_tipo_poblacion
                                 INT REFERENCES tipopoblacion (id_tipopoblacion),
  tipo_usuarios_id_tipo_usuarios INT REFERENCES tipousuarios (id_tipousuarios)
);

CREATE TABLE emprendimiento (
  id_emprendimiento              SERIAL PRIMARY KEY,
  codigo                         TEXT NOT NULL UNIQUE,
  nombre                         TEXT NOT NULL,
  descripcion                    TEXT,
  redes_sociales                 TEXT,
  estado_aprobacion              TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado_aprobacion IN ('Pendiente', 'Aprobado', 'Rechazado')),
  motivo_rechazo                 TEXT,
  es_paralelo                    BOOLEAN NOT NULL DEFAULT FALSE,
  avance                         INT NOT NULL DEFAULT 0 CHECK (avance BETWEEN 0 AND 100),
  fecha_eliminacion              TIMESTAMPTZ,
  etapa_emprendimiento_id_etapa_emprendimiento
                                 INT REFERENCES etapaemprendimiento (id_etapaemprendimiento),
  sector_economico_id_sector_economico
                                 INT REFERENCES sectoreconomico (id_sectoreconomico),
  centro_universitarios_id_centro_universitarios
                                 INT REFERENCES centrouniversitarios (id_centrouniversitarios),
  usuarios_id_usuarios           INT NOT NULL REFERENCES usuarios (id_usuarios),
  -- BR-004: rechazar exige motivo.
  CONSTRAINT emprendimiento_rechazo_con_motivo
    CHECK (estado_aprobacion <> 'Rechazado' OR motivo_rechazo IS NOT NULL)
);

CREATE TABLE adjuntos (
  id_adjunto          SERIAL PRIMARY KEY,
  nombre_archivo      TEXT NOT NULL,
  ruta_archivo        TEXT NOT NULL,
  tamano_bytes        BIGINT NOT NULL CHECK (tamano_bytes > 0),
  tipo_mime           TEXT NOT NULL
                        CHECK (tipo_mime IN ('image/jpeg', 'image/png', 'application/pdf')),
  fecha_subida        TIMESTAMPTZ NOT NULL DEFAULT now(),
  fecha_eliminacion   TIMESTAMPTZ,
  usuarios_id_usuarios INT NOT NULL REFERENCES usuarios (id_usuarios)
);

CREATE TABLE asignaciones (
  id_asignacion                   SERIAL PRIMARY KEY,
  fecha_asignacion                TIMESTAMPTZ NOT NULL DEFAULT now(),
  estado                          TEXT NOT NULL DEFAULT 'activa'
                                    CHECK (estado IN ('activa', 'inactiva')),
  horas_semanales                 INT NOT NULL CHECK (horas_semanales > 0),
  usuarios_id_mentor              INT NOT NULL REFERENCES usuarios (id_usuarios),
  usuarios_id_estudiante          INT NOT NULL REFERENCES usuarios (id_usuarios),
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento)
);

-- R11: como máximo una asignación activa por emprendimiento. Las multiplicidades del
-- diagrama no lo garantizan; se resuelve con un índice único parcial.
CREATE UNIQUE INDEX asignaciones_una_activa_por_emprendimiento
  ON asignaciones (emprendimiento_id_emprendimiento)
  WHERE estado = 'activa';

CREATE TABLE seguimientos (
  id_seguimientos                SERIAL PRIMARY KEY,
  descripcion                    TEXT NOT NULL,
  tipo_seguimiento               TEXT NOT NULL
                                   CHECK (tipo_seguimiento IN ('Avance de fase', 'Comentario')),
  puntaje                        INT CHECK (puntaje BETWEEN 0 AND 100),
  estado_revision                TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado_revision IN ('Pendiente', 'En revisión', 'Calificada', 'Devuelta')),
  fecha_seguimiento              TIMESTAMPTZ NOT NULL DEFAULT now(),
  retroalimentacion              TEXT,
  fecha_eliminacion              TIMESTAMPTZ,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_usuarios           INT NOT NULL REFERENCES usuarios (id_usuarios),
  fase_plan_id_fase_plan         INT REFERENCES faseplan (id_faseplan)
);

CREATE TABLE tareas (
  id_tareas                      SERIAL PRIMARY KEY,
  titulo                         TEXT NOT NULL,
  descripcion                    TEXT,
  fecha_limite                   DATE,
  prioridad                      TEXT NOT NULL CHECK (prioridad IN ('Alta', 'Media', 'Baja')),
  puntos                         INT CHECK (puntos >= 0),
  estado                         TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado IN ('Pendiente', 'En curso', 'En revisión', 'Completada', 'Vencida', 'Devuelta')),
  puntaje_obtenido               INT CHECK (puntaje_obtenido BETWEEN 0 AND 100),
  retroalimentacion              TEXT,
  estado_revision                TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado_revision IN ('Pendiente', 'En revisión', 'Calificada', 'Devuelta')),
  evidencia_requerida            BOOLEAN NOT NULL DEFAULT TRUE,
  motivo_devolucion              TEXT,
  observaciones_devolucion       TEXT,
  fecha_eliminacion              TIMESTAMPTZ,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_usuarios           INT REFERENCES usuarios (id_usuarios),
  usuarios_id_creador            INT REFERENCES usuarios (id_usuarios),
  fase_plan_id_fase_plan         INT REFERENCES faseplan (id_faseplan),
  -- R19b: devolver exige motivo.
  CONSTRAINT tareas_devolucion_con_motivo
    CHECK (estado <> 'Devuelta' OR motivo_devolucion IS NOT NULL)
);

CREATE TABLE asesorias (
  id_asesorias                   SERIAL PRIMARY KEY,
  tema                           TEXT NOT NULL,
  fecha_asesoria                 TIMESTAMPTZ,
  estado                         TEXT NOT NULL DEFAULT 'Por agendar'
                                   CHECK (estado IN ('Por agendar', 'Programada', 'Confirmada', 'En curso', 'Completada', 'Cancelada')),
  lugar_enlace                   TEXT,
  fecha_eliminacion              TIMESTAMPTZ,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_usuarios           INT NOT NULL REFERENCES usuarios (id_usuarios),
  usuarios_id_docentes           INT REFERENCES usuarios (id_usuarios),
  modalidad_id_modalidad         INT REFERENCES modalidad (id_modalidad),
  fecha_y_horarios_id_fecha_y_horarios
                                 INT REFERENCES fecha_y_horarios (id_fecha_y_horarios)
);

CREATE TABLE actas (
  id_acta                        SERIAL PRIMARY KEY,
  estado                         TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado IN ('Pendiente', 'En revisión', 'Aprobada', 'Rechazada')),
  observaciones                  TEXT,
  fecha_carga                    TIMESTAMPTZ,
  fecha_revision                 TIMESTAMPTZ,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_estudiante         INT NOT NULL REFERENCES usuarios (id_usuarios),
  usuarios_id_revisor            INT REFERENCES usuarios (id_usuarios),
  adjuntos_id_adjunto            INT REFERENCES adjuntos (id_adjunto),
  -- BR-009: rechazar el acta exige motivo (se guarda en `observaciones`).
  CONSTRAINT actas_rechazo_con_motivo
    CHECK (estado <> 'Rechazada' OR observaciones IS NOT NULL)
);

CREATE TABLE comentarios (
  id_comentario                  SERIAL PRIMARY KEY,
  texto                          TEXT NOT NULL,
  fecha                          TIMESTAMPTZ NOT NULL DEFAULT now(),
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_usuarios           INT NOT NULL REFERENCES usuarios (id_usuarios)
);

CREATE TABLE adjuntos_tareas (
  adjuntos_id_adjunto INT NOT NULL REFERENCES adjuntos (id_adjunto) ON DELETE CASCADE,
  tareas_id_tareas    INT NOT NULL REFERENCES tareas (id_tareas) ON DELETE CASCADE,
  PRIMARY KEY (adjuntos_id_adjunto, tareas_id_tareas)
);

CREATE TABLE adjuntos_seguimientos (
  adjuntos_id_adjunto          INT NOT NULL REFERENCES adjuntos (id_adjunto) ON DELETE CASCADE,
  seguimientos_id_seguimientos INT NOT NULL REFERENCES seguimientos (id_seguimientos) ON DELETE CASCADE,
  PRIMARY KEY (adjuntos_id_adjunto, seguimientos_id_seguimientos)
);

CREATE TABLE adjuntos_asesorias (
  adjuntos_id_adjunto INT NOT NULL REFERENCES adjuntos (id_adjunto) ON DELETE CASCADE,
  asesorias_id_asesorias INT NOT NULL REFERENCES asesorias (id_asesorias) ON DELETE CASCADE,
  PRIMARY KEY (adjuntos_id_adjunto, asesorias_id_asesorias)
);

-- =====================================================================================
-- Bloque 2 — Diagnóstico y eventos (8 clases)
-- =====================================================================================

CREATE TABLE diagnosticos (
  id_diagnosticos                SERIAL PRIMARY KEY,
  fecha_diagnostico              TIMESTAMPTZ NOT NULL DEFAULT now(),
  estado                         TEXT NOT NULL DEFAULT 'En progreso'
                                   CHECK (estado IN ('En progreso', 'Enviado', 'Revisado')),
  puntaje_total                  INT CHECK (puntaje_total BETWEEN 0 AND 100),
  url_informe                    TEXT,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  sector_economico_id_sector_economico INT REFERENCES sectoreconomico (id_sectoreconomico)
);

CREATE TABLE preguntas_diagnostico (
  id_pregunta SERIAL PRIMARY KEY,
  seccion     INT NOT NULL CHECK (seccion BETWEEN 1 AND 5),
  orden       INT NOT NULL,
  enunciado   TEXT NOT NULL,
  tipo        TEXT NOT NULL,
  opciones    TEXT,
  activa      BOOLEAN NOT NULL DEFAULT TRUE,
  origen      TEXT NOT NULL,
  UNIQUE (seccion, orden)
);

CREATE TABLE respuestas_diagnostico (
  id_respuesta                   SERIAL PRIMARY KEY,
  valor                          TEXT NOT NULL,
  fecha_respuesta                TIMESTAMPTZ NOT NULL DEFAULT now(),
  preguntas_id_pregunta          INT NOT NULL REFERENCES preguntas_diagnostico (id_pregunta),
  diagnosticos_id_diagnosticos   INT NOT NULL REFERENCES diagnosticos (id_diagnosticos) ON DELETE CASCADE,
  UNIQUE (preguntas_id_pregunta, diagnosticos_id_diagnosticos)
);

CREATE TABLE caracterizacion (
  id                             SERIAL PRIMARY KEY,
  seccion                        TEXT NOT NULL,
  resultado                      TEXT,
  puntaje                        INT,
  fortalezas                     TEXT,
  oportunidades                  TEXT,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  diagnosticos_id_diagnosticos   INT NOT NULL REFERENCES diagnosticos (id_diagnosticos) ON DELETE CASCADE
);

CREATE TABLE valoracion (
  id                             SERIAL PRIMARY KEY,
  -- Los seis valores de `dimension` dependen de la rúbrica (AQ-09) y todavía no se
  -- conocen: sin CHECK a propósito. La tabla permanece vacía hasta que se apruebe.
  dimension                      TEXT NOT NULL,
  puntaje                        INT CHECK (puntaje BETWEEN 0 AND 100),
  banda                          TEXT CHECK (banda IN ('90-100', '70-89', '50-69', '<50')),
  recomendacion                  TEXT,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  diagnosticos_id_diagnosticos   INT NOT NULL REFERENCES diagnosticos (id_diagnosticos) ON DELETE CASCADE
);

CREATE TABLE eventos (
  id_eventos                     SERIAL PRIMARY KEY,
  nombre_evento                  TEXT NOT NULL,
  descripcion                    TEXT,
  dirigido_a                     TEXT,
  capacidad_maxima               INT CHECK (capacidad_maxima > 0),
  cupo                           INT CHECK (cupo >= 0),
  estado                         TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado IN ('Pendiente', 'Aprobado', 'Rechazado', 'Publicado')),
  requiere_registro              BOOLEAN NOT NULL DEFAULT FALSE,
  lugar                          TEXT,
  enlace                         TEXT,
  fecha_eliminacion              TIMESTAMPTZ,
  usuarios_id_organizador        INT NOT NULL REFERENCES usuarios (id_usuarios),
  tipo_evento_id_tipo_evento     INT REFERENCES tipo_evento (id_tipo_evento),
  modalidad_id_modalidad         INT REFERENCES modalidad (id_modalidad),
  fecha_y_horarios_id_fecha_y_horarios
                                 INT REFERENCES fecha_y_horarios (id_fecha_y_horarios)
);

CREATE TABLE usuarios_has_eventos (
  usuarios_id_usuarios INT NOT NULL REFERENCES usuarios (id_usuarios),
  eventos_id_eventos   INT NOT NULL REFERENCES eventos (id_eventos) ON DELETE CASCADE,
  -- `estado_asistencia` es enum en el diagrama pero sus valores no están definidos:
  -- sin CHECK hasta que se confirmen (P-9).
  estado_asistencia    TEXT,
  fecha_inscripcion    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (usuarios_id_usuarios, eventos_id_eventos)
);

CREATE TABLE recomendaciones_evento (
  id_recomendacion               SERIAL PRIMARY KEY,
  mensaje                        TEXT,
  -- `estado` es enum en el diagrama sin valores definidos: sin CHECK (P-9).
  estado                         TEXT NOT NULL DEFAULT 'Pendiente',
  fecha                          TIMESTAMPTZ NOT NULL DEFAULT now(),
  eventos_id_eventos             INT NOT NULL REFERENCES eventos (id_eventos) ON DELETE CASCADE,
  emprendimiento_id_emprendimiento INT NOT NULL REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_estudiante         INT REFERENCES usuarios (id_usuarios),
  usuarios_id_docente            INT NOT NULL REFERENCES usuarios (id_usuarios)
);

-- =====================================================================================
-- Bloque 3 — Soporte del sistema (7 clases)
-- =====================================================================================

CREATE TABLE codigosverificacion (
  id_codigo             SERIAL PRIMARY KEY,
  correo_institucional  TEXT NOT NULL,
  proposito             TEXT NOT NULL
                          CHECK (proposito IN ('Verificación', 'Recuperación')),
  -- HMAC-SHA256 del código (D20). El código en claro nunca se guarda.
  codigo                TEXT NOT NULL,
  expiracion            TIMESTAMPTZ NOT NULL,
  usado                 BOOLEAN NOT NULL DEFAULT FALSE,
  intentos              INT NOT NULL DEFAULT 0 CHECK (intentos >= 0),
  usuarios_id_usuarios  INT REFERENCES usuarios (id_usuarios)
);

CREATE TABLE notificaciones (
  id_notificaciones     SERIAL PRIMARY KEY,
  tipo                  TEXT NOT NULL
                          CHECK (tipo IN ('Tarea', 'Asesoría', 'Seguimiento', 'Solicitud', 'Diagnóstico', 'Evento', 'Sistema')),
  mensaje               TEXT NOT NULL,
  url                   TEXT,
  tipo_objeto           TEXT,
  objeto_id             INT,
  leida                 BOOLEAN NOT NULL DEFAULT FALSE,
  fecha                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  usuarios_id_usuarios  INT NOT NULL REFERENCES usuarios (id_usuarios) ON DELETE CASCADE
);

CREATE TABLE habilitaciones (
  id_habilitacion       SERIAL PRIMARY KEY,
  -- `estado` es enum en el diagrama sin valores definidos: sin CHECK hasta AQ-07 (P-8).
  estado                TEXT NOT NULL,
  fecha                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  usuarios_id_usuarios  INT NOT NULL REFERENCES usuarios (id_usuarios) ON DELETE CASCADE,
  modulos_id_modulos    INT NOT NULL REFERENCES modulos (id_modulos)
);

CREATE TABLE solicitudes (
  id_solicitud                   SERIAL PRIMARY KEY,
  tipo                           TEXT NOT NULL CHECK (tipo IN ('Desbloqueo', 'Paralelo', 'Cita')),
  detalle                        TEXT,
  estado                         TEXT NOT NULL DEFAULT 'Pendiente'
                                   CHECK (estado IN ('Pendiente', 'Aprobada', 'Rechazada')),
  motivo_rechazo                 TEXT,
  fecha_solicitud                TIMESTAMPTZ NOT NULL DEFAULT now(),
  fecha_resolucion               TIMESTAMPTZ,
  usuarios_id_usuarios           INT NOT NULL REFERENCES usuarios (id_usuarios),
  emprendimiento_id_emprendimiento INT REFERENCES emprendimiento (id_emprendimiento),
  usuarios_id_resuelto_por       INT REFERENCES usuarios (id_usuarios),
  -- Bandeja única: rechazar exige motivo (R38).
  CONSTRAINT solicitudes_rechazo_con_motivo
    CHECK (estado <> 'Rechazada' OR motivo_rechazo IS NOT NULL)
);

CREATE TABLE configuracion_programa (
  id_configuracion      SERIAL PRIMARY KEY,
  clave                 TEXT NOT NULL UNIQUE,
  valor                 TEXT,
  tipo_dato             TEXT NOT NULL CHECK (tipo_dato IN ('int', 'bool', 'text', 'date')),
  descripcion           TEXT,
  usuarios_id_usuarios  INT REFERENCES usuarios (id_usuarios)
);

CREATE TABLE respaldos (
  id_respaldo           SERIAL PRIMARY KEY,
  codigo                TEXT NOT NULL UNIQUE,
  tipo                  TEXT NOT NULL CHECK (tipo IN ('Completo', 'Parcial')),
  fecha_hora            TIMESTAMPTZ NOT NULL DEFAULT now(),
  tamano_logico_mb      INT CHECK (tamano_logico_mb >= 0),
  tamano_anadido_mb     INT CHECK (tamano_anadido_mb >= 0),
  estado                TEXT NOT NULL CHECK (estado IN ('Exitosa', 'Fallida')),
  destino               TEXT,
  retencion_dias        INT CHECK (retencion_dias > 0),
  checksum_manifiesto   TEXT,
  -- Nulo cuando lo crea el job diario, sin usuario (diagrama, tabla de nulabilidad).
  usuarios_id_usuarios  INT REFERENCES usuarios (id_usuarios)
);

CREATE TABLE auditoria_eventos (
  id_auditoria          SERIAL PRIMARY KEY,
  -- La lista de acciones se fija en la Etapa 4 (P-4); sin CHECK por ahora.
  accion                TEXT NOT NULL,
  entidad               TEXT NOT NULL,
  entidad_id            INT,
  valor_anterior        JSONB,
  valor_nuevo           JSONB,
  fecha                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  ip                    TEXT,
  -- Nulo cuando la acción la ejecuta un job (inactividad, tareas vencidas).
  usuarios_id_usuarios  INT REFERENCES usuarios (id_usuarios)
);

-- =====================================================================================
-- Índices: claves foráneas y columnas de filtro/orden que usan las pantallas.
-- =====================================================================================

CREATE INDEX usuarios_estado_idx ON usuarios (estado) WHERE fecha_eliminacion IS NULL;
CREATE INDEX usuarios_rol_idx ON usuarios (roles_id_roles);
CREATE INDEX emprendimiento_usuario_idx ON emprendimiento (usuarios_id_usuarios);
CREATE INDEX emprendimiento_estado_idx ON emprendimiento (estado_aprobacion)
  WHERE fecha_eliminacion IS NULL;
CREATE INDEX asignaciones_mentor_idx ON asignaciones (usuarios_id_mentor);
CREATE INDEX asignaciones_estudiante_idx ON asignaciones (usuarios_id_estudiante);
CREATE INDEX seguimientos_emprendimiento_idx ON seguimientos (emprendimiento_id_emprendimiento);
CREATE INDEX seguimientos_fase_idx ON seguimientos (fase_plan_id_fase_plan);
CREATE INDEX tareas_emprendimiento_idx ON tareas (emprendimiento_id_emprendimiento);
CREATE INDEX tareas_estado_idx ON tareas (estado) WHERE fecha_eliminacion IS NULL;
CREATE INDEX tareas_fecha_limite_idx ON tareas (fecha_limite);
CREATE INDEX tareas_asignado_idx ON tareas (usuarios_id_usuarios);
CREATE INDEX asesorias_emprendimiento_idx ON asesorias (emprendimiento_id_emprendimiento);
CREATE INDEX asesorias_docente_idx ON asesorias (usuarios_id_docentes);
CREATE INDEX asesorias_estado_idx ON asesorias (estado) WHERE fecha_eliminacion IS NULL;
CREATE INDEX asesorias_fecha_idx ON asesorias (fecha_asesoria);
CREATE INDEX actas_emprendimiento_idx ON actas (emprendimiento_id_emprendimiento);
CREATE INDEX actas_estado_idx ON actas (estado);
CREATE INDEX comentarios_emprendimiento_idx ON comentarios (emprendimiento_id_emprendimiento);
CREATE INDEX adjuntos_usuario_idx ON adjuntos (usuarios_id_usuarios);
CREATE INDEX adjuntos_tareas_tarea_idx ON adjuntos_tareas (tareas_id_tareas);
CREATE INDEX adjuntos_seguimientos_seguimiento_idx
  ON adjuntos_seguimientos (seguimientos_id_seguimientos);
CREATE INDEX adjuntos_asesorias_asesoria_idx ON adjuntos_asesorias (asesorias_id_asesorias);
CREATE INDEX diagnosticos_emprendimiento_idx ON diagnosticos (emprendimiento_id_emprendimiento);
CREATE INDEX respuestas_diagnostico_idx ON respuestas_diagnostico (diagnosticos_id_diagnosticos);
CREATE INDEX eventos_estado_idx ON eventos (estado) WHERE fecha_eliminacion IS NULL;
CREATE INDEX eventos_horario_idx ON eventos (fecha_y_horarios_id_fecha_y_horarios);
CREATE INDEX usuarios_has_eventos_evento_idx ON usuarios_has_eventos (eventos_id_eventos);
CREATE INDEX recomendaciones_evento_evento_idx ON recomendaciones_evento (eventos_id_eventos);
CREATE INDEX recomendaciones_evento_docente_idx ON recomendaciones_evento (usuarios_id_docente);
CREATE INDEX codigos_correo_idx ON codigosverificacion (correo_institucional, usado);
CREATE INDEX notificaciones_usuario_idx ON notificaciones (usuarios_id_usuarios, leida);
CREATE INDEX habilitaciones_usuario_idx ON habilitaciones (usuarios_id_usuarios);
CREATE INDEX solicitudes_estado_idx ON solicitudes (estado);
CREATE INDEX solicitudes_solicitante_idx ON solicitudes (usuarios_id_usuarios);
CREATE INDEX auditoria_entidad_idx ON auditoria_eventos (entidad, entidad_id);
CREATE INDEX auditoria_fecha_idx ON auditoria_eventos (fecha DESC);
