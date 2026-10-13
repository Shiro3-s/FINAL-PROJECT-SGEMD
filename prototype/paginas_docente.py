# -*- coding: utf-8 -*-
"""Rol DOCENTE - 17 pantallas.

Reglas del rol:
  - Solo ve los emprendimientos que tiene asignados.
  - Registra y califica avances; el estudiante solo consulta su historial.
  - Confirma fecha y hora de la asesoria que el estudiante solicito (BR-002).
  - Revisa el diagnostico y deja recomendaciones; el estudiante lo responde.

Refactor UX/UI (ver cambios-a-docente.md): las acciones del docente ya no abren
ventanas modales: cada una lleva a una vista completa. Solo las confirmaciones
destructivas sin formulario (marcar todo leido) siguen siendo un dialogo. Cada
pagina inyecta un bundle CSS/JS propio del rol via _inyectar(). El script captura
en fase de captura y atiende sus data-accion; el resto lo sigue manejando lib_js.
"""

import re

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, lista_avisos,
    tarjeta_emp, kanban, agenda, linea_tiempo,
)
from lib_charts import (
    barras, barras_h, donut, stacked_tareas, progreso_fases, circular, AZUL, AMAR,
)

R = "docente"

DOCENTE_CSS = (
    ".sep{height:20px}"
    ".sep-lg{height:22px}"
    ".acciones-col{display:flex;flex-direction:column;gap:10px}"
    ".form-acciones{display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap}"
    ".acciones-rapidas{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}"
    ".acciones-rapidas .btn{width:100%}"
    ".resultados-contador{font-size:13px;color:var(--tinta-2);margin-left:auto}"
    ".prog{min-width:110px}"
    ".prog-num{font-size:13px;color:var(--tinta-2)}"
    ".chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}"
    ".chip.activo{background:var(--amarillo);border-color:var(--amarillo);color:var(--tinta)}"
    ".aviso[hidden]{display:none}"
    ".comentarios{display:flex;flex-direction:column;gap:14px}"
    ".comentario{border:1px solid var(--gris);border-radius:var(--r-sm);padding:12px 14px;"
    "background:var(--blanco)}"
    ".comentario-cab{display:flex;align-items:baseline;gap:8px;margin-bottom:6px}"
    ".comentario-autor{font-size:13px;font-weight:700;color:var(--tinta)}"
    ".comentario-fecha{font-size:13px;color:var(--tinta-2)}"
    ".comentario-texto{font-size:14px;color:var(--tinta-2);line-height:1.6}"
    ".comentario-form{margin-top:16px}"
    ".campo input[type=number]{width:100%;height:40px;border:1px solid var(--gris);"
    "border-radius:var(--r-sm);padding:0 12px;font-family:var(--sans);font-size:14px;"
    "color:var(--tinta);background:var(--blanco)}"
    ".texto-ayuda{font-size:14px;line-height:1.6;color:var(--tinta-2)}"
    ".medida{min-width:110px}"
    "@media (max-width:479px){.acciones-rapidas{grid-template-columns:minmax(0,1fr)}}"
)

DOCENTE_JS = """
(function () {
  "use strict";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  var GUARDAR = {
    "guardar-avance": "Avance registrado",
    "guardar-calificacion": "Calificacion guardada",
    "devolver-tarea": "Tarea devuelta al estudiante",
    "asignar-tarea": "Tarea asignada",
    "generar-asesoria": "Asesoria generada",
    "confirmar-asesoria": "Asesoria confirmada",
    "reprogramar-asesoria": "Nueva fecha propuesta",
    "rechazar-asesoria": "Solicitud rechazada",
    "guardar-recomendaciones": "Recomendaciones guardadas",
    "actualizar-contrasena": "Contrasena actualizada"
  };

  var pila = null;
  function toast(msg, tipo) {
    if (!pila) {
      pila = document.createElement("div");
      pila.className = "toast-pila";
      pila.setAttribute("role", "status");
      pila.setAttribute("aria-live", "polite");
      document.body.appendChild(pila);
    }
    var t = document.createElement("div");
    t.className = "toast t-" + (tipo || "info");
    t.appendChild(document.createTextNode(msg));
    pila.appendChild(t);
    setTimeout(function () { t.classList.add("va-fuera"); }, 3200);
    setTimeout(function () { t.remove(); }, 3700);
  }

  function cerrarModal() {
    var v = $(".modal-velo");
    if (v) v.remove();
    document.body.classList.remove("sin-scroll");
  }

  function confirmar(titulo, texto, al) {
    cerrarModal();
    var velo = document.createElement("div");
    velo.className = "modal-velo";
    var caja = document.createElement("div");
    caja.className = "modal";
    caja.setAttribute("role", "dialog");
    caja.setAttribute("aria-modal", "true");
    caja.setAttribute("aria-label", titulo);
    var head = document.createElement("div");
    head.className = "modal-head";
    var h2 = document.createElement("h2");
    h2.textContent = titulo;
    head.appendChild(h2);
    var cuerpo = document.createElement("div");
    cuerpo.className = "modal-cuerpo";
    var p = document.createElement("p");
    p.className = "confirm-texto";
    p.textContent = texto;
    cuerpo.appendChild(p);
    var pie = document.createElement("div");
    pie.className = "modal-foot";
    var no = document.createElement("button");
    no.className = "btn btn-secundario";
    no.textContent = "Cancelar";
    no.addEventListener("click", cerrarModal);
    var si = document.createElement("button");
    si.className = "btn btn-peligro";
    si.textContent = "Confirmar";
    si.addEventListener("click", function () {
      cerrarModal();
      if (al) al();
    });
    pie.appendChild(no);
    pie.appendChild(si);
    caja.appendChild(head);
    caja.appendChild(cuerpo);
    caja.appendChild(pie);
    velo.appendChild(caja);
    document.body.appendChild(velo);
    document.body.classList.add("sin-scroll");
    si.focus();
  }

  function slug(txt) {
    return (txt || "").toLowerCase().normalize("NFD")
      .replace(/[\\u0300-\\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  /* Emprendimientos asignados: al elegir un estudiante se sustituye la lista
     por las pestanas de sus emprendimientos (uno por emprendimiento). */
  var selEst = $("#sel-estudiante");
  if (selEst) {
    var lista = $("#lista-emprendimientos");
    var det = $("#detalle-estudiante");
    var pintar = function () {
      var v = slug(selEst.value);
      if (lista) lista.hidden = !!v;
      if (det) det.hidden = !v;
      $$("[data-est-perfil]").forEach(function (s) {
        s.hidden = s.getAttribute("data-est-perfil") !== v;
      });
      if (v) {
        var sec = $("[data-est-perfil]:not([hidden])");
        if (sec) {
          var t = $(".tabs button", sec);
          if (t) t.click();
        }
      } else if (lista) {
        var t0 = $(".tabs button", lista);
        if (t0) t0.click();
      }
    };
    selEst.addEventListener("change", pintar);
    if (selEst.value) pintar();
  }

  function aplicarFiltroDesdeURL() {
    var m = location.search.match(/[?&]f=([^&]+)/);
    if (!m) return;
    var val = decodeURIComponent(m[1].split("+").join(" "));
    var sels = document.querySelectorAll("select[data-filtro]");
    for (var i = 0; i < sels.length; i++) {
      var s = sels[i], ok = false;
      for (var j = 0; j < s.options.length; j++) {
        if (s.options[j].value === val) { ok = true; break; }
      }
      if (ok) { s.value = val; s.dispatchEvent(new Event("change")); return; }
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", aplicarFiltroDesdeURL);
  } else {
    aplicarFiltroDesdeURL();
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("button, a.btn");
    if (!b) return;
    var acc = b.getAttribute("data-accion");
    if (!acc) return;

    if (acc === "marcar-todo-leido") {
      e.preventDefault();
      confirmar("Marcar todo como leido",
        "Se archivaran todas las notificaciones pendientes.",
        function () {
          var c = $(".count");
          if (c) c.textContent = "0";
          toast("Notificaciones marcadas como leidas", "ok");
        });
      return;
    }
    if (acc === "filtrar-notificacion") {
      var tipo = b.getAttribute("data-tipo");
      $$(".chips .chip").forEach(function (c) {
        c.classList.toggle("activo", c === b);
        c.setAttribute("aria-pressed", c === b ? "true" : "false");
      });
      $$(".aviso").forEach(function (av) {
        var ver = !tipo || tipo === "todos" || av.classList.contains("u-" + tipo);
        av.hidden = !ver;
      });
      return;
    }
    if (acc === "publicar-comentario") {
      var cont = b.closest(".comentario-form") || document;
      var ta = $("textarea", cont);
      var txt = ta && ta.value.trim();
      if (!txt) { toast("Escribe un comentario", "error"); return; }
      var listaC = $(".comentarios");
      if (listaC) {
        var art = document.createElement("article");
        art.className = "comentario";
        var cab = document.createElement("div");
        cab.className = "comentario-cab";
        var aut = document.createElement("span");
        aut.className = "comentario-autor";
        aut.appendChild(document.createTextNode("Carlos Mendoza"));
        var fec = document.createElement("span");
        fec.className = "comentario-fecha";
        fec.appendChild(document.createTextNode("Ahora"));
        cab.appendChild(aut);
        cab.appendChild(fec);
        var tx = document.createElement("div");
        tx.className = "comentario-texto";
        tx.appendChild(document.createTextNode(txt));
        art.appendChild(cab);
        art.appendChild(tx);
        listaC.appendChild(art);
      }
      if (ta) ta.value = "";
      toast("Comentario publicado", "ok");
      return;
    }
    if (acc === "descargar-pdf") {
      toast("PDF del diagnostico generado", "info");
      return;
    }
    if (GUARDAR[acc]) {
      toast(GUARDAR[acc], "ok");
      return;
    }
  }, true);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarModal();
  });
})();
"""


def _js_docente():
    return DOCENTE_JS


def _inyectar(html):
    """Agrega el bundle CSS/JS del rol a un documento ya generado por shell().

    Ojo: `lib_js` incluye las cadenas literales `</head>` y `</body>` dentro de su
    funcion de impresion, asi que el `<script>` debe insertarse en el ULTIMO
    `</body>` del documento (no el primero): si se usa el primero, el script cae en
    medio del bundle de lib_js y el parser HTML cierra el `<script>` antes de tiempo,
    dejando la pagina sin JavaScript."""
    if "</head>" in html:
        html = html.replace(
            "</head>", "<style>" + DOCENTE_CSS + "</style>\n</head>", 1)
    if "</body>" in html:
        html = ("<script>" + _js_docente() + "</script>\n</body>").join(
            html.rsplit("</body>", 1))
    return html


ESTADOS_AS = {
    "Confirmada": "b-azul",
    "Finalizada": "b-linea",
    "Pendiente de confirmar": "b-amarillo",
    "Cancelada por el estudiante": "b-neutra",
}

# Agrupacion pedida para el filtro de la tabla de asesorias: agendadas,
# completadas y por agendar. El estado detallado se conserva en ESTADOS_AS.
GRUPO_AS = {
    "Confirmada": "Agendada",
    "Pendiente de confirmar": "Por agendar",
    "Finalizada": "Completada",
    "Cancelada por el estudiante": "Cancelada",
}
COLOR_GRUPO_AS = {
    "Agendada": "b-azul",
    "Por agendar": "b-amarillo",
    "Completada": "b-linea",
    "Cancelada": "b-neutra",
}

# Campos: (codigo, emprendimiento, estudiante, sector, estado, fecha, modalidad, tema)
ASESORIAS = [
    ("ASES-014", "Sabor y Sabe", "Mariana Lopez", "Alimentos",
     "Confirmada", "12 nov 2024, 10:00", "Modalidad mixta",
     "FASE 2 - Prototipo: empaque"),
    ("ASES-013", "Krea Textil", "Jhon Ospina", "Moda",
     "Confirmada", "14 nov 2024, 15:30", "Virtual",
     "Tarea: Perfil en redes sociales"),
    ("ASES-012", "EcoPack", "Lucia Fernandez", "Ambiental",
     "Pendiente de confirmar", "20 nov 2024, 09:00", "Presencial",
     "FASE 3 - Validación: prueba con usuarios"),
    ("ASES-011", "Sabor y Sabe", "Mariana Lopez", "Alimentos",
     "Finalizada", "05 nov 2024, 10:00", "Presencial",
     "FASE 2 - Prototipo: precios"),
    ("ASES-010", "Krea Textil", "Jhon Ospina", "Moda",
     "Finalizada", "31 oct 2024, 14:00", "Virtual",
     "Tarea: Análisis de competencia"),
    ("ASES-009", "EcoPack", "Lucia Fernandez", "Ambiental",
     "Cancelada por el estudiante", "28 oct 2024, 11:00", "Presencial",
     "FASE 1 - Ideación: problema"),
]

# Avances del emprendimiento: (fecha, fase, descripcion, calificacion, evidencia)
AVANCES = [
    ("12 nov 2024", "FASE 2", "Prototipo de empaque listo para 20 unidades",
     92, "Con evidencia"),
    ("05 nov 2024", "FASE 2", "Definicion de precios y punto de equilibrio",
     88, "Con evidencia"),
    ("28 oct 2024", "FASE 1", "Diagnostico inicial y problema claro",
     81, "Sin evidencia"),
]

# Tareas del docente: (titulo, emprendimiento, estudiante, prioridad, vence, estado)
TAREAS_DOC = [
    ("Evidencia fotografica del punto de venta", "Sabor y Sabe", "Mariana Lopez",
     "Alta", "12 nov 2024", "En revision"),
    ("Presupuesto de insumos", "Sabor y Sabe", "Mariana Lopez",
     "Media", "15 nov 2024", "Completada"),
    ("Perfil en redes sociales", "Krea Textil", "Jhon Ospina",
     "Baja", "16 nov 2024", "Pendiente"),
    ("Prototipo de empaque", "EcoPack", "Lucia Fernandez",
     "Alta", "14 nov 2024", "En revision"),
    ("Analisis de competencia", "Aromas del Sur", "Sofia Ramirez",
     "Media", "18 nov 2024", "Pendiente"),
]

PRIO_AS = {"Alta": "b-amarillo", "Media": "b-azul", "Baja": "b-linea"}
ESTADO_TAREA = {"En revision": "b-amarillo", "Completada": "b-azul",
                "Pendiente": "b-neutra", "Devuelta": "b-neutra"}

# Diagnostico generado: (origen, emprendimiento, estudiante, tema, estado, fecha)
DIAGNOSTICOS = [
    ("FASE 1 completada", "Sabor y Sabe", "Mariana Lopez",
     "Problema y perfil", "Completado", "28 oct 2024"),
    ("FASE 2 en curso", "Sabor y Sabe", "Mariana Lopez",
     "Prototipo y precios", "En curso", "12 nov 2024"),
    ("Tareas clave", "Krea Textil", "Jhon Ospina",
     "Validación con usuarios", "Pendiente", "Pendiente"),
]

DIAG_FASES = [
    ("FASE 1 - Ideación", 100, AZUL),
    ("FASE 2 - Prototipo", 62, AZUL),
    ("FASE 3 - Validación", 24, AMAR),
    ("FASE 4 - Formalización", 0, "#bbbbbb"),
]

# Grupo de cada emprendimiento: un emprendimiento puede tener varios estudiantes
# y un estudiante puede tener varios emprendimientos (relación N:N).
# Campos: (estudiante, codigo, sede)
ESTUDIANTES_EMP = {
    "Sabor y Sabe": [("Mariana Lopez", "EST-087", "Sede Norte"),
                     ("Diego Torres", "EST-090", "Sede Norte")],
    "Krea Textil": [("Jhon Ospina", "EST-086", "Sede Centro"),
                    ("Mariana Lopez", "EST-087", "Sede Norte")],
    "EcoPack": [("Lucia Fernandez", "EST-085", "Sede Norte"),
                ("Diego Torres", "EST-090", "Sede Norte")],
    "Aromas del Sur": [("Sofia Ramirez", "EST-084", "Sede Sur"),
                       ("Camilo Rojas", "EST-091", "Sede Sur")],
    "Muebles Origen": [("Andres Felipe", "EST-083", "Sede Centro")],
}

# Cartera del docente. Campos: (emprendimiento, sector, etapa, avance,
# asesoria_activa, ultima_actividad, con_evidencia)
ASIGNADOS = [
    ("Sabor y Sabe", "Alimentos", "FASE 2 - Prototipo", 62,
     "ASES-014 confirmada", "12 nov 2024", True),
    ("Krea Textil", "Moda", "FASE 1 - Ideación", 28,
     "ASES-013 confirmada", "14 nov 2024", False),
    ("EcoPack", "Ambiental", "FASE 3 - Validación", 84,
     "Sin asesoría activa", "09 nov 2024", True),
    ("Aromas del Sur", "Alimentos", "FASE 1 - Ideación", 15,
     "Sin asesoría activa", "06 nov 2024", False),
    ("Muebles Origen", "Muebles", "FASE 2 - Prototipo", 55,
     "ASES-008 confirmada", "04 nov 2024", True),
]

FASES = [
    "FASE 1 - Ideación",
    "FASE 2 - Prototipo",
    "FASE 3 - Validación",
    "FASE 4 - Formalización",
]

REVISION = {
    "Sabor y Sabe": ("En revision", "b-amarillo"),
    "Krea Textil": ("Pendiente", "b-linea"),
    "EcoPack": ("Calificada", "b-azul"),
    "Aromas del Sur": ("Pendiente", "b-linea"),
    "Muebles Origen": ("Devuelta", "b-neutra"),
}

INFO_EMP = {a[0]: a for a in ASIGNADOS}


def estudiantes_de(emp):
    """Nombres del grupo anexado a un emprendimiento."""
    return [e[0] for e in ESTUDIANTES_EMP.get(emp, [])]


def roster_de(emp):
    """Estudiantes del grupo con su codigo y sede."""
    return ESTUDIANTES_EMP.get(emp, [])


def emprendimientos_de(estudiante):
    """Emprendimientos asignados a un estudiante (relación N:N)."""
    return [emp for emp in EMPRESAS if estudiante in estudiantes_de(emp)]


def _estudiantes_unicos():
    vistos = []
    for grupo in ESTUDIANTES_EMP.values():
        for e in grupo:
            if e[0] not in vistos:
                vistos.append(e[0])
    return vistos


TODOS_ESTUDIANTES = _estudiantes_unicos()
EMPRESAS = [a[0] for a in ASIGNADOS]


# --- Helpers de marcado ------------------------------------------------------
_ACENTOS_SLUG = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")


def _slug(texto):
    """Slug igual al de lib_js, para casar el selector con las secciones."""
    s = texto.lower().translate(_ACENTOS_SLUG)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _b(icono, etiqueta):
    """Boton generico de tabla (data-accion por intencion del icono)."""
    return boton_accion(icono, etiqueta)


def _ba(accion, icono, etiqueta):
    """Boton de accion con data-accion explicito e icono."""
    return ('<button class="table-act" data-accion="%s" title="%s" aria-label="%s">%s</button>'
            % (accion, etiqueta, etiqueta, ico(icono, 16)))


def _bt(accion, icono, texto, clase="btn btn-primario"):
    """Boton con texto y data-accion explicito."""
    return ('<button data-accion="%s" class="%s">%s %s</button>'
            % (accion, clase, ico(icono, 16), texto))


def _lnk(href, icono, texto, clase="btn btn-primario"):
    """Enlace con aspecto de boton (navega a una vista completa)."""
    return ('<a class="%s" href="%s">%s %s</a>'
            % (clase, href, ico(icono, 16), texto))


def _a(icono, etiqueta, href):
    """Accion de tabla como enlace real (para navegar, no modal)."""
    return ('<a class="table-act" href="%s" title="%s" aria-label="%s">%s</a>'
            % (href, etiqueta, etiqueta, ico(icono, 16)))


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _sep():
    return '<div class="sep"></div>'


def _sep_lg():
    return '<div class="sep-lg"></div>'


def _zona(contenido):
    return '<div data-tabla-zona>%s</div>' % contenido


def _contador(n=0):
    return ('<span class="resultados-contador" data-resultados aria-live="polite">'
            '%d resultados</span>' % n)


def _filtro(aria, opciones, col):
    opts = '<option value="">%s</option>' % opciones[0]
    for o in opciones[1:]:
        opts += "<option>%s</option>" % o
    return ('<select class="filtro" data-filtro="1" data-filtro-col="%d" '
            'aria-label="%s">%s</select>' % (col, aria, opts))


def _tabs(items):
    btns = []
    for i, (clave, txt) in enumerate(items):
        btns.append('<button class="%s" data-panel="%s">%s</button>'
                    % ("activo" if i == 0 else "", clave, txt))
    return '<div class="tabs">%s</div>' % "".join(btns)


def _panel(clave, contenido, activo=False):
    return '<div data-panel-nombre="%s"%s>%s</div>' % (
        clave, "" if activo else " hidden", contenido)


def _chk(texto, on=True):
    return '<label class="chk"><input type="checkbox"%s> %s</label>' % (
        " checked" if on else "", texto)


def _comentario(autor, fecha, texto):
    return ('<article class="comentario"><div class="comentario-cab">'
            '<span class="comentario-autor">%s</span>'
            '<span class="comentario-fecha">%s</span></div>'
            '<div class="comentario-texto">%s</div></article>'
            % (autor, fecha, texto))


def _barra(pct):
    return ('<div class="barra prog"><span style="width:%d%%"></span></div>'
            '<span class="prog-num">%d%%</span>' % (pct, pct))


def _tabla_con_titulo(titulo, cabeceras, filas):
    return tabla(cabeceras, filas).replace(
        '<table class="tabla">',
        '<table class="tabla"><caption class="visually-hidden">%s</caption>' % titulo, 1)


def _campo_libre(idc, etiqueta, ph=""):
    """Campo con id fijo (no consume el contador global de ids de lib_ui)."""
    return ('<div class="campo"><label for="%s">%s</label>'
            '<textarea id="%s" placeholder="%s"></textarea></div>'
            % (idc, etiqueta, idc, ph))


def _envolver(fn):
    def _render():
        return _inyectar(fn())
    return _render


def registrar(reg):
    paginas_doc = [
        ("dashboard.html", "21 Docente - Inicio (dashboard)", dashboard),
        ("asesorias.html", "22 Docente - Mis asesorías", asesorias),
        ("asesoria-detalle.html", "23 Docente - Detalle de asesoría", asesoria_detalle),
        ("asesoria-form.html", "24 Docente - Registrar asesoría", asesoria_form),
        ("emprendimientos.html", "25 Docente - Emprendimientos asignados", emprendimientos),
        ("emprendimiento-expediente.html", "26 Docente - Expediente del emprendimiento",
         emprendimiento_expediente),
        ("avance-detalle.html", "27 Docente - Detalle del avance", avance_detalle),
        ("avance-form.html", "28 Docente - Registrar avance", avance_form),
        ("diagnostico.html", "29 Docente - Diagnóstico", diagnostico),
        ("diagnostico-revision.html", "30 Docente - Revisión del diagnóstico",
         diagnostico_revision),
        ("tareas.html", "31 Docente - Tareas asignadas", tareas),
        ("tarea-detalle.html", "32 Docente - Detalle de tarea", tarea_detalle),
        ("tarea-devolver.html", "33 Docente - Devolver tarea", tarea_devolver),
        ("tarea-form.html", "34 Docente - Asignar tarea", tarea_form),
        ("perfil.html", "35 Docente - Mi perfil", perfil),
        ("contrasena.html", "36 Docente - Cambiar contraseña", contrasena),
        ("notificaciones.html", "37 Docente - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_doc):
        reg("docente", arch, tit, _envolver(fn), i)


# --- 21. Dashboard -----------------------------------------------------------
def dashboard():
    cuerpo = metricas([
        ("maleta", "Emprendimientos asignados", "8", "", 62, "+2 este mes"),
        ("chat", "Asesorías del mes", "14", "", 78, "+4"),
        ("checklist", "Tareas por revisar", "9", "", 45, None),
        ("trend", "Avances registrados", "23", "", 88, "+7"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Avance por emprendimiento", barras_h(
        "", "", [a[0] for a in ASIGNADOS], [a[3] for a in ASIGNADOS],
        maximo=100, unidad="%"))
    cuerpo += card("Actividad reciente", _tabla_con_titulo(
        "Actividad reciente del docente",
        ["Fecha", "Emprendimiento", "Accion registrada", "@ACC"],
        [["12 nov 2024", "Sabor y Sabe", "Registraste un avance de fase",
          _acc(_a("eye", "Ver avance", "avance-detalle.html"))],
         ["11 nov 2024", "Krea Textil", "Calificaste una tarea con 92 de 100",
          _acc(_a("eye", "Ver tarea", "tarea-detalle.html"))],
         ["11 nov 2024", "EcoPack", "Confirmaste la asesoría del 20 de noviembre",
          _acc(_a("eye", "Ver asesoría", "asesoria-detalle.html"))],
         ["08 nov 2024", "Sabor y Sabe", "Asignaste la tarea de evidencia fotografica",
          _acc(_a("eye", "Ver tarea", "tarea-detalle.html"))]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones rapidas", '<div class="acciones-rapidas">'
                   + _lnk("avance-form.html", "edit", "Registrar avance")
                   + _lnk("tareas.html", "check", "Calificar", "btn btn-secundario")
                   + _lnk("diagnostico-revision.html", "clipboard", "Revisar diagnostico",
                          "btn btn-secundario")
                   + _lnk("asesoria-form.html", "chat", "Generar asesoria",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += card("Proximas asesorias", agenda([
        ("Hoy", [("10:00", "Sabor y Sabe", "Mariana Lopez · Modalidad mixta",
                  badge("Confirmada", "b-azul"))]),
        ("20 nov", [("09:00", "EcoPack", "Lucia Fernandez · Presencial",
                     badge("Por confirmar", "b-amarillo"))]),
        ("22 nov", [("15:30", "Krea Textil", "Jhon Ospina · Virtual",
                     badge("Confirmada", "b-azul"))]),
    ]))
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
                 acciones=_lnk("asesoria-form.html", "plus", "Generar asesoria"))


# --- 22. Mis asesorias -------------------------------------------------------
def asesorias():
    filas = []
    for cod, emp, estu, sector, estado, fecha, mod, tema in ASESORIAS:
        filas.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % emp, estu, tema,
            badge(GRUPO_AS[estado], COLOR_GRUPO_AS[GRUPO_AS[estado]]),
            fecha, mod,
            _acc(_a("eye", "Ver detalle", "asesoria-detalle.html")),
        ])
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Por agendar", "Agendada",
                        "Completada", "Cancelada"], 4)
               + _filtro("Filtrar por estudiante",
                         ["Todos los estudiantes"] + TODOS_ESTUDIANTES, 2)
               + _filtro("Filtrar por emprendimiento",
                         ["Todos los emprendimientos"] + EMPRESAS, 1)
               + _contador(len(filas)))
    cuerpo = callout(
        "Como docente tú confirmas la <b>fecha y la hora</b> que el estudiante solicitó. "
        "El estudiante no puede agendar por su cuenta.", "bombilla")
    cuerpo += _sep()
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo(
                        "Asesorías agendadas, completadas y por agendar",
                        ["Código", "Emprendimiento", "Estudiante", "Tema",
                         "Estado", "Fecha y hora", "Modalidad", "@ACC"], filas)
                    + paginas(1, 6, 24))
    return shell(R, "asesorias", "Mis asesorías", cuerpo,
                 migas=["Inicio", "Mis asesorías"],
                 sub="Todas tus asesorías: por agendar, agendadas y completadas.",
                 acciones=_lnk("asesoria-form.html", "plus", "Registrar asesoría"))


# --- 23. Detalle de asesoria -------------------------------------------------
def asesoria_detalle():
    cuerpo = steps(["Solicitud recibida", "Confirmar fecha", "Registrar sesion",
                    "Cerrar asesoria"], 1)
    cuerpo += _sep_lg()
    cuerpo += metricas([
        ("chat", "Modalidad", "Mixta", "", 60, "Sala 3 / enlace"),
        ("reloj", "Duracion", "60", "min", 60, "10:00 a 11:00"),
        ("users", "Agendada a", "2", "estudiantes", 100, "Todo el grupo"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Solicitud del estudiante", lista_def([
        ("Estudiante que solicita", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Tema por defecto", "FASE 2 - Prototipo: empaque"),
        ("Necesidades descritas", "Revisar el costo unitario del empaque y el "
         "punto de equilibrio."),
        ("Fecha pedida", "20 de noviembre de 2024"),
    ]))
    cuerpo += card("Agenda de la asesoría",
                   campo("Fecha", tipo="date", valor="2024-11-20", req=True)
                   + select("Hora disponible",
                            ["08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00",
                             "14:00 - 15:00", "15:00 - 16:00"], req=True,
                            valor="10:00 - 11:00")
                   + select("Modalidad", ["Presencial", "Virtual", "Modalidad mixta"],
                            req=True, valor="Modalidad mixta")
                   + campo("Lugar o enlace",
                           valor="Sala 3 del bloque B / meet.sgemd.edu.co/ases-014")
                   + '<div class="nota-foot">Los 2 estudiantes del grupo quedan '
                     "agendados en la misma asesoría.</div>")
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + _bt("confirmar-asesoria", "check", "Confirmar y notificar")
                   + _bt("reprogramar-asesoria", "calendar", "Proponer otra fecha",
                         "btn btn-secundario")
                   + _bt("rechazar-asesoria", "x", "Rechazar solicitud",
                         "btn btn-secundario")
                   + _lnk("asesorias.html", "izq", "Volver a asesorías",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += card("Estudiantes agendados", lista_def(
        [(n, "%s · %s" % (cod, sede))
         for n, cod, sede in roster_de("Sabor y Sabe")]))
    cuerpo += "</div></div>"
    return shell(R, "asesorias", "Detalle de asesoría", cuerpo,
                 migas=["Inicio", "Mis asesorías", "Detalle de asesoría"],
                 sub="Confirma, reprograma o rechaza la solicitud del estudiante.",
                 acciones=_lnk("asesorias.html", "izq", "Volver", "btn btn-secundario"))


# --- 24. Registrar asesoria --------------------------------------------------
def asesoria_form():
    cuerpo = callout(
        "Elige el emprendimiento: si es un grupo, la asesoría se agenda para "
        "<b>todos sus estudiantes</b>. El tema por defecto puede ser una fase con "
        "su tarea o una tarea asignada.", "bombilla")
    cuerpo += _sep()
    cuerpo += steps(["Datos", "Fecha y hora", "Necesidades", "Confirmar"], 0)
    cuerpo += _sep_lg()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la asesoría",
                   select("Emprendimiento", EMPRESAS, req=True, valor="Sabor y Sabe")
                   + '<div class="nota-foot">Se agendará a los 2 estudiantes del '
                     "grupo de Sabor y Sabe.</div>"
                   + select("Tema por defecto",
                            ["FASE 2 - Prototipo: empaque",
                             "FASE 2 - Prototipo: precios",
                             "FASE 3 - Validación: usuarios",
                             "Tarea: Evidencia fotografica",
                             "Tarea: Perfil en redes sociales",
                             "Otra (la define el docente)"], req=True,
                            valor="FASE 2 - Prototipo: empaque")
                   + select("Modalidad", ["Presencial", "Virtual", "Modalidad mixta"],
                            req=True, valor="Modalidad mixta")
                   + campo("Lugar o enlace",
                           valor="Sala 3 del bloque B / meet.sgemd.edu.co/ases-014"))
    cuerpo += card("Necesidades de la asesoría", campo(
        "Descripción de las necesidades", alto=True,
        valor="Revisar el costo unitario del empaque, el punto de equilibrio y el "
              "canal de venta en el campus.",
        ph="Qué necesita resolver el estudiante en la asesoría"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Fecha y hora disponible",
                   campo("Fecha", tipo="date", valor="2024-11-20", req=True)
                   + select("Hora disponible",
                            ["08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00",
                             "14:00 - 15:00", "15:00 - 16:00"], req=True,
                            valor="10:00 - 11:00"))
    cuerpo += card("Estudiantes que se agendan", lista_def(
        [(n, "%s · %s" % (cod, sede))
         for n, cod, sede in roster_de("Sabor y Sabe")]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + _bt("generar-asesoria", "check", "Generar asesoría")
                   + _lnk("asesorias.html", "izq", "Cancelar", "btn btn-secundario")
                   + "</div>"
                   + '<div class="nota-foot">Al generar, los estudiantes reciben '
                     "la notificación con la fecha, la hora y el lugar.</div>")
    cuerpo += "</div></div>"
    return shell(R, "asesorias", "Registrar asesoría", cuerpo,
                 migas=["Inicio", "Mis asesorías", "Registrar asesoría"],
                 sub="Agenda una asesoría para un emprendimiento y su grupo.",
                 acciones=_lnk("asesorias.html", "izq", "Volver", "btn btn-secundario"))


# --- 25. Emprendimientos asignados -------------------------------------------
def _emp_resumen(emp):
    """Panel de un emprendimiento dentro de las pestanas por estudiante."""
    a = INFO_EMP[emp]
    sector, etapa, avance, act, evid = a[1], a[2], a[3], a[5], a[6]
    rev, col = REVISION[emp]
    izq = card("Datos del emprendimiento", lista_def([
        ("Sector", sector),
        ("Etapa", badge(etapa, "b-azul")),
        ("Avance", _barra(avance)),
        ("Estado de revision", badge(rev, col)),
        ("Evidencia", badge("Con evidencia" if evid else "Sin evidencia",
                            "b-azul" if evid else "b-amarillo")),
        ("Ultima actividad", act),
    ])) + card("Estudiantes del grupo", lista_def(
        [(n, "%s · %s" % (cod, sede)) for n, cod, sede in roster_de(emp)]))
    der = card("Acciones", '<div class="acciones-col">'
               + _lnk("emprendimiento-expediente.html", "eye", "Abrir expediente")
               + _lnk("asesorias.html", "chat", "Ver asesorías", "btn btn-secundario")
               + _lnk("diagnostico.html", "clipboard", "Diagnóstico",
                      "btn btn-secundario")
               + _lnk("tareas.html", "checklist", "Tareas", "btn btn-secundario")
               + "</div>")
    return ('<div class="grid g-2-1"><div class="grid">%s</div>'
            '<div class="grid">%s</div></div>' % (izq, der))


def _secciones_estudiantes():
    """Una sección por estudiante con sus emprendimientos como pestañas."""
    out = []
    for est in TODOS_ESTUDIANTES:
        emps = emprendimientos_de(est)
        if not emps:
            continue
        tabs = _tabs([(_slug(e), e) for e in emps])
        paneles = "".join(
            _panel(_slug(e), _emp_resumen(e), activo=(i == 0))
            for i, e in enumerate(emps))
        out.append('<section data-est-perfil="%s" hidden>%s%s</section>'
                   % (_slug(est), tabs, paneles))
    return "".join(out)


def emprendimientos():
    """Tarjetas con avance + tabla de proyectos; el docente elige sobre cuales trabaja."""
    cuerpo = callout(
        "Solo aparecen los emprendimientos que tienes asignados. Al elegir un "
        "<b>estudiante</b>, sus emprendimientos se muestran como pestañas.", "bombilla")
    cuerpo += _sep()
    cuerpo += metricas([
        ("maleta", "Asignados", "%d" % len(ASIGNADOS), "", 62, None),
        ("upload", "Con evidencia", "3", "", 60, None),
        ("alerta", "Requieren atención", "2", "", 25, None),
    ])
    cuerpo += _sep()

    opts = '<option value="">Todos los estudiantes</option>'
    for est in TODOS_ESTUDIANTES:
        if emprendimientos_de(est):
            opts += '<option value="%s">%s</option>' % (est, est)
    cuerpo += ('<div class="campo"><label for="sel-estudiante">Ver emprendimientos '
               'por estudiante</label>'
               '<select class="filtro" id="sel-estudiante" '
               'aria-label="Ver emprendimientos por estudiante">%s</select>'
               '<div class="ayuda">Al elegir un estudiante se muestran sus '
               "emprendimientos como pestañas.</div></div>" % opts)
    cuerpo += _sep()

    tarjetas = '<div class="emp-grid">'
    for emp, sector, etapa, avance, asesoria, act, _evid in ASIGNADOS:
        pie = ('<a class="btn btn-sm btn-secundario" href="emprendimiento-expediente.html">'
               "Abrir expediente</a>")
        grupo = estudiantes_de(emp)
        meta = ("1 estudiante" if len(grupo) == 1
                else "%d estudiantes" % len(grupo)) + " · " + sector
        tarjetas += tarjeta_emp("maleta", emp, meta, avance,
                                etapa, "%d%%" % avance, pie)
    tarjetas += "</div>"
    tarjetas += ('<p class="nota-foot">Ultima actividad registrada en el expediente '
                 "de cada estudiante.</p>")

    filas = []
    for emp, sector, etapa, avance, ases, act, evid in ASIGNADOS:
        rev, col = REVISION[emp]
        filas.append([
            "<b>%s</b>" % emp,
            ", ".join(estudiantes_de(emp)),
            sector, etapa, _barra(avance), badge(rev, col),
            badge("Con evidencia" if evid else "Sin evidencia",
                  "b-azul" if evid else "b-amarillo"),
            act,
            '<a class="btn btn-sm btn-secundario" '
            'href="emprendimiento-expediente.html">Abrir</a>',
        ])
    filtros = (_filtro("Filtrar por etapa",
                       ["Todas las etapas", "FASE 1 - Ideación", "FASE 2 - Prototipo",
                        "FASE 3 - Validación"], 3)
               + _filtro("Filtrar por sector",
                         ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                          "Muebles"], 2)
               + _filtro("Filtrar por evidencia",
                         ["Toda la evidencia", "Con evidencia", "Sin evidencia"], 6)
               + _contador(len(filas)))
    tabla_proy = _zona(toolbar(filtros=filtros) + _tabla_con_titulo(
        "Proyectos asignados al docente",
        ["Emprendimiento", "Estudiante", "Sector", "Etapa", "Avance",
         "Estado de revision", "Evidencia", "Ultima actividad", "@ACC"], filas))

    cuerpo += ('<div id="lista-emprendimientos">'
               + _tabs([("tarjetas", "Tarjetas"), ("tabla", "Tabla")])
               + _panel("tarjetas", tarjetas, activo=True)
               + _panel("tabla", tabla_proy)
               + "</div>")
    cuerpo += ('<div id="detalle-estudiante" hidden>'
               + _secciones_estudiantes() + "</div>")
    return shell(R, "emprendimientos", "Emprendimientos asignados", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados"],
                 sub="Tus emprendimientos asignados y los de cada estudiante.")


# --- 26. Expediente ----------------------------------------------------------
def emprendimiento_expediente():
    """Expediente académico del docente: lo que califica y su evidencia."""
    cuerpo = metricas([
        ("trend", "Avance de fase", "62", "%", 62, "FASE 2 - Prototipo"),
        ("medalla", "Promedio de calificación", "87", "/ 100", 87,
         "3 avances calificados"),
        ("clipboard", "Tareas con evidencia", "9", "/ 11", 82, "2 sin adjuntar"),
        ("checklist", "Calificaciones por hacer", "2", "", 20, "Vence el 12 nov"),
    ])
    cuerpo += _sep()

    avances = _tabla_con_titulo(
        "Avances y calificaciones del emprendimiento",
        ["Fecha", "Fase", "Descripcion del avance", "Calificacion", "@ACC"],
        [["12 nov 2024", "FASE 2", "Prototipo de empaque listo para 20 unidades",
          badge("92 de 100", "b-azul"), _acc(_a("eye", "Ver avance", "avance-detalle.html"))],
         ["05 nov 2024", "FASE 2", "Definicion de precios y punto de equilibrio",
          badge("88 de 100", "b-azul"), _acc(_a("eye", "Ver avance", "avance-detalle.html"))],
         ["28 oct 2024", "FASE 1", "Diagnostico inicial y problema claro",
          badge("81 de 100", "b-azul"), _acc(_a("eye", "Ver avance", "avance-detalle.html"))]])

    tareas = kanban([
        ("Por calificar", [
            ("Evidencia fotografica del punto de venta",
             "Sabor y Sabe · Vence 12 nov 2024",
             badge("Alta", "b-amarillo"),
             _lnk("tarea-detalle.html", "check", "Calificar", "btn btn-sm btn-primario")),
        ]),
        ("Devueltas al estudiante", [
            ("Presupuesto de insumos", "Sabor y Sabe · Faltan soportes",
             badge("Media", "b-linea"),
             _lnk("tarea-detalle.html", "eye", "Ver", "btn btn-sm btn-secundario")),
        ]),
        ("Calificadas", [
            ("Perfil en redes sociales", "Calificada el 09 nov 2024",
             badge("Completada", "b-azul"),
             _lnk("tarea-detalle.html", "eye", "Ver", "btn btn-sm btn-secundario")),
        ]),
    ])

    filas_as = []
    for cod, emp, estu, sector, estado, fecha, mod, tema in ASESORIAS:
        if emp == "Sabor y Sabe":
            filas_as.append([cod, fecha, mod, badge(estado, ESTADOS_AS[estado]),
                             _acc(_a("eye", "Ver asesoría", "asesorias.html"))])
    asesorias_panel = tabla(["Codigo", "Fecha y hora", "Modalidad", "Estado", "@ACC"],
                            filas_as)
    asesorias_panel += ('<div class="form-acciones">'
                        + _lnk("asesorias.html", "chat", "Ver todas las asesorías",
                               "btn btn-secundario") + "</div>")

    diag_panel = lista_def([
        ("Ultima revision", "28 oct 2024, 09:14"),
        ("Puntaje heuristics", "7.8 de 10"),
        ("Recomendaciones enviadas", "Canal de venta y presupuesto de publicidad"),
    ]) + '<div class="form-acciones">' + _lnk(
        "diagnostico-revision.html", "clipboard", "Revisar y recomendar") + "</div>"

    com_panel = ('<div class="comentarios">'
                 + _comentario("Carlos Mendoza", "12 nov 2024",
                               "Buen avance en el prototipo. Falta medir el costo unitario "
                               "de los empaques.")
                 + _comentario("Mariana Lopez", "11 nov 2024",
                               "Adjunte las fotos del punto de venta y la lista de precios.")
                 + "</div>"
                 + '<div class="comentario-form">'
                 + _campo_libre("com-obs", "Observacion",
                                "Escribe una observacion para el estudiante")
                 + _bt("publicar-comentario", "enviar", "Publicar comentario")
                 + "</div>")

    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += _tabs([("avances", "Avances"), ("tareas", "Tareas"),
                     ("asesorias", "Asesorias"), ("diag", "Diagnostico"),
                     ("com", "Comentarios")])
    cuerpo += _panel("avances", avances, activo=True)
    cuerpo += _panel("tareas", tareas)
    cuerpo += _panel("asesorias", asesorias_panel)
    cuerpo += _panel("diag", diag_panel)
    cuerpo += _panel("com", com_panel)
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
    ]))
    cuerpo += card("Estudiantes del grupo", lista_def(
        [(n, "%s · %s" % (cod, sede))
         for n, cod, sede in roster_de("Sabor y Sabe")])
        + '<div class="nota-foot">Este emprendimiento se trabaja en equipo: las '
          "calificaciones y los avances aplican a todos sus integrantes.</div>")
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + _lnk("avance-form.html", "edit", "Registrar avance")
                   + _lnk("asesoria-form.html", "chat", "Generar asesoría",
                          "btn btn-secundario")
                   + _lnk("tareas.html", "checklist", "Revisar tareas",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "emprendimientos", "Sabor y Sabe", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados", "Sabor y Sabe"],
                 sub="Expediente académico del emprendimiento y su grupo de estudiantes.",
                 acciones=_lnk("emprendimientos.html", "izq", "Volver",
                               "btn btn-secundario"))


# --- 27. Detalle del avance --------------------------------------------------
def avance_detalle():
    cuerpo = metricas([
        ("trend", "Fase", "FASE 2", "", 62, "Prototipo"),
        ("medalla", "Calificación", "92", "/ 100", 92, None),
        ("clip", "Evidencia", "3", "archivos", 100, None),
        ("check", "Estado", "En rev.", "", 50, "Por calificar"),
    ])
    cuerpo += _sep()
    cuerpo += callout(
        "El avance aplica a <b>todo el grupo</b> del emprendimiento. Editar el "
        "puntaje recalifica a todos sus estudiantes.", "bombilla")
    cuerpo += _sep()
    izq = card("Descripción del avance", '<p class="texto-ayuda">Se completó el '
               "prototipo de empaque para 20 unidades, con ficha técnica y costos "
               "unitarios. Falta validar el punto de equilibrio.</p>")
    izq += card("Evidencia adjunta", lista_def([
        ("prototipo-empaque.pdf", "Subido el 12 nov 2024"),
        ("costos-unitarios.xlsx", "Subido el 12 nov 2024"),
        ("ficha-tecnica.docx", "Subido el 12 nov 2024"),
    ]))
    der = card("Datos del avance", lista_def([
        ("Emprendimiento", "Sabor y Sabe"),
        ("Estudiante", "Mariana Lopez"),
        ("Fase", "FASE 2 - Prototipo"),
        ("Fecha", "12 nov 2024"),
        ("Estado de revision", badge("En revision", "b-amarillo")),
    ]))
    der += card("Acciones", '<div class="acciones-col">'
                + _lnk("avance-form.html", "edit", "Editar avance")
                + _lnk("tarea-detalle.html", "check", "Ver tarea asociada",
                       "btn btn-secundario")
                + _lnk("emprendimiento-expediente.html", "izq", "Volver al expediente",
                       "btn btn-secundario")
                + "</div>")
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    cuerpo += _sep()
    cuerpo += card("Historial del avance", linea_tiempo([
        ("12", "nov", "Avance registrado", "Puntaje 92 de 100", ""),
        ("13", "nov", "Evidencia revisada", "3 archivos validados", ""),
        ("14", "nov", "Comentario del docente", "Falta el punto de equilibrio", ""),
    ]))
    return shell(R, "emprendimientos", "Detalle del avance", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados", "Sabor y Sabe",
                        "Detalle del avance"],
                 sub="Visualiza el avance registrado y edítalo si hace falta.",
                 acciones=_lnk("emprendimiento-expediente.html", "izq", "Volver",
                               "btn btn-secundario"))


# --- 28. Registrar / editar avance -------------------------------------------
def avance_form():
    cuerpo = callout(
        "Registra el avance de una fase. El puntaje y la evidencia quedan "
        "visibles para todo el grupo del emprendimiento.", "bombilla")
    cuerpo += _sep()
    cuerpo += steps(["Fase alcanzada", "Descripción", "Evidencia", "Calificación"], 0)
    cuerpo += _sep_lg()
    izq = card("Datos del avance",
               select("Emprendimiento", EMPRESAS, req=True, valor="Sabor y Sabe")
               + select("Fase alcanzada", FASES, req=True, valor="FASE 2 - Prototipo")
               + campo("Fecha del avance", tipo="date", valor="2024-11-12", req=True)
               + campo("Puntaje (0 a 100)", tipo="number", valor="92")
               + select("Estado de revision",
                        ["Pendiente", "En revision", "Calificada", "Devuelta"],
                        valor="En revision")
               + select("Evidencia", ["Con evidencia", "Sin evidencia"],
                        valor="Con evidencia"))
    izq += card("Descripción del avance", campo(
        "Descripción", alto=True,
        valor="Prototipo de empaque listo para 20 unidades, con ficha tecnica y "
              "costos unitarios.",
        ph="Qué se avanzó en esta fase"))
    der = card("Aplicar a los estudiantes del grupo", lista_def(
        [(n, "%s · %s" % (cod, sede))
         for n, cod, sede in roster_de("Sabor y Sabe")])
        + '<div class="nota-foot">El avance y su calificación aplican a todos los '
          "integrantes del grupo.</div>")
    der += card("Acciones", '<div class="acciones-col">'
                + _bt("guardar-avance", "check", "Guardar avance")
                + _lnk("emprendimiento-expediente.html", "izq", "Cancelar",
                       "btn btn-secundario")
                + "</div>")
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    return shell(R, "emprendimientos", "Registrar avance", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados", "Sabor y Sabe",
                        "Registrar avance"],
                 sub="Registra o edita el avance de una fase del emprendimiento.",
                 acciones=_lnk("emprendimiento-expediente.html", "izq", "Volver",
                               "btn btn-secundario"))


# --- 29. Diagnostico ---------------------------------------------------------
def diagnostico():
    cuerpo = callout(
        "Elige el emprendimiento y filtra por estudiante o proyecto. El "
        "diagnóstico se calcula por la <b>completación de las 4 fases</b> o por "
        "una serie de <b>tareas clave</b> completadas.", "bombilla")
    cuerpo += _sep()
    cuerpo += metricas([
        ("maleta", "Emprendimientos", "%d" % len(ASIGNADOS), "", 60, None),
        ("trend", "Fases completadas", "1 de 4", "", 25, None),
        ("clipboard", "Diagnósticos", "3", "", 45, None),
        ("checklist", "Tareas clave", "2 de 5", "", 40, None),
    ])
    cuerpo += _sep()
    cuerpo += ('<div class="grid g-2-1">'
               '<div class="grid">'
               + select("Emprendimiento", EMPRESAS, valor="Sabor y Sabe")
               + select("Estudiante", ["Todos los estudiantes"] + TODOS_ESTUDIANTES,
                        valor="Mariana Lopez")
               + select("Proyecto / grupo", ["Todos los proyectos"] + EMPRESAS,
                        valor="Sabor y Sabe")
               + select("Origen del diagnóstico",
                        ["Fases y tareas clave", "Solo por fases (4)",
                         "Solo por tareas clave"], valor="Fases y tareas clave")
               + "</div>"
               '<div class="grid">'
               + card("Datos del emprendimiento", lista_def([
                   ("Emprendimiento", "Sabor y Sabe"),
                   ("Sector", "Alimentos"),
                   ("Etapa", "FASE 2 - Prototipo"),
                   ("Grupo", "Mariana Lopez · Diego Torres"),
               ]))
               + "</div></div>")
    cuerpo += _sep()
    cuerpo += card("Avance por fases", progreso_fases(DIAG_FASES))
    cuerpo += card("Comportamiento entrepreneurial", barras_h(
        "", "", ["Visión", "Creatividad", "Resiliencia", "Liderazgo",
                 "Trabajo en equipo", "Toma de decisiones"],
        [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Completado", "En curso",
                        "Pendiente"], 4)
               + _filtro("Filtrar por emprendimiento",
                         ["Todos los emprendimientos"] + EMPRESAS, 1)
               + _filtro("Filtrar por estudiante",
                         ["Todos los estudiantes"] + TODOS_ESTUDIANTES, 2)
               + _contador(len(DIAGNOSTICOS)))
    filas = [[origen, emp, estu, tema, badge(estado, "b-azul" if estado == "Completado"
              else "b-amarillo" if estado == "En curso" else "b-linea"), fecha,
              _acc(_a("eye", "Revisar", "diagnostico-revision.html"))]
             for origen, emp, estu, tema, estado, fecha in DIAGNOSTICOS]
    cuerpo += _zona(toolbar(buscar=False, filtros=filtros)
                    + _tabla_con_titulo(
                        "Diagnósticos por fase o tareas clave",
                        ["Origen", "Emprendimiento", "Estudiante", "Tema", "Estado",
                         "Fecha", "@ACC"], filas)
                    + paginas(1, 3, 3, tam=10))
    cuerpo += _sep()
    cuerpo += card("Historial de diagnósticos", linea_tiempo([
        ("28", "oct", "Diagnóstico FASE 1", "Puntaje 7.8 de 10", ""),
        ("12", "nov", "Diagnóstico FASE 2 en curso", "62% de la fase", ""),
    ]))
    return shell(R, "diagnostico", "Diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico"],
                 sub="Diagnóstico por fases o por tareas clave de cada emprendimiento.",
                 acciones=_lnk("diagnostico-revision.html", "clipboard",
                               "Revisar y recomendar"))


# --- 30. Revision del diagnostico --------------------------------------------
def diagnostico_revision():
    cuerpo = callout(
        "Revisa el resultado y deja tus <b>recomendaciones</b>. El cuestionario lo "
        "responde el estudiante y la revisión se guarda en el expediente.", "bombilla")
    cuerpo += _sep()
    cuerpo += metricas([
        ("trend", "Puntaje heuristics", "7.8", "/ 10", 78, "28 oct 2024"),
        ("clipboard", "Fases completadas", "1", "de 4", 25, "FASE 1"),
        ("checklist", "Tareas clave", "2", "de 5", 40, "3 pendientes"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la revisión", lista_def([
        ("Estudiante", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Respondido", "28 oct 2024, 09:14"),
        ("Origen", "Fases y tareas clave"),
    ]))
    cuerpo += card("Tus recomendaciones", campo(
        "Recomendaciones", alto=True,
        valor="Definir con más precisión el canal de venta digital y separar el "
              "presupuesto de insumos del de publicidad.",
        ph="Qué debe reforzar el estudiante"))
    cuerpo += '<div class="form-acciones">'
    cuerpo += ('<button class="btn btn-secundario" data-accion="descargar-pdf">%s '
               "Descargar PDF</button>" % ico("download", 16))
    cuerpo += _bt("guardar-recomendaciones", "check", "Guardar recomendaciones")
    cuerpo += "</div></div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Resumen", lista_def([
        ("Comportamiento", "Fuerte en trabajo en equipo"),
        ("A reforzar", "Toma de decisiones"),
        ("Pendientes", "FASES 2 a 4 y 3 tareas clave"),
    ]))
    cuerpo += card("Pendientes de revision", _tabla_con_titulo(
        "Pendientes de revision del diagnostico",
        ["Estudiante", "Emprendimiento", "Fecha", "@ACC"],
        [["Jhon Ospina", "Krea Textil", "30 oct 2024",
          _acc(_a("eye", "Revisar", "diagnostico-revision.html"))],
         ["Sofia Ramirez", "Aromas del Sur", "02 nov 2024",
          _acc(_a("eye", "Revisar", "diagnostico-revision.html"))]]))
    cuerpo += "</div></div>"
    return shell(R, "diagnostico", "Revisión del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico", "Revisión"],
                 sub="Revisa los resultados y deja recomendaciones al estudiante.",
                 acciones=_lnk("diagnostico.html", "izq", "Volver",
                               "btn btn-secundario"))


# --- 31. Tareas asignadas ----------------------------------------------------
def tareas():
    filas = []
    for titulo, emp, estu, prio, vence, estado in TAREAS_DOC:
        acciones = [_a("check", "Ver y calificar", "tarea-detalle.html")]
        if estado != "Completada":
            acciones.append(_a("x", "Devolver tarea", "tarea-devolver.html"))
        filas.append([
            "<b>%s</b>" % titulo, emp, estu,
            badge(prio, PRIO_AS[prio]), vence,
            badge(estado, ESTADO_TAREA[estado]),
            _acc(*acciones),
        ])
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Pendiente", "En revision",
                        "Completada"], 5)
               + _filtro("Filtrar por prioridad",
                         ["Toda la prioridad", "Alta", "Media", "Baja"], 3)
               + _contador(len(filas)))
    cuerpo = callout("La tarea se considera <b>completada</b> cuando el estudiante "
                     "adjunta al menos una evidencia.", "bombilla")
    cuerpo += _sep()
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo("Tareas asignadas por revisar",
                                        ["Tarea", "Emprendimiento", "Estudiante",
                                         "Prioridad", "Vence", "Estado", "@ACC"], filas)
                    + paginas(1, 5, 23))
    return shell(R, "tareas", "Tareas asignadas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Revisa y califica las entregas con evidencia de tus estudiantes.",
                 acciones=_lnk("tarea-form.html", "plus", "Asignar tarea"))


# --- 32. Detalle de tarea ----------------------------------------------------
def tarea_detalle():
    cuerpo = metricas([
        ("checklist", "Prioridad", "Alta", "", 80, "Vence 12 nov 2024"),
        ("clip", "Evidencia", "2", "archivos", 100, "Entregada 16:40"),
        ("medalla", "Calificación", "92", "/ 100", 92, None),
        ("check", "Estado", "En rev.", "", 50, "Por calificar"),
    ])
    cuerpo += _sep()
    cuerpo += callout(
        "Califica la entrega o <b>devuélvela</b> con observaciones y el motivo. "
        "La devolución la recibe el estudiante en su bandeja.", "bombilla")
    cuerpo += _sep()
    izq = card("Descripción de la tarea", '<p class="texto-ayuda">Adjunta una foto '
               "del punto de venta y la lista de precios con el costo unitario de "
               "cada producto.</p>")
    izq += card("Evidencia entregada", lista_def([
        ("punto-de-venta.jpg", "Subida el 12 nov 2024, 16:40"),
        ("lista-precios.xlsx", "Subida el 12 nov 2024, 16:41"),
    ]))
    izq += card("Retroalimentación", campo(
        "Retroalimentación para el estudiante", alto=True,
        valor="Buena evidencia del punto de venta. Ajusta el costo unitario del "
              "empaque.",
        ph="Observaciones para el estudiante"))
    der = card("Datos de la entrega", lista_def([
        ("Tarea", "Evidencia fotografica del punto de venta"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Estudiante", "Mariana Lopez"),
        ("Entregada", "12 nov 2024, 16:40"),
        ("Vence", "12 nov 2024"),
    ]))
    der += card("Calificación", circular(92, "Calificación", "Sobre 100")
                + campo("Puntaje (0 a 100)", tipo="number", valor="92")
                + select("Resultado",
                         ["Aprobada", "En revision", "Devuelta"], valor="Aprobada"))
    der += card("Acciones", '<div class="acciones-col">'
                + _bt("guardar-calificacion", "check", "Guardar calificación")
                + _lnk("tarea-devolver.html", "x", "Devolver tarea",
                       "btn btn-secundario")
                + _lnk("tareas.html", "izq", "Volver a tareas", "btn btn-secundario")
                + "</div>")
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    return shell(R, "tareas", "Detalle de tarea", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Visualiza la entrega, califícala o devuélvela.",
                 acciones=_lnk("tareas.html", "izq", "Volver", "btn btn-secundario"))


# --- 33. Devolver tarea ------------------------------------------------------
def tarea_devolver():
    cuerpo = callout(
        "Devuelve la tarea con el <b>motivo</b> y las observaciones. El estudiante "
        "podrá ajustar la evidencia y volver a entregarla.", "alerta")
    cuerpo += _sep()
    izq = card("Datos de la entrega", lista_def([
        ("Tarea", "Prototipo de empaque"),
        ("Emprendimiento", "EcoPack"),
        ("Estudiante", "Lucia Fernandez"),
        ("Entregada", "14 nov 2024, 11:20"),
        ("Vence", "14 nov 2024"),
    ]))
    izq += card("Evidencia entregada", lista_def([
        ("prototipo-v1.pdf", "Subida el 14 nov 2024, 11:20"),
    ]))
    der = card("Motivo de la devolución", select(
        "Motivo",
        ["Evidencia incompleta",
         "No cumple con lo solicitado",
         "Archivos ilegibles",
         "Entrega fuera de fecha",
         "Otro motivo"], req=True, valor="No cumple con lo solicitado"))
    der += card("Observaciones para el estudiante", campo(
        "Observaciones", alto=True,
        valor="El prototipo no incluye la ficha técnica ni el costo unitario. "
              "Adjúntalos y vuelve a entregar.",
        ph="Describe qué debe corregir el estudiante"))
    der += card("Acciones", '<div class="acciones-col">'
                + _bt("devolver-tarea", "x", "Devolver al estudiante")
                + _lnk("tarea-detalle.html", "izq", "Cancelar", "btn btn-secundario")
                + "</div>")
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    return shell(R, "tareas", "Devolver tarea", cuerpo,
                 migas=["Inicio", "Tareas", "Devolver tarea"],
                 sub="Explica el motivo y las observaciones de la devolución.",
                 acciones=_lnk("tareas.html", "izq", "Volver", "btn btn-secundario"))


# --- 34. Asignar tarea -------------------------------------------------------
def tarea_form():
    cuerpo = callout(
        "Asigna una tarea al emprendimiento; si es un grupo, la reciben todos sus "
        "estudiantes y cada uno entrega su evidencia.", "bombilla")
    cuerpo += _sep()
    cuerpo += steps(["Datos", "Fechas", "Evidencia", "Confirmar"], 0)
    cuerpo += _sep_lg()
    izq = card("Datos de la tarea",
               campo("Título", valor="Evidencia fotografica del punto de venta",
                     req=True, ph="Qué debe entregar el estudiante")
               + select("Emprendimiento", EMPRESAS, req=True, valor="Sabor y Sabe")
               + select("Prioridad", ["Alta", "Media", "Baja"], req=True,
                        valor="Alta")
               + campo("Fecha límite", tipo="date", valor="2024-11-12", req=True))
    izq += card("Instrucciones", campo(
        "Instrucciones", alto=True,
        valor="Adjunta una foto del punto de venta y la lista de precios con el "
              "costo unitario de cada producto.",
        ph="Qué debe entregar el estudiante"))
    der = card("Evidencia requerida", select(
        "Tipo de evidencia",
        ["Archivo o foto", "Enlace", "Texto", "Sin evidencia"], valor="Archivo o foto")
        + _chk("Obligatoria para completar la tarea", True)
        + _chk("Permitir entrega fuera de fecha", False))
    der += card("Estudiantes que la reciben", lista_def(
        [(n, "%s · %s" % (cod, sede))
         for n, cod, sede in roster_de("Sabor y Sabe")])
        + '<div class="nota-foot">La tarea se asigna a todo el grupo del '
          "emprendimiento.</div>")
    der += card("Acciones", '<div class="acciones-col">'
                + _bt("asignar-tarea", "check", "Asignar tarea")
                + _lnk("tareas.html", "izq", "Cancelar", "btn btn-secundario")
                + "</div>")
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    return shell(R, "tareas", "Asignar tarea", cuerpo,
                 migas=["Inicio", "Tareas", "Asignar tarea"],
                 sub="Crea una tarea con evidencia para un emprendimiento.",
                 acciones=_lnk("tareas.html", "izq", "Volver", "btn btn-secundario"))


# --- 35. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos personales", campo("Nombres", valor="Carlos Alejandro")
                   + campo("Apellidos", valor="Mendoza Rios")
                   + campo("Correo institucional", valor="carlos.mendoza@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Teléfono", valor="+57 300 555 0142")
                   + campo("Título / especialidad",
                           valor="Magíster en Innovación y Emprendimiento")
                   + campo("Área de conocimiento", valor="Emprendimientos innovate"))
    cuerpo += card("Ubicación", select(
        "Región / Rectoría",
        ["Rectoría Bogotá", "Rectoría Medellín", "Rectoría Cali"], valor="Rectoría Bogotá")
        + select("Departamento",
                 ["Cundinamarca", "Antioquia", "Valle del Cauca"],
                 valor="Cundinamarca")
        + campo("Ciudad", valor="Bogotá")
        + select("Sede", ["Sede Norte", "Sede Centro", "Sede Sur"], valor="Sede Norte"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Seguridad", lista_def([
        ("Contraseña", "Actualizada hace 3 meses"),
        ("Verificación en dos pasos", "Activada"),
        ("Último acceso", "Hoy, 07:42"),
    ]))
    cuerpo += card("Preferencias de notificacion",
                   _chk("Avisos de nuevas asesorias", True)
                   + _chk("Recordatorios de tareas por revisar", True)
                   + _chk("Resumen semanal por correo", False))
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + '<button class="btn btn-primario">%s Guardar cambios</button>'
                     % ico("check", 16)
                   + _lnk("contrasena.html", "lock", "Cambiar contraseña",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Actualiza tus datos de contacto y revisa tu actividad.")


# --- 36. Cambiar contrasena --------------------------------------------------
def contrasena():
    cuerpo = callout(
        "Por seguridad, la contraseña nueva debe tener al menos <b>8 caracteres</b>, "
        "una mayúscula y un número.", "lock")
    cuerpo += _sep()
    izq = card("Cambiar contraseña",
               campo("Contraseña actual", tipo="password", req=True)
               + campo("Contraseña nueva", tipo="password", req=True,
                       ayuda="Mínimo 8 caracteres, una mayúscula y un número.")
               + campo("Repetir contraseña nueva", tipo="password", req=True)
               + '<div class="form-acciones">'
               + _bt("actualizar-contrasena", "lock", "Actualizar contraseña")
               + "</div>")
    der = card("Recomendaciones", '<div class="texto-ayuda">No reutilices la '
               "contraseña de otros servicios. Si detectas un acceso que no "
               "reconoces, actualízala y avisa a soporte.</div>")
    der += card("Acciones", _lnk("perfil.html", "izq", "Volver a mi perfil",
                                 "btn btn-secundario"))
    cuerpo += '<div class="grid g-2-1"><div class="grid">%s</div><div class="grid">%s</div></div>' % (
        izq, der)
    return shell(R, "perfil", "Cambiar contraseña", cuerpo,
                 migas=["Inicio", "Mi perfil", "Cambiar contraseña"],
                 sub="Actualiza la contraseña de tu cuenta institucional.",
                 acciones=_lnk("perfil.html", "izq", "Volver", "btn btn-secundario"))


# --- 37. Notificaciones ------------------------------------------------------
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
             "asesoria-detalle.html", "media",
             '<a class="btn btn-sm btn-primario" href="asesoria-detalle.html">Confirmar</a>'
             + _b("check", "Marcar como leída")),
            ("upload", "Evidencia enviada: Sabor y Sabe",
             "Emprendimientos · Prototipo · Entregada 16:40",
             "tarea-detalle.html", "media",
             '<a class="btn btn-sm btn-primario" href="tarea-detalle.html">Calificar</a>'
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
    cuerpo += _sep()
    cuerpo += ('<div class="chips" role="group">'
               '<button class="chip activo" aria-pressed="true" '
               'data-accion="filtrar-notificacion" data-tipo="todos">Todas</button>'
               '<button class="chip" aria-pressed="false" '
               'data-accion="filtrar-notificacion" data-tipo="alta">Urgentes</button>'
               '<button class="chip" aria-pressed="false" '
               'data-accion="filtrar-notificacion" data-tipo="media">De hoy</button>'
               '<button class="chip" aria-pressed="false" '
               'data-accion="filtrar-notificacion" data-tipo="baja">Recientes</button>'
               "</div>")
    cuerpo += lista_avisos(grupos)
    cuerpo += ('<p class="nota-foot">Las notificaciones se archivan solas '
               "30 dias despues de resolverse.</p>")
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Lo que debes revisar, ordenado por urgencia.",
                 acciones=_bt("marcar-todo-leido", "check", "Marcar todo como leido",
                              "btn btn-secundario"))
