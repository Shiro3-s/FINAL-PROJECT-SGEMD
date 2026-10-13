# -*- coding: utf-8 -*-
"""Rol DOCENTE - 12 pantallas.

Reglas del rol:
  - Solo ve los emprendimientos que tiene asignados.
  - Registra y califica avances; el estudiante solo consulta su historial.
  - Confirma fecha y hora de la asesoría que el estudiante solicitó (BR-002).
  - Revisa el diagnóstico y deja recomendaciones; el estudiante lo responde.
"""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, ico, lista_avisos, tarjeta_emp,
    kanban,
)
from lib_charts import barras, barras_h, donut, stacked_tareas, AZUL, AMAR

R = "docente"

ESTADOS_AS = {
    "Confirmada": "b-azul",
    "Finalizada": "b-linea",
    "Pendiente de confirmar": "b-amarillo",
    "Cancelada por el estudiante": "b-neutra",
}

ASESORIAS = [
    ("ASES-014", "Sabor y Sabe", "Mariana Lopez", "Alimentos",
     "Confirmada", "12 nov 2024, 10:00", "Modalidad mixta"),
    ("ASES-013", "Krea Textil", "Jhon Ospina", "Moda",
     "Confirmada", "14 nov 2024, 15:30", "Virtual"),
    ("ASES-012", "EcoPack", "Lucia Fernandez", "Ambiental",
     "Pendiente de confirmar", "20 nov 2024, 09:00", "Presencial"),
    ("ASES-011", "Sabor y Sabe", "Mariana Lopez", "Alimentos",
     "Finalizada", "05 nov 2024, 10:00", "Presencial"),
    ("ASES-010", "Krea Textil", "Jhon Ospina", "Moda",
     "Finalizada", "31 oct 2024, 14:00", "Virtual"),
    ("ASES-009", "EcoPack", "Lucia Fernandez", "Ambiental",
     "Cancelada por el estudiante", "28 oct 2024, 11:00", "Presencial"),
]

ASIGNADOS = [
    ("Sabor y Sabe", "Mariana Lopez", "Alimentos", "FASE 2 - Prototipo", 62,
     "ASES-014 confirmada", "12 nov 2024"),
    ("Krea Textil", "Jhon Ospina", "Moda", "FASE 1 - Ideación", 28,
     "ASES-013 confirmada", "14 nov 2024"),
    ("EcoPack", "Lucia Fernandez", "Ambiental", "FASE 3 - Validación", 84,
     "Sin asesoría activa", "09 nov 2024"),
    ("Aromas del Sur", "Sofia Ramirez", "Alimentos", "FASE 1 - Ideación", 15,
     "Sin asesoría activa", "06 nov 2024"),
    ("Muebles Origen", "Andres Felipe", "Muebles", "FASE 2 - Prototipo", 55,
     "ASES-008 confirmada", "04 nov 2024"),
]

SEGUIMIENTO = [
    ("Mariana Lopez", "Sabor y Sabe", 62, "12 nov 2024", True),
    ("Jhon Ospina", "Krea Textil", 28, "11 nov 2024", False),
    ("Lucia Fernandez", "EcoPack", 84, "09 nov 2024", True),
    ("Sofia Ramirez", "Aromas del Sur", 15, "06 nov 2024", False),
    ("Andres Felipe", "Muebles Origen", 55, "04 nov 2024", True),
]

FASES = [
    "FASE 1 - Ideación",
    "FASE 2 - Prototipo",
    "FASE 3 - Validación",
    "FASE 4 - Formalización",
]


def _b(icono, etiqueta):
    return boton_accion(icono, etiqueta)


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _barra(pct):
    return ('<div class="barra" style="min-width:110px"><span style="width:%d%%"></span></div>'
            '<span style="font-size:13px;color:#162644">%d%%</span>' % (pct, pct))


def registrar(reg):
    paginas_doc = [
        ("dashboard.html", "21 Docente - Inicio (dashboard)", dashboard),
        ("asesorias.html", "22 Docente - Mis asesorías", asesorias),
        ("asesoria-form.html", "23 Docente - Registrar asesoría", asesoria_form),
        ("emprendimientos.html", "24 Docente - Emprendimientos asignados", emprendimientos),
        ("emprendimiento-expediente.html", "25 Docente - Expediente del emprendimiento",
         emprendimiento_expediente),
        ("seguimiento.html", "26 Docente - Seguimiento (lista)", seguimiento),
        ("seguimiento-dashboard.html", "27 Docente - Tablero de seguimiento",
         seguimiento_dashboard),
        ("seguimiento-notas.html", "28 Docente - Registrar avance y calificar",
         seguimiento_notas),
        ("diagnostico.html", "29 Docente - Revisión del diagnóstico", diagnostico),
        ("tareas.html", "30 Docente - Tareas asignadas", tareas),
        ("perfil.html", "31 Docente - Mi perfil", perfil),
        ("notificaciones.html", "32 Docente - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_doc):
        reg("docente", arch, tit, fn, i)


def _btn(icono, texto, clase="btn btn-primario"):
    return '<a class="%s" href="#">%s %s</a>' % (clase, ico(icono, 16), texto)


# --- 21. Dashboard -----------------------------------------------------------
def dashboard():
    cuerpo = metricas([
        ("maleta", "Emprendimientos asignados", "8", "", 62, "+2 este mes"),
        ("chat", "Asesorías del mes", "14", "", 78, "+4"),
        ("checklist", "Tareas por revisar", "9", "", 45, None),
        ("trend", "Avances registrados", "23", "", 88, "+7"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Avance por emprendimiento", barras_h(
        "", "", [a[0] for a in ASIGNADOS], [a[4] for a in ASIGNADOS],
        maximo=100, unidad="%"))
    cuerpo += card("Actividad reciente", tabla(
        ["Fecha", "Emprendimiento", "Accion registrada", "@ACC"],
        [["12 nov 2024", "Sabor y Sabe", "Registraste un avance de fase",
          _acc(_b("eye", "Ver detalle"))],
         ["11 nov 2024", "Krea Textil", "Calificaste una tarea con 92 de 100",
          _acc(_b("eye", "Ver detalle"))],
         ["11 nov 2024", "EcoPack", "Confirmaste la asesoría del 20 de noviembre",
          _acc(_b("eye", "Ver detalle"))],
         ["08 nov 2024", "Sabor y Sabe", "Asignaste la tarea de evidencia fotografica",
          _acc(_b("eye", "Ver detalle"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Compromisos de hoy", lista_def([
        ("Asesorías por confirmar", "1 pendiente"),
        ("Evidencias por revisar", "3 archivos"),
        ("Avances sin calificar", "2 entregas"),
    ]))
    cuerpo += card("Carga semanal", stacked_tareas(
        [("Prioridad alta", 9, AZUL), ("Prioridad media", 14, "#162644"),
         ("Prioridad baja", 5, "#bbbbbb")], "tareas"))
    cuerpo += "</div></div>"
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama de tus emprendimientos asignados y tu carga de trabajo.",
                 acciones=_btn("plus", "Registrar asesoría").replace('href="#"',
                                                                    'href="asesoria-form.html"'))


# --- 22. Mis asesorias -------------------------------------------------------
def asesorias():
    filas = []
    for cod, emp, estu, sector, estado, fecha, mod in ASESORIAS:
        filas.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % emp, estu, sector,
            badge(estado, ESTADOS_AS[estado]), fecha, mod,
            _acc(_b("eye", "Ver detalle"), _b("edit", "Editar")),
        ])
    filtros = ('<select class="filtro" aria-label="Filtrar por estado">'
               "<option>Todos los estados</option><option>Confirmada</option>"
               "<option>Pendiente de confirmar</option><option>Finalizada</option></select>"
               '<select class="filtro" aria-label="Filtrar por emprendimiento">'
               "<option>Todos los emprendimientos</option><option>Sabor y Sabe</option>"
               "<option>Krea Textil</option><option>EcoPack</option></select>")
    cuerpo = callout(
        "Como docente tú confirmas la <b>fecha y la hora</b> que el estudiante solicitó. "
        "El estudiante no puede agendar por su cuenta.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += toolbar(filtros=filtros)
    cuerpo += tabla(["Código", "Emprendimiento", "Estudiante", "Sector", "Estado",
                     "Fecha y hora", "Modalidad", "@ACC"], filas)
    cuerpo += paginas(1, 6, 24)
    return shell(R, "asesorias", "Mis asesorías", cuerpo,
                 migas=["Inicio", "Mis asesorías"],
                 sub="Asesorías asignadas y las que aún debes confirmar.",
                 acciones=_btn("plus", "Registrar asesoría").replace(
                     'href="#"', 'href="asesoria-form.html"'))


# --- 23. Registrar asesoria --------------------------------------------------
def asesoria_form():
    cuerpo = steps(["Solicitud recibida", "Confirmar fecha", "Registrar sesión",
                    "Cerrar asesoría"], 1)
    cuerpo += '<div style="height:22px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Solicitud del estudiante", lista_def([
        ("Estudiante", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Fecha preferida", "20 de noviembre de 2024"),
        ("Horario preferido", "Mañana, 09:00 a 11:00"),
        ("Temas sugeridos", "Presupuesto y punto de equilibrio"),
    ]))
    cuerpo += card("Datos de la asesoría",
                   campo("Emprendimiento", valor="Sabor y Sabe",
                         bloqueo="Solo tus emprendimientos asignados"))
    cuerpo += card("Confirmación de agenda",
                   campo("Fecha", tipo="date", valor="2024-11-20", req=True,
                         ayuda="La fecha propuesta por el estudiante fue el 20 de noviembre.")
                   + campo("Hora", tipo="time", valor="10:00", req=True)
                   + select("Modalidad", ["Presencial", "Virtual", "Modalidad mixta"],
                            req=True, valor="Modalidad mixta")
                   + campo("Lugar o enlace",
                           valor="Sala 3 del bloque B / meet.sgemd.edu.co/ases-014"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Temas a trabajar", campo(
        "Contenido de la sesión", alto=True,
        valor="Presupuesto de insumos, punto de equilibrio y canal de venta en el campus.",
        ph="Que temas se van a trabajar"))
    cuerpo += card("Acciones", '<div style="display:flex;flex-direction:column;gap:10px">'
                 + _btn("check", "Confirmar y notificar")
                 + _btn("calendar", "Proponer otra fecha", "btn btn-secundario")
                 + _btn("x", "Rechazar solicitud", "btn btn-secundario")
                 + "</div>"
                 + '<div class="nota-foot">Al confirmar, el estudiante recibe la '
                   "notificación con la fecha, la hora y el lugar.</div>")
    cuerpo += "</div></div>"
    return shell(R, "asesorias", "Registrar asesoría", cuerpo,
                 migas=["Inicio", "Mis asesorías", "Registrar asesoría"],
                 sub="Confirma la fecha solicitada y deja el acta de la sesión.",
                 acciones='<a class="btn btn-secundario" href="asesorias.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 24. Emprendimientos asignados -------------------------------------------
def emprendimientos():
    """Tarjetas con avance: el docente elige sobre cuales trabaja."""
    cuerpo = callout(
        "Solo aparecen los <b>8 emprendimientos</b> que tienes asignados. No puedes "
        "agregar ni reasignar estudiantes.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("maleta", "Asignados", "8", "", 62, None),
        ("trend", "En fase 2 o 3", "5", "", 70, None),
        ("alerta", "Requieren atención", "2", "", 25, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="emp-grid">'
    for emp, estu, sector, etapa, avance, asesoria, act in ASIGNADOS:
        pie = ('<a class="btn btn-sm btn-secundario" href="emprendimiento-expediente.html">'
               'Abrir expediente</a>')
        cuerpo += tarjeta_emp("maleta", emp,
                              "%s · %s" % (estu, sector), avance,
                              etapa, "%d%%" % avance, pie)
    cuerpo += "</div>"
    cuerpo += ("<p class=\"nota-foot\">Última actividad registrada en el expediente "
               "de cada estudiante.</p>")
    return shell(R, "emprendimientos", "Emprendimientos asignados", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados"],
                 sub="Los 8 emprendimientos que tienes asignados.")


# --- 25. Expediente ----------------------------------------------------------
def emprendimiento_expediente():
    """Expediente académico del docente: lo que califica y su evidencia."""
    cuerpo = metricas([
        ("trend", "Avance de fase", "62", "%", 62, "FASE 2 - Prototipo"),
        ("medalla", "Promedio de calificación", "87", "/ 100", 87,
         "3 avances calificados"),
        ("clipboard", "Tareas con evidencia", "9", "/ 11", 82, "2 sin adjuntar"),
        ("checklist", "Calificaciones por hacer", "2", "", 20, "Vence el 12 nov"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Historial de avances calificados", tabla(
        ["Fecha", "Fase", "Descripción del avance", "Calificación", "@ACC"],
        [["12 nov 2024", "FASE 2", "Prototipo de empaque listo para 20 unidades",
          badge("92 de 100", "b-azul"), _acc(_b("eye", "Ver detalle"))],
         ["05 nov 2024", "FASE 2", "Definición de precios y punto de equilibrio",
          badge("88 de 100", "b-azul"), _acc(_b("eye", "Ver detalle"))],
         ["28 oct 2024", "FASE 1", "Diagnóstico inicial y problema claro",
          badge("81 de 100", "b-azul"), _acc(_b("eye", "Ver detalle"))]]))
    cuerpo += card("Tareas por calificar", kanban([
        ("Por calificar", [
            ("Evidencia fotografica del punto de venta",
             "Sabor y Sabe · Vence 12 nov 2024",
             badge("Alta", "b-amarillo"),
             '<a class="btn btn-sm btn-primario" href="tareas.html">'
             'Calificar</a>'),
        ]),
        ("Devueltas al estudiante", [
            ("Presupuesto de insumos", "Sabor y Sabe · Faltan soportes",
             badge("Media", "b-linea"),
             '<a class="btn btn-sm btn-secundario" href="tareas.html">'
             'Ver</a>'),
        ]),
        ("Calificadas", [
            ("Perfil en redes sociales", "Calificada el 09 nov 2024",
             badge("Completada", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="tareas.html">'
             'Ver</a>'),
        ]),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Estudiante", "Mariana Lopez"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<a class="btn btn-primario" href="seguimiento-notas.html">%s Registrar avance</a>'
                     % ico("edit", 16)
                   + '<a class="btn btn-secundario" href="tareas.html">%s Revisar tareas</a>'
                     % ico("checklist", 16)
                   + '<a class="btn btn-secundario" href="asesoria-form.html">%s Registrar asesoría</a>'
                     % ico("chat", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "emprendimientos", "Sabor y Sabe", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados", "Sabor y Sabe"],
                 sub="Expediente académico de Mariana Lopez: avances y calificaciones.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 26. Seguimiento (lista) -------------------------------------------------
def seguimiento():
    filas = []
    for estu, emp, avance, act, evid in SEGUIMIENTO:
        filas.append([
            "<b>%s</b>" % estu, emp, _barra(avance), act,
            badge("Con evidencia" if evid else "Sin evidencia",
                  "b-azul" if evid else "b-amarillo"),
            _acc(_b("edit", "Registrar avance"), _b("eye", "Ver historial")),
        ])
    cuerpo = callout(
        "Registra aquí el avance de fase de cada estudiante. El estudiante solo puede "
        "<b>consultar</b> su historial.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += toolbar()
    cuerpo += tabla(["Estudiante", "Emprendimiento", "Avance", "Último registro",
                     "Evidencia", "@ACC"], filas)
    cuerpo += paginas(1, 5, 8)
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Registra avances y califica entregas de tus estudiantes.",
                 acciones='<a class="btn btn-primario" href="seguimiento-dashboard.html">'
                          "%s Ver tablero</a>" % ico("grid", 16))


# --- 27. Tablero de seguimiento ----------------------------------------------
def seguimiento_dashboard():
    cuerpo = metricas([
        ("trend", "Avances este mes", "23", "", 88, "+7"),
        ("checklist", "Sin calificar", "2", "", 22, None),
        ("alerta", "Sin evidencia", "3", "", 34, None),
        ("medalla", "Promedio de calificación", "89", "", 89, "+2"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Avance de fase por emprendimiento", barras_h(
        "", "", [a[0] for a in ASIGNADOS], [a[4] for a in ASIGNADOS],
        maximo=100, unidad="%"))
    cuerpo += card("Calificaciones por estudiante", barras(
        "", "", ["Mariana L.", "Jhon O.", "Lucia F.", "Sofia R.", "Andres F."],
        [92, 85, 95, 78, 88], maximo=100, unidad=" de 100"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Distribución de avances", donut(
        "", "", [("Con evidencia", 18, AZUL), ("Sin evidencia", 5, AMAR)], "avances"))
    cuerpo += card("Pendientes por orden de prioridad", lista_def([
        ("Evidencias por revisar", "3 archivos"),
        ("Avances sin calificar", "2 entregas"),
        ("Asesorías por confirmar", "1 solicitud"),
    ]))
    cuerpo += "</div></div>"
    return shell(R, "seguimiento", "Tablero de seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Tablero"],
                 sub="Vista agregada del avance de tus estudiantes.",
                 acciones='<a class="btn btn-primario" href="seguimiento-notas.html">'
                          "%s Registrar avance</a>" % ico("edit", 16))


# --- 28. Registrar avance y calificar ----------------------------------------
def seguimiento_notas():
    cuerpo = '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Registro de avance", campo(
        "Emprendimiento", valor="Sabor y Sabe",
        bloqueo="Solo tus emprendimientos asignados"))
    cuerpo += card("Datos del avance",
                   select("Fase alcanzada", FASES, req=True, valor="FASE 2 - Prototipo")
                   + campo("Fecha del avance", tipo="date", valor="2024-11-12", req=True)
                   + campo("Descripción del avance", alto=True,
                           valor="Prototipo de empaque listo para 20 unidades y prueba "
                                 "de precios en el campus.",
                           ph="Que se avanzo en esta fase"))
    cuerpo += card("Calificación",
                   callout("La calificación es opcional. Si la omites, el estudiante "
                           "no vera un puntaje.", "bombilla")
                   + campo("Puntaje", tipo="number", valor="92", ph="De 0 a 100")
                   + campo("Comentario para el estudiante", alto=True,
                           valor="Buen trabajo en la definición de precios. Para la "
                                 "siguiente fase falta medir el costo de los empaques.",
                           ph="Retroalimentacion"))
    cuerpo += '<div style="display:flex;gap:10px;justify-content:flex-end">'
    cuerpo += '<button class="btn btn-secundario">%s Guardar borrador</button>' % ico("doc", 16)
    cuerpo += '<button class="btn btn-primario">%s Registrar avance</button>' % ico("check", 16)
    cuerpo += "</div></div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Evidencia adjunta", estado_vacio(
        "Sin archivos adjuntos",
        "El estudiante puede adjuntar hasta 3 archivos como evidencia del avance.",
        '<button class="btn btn-secundario">%s Adjuntar archivo</button>' % ico("upload", 16),
        "clipboard"))
    cuerpo += card("Historial reciente", lista_def([
        ("12 nov 2024", "FASE 2 - Calificado 92 de 100"),
        ("05 nov 2024", "FASE 2 - Calificado 88 de 100"),
        ("28 oct 2024", "FASE 1 - Calificado 81 de 100"),
    ]))
    cuerpo += "</div></div>"
    return shell(R, "seguimiento", "Registrar avance", cuerpo,
                 migas=["Inicio", "Seguimiento", "Registrar avance"],
                 sub="Registra el avance de fase y califica la entrega del estudiante.",
                 acciones='<a class="btn btn-secundario" href="seguimiento.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 29. Revision del diagnostico --------------------------------------------
def diagnostico():
    cuerpo = callout(
        "Como docente <b>revisas</b> el diagnóstico y dejas recomendaciones. "
        "El cuestionario lo responde el estudiante.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Comportamiento entrepreneurial del estudiante", barras_h(
        "", "", ["Visión", "Creatividad", "Resiliencia", "Liderazgo",
                 "Trabajo en equipo", "Toma de decisiones"],
        [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
    cuerpo += card("Tus recomendaciones", campo(
        "Recomendaciones", alto=True,
        valor="Definir con más precisión el canal de venta digital y separar el "
              "presupuesto de insumos del de publicidad.",
        ph="Que debe reforzar el estudiante"))
    cuerpo += '<div style="display:flex;gap:10px;justify-content:flex-end">'
    cuerpo += '<button class="btn btn-secundario">%s Descargar PDF</button>' % ico("download", 16)
    cuerpo += '<button class="btn btn-primario">%s Guardar recomendaciones</button>' % ico("check", 16)
    cuerpo += "</div></div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Resumen", lista_def([
        ("Estudiante", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Respondido", "28 oct 2024, 09:14"),
        ("Puntaje heuristics", "7.8 de 10"),
    ]))
    cuerpo += card("Pendientes de revisión", tabla(
        ["Estudiante", "Emprendimiento", "Fecha", "@ACC"],
        [["Jhon Ospina", "Krea Textil", "30 oct 2024", _acc(_b("eye", "Revisar"))],
         ["Sofia Ramirez", "Aromas del Sur", "02 nov 2024", _acc(_b("eye", "Revisar"))]]))
    cuerpo += "</div></div>"
    return shell(R, "diagnostico", "Revisión del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico"],
                 sub="Revisa los resultados y deja recomendaciones al estudiante.")


# --- 30. Tareas asignadas ----------------------------------------------------
def tareas():
    filas = [
        ["<b>Evidencia fotografica del punto de venta</b>", "Sabor y Sabe", "Mariana Lopez",
         badge("Alta", "b-amarillo"), "12 nov 2024", badge("En revisión", "b-amarillo"),
         _acc(_b("check", "Calificar"), _b("eye", "Ver evidencia"))],
        ["<b>Presupuesto de insumos</b>", "Sabor y Sabe", "Mariana Lopez",
         badge("Media", "b-amarillo"), "15 nov 2024", badge("Completada", "b-azul"),
         _acc(_b("check", "Calificar"))],
        ["<b>Perfil en redes sociales</b>", "Krea Textil", "Jhon Ospina",
         badge("Baja", "b-linea"), "16 nov 2024", badge("Pendiente", "b-neutra"),
         _acc(_b("check", "Calificar"))],
        ["<b>Prototipo de empaque</b>", "EcoPack", "Lucia Fernandez",
         badge("Alta", "b-amarillo"), "14 nov 2024", badge("En revisión", "b-amarillo"),
         _acc(_b("check", "Calificar"), _b("eye", "Ver evidencia"))],
        ["<b>Análisis de competencia</b>", "Aromas del Sur", "Sofia Ramirez",
         badge("Media", "b-amarillo"), "18 nov 2024", badge("Pendiente", "b-neutra"),
         _acc(_b("check", "Calificar"))],
    ]
    filtros = ('<select class="filtro" aria-label="Filtrar por estado">'
               "<option>Todos los estados</option><option>Pendiente</option>"
               "<option>En revisión</option><option>Completada</option></select>"
               '<select class="filtro" aria-label="Filtrar por prioridad">'
               "<option>Toda la prioridad</option><option>Alta</option>"
               "<option>Media</option><option>Baja</option></select>")
    cuerpo = callout("La tarea se considera <b>completada</b> cuando el estudiante "
                     "adjunta al menos una evidencia.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += toolbar(filtros=filtros)
    cuerpo += tabla(["Tarea", "Emprendimiento", "Estudiante", "Prioridad", "Vence",
                     "Estado", "@ACC"], filas)
    cuerpo += paginas(1, 5, 23)
    return shell(R, "tareas", "Tareas asignadas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Revisa y califica las entregas con evidencia de tus estudiantes.",
                 acciones='<button class="btn btn-primario">%s Asignar tarea</button>'
                          % ico("plus", 16))


# --- 31. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = metricas([
        ("maleta", "Emprendimientos asignados", "8", "", 62, None),
        ("chat", "Asesorías realizadas", "31", "", 78, None),
        ("medalla", "Promedio de calificación", "89", "", 89, "+2"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos personales", campo("Nombres", valor="Carlos Alejandro")
                   + campo("Apellidos", valor="Mendoza Rios")
                   + campo("Correo institucional", valor="carlos.mendoza@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Teléfono", valor="+57 300 555 0142")
                   + campo("Área de conocimiento", valor="Emprendimientos innovate"))
    cuerpo += card("Zona horaria y firma", campo("Zona horaria", valor="America/Bogota")
                   + campo("Firmaelectronica",
                           valor="Carlos Mendoza - Docente de Emprendimientos",
                           bloqueo="La firmaelectronica se solicita al programa"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Seguridad", lista_def([
        ("Contraseña", "Actualizada hace 3 meses"),
        ("Verificación en dos pasos", "Activada"),
        ("Último acceso", "Hoy, 07:42"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Guardar cambios</button>'
                     % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Cambiar contraseña</button>'
                     % ico("lock", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Actualiza tus datos de contacto y revisa tu actividad.")


# --- 32. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja del docente: lista agrupada por urgencia, no tabla.

    El docente actua sobre lo que tiene que hacer hoy, asi que la pantalla se
    ordena por urgencia y cada aviso abre la tarea donde resolverlo.
    """
    grupos = [
        ("Vencido", [
            ("alerta", "Tarea vencida: perfil en redes sociales",
             "Tareas · Sabor y Sabe · Vencio el 09 nov 2024",
             "tareas.html", "alta",
             '<a class="btn btn-sm btn-primario" href="tareas.html">Revisar</a>'
             + _b("check", "Marcar como leída")),
            ("reloj", "Revisión de diagnóstico pendiente",
             "Emprendimientos · Krea Textil · Sin revisar hace 3 días",
             "diagnostico.html", "alta",
             '<a class="btn btn-sm btn-primario" href="diagnostico.html">Revisar</a>'
             + _b("check", "Marcar como leída")),
        ]),
        ("Hoy", [
            ("bell", "Solicitud de asesoría de Mariana Lopez",
             "Asesorías · Modalidad mixta · 10:00",
             "asesorias.html", "media",
             '<a class="btn btn-sm btn-primario" href="asesorias.html">Confirmar</a>'
             + _b("check", "Marcar como leída")),
            ("upload", "Evidencia enviada: Sabor y Sabe",
             "Seguimiento · Prototipo · Entregada 16:40",
             "seguimiento-notas.html", "media",
             '<a class="btn btn-sm btn-primario" href="seguimiento-notas.html">Calificar</a>'
             + _b("check", "Marcar como leída")),
        ]),
        ("Recientes", [
            ("check", "Asesoría finalizada con EcoPack",
             "Asesorías · 05 nov 2024 · Modalidad presencial",
             "asesorias.html", "baja", ""),
            ("users", "Nuevo estudiante asignado: Aromas del Sur",
             "Emprendimientos · Fase 1 - Ideación · 06 nov 2024",
             "emprendimientos.html", "baja", ""),
        ]),
    ]
    cuerpo = metricas([
        ("alerta", "Requieren accion hoy", "2", "", 40, None),
        ("bell", "Pendientes de revisión", "2", "", 25, None),
        ("check", "Resueltas este mes", "18", "", 90, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += lista_avisos(grupos)
    cuerpo += '<p class="nota-foot">Las notificaciones se archivan solas '\
              '30 días después de resolverse.</p>'
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Lo que debes revisar, ordenado por urgencia.",
                 acciones='<button class="btn btn-secundario">%s Marcar todo '
                          'como leído</button>' % ico("check", 16))