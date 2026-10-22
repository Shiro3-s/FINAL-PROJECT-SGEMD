# -*- coding: utf-8 -*-
"""Rol ADMINISTRADOR - 19 pantallas.

Reglas del rol:
  - Gestiona perfiles de docentes y estudiantes, y sus asignaciones.
  - Aprueba solicitudes, crea eventos y modera comentarios.
  - Ve el seguimiento de todos los emprendimientos, no solo los asignados.
  - Exporta reportes en CSV y PDF.
  - Configura el programa (sedes, etapas, cupos, notificaciones) desde su
    propia vista de Configuración.
"""

import json
import unicodedata

from lib_ui import (calendario, calendario_interactivo, agenda,
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, formulario, lista_def, steps, ico, boton_accion, distribucion,
    lista_avisos, kanban, linea_tiempo, tabs_paneles, NOTIFS_ADMIN,
    th, _etiqueta,
)
from lib_charts import barras, barras_h, lineas, donut, AZUL, AMAR, GRIS

R = "administrador"

SEDES = ["Sede Norte", "Sede Centro", "Sede Sur"]

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
    ("912646", "Mariana López", "Alimentos", "Sabor y Sabe",
     "FASE 2 - Prototipo", 62, "Activo"),
    ("912647", "Jhon Ospina", "Moda", "Krea Textil",
     "FASE 1 - Ideación", 28, "Activo"),
    ("912648", "Lucía Fernández", "Ambiental", "EcoPack",
     "FASE 3 - Validación", 84, "Activo"),
    ("912649", "Sofía Ramírez", "Alimentos", "Aromas del Sur",
     "FASE 1 - Ideación", 15, "Activo"),
    ("912650", "Andrés Felipe", "Muebles", "Muebles Origen",
     "FASE 2 - Prototipo", 55, "Inactivo"),
    ("912651", "Camilo Rojas", "Tecnología", "TechNova",
     "FASE 1 - Ideación", 12, "Activo"),
    ("912652", "Valentina Ortega", "Moda", "Aura Design",
     "FASE 2 - Prototipo", 47, "Activo"),
    ("912653", "Diego Peralta", "Muebles", "WoodCraft",
     "FASE 1 - Ideación", 24, "Activo"),
    ("912654", "Laura Martínez", "Ambiental", "BioEco",
     "FASE 3 - Validación", 76, "Activo"),
    ("912655", "Sebastián Torres", "Alimentos", "Gourmet Fresh",
     "FASE 2 - Prototipo", 58, "Activo"),
    ("912656", "Ana Restrepo", "Tecnología", "SmartApp",
     "FASE 1 - Ideación", 19, "Activo"),
    ("912657", "Mateo Gómez", "Moda", "Urban Style",
     "FASE 1 - Ideación", 31, "Activo"),
]

EMPRENDIMIENTOS = [
    ("EMP-041", "Sabor y Sabe", "Mariana López", "mariana.lopez@sgemd.edu.co",
     "Alimentos", "Comercio", "FASE 2 - Prototipo", 62, "Carlos Mendoza",
     "carlos.mendoza@sgemd.edu.co", "Sede Norte"),
    ("EMP-040", "Krea Textil", "Jhon Ospina", "jhon.ospina@sgemd.edu.co",
     "Moda", "Moda", "FASE 1 - Ideación", 28, "Paula Andrea Rios",
     "paula.rios@sgemd.edu.co", "Sede Centro"),
    ("EMP-039", "EcoPack", "Lucía Fernández", "lucia.fernandez@sgemd.edu.co",
     "Ambiental", "Industrial", "FASE 3 - Validación", 84, "Hector Vargas",
     "hector.vargas@sgemd.edu.co", "Sede Sur"),
    ("EMP-038", "Aromas del Sur", "Sofía Ramírez", "sofia.ramirez@sgemd.edu.co",
     "Alimentos", "Alimentos", "FASE 1 - Ideación", 15, "Sin asignar",
     "", "Sede Norte"),
    ("EMP-037", "Muebles Origen", "Andrés Felipe", "andres.felipe@sgemd.edu.co",
     "Muebles", "Artesanal", "FASE 2 - Prototipo", 55, "Ninafq Beltran",
     "nina.beltran@sgemd.edu.co", "Sede Centro"),
    ("EMP-036", "TechNova", "Camilo Rojas", "camilo.rojas@sgemd.edu.co",
     "Tecnología", "Software", "FASE 1 - Ideación", 12, "Rafael Nieto",
     "rafael.nieto@sgemd.edu.co", "Sede Norte"),
    ("EMP-035", "Aura Design", "Valentina Ortega", "valentina.ortega@sgemd.edu.co",
     "Moda", "Moda", "FASE 2 - Prototipo", 47, "Paula Andrea Rios",
     "paula.rios@sgemd.edu.co", "Sede Sur"),
    ("EMP-034", "WoodCraft", "Diego Peralta", "diego.peralta@sgemd.edu.co",
     "Muebles", "Artesanal", "FASE 1 - Ideación", 24, "Sin asignar",
     "", "Sede Centro"),
    ("EMP-033", "BioEco", "Laura Martínez", "laura.martinez@sgemd.edu.co",
     "Ambiental", "Industrial", "FASE 3 - Validación", 76, "Hector Vargas",
     "hector.vargas@sgemd.edu.co", "Sede Norte"),
    ("EMP-032", "Gourmet Fresh", "Sebastián Torres", "sebastian.torres@sgemd.edu.co",
     "Alimentos", "Alimentos", "FASE 2 - Prototipo", 58, "Carlos Mendoza",
     "carlos.mendoza@sgemd.edu.co", "Sede Sur"),
    ("EMP-031", "SmartApp", "Ana Restrepo", "ana.restrepo@sgemd.edu.co",
     "Tecnología", "Software", "FASE 1 - Ideación", 19, "Rafael Nieto",
     "rafael.nieto@sgemd.edu.co", "Sede Centro"),
    ("EMP-030", "Urban Style", "Mateo Gómez", "mateo.gomez@sgemd.edu.co",
     "Moda", "Moda", "FASE 1 - Ideación", 31, "Sin asignar",
     "", "Sede Norte"),
]

# Bandeja de solicitudes pendientes (D1/D2/D4).
SOLIC_DESBLOQUEOS = [
    ("912650", "Andres Felipe", "Estudiante", "Cuenta inactiva por 90 días sin acceso",
     "05 nov 2024"),
    ("DOC-011", "Ninafq Beltran", "Docente", "Bloqueo por intentos fallidos de acceso",
     "04 nov 2024"),
    ("912651", "Camilo Rojas", "Estudiante", "Reactivar para retomar su emprendimiento",
     "02 nov 2024"),
    ("912652", "Valentina Ortega", "Estudiante", "Cuenta limitada a petición; solicita reactivar",
     "01 nov 2024"),
]

SOLIC_PARALELOS = [
    ("912647", "Jhon Ospina", "Krea Textil", "Krea Accesorios", "Moda", "06 nov 2024"),
    ("912649", "Sofia Ramirez", "Aromas del Sur", "Café del Sur", "Alimentos", "05 nov 2024"),
    ("912653", "Diego Peralta", "Muebles Origen", "Muebles Origen Kids", "Muebles", "03 nov 2024"),
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

def _sin_tildes(txt):
    """Texto sin tildes ni ñ, en minúsculas: base de correos y comparaciones."""
    s = unicodedata.normalize("NFKD", txt or "")
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


def _correo(nombre):
    """Correo institucional a partir del nombre: sin tildes y con puntos."""
    base = _sin_tildes(nombre).replace(" ", ".")
    return "%s@sgemd.edu.co" % base


# Correo institucional derivado del nombre del estudiante
CORREOS_EST = {e[1]: _correo(e[1]) for e in ESTUDIANTES}

# Indice de estudiantes por ID de 6 dígitos y por nombre normalizado (para
# cruzar las bandejas de solicitudes, que escriben el nombre sin tildes).
ID_EST = {e[0]: e for e in ESTUDIANTES}
EST_POR_NOMBRE = {_sin_tildes(e[1]): e for e in ESTUDIANTES}

# Sede de cada estudiante, deducida del emprendimiento que tiene asignado.
SEDE_EST = {e[2]: e[10] for e in EMPRENDIMIENTOS}


def _estudiante(nombre):
    """Registro de ESTUDIANTES a partir del nombre (con o sin tildes)."""
    return EST_POR_NOMBRE.get(_sin_tildes(nombre))


def _id_estudiante(nombre):
    """ID de 6 dígitos del estudiante; si no se conoce, devuelve el código
   legacy para que la vista no se rompa."""
    est = _estudiante(nombre)
    return est[0] if est else "—"

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
# Script JS propio del rol administrador: controlador de tablas con
# buscador, filtros y paginacion propias, fichas de registro, enlaces
# profundos, toasts y modales propios y calendario de eventos. Vive en
# el rol (y no en lib_js) para no tocar el kit compartido ni los otros
# roles.
ADMIN_JS = r"""
(function () {
  "use strict";

  /* ===================================================================
     Script propio del rol ADMINISTRADOR.

     El kit compartido (lib_js) resuelve buscador, filtros y paginacion de
     UNA sola tabla por pagina: se agarra del primer [data-tabla-zona] y de
     los .buscador. Varias pantallas del admin tienen dos tablas, asi que
     aqui hay un controlador por tabla.

     Regla de convivencia (para no tocar lib_js y no romper otros roles):
       - los controles del admin se marcan con data-filtro="off" para que
         el kit los ignore;
       - el buscador del admin no usa la clase .buscador ni la palabra
         "Buscar" en el placeholder, asi que el kit no lo engancha;
       - la paginacion del admin se marca data-pag-adm (no data-paginacion),
         de modo que el kit no la mueve;
       - la visibilidad de las filas la lleva solo este script.
     =================================================================== */

  /* ---- utilidades ----------------------------------------------------- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };
  var norm = function (s) {
    return String(s == null ? "" : s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };
  var ICO = {
    check: "M20 6 9 17l-5-5",
    x: "M18 6 6 18M6 6l12 12",
    alerta: "M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0ZM12 9v4M12 17h.01",
    bombilla: "M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z",
    ojo: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7zM12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
    correo: "M4 4h16v16H4zM4 6l8 6 8-6"
  };
  var svg = function (d, n) {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + (n || 16) + '" height="' +
      (n || 16) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ' +
      'aria-hidden="true"><path d="' + d + '"/></svg>';
  };
  var dato = function (fila, attr) {
    var key = String(attr).replace(/-([a-z])/g, function (m, c) { return c.toUpperCase(); });
    return fila.dataset[key];
  };

  /* ---- toast propio (el kit lo esconde dentro de su IIFE) -------------- */
  var pilaToast = null;
  function toast(mensaje, tipo) {
    if (!pilaToast) {
      pilaToast = document.createElement("div");
      pilaToast.className = "toast-pila";
      pilaToast.setAttribute("role", "status");
      pilaToast.setAttribute("aria-live", "polite");
      document.body.appendChild(pilaToast);
    }
    var t = document.createElement("div");
    t.className = "toast t-" + (tipo || "info");
    t.innerHTML = svg(tipo === "ok" ? ICO.check : (tipo === "error" ? ICO.alerta : ICO.bombilla), 16) +
      "<span>" + esc(mensaje) + "</span>";
    pilaToast.appendChild(t);
    setTimeout(function () { t.classList.add("va-fuera"); }, 3200);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 3800);
  }

  /* ---- modal propio (mismo marcado que el del kit) --------------------- */
  function cerrarModal() {
    var v = $(".modal-velo");
    if (v) v.remove();
    document.body.classList.remove("sin-scroll");
  }
  function abrirModal(titulo, cuerpo, botones) {
    cerrarModal();
    var velo = document.createElement("div");
    velo.className = "modal-velo";
    velo.innerHTML =
      '<div class="modal" role="dialog" aria-modal="true" aria-label="' + esc(titulo) + '">' +
      '<div class="modal-head"><h2>' + esc(titulo) + '</h2>' +
      '<button class="icon-btn modal-x" aria-label="Cerrar">' + svg(ICO.x, 18) + "</button></div>" +
      '<div class="modal-cuerpo">' + cuerpo + "</div>" +
      '<div class="modal-foot"></div></div>';
    var pie = $(".modal-foot", velo);
    (botones || [{ txt: "Cerrar", clase: "btn btn-secundario" }]).forEach(function (b) {
      var el = document.createElement("button");
      el.className = b.clase || "btn btn-secundario";
      el.textContent = b.txt;
      el.addEventListener("click", function (e) {
        e.stopPropagation();
        if (b.alClic) b.alClic(velo);
        if (b.cerrar !== false) cerrarModal();
      });
      pie.appendChild(el);
    });
    document.body.appendChild(velo);
    document.body.classList.add("sin-scroll");
    $(".modal-x", velo).addEventListener("click", function (e) {
      e.stopPropagation();
      cerrarModal();
    });
    velo.addEventListener("click", function (e) { if (e.target === velo) cerrarModal(); });
    return velo;
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarModal();
  });

  /* ---- calendario interactivo de eventos ------------------------------- */
  var calDoc = document.querySelector("[data-cal-doc]");
  if (calDoc) {
    var celdas = Array.prototype.slice.call(calDoc.querySelectorAll("[data-dia]"));
    var paneles = Array.prototype.slice.call(calDoc.querySelectorAll("[data-dia-panel]"));
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
    if (hoyCal) verDia(hoyAttr, hoyCal.getAttribute("data-etiqueta"));
  }

  /* ---- controlador de tablas del admin --------------------------------- */
  var ZONAS = [];

  function crearZona(zona) {
    var tabla = $("table.tabla", zona);
    if (!tabla) return null;
    var tid = (zona.getAttribute("data-tabla-zona") || "").replace(/^adm-/, "");
    var filas = $$("tbody tr", tabla);
    var control = $("[data-pag-adm]", zona);
    var tam = control ? (parseInt(control.dataset.pagTam, 10) || 5) : 0;
    var buscador = $("[data-adm-busca]", zona);
    var filtros = $$("[data-filtro-adm]", zona);
    var contador = $("[data-resultados]", zona);
    var vacio = $("[data-vacio]", zona);
    var pagina = 1;

    function coincide(fila) {
      var q = buscador ? norm(buscador.value) : "";
      if (q && norm(fila.textContent).indexOf(q) < 0) return false;
      for (var i = 0; i < filtros.length; i++) {
        var sel = filtros[i];
        var col = parseInt(sel.dataset.col, 10);
        if (isNaN(col)) continue;
        var celda = fila.children[col];
        if (!celda) continue;
        /* Si la celda declara data-valor se compara contra ese valor (por
           ejemplo un <select> de estado, cuyo textContent trae todas las
           opciones). Si la celda trae un <select>, manda su valor actual,
           para que el filtro siga a la cuenta despues de cambiarla. */
        var selCelda = celda.querySelector("select");
        var propio = selCelda ? selCelda.value : celda.getAttribute("data-valor");
        var txt = norm(propio === null ? celda.textContent : propio);
        var valor = "";
        if (sel.tagName === "SELECT") {
          if (!sel.value) continue;
          valor = norm(sel.value || (sel.selectedOptions[0] ? sel.selectedOptions[0].textContent : ""));
        } else {
          valor = norm(sel.value);
          if (!valor) continue;
        }
        if (valor && txt.indexOf(valor) < 0) return false;
      }
      return true;
    }

    function visibles() {
      return filas.filter(coincide);
    }

    function pintarPag(nPag) {
      var pag = control ? $(".pag", control) : null;
      if (!pag) return;
      var tplPrev = control.querySelector("template[data-pg-ico-prev]");
      var tplNext = control.querySelector("template[data-pg-ico-next]");
      var ip = tplPrev ? tplPrev.innerHTML : "";
      var inx = tplNext ? tplNext.innerHTML : "";
      var h = '<button class="btn btn-secundario btn-sm" data-pagina="prev"' +
        (pagina <= 1 ? " disabled" : "") + ">" + ip + " Anterior</button>";
      for (var n = 1; n <= nPag; n++) {
        h += '<button class="btn btn-sm ' + (n === pagina ? "btn-acento" : "btn-secundario") +
          '" data-pagina="' + n + '"' + (n === pagina ? ' aria-current="page"' : "") + ">" + n + "</button>";
      }
      h += '<button class="btn btn-secundario btn-sm" data-pagina="next"' +
        (pagina >= nPag ? " disabled" : "") + ">Siguiente " + inx + "</button>";
      pag.innerHTML = h;
    }

    function aplicar() {
      var vis = visibles();
      var nPag = tam ? Math.max(1, Math.ceil(vis.length / tam)) : 1;
      if (pagina > nPag) pagina = nPag;
      if (pagina < 1) pagina = 1;
      var desde = (pagina - 1) * tam;
      var hasta = tam ? Math.min(desde + tam, vis.length) : vis.length;
      filas.forEach(function (f) { f.hidden = true; });
      vis.slice(desde, hasta).forEach(function (f) { f.hidden = false; });
      if (contador) {
        contador.textContent = vis.length + (vis.length === 1 ? " resultado" : " resultados");
      }
      if (vacio) vacio.hidden = vis.length > 0;
      if (control) {
        control.dataset.pagActual = pagina;
        control.dataset.pagTotal = nPag;
        control.dataset.pagRegs = vis.length;
        var t = $("[data-pag-texto]", control);
        if (t) {
          t.textContent = "Mostrando " + (vis.length && tam ? desde + 1 : 0) +
            " a " + hasta + " de " + vis.length;
        }
        pintarPag(nPag);
      }
      return vis;
    }

    function irA(fila) {
      var vis = visibles();
      var i = vis.indexOf(fila);
      if (i < 0) return false;
      pagina = tam ? Math.floor(i / tam) + 1 : 1;
      aplicar();
      return true;
    }

    function limpiar() {
      if (buscador) buscador.value = "";
      filtros.forEach(function (f) { f.value = ""; });
      pagina = 1;
      aplicar();
    }

    if (buscador) {
      var t = null;
      buscador.addEventListener("input", function () {
        clearTimeout(t);
        t = setTimeout(function () { pagina = 1; aplicar(); }, 220);
      });
      buscador.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          clearTimeout(t);
          pagina = 1;
          aplicar();
        }
      });
    }
    filtros.forEach(function (f) {
      if (f.tagName === "SELECT") {
        f.addEventListener("change", function () { pagina = 1; aplicar(); });
      } else {
        var tt = null;
        f.addEventListener("input", function () {
          clearTimeout(tt);
          tt = setTimeout(function () { pagina = 1; aplicar(); }, 220);
        });
      }
    });
    if (control) {
      control.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-pagina]");
        if (!b || b.disabled) return;
        e.preventDefault();
        e.stopPropagation();
        var nPag = parseInt(control.dataset.pagTotal, 10) || 1;
        var v = b.dataset.pagina;
        if (v === "prev") pagina = Math.max(1, pagina - 1);
        else if (v === "next") pagina = Math.min(nPag, pagina + 1);
        else pagina = parseInt(v, 10) || 1;
        aplicar();
      });
    }
    aplicar();
    return {
      tid: tid, zona: zona, filas: filas,
      aplicar: aplicar, irA: irA, limpiar: limpiar
    };
  }

  $$("[data-tabla-zona]").forEach(function (z) {
    var c = crearZona(z);
    if (c) ZONAS.push(c);
  });

  function zonaDe(fila) {
    var z = fila.closest("[data-tabla-zona]");
    for (var i = 0; i < ZONAS.length; i++) {
      if (ZONAS[i].zona === z) return ZONAS[i];
    }
    return null;
  }

  /* ---- fichas de registro --------------------------------------------- */
  var FICHAS = {
    estudiante: {
      titulo: "est-nombre",
      campos: [["ID de estudiante", "est-id"], ["Nombre", "est-nombre"],
               ["Correo institucional", "est-correo"], ["Sector", "est-sector"],
               ["Emprendimiento", "est-emp"], ["Etapa", "est-etapa"],
               ["Sede", "est-sede"], ["Avance", "est-avance"],
               ["Estado de la cuenta", "est-estado"]],
      correo: "est-correo"
    },
    emprendimiento: {
      titulo: "emp-nombre",
      campos: [["Código", "emp-cod"], ["Emprendimiento", "emp-nombre"],
               ["ID de estudiante", "emp-est-id"], ["Estudiante", "emp-est-nombre"],
               ["Correo institucional", "emp-est-correo"], ["Sector", "emp-sector"],
               ["Tipo", "emp-tipo"], ["Etapa", "emp-etapa"],
               ["Avance", "emp-avance"], ["Sede", "emp-sede"],
               ["Docente asignado", "emp-docente"]],
      correo: "emp-est-correo"
    },
    docente: {
      titulo: "doc-nombre",
      campos: [["Código", "doc-cod"], ["Nombre", "doc-nombre"],
               ["Correo institucional", "doc-correo"], ["Área", "doc-area"],
               ["Carga semanal", "doc-carga"], ["Emprendimientos", "doc-emp"],
               ["Estado de la cuenta", "doc-estado"]],
      correo: "doc-correo"
    },
    solicitud: {
      titulo: "sol-nombre",
      campos: [["Código", "sol-id"], ["Solicitante", "sol-nombre"],
               ["Tipo de solicitud", "sol-tipo"], ["Detalle", "sol-detalle"],
               ["Fecha", "sol-fecha"]],
      correo: "sol-correo"
    }
  };

  function fichaHTML(fila, tipo) {
    var def = FICHAS[tipo];
    if (!def) return "";
    var h = '<dl class="lista-def">';
    def.campos.forEach(function (c) {
      var v = dato(fila, c[1]);
      if (!v) return;
      h += '<div class="def-row"><dt>' + esc(c[0]) + "</dt><dd>" + esc(v) + "</dd></div>";
    });
    h += "</dl>";
    var correo = def.correo ? dato(fila, def.correo) : "";
    if (correo) {
      h += '<p class="modal-aviso">Contacto directo: <a href="mailto:' + esc(correo) + '">' +
        esc(correo) + "</a></p>";
    }
    return h;
  }

  function abrirFicha(fila, tipo) {
    var def = FICHAS[tipo];
    if (!def || !fila) return;
    var titulo = dato(fila, def.titulo) || "Ficha";
    abrirModal(titulo, fichaHTML(fila, tipo), [
      { txt: "Cerrar", clase: "btn btn-secundario" }
    ]);
  }

  /* ---- panel de detalle de una solicitud ------------------------------- */
  function abrirSolicitud(fila) {
    if (!fila) return;
    var tipo = dato(fila, "sol-tipo") || "Solicitud";
    var cod = dato(fila, "sol-id") || "";
    var nombre = dato(fila, "sol-nombre") || "";
    var detalle = dato(fila, "sol-detalle") || "Sin detalle registrado.";
    var fecha = dato(fila, "sol-fecha") || "";
    var cuerpo =
      '<dl class="lista-def">' +
      '<div class="def-row"><dt>Código</dt><dd>' + esc(cod) + "</dd></div>" +
      '<div class="def-row"><dt>Solicitante</dt><dd>' + esc(nombre) + "</dd></div>" +
      '<div class="def-row"><dt>Tipo</dt><dd>' + esc(tipo) + "</dd></div>" +
      '<div class="def-row"><dt>Fecha</dt><dd>' + esc(fecha) + "</dd></div>" +
      "</dl>" +
      '<p class="modal-aviso"><b>Detalle:</b> ' + esc(detalle) + "</p>" +
      '<div class="form-acciones">' +
      '<button class="btn btn-primario btn-sm" data-accion="solicitud-aprobar">Aprobar</button>' +
      '<button class="btn btn-secundario btn-sm" data-accion="solicitud-rechazar">Rechazar</button>' +
      "</div>";
    abrirModal("Detalle de la solicitud", cuerpo, [
      { txt: "Cerrar", clase: "btn btn-secundario" }
    ]);
  }

  /* ---- reasignar docente (tabla de asignaciones) ----------------------- */
  /* El formulario vive en la pagina (#form-asignar-docente, oculto) y aqui
     solo se clona, se rellena con los data-* de la fila y se abre. */
  function abrirReasignar(fila) {
    if (!fila) return;
    var actual = fila.dataset.docente || "";
    var pendiente = !actual || actual === "Sin asignar" ||
      actual === "Sin docente asignado";
    var plantilla = $("#form-asignar-docente");
    var cuerpo = plantilla
      ? plantilla.innerHTML
      : '<p><b>Proyecto:</b> ' + esc(fila.dataset.proyecto || "") + "</p>";
    var velo = abrirModal(pendiente ? "Asignar docente" : "Reasignar docente",
      cuerpo, [{
        txt: "Confirmar asignación", clase: "btn btn-primario", cerrar: false,
        alClic: function () {
          var sel = $("#docente-asignacion", velo);
          var nuevo = sel ? sel.value : "";
          if (!nuevo) return;
          fila.dataset.docente = nuevo.split(" · ")[0];
          var celdas = fila.children;
          var col = parseInt(fila.dataset.colDocente, 10);
          if (!isNaN(col) && celdas[col]) celdas[col].textContent = fila.dataset.docente;
          var btn = $("[data-adm-accion='reasignar']", fila);
          if (btn) {
            btn.setAttribute("title", "Reasignar docente");
            btn.setAttribute("aria-label", "Reasignar docente");
          }
          toast("Docente asignado correctamente", "ok");
          cerrarModal();
        }
      }, { txt: "Cancelar", clase: "btn btn-secundario" }]);
    /* Rellena el clon con los datos de la fila. */
    var llenar = function (sel2, valor) {
      var el = $(sel2, velo);
      if (el && valor) el.value = valor;
    };
    llenar("#asg-estudiante", fila.dataset.estudiante);
    llenar("#asg-emprendimiento", fila.dataset.proyecto);
    llenar("#asg-correo", fila.dataset.correo);
    var selDoc = $("#docente-asignacion", velo);
    if (selDoc) {
      var coincide = false;
      for (var i = 0; i < selDoc.options.length; i++) {
        if (selDoc.options[i].value === actual) coincide = true;
      }
      selDoc.value = coincide ? actual : "";
    }
    return velo;
  }

  /* ---- atajo del menu: #asignar-docente abre la cola pendiente ---------- */
  function abrirAsignarPendiente() {
    var filas = $$("tr[data-proyecto]");
    for (var i = 0; i < filas.length; i++) {
      var d = filas[i].dataset.docente || "";
      if (!d || d === "Sin asignar" || d === "Sin docente asignado") {
        filas[i].scrollIntoView({ block: "center" });
        abrirReasignar(filas[i]);
        return;
      }
    }
    toast("No hay emprendimientos sin docente asignado", "info");
  }

  /* ---- acciones propias del admin (data-adm-accion) -------------------- */
  $$("[data-adm-accion]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var accion = b.dataset.admAccion;
      var fila = b.closest("tr");
      if (accion === "ficha") abrirFicha(fila, b.dataset.ficha);
      else if (accion === "solicitud") abrirSolicitud(fila);
      else if (accion === "reasignar") abrirReasignar(fila);
    });
  });

  /* ---- interruptor de graficos (barras / anillo) ----------------------- */
  $$("[data-adm-grafico]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var tipo = b.dataset.admGrafico;
      var zona = b.closest(".card") || document;
      $$("[data-grafico-vista]", zona).forEach(function (v) {
        v.hidden = v.getAttribute("data-grafico-vista") !== tipo;
      });
      $$("[data-adm-grafico]", zona).forEach(function (o) {
        o.classList.toggle("btn-acento", o === b);
        o.classList.toggle("btn-secundario", o !== b);
        o.setAttribute("aria-pressed", o === b ? "true" : "false");
      });
    });
  });

  /* ---- prefill del modal de avance ------------------------------------ */
  /* El kit clona el formulario con innerHTML, asi que al abrirlo se pierde la
     opcion marcada del <select> y los valores escritos a mano. Este bloque
     corre despues del handler del kit (el script del admin va detras) y los
     vuelve a poner con los data-* de la fila. */
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest
      ? e.target.closest('[data-accion="registrar-avance"]') : null;
    if (!b) return;
    var fila = b.closest("tr");
    if (!fila) return;
    var d = fila.dataset || {};
    var campos = { emp: d.emp, estu: d.estu, etapa: d.etapa, avance: d.avance };
    for (var nombre in campos) {
      var el = document.querySelector(".modal [name=" + nombre + "]");
      if (el && campos[nombre] !== undefined && campos[nombre] !== "") {
        el.value = campos[nombre];
      }
    }
  });

  /* ---- enlaces profundos: #est-912646, #emp-EMP-041, #doc-DOC-014 ----- */
  function abrirHash() {
    var hash = (location.hash || "").replace("#", "");
    if (!hash) return;
    if (hash === "asignar-docente") { abrirAsignarPendiente(); return; }
    var corte = hash.indexOf("-");
    if (corte < 0) return;
    var tipo = hash.slice(0, corte);
    var id = hash.slice(corte + 1);
    var attr = { est: "est-id", emp: "emp-id", doc: "doc-id", sol: "sol-id" }[tipo];
    if (!attr) return;
    var fila = $("tr[data-" + attr + '="' + id + '"]');
    if (!fila) {
      toast("No encontramos el registro " + id, "error");
      return;
    }
    var z = zonaDe(fila);
    if (z) {
      z.limpiar();
      z.irA(fila);
    }
    fila.scrollIntoView({ block: "center" });
    fila.classList.add("adm-resaltada");
    setTimeout(function () { fila.classList.remove("adm-resaltada"); }, 2600);
    var ficha = $("[data-adm-accion='ficha']", fila);
    if (ficha) ficha.click();
  }
  window.addEventListener("hashchange", abrirHash);
  abrirHash();

  /* ---- el admin tambien tiene vista de configuracion -------------------- */
  /* El kit arma el mini menu con "Preferencias" para el admin; aqui se
     cambia por "Configuracion", que si tiene vista propia. */
  if (window.MutationObserver) {
    var obs = new MutationObserver(function () {
      $$(".who-menu").forEach(function (m) {
        var b = $("button[data-accion='preferencias']", m);
        if (!b) return;
        b.dataset.accion = "configuracion";
        b.textContent = "Configuracion";
      });
    });
    obs.observe(document.body, { childList: true, subtree: true });
  }
})();
"""


# CSS propio del administrador. Se inyecta en el <style> de la pagina con
# shell(extra_head=...) para no tocar lib_css, que se comparte con los demas
# roles. Solo usa tokens de la paleta del sistema.
ADMIN_CSS = """
/* Buscador propio del admin: no usa la clase .buscador porque el kit
   compartido se engancha a ".buscador input" y filtraria la primera tabla
   de la pagina, no la que el admin quiere. */
.adm-busca{display:flex;align-items:center;gap:8px;flex:1 1 240px;min-width:200px;
  padding:0 12px;background:var(--blanco);border:1px solid var(--gris);
  border-radius:var(--r-sm)}
.adm-busca svg{flex:0 0 16px;color:var(--gris)}
.adm-busca input{flex:1;min-width:0;border:0;outline:none;background:transparent;
  font-family:inherit;font-size:13px;color:var(--tinta);padding:9px 0}
.adm-busca input::placeholder{color:var(--gris)}
.adm-busca:focus-within{border-color:var(--azul-real);box-shadow:0 0 0 3px var(--azul-12)}
/* Fila que destaca un enlace profundo (#est-912646) */
tr.adm-resaltada>td{background:var(--azul-08)}
tr.adm-resaltada>td:first-child{box-shadow:inset 3px 0 0 var(--amarillo)}
/* La cabecera de la zona del admin muestra el total de resultados */
.adm-zona .card-head .hint{white-space:nowrap;font-weight:600}
"""


def _adm_busca(tid, etiqueta="Nombre, ID o correo"):
    """Buscador de una tabla del admin.

    No usa la clase .buscador (el kit compartido se engancha a ".buscador input"
    y filtraria otra tabla) ni la palabra "Buscar" en el placeholder (el kit
    tambien engancha los input[type=text] cuyo placeholder la contenga)."""
    return ('<div class="adm-busca">%s<input type="text" class="filtro" '
            'data-adm-busca="%s" placeholder="%s" autocomplete="off" '
            'aria-label="Filtrar %s"></div>'
            % (ico("search", 16), tid, etiqueta, etiqueta))


def _adm_filtro(tid, etiqueta, opciones, col, texto=False):
    """Filtro por columna de una tabla del admin.

    data-filtro="off" deja el control fuera del kit compartido. El valor de
    cada opcion es el texto exacto que aparece en la celda, que es lo que
    compara el controlador del admin."""
    if texto:
        return ('<input type="text" class="filtro" data-filtro="off" '
                'data-filtro-adm="%s" data-col="%d" placeholder="%s" '
                'autocomplete="off" aria-label="%s">'
                % (tid, col, etiqueta, etiqueta))
    ops = '<option value="">%s</option>' % opciones[0] + "".join(
        '<option value="%s">%s</option>' % (o, o) for o in opciones[1:])
    return ('<select class="filtro" data-filtro="off" data-filtro-adm="%s" '
            'data-col="%d" aria-label="%s">%s</select>'
            % (tid, col, etiqueta, ops))


def _ficha(tipo, etiqueta="Ver ficha"):
    """Boton de ficha de un registro. El controlador del admin (ADMIN_JS)
    arma el modal con los datos que la fila lleva en data-*."""
    return ('<button class="table-act" data-adm-accion="ficha" data-ficha="%s" '
            'title="%s" aria-label="%s">%s</button>'
            % (tipo, etiqueta, etiqueta, ico("eye", 16)))


def _tabla_adm(tid, titulo, cabeceras, filas, sub="", por_pagina=5,
               caption="", buscador=None, filtros="", acciones="", extra=""):
    """Tabla del admin con buscador, filtros por columna y paginacion propias.

    La zona se marca con data-tabla-zona="adm-<tid>": el controlador del admin
    (ADMIN_JS) filtra, cuenta y pagina SOLO esa tabla. El kit compartido
    resuelve una unica tabla por pagina (toma la primera [data-tabla-zona]),
    asi que las vistas del admin con dos tablas necesitan este camino propio.

    filas: lista de dicts con "celdas" (HTML de cada celda) y "attrs"
    (data-* de la fila: identificadores y datos de la ficha). Una celda puede
    ser ("html", "valor"): el "valor" es lo que comparan los filtros (util para
    un <select> de estado, cuyo textContent trae todas las opciones)."""
    cab = "".join(th(c) for c in cabeceras)
    etiquetas = [_etiqueta(c) for c in cabeceras]
    body = ""
    for fila in filas:
        attrs = "".join(' data-%s="%s"' % (k, v)
                        for k, v in fila.get("attrs", {}).items() if v)
        celdas = ""
        for c, x, eti in zip(cabeceras, fila["celdas"], etiquetas):
            valor = ""
            if isinstance(x, tuple):
                x, valor = x[0], x[1]
            if c == "@ACC":
                celdas += '<td class="acc" data-label="%s">%s</td>' % (eti, x)
            elif isinstance(c, tuple) and c[0] == "num":
                celdas += '<td class="num" data-label="%s">%s</td>' % (eti, x)
            elif valor:
                celdas += '<td data-label="%s" data-valor="%s">%s</td>' % (eti, valor, x)
            else:
                celdas += '<td data-label="%s">%s</td>' % (eti, x)
        body += "<tr%s>%s</tr>" % (attrs, celdas)
    cap = ('<caption class="visually-hidden">%s</caption>' % caption) if caption else ""
    h = '<div class="card adm-zona" data-tabla-zona="adm-%s">' % tid
    h += ('<div class="card-head"><div><h3>%s</h3>%s</div>'
          '<span class="hint" data-resultados>0 resultados</span></div>'
          % (titulo, ('<p class="sub">%s</p>' % sub) if sub else ""))
    h += '<div class="toolbar">'
    h += buscador if buscador is not None else _adm_busca(tid)
    h += filtros
    h += acciones
    h += "</div>"
    h += ('<div class="tabla-scroll"><table class="tabla" id="adm-%s">%s'
          "<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>"
          % (tid, cap, cab, body))
    h += ('<div data-vacio hidden>%s</div>'
          % estado_vacio("Sin resultados",
                         "No hay registros que coincidan con los filtros actuales.",
                         "", "checklist"))
    h += paginas(1, por_pagina, len(filas), tam=por_pagina, tabla_id=tid)
    h += extra
    h += "</div>"
    return h


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
    """Botón de acción de la bandeja de solicitudes (Aprobar/Rechazar)."""
    return ('<button data-accion="%s" title="%s" aria-label="%s">%s</button>'
            % (accion, etiqueta, etiqueta, ico(icono, 16)))


def _detalle(tipo, etiqueta="Ver detalle"):
    """Botón que abre el detalle de una fila (panel de solicitud)."""
    return ('<button class="table-act" data-adm-accion="%s" title="%s" '
            'aria-label="%s">%s</button>' % (tipo, etiqueta, etiqueta, ico("eye", 16)))


def _check(etiqueta, activo=False):
    """Casilla de verificacion (usa la clase .chk del kit)."""
    return ('<label class="chk"><input type="checkbox"%s> %s</label>'
            % (" checked" if activo else "", etiqueta))


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


# Datos que el JS del admin necesita en el ambito global: el kit compartido
# usa CORREOS_EST al asignar docente y aqui no existe (vive en Python), asi que
# se publica en la pagina del admin. Se agregan tambien las variantes sin
# tildes porque algunas bandejas escriben el nombre asi.
CORREOS_EST_JS = {}
for _nombre, _correo in CORREOS_EST.items():
    CORREOS_EST_JS[_nombre] = _correo
    CORREOS_EST_JS[_sin_tildes(_nombre)] = _correo

# [codigo, nombre, correo] de cada docente registrado, para el selector del
# modal de asignar/reasignar docente.
ADMIN_DOCENTES = [[d[0], d[1], d[2]] for d in DOCENTES]


def _inyectar(html):
    """Inyecta el JS propio del administrador (tablas, fichas, calendario) y los
    datos globales que el kit compartido espera."""
    if "</body>" in html:
        js = ("window.CORREOS_EST = %s;\nwindow.ADMIN_DOCENTES = %s;\n"
              % (json.dumps(CORREOS_EST_JS, ensure_ascii=False),
                 json.dumps(ADMIN_DOCENTES, ensure_ascii=False)))
        js += _js_admin()
        html = ("<script>" + js + "</script>\n</body>").join(
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
    """Inicio del admin: panorama con los datos reales del programa.

    El grafico de sede trae dos vistas (barras y anillo) que se alternan con
    el interruptor de la tarjeta; el cambio lo lleva ADMIN_JS."""
    por_sede = [(s, sum(1 for e in EMPRENDIMIENTOS if e[10] == s)) for s in SEDES]
    por_sector = []
    for s in ["Alimentos", "Moda", "Ambiental", "Tecnología", "Muebles"]:
        n = sum(1 for e in EMPRENDIMIENTOS if e[4] == s)
        if n:
            por_sector.append((s, n))
    activos = sum(1 for d in DOCENTES if d[6] == "Activo")
    prom = round(sum(e[7] for e in EMPRENDIMIENTOS) / float(len(EMPRENDIMIENTOS)))
    cuerpo = metricas([
        ("users", "Usuarios activos", str(activos + len(ESTUDIANTES)), "", 84, "+12 este mes"),
        ("maleta", "Emprendimientos", str(len(EMPRENDIMIENTOS)), "", 72, "+5"),
        ("trend", "Tareas del programa", str(len(TAREAS_ADM)), "", 88, "+14"),
        ("medalla", "Avance promedio", str(prom), "%", prom, "+3"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Avance de fase por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [12, 19, 27, 41, 61],
        unidad=" avances"))
    cuerpo += card("Emprendimientos por sede",
                   '<div data-grafico-vista="barras">%s</div>'
                   '<div data-grafico-vista="anillo" hidden>%s</div>'
                   % (barras("", "", [s.replace("Sede ", "") for s, _ in por_sede],
                             [n for _, n in por_sede], unidad=" ventures", alto=200),
                      donut("", "", [(s, n, AZUL) for s, n in por_sede],
                            "emprendimientos")),
                   accion=('<div class="acciones" role="group" aria-label="Tipo de gráfico">'
                           '<button class="btn btn-sm btn-acento" data-adm-grafico="barras">Barras</button>'
                           '<button class="btn btn-sm btn-secundario" data-adm-grafico="anillo">Anillo</button>'
                           '</div>'))
    cuerpo += card("Emprendimientos por sector", barras_h(
        "", "", [s for s, _ in por_sector], [n for _, n in por_sector], color=AMAR))
    cuerpo += card("Actividad reciente (Agenda)", agenda([
        ("12 nov 2024, 08:30 – Asesoría", [("08:30", "EcoPack - Carlos Mendoza", "", "")]),
        ("12 nov 2024, 11:00 – Evento", [("11:00", "Taller de costos - Confirmado", "", "")]),
        ("11 nov 2024, 15:00 – Comentario", [("15:00", "Pendiente de moderación", "", "")]),
    ]) + _vacio(".ag-ev", "Sin actividad programada",
                "Cuando haya asesorías, eventos o comentarios pendientes "
                "aparecerán aquí con su fecha y hora.", "calendar"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Calendario", calendario("noviembre", 2024, hoy=12, marcados=(18, 22),
                                       eventos={18: ("Taller de costos y precios",
                                                  "Auditorio A – 32 de 40 cupos – Publicado"),
                                              22: ("Feria de emprendedores",
                                                  "Plaza central – 86 de 120 cupos – Publicado")}))
    cuerpo += card("Pendientes de decisión", lista_def([
        ("<a href='asignaciones.html'>Emprendimientos sin docente</a>",
         str(sum(1 for e in EMPRENDIMIENTOS if e[8] == "Sin asignar"))),
        ("<a href='eventos.html'>Eventos por aprobar</a>", "1"),
        ("<a href='diagnosticos.html'>Diagnósticos sin revisar</a>", "5"),
    ]))
    cuerpo += card("Distribución de usuarios", donut(
        "", "", [("Docentes", len(DOCENTES), AZUL),
                 ("Estudiantes", len(ESTUDIANTES), AMAR)], "usuarios"))
    cuerpo += "</div></div>"
    cuerpo = formulario("dashboard", cuerpo)
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama institucional de usuarios, emprendimientos y seguimiento.",
                 extra_head=ADMIN_CSS,
                 acciones=_btn("download", "Exportar reportes", "reportes.html"))
# --- 34. Gestión de perfiles -------------------------------------------------
def usuarios():
    """Gestión de perfiles: docentes y estudiantes en tablas propias.

    Cada tabla tiene su buscador, sus filtros y su paginacion: el kit
    compartido solo resuelve una tabla por pagina, asi que aqui cada zona
    la lleva el controlador del admin (ADMIN_JS)."""
    filas_doc = []
    for cod, nom, correo, area, carga, emp, estado in DOCENTES:
        filas_doc.append({
            "attrs": {"doc-id": cod, "doc-cod": cod, "doc-nombre": nom, "doc-correo": correo,
                      "doc-area": area, "doc-carga": carga,
                      "doc-emp": emp, "doc-estado": estado},
            "celdas": [
                "<b>%s</b>" % cod, "<b>%s</b>" % nom, correo, area,
                carga, emp,
                (_sel_estado(cod, nom, estado), estado),
                _acc(_ficha("docente"),
                     '<button data-accion="editar-docente" title="Editar docente" '
                     'aria-label="Editar docente">%s</button>' % ico("edit", 16)
                     + '<button data-accion="dar-de-baja" title="Dar de baja" '
                     'aria-label="Dar de baja a %s">%s</button>' % (nom, ico("trash", 16))),
            ],
        })
    filas_est = []
    for cod, nom, sec, emp, et, av, est in ESTUDIANTES:
        filas_est.append({
            "attrs": {"est-id": cod, "est-nombre": nom,
                      "est-correo": CORREOS_EST.get(nom, ""), "est-sector": sec,
                      "est-emp": emp, "est-etapa": et, "est-sede": SEDE_EST.get(nom, ""),
                      "est-avance": "%d%%" % av, "est-estado": est},
            "celdas": [
                "<b>%s</b>" % cod, "<b>%s</b>" % nom, CORREOS_EST.get(nom, ""),
                sec, emp, badge(et, "b-linea"), _barra(av),
                (_sel_estado(cod, nom, est), est),
                _acc(_ficha("estudiante"),
                     '<button data-accion="editar-estudiante" title="Editar estudiante" '
                     'aria-label="Editar estudiante">%s</button>' % ico("edit", 16)
                     + '<button data-accion="dar-de-baja" title="Dar de baja" '
                     'aria-label="Dar de baja a %s">%s</button>' % (nom, ico("trash", 16))),
            ],
        })
    cuerpo = callout("Los perfiles de estudiante se editan desde su cuenta. El "
                     "administrador solo puede cambiar el estado de acceso (Activo, "
                     "Limitado o Inactivo).", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("users", "Docentes", str(len(DOCENTES)), "", 45, "+1"),
        ("users", "Estudiantes", str(len(ESTUDIANTES)), "", 92, "+11"),
        ("alerta", "Cuentas inactivas", "4", "", 12, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "docentes", "Docentes",
        ["Código", "Nombre", "Correo institucional", "Área", "Carga semanal",
         "Emprendimientos", "Estado", "@ACC"], filas_doc,
        sub="Docentes registrados en el programa y su carga asignada.",
        caption="Docentes registrados en el programa",
        filtros=(_adm_filtro("docentes", "Todas las áreas",
                             ["Todas las áreas", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("docentes", "Todos los estados",
                               ["Todos los estados", "Activo", "Limitado", "Inactivo"], 6)),
        acciones=_nuevo("nuevo-docente", "Nuevo docente"))
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "estudiantes", "Estudiantes",
        ["ID de estudiante", "Nombre", "Correo institucional", "Sector",
         "Emprendimiento", "Etapa", "Avance", "Estado", "@ACC"], filas_est,
        sub="Estudiantes vinculados a un emprendimiento del programa.",
        caption="Estudiantes registrados en el programa",
        filtros=(_adm_filtro("estudiantes", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("estudiantes", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 5)
                 + _adm_filtro("estudiantes", "Todos los estados",
                               ["Todos los estados", "Activo", "Limitado", "Inactivo"], 7)),
        acciones=_nuevo("nuevo-estudiante", "Nuevo estudiante"))
    cuerpo += '<div id="form-docente" hidden>' + _cuerpo_docente() + "</div>"
    cuerpo += '<div id="form-estudiante" hidden>' + _cuerpo_estudiante() + "</div>"
    cuerpo += '<div id="form-nuevo-docente" hidden>' + _cuerpo_nuevo_docente() + "</div>"
    cuerpo += '<div id="form-nuevo-estudiante" hidden>' + _cuerpo_nuevo_estudiante() + "</div>"
    cuerpo = formulario("perfiles", cuerpo)
    return shell(R, "usuarios", "Gestión de perfiles", cuerpo,
                 migas=["Inicio", "Gestión de perfiles"],
                 sub="Altas, edición y estado de acceso de docentes y estudiantes.",
                 extra_head=ADMIN_CSS)


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
                   campo("Código", valor="912646", bloqueo="Código asignado por el sistema")
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
    filas = []
    for c, n, r, m, f in SOLIC_DESBLOQUEOS:
        filas.append({
            "attrs": {"sol-id": c, "sol-nombre": n, "sol-tipo": r,
                      "sol-detalle": m, "sol-fecha": f,
                      "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % c, "<b>%s</b>" % n, badge(r, "b-linea"), m, f,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle"))],
        })
    return _tabla_adm(
        "desbloqueos", "Desbloqueos de cuenta",
        ["Código", "Nombre", "Rol", "Motivo de la solicitud", "Fecha", "@ACC"],
        filas, sub="Cuentas bloqueadas o inactivas que esperan una decisión.",
        caption="Solicitudes de desbloqueo de cuenta",
        por_pagina=5)


def _cuerpo_par():
    filas = []
    for c, n, emp, nu, s, f in SOLIC_PARALELOS:
        filas.append({
            "attrs": {"sol-id": c, "sol-nombre": n, "sol-tipo": "Emprendimiento paralelo",
                      "sol-detalle": "Pasa de %s a %s (sector %s)." % (emp, nu, s),
                      "sol-fecha": f, "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % c, "<b>%s</b>" % n, emp, "<b>%s</b>" % nu, s, f,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle"))],
        })
    return _tabla_adm(
        "paralelos", "Emprendimientos en paralelo",
        ["ID de estudiante", "Estudiante", "Emprendimiento actual",
         "Nuevo emprendimiento", "Sector", "Fecha", "@ACC"], filas,
        sub="Estudiantes que quieren registrar un segundo emprendimiento.",
        caption="Solicitudes de emprendimiento en paralelo",
        por_pagina=5)


def _cuerpo_cit():
    filas = []
    for n, e, d, f, m in SOLIC_CITAS:
        cid = _id_estudiante(n)
        filas.append({
            "attrs": {"sol-id": cid, "sol-nombre": n,
                      "sol-tipo": "Cita de asesoria",
                      "sol-detalle": "%s, docente sugerido: %s." % (m, d),
                      "sol-fecha": f, "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % cid, "<b>%s</b>" % n, e, d, f, m,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle"))],
        })
    return _tabla_adm(
        "citas", "Citas de asesoria",
        ["ID de estudiante", "Estudiante", "Emprendimiento", "Docente sugerido",
         "Fecha propuesta", "Motivo", "@ACC"], filas,
        sub="Citas de asesoria propuestas por los estudiantes.",
        caption="Solicitudes de cita de asesoria",
        por_pagina=5)


def solicitudes():
    """Bandeja unica del Admin: desbloqueos de cuenta, paralelos y citas.

    Cada bandeja es una tabla propia del admin (buscador, filtros y
    paginacion) y el boton de detalle abre el panel con la descripcion
    completa de la solicitud."""
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
        ("calendar", "Citas de asesoria", str(len(SOLIC_CITAS)), "", 20, None),
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
                 sub="Bandeja de desbloqueos de cuenta, solicitudes de paralelo y citas de asesoria.",
                 extra_head=ADMIN_CSS)


# --- 37. Emprendimientos -----------------------------------------------------
def emprendimientos():
    """Registro maestro del admin: la tabla canonica, con buscador, filtros
    por columna, paginacion propia y ficha de cada entrepreneurial."""
    cuerpo = callout("Como administrador tu ves <b>todos</b> los emprendimientos, "
                     "tengan o no docente asignado.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("maleta", "Total", str(len(EMPRENDIMIENTOS)), "", 72, "+5"),
        ("trend", "En fase 3 o 4", "18", "", 62, None),
        ("alerta", "Sin docente", str(sum(1 for e in EMPRENDIMIENTOS
                                          if e[8] == "Sin asignar")), "", 18, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    filas = []
    for cod, emp, estu, correo_est, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS:
        est_id = _id_estudiante(estu)
        filas.append({
            "attrs": {"cod": cod, "emp": emp, "estu": estu,
                      "emp-id": cod, "emp-cod": cod, "emp-nombre": emp, "emp-est-id": est_id,
                      "emp-est-nombre": estu, "emp-est-correo": correo_est,
                      "emp-sector": sector, "emp-tipo": tipo, "emp-etapa": etapa,
                      "emp-avance": "%d%%" % avance, "emp-sede": sede,
                      "emp-docente": docente},
            "celdas": [
                "<b>%s</b>" % emp, cod, est_id, estu, correo_est,
                badge(sector, "b-azul" if sector == "Alimentos" else
                      ("b-linea" if sector == "Ambiental" else "b-neutra")),
                tipo, badge(etapa, "b-linea"), _barra(avance), sede,
                docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
                _acc(_ficha("emprendimiento"),
                     _revisar(cod, emp, estu, sector, tipo, etapa, docente),
                     '<a class="table-act" href="emprendimiento-plan.html" '
                     'title="Abrir plan" aria-label="Abrir plan">%s</a>' % ico("eye", 16),
                     '<a class="table-act" href="emprendimiento-expediente.html" '
                     'title="Abrir expediente" aria-label="Abrir expediente">%s</a>'
                     % ico("carpeta", 16),
                     _emp("editar-emprendimiento", "edit", "Editar emprendimiento",
                          cod=cod, emp=emp, estu=estu, sector=sector, tipo=tipo,
                          etapa=etapa, avance=str(avance), docente=docente)),
            ],
        })
    cuerpo += _tabla_adm(
        "emprendimientos", "Emprendimientos",
        ["Emprendimiento", "Código", "ID de estudiante", "Estudiante",
         "Correo institucional", "Sector", "Tipo", "Etapa", "Avance", "Sede",
         "Docente asignado", "@ACC"], filas,
        sub="Registro maestro de emprendimientos del programa.",
        caption="Emprendimientos registrados en el programa",
        filtros=(_adm_filtro("emprendimientos", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 5)
                 + _adm_filtro("emprendimientos", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 7)
                 + _adm_filtro("emprendimientos", "Todas las sedes",
                               ["Todas las sedes"] + SEDES, 9)))
    cuerpo += '<div id="form-emprendimiento" hidden>' + _cuerpo_emprendimiento() + "</div>"
    cuerpo = formulario("emprendimientos", cuerpo)
    return shell(R, "emprendimientos", "Emprendimientos", cuerpo,
                 migas=["Inicio", "Emprendimientos"],
                 sub="Todos los emprendimientos registrados en el programa.",
                 extra_head=ADMIN_CSS,
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
                 + "</div>")

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
        ("Mariana López", "912646 · Sede Norte"),
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
    """Seguimiento de todos los undertakings con filtros por columna,
    paginacion propia y ficha de cada uno."""
    filas = []
    for cod, emp, estu, correo_est, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS:
        est_id = _id_estudiante(estu)
        filas.append({
            "attrs": {"cod": cod, "emp": emp, "estu": estu, "etapa": etapa,
                      "avance": str(avance),
                      "emp-id": cod, "emp-cod": cod, "emp-nombre": emp, "emp-est-id": est_id,
                      "emp-est-nombre": estu, "emp-est-correo": correo_est,
                      "emp-sector": sector, "emp-tipo": tipo, "emp-etapa": etapa,
                      "emp-avance": "%d%%" % avance, "emp-sede": sede,
                      "emp-docente": docente},
            "celdas": [
                cod, "<b>%s</b>" % emp, estu,
                badge(sector, "b-azul" if sector == "Alimentos" else "b-neutra"),
                badge(etapa, "b-linea"),
                docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
                _barra(avance), _sem(avance),
                _acc(_ficha("emprendimiento"),
                     _b("eye", "Ver detalle", "ver-detalle"),
                     _avance("registrar-avance", "edit", "Registrar avance",
                             cod=cod, emp=emp, estu=estu, etapa=etapa,
                             docente=docente, avance=avance)),
            ],
        })
    cuerpo = _tabla_adm(
        "seguimiento", "Seguimiento de emprendimientos",
        ["Código", "Emprendimiento", "Estudiante", "Sector", "Etapa",
         "Docente", "Avance", "Estado", "@ACC"], filas,
        sub="Estado y avance de los %d emprendimientos del programa."
            % len(EMPRENDIMIENTOS),
        caption="Seguimiento de emprendimientos",
        filtros=(_adm_filtro("seguimiento", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("seguimiento", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 4)
                 + _adm_filtro("seguimiento", "Todos los docentes",
                               ["Todos los docentes"] + [d[1] for d in DOCENTES]
                               + ["Sin asignar"], 5)
                 + _adm_filtro("seguimiento", "Todo el estado",
                               ["Todo el estado", "Al día", "En riesgo", "Sin avance"], 7)),
        acciones=_exportar("Exportar seguimiento"))
    cuerpo += '<div id="form-avance" hidden>' + _cuerpo_avance() + "</div>"
    cuerpo = formulario("seguimiento", cuerpo)
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Estado y avance de los %d emprendimientos del programa."
                     % len(EMPRENDIMIENTOS),
                 extra_head=ADMIN_CSS,
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
        "", "", [e[1] for e in EMPRENDIMIENTOS], [e[7] for e in EMPRENDIMIENTOS],
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
        ("Asignar docente a 1 emprendimiento", "Sin asignar"),
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
# --- 46. Asignaciones: hoja de pagina y modal de asignacion ----------------
# El boton de la tabla pasa de icono 32x32 a btn-sm con texto al confirmar
# (evita el desborde) y la hoja anade el margen/nowrap que lo contiene.
HOJA_BTN_REASIGNAR = "\ntable.tabla .acc .btn{margin-left:4px;white-space:nowrap;max-width:100%;width:auto;min-width:0;padding:0 12px;justify-content:center;height:32px;flex:0 0 auto}"
JS_ASIGNAR_DOCENTE = r"""
/* Asignar/reasignar docente: modal inline que lee y escribe los dataset de la
   fila. Al confirmar, el boton se vuelve btn-sm con el texto "Reasignar
   docente" (antes solo tenia el icono y desbordaba la celda). */
document.querySelector("#vista-asignaciones").addEventListener("click", function (event) {
  var button = event.target.closest("[data-accion='asignar-docente-inline']");
  if (!button) return;
  var fila = button.closest("tr");
  var actual = fila.dataset.docente || "Sin docente asignado";
  var docentes = (function () {
    var vistos = {};
    var nombres = [];
    document.querySelectorAll("table.tabla tbody tr").forEach(function (tr) {
      var n = (tr.dataset.docente || "").trim();
      if (n && n !== "Sin docente" && !vistos[n]) { vistos[n] = 1; nombres.push(n); }
    });
    return nombres;
  })();
  var opciones = docentes.map(function (d) {
    var sel = d === actual ? " selected" : "";
    return "<option" + sel + ">" + d + "</option>";
  }).join("");
  var velo = document.createElement("div");
  velo.className = "modal-velo";
  velo.innerHTML = '<div class="modal" role="dialog" aria-modal="true" aria-label="Asignar docente"><div class="modal-head"><h2>' +
    (actual === "Sin docente asignado" ? "Asignar docente" : "Reasignar docente") + '</h2><button class="icon-btn modal-x" aria-label="Cerrar">\u00d7</button></div>' +
    '<div class="modal-cuerpo"><p><b>Proyecto:</b> ' + fila.dataset.proyecto + '<br><b>Estudiante:</b> ' + fila.dataset.estudiante + '</p>' +
    '<div class="campo"><label for="docente-asignacion">Docente registrado</label><select id="docente-asignacion">' + opciones + '</select></div>' +
    '<p class="modal-aviso">La confirmaci\u00f3n actualizar\u00e1 el docente visible en esta tabla.</p></div><div class="modal-foot"><button class="btn btn-secundario modal-cancelar">Cancelar</button><button class="btn btn-primario modal-confirmar">Confirmar asignaci\u00f3n</button></div></div>';
  document.body.appendChild(velo);
  function cerrar() { velo.remove(); document.body.classList.remove("sin-scroll"); }
  document.body.classList.add("sin-scroll");
  velo.querySelector(".modal-x").addEventListener("click", function (e) { e.stopPropagation(); cerrar(); });
  velo.querySelector(".modal-cancelar").addEventListener("click", function (e) { e.stopPropagation(); cerrar(); });
  velo.querySelector(".modal-confirmar").addEventListener("click", function (e) {
    e.stopPropagation();
    var docente = velo.querySelector("#docente-asignacion").value;
    fila.dataset.docente = docente.split(" \u2014 ")[0];
    fila.cells[3].textContent = fila.dataset.docente;
    fila.cells[4].innerHTML = '<span class="badge b-azul">Asignado</span>';
    button.className = "btn btn-sm btn-secundario";
    button.textContent = "Reasignar docente";
    button.title = "Reasignar docente";
    button.setAttribute("aria-label", "Reasignar docente");
    cerrar();
    if (typeof toast === "function") toast("Docente asignado correctamente", "ok");
  });
});
"""


def _cuerpo_asignar_docente():
    """Plantilla del modal de asignar/reasignar docente.

    Vive oculta en la pantalla de Asignaciones; el JS la clona, la rellena con
    los data-* de la fila y abre el modal con ella."""
    opciones = "".join('<option value="%s">%s · %s</option>' % (d[1], d[1], d[2])
                       for d in DOCENTES)
    return (
        '<div class="grid">'
        + '<div class="campo"><label for="asg-estudiante">Estudiante</label>'
          '<input id="asg-estudiante" name="estudiante" type="text" disabled></div>'
        + '<div class="campo"><label for="asg-emprendimiento">Emprendimiento</label>'
          '<input id="asg-emprendimiento" name="emprendimiento" type="text" disabled></div>'
        + '<div class="campo"><label for="asg-correo">Correo</label>'
          '<input id="asg-correo" name="correo" type="text" disabled></div>'
        + "</div>"
        + '<div class="grid g-2">'
        + '<div class="campo"><label for="docente-asignacion">Docente registrado</label>'
          '<select id="docente-asignacion" name="docente">'
          '<option value="">Sin asignar</option>' + opciones + "</select></div>"
        + '<div class="campo"><label for="asg-horas">Horas semanales</label>'
          '<input id="asg-horas" name="horas" type="number" value="2" min="1" max="20">'
          "</div>"
        + "</div>"
        + '<p class="modal-aviso">La confirmación actualizará el docente visible '
          "en esta tabla.</p>"
    )


def asignaciones():
    """Asignaciones de docente a emprendimiento.

    Mantiene la estructura ya aprobada en el prototipo (regla de asignacion,
    tres metricas y la tabla "Estudiantes y emprendimientos"), pero los tres
    filtros los resuelve el controlador del admin (data-filtro-adm) en vez de
    un script suelto, y la fila lleva los datos que necesita el modal de
    reasignacion."""
    filas = []
    for cod, emp, estu, correo, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS[:5]:
        est_id = _id_estudiante(estu)
        sin_doc = docente == "Sin asignar"
        estado = (badge("Sin asignar", "b-neutra", "alerta") if sin_doc
                  else badge("Asignado", "b-azul", "check"))
        etiqueta = "Asignar docente" if sin_doc else "Reasignar docente"
        filas.append({
            "attrs": {"correo": correo, "proyecto": emp, "estudiante": estu,
                      "docente": docente, "cod": cod, "col-docente": 3},
            "celdas": [
                "<b>%s</b><small class=\"nota-foot\">%s</small>" % (emp, cod),
                "<b>%s</b><small class=\"nota-foot\">%s</small><small class=\"nota-foot\">%s</small>"
                % (estu, est_id, correo),
                sector,
                docente if not sin_doc else "Sin docente asignado",
                estado,
                ('<div class="acciones-cell"><button class="table-act" '
                 'data-adm-accion="reasignar" title="%s" aria-label="%s">%s</button></div>'
                 % (etiqueta, etiqueta, ico("edit", 16))),
            ],
        })
    cab = "".join(th(c) for c in ["Proyecto", "Estudiante", "Sector",
                                  "Docente asignado", "Estado", "@ACC"])
    eti = [_etiqueta(c) for c in ["Proyecto", "Estudiante", "Sector",
                                  "Docente asignado", "Estado", "@ACC"]]
    body = ""
    for fila in filas:
        attrs = "".join(' data-%s="%s"' % (k, v)
                        for k, v in fila["attrs"].items() if v)
        celdas = ""
        for e, x in zip(eti, fila["celdas"]):
            if e == "Acciones":
                celdas += '<td class="acc" data-label="%s">%s</td>' % (e, x)
            else:
                celdas += '<td data-label="%s">%s</td>' % (e, x)
        body += "<tr%s>%s</tr>" % (attrs, celdas)
    cuerpo = callout(
        "<b>Regla de asignación:</b> verifica que el acta de confidencialidad esté "
        "aceptada antes de confirmar una asignación definitiva. Un docente puede "
        "tener hasta <b>12 emprendimientos</b>.", "alerta")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-4">'
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Asignaciones vigentes</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra"><span style="width:%d%%"></span></div></div>'
               % (ico("check", 18), 4, 80))
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Sin docente</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra amarilla"><span style="width:%d%%"></span></div></div>'
               % (ico("alerta", 18), 1, 20))
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Docentes registrados</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra"><span style="width:%d%%"></span></div></div>'
               % (ico("users", 18), len(DOCENTES), 62))
    cuerpo += "</div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="card" data-tabla-zona="adm-asignaciones">'
    cuerpo += ('<div class="card-head"><div><h3>Estudiantes y emprendimientos</h3>'
               '<p class="sub">Busca por correo institucional o nombre del proyecto.</p>'
               '</div><span class="hint" data-resultados>%d resultados</span></div>'
               % len(filas))
    cuerpo += '<div class="toolbar">'
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-correo">'
               'Correo del estudiante</label><input id="filtro-correo" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="1" '
               'type="text" placeholder="estudiante@sgemd.edu.co" autocomplete="off">'
               '</div>')
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-proyecto">'
               'Nombre del proyecto</label><input id="filtro-proyecto" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="0" '
               'type="text" placeholder="Ej. Sabor y Sabe" autocomplete="off"></div>')
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-docente">'
               'Estado de asignación</label><select id="filtro-docente" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="4">'
               '<option value="">Todos</option><option value="asignado">Con docente</option>'
               '<option value="sin asignar">Sin docente</option></select></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="tabla-scroll"><table class="tabla"><thead><tr>%s</tr></thead>' \
              "<tbody>%s</tbody></table></div>" % (cab, body)
    cuerpo += ('<div data-vacio hidden>%s</div>'
               % estado_vacio("Sin resultados",
                              "No hay estudiantes que coincidan con los filtros actuales.",
                              "", "alerta"))
    cuerpo += "</div>"
    # Plantilla del modal de asignar/reasignar docente: vive oculta en la
    # pagina y el JS la clona al abrir el modal (data-adm-accion="reasignar").
    cuerpo += '<div id="form-asignar-docente" hidden>%s</div>' % _cuerpo_asignar_docente()
    cuerpo = formulario("asignaciones", cuerpo)
    return shell(R, "asignaciones", "Asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones"],
                 sub="Asigna docentes registrados a los emprendimientos y consulta "
                     "el estado actual del vínculo.",
                 extra_head=ADMIN_CSS,
                 acciones=_exportar("Exportar asignaciones"))


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
    ("Plan de marketing", "TechNova", "Camilo Rojas",
     "Alta", "20 nov 2024", "Pendiente"),
    ("Estudio de costos", "Aura Design", "Valentina Ortega",
     "Media", "21 nov 2024", "Completada"),
    ("Prototipo funcional", "BioEco", "Laura Martínez",
     "Alta", "22 nov 2024", "En revisión"),
    ("Menú y precios", "Gourmet Fresh", "Sebastián Torres",
     "Media", "23 nov 2024", "Pendiente"),
    ("MVP aplicación", "SmartApp", "Ana Restrepo",
     "Alta", "24 nov 2024", "Pendiente"),
    ("Validación mercado", "Urban Style", "Mateo Gómez",
     "Media", "25 nov 2024", "Pendiente"),
    ("Control de inventario", "WoodCraft", "Diego Peralta",
     "Baja", "26 nov 2024", "Pendiente"),
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
    """Tareas del admin: dos tablas propias (emprendimientos con tareas y
    tareas asignadas), cada una con buscador, filtros y paginacion."""
    filas_t = []
    for t, emp, estu, prio, vence, est in TAREAS_ADM:
        est_id = _id_estudiante(estu)
        filas_t.append({
            "attrs": {"est-id": est_id, "est-nombre": estu,
                      "est-correo": CORREOS_EST.get(estu, ""), "est-emp": emp,
                      "tarea-titulo": t, "tarea-prioridad": prio,
                      "tarea-vence": vence, "tarea-estado": est},
            "celdas": [
                "<b>%s</b>" % t, emp, estu, badge(prio, PRIO_ADM[prio]), vence,
                badge(est, ESTADO_TAREA_ADM[est]),
                _acc(_ficha("estudiante"),
                     _b("edit", "Editar", "editar-tarea"),
                     _b("trash", "Eliminar", "eliminar-tarea"))],
        })
    filas_emp = []
    for cod, emp, estu, etapa, n_tareas in (
            ("EMP-041", "Sabor y Sabe", "Mariana López", "FASE 2 - Prototipo", "2"),
            ("EMP-040", "Krea Textil", "Jhon Ospina", "FASE 1 - Ideación", "1"),
            ("EMP-039", "EcoPack", "Lucía Fernández", "FASE 3 - Validación", "1"),
            ("EMP-038", "Aromas del Sur", "Sofía Ramírez", "FASE 1 - Ideación", "1")):
        filas_emp.append({
            "attrs": {"emp-id": cod, "emp-cod": cod, "emp-nombre": emp,
                      "emp-est-id": _id_estudiante(estu), "emp-est-nombre": estu,
                      "emp-est-correo": CORREOS_EST.get(estu, ""),
                      "emp-etapa": etapa},
            "celdas": [
                cod, "<b>%s</b>" % emp, estu, badge(etapa, "b-linea"), n_tareas,
                _acc(_ficha("emprendimiento"),
                     _b("eye", "Ver tareas", "ver-tareas"))],
        })
    cuerpo = callout("Como administrador puedes <b>consultar, añadir y eliminar</b> "
                     "tareas de cualquier emprendimiento. La calificación de las "
                     "entregas la realiza el docente.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "emprendimientos-tareas", "Emprendimientos con tareas",
        ["Código", "Emprendimiento", "Estudiante", "Etapa", "Tareas", "@ACC"],
        filas_emp,
        sub="Emprendimientos del programa con tareas activas.",
        caption="Emprendimientos con tareas asignadas",
        filtros=_adm_filtro("emprendimientos-tareas", "Todas las etapas",
                             ["Todas las etapas"] + ETAPAS, 3))
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "tareas", "Tareas asignadas a estudiantes",
        ["Tarea", "Emprendimiento", "Estudiante", "Prioridad", "Vence",
         "Estado", "@ACC"], filas_t,
        sub="Tareas creadas por los docentes para sus estudiantes.",
        caption="Tareas asignadas a estudiantes",
        filtros=(_adm_filtro("tareas", "Todos los estados",
                             ["Todos los estados", "Pendiente", "En revisión",
                              "Completada", "Devuelta"], 5)
                 + _adm_filtro("tareas", "Toda la prioridad",
                               ["Toda la prioridad", "Alta", "Media", "Baja"], 3)),
        acciones=_nuevo("nueva-tarea", "Nueva tarea"))
    cuerpo += '<div id="form-tarea" hidden>' + _cuerpo_tarea_adm() + "</div>"
    cuerpo = formulario("tareas", cuerpo)
    return shell(R, "tareas", "Tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Consulta, alta y baja de tareas por emprendimiento.",
                 extra_head=ADMIN_CSS,
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


# --- 51. Configuracion del administrador --------------------------------------

def configuracion():
    """Configuracion del admin: cuenta, parametros del programa, sedes,
    notificaciones y bitacora de decisiones.

    Es la vista a la que lleva el mini-menu (que el kit arma como
    "Preferencias" y el JS del admin renombra a "Configuracion")."""
    sin_doc = sum(1 for e in EMPRENDIMIENTOS if e[8] == "Sin asignar")
    cuerpo = callout(
        "Los cambios de esta pantalla aplican a todo el programa: sedes, etapas, "
        "cupos y reglas de asignación.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Cuenta del administrador",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Nombres", valor="Ana", req=True)
                   + campo("Apellidos", valor="Restrepo", req=True)
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Correo institucional", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Teléfono", tipo="tel", valor="+57 301 555 0199")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Cargo", valor="Administradora del programa",
                           bloqueo="El cargo lo asigna la institución")
                   + campo("Sede principal", valor="Sede Norte")
                   + "</div>"
                   + '<div class="fila-fin">'
                   + '<button class="btn btn-secundario" data-accion="cancelar-perfil">'
                     "Cancelar</button>"
                   + '<button class="btn btn-primario" data-accion="guardar-perfil">%s '
                     "Guardar cambios</button></div>" % ico("check", 16))
    cuerpo += card("Parámetros del programa",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Carga máxima por docente (horas)", tipo="number", valor="12")
                   + campo("Emprendimientos máximos por docente", tipo="number", valor="12")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + select("Sede por defecto", SEDES, valor="Sede Norte")
                   + select("Etapa inicial del programa", ETAPAS,
                            valor="FASE 1 - Ideación")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Fecha de cierre de admisiones", tipo="date",
                           valor="2024-12-15")
                   + campo("Cupos por sede", tipo="number", valor="40")
                   + "</div>"
                   + '<p class="nota-foot">Hoy hay %d emprendimientos sin docente '
                     'asignado: la cola se resuelve desde Asignaciones.</p>' % sin_doc)
    cuerpo += card("Notificaciones automáticas",
                   '<div class="fila-col">'
                   + _check("Aviso de solicitud de desbloqueo", True)
                    + _check("Aviso de emprendimiento en paralelo", True)
                   + _check("Aviso de tarea vencida", True)
                   + _check("Resumen semanal al equipo docente", False)
                   + "</div>"
                   + '<p class="nota-foot">Los avisos se envían al correo '
                     "institucional de cada docente y estudiante.</p>")
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Sedes del programa", tabla(
        ["Sede", "Emprendimientos", "Estudiantes", "Estado"],
        [[s,
          str(sum(1 for e in EMPRENDIMIENTOS if e[10] == s)),
          str(sum(1 for e in ESTUDIANTES
                  if any(x[10] == s for x in EMPRENDIMIENTOS
                         if x[2] == e[1]))),
          badge("Activa", "b-azul")] for s in SEDES],
        caption="Sedes del programa"))
    cuerpo += card("Cambiar contraseña",
                   '<div class="grid g-3 g-col">'
                   + campo("Contraseña actual", tipo="password", ph="••••••••")
                   + campo("Nueva contraseña", tipo="password", ph="Mínimo 8 caracteres")
                   + campo("Repetir nueva contraseña", tipo="password", ph="••••••••")
                   + "</div>"
                   '<div style="display:flex;justify-content:flex-end">'
                   + '<button class="btn btn-secundario" data-accion="actualizar-contrasena">'
                     "%s Actualizar contraseña</button></div>" % ico("lock", 16))
    cuerpo += card("Bitácora de decisiones",
                   lista_def([
                       ("Aprobación de desbloqueo de cuenta",
                        "05 nov 2024 · 912651 · Camilo.rojas@sgemd.edu.co"),
                       ("Cambio de docente asignado",
                        "04 nov 2024 · EMP-039 · EcoPack · Paula Andrea Rios → Hector Vargas"),
                       ("Reactivación de cuenta inactiva",
                        "02 nov 2024 · DOC-011 · Ninafq Beltran"),
                   ]) + _vacio(".def-row", "Sin decisiones registradas",
                               "Las aprobaciones, rechazos y cambios de docente "
                               "quedan registrados aquí.", "checklist"))
    cuerpo += "</div></div>"
    cuerpo = formulario("configuracion", cuerpo)
    return shell(R, "configuracion", "Configuración", cuerpo,
                 migas=["Inicio", "Configuración"],
                 sub="Parámetros del programa, sedes, notificaciones y bitácora.",
                 extra_head=ADMIN_CSS)


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
            ("08:15", "1 emprendimiento sigue sin docente",
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
        ("configuracion.html", "21 Admin - Configuración", configuracion),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_adm):
        reg("admin", arch, tit, _envolver(fn), i)
