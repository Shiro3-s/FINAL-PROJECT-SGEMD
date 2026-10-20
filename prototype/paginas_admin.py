# -*- coding: utf-8 -*-
"""Rol ADMINISTRADOR - 18 pantallas.

Reglas del rol:
  - Gestiona perfiles de docentes y estudiantes, y sus asignaciones.
  - Aprueba solicitudes, crea eventos y modera comentarios.
  - Ve el seguimiento de todos los emprendimientos, no solo los asignados.
  - Exporta reportes en CSV y PDF.
"""

import unicodedata

from lib_ui import (calendario, calendario_interactivo, agenda,
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, formulario, lista_def, steps, ico, boton_accion, distribucion,
    lista_avisos, kanban, linea_tiempo, tabs_paneles, NOTIFS_ADMIN,
)
from lib_charts import barras, barras_h, lineas, donut, AZUL, AMAR, GRIS

R = "administrador"

BADGE = {
    "activo": "b-azul",
    "confirmado": "b-azul",
    "finalizada": "b-linea",
    "en revisión": "b-amarillo",
    "pendiente": "b-amarillo",
    "vencido": "b-amarillo",
    "aprobado": "b-azul",
    "rechazado": "b-neutra",
    "en espera": "b-amarillo",
    "borrado": "b-neutra",
    "visible": "b-azul",
    "oculto": "b-neutra",
    "programada": "b-amarillo",
    "confirmada": "b-azul",
    "en curso": "b-azul",
    "finalizada": "b-linea",
    "cancelada": "b-neutra",
}

ETAPAS = ["FASE 1 - Ideación", "FASE 2 - Prototipo",
          "FASE 3 - Validación", "FASE 4 - Formalización"]

# Abreviaturas de mes para _fmt_fecha (índice 0-based).
_MESES = ["ene", "feb", "mar", "abr", "may", "jun",
          "jul", "ago", "sep", "oct", "nov", "dic"]

DOCENTES = [
    ("DOC-014", "Carlos Mendoza", "carlos.mendoza@sgemd.edu.co", "Alimentos",
     "3 h", "8", "Activo"),
    ("DOC-013", "Paula Andrea Rios", "paula.rios@sgemd.edu.co", "Moda",
     "2h", "5", "Activo"),
    ("DOC-012", "Hector Vargas", "hector.vargas@sgemd.edu.co", "Muebles",
     "4h", "6", "Activo"),
    ("DOC-011", "Ninafq Beltran", "nina.beltran@sgemd.edu.co", "Ambiental",
     "3h", "7", "Inactivo"),
    ("DOC-010", "Rafael Nieto", "rafael.nieto@sgemd.edu.co", "Tecnología",
     "5h", "4", "Activo"),
]

ESTUDIANTES = [
    ("EST-087", "Mariana López", "Alimentos", "Sabor y Sabe",
     "FASE 2 - Prototipo", 62, "Activo"),
    ("EST-086", "Jhon Ospina", "Moda", "Krea Textil",
     "FASE 1 - Ideación", 28, "Activo"),
    ("EST-085", "Lucia Fernandez", "Ambiental", "EcoPack",
     "FASE 3 - Validación", 84, "Activo"),
    ("EST-084", "Sofia Ramirez", "Alimentos", "Aromas del Sur",
     "FASE 1 - Ideación", 15, "Activo"),
    ("EST-083", "Andres Felipe", "Muebles", "Muebles Origen",
     "FASE 2 - Prototipo", 55, "Inactivo"),
]

EMPRENDIMIENTOS = [
    ("EMP-041", "Sabor y Sabe", "Mariana López", "Alimentos", "Comercio",
     "FASE 2 - Prototipo", 62, "Carlos Mendoza"),
    ("EMP-040", "Krea Textil", "Jhon Ospina", "Moda", "Moda",
     "FASE 1 - Ideación", 28, "Paula Andrea Rios"),
    ("EMP-039", "EcoPack", "Lucia Fernandez", "Ambiental", "Industrial",
     "FASE 3 - Validación", 84, "Hector Vargas"),
    ("EMP-038", "Aromas del Sur", "Sofia Ramirez", "Alimentos", "Alimentos",
     "FASE 1 - Ideación", 15, "Sin asignar"),
    ("EMP-037", "Muebles Origen", "Andres Felipe", "Muebles", "Artesanal",
     "FASE 2 - Prototipo", 55, "Ninafq Beltran"),
]

# Bandeja de solicitudes pendientes (D1/D2/D4).
SOLIC_DESBLOQUEOS = [
    ("EST-083", "Andres Felipe", "Estudiante", "Cuenta inactiva por 90 días sin acceso",
     "05 nov 2024"),
    ("DOC-011", "Ninafq Beltran", "Docente", "Bloqueo por intentos fallidos de acceso",
     "04 nov 2024"),
    ("EST-079", "Camilo Rojas", "Estudiante", "Reactivar para retomar su emprendimiento",
     "02 nov 2024"),
    ("EST-076", "Valentina Ortega", "Estudiante", "Cuenta limitada a petición; solicita reactivar",
     "01 nov 2024"),
]

SOLIC_PARALELOS = [
    ("EST-086", "Jhon Ospina", "Krea Textil", "Krea Accesorios", "Moda", "06 nov 2024"),
    ("EST-084", "Sofia Ramirez", "Aromas del Sur", "Café del Sur", "Alimentos", "05 nov 2024"),
    ("EST-081", "Diego Peralta", "Muebles Origen", "Muebles Origen Kids", "Muebles", "03 nov 2024"),
]

SOLIC_CITAS = [
    ("Mariana López", "Sabor y Sabe", "Carlos Mendoza", "12 nov 2024, 10:00",
     "Revisión del prototipo de empaque"),
    ("Lucia Fernandez", "EcoPack", "Hector Vargas", "13 nov 2024, 14:00",
     "Asesoría sobre costos de producción"),
    ("Jhon Ospina", "Krea Textil", "Paula Andrea Rios", "14 nov 2024, 09:00",
     "Validación de mercado para nueva línea"),
]

# Programa de asesorias (A08): fields = cod, estudiante, docente, fecha (ISO),
# hora, tema, modalidad, estado. Los nombres deben existir en ESTUDIANTES/DOCENTES
# para poder prefiltarlos en el formulario de edicion.
ASESORIAS = [
    ("ASE-012", "Mariana López", "Carlos Mendoza", "2024-11-12", "10:00",
     "Revisión del prototipo de empaque", "Virtual", "Programada"),
    ("ASE-011", "Lucia Fernandez", "Hector Vargas", "2024-11-13", "14:00",
     "Asesoría sobre costos de producción", "Presencial", "Confirmada"),
    ("ASE-010", "Jhon Ospina", "Paula Andrea Rios", "2024-11-14", "09:00",
     "Validación de mercado para nueva línea", "Virtual", "En curso"),
    ("ASE-009", "Sofia Ramirez", "Carlos Mendoza", "2024-11-08", "16:00",
     "Plan financiero y fuentes de financiación", "Virtual", "Finalizada"),
    ("ASE-008", "Andres Felipe", "Ninafq Beltran", "2024-11-07", "11:00",
     "Costos y margen en la línea de muebles", "Presencial", "Cancelada"),
    ("ASE-007", "Mariana López", "Hector Vargas", "2024-11-06", "15:00",
     "Impacto ambiental del empaque", "Virtual", "Finalizada"),
]

# Correo institucional derivado del nombre del estudiante (no se toca la
# tupla ESTUDIANTES, que es intocable por diseño del prototipo).
CORREOS_EST = {e[1]: "%s@sgemd.edu.co" % e[1].lower().replace(" ", ".")
               for e in ESTUDIANTES}

# Eventos del calendario navegable de Eventos: día de noviembre de 2024 -> html.
# Se pinta con calendario_interactivo (data-cal-doc) y lo controla ADMIN_JS.

EVENTOS_CAL = {
    18: "<b>Taller de costos y precios</b><br/>Auditorio A · 32 de 40 cupos · Publicado",
    22: "<b>Feria de emprendedores</b><br/>Plaza central · 86 de 120 cupos · Publicado",
    25: "<b>Jornada de mentoria</b><br/>Sala 2 · 14 confirmados · Por aproximado",
}

# Script JS propio del rol administrador para calendario navegable (idéntico
# a la lógica del rol docente, pero inyectado aquí para no añadir cases
# genéricos a lib_js).
ADMIN_JS = r"""
(function () {
  /* Calendario interactivo de eventos del administrador */
  var calDoc = document.querySelector("[data-cal-doc]");
  if (calDoc) {
    var celdas = Array.prototype.slice.call(
      calDoc.querySelectorAll("[data-dia]"));
    var paneles = Array.prototype.slice.call(
      calDoc.querySelectorAll("[data-dia-panel]"));
    var rotulo = calDoc.querySelector("[data-dia-titulo]");
    var verDia = function (dia, etiqueta) {
      celdas.forEach(function (c) {
        var es = c.getAttribute("data-dia") === String(dia);
        c.classList.toggle("activo", es);
        c.setAttribute("aria-pressed", es ? "true" : "false");
      });
      var hay = false;
      paneles.forEach(function (p) {
        if (p.getAttribute("data-dia-panel") === String(dia)) hay = true;
      });
      paneles.forEach(function (p) {
        var k = p.getAttribute("data-dia-panel");
        p.hidden = hay ? (k !== String(dia)) : (k !== "sin");
      });
      if (rotulo) rotulo.textContent = etiqueta || ("Dia " + dia);
    };
    celdas.forEach(function (c) {
      c.addEventListener("click", function () {
        verDia(c.getAttribute("data-dia"), c.getAttribute("data-etiqueta"));
      });
    });
    var hoyAttr = calDoc.getAttribute("data-hoy");
    var hoyCal = calDoc.querySelector('[data-dia="' + hoyAttr + '"]');
    if (hoyCal) {
      verDia(hoyAttr, hoyCal.getAttribute("data-etiqueta"));
    }
  }
})();
"""


def _fmt_fecha(iso):
    """Convierte 2024-11-12 a '12 nov 2024' para mostrar en tabla/cancelacion."""
    try:
        anio, mes, dia = iso.split("-")
        return "%d %s %s" % (int(dia), _MESES[int(mes) - 1], anio)
    except (ValueError, AttributeError):
        return iso


def _b(icono, etiqueta, accion=""):
    """Botón de fila. Con accion explicita emite ese data-accion; sin ella
    cae en el mapa ICONO_ACCION (evita que 'Seleccionar' dispare 'aprobar')."""
    if accion:
        return ('<button data-accion="%s" title="%s" aria-label="%s">%s</button>'
                % (accion, etiqueta, etiqueta, ico(icono, 16)))
    return boton_accion(icono, etiqueta)


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _nuevo(accion, etiqueta):
    """Botón primario de alta para la cabecera de una tarjeta."""
    return ('<button class="btn btn-primario btn-sm" data-accion="%s">%s %s</button>'
            % (accion, ico("plus", 16), etiqueta))


def _solic(accion, icono, etiqueta):
    """Botón de accion de la bandeja de solicitudes (Aprobar/Rechazar)."""
    return ('<button data-accion="%s" title="%s" aria-label="%s">%s</button>'
            % (accion, etiqueta, etiqueta, ico(icono, 16)))


def _revisar(cod, emp, estu, sector, tipo, etapa, docente):
    """Botón por fila para abrir la revisión de un emprendimiento (datos en dataset)."""
    return ('<button data-accion="revisar-emprendimiento" title="Revisar" aria-label="Revisar" '
            'data-emp="%s" data-cod="%s" data-estu="%s" data-sector="%s" data-tipo="%s" '
            'data-etapa="%s" data-docente="%s">%s</button>'
            % (emp, cod, estu, sector, tipo, etapa, docente, ico("check", 16)))


def _sel_estado(cod, nombre, estado):
    """Selector de estado de acceso por fila (Activo/Limitado/Inactivo).
    data-filtro='off' evita que el buscador/filtros de tabla lo tomen como filtro."""
    opciones = "".join('<option%s>%s</option>' % (" selected" if o == estado else "", o)
                       for o in ("Activo", "Limitado", "Inactivo"))
    return ('<select class="sel-estado" data-filtro="off" data-cod="%s" data-nombre="%s" '
            'aria-label="Estado de la cuenta de %s">%s</select>'
            % (cod, nombre, nombre, opciones))


def _asesoria(accion, icono, etiqueta, cod="", estu="", doc="", fecha="", hora="",
              tema="", mod="", est=""):
    """Botón por fila del programa de asesorías; los datos opcionales viajan en
    data-* para prefill del modal de edición o para el mensaje de cancelacion."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("cod", cod), ("estu", estu), ("doc", doc), ("fecha", fecha),
        ("hora", hora), ("tema", tema), ("mod", mod), ("estado", est)) if v)
    return ('<button data-accion="%s"%s title="%s" aria-label="%s">%s</button>'
            % (accion, extra, etiqueta, etiqueta, ico(icono, 16)))


def _evento(accion, icono, etiqueta, titulo="", fecha="", lugar="",
            confirmados="", sector="", primario=False):
    """Botón de aprobación/rechazo de eventos pendientes (A03); los datos del
    evento viajan en data-* para armar la ficha del modal de aprobación."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("titulo", titulo), ("fecha", fecha), ("lugar", lugar),
        ("confirmados", confirmados), ("sector", sector)) if v)
    cls = "btn-primario" if primario else "btn-secundario"
    return ('<button class="btn btn-sm %s" data-accion="%s"%s title="%s" '
            'aria-label="%s">%s</button>'
            % (cls, accion, extra, etiqueta, etiqueta, ico(icono, 14)))


def _barra(pct):
    """A30: sin hex inline; min-width y el estilo del porcentaje viven en
    .barra-celda / .barra-pct (lib_css). El ancho de la barra es dato (%)."""
    return ('<div class="barra barra-celda"><span style="width:%d%%"></span></div>'
            '<span class="barra-pct">%d%%</span>' % (pct, pct))


def _sel(etiqueta, opciones, extra=""):
    """Select de filtro de tabla. Emite data-filtro para que el JS lo escuche;
    la primera opción ('Todos/Todas...') va con value='' para no filtrar."""
    primero, resto = opciones[0], opciones[1:]
    pops = '<option value="">%s</option>' % primero + "".join(
        "<option>%s</option>" % o for o in resto)
    return '<select class="filtro" data-filtro="%s" aria-label="%s" %s>%s</select>' % (
        _slug(etiqueta), etiqueta, extra, pops)


def _slug(txt):
    """Versión Python del slug JS (para data-filtro)."""
    s = "".join(ch for ch in unicodedata.normalize("NFD", txt)
                if unicodedata.category(ch) != "Mn")
    return "-".join(s.lower().split())


def data_filtro_col(col):
    """Acota un filtro a la columna (indice 0-based) de la tabla."""
    return 'data-filtro-col="%d"' % col


def _js_admin():
    return ADMIN_JS


def _inyectar(html):
    """Inyecta JS de rol administrador (solo cuando es necesario: calendario)."""
    if "</body>" in html and "data-cal-doc" in html:
        html = ("<script>" + _js_admin() + "</script>\n</body>").join(
            html.rsplit("</body>", 1))
    return html


def _envolver(fn):
    def _render():
        return _inyectar(fn())
    return _render


def _btn(icono, texto, href="#", clase="btn btn-primario"):
    return '<a class="%s" href="%s">%s %s</a>' % (clase, href, ico(icono, 16), texto)


def _exportar(etiqueta, clase="btn btn-secundario"):
    """Botón de exportación real (A27): dispara el caso JS 'exportar' (CSV de la
    tabla o, si no hay tabla, resumen de métricas) en vez de navegar a reportes."""
    return ('<button class="%s" data-accion="exportar">%s %s</button>'
            % (clase, ico("download", 16), etiqueta))


def _emp(accion, icono, etiqueta, cod="", emp="", estu="", sector="", tipo="",
         etapa="", avance="", docente=""):
    """Botón por fila del registro de emprendimientos; los datos viajan en
    data-* para el prefill del modal de edición (A07)."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("cod", cod), ("emp", emp), ("estu", estu), ("sector", sector),
        ("tipo", tipo), ("etapa", etapa), ("avance", avance),
        ("doc", docente)) if v)
    return ('<button data-accion="%s"%s title="%s" aria-label="%s">%s</button>'
            % (accion, extra, etiqueta, etiqueta, ico(icono, 16)))


def _coment(autor, rol, ini, fecha, txt):
    """Comentario con avatar, autor, rol y fecha (C13)."""
    return ('<div class="coment"><span class="avatar">%s</span>'
            '<div style="flex:1;min-width:0">'
            '<div class="coment-cab"><b>%s</b><span class="who-role">%s</span>'
            "<time>%s</time></div>"
            '<div class="coment-txt">%s</div></div></div>'
            % (ini, autor, rol, fecha, txt))


def _tabla_t(cabeceras, filas, titulo):
    """Tabla con caption oculto para lectores de pantalla (C6)."""
    return tabla(cabeceras, filas, caption=titulo)


def _drop():
    """Zona de adjuntos .drop (C3): mismo marcado y ids que tarea-detalle.

    lib_js cuelga el input #evidencia-real; el contador y la lista usan los
    mismos ids del flujo estudiante para que el kit funcione sin cambios."""
    return ('<label class="drop" for="evidencia-real">%s'
            '<b class="drop-tit">Arrastra tus '
            'archivos aquí o haz clic para seleccionarlos</b>'
            '<span class="drop-nota">Formatos admitidos: JPG, PNG o PDF '
            '&middot; Máximo 10 MB</span>'
            '<input type="file" id="evidencia-real" multiple '
            'accept=".jpg,.jpeg,.png,.pdf" aria-label="Seleccionar archivos" '
            'style="display:none"></label>' % ico("upload", 34))


def _vacio(fuente, titulo, txt, icono="doc"):
    """Estado vacio enlazado a su lista (hallazgo MEDIO P6-P10).

    fuente: selector CSS de los items dentro del mismo contenedor (.card,
    .tabla-envoltura o [data-vacio-lista]). Arranca oculto y lib_js lo
    muestra cuando la lista queda sin items visibles."""
    return ('<div data-vacio data-vacio-fuente="%s" hidden>%s</div>'
            % (fuente, estado_vacio(titulo, txt, "", icono)))


# --- 33. Dashboard -----------------------------------------------------------

def dashboard():
    cuerpo = metricas([
        ("users", "Usuarios activos", "128", "", 84, "+12 este mes"),
        ("maleta", "Emprendimientos", "46", "", 72, "+5"),
        ("trend", "Avances del mes", "61", "", 88, "+14"),
        ("medalla", "Tasa de cierre", "78", "%", 78, "+3"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Avance de fase por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [12, 19, 27, 41, 61],
        unidad=" avances"))
    cuerpo += card("Emprendimientos por sector", barras_h(
        "", "", ["Alimentos", "Moda", "Ambiental", "Tecnología", "Muebles"],
        [14, 11, 9, 7, 5], color=AMAR))
    cuerpo += card("Actividad reciente (Agenda)", agenda([
        ("12 nov 2024, 08:30 · Asesoría", [("08:30", "EcoPack - Carlos Mendoza", "", "")]),
        ("12 nov 2024, 11:00 · Evento", [("11:00", "Taller de costos - Confirmado", "", "")]),
        ("11 nov 2024, 15:00 · Comentario", [("15:00", "Pendiente de moderación", "", "")]),
    ]) + _vacio(".ag-ev", "Sin actividad programada",
                "Cuando haya asesorías, eventos o comentarios pendientes "
                "aparecerán aquí con su fecha y hora.", "calendar"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Calendario", calendario("noviembre", 2024, hoy=12, marcados=(21,26,2)))
    cuerpo += card("Pendientes de decisión", lista_def([
        ("<a href='asignaciones.html'>Emprendimientos sin docente</a>", "3"),
        ("<a href='eventos.html'>Eventos por aprobar</a>", "1"),
        ("<a href='comentarios.html'>Comentarios reportados</a>", "3"),
        ("<a href='diagnosticos.html'>Diagnósticos sin revisar</a>", "5"),
    ]))
    cuerpo += card("Distribución de usuarios", donut(
        "", "", [("Docentes", 18, AZUL), ("Estudiantes", 110, AMAR)], "usuarios"))
    cuerpo += "</div></div>"
    cuerpo = formulario("dashboard", cuerpo)
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
            "%s h" % carga, emp,             _sel_estado(cod, nom, estado),
            _acc('<button data-accion="editar-docente" title="Editar docente" '
                 'aria-label="Editar docente">%s</button>' % ico("edit", 16)
                 + '<button data-accion="dar-de-baja" title="Dar de baja" '
                 'aria-label="Dar de baja a %s">%s</button>' % (nom, ico("trash", 16))),
        ])
    cuerpo = callout("Los perfiles de estudiante se editan desde su cuenta. El "
                     "administrador solo puede cambiar el estado de acceso (Activo, "
                     "Limitado o Inactivo).", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("users", "Docentes", "18", "", 45, "+1"),
        ("users", "Estudiantes", "110", "", 92, "+11"),
        ("alerta", "Cuentas inactivas", "4", "", 12, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += toolbar(filtros=_sel("Filtrar área", ["Todas las áreas", "Alimentos",
                                                     "Moda", "Ambiental", "Tecnología"]))
    cuerpo += card("Docentes", tabla(
        ["Código", "Nombre", "Correo institucional", "Área", "Carga semanal",
         "Emprendimientos", "Estado", "@ACC"], filas_doc), accion=_nuevo("nuevo-docente", "Nuevo docente"), sin_pad=True)
    cuerpo += card("Estudiantes", tabla(
        ["Código", "Nombre", "Sector", "Emprendimiento", "Etapa", "Avance", "Estado", "@ACC"],
        [[c, "<b>%s</b>" % n, sec, emp, badge(et, "b-linea"), _barra(av),
          _sel_estado(c, n, est),
          _acc('<button data-accion="editar-estudiante" title="Editar estudiante" '
               'aria-label="Editar estudiante">%s</button>' % ico("edit", 16)
               + '<button data-accion="dar-de-baja" title="Dar de baja" '
               'aria-label="Dar de baja a %s">%s</button>' % (n, ico("trash", 16)))] for c, n, sec, emp, et, av, est in ESTUDIANTES],
    ), accion=_nuevo("nuevo-estudiante", "Nuevo estudiante"), sin_pad=True)
    cuerpo += paginas(1, 5, 18)
    cuerpo += '<div id="form-docente" hidden>' + _cuerpo_docente() + "</div>"
    cuerpo += '<div id="form-estudiante" hidden>' + _cuerpo_estudiante() + "</div>"
    cuerpo += '<div id="form-nuevo-docente" hidden>' + _cuerpo_nuevo_docente() + "</div>"
    cuerpo += '<div id="form-nuevo-estudiante" hidden>' + _cuerpo_nuevo_estudiante() + "</div>"
    cuerpo = formulario("perfiles", cuerpo)
    return shell(R, "usuarios", "Gestión de perfiles", cuerpo,
                 migas=["Inicio", "Gestión de perfiles"],
                 sub="Altas, edición y estado de acceso de docentes y estudiantes.")


# --- 35. Editar docente (formulario embebido en Gestion de perfiles) --------
def _cuerpo_docente():
    """Formulario de edición de docente. Se abre en un modal desde usuarios();
    ya no es una página aparte."""
    cuerpo = '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del docente",
                   campo("Código", valor="DOC-014", bloqueo="Código asignado por el sistema")
                   + campo("Nombres", valor="Carlos Alejandro", req=True)
                   + campo("Apellidos", valor="Mendoza Rios", req=True)
                   + campo("Correo institucional", tipo="email",
                           valor="carlos.mendoza@sgemd.edu.co", req=True)
                   + campo("Teléfono", tipo="tel", valor="+57 300 555 0142"))
    cuerpo += card("Área y carga", select("Área de conocimiento",
                                          ["Alimentos", "Moda", "Ambiental",
                                           "Tecnología", "Muebles"],
                                          req=True, valor="Alimentos")
                   + campo("Horas de asesoría por semana", tipo="number", valor="3",
                           ph="De 1 a 20")
                   + campo("Emprendimientos asignados", tipo="number", valor="8",
                           bloqueo="Se actualiza desde Asignaciones"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Último acceso", "Hoy, 07:42"),
        ("Asesorías realizadas", "31"),
        ("Promedio de calificación", "89 de 100"),
    ]))
    cuerpo += "</div></div>"
    return cuerpo


# --- 36. Editar estudiante (formulario embebido en Gestion de perfiles) -----
def _cuerpo_estudiante():
    """Formulario de edición de estudiante. Se abre en un modal desde
    usuarios(); ya no es una página aparte."""
    cuerpo = callout("El estudiante edita su cuenta. El administrador solo puede "
                     "<b>cambiar el estado de acceso</b> (Activo, Limitado o Inactivo).", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del estudiante",
                   campo("Código", valor="EST-087", bloqueo="Código asignado por el sistema")
                   + campo("Nombres", valor="Mariana", bloqueo="Los edita el estudiante")
                   + campo("Apellidos", valor="López", bloqueo="Los edita el estudiante")
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
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Fecha de registro", "12 mar 2024"),
        ("Último acceso", "Hoy, 08:02"),
        ("Asesorías recibidas", "3"),
    ]))
    cuerpo += "</div></div>"
    return cuerpo


# --- 36b. Alta de docente (formulario embebido en Gestion de perfiles) ------
def _cuerpo_nuevo_docente():
    """Alta de docente. Se abre en un modal desde usuarios(); el código y la
    cuenta los asigna el sistema, por eso no son campos editables."""
    cuerpo = callout("El docente recibirá un correo de activación en su cuenta "
                     "institucional para definir su contraseña.", "mail")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del docente",
                   campo("Nombres", req=True)
                   + campo("Apellidos", req=True)
                   + campo("Correo institucional", tipo="email", req=True,
                           ayuda="Debe ser una cuenta @sgemd.edu.co")
                   + campo("Teléfono", tipo="tel"))
    cuerpo += card("Área y carga",
                   select("Área de conocimiento", ["Alimentos", "Moda", "Ambiental",
                                                   "Tecnología", "Muebles"],
                          req=True, valor="Alimentos")
                   + campo("Horas de asesoría por semana", tipo="number",
                           ph="De 1 a 20"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso",
                   select("Estado de la cuenta", ["Activo", "Limitado"],
                          req=True, valor="Activo")
                   + '<div class="ayuda">%s Limitado deja la cuenta creada pero '
                     'sin acceso hasta que la habilites.</div>' % ico("alerta", 13))
    cuerpo += "</div></div>"
    return cuerpo


# --- 36c. Alta de estudiante (formulario embebido en Gestion de perfiles) ----
def _cuerpo_nuevo_estudiante():
    """Alta de estudiante. Se abre en un modal desde usuarios()."""
    cuerpo = callout("El estudiante recibirá un correo de activación en su cuenta "
                     "institucional para definir su contraseña.", "mail")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del estudiante",
                   campo("Nombres", req=True)
                   + campo("Apellidos", req=True)
                   + campo("Correo institucional", tipo="email", req=True,
                           ayuda="Debe ser una cuenta @sgemd.edu.co")
                   + campo("Teléfono", tipo="tel"))
    cuerpo += card("Emprendimiento y sector",
                   select("Sector", ["Alimentos", "Moda", "Ambiental",
                                     "Tecnología", "Muebles"],
                          req=True, valor="Alimentos")
                   + campo("Nombre del emprendimiento", ph="Ej.: Sabor y Sabe")
                   + select("Etapa", ETAPAS, req=True, valor="FASE 1 - Ideación"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso",
                   select("Estado de la cuenta", ["Activo", "Limitado"],
                          req=True, valor="Activo")
                   + '<div class="ayuda">%s Limitado deja la cuenta creada pero '
                     'sin acceso hasta que la habilites.</div>' % ico("alerta", 13))
    cuerpo += "</div></div>"
    return cuerpo


# --- 35. Solicitudes pendientes (bandeja del Admin) --------------------------
def _cuerpo_desb():
    filas = [
        ["<b>%s</b>" % c, "<b>%s</b>" % n, badge(r, "b-linea"), m, f,
         _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
              _solic("solicitud-rechazar", "x", "Rechazar"))]
        for c, n, r, m, f in SOLIC_DESBLOQUEOS
    ]
    return tabla(["Código", "Nombre", "Rol", "Motivo de la solicitud", "Fecha", "@ACC"],
                 filas)


def _cuerpo_par():
    filas = [
        ["<b>%s</b>" % c, "<b>%s</b>" % n, a, "<b>%s</b>" % nu, s, f,
         _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
              _solic("solicitud-rechazar", "x", "Rechazar"))]
        for c, n, a, nu, s, f in SOLIC_PARALELOS
    ]
    return tabla(["Código", "Estudiante", "Emprendimiento actual", "Nuevo emprendimiento",
                  "Sector", "Fecha", "@ACC"], filas)


def _cuerpo_cit():
    filas = [
        ["<b>%s</b>" % n, e, d, f, m,
         _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
              _solic("solicitud-rechazar", "x", "Rechazar"))]
        for n, e, d, f, m in SOLIC_CITAS
    ]
    return tabla(["Estudiante", "Emprendimiento", "Docente sugerido", "Fecha propuesta",
                  "Motivo", "@ACC"], filas)


def solicitudes():
    """Bandeja única del Admin: desbloqueos de cuenta, paralelos y citas (D1/D2/D4)."""
    paneles = [
        ("Desbloqueos (%d)" % len(SOLIC_DESBLOQUEOS), "tab-desb", _cuerpo_desb()),
        ("Paralelos (%d)" % len(SOLIC_PARALELOS), "tab-par", _cuerpo_par()),
        ("Citas (%d)" % len(SOLIC_CITAS), "tab-cit", _cuerpo_cit()),
    ]
    cuerpo = callout(
        "Aprueba o rechaza las solicitudes pendientes. Al aprobar, el sistema aplica "
        "el cambio y notifica al solicitante; al rechazar, se solicita un motivo.",
        "checklist")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("lock", "Desbloqueos", str(len(SOLIC_DESBLOQUEOS)), "", 35, None),
        ("maleta", "Paralelos", str(len(SOLIC_PARALELOS)), "", 25, None),
        ("calendar", "Citas de asesoría", str(len(SOLIC_CITAS)), "", 20, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += tabs_paneles([(n, pid) for n, pid, _ in paneles])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += "".join(
        '<div data-panel-nombre="%s"%s>%s</div>' % (pid, "" if i == 0 else " hidden", b)
        for i, (_, pid, b) in enumerate(paneles)
    )
    cuerpo = formulario("solicitudes", cuerpo)
    return shell(R, "solicitudes", "Solicitudes pendientes", cuerpo,
                 migas=["Inicio", "Solicitudes pendientes"],
                 sub="Bandeja de desbloqueos de cuenta, solicitudes de paralelo y citas de asesoría.")


# --- 37. Emprendimientos -----------------------------------------------------
def emprendimientos():
    """Registro maestro: es la tabla canonica del admin, con chips de sector."""
    cuerpo = callout("Como administrador tu ves <b>todos</b> los emprendimientos, "
                     "tengan o no docente asignado.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("maleta", "Total", "46", "", 72, "+5"),
        ("trend", "En fase 3 o 4", "18", "", 62, None),
        ("alerta", "Sin docente", "3", "", 18, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += toolbar(filtros=_sel("Filtrar sector", ["Todos los sectores", "Alimentos",
                                                      "Moda", "Ambiental", "Muebles"],
                                  data_filtro_col(3))
                      + _sel("Filtrar etapa", ["Todas las etapas"] + ETAPAS, data_filtro_col(5))
                      + _sel("Filtrar docente", ["Todos los docentes", "Sin asignar"],
                             data_filtro_col(7)))
    filas = []
    for cod, emp, estu, sector, tipo, etapa, avance, docente in EMPRENDIMIENTOS:
        filas.append([
            "<b>%s</b>" % emp, cod, estu,
            badge(sector, "b-azul" if sector == "Alimentos" else
                  ("b-linea" if sector == "Ambiental" else "b-neutra")),
            tipo, badge(etapa, "b-linea"), _barra(avance),
            docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
            _acc(_revisar(cod, emp, estu, sector, tipo, etapa, docente),
                 '<a class="table-act" href="emprendimiento-plan.html" '
                 'title="Abrir plan" aria-label="Abrir plan">%s</a>' % ico("eye", 16),
                 '<a class="table-act" href="emprendimiento-expediente.html" '
                 'title="Abrir expediente" aria-label="Abrir expediente">%s</a>'
                 % ico("carpeta", 16),
                 _emp("editar-emprendimiento", "edit", "Editar emprendimiento",
                      cod=cod, emp=emp, estu=estu, sector=sector, tipo=tipo,
                      etapa=etapa, avance=str(avance), docente=docente)),
        ])
    cuerpo += tabla(["Emprendimiento", "Código", "Estudiante", "Sector", "Tipo",
                     "Etapa", "Avance", "Docente asignado", "@ACC"], filas)
    cuerpo += '<div id="form-emprendimiento" hidden>' + _cuerpo_emprendimiento() + "</div>"
    cuerpo += paginas(1, 5, 46)
    cuerpo = formulario("emprendimientos", cuerpo)
    return shell(R, "emprendimientos", "Emprendimientos", cuerpo,
                 migas=["Inicio", "Emprendimientos"],
                 sub="Todos los emprendimientos registrados en el programa.",
                 acciones=_btn("sliders", "Asignar emprendimiento",
                               "asignaciones.html", "btn btn-secundario"))


# --- 37b. Expediente del emprendimiento --------------------------------------
def emprendimiento_expediente():
    """Expediente del emprendimiento (C2/C3/C4/C11/C13): vista del admin.

    Porta el arquetipo del expediente docente sin acciones de calificación ni
    registro de avance (el admin consulta y modera); cada bloque se resuelve
    en una vista admin existente (plan, seguimiento, asesorías, diagnosticos,
    comentarios, reportes).
    """
    cuerpo = metricas([
        ("trend", "Avance de fase", "62", "%", 62, "FASE 2 - Prototipo"),
        ("medalla", "Promedio de calificación", "87", "/ 100", 87,
         "3 avances calificados"),
        ("clipboard", "Asesorías registradas", "2", "", 35, "1 por confirmar"),
        ("chat", "Comentarios en el expediente", "12", "", 40, "2 reportados"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'

    avances = _tabla_t(
        ["Fecha", "Fase", "Descripción del avance", "Calificación"],
        [["12 nov 2024", "FASE 2", "Prototipo de empaque listo para 20 unidades",
          badge("92 de 100", "b-azul")],
         ["05 nov 2024", "FASE 2", "Definición de precios y punto de equilibrio",
          badge("88 de 100", "b-azul")],
         ["28 oct 2024", "FASE 1", "Diagnóstico inicial y problema claro",
          badge("81 de 100", "b-azul")]],
        "Avances y calificaciones del emprendimiento Sabor y Sabe")

    filas_as = [
        [cod, _fmt_fecha(fecha) + ", " + hora, mod,
         badge(estado, BADGE.get(estado, "b-neutra"))]
        for cod, estu, doc, fecha, hora, tema, mod, estado in ASESORIAS
        if estu == "Mariana López"]
    asesorias_panel = _tabla_t(
        ["Código", "Fecha y hora", "Modalidad", "Estado"], filas_as,
        "Asesorías del emprendimiento Sabor y Sabe")
    asesorias_panel += ('<div class="form-acciones">'
                        + _btn("chat", "Ver todas las asesorías", "asesorias.html",
                               "btn btn-secundario") + "</div>")

    diag_panel = lista_def([
        ("Última revisión", "28 oct 2024, 09:14"),
        ("Puntaje heurísticas", "7.8 de 10"),
        ("Recomendaciones enviadas", "Canal de venta y presupuesto de publicidad"),
        ("Estado", badge("Revisado", "b-azul", "check")),
    ]) + '<div class="form-acciones">' + _btn(
        "clipboard", "Ver diagnósticos", "diagnosticos.html",
        "btn btn-secundario") + "</div>"

    com_panel = ('<div class="grid">'
                 + _coment("Ana Restrepo", "Administradora", "AR", "12 nov 2024",
                           "Se deja constancia de la moderación del comentario "
                           "reportado; el expediente queda actualizado.")
                 + _coment("Carlos Mendoza", "Docente", "CM", "12 nov 2024",
                           "Buen avance en el prototipo. Falta medir el costo "
                           "unitario de los empaques.")
                 + _coment("Mariana López", "Estudiante", "ML", "11 nov 2024",
                           "Adjunté las fotos del punto de venta y la lista de "
                           "precios.")
                 + "</div>"
                 + '<div class="form-acciones">'
                 + _btn("puntos", "Moderar comentarios", "comentarios.html",
                        "btn btn-secundario") + "</div>")

    ev_panel = (
        card("Evidencias y anexos del expediente",
             '<p class="suave">Adjunta anexos institucionales del expediente '
             "(actas, conceptos o soportes de moderación).</p>"
             '<div style="margin-top:12px">' + _drop() + "</div>"
             '<div class="divisor"></div>'
             '<h3 style="margin-bottom:8px">Adjuntos del expediente</h3>'
             '<div id="adjuntos-lista">' + estado_vacio(
                 "Todavía no hay anexos en este expediente",
                 "Cuando se adjunten archivos aparecerán aquí con su fecha de carga.",
                 '<button class="btn btn-secundario" '
                 'data-accion="adjuntar-evidencias">%s Adjuntar ahora</button>'
                 % ico("clip", 16), "clip")
             + "</div>",
             hint='<span id="contador-adjuntos">0 archivos</span>')
        + callout("El estudiante y el docente cargan la evidencia de tareas y "
                  "avances; los anexos de esta zona son administrativos.", "clip"))

    paneles = [
        ("Avances", "exp-avances", avances),
        ("Asesorías", "exp-asesorias", asesorias_panel),
        ("Diagnóstico", "exp-diag", diag_panel),
        ("Comentarios", "exp-com", com_panel),
        ("Evidencias", "exp-ev", ev_panel),
    ]
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += tabs_paneles([(n, pid) for n, pid, _ in paneles])
    cuerpo += '<div class="sep sep-12"></div>'
    cuerpo += "".join(
        '<div data-panel-nombre="%s"%s>%s</div>' % (pid, "" if i == 0 else " hidden", b)
        for i, (_, pid, b) in enumerate(paneles))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Código", "EMP-041"),
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente asignado", "Carlos Mendoza"),
    ]))
    cuerpo += card("Estudiantes del grupo", lista_def([
        ("Mariana López", "EST-087 · Sede Norte"),
    ]) + '<div class="nota-foot">Las calificaciones y avances aplican a todos '
         "los integrantes del emprendimiento.</div>")
    cuerpo += card("Historial del expediente", linea_tiempo([
        ("12", "nov", "Asesoría programada: revisión del prototipo",
         "ASE-012 · Carlos Mendoza · 10:00",
         '<div class="mt-10">%s</div>' % badge("Programada", "b-amarillo", "reloj")),
        ("06", "nov", "Asesoría finalizada: impacto ambiental",
         "ASE-007 · Héctor Vargas · 15:00",
         '<div class="mt-10">%s</div>' % badge("Finalizada", "b-linea", "check")),
        ("28", "oct", "Diagnóstico revisado",
         "Puntaje heurísticas 7.8 de 10",
         '<div class="mt-10">%s</div>' % badge("Revisado", "b-azul", "check")),
    ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + _btn("layers", "Ver plan de trabajo",
                          "emprendimiento-plan.html")
                   + _btn("trend", "Ver tablero de seguimiento",
                          "seguimiento-dashboard.html", "btn btn-secundario")
                   + _btn("puntos", "Moderar comentarios", "comentarios.html",
                          "btn btn-secundario")
                   + _exportar("Exportar expediente")
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("expediente", cuerpo)
    return shell(R, "emprendimientos", "Sabor y Sabe", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Sabor y Sabe"],
                 sub="Expediente completo del emprendimiento y su grupo.",
                 acciones=_btn("izq", "Volver", "emprendimientos.html",
                               "btn btn-secundario"))


# --- 38. Plan de trabajo -----------------------------------------------------
def emprendimiento_plan():
    """Plan operativo del admin: fases, carga y estado, sin notas academicas."""
    cuerpo = metricas([
        ("layers", "Fases completadas", "1", "/ 4", 25, "FASE 2 en curso"),
        ("checklist", "Tareas en curso", "4", "/ 11", 36, "2 sin responsable"),
        ("reloj", "Días sin avance", "6", "", 40, "Último: 05 nov 2024"),
        ("calendar", "Asesorías programadas", "3", "", 60, "1 por confirmar"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
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
         "Responsable: Mariana López · 5 tareas abiertas",
         '<div class="mt-10">' + badge("En curso", "b-amarillo", "reloj")
         + '</div>'),
        ("20", "nov", "Revisión tecnica con el docente",
         "Responsable: Carlos Mendoza · Confirmado",
         '<div class="mt-10">' + badge("Confirmado", "b-azul", "check")
         + '</div>'),
        ("28", "nov", "Prueba de ventas en punto real",
         "Responsable: equipo del emprendimiento · Sin asignar",
         '<div class="mt-10">' + badge("Sin asignar", "b-amarillo")
         + '</div>'),
        ("05", "dic", "Evaluación y cierre de FASE 2",
         "Comite académico · Pendiente",
         '<div class="mt-10">' + badge("Pendiente", "b-neutra")
         + '</div>'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Código", "EMP-041"),
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente", "Carlos Mendoza"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<a class="btn btn-primario" href="seguimiento-dashboard.html">'
                     "%s Ver seguimiento</a>" % ico("trend", 16)
                   + '<a class="btn btn-secundario" href="asignaciones.html">'
                     "%s Reasignar docente</a>" % ico("sliders", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("plan", cuerpo)
    return shell(R, "emprendimientos", "Plan de trabajo", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Plan de trabajo"],
                 sub="Plan, fases y carga de trabajo del emprendimiento EMP-041.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>'
                          % ico("izq", 16))


def _cuerpo_avance():
    """Formulario de registrar avance; vive oculto y lo abre el modal
    (case 'registrar-avance' en lib_js) con prefill desde data-* de la fila."""
    cuerpo = '<div class="grid">'
    cuerpo += campo("Emprendimiento", valor="Sabor y Sabe", bloqueo="No editable",
                    name="emp")
    cuerpo += campo("Estudiante", valor="Mariana López", bloqueo="No editable",
                    name="estu")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Fase", ETAPAS, req=True, name="etapa")
    cuerpo += campo("Avance (%)", tipo="number", valor="62", req=True, name="avance")
    cuerpo += "</div>"
    cuerpo += campo("Notas del avance", tipo="textarea",
                    valor="Prototipo de empaque validado con el grupo focal.")
    cuerpo += '<div class="fila" style="margin-top:16px">'
    cuerpo += '<button class="btn btn-primario" data-accion="guardar-avance">'
    cuerpo += '%s Guardar avance</button>' % ico("check", 16)
    cuerpo += '<a class="btn btn-secundario" href="emprendimiento-plan.html">'
    cuerpo += '%s Ver plan de trabajo</a>' % ico("izq", 16)
    cuerpo += "</div>"
    cuerpo += '<div class="nota-foot">El avance actualiza el semáforo de estado '
    cuerpo += "y notifica al docente responsable.</div>"
    return cuerpo


def _sem(avance):
    """Semáforo de estado del emprendimiento a partir de su % de avance."""
    if avance == 0:
        return badge("Sin avance", "b-amarillo", "alerta")
    if avance < 60:
        return badge("En riesgo", "b-amarillo", "alerta")
    return badge("Al día", "b-azul", "check")


def _avance(accion, icono, etiqueta, cod="", emp="", estu="", etapa="",
            docente="", avance=""):
    """Botón 'Registrar avance' por fila; los datos viajan en data-* para el
    prefill del modal #form-avance."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("cod", cod), ("emp", emp), ("estu", estu), ("etapa", etapa),
        ("doc", docente), ("avance", avance)) if v)
    return ('<button data-accion="%s"%s title="%s" aria-label="%s">%s</button>'
            % (accion, extra, etiqueta, etiqueta, ico(icono, 16)))


def seguimiento():
    filas = []
    for cod, emp, estu, sector, tipo, etapa, avance, docente in EMPRENDIMIENTOS:
        filas.append([
            cod, "<b>%s</b>" % emp, estu,
            badge(sector, "b-azul" if sector == "Alimentos" else "b-neutra"),
            badge(etapa, "b-linea"),
            docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
            _barra(avance), _sem(avance),
            _acc(_b("eye", "Ver detalle", "ver-detalle"),
                 _avance("registrar-avance", "edit", "Registrar avance",
                         cod=cod, emp=emp, estu=estu, etapa=etapa,
                         docente=docente, avance=avance)),
        ])
    cuerpo = toolbar(
        filtros=(
            _sel("Filtrar por sector", ["Todos los sectores", "Alimentos", "Moda",
                                        "Ambiental", "Muebles", "Tecnología"],
                 data_filtro_col(3))
            + _sel("Filtrar por etapa", ["Todas las etapas"] + ETAPAS,
                   data_filtro_col(4))
            + _sel("Filtrar por docente",
                   ["Todos los docentes"] + [d[1] for d in DOCENTES]
                   + ["Sin asignar"], data_filtro_col(5))
            + _sel("Filtrar por estado",
                   ["Todo el estado", "Al día", "En riesgo", "Sin avance"],
                   data_filtro_col(7))
        ),
        acciones=_exportar("Exportar seguimiento"))
    cuerpo += '<div class="sep sep-12"></div>'
    cuerpo += '<div class="tabla-envoltura">'
    cuerpo += _tabla_t(
        ["Código", "Emprendimiento", "Estudiante", "Sector", "Etapa",
         "Docente", "Avance", "Estado", "@ACC"], filas,
        "Seguimiento de emprendimientos")
    cuerpo += _vacio(".tabla-envoltura tr",
                     "Sin emprendimientos que coincidan",
                     "Ajusta los filtros o la búsqueda para ver más resultados.",
                     "checklist")
    cuerpo += "</div>"
    cuerpo += '<div id="form-avance" hidden>' + _cuerpo_avance() + "</div>"
    cuerpo = formulario("seguimiento", cuerpo)
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Estado y avance de los %d emprendimientos del programa."
                     % len(EMPRENDIMIENTOS),
                 acciones=_btn("grid", "Ver tablero", "seguimiento-dashboard.html",
                               "btn btn-secundario"))
# --- 40. Tablero de seguimiento ----------------------------------------------
def seguimiento_dashboard():
    cuerpo = metricas([
        ("trend", "Avances del mes", "61", "", 88, "+14"),
        ("checklist", "Tareas sin calificar", "11", "", 34, None),
        ("alerta", "Emprendimientos en riesgo", "9", "", 20, None),
        ("medalla", "Promedio institucional", "87", "", 87, "+2"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
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
    cuerpo += '<div class="grid">'
    cuerpo += card("Salud de los seguimiento", donut(
        "", "", [("Al día", 31, AZUL), ("En riesgo", 9, AMAR),
                 ("Inactivos", 6, GRIS)], "emprendimientos"))
    cuerpo += card("Acciones sugeridas", lista_def([
        ("Asignar docente a 3 emprendimientos", "Sin asignar"),
        ("Contactar 6 estudiantes inactivos", "15 días sin avance"),
        ("Revisar 5 diagnosticos", "Sin revisión"),
    ]) + _vacio(".def-row", "Sin acciones pendientes",
                "Cuando haya emprendimientos sin docente, estudiantes inactivos "
                "o diagnósticos sin revisar, aparecerán aquí.", "checklist"))
    cuerpo += "</div></div>"
    cuerpo = formulario("tablero", cuerpo)
    return shell(R, "seguimiento", "Tablero de seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Tablero"],
                 sub="Métricas consolidadas de seguimiento institucional.",
                 acciones=_exportar("Exportar tablero"))


# --- 41. Asignar emprendimiento ---------------------------------------------
def asignar_emprendimiento():
    cuerpo = steps(["Seleccionar emprendimiento", "Elegir docente",
                    "Confirmar asignación"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Emprendimiento sin docente", tabla(
        ["Código", "Emprendimiento", "Estudiante", "Sector", "Etapa", "@ACC"],
        [["EMP-038", "<b>Aromas del Sur</b>", "Sofia Ramirez", "Alimentos",
          badge("FASE 1 - Ideación", "b-linea"), _acc(_b("check", "Seleccionar", "seleccionar"))],
         ["EMP-036", "<b>Sabores de la Costa</b>", "Daniel Rojas", "Alimentos",
          badge("FASE 1 - Ideación", "b-linea"), _acc(_b("check", "Seleccionar", "seleccionar"))],
         ["EMP-034", "<b>Eco Hogar</b>", "Valeria Cruz", "Muebles",
          badge("FASE 2 - Prototipo", "b-linea"), _acc(_b("check", "Seleccionar", "seleccionar"))]]))
    cuerpo += card("Docente disponible", tabla(
        ["Docente", "Área", "Carga actual", "Horas disponibles", "@ACC"],
        [["Carlos Mendoza", "Alimentos", "3 h de 5 h", "2 h",
          _acc(_b("check", "Seleccionar", "seleccionar"))],
         ["Paula Andrea Rios", "Moda", "2 h de 4 h", "2 h",
          _acc(_b("check", "Seleccionar", "seleccionar"))],
         ["Rafael Nieto", "Tecnología", "5 h de 6 h", "1 h",
          _acc(_b("check", "Seleccionar", "seleccionar"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Asignación seleccionada", lista_def([
        ("Emprendimiento", "Aromas del Sur"),
        ("Estudiante", "Sofia Ramirez"),
        ("Docente", "Carlos Mendoza"),
        ("Horas asignadas", "2 h por semana"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<button class="btn btn-primario" data-accion="confirmar-asignacion">'
                     '%s Confirmar asignación</button>' % ico("check", 16)
                   + '<button class="btn btn-secundario">%s Cancelar</button>'
                     % ico("x", 16)
                   + "</div>"
                     '<div class="nota-foot">El docente y el estudiante reciben una '
                     "notificación con la asignación.</div>")
    cuerpo += "</div></div>"

    # Modal para asignar docente por fila
    cuerpo += '<div id="form-asignar-docente" hidden>' + '</div>' + ""
    cuerpo += '<div class="grid">'
    cuerpo += campo("Estudiante", bloqueo="No editable", name="estudiante")
    cuerpo += campo("Emprendimiento", bloqueo="No editable", name="emprendimiento")
    cuerpo += campo("Correo", bloqueo="No editable", name="correo")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Docente", [d[1] + " - " + d[3] for d in DOCENTES] + ["Sin asignar"], req=True, name="docente")
    cuerpo += campo("Horas semanales", tipo="number", valor="2", req=True, name="horas")
    cuerpo += "</div>"
    cuerpo += '<div class="fila" style="margin-top:16px">'
    cuerpo += '<button class="btn btn-primario" data-accion="guardar-asignacion-docente">'
    cuerpo += '%s Guardar asignación</button>' % ico("check", 16)
    cuerpo += '<a class="btn btn-secundario" href="asignaciones.html">'
    cuerpo += '%s Volver</a>' % ico("izq", 16)
    cuerpo += "</div>"
    cuerpo += '<div class="nota-foot">El docente y el estudiante reciben una '
    cuerpo += "notificación con la asignación.</div>"
    cuerpo += "</div>"
    cuerpo = formulario("asignar", cuerpo)
    return shell(R, "asignaciones", "Asignar emprendimiento", cuerpo,
                 migas=["Inicio", "Asignaciones", "Asignar emprendimiento"],
                 sub="Asigna un docente a los emprendimientos que aún no lo tienen.",
                 acciones='<a class="btn btn-secundario" href="asignaciones.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 42. Moderacion de comentarios -------------------------------------------
def comentarios():
    """Dos colas lado a lado: lo reportado y lo visible. Sin tabla."""
    cuerpo = callout("Solo los comentarios <b>reportados</b> requieren moderación. "
                     "Borrar un comentario es permanente.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("alerta", "Reportados", "3", "", 25, None),
        ("chat", "Visibles", "27", "", 90, "+4"),
        ("trash", "Borrados este mes", "2", "", 12, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += '<div id="cola"></div>'
    cuerpo += card("Cola de moderación (3)", lista_avisos([
        ("Requieren decisión", [
            ("chat", "Comentario reportado en Sabor y Sabe",
             "Estudiante · EMP-041 · 12 nov 2024", "#cola",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Lenguaje inapropiado en Krea Textil",
             "Docente · EMP-040 · 12 nov 2024", "#cola",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Comentario duplicado en EcoPack",
             "Estudiante · EMP-039 · 11 nov 2024", "#cola",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
        ]),
    ]) + _vacio(".aviso", "Sin comentarios por moderar",
                "Los comentarios reportados aparecerán aquí para que decidas "
                "si aprobarlos o borrarlos.", "chat"))
    cuerpo += card("Publicados recientemente", '<div class="card-body">'
                   + '<div class="grid" style="gap:10px">'
                   + '<div class="fila-simple"><div><b>Consulta sobre el evento de costos</b>'
                     '<div class="nota-foot">Docente · EMP-041 · 10 nov 2024</div></div>'
                     '<div class="fila-6">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Sugerencia para el plan de trabajo</b>'
                     '<div class="nota-foot">Docente · EMP-037 · 09 nov 2024</div></div>'
                     '<div class="fila-6">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Duda sobre el costo de insumos</b>'
                     '<div class="nota-foot">Estudiante · EMP-035 · 08 nov 2024</div></div>'
                     '<div class="fila-6">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '</div></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Reglas de moderación", lista_def([
        ("Reportado", "3 en cola"),
        ("Visible", "27 publicados"),
        ("Oculto", "5 ocultos"),
        ("Borrado", "2 este mes"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<a class="btn btn-primario" href="#cola">%s '
                     'Moderar cola</a>' % ico("check", 16)
                   + '<a class="btn btn-secundario" href="reportes.html">%s '
                     'Ver reportes</a>' % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("comentarios", cuerpo)
    return shell(R, "comentarios", "Moderación de comentarios", cuerpo,
                 migas=["Inicio", "Moderación de comentarios"],
                 sub="Aprueba, oculta o borra comentarios de la comunidad.")


# --- 43. Metricas y programa de asesorias ------------------------------------
def _cuerpo_asesoria_form():
    """Formulario de crear/editar asesoría. Se abre en un modal desde asesorías();
    los campos llevan name para prefiltarlos al editar."""
    cuerpo = '<div class="grid">'
    cuerpo += select("Estudiante", [e[1] for e in ESTUDIANTES], req=True,
                     name="estudiante")
    cuerpo += select("Docente asignado", [d[1] for d in DOCENTES], req=True,
                     name="docente")
    cuerpo += '<div class="grid g-2">'
    cuerpo += campo("Fecha", tipo="date", req=True, name="fecha")
    cuerpo += campo("Hora", tipo="time", req=True, name="hora")
    cuerpo += "</div>"
    cuerpo += campo("Tema", ph="P. ej. Plan financiero del emprendimiento",
                    req=True, name="tema")
    cuerpo += select("Modalidad", ["Virtual", "Presencial"], valor="Virtual",
                     name="modalidad")
    cuerpo += select("Estado", ["Programada", "Confirmada", "En curso",
                                "Finalizada", "Cancelada"], valor="Programada",
                     name="estado")
    cuerpo += "</div>"
    return cuerpo


def _instrumento():
    """Resumen de solo lectura del instrumento del diagnóstico (A16): se
    desplega en un modal desde diagnosticos() para poder consultar las
    preguntas del cuestionario de 5 secciones / 22 preguntas."""
    secciones = [
        ("Perfil del emprendimiento", [
            "¿Cuál es el nombre de tu emprendimiento?",
            "¿Qué tipo de emprendimiento es?",
            "¿A qué sector productivo pertenece?",
            "¿Qué producto o servicio ofreces?",
            "¿En qué etapa del programa está tu emprendimiento?"]),
        ("Problema o necesidad", [
            "¿Qué problema concreto resuelve tu producto o servicio?",
            "¿A quién le ocurre ese problema?",
            "¿Cómo lo resuelven hoy (sin tu producto)?",
            "¿Qué tan urgente es el problema para tu cliente?"]),
        ("Propuesta de valor", [
            "¿Cuál es tu propuesta de valor en una frase?",
            "¿Qué beneficio concreto entrega al cliente?",
            "¿Qué te diferencia de la competencia?",
            "¿Qué necesidad principal cubre?"]),
        ("Mercado objetivo", [
            "¿Quién es tu cliente ideal (perfil)?",
            "¿Cuántos clientes potenciales estimas?",
            "¿Cuál es tu estrategia de precio?",
            "¿Qué canales usarás para llegarles?"]),
        ("Capacidad operativa y financiera", [
            "¿Con cuántas personas cuenta el equipo?",
            "¿Cuál es tu capacidad de producción actual?",
            "¿Llevas registro de costos y ventas?",
            "¿Qué inversión necesitas para crecer?",
            "¿Cuál es tu meta de ventas del próximo mes?"]),
    ]
    uls = []
    for i, (tit, preguntas) in enumerate(secciones, 1):
        items = "".join("<li>%s</li>" % p for p in preguntas)
        uls.append('<p><b>Sección %d · %s</b></p><ul style="margin:0 0 12px">%s</ul>'
                   % (i, tit, items))
    return ('<div class="suave">Cuestionario de 5 secciones y 22 preguntas que '
            "responde el estudiante al iniciar su plan.</div>" + "".join(uls))


def _cuerpo_emprendimiento():
    """Formulario de edición de emprendimiento (A07). Se abre en un modal desde
    emprendimientos(); los campos llevan name para prefiltarlos al editar."""
    cuerpo = '<div class="grid">'
    cuerpo += campo("Emprendimiento", valor="EcoPack", req=True, name="nombre")
    cuerpo += campo("Código", valor="EMP-039",
                    bloqueo="Código asignado por el sistema", name="codigo")
    cuerpo += select("Estudiante", [e[1] for e in ESTUDIANTES], req=True,
                     name="estudiante")
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Sector", ["Alimentos", "Moda", "Ambiental", "Muebles"],
                     req=True, name="sector")
    cuerpo += select("Tipo", ["Comercio", "Moda", "Industrial", "Alimentos",
                              "Artesanal"], req=True, name="tipo")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Etapa", ETAPAS, req=True, name="etapa")
    cuerpo += campo("Avance (%)", tipo="number", valor="62", req=True, name="avance")
    cuerpo += "</div>"
    cuerpo += select("Docente asignado", [d[1] for d in DOCENTES] + ["Sin asignar"],
                     valor="Sin asignar", name="docente")
    cuerpo += "</div>"
    return cuerpo


def asesorias():
    panel_res = metricas([
        ("chat", "Asesorías este mes", "38", "", 84, "+9"),
        ("reloj", "Promedio de respuesta", "4.2", " h", 42, "-0.6"),
        ("checklist", "Asesorías finalizadas", "31", "", 82, None),
        ("alerta", "Sin confirmar", "5", "", 22, None),
    ])
    panel_graf = card("Asesorías por mes", barras("","",["Jul","Ago","Sep","Oct","Nov"],[18,24,29,33,38],unidad=" asesorías"))+card("Asesorías por sector", barras_h("","",["Alimentos","Moda","Ambiental","Muebles","Tecnología"],[16,10,7,3,2],color=AMAR))
    panel_kpi = card("Estado de las asesorías", donut("","",[("Finalizadas",31,AZUL),("Confirmadas",7,AMAR),("Sin confirmar",5,GRIS),("Canceladas",3,GRIS)],"asesorías"))+card("Docentes con mejor respuesta", lista_def([("Hector Vargas","1.8 h promedio"),("Paula Andrea Rios","2.4 h promedio"),("Carlos Mendoza","3.1 h promedio")]))
    panel_prog = card("Programación de asesorías", tabla(["Estudiante","Docente","Fecha y hora","Tema","Modalidad","Estado","@ACC"], [ ["<b>{estu}</b>".format(estu=e), d, "{f} · {h}".format(f=_fmt_fecha(f), h=h), t, m, badge(es,BADGE.get(es.lower(),"b-neutra")), _acc(_asesoria("ver","eye","Ver asesoría"), _asesoria("editar-asesoria","edit","Editar asesoría",cod=c,estu=e,doc=d,fecha=f,hora=h,tema=t,mod=m,est=es), _asesoria("cancelar-asesoria","x","Cancelar asesoría",estu=e,fecha=_fmt_fecha(f),hora=h,tema=t))] for c,e,d,f,h,t,m,es in ASESORIAS]), accion=_nuevo("nueva-asesoria","Nueva asesoría"), sin_pad=True)
    panels = [("Resumen","ases-res",panel_res),("Gráficas","ases-graf",panel_graf),("KPIs","ases-kpi",panel_kpi),("Programación","ases-prog",panel_prog)]
    cuerpo = '<div class="sep sep-20"></div>'+tabs_paneles([(n,pid) for n,pid,_ in panels])+'<div class="sep sep-12"></div>'+''.join('<div data-panel-nombre="%s"%s>%s</div>'%(pid,'' if i==0 else ' hidden',b) for i,(_,pid,b) in enumerate(panels))+'<div id="form-asesoria" hidden>'+_cuerpo_asesoria_form()+'</div>'
    cuerpo = formulario("asesorias", cuerpo)
    return shell(R, "asesorias", "Métricas de asesorías", cuerpo,
                 migas=["Inicio","Asesorías"],
                 sub="Indicadores de uso, respuesta y programación del servicio de asesorías.",
                 acciones=_exportar("Exportar asesorías"))
# --- 44. Eventos -------------------------------------------------------------
def eventos():
    """Pipeline editorial con calendario y agenda de eventos."""
    cuerpo = metricas([
        ("calendar", "Eventos publicados", "2", "", 40, None),
        ("reloj", "Por aprobar", "1", "", 20, None),
        ("doc", "Borradores", "1", "", 20, None),
        ("users", "Confirmaciones", "141", "", 88, "+37"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Próximos eventos",
                   agenda([
                       ("18 nov 2024", [
                           ("09:00", "Taller de costos y precios",
                            "Auditorio A · 32 de 40 cupos",
                            badge("Publicado", "b-azul", "check")),
                       ]),
                       ("22 nov 2024", [
                           ("14:00", "Feria de emprendedores",
                            "Plaza central · 86 de 120 cupos",
                            badge("Publicado", "b-azul", "check")),
                       ]),
                       ("25 nov 2024", [
                           ("08:30", "Jornada de mentoria",
                            "Sala 2 · 14 confirmados",
                            badge("Por aprobar", "b-amarillo", "reloj")),
                       ]),
                   ]))
    cuerpo += card("Calendario de noviembre",
                   '<div data-vacio-lista>'
                   + calendario_interactivo("noviembre", 2024, EVENTOS_CAL,
                                              hoy=12, vacio="Sin eventos")
                   + "</div>")
    cuerpo += "</div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += kanban([
        ("Por aprobar", [
            ("<b>Jornada de mentoria</b>",
             "25 nov 2024, 08:30 · Sala 2 · 14 confirmados",
             badge("1 solicitud", "b-amarillo", "reloj"),
             _evento("aprobar-evento", "check", "Aprobar evento",
                     titulo="Jornada de mentoria", fecha="25 nov 2024, 08:30",
                     lugar="Sala 2", confirmados="14", sector="Alimentos",
                     primario=True)
             + _evento("rechazar-evento", "x", "Rechazar",
                       titulo="Jornada de mentoria")),
        ]),
        ("Borrador", [
            ("<b>Charla: marco legal para negocios</b>",
             "02 dic 2024, 10:00 · Auditorio B",
             badge("Sin publicar", "b-neutra"),
             _btn("edit", "Editar", "evento-form.html", "btn btn-sm btn-secundario")),
        ]),
        ("Publicado", [
            ("<b>Taller de costos y precios</b>",
             "18 nov 2024, 09:00 · Auditorio A",
             badge("32 de 40 cupos", "b-azul"),
             _btn("edit", "Editar", "evento-form.html", "btn btn-sm btn-secundario")),
            ("<b>Feria de emprendedores</b>",
             "22 nov 2024, 14:00 · Plaza central",
             badge("86 de 120 cupos", "b-azul"),
             _btn("edit", "Editar", "evento-form.html", "btn btn-sm btn-secundario")),
        ]),
        ("Finalizados", [
            ("<b>Charla: opciones de financiamiento</b>",
             "04 nov 2024, 10:00 · Auditorio B · 48 asistentes",
             badge("Cerrado", "b-linea"),
             _btn("eye", "Ver", "evento-form.html", "btn btn-sm btn-secundario")),
        ]),
    ])
    cuerpo += ('<p class="nota-foot">Publicar un evento notifica a los estudiantes '
               'del sector correspondiente.</p>')
    cuerpo = formulario("eventos", cuerpo)
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Aprueba y publica eventos del programa.",
                 acciones=_btn("plus", "Crear evento", "evento-form.html"))
# --- 45. Crear evento --------------------------------------------------------
def evento_form():
    cuerpo = steps(["Datos del evento", "Fecha y lugar", "Publicar"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del evento",
                   campo("Título del evento", valor="Taller de costos y precios", req=True)
                   + select("Dirigido a", ["Todos los estudiantes",
                                           "Solo Alimentos", "Solo Moda",
                                           "Solo Ambiental", "Solo Muebles"],
                            req=True, valor="Alimentos")
                   + campo("Descripción", alto=True,
                           valor="Taller practico para calcular el costo de insumos y "
                                 "definir el punto de equilibrio de un emprendimiento.",
                           ph="De que tratara el evento")
                   + campo("Cupo máximo", tipo="number", valor="40",
                           ph="Número de asistentes"))
    cuerpo += card("Fecha y lugar",
                   campo("Fecha", tipo="date", valor="2024-11-18", req=True)
                   + campo("Hora de inicio", tipo="time", valor="09:00", req=True)
                   + campo("Hora de cierre", tipo="time", valor="11:00", req=True)
                   + campo("Lugar", valor="Auditorio A")
                   + campo("Link de inscripción",
                           valor="sgemd.edu.co/eventos/taller-costos"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Visibilidad", lista_def([
        ("Visibilidad", "Visible para-Alimentos"),
        ("Confirmaciones", "32 de 40"),
        ("Recordatorio", "Un día antes"),
    ]) + _vacio(".def-row", "Sin configuración de visibilidad",
                "Selecciona a qué sector va dirigido el evento y su "
                "recordatorio antes de publicar.", "eye"))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<button class="btn btn-primario" data-accion="publicar-evento">'
                     '%s Publicar evento</button>' % ico("enviar", 16)
                    + '<button class="btn btn-secundario" data-accion="guardar-borrador">'
                      '%s Guardar borrador</button>' % ico("doc", 16)
                   + '<a class="btn btn-secundario" href="eventos.html">%s Cancelar</a>'
                     % ico("x", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("crear-evento", cuerpo)
    return shell(R, "eventos", "Crear evento", cuerpo,
                 migas=["Inicio", "Eventos", "Crear evento"],
                 sub="Publica un evento y notifica a los asistentes.",
                 acciones='<button class="btn btn-primario" data-accion="guardar-borrador">'
                          '%s Guardar</button>' % ico("check", 16))


# --- 46. Asignaciones --------------------------------------------------------
def asignaciones():
    """Carga de docentes arriba, cola de asignaciones pendientes abajo."""
    cuerpo = callout("Un docente puede tener hasta <b>12 emprendimientos</b>. "
                     "La carga semanal se descuenta del cupo disponible.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("sliders", "Asignaciones vigentes", "43", "", 93, None),
        ("alerta", "Sin docente", "3", "", 18, None),
        ("reloj", "Carga promedio", "3.1", " h", 62, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Cupo ocupado por docente", '<div class="card-body">'
                   + distribucion([
                       ("P. A. Rios", "6 h", 50),
                       ("C. Mendoza", "8 h", 67),
                       ("H. Vargas", "9 h", 75),
                       ("N. Beltran", "11 h", 92),
                   ])
                   + '<p class="nota-foot">Cupo máximo de 12 h por docente. '
                     'Ninafq Beltran tiene 1 h libre.</p></div>')
    cuerpo += card("Pendientes de asignar", tabla(
        ["Emprendimiento", "Estudiante", "Sector", "Horas sugeridas", "@ACC"],
        [["<b>EMP-038 Aromas del Sur</b>", "Sofia Ramirez", "Alimentos",
          badge("3 h", "b-neutra"), _acc(_b("edit", "Asignar", "asignar"))],
         ["<b>EMP-034 Eco Hogar</b>", "Valeria Cruz", "Hogar",
          badge("2 h", "b-neutra"), _acc(_b("edit", "Asignar", "asignar"))],
         ["<b>EMP-033 Pan de Abuela</b>", "Valentina Gómez", "Alimentos",
          badge("3 h", "b-neutra"), _acc(_b("edit", "Asignar", "asignar"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Resumen", lista_def([
        ("Vigentes", "43 de 46"),
        ("Pendientes", "3"),
        ("Cupo total", "12 por docente"),
        ("Carga promedio", "3.1 h semanales"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + _btn("plus", "Asignar emprendimiento", "asignaciones.html")
                   + _exportar("Exportar asignaciones")
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("asignaciones", cuerpo)
    return shell(R, "asignaciones", "Asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones"],
                 sub="Docente asignado por emprendimiento y carga semanal.")


# --- 47. Diagnosticos --------------------------------------------------------
def diagnosticos():
    """Gráfico de puntajes + cola de revisión con pestañas."""
    panel_res = metricas([
        ("clipboard", "Respondidos", "94", "", 88, "+8"),
        ("reloj", "Sin revisión", "5", "", 22, None),
        ("medalla", "Promedio", "74", "", 74, "+2"),
    ])
    panel_graf = card("Puntaje por emprendimiento", '<div class="card-body">')+barras_h("", "Último diagnóstico registrado", ["EcoPack", "Sabor y Sabe", "Aromas del Sur", "Krea Textil", "Muebles Origen"], [91,78,64,71,70], maximo=100)+'</div>'+card("Rendimiento del grupo", '<div class="card-body">')+distribucion([("90 - 100","12",26),("70 - 89","45",48),("50 - 69","28",30),("Menos de 50","9",19)])+'<p class="nota-foot">La mayoria de los estudiantes se ubica entre 70 y 89 puntos.</p></div>'
    panel_pen = card("Pendientes de revisión", '<div class="card-body">')+lista_avisos([("Sin revisión del docente", [("clipboard", "Aromas del Sur · Sofia Ramirez", "Sin docente asignado · 02 nov 2024", "diagnosticos.html", "alta", _b("check","Revisar")), ("clipboard", "Krea Textil · Jhon Ospina", "Paula Andrea Rios · 30 oct 2024", "diagnosticos.html", "media", _b("check","Revisar")), ("clipboard", "Muebles Origen · Andres Felipe", "Ninafq Beltran · 18 oct 2024", "diagnosticos.html", "media", _b("check","Revisar"))])])+_vacio(".aviso", "Sin diagnósticos pendientes", "Cuando los estudiantes respondan nuevos diagnósticos, aparecerán aquí para su revisión.", "clipboard")+'</div>'+card("Acciones", '<div class="fila-col">')+_btn("download","Exportar resultados","reportes.html","btn btn-secundario")+'<button class="btn btn-secundario" data-accion="ver-instrumento">%s Ver instrumento</button>'%ico("doc",16)+"</div>"
    panels = [("Resumen","diag-res",panel_res),("Gráficas","diag-graf",panel_graf),("Pendientes","diag-pen",panel_pen)]
    cuerpo = '<div class="sep sep-20"></div>'+tabs_paneles([(n,pid) for n,pid,_ in panels])+'<div class="sep sep-12"></div>'+''.join('<div data-panel-nombre="%s"%s>%s</div>'%(pid,'' if i==0 else ' hidden',b) for i,(_,pid,b) in enumerate(panels))+'<div id="contenido-instrumento" hidden>'+_instrumento()+'</div>'
    cuerpo = formulario("diagnosticos", cuerpo)
    return shell(R, "diagnosticos", "Diagnosticos respondidos", cuerpo, migas=["Inicio","Diagnosticos"], sub="Resultados del diagnóstico de los estudiantes.")
def reportes():
    cuerpo = card("Tipo de reporte", tabla(
        ["Reporte", "Descripción", "Formato", "Última generación", "@ACC"],
        [[badge("Seguimiento", "b-linea"), "Avances y calificación por emprendimiento",
          "CSV y PDF", "12 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Asesorías", "b-linea"), "Uso y respuesta del servicio de asesorías",
          "CSV y PDF", "11 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Emprendimientos", "b-linea"), "Inventario completo con sector y etapa",
          "CSV y PDF", "10 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Diagnosticos", "b-linea"), "Puntajes del diagnóstico por estudiante",
          "CSV y PDF", "08 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))]]),
        sin_pad=True)
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Filtros del reporte", select("Formato", ["CSV", "PDF", "XLSX"], req=True,
                                                 valor="CSV")
                   + select("Periodo", ["Últimos 30 días", "Últimos 3 meses",
                                        "Todo el periodo"], req=True,
                            valor="Últimos 3 meses")
                   + select("Docente", ["Todos los docentes", "Carlos Mendoza",
                                        "Paula Andrea Rios", "Hector Vargas"], req=True,
                            valor="Todos los docentes")
                   + campo("Enviar por correo", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co"))
    cuerpo += card("Resumen de la exportación",
                   lista_def([
                       ("Emprendimientos incluidos", "46"),
                       ("Estudiantes incluidos", "110"),
                       ("Estimación de filas", "1.284"),
                       ("Último archivo generado", "12 nov 2024, 09:20"),
                   ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<button class="btn btn-primario" data-accion="generar-reporte">'
                     '%s Generar reporte</button>' % ico("download", 16)
                   + '<button class="btn btn-secundario" data-accion="descargar-plantilla">'
                     '%s Descargar plantilla</button>' % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div>"
    cuerpo = formulario("reportes", cuerpo)
    return shell(R, "reportes", "Exportar reportes", cuerpo,
                 migas=["Inicio", "Reportes"],
                 sub="Genera y descarga reportes institucionales en CSV, PDF o XLSX.",
                 acciones='<button class="btn btn-primario" data-accion="generar-reporte">'
                          '%s Generar</button>' % ico("check", 16))


# --- 52. Tareas (consulta, alta y baja) --------------------------------------
# Vista completa aprobada en la auditoria V3: el admin revisa el tablero de
# tareas por emprendimiento y puede añadir (modal con insercion real de fila)
# o eliminar (confirmacion + baja de la fila). Calificar sigue siendo del
# docente; aqui solo se gestiona la asignacion.
TAREAS_ADM = [
    ("Evidencia fotográfica del punto de venta", "Sabor y Sabe", "Mariana López",
     "Alta", "12 nov 2024", "En revisión"),
    ("Presupuesto de insumos", "Sabor y Sabe", "Mariana López",
     "Media", "15 nov 2024", "Completada"),
    ("Perfil en redes sociales", "Krea Textil", "Jhon Ospina",
     "Baja", "16 nov 2024", "Pendiente"),
    ("Prototipo de empaque", "EcoPack", "Lucía Fernández",
     "Alta", "14 nov 2024", "En revisión"),
    ("Análisis de competencia", "Aromas del Sur", "Sofía Ramírez",
     "Media", "18 nov 2024", "Pendiente"),
]

PRIO_ADM = {"Alta": "b-amarillo", "Media": "b-azul", "Baja": "b-linea"}
ESTADO_TAREA_ADM = {"En revisión": "b-amarillo", "Completada": "b-azul",
                    "Pendiente": "b-neutra", "Devuelta": "b-neutra"}


def _cuerpo_tarea_adm():
    """Formulario de alta/edición de tarea; vive oculto y lo abre el modal
    (case 'nueva-tarea' / 'editar-tarea' en lib_js)."""
    emps = ["Sabor y Sabe", "Krea Textil", "EcoPack", "Aromas del Sur"]
    ests = ["Mariana López", "Jhon Ospina", "Lucía Fernández", "Sofía Ramírez"]
    return ('<div class="grid g-2 g-col">'
            + campo("Título de la tarea", ph="Ej.: Presentación de pitch", req=True)
            + select("Emprendimiento", ["- Elegir -"] + emps)
            + select("Estudiante", ["- Elegir -"] + ests)
            + select("Prioridad", ["Baja", "Media", "Alta"], valor="Media")
            + campo("Vence el", tipo="date")
            + campo("Puntos", tipo="number", valor="100")
            + "</div>"
            + campo("Descripción (opcional)", alto=True,
                    ph="Detalla qué debe entregar el estudiante"))


def tareas():
    filas_t = [
        ["<b>%s</b>" % t, emp, estu, badge(prio, PRIO_ADM[prio]), vence,
         badge(est, ESTADO_TAREA_ADM[est]),
         _acc(_b("edit", "Editar", "editar-tarea"),
              _b("trash", "Eliminar", "eliminar-tarea"))]
        for t, emp, estu, prio, vence, est in TAREAS_ADM
    ]
    filas_emp = [
        ["EMP-041", "<b>Sabor y Sabe</b>", "Mariana López",
         badge("FASE 2 - Prototipo", "b-linea"), "2",
         _acc(_b("eye", "Ver tareas", "ver-tareas"))],
        ["EMP-039", "<b>Krea Textil</b>", "Jhon Ospina",
         badge("FASE 3 - Validación", "b-linea"), "1",
         _acc(_b("eye", "Ver tareas", "ver-tareas"))],
        ["EMP-037", "<b>EcoPack</b>", "Lucía Fernández",
         badge("FASE 2 - Prototipo", "b-linea"), "1",
         _acc(_b("eye", "Ver tareas", "ver-tareas"))],
        ["EMP-038", "<b>Aromas del Sur</b>", "Sofía Ramírez",
         badge("FASE 1 - Ideación", "b-linea"), "1",
         _acc(_b("eye", "Ver tareas", "ver-tareas"))],
    ]
    cuerpo = callout("Como administrador puedes <b>consultar, añadir y eliminar</b> "
                     "tareas de cualquier emprendimiento. La calificación de las "
                     "entregas la realiza el docente.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += toolbar(filtros=(
        _sel("Filtrar por estado", ["Todos los estados", "Pendiente",
                                    "En revisión", "Completada"],
             data_filtro_col(5))
        + _sel("Filtrar por prioridad", ["Toda la prioridad", "Alta", "Media",
                                         "Baja"],
               data_filtro_col(3))))
    cuerpo += card("Emprendimientos con tareas", tabla(
        ["Código", "Emprendimiento", "Estudiante", "Etapa", "Tareas", "@ACC"],
        filas_emp, caption="Emprendimientos con tareas asignadas"), sin_pad=True)
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div id="zona-tareas">'
    cuerpo += card("Tareas asignadas a estudiantes", tabla(
        ["Tarea", "Emprendimiento", "Estudiante", "Prioridad", "Vence",
         "Estado", "@ACC"], filas_t, caption="Tareas asignadas a estudiantes"),
        accion=_nuevo("nueva-tarea", "Nueva tarea"), sin_pad=True)
    cuerpo += "</div>"
    cuerpo += paginas(1, 5, len(TAREAS_ADM))
    cuerpo += '<div id="form-tarea" hidden>' + _cuerpo_tarea_adm() + "</div>"
    cuerpo = formulario("tareas", cuerpo)
    return shell(R, "tareas", "Tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Consulta, alta y baja de tareas por emprendimiento.",
                 acciones=_nuevo("nueva-tarea", "Nueva tarea"))


# --- 49. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = metricas([
        ("users", "Usuarios gestionados", "128", "", 84, "+12"),
        ("medalla", "Reportes generados", "24", "", 62, "+4"),
        ("alerta", "Decisiones pendientes", "12", "", 20, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos personales",
                   '<div class="campos-perfil">'
                   + campo("Nombres", valor="Ana", req=True)
                   + campo("Apellidos", valor="Restrepo", req=True)
                   + campo("Correo institucional", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Teléfono", tipo="tel", valor="+57 301 555 0199")
                   + "</div>")
    cuerpo += card("Zona horaria", campo("Zona horaria", valor="America/Bogota")
                   + campo("Cargo", valor="Administradora del programa",
                           bloqueo="El cargo lo asigna la institución"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Seguridad", lista_def([
        ("Contraseña", "Actualizada hace 2 meses"),
        ("Verificación en dos pasos", "Activada"),
        ("Último acceso", "Hoy, 07:15"),
    ]) + _vacio(".def-row", "Sin datos de seguridad",
                "La información de tu contraseña y tu último acceso "
                "aparecerá aquí.", "lock"))
    cuerpo += card("Cambiar contraseña",
                   '<div class="grid g-3 g-col">'
                   + campo("Contraseña actual", tipo="password", ph="••••••••")
                   + campo("Nueva contraseña", tipo="password", ph="Mínimo 8 caracteres")
                   + campo("Repetir nueva contraseña", tipo="password", ph="••••••••")
                   + "</div>"
                   '<div style="display:flex;justify-content:flex-end">'
                   + '<button class="btn btn-secundario" data-accion="actualizar-contrasena">'
                     '%s Actualizar contraseña</button></div>' % ico("lock", 16))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<button class="btn btn-primario" data-accion="guardar-perfil">'
                     '%s Guardar cambios</button>' % ico("check", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo = formulario("perfil", cuerpo)
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Actualiza tus datos y revisa tu actividad.")


# --- 50. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja del administrador: items .notif + chips de filtro (NO2/NO3).

    Replica la bandeja de estudiante y docente (avisos enlazados a la vista
    donde se resuelven, chip de tipo con filtrado y contador "sin leer" que
    persiste en localStorage) y conserva la agenda agrupada por fecha como
    sección secundaria de trazabilidad (90 días).
    """
    no_leidas = sum(1 for n in NOTIFS_ADMIN if not n[0])
    dias = [
        ("Hoy, 12 de noviembre", [
            ("08:15", "3 emprendimientos siguen sin docente",
             "Asignaciones · Sin docente asignado",
             '<a class="btn btn-sm btn-primario" href="asignaciones.html">'
             'Asignar</a>'),
            ("09:40", "5 diagnosticos sin revisión",
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
             "Moderación · Cola de reportes",
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
        ("bell", "Sin leer", str(no_leidas), "", 18, None),
        ("check", "Aprobaciones del mes", "24", "", 62, None),
        ("users", "Docentes activos", "8", "", 88, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += ('<div class="card"><div class="card-head">'
               '<h3>Bandeja de notificaciones</h3>'
               '<span class="hint" id="contador-no-leidas" aria-live="polite">%d sin leer</span></div>'
               '<div class="card-body sin-pad">' % no_leidas)
    cuerpo += "".join(
        '<a class="notif%s" href="%s" data-tipo="%s" data-i="%d">'
        '<span class="notif-ico">%s</span>'
        '<div class="notif-cuerpo"><h3>%s</h3><p>%s</p><time>%s</time></div>'
        '<span class="notif-flecha">%s</span>%s</a>'
        % (" no-leida" if not leer else "", href, tipo, i, ico(ic, 17),
           t, txt, f, ico("der", 16),
           '<span class="notif-dot"></span>' if not leer else "")
        for i, (leer, t, txt, f, ic, tipo, href) in enumerate(NOTIFS_ADMIN)
    )
    cuerpo += _vacio(".notif", "Sin notificaciones",
                      "Cuando haya asignaciones, diagnósticos, eventos o "
                      "reportes nuevos, se avisará aquí.", "bell")
    cuerpo += "</div></div>"
    cuerpo += card("Actividad reciente", agenda(dias))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Filtros", '<div style="display:flex;flex-direction:column;'
                              'gap:8px">'
                    + "".join('<span class="chip%s" data-chip="%s">%s</span>'
                              % (" on" if i == 0 else "", val, etiqueta)
                              for i, (val, etiqueta) in enumerate(
                                  [("todas", "Todas"), ("sin-leer", "Sin leer"),
                                   ("asignacion", "Asignaciones"),
                                   ("diagnostico", "Diagnósticos"),
                                   ("evento", "Eventos"),
                                   ("reporte", "Reportes")]))
                    + "</div>")
    cuerpo += card("Retención", lista_def([
        ("Registro de decisiones", "90 días"),
        ("Exportación", "CSV desde Reportes"),
        ("Archivado automático", "Al resolverse"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += ('<p class="nota-foot">El registro conserva 90 días y se puede '
               'exportar desde Reportes.</p>')
    cuerpo = formulario("notificaciones", cuerpo)
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Registro de aprobaciones y decisiones del equipo.",
                 acciones='<button class="btn btn-secundario" data-accion='
                          '"marcar-todas-como-leidas">%s Marcar todo como leído</button>'
                          % ico("check", 16))# --- 51. Respaldos ----------------------------------------------------------
def respaldos():
    cuerpo = metricas([
        ("carpeta","Respaldos realizados","12","",80,"+3"),
        ("reloj","Último respaldo","12 nov 2024","",100,None),
        ("download","Tamaño ocupado","84"," MB",75,None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    filas=[["BKP-20241112-0915","Completo","12 nov 2024, 09:15","84 MB","Exitosa", _acc(_b("download","Descargar"), _b("eye","Ver detalle"))],["BKP-20241111-0910","Parcial","11 nov 2024, 09:10","41 MB","Exitosa", _acc(_b("download","Descargar"))],["BKP-20241110-0912","Completo","10 nov 2024, 09:12","83 MB","Fallida", _acc(_b("download","Descargar"))]]
    cuerpo += card("Historial de respaldos", tabla(["Código","Tipo","Fecha y hora","Tamaño","Estado","@ACC"],filas, caption="Historial de respaldos"), accion='<button class="btn btn-primario" data-accion="crear-respaldo">%s Crear respaldo</button>'%ico("download",16), sin_pad=True)
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += card("Configuración de respaldo", lista_def([("Frecuencia","Diaria a las 09:00"),("Destino","Almacenamiento institucional"),("Retención","30 días"),("Notificación","ana.restrepo@sgemd.edu.co")]))
    cuerpo = formulario("respaldos", cuerpo)
    return shell(R,"respaldos","Respaldos y recuperación", cuerpo, migas=["Inicio","Respaldos"], sub="Gestión de respaldos y verificación de integridad.")


def registrar(reg):
    paginas_adm = [
        ("dashboard.html", "01 Admin - Inicio (dashboard)", dashboard),
        ("usuarios.html", "02 Admin - Gestión de perfiles", usuarios),
        ("solicitudes.html", "03 Admin - Solicitudes pendientes", solicitudes),
        ("emprendimientos.html", "04 Admin - Emprendimientos", emprendimientos),
        ("emprendimiento-expediente.html",
         "05 Admin - Expediente del emprendimiento", emprendimiento_expediente),
        ("emprendimiento-plan.html", "06 Admin - Plan de trabajo",
         emprendimiento_plan),
        ("seguimiento.html", "07 Admin - Seguimiento", seguimiento),
        ("seguimiento-dashboard.html", "08 Admin - Tablero de seguimiento",
         seguimiento_dashboard),
        ("comentarios.html", "10 Admin - Moderación de comentarios", comentarios),
        ("asesorias.html", "11 Admin - Asesorías", asesorias),
        ("eventos.html", "12 Admin - Eventos", eventos),
        ("evento-form.html", "13 Admin - Crear evento", evento_form),
        ("asignaciones.html", "14 Admin - Asignaciones", asignaciones),
        ("diagnosticos.html", "15 Admin - Diagnósticos", diagnosticos),
        ("reportes.html", "16 Admin - Reportes", reportes),
        ("tareas.html", "17 Admin - Tareas", tareas),
        ("perfil.html", "18 Admin - Mi perfil", perfil),
        ("notificaciones.html", "19 Admin - Notificaciones", notificaciones),
        ("respaldos.html", "20 Admin - Respaldos y recuperación", respaldos),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_adm):
        reg("admin", arch, tit, _envolver(fn), i)
