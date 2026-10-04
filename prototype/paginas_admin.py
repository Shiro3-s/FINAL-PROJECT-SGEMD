# -*- coding: utf-8 -*-
"""Rol ADMINISTRADOR - 18 pantallas.

Reglas del rol:
  - Gestiona perfiles de docentes y estudiantes, y sus asignaciones.
  - Aprueba solicitudes, crea eventos y modera comentarios.
  - Ve el seguimiento de todos los emprendimientos, no solo los asignados.
  - Exporta reportes en CSV y PDF.
"""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, ico, agenda, distribucion,
    lista_avisos, kanban, linea_tiempo,
)
from lib_charts import barras, barras_h, lineas, donut, AZUL, AMAR

R = "administrador"

BADGE = {
    "activo": "b-azul",
    "confirmado": "b-azul",
    "finalizada": "b-linea",
    "en revision": "b-amarillo",
    "pendiente": "b-amarillo",
    "vencido": "b-amarillo",
    "aprobado": "b-azul",
    "rechazado": "b-neutra",
    "en espera": "b-amarillo",
    "borrado": "b-neutra",
    "visible": "b-azul",
    "oculto": "b-neutra",
}

ETAPAS = ["FASE 1 - Ideacion", "FASE 2 - Prototipo",
          "FASE 3 - Validacion", "FASE 4 - Formalizacion"]

DOCENTES = [
    ("DOC-014", "Carlos Mendoza", "carlos.mendoza@sgemd.edu.co", "Alimentos",
     "3 h", "8", "Activo"),
    ("DOC-013", "Paula Andrea Rios", "paula.rios@sgemd.edu.co", "Moda",
     "2h", "5", "Activo"),
    ("DOC-012", "Hector Vargas", "hector.vargas@sgemd.edu.co", "Muebles",
     "4h", "6", "Activo"),
    ("DOC-011", "Ninafq Beltran", "nina.beltran@sgemd.edu.co", "Ambiental",
     "3h", "7", "Inactivo"),
    ("DOC-010", "Rafael Nieto", "rafael.nieto@sgemd.edu.co", "Tecnologia",
     "5h", "4", "Activo"),
]

ESTUDIANTES = [
    ("EST-087", "Mariana Lopez", "Alimentos", "Sabor y Sabe",
     "FASE 2 - Prototipo", 62, "Activo"),
    ("EST-086", "Jhon Ospina", "Moda", "Krea Textil",
     "FASE 1 - Ideacion", 28, "Activo"),
    ("EST-085", "Lucia Fernandez", "Ambiental", "EcoPack",
     "FASE 3 - Validacion", 84, "Activo"),
    ("EST-084", "Sofia Ramirez", "Alimentos", "Aromas del Sur",
     "FASE 1 - Ideacion", 15, "Activo"),
    ("EST-083", "Andres Felipe", "Muebles", "Muebles Origen",
     "FASE 2 - Prototipo", 55, "Inactivo"),
]

EMPRENDIMIENTOS = [
    ("EMP-041", "Sabor y Sabe", "Mariana Lopez", "Alimentos", "Comercio",
     "FASE 2 - Prototipo", 62, "Carlos Mendoza"),
    ("EMP-040", "Krea Textil", "Jhon Ospina", "Moda", "Moda",
     "FASE 1 - Ideacion", 28, "Paula Andrea Rios"),
    ("EMP-039", "EcoPack", "Lucia Fernandez", "Ambiental", "Industrial",
     "FASE 3 - Validacion", 84, "Hector Vargas"),
    ("EMP-038", "Aromas del Sur", "Sofia Ramirez", "Alimentos", "Alimentos",
     "FASE 1 - Ideacion", 15, "Sin asignar"),
    ("EMP-037", "Muebles Origen", "Andres Felipe", "Muebles", "Artesanal",
     "FASE 2 - Prototipo", 55, "Ninafq Beltran"),
]


def _b(icono, etiqueta):
    return boton_accion(icono, etiqueta)


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _barra(pct):
    return ('<div class="barra" style="min-width:110px"><span style="width:%d%%"></span></div>'
            '<span style="font-size:13px;color:#162644">%d%%</span>' % (pct, pct))


def _sel(etiqueta, opciones, extra=""):
    return '<select class="filtro" aria-label="%s">%s%s</select>' % (
        etiqueta, "".join("<option>%s</option>" % o for o in opciones), extra)


def registrar(reg):
    paginas_adm = [
        ("dashboard.html", "33 Administrador - Inicio (dashboard)", dashboard),
        ("usuarios.html", "34 Administrador - Gestion de perfiles", usuarios),
        ("usuario-docente.html", "35 Administrador - Editar docente", usuario_docente),
        ("usuario-estudiante.html", "36 Administrador - Editar estudiante", usuario_estudiante),
        ("emprendimientos.html", "37 Administrador - Emprendimientos", emprendimientos),
        ("emprendimiento-plan.html", "38 Administrador - Plan de trabajo del emprendimiento",
         emprendimiento_plan),
        ("seguimiento.html", "39 Administrador - Seguimiento (lista)", seguimiento),
        ("seguimiento-dashboard.html", "40 Administrador - Tablero de seguimiento",
         seguimiento_dashboard),
        ("asignar-emprendimiento.html", "41 Administrador - Asignar emprendimiento",
         asignar_emprendimiento),
        ("comentarios.html", "42 Administrador - Moderacion de comentarios", comentarios),
        ("asesorias.html", "43 Administrador - Metricas de asesorias", asesorias),
        ("eventos.html", "44 Administrador - Eventos", eventos),
        ("evento-form.html", "45 Administrador - Crear evento", evento_form),
        ("asignaciones.html", "46 Administrador - Asignaciones", asignaciones),
        ("diagnosticos.html", "47 Administrador - Diagnosticos respondidos", diagnosticos),
        ("reportes.html", "48 Administrador - Exportar reportes", reportes),
        ("perfil.html", "49 Administrador - Mi perfil", perfil),
        ("notificaciones.html", "50 Administrador - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_adm):
        reg("admin", arch, tit, fn, i)


def _btn(icono, texto, href="#", clase="btn btn-primario"):
    return '<a class="%s" href="%s">%s %s</a>' % (clase, href, ico(icono, 16), texto)


# --- 33. Dashboard -----------------------------------------------------------
def dashboard():
    cuerpo = metricas([
        ("users", "Usuarios activos", "128", "", 84, "+12 este mes"),
        ("maleta", "Emprendimientos", "46", "", 72, "+5"),
        ("trend", "Avances del mes", "61", "", 88, "+14"),
        ("medalla", "Tasa de cierre", "78", "%", 78, "+3"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Avance de fase por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [12, 19, 27, 41, 61],
        unidad=" avances"))
    cuerpo += card("Emprendimientos por sector", barras_h(
        "", "", ["Alimentos", "Moda", "Ambiental", "Tecnologia", "Muebles"],
        [14, 11, 9, 7, 5], color=AMAR))
    cuerpo += card("Actividad reciente", tabla(
        ["Fecha", "Accion del administrador", "@ACC"],
        [["12 nov 2024", "Asignaste EcoPack a Hector Vargas",
          _acc(_b("eye", "Ver detalle"))],
         ["12 nov 2024", "Aprobaste el evento Taller de costos",
          _acc(_b("eye", "Ver detalle"))],
         ["11 nov 2024", "Desactivaste el perfil de EST-083",
          _acc(_b("eye", "Ver detalle"))],
         ["11 nov 2024", "Moderaste 3 comentarios reportados",
          _acc(_b("eye", "Ver detalle"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Pendientes de decision", lista_def([
        ("Emprendimientos sin docente", "3"),
        ("Eventos por aprobar", "2"),
        ("Comentarios reportados", "3"),
        ("Diagnosticos sin revisar", "5"),
    ]))
    cuerpo += card("Distribucion de usuarios", donut(
        "", "", [("Docentes", 18, AZUL), ("Estudiantes", 110, AMAR)], "usuarios"))
    cuerpo += "</div></div>"
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama institucional de usuarios, emprendimientos y seguimiento.",
                 acciones=_btn("download", "Exportar reportes", "reportes.html"))


# --- 34. Gestion de perfiles -------------------------------------------------
def usuarios():
    filas_doc = []
    for cod, nom, correo, area, carga, emp, estado in DOCENTES:
        filas_doc.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % nom, correo, area,
            "%s h" % carga, emp, badge(estado, "b-azul" if estado == "Activo" else "b-neutra"),
            _acc(_b("edit", "Editar docente")),
        ])
    cuerpo = callout("Los perfiles de estudiante se editan desde su cuenta. El "
                     "administrador solo puede activar o desactivar el acceso.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("users", "Docentes", "18", "", 45, "+1"),
        ("users", "Estudiantes", "110", "", 92, "+11"),
        ("alerta", "Cuentas inactivas", "4", "", 12, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += toolbar(filtros=_sel("Filtrar area", ["Todas las areas", "Alimentos",
                                                     "Moda", "Ambiental", "Tecnologia"]))
    cuerpo += card("Docentes", tabla(
        ["Codigo", "Nombre", "Correo institucional", "Area", "Carga semanal",
         "Emprendimientos", "Estado", "@ACC"], filas_doc), sin_pad=True)
    cuerpo += card("Estudiantes", tabla(
        ["Codigo", "Nombre", "Sector", "Emprendimiento", "Etapa", "Avance", "Estado", "@ACC"],
        [[c, "<b>%s</b>" % n, sec, emp, badge(et, "b-linea"), _barra(av),
          badge(est, "b-azul" if est == "Activo" else "b-neutra"),
          _acc(_b("edit", "Editar estudiante"))] for c, n, sec, emp, et, av, est in ESTUDIANTES],
    ), sin_pad=True)
    cuerpo += paginas(1, 5, 18)
    return shell(R, "usuarios", "Gestion de perfiles", cuerpo,
                 migas=["Inicio", "Gestion de perfiles"],
                 sub="Altas, edicion y estado de acceso de docentes y estudiantes.")


# --- 35. Editar docente ------------------------------------------------------
def usuario_docente():
    cuerpo = steps(["Datos", "Area y carga", "Permisos", "Confirmar"], 1)
    cuerpo += '<div style="height:22px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos del docente",
                   campo("Codigo", valor="DOC-014", bloqueo="Codigo asignado por el sistema")
                   + campo("Nombres", valor="Carlos Alejandro", req=True)
                   + campo("Apellidos", valor="Mendoza Rios", req=True)
                   + campo("Correo institucional", tipo="email",
                           valor="carlos.mendoza@sgemd.edu.co", req=True)
                   + campo("Telefono", tipo="tel", valor="+57 300 555 0142"))
    cuerpo += card("Area y carga", select("Area de conocimiento",
                                          ["Alimentos", "Moda", "Ambiental",
                                           "Tecnologia", "Muebles"],
                                          req=True, valor="Alimentos")
                   + campo("Horas de asesoria por semana", tipo="number", valor="3",
                           ph="De 1 a 20")
                   + campo("Emprendimientos asignados", tipo="number", valor="8",
                           bloqueo="Se actualiza desde Asignaciones"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Ultimo acceso", "Hoy, 07:42"),
        ("Asesorias realizadas", "31"),
        ("Promedio de calificacion", "89 de 100"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Guardar cambios</button>'
                     % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Desactivar acceso</button>'
                     % ico("lock", 16)
                   + '<a class="btn btn-secundario" href="usuarios.html">%s Volver</a>'
                     % ico("izq", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "usuarios", "Editar docente", cuerpo,
                 migas=["Inicio", "Gestion de perfiles", "Editar docente"],
                 sub="Actualiza los datos institutionales del docente.",
                 acciones=_btn("check", "Guardar"))


# --- 36. Editar estudiante ---------------------------------------------------
def usuario_estudiante():
    cuerpo = callout("El estudiante edita su cuenta. El administrador solo puede "
                     "<b>activar o desactivar</b> el acceso.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos del estudiante",
                   campo("Codigo", valor="EST-087", bloqueo="Codigo asignado por el sistema")
                   + campo("Nombres", valor="Mariana", bloqueo="Los edita el estudiante")
                   + campo("Apellidos", valor="Lopez", bloqueo="Los edita el estudiante")
                   + campo("Correo institucional", tipo="email",
                           valor="mariana.lopez@sgemd.edu.co",
                           bloqueo="Los edita el estudiante"))
    cuerpo += card("Emprendimiento y etapa", lista_def([
        ("Emprendimiento", "Sabor y Sabe"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente asignado", "Carlos Mendoza"),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Fecha de registro", "12 mar 2024"),
        ("Ultimo acceso", "Hoy, 08:02"),
        ("Asesorias recibidas", "3"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Guardar estado</button>'
                     % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Desactivar acceso</button>'
                     % ico("lock", 16)
                   + '<a class="btn btn-secundario" href="usuarios.html">%s Volver</a>'
                     % ico("izq", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "usuarios", "Editar estudiante", cuerpo,
                 migas=["Inicio", "Gestion de perfiles", "Editar estudiante"],
                 sub="Gestiona el acceso del estudiante a la plataforma.",
                 acciones=_btn("check", "Guardar"))


# --- 37. Emprendimientos -----------------------------------------------------
def emprendimientos():
    """Registro maestro: es la tabla canonica del admin, con chips de sector."""
    cuerpo = callout("Como administrador tu ves <b>todos</b> los emprendimientos, "
                     "tengan o no docente asignado.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("maleta", "Total", "46", "", 72, "+5"),
        ("trend", "En fase 3 o 4", "18", "", 62, None),
        ("alerta", "Sin docente", "3", "", 18, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += toolbar(filtros=_sel("Filtrar sector", ["Todos los sectores", "Alimentos",
                                                      "Moda", "Ambiental", "Muebles"])
                      + _sel("Filtrar etapa", ["Todas las etapas"] + ETAPAS)
                      + _sel("Filtrar docente", ["Todos los docentes", "Sin asignar"]))
    filas = []
    for cod, emp, estu, sector, tipo, etapa, avance, docente in EMPRENDIMIENTOS:
        filas.append([
            "<b>%s</b>" % emp, cod, estu,
            badge(sector, "b-azul" if sector == "Alimentos" else
                  ("b-linea" if sector == "Ambiental" else "b-neutra")),
            tipo, badge(etapa, "b-linea"), _barra(avance),
            docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
            _acc(_b("eye", "Abrir plan"), _b("edit", "Editar")),
        ])
    cuerpo += tabla(["Emprendimiento", "Codigo", "Estudiante", "Sector", "Tipo",
                     "Etapa", "Avance", "Docente asignado", "@ACC"], filas)
    cuerpo += paginas(1, 5, 46)
    return shell(R, "emprendimientos", "Emprendimientos", cuerpo,
                 migas=["Inicio", "Emprendimientos"],
                 sub="Todos los emprendimientos registrados en el programa.",
                 acciones=_btn("sliders", "Asignar emprendimiento",
                               "asignar-emprendimiento.html", "btn btn-secundario"))


# --- 38. Plan de trabajo -----------------------------------------------------
def emprendimiento_plan():
    """Plan operativo del admin: fases, carga y estado, sin notas academicas."""
    cuerpo = metricas([
        ("layers", "Fases completadas", "1", "/ 4", 25, "FASE 2 en curso"),
        ("checklist", "Tareas en curso", "4", "/ 11", 36, "2 sin responsable"),
        ("reloj", "Dias sin avance", "6", "", 40, "Ultimo: 05 nov 2024"),
        ("calendar", "Asesorias programadas", "3", "", 60, "1 por confirmar"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Plan de trabajo por fase", tabla(
        ["Fase", "Tareas", "Completadas", "Avance", "Estado", "@ACC"],
        [[badge(ETAPAS[0], "b-linea"), "3", "3", "100%",
          badge("Finalizada", "b-azul"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[1], "b-linea"), "5", "4", "80%",
          badge("En curso", "b-amarillo"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[2], "b-linea"), "4", "1", "25%",
          badge("Pendiente", "b-neutra"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[3], "b-linea"), "2", "0", "0%",
          badge("No iniciada", "b-neutra"), _acc(_b("eye", "Ver detalle"))]]))
    cuerpo += card("Hitos de la fase actual", linea_tiempo([
        ("12", "nov", "Cierre de prototipo y control de calidad",
         "Responsable: Mariana Lopez · 5 tareas abiertas",
         '<div style="margin-top:10px">' + badge("En curso", "b-amarillo", "reloj")
         + '</div>'),
        ("20", "nov", "Revision tecnica con el docente",
         "Responsable: Carlos Mendoza · Confirmado",
         '<div style="margin-top:10px">' + badge("Confirmado", "b-azul", "check")
         + '</div>'),
        ("28", "nov", "Prueba de ventas en punto real",
         "Responsable: equipo del emprendimiento · Sin asignar",
         '<div style="margin-top:10px">' + badge("Sin asignar", "b-amarillo")
         + '</div>'),
        ("05", "dic", "Evaluacion y cierre de FASE 2",
         "Comite academico · Pendiente",
         '<div style="margin-top:10px">' + badge("Pendiente", "b-neutra")
         + '</div>'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Codigo", "EMP-041"),
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente", "Carlos Mendoza"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<a class="btn btn-primario" href="seguimiento-dashboard.html">'
                     "%s Ver seguimiento</a>" % ico("trend", 16)
                   + '<a class="btn btn-secundario" href="asignar-emprendimiento.html">'
                     "%s Reasignar docente</a>" % ico("sliders", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "emprendimientos", "Plan de trabajo", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Plan de trabajo"],
                 sub="Plan, fases y carga de trabajo del emprendimiento EMP-041.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 39. Seguimiento (lista) -------------------------------------------------
def seguimiento():
    """Salud global primero; la tabla es solo la cola de alertas."""
    cuerpo = callout("Vista institucional del seguimiento. El docente registra los "
                     "avances de los emprendimientos asignados.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("trend", "Al dia", "31", "", 68, None),
        ("alerta", "En riesgo", "9", "", 20, None),
        ("alerta", "Sin avances en 15 dias", "6", "", 13, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Salud del seguimiento", '<div class="card-body">'
                   + distribucion([
                       ("Al dia", "31", 68),
                       ("En riesgo", "9", 20),
                       ("Sin avances", "6", 13),
                   ])
                   + '<p class="nota-foot">31 de 46 emprendimientos avanzan dentro '
                     'del plazo de la fase actual.</p></div>')
    alertas = []
    for cod, emp, estu, sector, tipo, etapa, avance, docente in EMPRENDIMIENTOS:
        if avance < 60:
            alertas.append((
                "trend", "%s · %s" % (emp, estu),
                "%s · %s · %d%% de avance" % (etapa, docente, avance),
                "emprendimiento-plan.html",
                "alta" if avance < 30 else "media",
                _b("edit", "Registrar avance") + " " + _b("eye", "Ver detalle")))
    cuerpo += card("Requieren atencion (%d)" % len(alertas),
                   '<div class="card-body">'
                   + lista_avisos([("Sin avance reciente", alertas)])
                   + '</div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Docentes con mayor carga", '<div class="card-body">'
                   + distribucion([
                       ("Paula Rios", "6", 50),
                       ("Carlos Mendoza", "5", 42),
                       ("Hector Vargas", "4", 33),
                       ("Ninafq Beltran", "3", 25),
                   ]) + '</div>')
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + _btn("grid", "Ver tablero", "seguimiento-dashboard.html",
                          "btn btn-secundario")
                   + _btn("download", "Exportar", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Salud del seguimiento de los 46 emprendimientos.")


# --- 40. Tablero de seguimiento ----------------------------------------------
def seguimiento_dashboard():
    cuerpo = metricas([
        ("trend", "Avances del mes", "61", "", 88, "+14"),
        ("checklist", "Tareas sin calificar", "11", "", 34, None),
        ("alerta", "Emprendimientos en riesgo", "9", "", 20, None),
        ("medalla", "Promedio institucional", "87", "", 87, "+2"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Avance acumulado por mes", lineas(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"],
        [("Avances", [12, 19, 27, 41, 61], AZUL),
         ("Tareas", [9, 14, 20, 33, 52, ], AMAR)], unidad=""))
    cuerpo += card("Avance por emprendimiento", barras_h(
        "", "", [e[1] for e in EMPRENDIMIENTOS], [e[6] for e in EMPRENDIMIENTOS],
        maximo=100, unidad="%"))
    cuerpo += card("Rendimiento por docente", barras(
        "", "", ["C. Mendoza", "P. Rios", "H. Vargas", "N. Beltran", "R. Nieto"],
        [92, 86, 84, 78, 74], maximo=100, unidad=" de 100"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Salud de los seguimiento", donut(
        "", "", [("Al dia", 31, AZUL), ("En riesgo", 9, AMAR),
                 ("Inactivos", 6, "#bbbbbb")], "emprendimientos"))
    cuerpo += card("Acciones sugeridas", lista_def([
        ("Asignar docente a 3 emprendimientos", "Sin asignar"),
        ("Contactar 6 estudiantes inactivos", "15 dias sin avance"),
        ("Revisar 5 diagnosticos", "Sin revision"),
    ]))
    cuerpo += "</div></div>"
    return shell(R, "seguimiento", "Tablero de seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Tablero"],
                 sub="Metricas consolidadas de seguimiento institucional.",
                 acciones=_btn("download", "Exportar", "reportes.html", "btn btn-secundario"))


# --- 41. Asignar emprendimiento ---------------------------------------------
def asignar_emprendimiento():
    cuerpo = steps(["Seleccionar emprendimiento", "Elegir docente",
                    "Confirmar asignación"], 1)
    cuerpo += '<div style="height:22px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Emprendimiento sin docente", tabla(
        ["Codigo", "Emprendimiento", "Estudiante", "Sector", "Etapa", "@ACC"],
        [["EMP-038", "<b>Aromas del Sur</b>", "Sofia Ramirez", "Alimentos",
          badge("FASE 1 - Ideacion", "b-linea"), _acc(_b("check", "Seleccionar"))],
         ["EMP-036", "<b>Sabores de la Costa</b>", "Daniel Rojas", "Alimentos",
          badge("FASE 1 - Ideacion", "b-linea"), _acc(_b("check", "Seleccionar"))],
         ["EMP-034", "<b>Eco Hogar</b>", "Valeria Cruz", "Muebles",
          badge("FASE 2 - Prototipo", "b-linea"), _acc(_b("check", "Seleccionar"))]]))
    cuerpo += card("Docente disponible", tabla(
        ["Docente", "Area", "Carga actual", "Horas disponibles", "@ACC"],
        [["Carlos Mendoza", "Alimentos", "3 h de 5 h", "2 h",
          _acc(_b("check", "Seleccionar"))],
         ["Paula Andrea Rios", "Moda", "2 h de 4 h", "2 h",
          _acc(_b("check", "Seleccionar"))],
         ["Rafael Nieto", "Tecnologia", "5 h de 6 h", "1 h",
          _acc(_b("check", "Seleccionar"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Asignacion seleccionada", lista_def([
        ("Emprendimiento", "Aromas del Sur"),
        ("Estudiante", "Sofia Ramirez"),
        ("Docente", "Carlos Mendoza"),
        ("Horas asignadas", "2 h por semana"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Confirmar asignación</button>'
                     % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Cancelar</button>'
                     % ico("x", 16)
                   + "</div>"
                     '<div class="nota-foot">El docente y el estudiante reciben una '
                     "notificacion con la asignacion.</div>")
    cuerpo += "</div></div>"
    return shell(R, "asignaciones", "Asignar emprendimiento", cuerpo,
                 migas=["Inicio", "Asignaciones", "Asignar emprendimiento"],
                 sub="Asigna un docente a los emprendimientos que aun no lo tienen.",
                 acciones='<a class="btn btn-secundario" href="asignaciones.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 42. Moderacion de comentarios -------------------------------------------
def comentarios():
    """Dos colas lado a lado: lo reportado y lo visible. Sin tabla."""
    cuerpo = callout("Solo los comentarios <b>reportados</b> requieren moderacion. "
                     "Borrar un comentario es permanente.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("alerta", "Reportados", "3", "", 25, None),
        ("chat", "Visibles", "27", "", 90, "+4"),
        ("trash", "Borrados este mes", "2", "", 12, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Cola de moderacion (3)", lista_avisos([
        ("Requieren decision", [
            ("chat", "Comentario reportado en Sabor y Sabe",
             "Estudiante · EMP-041 · 12 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Lenguaje inapropiado en Krea Textil",
             "Docente · EMP-040 · 12 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Comentario duplicado en EcoPack",
             "Estudiante · EMP-039 · 11 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
        ]),
    ]))
    cuerpo += card("Publicados recientemente", '<div class="card-body">'
                   + '<div class="grid" style="gap:10px">'
                   + '<div class="fila-simple"><div><b>Consulta sobre el evento de costos</b>'
                     '<div class="nota-foot">Docente · EMP-041 · 10 nov 2024</div></div>'
                     '<div style="display:flex;gap:6px">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Sugerencia para el plan de trabajo</b>'
                     '<div class="nota-foot">Docente · EMP-037 · 09 nov 2024</div></div>'
                     '<div style="display:flex;gap:6px">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Duda sobre el costo de insumos</b>'
                     '<div class="nota-foot">Estudiante · EMP-035 · 08 nov 2024</div></div>'
                     '<div style="display:flex;gap:6px">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '</div></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Reglas de moderacion", lista_def([
        ("Reportado", "3 en cola"),
        ("Visible", "27 publicados"),
        ("Oculto", "5 ocultos"),
        ("Borrado", "2 este mes"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<a class="btn btn-primario" href="comentarios.html">%s '
                     'Moderar cola</a>' % ico("check", 16)
                   + '<a class="btn btn-secundario" href="reportes.html">%s '
                     'Ver reportes</a>' % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "comentarios", "Moderacion de comentarios", cuerpo,
                 migas=["Inicio", "Moderacion de comentarios"],
                 sub="Aprueba, oculta o borra comentarios de la comunidad.")


# --- 43. Metricas de asesorias -----------------------------------------------
def asesorias():
    cuerpo = metricas([
        ("chat", "Asesorias este mes", "38", "", 84, "+9"),
        ("reloj", "Promedio de respuesta", "4.2", " h", 42, "-0.6"),
        ("checklist", "Asesorias finalizadas", "31", "", 82, None),
        ("alerta", "Sin confirmar", "5", "", 22, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Asesorias por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [18, 24, 29, 33, 38],
        unidad=" asesorías"))
    cuerpo += card("Asesorias por sector", barras_h(
        "", "", ["Alimentos", "Moda", "Ambiental", "Muebles", "Tecnologia"],
        [16, 10, 7, 3, 2], color=AMAR))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Estado de las asesorias", donut(
        "", "", [("Finalizadas", 31, AZUL), ("Confirmadas", 7, AMAR),
                 ("Sin confirmar", 5, "#bbbbbb"), ("Canceladas", 3, "#bbbbbb")],
        "asesorias"))
    cuerpo += card("Docentes con mejor respuesta", lista_def([
        ("Hector Vargas", "1.8 h promedio"),
        ("Paula Andrea Rios", "2.4 h promedio"),
        ("Carlos Mendoza", "3.1 h promedio"),
    ]))
    cuerpo += "</div></div>"
    return shell(R, "asesorias", "Metricas de asesorias", cuerpo,
                 migas=["Inicio", "Asesorias"],
                 sub="Indicadores de uso y respuesta del servicio de asesorias.",
                 acciones=_btn("download", "Exportar", "reportes.html", "btn btn-secundario"))


# --- 44. Eventos -------------------------------------------------------------
def eventos():
    """Pipeline editorial: el admin aprueba y publica, no solo lista."""
    cuerpo = metricas([
        ("calendar", "Eventos publicados", "2", "", 40, None),
        ("reloj", "Por aprobar", "1", "", 20, None),
        ("doc", "Borradores", "1", "", 20, None),
        ("users", "Confirmaciones", "141", "", 88, "+37"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += kanban([
        ("Por aprobar", [
            ("<b>Jornada de mentoria</b>",
             "25 nov 2024, 08:30 · Sala 2 · 14 confirmados",
             badge("1 solicitud", "b-amarillo", "reloj"),
             '<a class="btn btn-sm btn-primario" href="evento-form.html">'
             'Aprobar</a>'),
        ]),
        ("Borrador", [
            ("<b>Charla: marco legal para negocios</b>",
             "02 dic 2024, 10:00 · Auditorio B",
             badge("Sin publicar", "b-neutra"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
        ]),
        ("Publicado", [
            ("<b>Taller de costos y precios</b>",
             "18 nov 2024, 09:00 · Auditorio A",
             badge("32 de 40 cupos", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
            ("<b>Feria de emprendedores</b>",
             "22 nov 2024, 14:00 · Plaza central",
             badge("86 de 120 cupos", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
        ]),
        ("Finalizados", [
            ("<b>Charla: opciones de financiamiento</b>",
             "04 nov 2024, 10:00 · Auditorio B · 48 asistentes",
             badge("Cerrado", "b-linea"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Ver</a>'),
        ]),
    ])
    cuerpo += ('<p class="nota-foot">Publicar un evento notifica a los estudiantes '
               'del sector correspondiente.</p>')
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Aprueba y publica eventos del programa.",
                 acciones=_btn("plus", "Crear evento", "evento-form.html"))


# --- 45. Crear evento --------------------------------------------------------
def evento_form():
    cuerpo = steps(["Datos del evento", "Fecha y lugar", "Publicar"], 1)
    cuerpo += '<div style="height:22px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos del evento",
                   campo("Titulo del evento", valor="Taller de costos y precios", req=True)
                   + select("Dirigido a", ["Todos los estudiantes",
                                           "Solo Alimentos", "Solo Moda",
                                           "Solo Ambiental", "Solo Muebles"],
                            req=True, valor="Alimentos")
                   + campo("Descripcion", alto=True,
                           valor="Taller practico para calcular el costo de insumos y "
                                 "definir el punto de equilibrio de un emprendimiento.",
                           ph="De que tratara el evento")
                   + campo("Cupo maximo", tipo="number", valor="40",
                           ph="Numero de asistentes"))
    cuerpo += card("Fecha y lugar",
                   campo("Fecha", tipo="date", valor="2024-11-18", req=True)
                   + campo("Hora de inicio", tipo="time", valor="09:00", req=True)
                   + campo("Hora de cierre", tipo="time", valor="11:00", req=True)
                   + campo("Lugar", valor="Auditorio A")
                   + campo("Link de inscripcion",
                           valor="sgemd.edu.co/eventos/taller-costos"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Visibilidad", lista_def([
        ("Visibilidad", "Visible para-Alimentos"),
        ("Confirmaciones", "32 de 40"),
        ("Recordatorio", "Un dia antes"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Publicar evento</button>'
                     % ico("enviar", 16)
                   + '<button class="btn btn-secundario">%s Guardar borrador</button>'
                     % ico("doc", 16)
                   + '<a class="btn btn-secundario" href="eventos.html">%s Cancelar</a>'
                     % ico("x", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "eventos", "Crear evento", cuerpo,
                 migas=["Inicio", "Eventos", "Crear evento"],
                 sub="Publica un evento y notifica a los asistentes.",
                 acciones=_btn("check", "Guardar"))


# --- 46. Asignaciones --------------------------------------------------------
def asignaciones():
    """Carga de docentes arriba, cola de asignaciones pendientes abajo."""
    cuerpo = callout("Un docente puede tener hasta <b>12 emprendimientos</b>. "
                     "La carga semanal se descuenta del cupo disponible.", "bombilla")
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += metricas([
        ("sliders", "Asignaciones vigentes", "43", "", 93, None),
        ("alerta", "Sin docente", "3", "", 18, None),
        ("reloj", "Carga promedio", "3.1", " h", 62, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Cupo ocupado por docente", '<div class="card-body">'
                   + distribucion([
                       ("P. A. Rios", "6 h", 50),
                       ("C. Mendoza", "8 h", 67),
                       ("H. Vargas", "9 h", 75),
                       ("N. Beltran", "11 h", 92),
                   ])
                   + '<p class="nota-foot">Cupo maximo de 12 h por docente. '
                     'Ninafq Beltran tiene 1 h libre.</p></div>')
    cuerpo += card("Pendientes de asignar", tabla(
        ["Emprendimiento", "Estudiante", "Sector", "Horas sugeridas", "@ACC"],
        [["<b>EMP-038 Aromas del Sur</b>", "Sofia Ramirez", "Alimentos",
          badge("3 h", "b-neutra"), _acc(_b("edit", "Asignar"))],
         ["<b>EMP-034 Eco Hogar</b>", "Valeria Cruz", "Hogar",
          badge("2 h", "b-neutra"), _acc(_b("edit", "Asignar"))],
         ["<b>EMP-033 Pan de Abuela</b>", "Valentina Gomez", "Alimentos",
          badge("3 h", "b-neutra"), _acc(_b("edit", "Asignar"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Resumen", lista_def([
        ("Vigentes", "43 de 46"),
        ("Pendientes", "3"),
        ("Cupo total", "12 por docente"),
        ("Carga promedio", "3.1 h semanales"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + _btn("plus", "Asignar emprendimiento", "asignar-emprendimiento.html")
                   + _btn("download", "Exportar", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "asignaciones", "Asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones"],
                 sub="Docente asignado por emprendimiento y carga semanal.")


# --- 47. Diagnosticos --------------------------------------------------------
def diagnosticos():
    """Grafico de puntajes + cola de revision. No es una tabla de resultados."""
    cuerpo = metricas([
        ("clipboard", "Respondidos", "94", "", 88, "+8"),
        ("reloj", "Sin revision", "5", "", 22, None),
        ("medalla", "Promedio", "74", "", 74, "+2"),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Puntaje por emprendimiento", '<div class="card-body">'
                   + barras_h("", "Ultimo diagnostico registrado", [
                       "EcoPack", "Sabor y Sabe", "Aromas del Sur",
                       "Krea Textil", "Muebles Origen"],
                       [91, 78, 64, 71, 70], maximo=100)
                   + '</div>')
    cuerpo += card("Rendimiento del grupo", '<div class="card-body">'
                   + distribucion([
                       ("90 - 100", "12", 26),
                       ("70 - 89", "45", 48),
                       ("50 - 69", "28", 30),
                       ("Menos de 50", "9", 19),
                   ])
                   + '<p class="nota-foot">La mayoria de los estudiantes se ubica '
                     'entre 70 y 89 puntos.</p></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Pendientes de revision", '<div class="card-body">'
                   + lista_avisos([
                       ("Sin revision del docente", [
                           ("clipboard", "Aromas del Sur · Sofia Ramirez",
                            "Sin docente asignado · 02 nov 2024",
                            "diagnosticos.html", "alta",
                            _b("check", "Revisar")),
                           ("clipboard", "Krea Textil · Jhon Ospina",
                            "Paula Andrea Rios · 30 oct 2024",
                            "diagnosticos.html", "media",
                            _b("check", "Revisar")),
                           ("clipboard", "Muebles Origen · Andres Felipe",
                            "Ninafq Beltran · 18 oct 2024",
                            "diagnosticos.html", "media",
                            _b("check", "Revisar")),
                       ]),
                   ]) + '</div>')
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + _btn("download", "Exportar resultados", "reportes.html",
                          "btn btn-secundario")
                   + _btn("doc", "Ver instrumento", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "diagnosticos", "Diagnosticos respondidos", cuerpo,
                 migas=["Inicio", "Diagnosticos"],
                 sub="Resultados del diagnostico de los estudiantes.")


# --- 48. Exportar reportes ---------------------------------------------------
def reportes():
    cuerpo = card("Tipo de reporte", tabla(
        ["Reporte", "Descripcion", "Formato", "Ultima generacion", "@ACC"],
        [[badge("Seguimiento", "b-linea"), "Avances y calificacion por emprendimiento",
          "CSV y PDF", "12 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Asesorias", "b-linea"), "Uso y respuesta del servicio de asesorias",
          "CSV y PDF", "11 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Emprendimientos", "b-linea"), "Inventario completo con sector y etapa",
          "CSV y PDF", "10 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Diagnosticos", "b-linea"), "Puntajes del diagnostico por estudiante",
          "CSV y PDF", "08 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))]]),
        sin_pad=True)
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Filtros del reporte", select("Formato", ["CSV", "PDF", "XLSX"], req=True,
                                                 valor="CSV")
                   + select("Periodo", ["Ultimos 30 dias", "Ultimos 3 meses",
                                        "Todo el periodo"], req=True,
                            valor="Ultimos 3 meses")
                   + select("Docente", ["Todos los docentes", "Carlos Mendoza",
                                        "Paula Andrea Rios", "Hector Vargas"], req=True,
                            valor="Todos los docentes")
                   + campo("Enviar por correo", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co"))
    cuerpo += card("Resumen de la exportacion",
                   lista_def([
                       ("Emprendimientos incluidos", "46"),
                       ("Estudiantes incluidos", "110"),
                       ("Estimacion de filas", "1.284"),
                       ("Ultimo archivo generado", "12 nov 2024, 09:20"),
                   ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Generar reporte</button>'
                     % ico("download", 16)
                   + '<button class="btn btn-secundario">%s Descargar plantilla</button>'
                     % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div>"
    return shell(R, "reportes", "Exportar reportes", cuerpo,
                 migas=["Inicio", "Reportes"],
                 sub="Genera y descarga reportes institucionales en CSV, PDF o XLSX.",
                 acciones=_btn("check", "Generar"))


# --- 49. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = metricas([
        ("users", "Usuarios gestionados", "128", "", 84, "+12"),
        ("medalla", "Reportes generados", "24", "", 62, "+4"),
        ("alerta", "Decisiones pendientes", "6", "", 20, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Datos personales", campo("Nombres", valor="Ana", req=True)
                   + campo("Apellidos", valor="Restrepo", req=True)
                   + campo("Correo institucional", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Telefono", tipo="tel", valor="+57 301 555 0199"))
    cuerpo += card("Zona horaria", campo("Zona horaria", valor="America/Bogota")
                   + campo("Cargo", valor="Administradora del programa",
                           bloqueo="El cargo lo asigna la institucion"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid" style="gap:20px">'
    cuerpo += card("Seguridad", lista_def([
        ("Contrasena", "Actualizada hace 2 meses"),
        ("Verificacion en dos pasos", "Activada"),
        ("Ultimo acceso", "Hoy, 07:15"),
    ]))
    cuerpo += card("Acciones",
                   '<div style="display:flex;flex-direction:column;gap:10px">'
                   + '<button class="btn btn-primario">%s Guardar cambios</button>'
                     % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Cambiar contrasena</button>'
                     % ico("lock", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Actualiza tus datos y revisa tu actividad.")


# --- 50. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja del administrador: registro de trabajo por dia, no tabla.

    Aqui el objetivo es trazabilidad (que se aprobo, cuando y quien), asi que
    la pantalla es un historial agrupado por fecha y las metricas son de
    gobernanza, no de pendientes del rol.
    """
    dias = [
        ("Hoy, 12 de noviembre", [
            ("08:15", "3 emprendimientos siguen sin docente",
             "Asignaciones · Sin docente asignado",
             '<a class="btn btn-sm btn-primario" href="asignar-emprendimiento.html">'
             'Asignar</a>'),
            ("09:40", "5 diagnosticos sin revision",
             "Diagnosticos · Enviados por estudiantes",
             '<a class="btn btn-sm btn-primario" href="diagnosticos.html">'
             'Revisar</a>'),
        ]),
        ("Ayer, 11 de noviembre", [
            ("16:40", "Evento por aprobar: Jornada de mentoria",
             "Eventos · Creado por docente tutor",
             '<a class="btn btn-sm btn-secundario" href="eventos.html">'
             'Aprobar</a>'),
            ("11:05", "Moderaste 3 comentarios reportados",
             "Moderacion · Cola de reportes",
             '<a class="btn btn-sm btn-secundario" href="comentarios.html">'
             'Ver cola</a>'),
        ]),
        ("12 de noviembre", [
            ("18:20", "Reporte de seguimiento generado",
             "Reportes · Seguimiento del mes",
             '<a class="btn btn-sm btn-secundario" href="reportes.html">'
             'Descargar</a>'),
            ("10:12", "Docente asignado a EcoPack",
             "Asignaciones · Lucia Fernandez",
             badge("Hecho", "b-linea")),
        ]),
    ]
    cuerpo = metricas([
        ("bell", "Sin leer", "2", "", 18, None),
        ("check", "Aprobaciones del mes", "24", "", 62, None),
        ("users", "Docentes activos", "8", "", 88, None),
    ])
    cuerpo += '<div style="height:20px"></div>'
    cuerpo += agenda(dias)
    cuerpo += '<p class="nota-foot">El registro conserva 90 dias y se puede '\
              'exportar desde Reportes.</p>'
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Registro de aprobaciones y decisiones del equipo.",
                 acciones='<button class="btn btn-secundario">%s Marcar todo '
                          'como leido</button>' % ico("check", 16))