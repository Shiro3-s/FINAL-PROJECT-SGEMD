# -*- coding: utf-8 -*-
"""Rol DOCENTE - 12 pantallas.

Reglas del rol:
  - Solo ve los emprendimientos que tiene asignados.
  - Registra y califica avances; el estudiante solo consulta su historial.
  - Confirma fecha y hora de la asesoria que el estudiante solicito (BR-002).
  - Revisa el diagnostico y deja recomendaciones; el estudiante lo responde.

Refactor UX/UI (ver cambios-a-docente.md): cada pagina inyecta un bundle CSS/JS
propio del rol via _inyectar(). El script captura en fase de captura y atiende
solo sus data-accion nuevos; el resto lo sigue manejando lib_js.
"""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, lista_avisos,
    tarjeta_emp, kanban, agenda,
)
from lib_charts import barras, barras_h, donut, stacked_tareas, AZUL, AMAR

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
    "@media (max-width:479px){.acciones-rapidas{grid-template-columns:minmax(0,1fr)}}"
)

DOCENTE_JS = """
(function () {
  "use strict";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  var ACCIONES = {
    "calificar": 1, "asignar-tarea": 1, "confirmar-asesoria": 1,
    "reprogramar-asesoria": 1, "rechazar-asesoria": 1, "publicar-comentario": 1,
    "devolver-tarea": 1, "registrar-avance": 1, "revisar-diagnostico": 1,
    "guardar-recomendaciones": 1,
    "confirmar-avance": 1, "cambiar-contrasena": 1, "marcar-todo-leido": 1,
    "filtrar-notificacion": 1
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

  function abrirModal(titulo, cuerpoHTML, botones) {
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
    var equis = document.createElement("button");
    equis.className = "icon-btn modal-x";
    equis.setAttribute("aria-label", "Cerrar");
    equis.appendChild(document.createTextNode("X"));
    head.appendChild(h2);
    head.appendChild(equis);
    var cuerpo = document.createElement("div");
    cuerpo.className = "modal-cuerpo";
    cuerpo.innerHTML = cuerpoHTML;
    var pie = document.createElement("div");
    pie.className = "modal-foot";
    (botones || []).forEach(function (b) {
      var el = document.createElement("button");
      el.className = b.clase || "btn btn-secundario";
      el.appendChild(document.createTextNode(b.txt));
      el.addEventListener("click", function () {
        if (b.al) b.al(caja);
        if (b.cerrar !== false) cerrarModal();
      });
      pie.appendChild(el);
    });
    caja.appendChild(head);
    caja.appendChild(cuerpo);
    caja.appendChild(pie);
    velo.appendChild(caja);
    document.body.appendChild(velo);
    document.body.classList.add("sin-scroll");
    equis.addEventListener("click", cerrarModal);
    velo.addEventListener("click", function (e) { if (e.target === velo) cerrarModal(); });
    var foco = $("input, select, textarea, .modal-foot button", caja);
    if (foco) foco.focus();
    return caja;
  }

  function confirmar(titulo, texto, al) {
    abrirModal(titulo, '<p class="confirm-texto"></p>', [
      { txt: "Cancelar", clase: "btn btn-secundario" },
      { txt: "Confirmar", clase: "btn btn-peligro", al: al }
    ]);
    $(".confirm-texto").textContent = texto;
  }

  function campo(id, etq, tipo) {
    return '<div class="campo"><label for="' + id + '">' + etq + '</label>' +
      '<input id="' + id + '" type="' + (tipo || "text") + '"></div>';
  }
  function area(id, etq, ph) {
    return '<div class="campo"><label for="' + id + '">' + etq + '</label>' +
      '<textarea id="' + id + '" placeholder="' + ph + '"></textarea></div>';
  }
  function selCampo(id, etq, opciones) {
    var ops = opciones.map(function (o) { return "<option>" + o + "</option>"; }).join("");
    return '<div class="campo"><label for="' + id + '">' + etq + '</label>' +
      '<select id="' + id + '">' + ops + '</select></div>';
  }

  var BODY_CALIFICAR = campo("cal-puntaje", "Puntaje (0 a 100)", "number") +
    selCampo("cal-resultado", "Resultado", ["Aprobada", "En revision", "Devuelta"]) +
    area("cal-retro", "Retroalimentacion", "Observaciones para el estudiante");

  var BODY_ASIGNAR = campo("asig-titulo", "Titulo de la tarea") +
    campo("asig-emp", "Emprendimiento") +
    selCampo("asig-prio", "Prioridad", ["Alta", "Media", "Baja"]) +
    campo("asig-fecha", "Fecha limite", "date") +
    area("asig-instr", "Instrucciones", "Que debe entregar el estudiante");

  var BODY_ASESORIA = campo("as-fecha", "Fecha", "date") +
    campo("as-hora", "Hora", "time") +
    selCampo("as-mod", "Modalidad", ["Presencial", "Virtual", "Modalidad mixta"]) +
    campo("as-lugar", "Lugar o enlace");

  var BODY_DIAG = area("diag-rec", "Recomendaciones", "Que debe reforzar el estudiante");

  var BODY_CLAVE = campo("clave-act", "Contrasena actual", "password") +
    campo("clave-nueva", "Contrasena nueva", "password") +
    campo("clave-rep", "Repetir contrasena nueva", "password");

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
    if (!acc || !ACCIONES[acc]) return;
    e.preventDefault();
    e.stopPropagation();

    if (acc === "registrar-avance") { location.href = "seguimiento-notas.html"; return; }

    if (acc === "calificar") {
      abrirModal("Calificar entrega", BODY_CALIFICAR, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Guardar calificacion", clase: "btn btn-primario", al: function () { toast("Calificacion guardada", "ok"); } }
      ]);
      return;
    }
    if (acc === "asignar-tarea") {
      abrirModal("Asignar tarea", BODY_ASIGNAR, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Asignar tarea", clase: "btn btn-primario", al: function () { toast("Tarea asignada", "ok"); } }
      ]);
      return;
    }
    if (acc === "confirmar-asesoria") {
      abrirModal("Confirmar asesoria", BODY_ASESORIA, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Confirmar y notificar", clase: "btn btn-primario", al: function () { toast("Asesoria confirmada", "ok"); } }
      ]);
      return;
    }
    if (acc === "reprogramar-asesoria") {
      abrirModal("Proponer otra fecha", BODY_ASESORIA, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Enviar propuesta", clase: "btn btn-primario", al: function () { toast("Nueva fecha propuesta", "ok"); } }
      ]);
      return;
    }
    if (acc === "rechazar-asesoria") {
      confirmar("Rechazar solicitud", "Se notificara al estudiante que la solicitud fue rechazada.", function () { toast("Solicitud rechazada", "info"); });
      return;
    }
    if (acc === "revisar-diagnostico") {
      abrirModal("Recomendaciones del diagnostico", BODY_DIAG, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Guardar recomendaciones", clase: "btn btn-primario", al: function () { toast("Recomendaciones guardadas", "ok"); } }
      ]);
      return;
    }
    if (acc === "guardar-recomendaciones") {
      confirmar("Guardar recomendaciones", "Se enviaran al estudiante y se marcaran como revisadas.", function () { toast("Recomendaciones guardadas", "ok"); });
      return;
    }
    if (acc === "cambiar-contrasena") {
      abrirModal("Cambiar contrasena", BODY_CLAVE, [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Actualizar contrasena", clase: "btn btn-primario", al: function () { toast("Contrasena actualizada", "ok"); } }
      ]);
      return;
    }
    if (acc === "devolver-tarea") {
      confirmar("Devolver tarea", "La tarea volvera al estudiante para que ajuste la evidencia.", function () { toast("Tarea devuelta", "info"); });
      return;
    }
    if (acc === "confirmar-avance") {
      confirmar("Registrar avance", "Se guardara el avance y se notificara al estudiante.", function () { toast("Avance registrado", "ok"); });
      return;
    }
    if (acc === "marcar-todo-leido") {
      confirmar("Marcar todo como leido", "Se archivaran todas las notificaciones pendientes.", function () {
        var c = $(".count");
        if (c) c.textContent = "0";
        toast("Notificaciones marcadas como leidas", "ok");
      });
      return;
    }
    if (acc === "publicar-comentario") {
      var cont = b.closest(".comentario-form") || document;
      var ta = $("textarea", cont);
      var txt = ta && ta.value.trim();
      if (!txt) { toast("Escribe un comentario", "error"); return; }
      var lista = $(".comentarios");
      if (lista) {
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
        lista.appendChild(art);
      }
      if (ta) ta.value = "";
      toast("Comentario publicado", "ok");
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
  }, true);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarModal();
  });
})();
"""


def _inyectar(html):
    """Agrega el bundle CSS/JS del rol a un documento ya generado por shell()."""
    if "</head>" in html:
        html = html.replace(
            "</head>", "<style>" + DOCENTE_CSS + "</style>\n</head>", 1)
    if "</body>" in html:
        html = html.replace(
            "</body>", "<script>" + DOCENTE_JS + "</script>\n</body>", 1)
    return html


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

REVISION = {
    "Sabor y Sabe": ("En revision", "b-amarillo"),
    "Krea Textil": ("Pendiente", "b-linea"),
    "EcoPack": ("Calificada", "b-azul"),
    "Aromas del Sur": ("Pendiente", "b-linea"),
    "Muebles Origen": ("Devuelta", "b-neutra"),
}

FASE_POR_EMP = {a[0]: a[3] for a in ASIGNADOS}


# --- Helpers de marcado ------------------------------------------------------
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


def _select_libre(idc, etiqueta, opciones, valor=None):
    """Select con id fijo (no consume el contador global de ids de lib_ui)."""
    opts = "".join('<option%s>%s</option>'
                   % (" selected" if valor and o == valor else "", o)
                   for o in opciones)
    return ('<div class="campo"><label for="%s">%s</label>'
            '<select id="%s">%s</select></div>' % (idc, etiqueta, idc, opts))


def _envolver(fn):
    def _render():
        return _inyectar(fn())
    return _render


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
        "", "", [a[0] for a in ASIGNADOS], [a[4] for a in ASIGNADOS],
        maximo=100, unidad="%"))
    cuerpo += card("Actividad reciente", _tabla_con_titulo(
        "Actividad reciente del docente",
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
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones rapidas", '<div class="acciones-rapidas">'
                   + _bt("registrar-avance", "edit", "Registrar avance")
                   + _bt("calificar", "check", "Calificar", "btn btn-secundario")
                   + _bt("revisar-diagnostico", "clipboard", "Revisar diagnostico",
                         "btn btn-secundario")
                   + '<a class="btn btn-secundario" href="asesoria-form.html">%s '
                     "Registrar asesoria</a>" % ico("chat", 16)
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
                 acciones='<a class="btn btn-primario" href="asesoria-form.html">%s '
                          "Registrar asesoria</a>" % ico("plus", 16))


# --- 22. Mis asesorias -------------------------------------------------------
def asesorias():
    filas = []
    for cod, emp, estu, sector, estado, fecha, mod in ASESORIAS:
        acciones = []
        if estado == "Pendiente de confirmar":
            acciones.append(_ba("confirmar-asesoria", "check", "Confirmar"))
        acciones.append(_ba("reprogramar-asesoria", "edit", "Reprogramar"))
        acciones.append(_ba("ver", "eye", "Ver detalle"))
        filas.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % emp, estu, sector,
            badge(estado, ESTADOS_AS[estado]), fecha, mod,
            _acc(*acciones),
        ])
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Confirmada", "Pendiente de confirmar",
                        "Finalizada"], 4)
               + _filtro("Filtrar por emprendimiento",
                         ["Todos los emprendimientos", "Sabor y Sabe", "Krea Textil",
                          "EcoPack"], 1)
               + _contador())
    cuerpo = callout(
        "Como docente tú confirmas la <b>fecha y la hora</b> que el estudiante solicitó. "
        "El estudiante no puede agendar por su cuenta.", "bombilla")
    cuerpo += _sep()
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo("Solicitudes y asesorias del docente",
                                        ["Codigo", "Emprendimiento", "Estudiante", "Sector", "Estado",
                                         "Fecha y hora", "Modalidad", "@ACC"], filas)
                    + paginas(1, 6, 24))
    return shell(R, "asesorias", "Mis asesorias", cuerpo,
                 migas=["Inicio", "Mis asesorias"],
                 sub="Asesorias asignadas y las que aun debes confirmar.",
                 acciones='<a class="btn btn-primario" href="asesoria-form.html">%s '
                          "Registrar asesoria</a>" % ico("plus", 16))


# --- 23. Registrar asesoria --------------------------------------------------
def asesoria_form():
    cuerpo = steps(["Solicitud recibida", "Confirmar fecha", "Registrar sesion",
                    "Cerrar asesoria"], 1)
    cuerpo += _sep_lg()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
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
    cuerpo += '<div class="grid">'
    cuerpo += card("Temas a trabajar", campo(
        "Contenido de la sesión", alto=True,
        valor="Presupuesto de insumos, punto de equilibrio y canal de venta en el campus.",
        ph="Que temas se van a trabajar"))
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + _bt("confirmar-asesoria", "check", "Confirmar y notificar")
                   + _bt("reprogramar-asesoria", "calendar", "Proponer otra fecha",
                         "btn btn-secundario")
                   + _bt("rechazar-asesoria", "x", "Rechazar solicitud",
                         "btn btn-secundario")
                   + "</div>"
                   + '<div class="nota-foot">Al confirmar, el estudiante recibe la '
                     "notificacion con la fecha, la hora y el lugar.</div>")
    cuerpo += "</div></div>"
    return shell(R, "asesorias", "Registrar asesoría", cuerpo,
                 migas=["Inicio", "Mis asesorías", "Registrar asesoría"],
                 sub="Confirma la fecha solicitada y deja el acta de la sesión.",
                 acciones='<a class="btn btn-secundario" href="asesorias.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 24. Emprendimientos asignados -------------------------------------------
def emprendimientos():
    """Tarjetas con avance + tabla de proyectos; el docente elige sobre cuales trabaja."""
    cuerpo = callout(
        "Solo aparecen los <b>8 emprendimientos</b> que tienes asignados. No puedes "
        "agregar ni reasignar estudiantes.", "bombilla")
    cuerpo += _sep()
    cuerpo += metricas([
        ("maleta", "Asignados", "8", "", 62, None),
        ("trend", "En fase 2 o 3", "5", "", 70, None),
        ("alerta", "Requieren atención", "2", "", 25, None),
    ])
    cuerpo += _sep()

    tarjetas = '<div class="emp-grid">'
    for emp, estu, sector, etapa, avance, asesoria, act in ASIGNADOS:
        pie = ('<a class="btn btn-sm btn-secundario" href="emprendimiento-expediente.html">'
               "Abrir expediente</a>")
        tarjetas += tarjeta_emp("maleta", emp,
                                "%s · %s" % (estu, sector), avance,
                                etapa, "%d%%" % avance, pie)
    tarjetas += "</div>"
    tarjetas += ('<p class="nota-foot">Ultima actividad registrada en el expediente '
                 "de cada estudiante.</p>")

    filas = []
    for emp, estu, sector, etapa, avance, ases, act in ASIGNADOS:
        rev, col = REVISION[emp]
        filas.append([
            "<b>%s</b>" % emp, estu, sector, etapa, _barra(avance),
            badge(rev, col), act,
            '<a class="btn btn-sm btn-secundario" '
            'href="emprendimiento-expediente.html">Abrir</a>',
        ])
    filtros = (_filtro("Filtrar por etapa",
                       ["Todas las etapas", "FASE 1 - Ideacion", "FASE 2 - Prototipo",
                        "FASE 3 - Validacion"], 3)
               + _filtro("Filtrar por sector",
                         ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                          "Muebles"], 2)
               + _contador())
    tabla_proy = _zona(toolbar(filtros=filtros) + _tabla_con_titulo(
        "Proyectos asignados al docente",
        ["Emprendimiento", "Estudiante", "Sector", "Etapa", "Avance",
         "Estado de revision", "Ultima actividad", "@ACC"], filas))

    cuerpo += _tabs([("tarjetas", "Tarjetas"), ("tabla", "Tabla")])
    cuerpo += _panel("tarjetas", tarjetas, activo=True)
    cuerpo += _panel("tabla", tabla_proy)
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
    cuerpo += _sep()

    avances = _tabla_con_titulo(
        "Avances y calificaciones del emprendimiento",
        ["Fecha", "Fase", "Descripcion del avance", "Calificacion", "@ACC"],
        [["12 nov 2024", "FASE 2", "Prototipo de empaque listo para 20 unidades",
          badge("92 de 100", "b-azul"), _acc(_ba("ver", "eye", "Ver detalle"))],
         ["05 nov 2024", "FASE 2", "Definicion de precios y punto de equilibrio",
          badge("88 de 100", "b-azul"), _acc(_ba("ver", "eye", "Ver detalle"))],
         ["28 oct 2024", "FASE 1", "Diagnostico inicial y problema claro",
          badge("81 de 100", "b-azul"), _acc(_ba("ver", "eye", "Ver detalle"))]])

    tareas = kanban([
        ("Por calificar", [
            ("Evidencia fotografica del punto de venta",
             "Sabor y Sabe · Vence 12 nov 2024",
             badge("Alta", "b-amarillo"),
             _bt("calificar", "check", "Calificar", "btn btn-sm btn-primario")),
        ]),
        ("Devueltas al estudiante", [
            ("Presupuesto de insumos", "Sabor y Sabe · Faltan soportes",
             badge("Media", "b-linea"),
             '<a class="btn btn-sm btn-secundario" href="tareas.html">Ver</a>'),
        ]),
        ("Calificadas", [
            ("Perfil en redes sociales", "Calificada el 09 nov 2024",
             badge("Completada", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="tareas.html">Ver</a>'),
        ]),
    ])

    filas_as = []
    for cod, emp, estu, sector, estado, fecha, mod in ASESORIAS:
        if emp == "Sabor y Sabe":
            filas_as.append([cod, fecha, mod, badge(estado, ESTADOS_AS[estado]),
                             _acc(_ba("ver", "eye", "Ver detalle"))])
    asesorias_panel = tabla(["Codigo", "Fecha y hora", "Modalidad", "Estado", "@ACC"],
                            filas_as)

    diag_panel = lista_def([
        ("Ultima revision", "28 oct 2024, 09:14"),
        ("Puntaje heuristics", "7.8 de 10"),
        ("Recomendaciones enviadas", "Canal de venta y presupuesto de publicidad"),
    ]) + '<div class="form-acciones">' + _bt(
        "revisar-diagnostico", "clipboard", "Revisar y recomendar") + "</div>"

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
        ("Estudiante", "Mariana Lopez"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col">'
                   + _bt("registrar-avance", "edit", "Registrar avance")
                   + '<a class="btn btn-secundario" href="tareas.html">%s Revisar tareas</a>'
                     % ico("checklist", 16)
                   + '<a class="btn btn-secundario" href="asesoria-form.html">%s '
                     "Registrar asesoria</a>" % ico("chat", 16)
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
            "<b>%s</b>" % estu, emp, FASE_POR_EMP[emp], _barra(avance), act,
            badge("Con evidencia" if evid else "Sin evidencia",
                  "b-azul" if evid else "b-amarillo"),
            _acc(_ba("registrar-avance", "edit", "Registrar avance"),
                 _ba("ver", "eye", "Ver historial")),
        ])
    filtros = (_filtro("Filtrar por fase", ["Todas las fases"] + FASES, 2)
               + _filtro("Filtrar por evidencia",
                         ["Toda la evidencia", "Con evidencia", "Sin evidencia"], 5)
               + _contador())
    cuerpo = callout(
        "Registra aquí el avance de fase de cada estudiante. El estudiante solo puede "
        "<b>consultar</b> su historial.", "bombilla")
    cuerpo += _sep()
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo("Avance de fase por estudiante",
                                        ["Estudiante", "Emprendimiento", "Fase", "Avance",
                                         "Ultimo registro", "Evidencia", "@ACC"], filas)
                    + paginas(1, 5, 8))
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Registra avances y califica entregas de tus estudiantes.",
                 acciones='<a class="btn btn-secundario" href="seguimiento-dashboard.html">'
                          "%s Ver tablero</a>" % ico("grid", 16))


# --- 27. Tablero de seguimiento ----------------------------------------------
def seguimiento_dashboard():
    cuerpo = metricas([
        ("trend", "Avances este mes", "23", "", 88, "+7"),
        ("checklist", "Sin calificar", "2", "", 22, None),
        ("alerta", "Sin evidencia", "3", "", 34, None),
        ("medalla", "Promedio de calificación", "89", "", 89, "+2"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Avance de fase por emprendimiento", barras_h(
        "", "", [a[0] for a in ASIGNADOS], [a[4] for a in ASIGNADOS],
        maximo=100, unidad="%"))
    cuerpo += card("Calificaciones por estudiante", barras(
        "", "", ["Mariana L.", "Jhon O.", "Lucia F.", "Sofia R.", "Andres F."],
        [92, 85, 95, 78, 88], maximo=100, unidad=" de 100"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Distribucion de avances", donut(
        "", "", [("Con evidencia", 18, AZUL), ("Sin evidencia", 5, AMAR)], "avances"))
    cuerpo += card("Pendientes por orden de prioridad", lista_def([
        ("Evidencias por revisar", '<a href="tareas.html?f=En+revision">3 archivos</a>'),
        ("Avances sin calificar", '<a href="seguimiento.html?f=Sin+evidencia">2 entregas</a>'),
        ("Asesorias por confirmar", '<a href="asesorias.html?f=Pendiente+de+confirmar">1 solicitud</a>'),
    ]))
    cuerpo += "</div></div>"
    return shell(R, "seguimiento", "Tablero de seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Tablero"],
                 sub="Vista agregada del avance de tus estudiantes.",
                 acciones=_bt("registrar-avance", "edit", "Registrar avance"))


# --- 28. Registrar avance y calificar ----------------------------------------
def seguimiento_notas():
    cuerpo = '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
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
                   + _select_libre("rev-estado", "Estado de revision",
                                   ["Pendiente", "En revision", "Calificada", "Devuelta"],
                                   valor="En revision")
                   + campo("Comentario para el estudiante", alto=True,
                           valor="Buen trabajo en la definición de precios. Para la "
                                 "siguiente fase falta medir el costo de los empaques.",
                           ph="Retroalimentacion"))
    cuerpo += '<div class="form-acciones">'
    cuerpo += '<button class="btn btn-secundario">%s Guardar borrador</button>' % ico("doc", 16)
    cuerpo += _bt("confirmar-avance", "check", "Registrar avance")
    cuerpo += "</div></div>"
    cuerpo += '<div class="grid">'
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
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Comportamiento entrepreneurial del estudiante", barras_h(
        "", "", ["Visión", "Creatividad", "Resiliencia", "Liderazgo",
                 "Trabajo en equipo", "Toma de decisiones"],
        [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
    cuerpo += card("Tus recomendaciones", campo(
        "Recomendaciones", alto=True,
        valor="Definir con más precisión el canal de venta digital y separar el "
              "presupuesto de insumos del de publicidad.",
        ph="Que debe reforzar el estudiante"))
    cuerpo += '<div class="form-acciones">'
    cuerpo += '<button class="btn btn-secundario">%s Descargar PDF</button>' % ico("download", 16)
    cuerpo += _bt("guardar-recomendaciones", "check", "Guardar recomendaciones")
    cuerpo += "</div></div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Resumen", lista_def([
        ("Estudiante", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Respondido", "28 oct 2024, 09:14"),
        ("Puntaje heuristics", "7.8 de 10"),
    ]))
    cuerpo += card("Pendientes de revision", _tabla_con_titulo(
        "Pendientes de revision del diagnostico",
        ["Estudiante", "Emprendimiento", "Fecha", "@ACC"],
        [["Jhon Ospina", "Krea Textil", "30 oct 2024",
          _acc(_ba("revisar-diagnostico", "eye", "Revisar"))],
         ["Sofia Ramirez", "Aromas del Sur", "02 nov 2024",
          _acc(_ba("revisar-diagnostico", "eye", "Revisar"))]]))
    cuerpo += "</div></div>"
    return shell(R, "diagnostico", "Revisión del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico"],
                 sub="Revisa los resultados y deja recomendaciones al estudiante.")


# --- 30. Tareas asignadas ----------------------------------------------------
def tareas():
    filas = [
        ["<b>Evidencia fotografica del punto de venta</b>", "Sabor y Sabe", "Mariana Lopez",
         badge("Alta", "b-amarillo"), "12 nov 2024", badge("En revision", "b-amarillo"),
         _acc(_ba("calificar", "check", "Calificar"), _ba("ver", "eye", "Ver evidencia"))],
        ["<b>Presupuesto de insumos</b>", "Sabor y Sabe", "Mariana Lopez",
         badge("Media", "b-amarillo"), "15 nov 2024", badge("Completada", "b-azul"),
         _acc(_ba("calificar", "check", "Calificar"))],
        ["<b>Perfil en redes sociales</b>", "Krea Textil", "Jhon Ospina",
         badge("Baja", "b-linea"), "16 nov 2024", badge("Pendiente", "b-neutra"),
         _acc(_ba("calificar", "check", "Calificar"))],
        ["<b>Prototipo de empaque</b>", "EcoPack", "Lucia Fernandez",
         badge("Alta", "b-amarillo"), "14 nov 2024", badge("En revision", "b-amarillo"),
         _acc(_ba("calificar", "check", "Calificar"), _ba("ver", "eye", "Ver evidencia"),
              _ba("devolver-tarea", "x", "Devolver"))],
        ["<b>Analisis de competencia</b>", "Aromas del Sur", "Sofia Ramirez",
         badge("Media", "b-amarillo"), "18 nov 2024", badge("Pendiente", "b-neutra"),
         _acc(_ba("calificar", "check", "Calificar"))],
    ]
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Pendiente", "En revision", "Completada"], 5)
               + _filtro("Filtrar por prioridad",
                         ["Toda la prioridad", "Alta", "Media", "Baja"], 3)
               + _contador())
    cuerpo = callout("La tarea se considera <b>completada</b> cuando el estudiante "
                     "adjunta al menos una evidencia.", "bombilla")
    cuerpo += _sep()
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo("Tareas asignadas por revisar",
                                        ["Tarea", "Emprendimiento", "Estudiante", "Prioridad", "Vence",
                                         "Estado", "@ACC"], filas)
                    + paginas(1, 5, 23))
    return shell(R, "tareas", "Tareas asignadas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Revisa y califica las entregas con evidencia de tus estudiantes.",
                 acciones=_bt("asignar-tarea", "plus", "Asignar tarea"))


# --- 31. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = metricas([
        ("maleta", "Emprendimientos asignados", "8", "", 62, None),
        ("chat", "Asesorías realizadas", "31", "", 78, None),
        ("medalla", "Promedio de calificación", "89", "", 89, "+2"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
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
                   + _bt("cambiar-contrasena", "lock", "Cambiar contrasena",
                         "btn btn-secundario")
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
