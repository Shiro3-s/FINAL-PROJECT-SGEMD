-- =====================================================================================
-- SGEMD — Datos iniciales (seed)
--
-- Contenido: 14 catálogos con sus valores canónicos, configuración del programa,
-- 1 administrador, 2 docentes y 2 estudiantes FICTICIOS, 1 emprendimiento con su acta
-- aprobada y su asignación, 2 tareas y las 22 preguntas del diagnóstico.
--
-- Reglas:
--  · Nunca datos personales reales (Ley 1581/2012).
--  · Las contraseñas se generan con bcrypt (pgcrypto, coste 10) y son todas `Demo1234`.
--  · Las preguntas se transcriben de `prototype/estudiante/diagnostico.html` con
--    Origen='Prototipo'; el banco es PROVISIONAL hasta recibir el Excel (AQ-12).
--    Los valores de `tipo` ('Texto', 'Texto largo', 'Selección única') son provisionales:
--    el diagrama declara el enum pero no sus valores (P-9).
-- =====================================================================================

-- Catálogos ---------------------------------------------------------------------------

INSERT INTO roles (id_roles, nombre, descripcion) VALUES
  (1, 'Admin', 'Coordinación del programa'),
  (2, 'Estudiante', 'Emprendedor en formación'),
  (3, 'Docente', 'Mentor asignado'),
  (4, 'Auditor', 'Consulta y exportación (post-MVP)');

INSERT INTO tipodocumentos (id_tipodocumentos, nombre) VALUES
  (1, 'CC'), (2, 'TI'), (3, 'CE');

INSERT INTO programaacademico (id_programaacademico, nombre) VALUES
  (1, 'Ingeniería Industrial'),
  (2, 'Administración de Empresas'),
  (3, 'Contaduría Pública'),
  (4, 'Ingeniería de Sistemas'),
  (5, 'Psicología');

INSERT INTO centrouniversitarios (id_centrouniversitarios, nombre) VALUES
  (1, 'Sede Norte'), (2, 'Sede Centro'), (3, 'Sede Sur');

INSERT INTO municipios (id_municipios, departamento, ciudad) VALUES
  (1, 'Cundinamarca', 'Bogotá D.C.'),
  (2, 'Cundinamarca', 'Soacha'),
  (3, 'Cundinamarca', 'Zipaquirá');

INSERT INTO tipopoblacion (id_tipopoblacion, nombre) VALUES
  (1, 'Ninguna'),
  (2, 'Víctima del conflicto armado'),
  (3, 'Persona con discapacidad'),
  (4, 'Grupo étnico'),
  (5, 'Madre cabeza de hogar');

INSERT INTO tipousuarios (id_tipousuarios, nombre) VALUES
  (1, 'Estudiante'), (2, 'Egresado'), (3, 'Docente'), (4, 'Administrativo');

INSERT INTO etapaemprendimiento (id_etapaemprendimiento, nombre) VALUES
  (1, 'FASE 1 - Ideación'),
  (2, 'FASE 2 - Prototipo'),
  (3, 'FASE 3 - Validación'),
  (4, 'FASE 4 - Formalización');

INSERT INTO faseplan (id_faseplan, nombre) VALUES
  (1, 'FASE 1 Ideación y priorización de ideas'),
  (2, 'FASE 2 Estructuración y ejecución'),
  (3, 'FASE 3 Consolidación del proceso'),
  (4, 'FASE 4 Escalamiento');

INSERT INTO sectoreconomico (id_sectoreconomico, nombre) VALUES
  (1, 'Alimentos'), (2, 'Moda'), (3, 'Ambiental'),
  (4, 'Muebles'), (5, 'Tecnología'), (6, 'Comercio');

INSERT INTO modalidad (id_modalidad, nombre) VALUES
  (1, 'Presencial'), (2, 'Virtual'), (3, 'Mixta');

INSERT INTO tipo_evento (id_tipo_evento, nombre) VALUES
  (1, 'Startup'), (2, 'Capacitación'), (3, 'Asesoría grupal'),
  (4, 'Showroom'), (5, 'Taller');

INSERT INTO fecha_y_horarios (id_fecha_y_horarios, fecha, hora_inicio, hora_fin) VALUES
  (1, DATE '2026-11-05', TIME '09:00', TIME '11:00'),
  (2, DATE '2026-11-12', TIME '14:00', TIME '16:00');

INSERT INTO modulos (id_modulos, nombre) VALUES
  (1, 'Perfil'), (2, 'Emprendimiento'), (3, 'Diagnóstico'), (4, 'Tareas'),
  (5, 'Asesorías'), (6, 'Seguimiento'), (7, 'Eventos'), (8, 'Reportes');

-- Sincronización de secuencias ----------------------------------------------------------
-- Los catálogos se siembran con id explícito para que los datos demo sean estables entre
-- ejecuciones. Eso **no** avanza el `SERIAL`: sin este bloque, el primer alta real choca
-- con la clave primaria (pasaba con `fecha_y_horarios` al agendar la primera asesoría).

SELECT setval(pg_get_serial_sequence('roles', 'id_roles'), (SELECT MAX(id_roles) FROM roles));
SELECT setval(pg_get_serial_sequence('tipodocumentos', 'id_tipodocumentos'), (SELECT MAX(id_tipodocumentos) FROM tipodocumentos));
SELECT setval(pg_get_serial_sequence('programaacademico', 'id_programaacademico'), (SELECT MAX(id_programaacademico) FROM programaacademico));
SELECT setval(pg_get_serial_sequence('centrouniversitarios', 'id_centrouniversitarios'), (SELECT MAX(id_centrouniversitarios) FROM centrouniversitarios));
SELECT setval(pg_get_serial_sequence('municipios', 'id_municipios'), (SELECT MAX(id_municipios) FROM municipios));
SELECT setval(pg_get_serial_sequence('tipopoblacion', 'id_tipopoblacion'), (SELECT MAX(id_tipopoblacion) FROM tipopoblacion));
SELECT setval(pg_get_serial_sequence('tipousuarios', 'id_tipousuarios'), (SELECT MAX(id_tipousuarios) FROM tipousuarios));
SELECT setval(pg_get_serial_sequence('etapaemprendimiento', 'id_etapaemprendimiento'), (SELECT MAX(id_etapaemprendimiento) FROM etapaemprendimiento));
SELECT setval(pg_get_serial_sequence('faseplan', 'id_faseplan'), (SELECT MAX(id_faseplan) FROM faseplan));
SELECT setval(pg_get_serial_sequence('sectoreconomico', 'id_sectoreconomico'), (SELECT MAX(id_sectoreconomico) FROM sectoreconomico));
SELECT setval(pg_get_serial_sequence('modalidad', 'id_modalidad'), (SELECT MAX(id_modalidad) FROM modalidad));
SELECT setval(pg_get_serial_sequence('tipo_evento', 'id_tipo_evento'), (SELECT MAX(id_tipo_evento) FROM tipo_evento));
SELECT setval(pg_get_serial_sequence('fecha_y_horarios', 'id_fecha_y_horarios'), (SELECT MAX(id_fecha_y_horarios) FROM fecha_y_horarios));
SELECT setval(pg_get_serial_sequence('modulos', 'id_modulos'), (SELECT MAX(id_modulos) FROM modulos));

-- Configuración del programa -----------------------------------------------------------
-- Una sola fuente por dato: los topes, límites y banderas viven aquí, no en el código.

INSERT INTO configuracion_programa (clave, valor, tipo_dato, descripcion) VALUES
  ('carga_max_horas', '12', 'int', 'Tope de horas semanales por docente (FR-016)'),
  ('max_emprendimientos_docente', '12', 'int', 'Tope de emprendimientos por docente (FR-016)'),
  ('sede_por_defecto', 'Sede Norte', 'text', 'Sede que se propone al registrar'),
  ('etapa_inicial', 'FASE 1 - Ideación', 'text', 'Etapa con la que nace un emprendimiento'),
  ('fecha_cierre_admisiones', NULL, 'date', 'Cierre de admisiones (vacío = abierto)'),
  ('cupos_por_sede', '40', 'int', 'Cupos por sede'),
  ('upload_max_mb', '500', 'int', 'Tamaño máximo por archivo (FR-008)'),
  ('upload_max_files_per_entity', '5', 'int', 'Archivos por entidad (D1b)'),
  ('correos_dominios_permitidos', 'uniminuto.edu,uniminuto.edu.co', 'text', 'Dominios aceptados (D3)'),
  ('paralelos_maximos', '1', 'int', 'Emprendimientos paralelos permitidos (D5)'),
  ('backup_retention_days', '30', 'int', 'Retención de respaldos (D7, D22)'),
  ('inactividad_dias', '90', 'int', 'Días sin actividad para pasar a Inactivo (BR-005)'),
  ('rubrica_diagnostico_aprobada', 'false', 'bool', 'Bandeja de AQ-09: sin rúbrica no se puntúa'),
  ('checklist_activacion_aprobado', 'false', 'bool', 'Bandeja de AQ-06'),
  ('acta_plazo_revision_dias', NULL, 'int', 'Sin implementar hasta confirmar AQ-10'),
  ('notif_tareas', 'true', 'bool', 'Notificar tareas'),
  ('notif_asesorias', 'true', 'bool', 'Notificar asesorías'),
  ('notif_seguimiento', 'true', 'bool', 'Notificar seguimiento');

-- Usuarios ficticios --------------------------------------------------------------------
-- Contraseña de todas las cuentas demo: Demo1234 (bcrypt, coste 10).

INSERT INTO usuarios
  (codigo, nombres, apellidos, numero_documento, correo_institucional, password,
   nivel_academico, verificado, estado, ultima_actividad,
   roles_id_roles, tipo_documentos_id_tipo_documentos,
   programa_academico_id_programa_academico,
   centro_universitarios_id_centro_universitarios, municipios_id_municipios,
   tipo_poblacion_id_tipo_poblacion, tipo_usuarios_id_tipo_usuarios)
VALUES
  ('ADM-001', 'Cuenta', 'Administradora Demo', '900000001',
   'admin.demo@uniminuto.edu.co', crypt('Demo1234', gen_salt('bf', 10)),
   NULL, TRUE, 'Activo', now(), 1, 1, NULL, 1, 1, 1, 4),

  ('DOC-001', 'Docente', 'Demo Uno', '900000002',
   'docente.demo1@uniminuto.edu.co', crypt('Demo1234', gen_salt('bf', 10)),
   NULL, TRUE, 'Activo', now(), 3, 1, NULL, 1, 1, 1, 3),

  ('DOC-002', 'Docente', 'Demo Dos', '900000003',
   'docente.demo2@uniminuto.edu.co', crypt('Demo1234', gen_salt('bf', 10)),
   NULL, TRUE, 'Activo', now(), 3, 1, NULL, 1, 1, 1, 3),

  ('100001', 'Estudiante', 'Demo Uno', '900000004',
   'estudiante.demo1@uniminuto.edu.co', crypt('Demo1234', gen_salt('bf', 10)),
   'Pregrado', TRUE, 'Activo', now(), 2, 1, 1, 1, 1, 1, 1),

  ('100002', 'Estudiante', 'Demo Dos', '900000005',
   'estudiante.demo2@uniminuto.edu.co', crypt('Demo1234', gen_salt('bf', 10)),
   'Pregrado', TRUE, 'Limitado', NULL, 2, 1, 1, 1, 1, 1, 1);

-- Emprendimiento, acta y asignación ------------------------------------------------------
-- El acta está Aprobada porque BR-001 impide asignar mentor sin ella.

INSERT INTO emprendimiento
  (codigo, nombre, descripcion, redes_sociales, estado_aprobacion, es_paralelo, avance,
   etapa_emprendimiento_id_etapa_emprendimiento,
   sector_economico_id_sector_economico,
   centro_universitarios_id_centro_universitarios, usuarios_id_usuarios)
VALUES
  ('EMP-001', 'Sabor y Sabe', 'Snacks artesanales de frutos secos y granola.',
   '@saborysabe', 'Aprobado', FALSE, 0, 1, 1, 1, 4);

INSERT INTO actas
  (estado, observaciones, fecha_carga, fecha_revision,
   emprendimiento_id_emprendimiento, usuarios_id_estudiante, usuarios_id_revisor)
VALUES
  ('Aprobada', 'Acta de compromiso y confidencialidad firmada.',
   now() - INTERVAL '5 days', now() - INTERVAL '4 days', 1, 4, 1);

INSERT INTO asignaciones
  (fecha_asignacion, estado, horas_semanales,
   usuarios_id_mentor, usuarios_id_estudiante, emprendimiento_id_emprendimiento)
VALUES
  (now() - INTERVAL '3 days', 'activa', 4, 2, 4, 1);

-- Tareas del plan -----------------------------------------------------------------------

INSERT INTO tareas
  (titulo, descripcion, fecha_limite, prioridad, puntos, estado, estado_revision,
   evidencia_requerida, emprendimiento_id_emprendimiento, usuarios_id_usuarios,
   usuarios_id_creador, fase_plan_id_fase_plan)
VALUES
  ('Definir la propuesta de valor',
   'Escribir en una frase el beneficio concreto para el cliente.',
   CURRENT_DATE + 7, 'Alta', 20, 'Pendiente', 'Pendiente', TRUE, 1, 4, 2, 1),
  ('Registrar los costos del primer lote',
   'Listar insumos, cantidades y precios para calcular el costo unitario.',
   CURRENT_DATE + 14, 'Media', 15, 'En curso', 'En revisión', TRUE, 1, 4, 2, 2);

-- Banco de preguntas del diagnóstico (22) ------------------------------------------------
-- Sección 1 · Perfil del emprendimiento

INSERT INTO preguntas_diagnostico (seccion, orden, enunciado, tipo, opciones, activa, origen) VALUES
  (1, 1, '¿Cuál es el nombre de tu emprendimiento?', 'Texto', NULL, TRUE, 'Prototipo'),
  (1, 2, '¿Qué tipo de emprendimiento es?', 'Selección única',
   'Pequeño|Escalable|Social|Ambiental|Cultural|Intraemprendimiento', TRUE, 'Prototipo'),
  (1, 3, '¿A qué sector productivo pertenece?', 'Selección única',
   'Sector primario|Sector secundario|Sector terciario|Sector cuaternario|Sector quinario', TRUE, 'Prototipo'),
  (1, 4, '¿Qué producto o servicio ofreces?', 'Texto largo', NULL, TRUE, 'Prototipo'),
  -- Las opciones usan el catálogo `etapaemprendimiento` y no los alias del prototipo
  -- (defecto #6 de §8: "FASE 2 - Ejecución" no es un valor canónico).
  (1, 5, '¿En qué etapa del programa está tu emprendimiento?', 'Selección única',
   'FASE 1 - Ideación|FASE 2 - Prototipo|FASE 3 - Validación|FASE 4 - Formalización', TRUE, 'Prototipo');

-- Sección 2 · Problema o necesidad
INSERT INTO preguntas_diagnostico (seccion, orden, enunciado, tipo, opciones, activa, origen) VALUES
  (2, 1, '¿Qué problema concreto resuelve tu producto o servicio?', 'Texto largo', NULL, TRUE, 'Prototipo'),
  (2, 2, '¿A quién le ocurre ese problema?', 'Texto', NULL, TRUE, 'Prototipo'),
  (2, 3, '¿Cómo lo resuelven hoy (sin tu producto)?', 'Texto', NULL, TRUE, 'Prototipo'),
  (2, 4, '¿Qué tan urgente es el problema para tu cliente?', 'Selección única',
   'Baja|Media|Alta', TRUE, 'Prototipo');

-- Sección 3 · Propuesta de valor
INSERT INTO preguntas_diagnostico (seccion, orden, enunciado, tipo, opciones, activa, origen) VALUES
  (3, 1, '¿Cuál es tu propuesta de valor en una frase?', 'Texto largo', NULL, TRUE, 'Prototipo'),
  (3, 2, '¿Qué beneficio concreto entrega al cliente?', 'Texto', NULL, TRUE, 'Prototipo'),
  (3, 3, '¿Qué te diferencia de la competencia?', 'Selección única',
   'Precio|Calidad|Sostenibilidad|Cercanía con el cliente', TRUE, 'Prototipo'),
  (3, 4, '¿Qué necesidad principal cubre?', 'Selección única',
   'Salud|Comodidad|Precio|Sabor', TRUE, 'Prototipo');

-- Sección 4 · Mercado objetivo
INSERT INTO preguntas_diagnostico (seccion, orden, enunciado, tipo, opciones, activa, origen) VALUES
  (4, 1, '¿Quién es tu cliente ideal (perfil)?', 'Texto', NULL, TRUE, 'Prototipo'),
  (4, 2, '¿Cuántos clientes potenciales estimas?', 'Texto', NULL, TRUE, 'Prototipo'),
  (4, 3, '¿Cuál es tu estrategia de precio?', 'Selección única',
   'Economía (bajo costo)|Valor medio|Premium', TRUE, 'Prototipo'),
  (4, 4, '¿Qué canales usarás para llegarles?', 'Texto', NULL, TRUE, 'Prototipo');

-- Sección 5 · Capacidad operativa y financiera
INSERT INTO preguntas_diagnostico (seccion, orden, enunciado, tipo, opciones, activa, origen) VALUES
  (5, 1, '¿Con cuántas personas cuenta el equipo?', 'Selección única',
   '1 (fundador/a)|2 - 3|4 - 5|Más de 5', TRUE, 'Prototipo'),
  (5, 2, '¿Cuál es tu capacidad de producción actual?', 'Texto', NULL, TRUE, 'Prototipo'),
  (5, 3, '¿Llevas registro de costos y ventas?', 'Selección única',
   'No|Básico (cuaderno)|Completo (planilla)', TRUE, 'Prototipo'),
  (5, 4, '¿Qué inversión necesitas para crecer?', 'Texto', NULL, TRUE, 'Prototipo'),
  (5, 5, '¿Cuál es tu meta de ventas del próximo mes?', 'Texto', NULL, TRUE, 'Prototipo');
