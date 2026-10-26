# -*- coding: utf-8 -*-
"""Rol DOCENTE - 23 pantallas.

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
from urllib.parse import quote_plus

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, lista_avisos,
    tarjeta_emp, kanban, agenda, linea_tiempo, tabs_paneles, calendario,
    calendario_interactivo,
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
    # Un .tabs/.pest hijo directo de un .grid se estiraba a todo el alto de la
    # fila del grid (335-380 px de alto en escritorio). Con align-self:start
    # recupera su alto natural (39 px) sin tocar el CSS compartido.
    ".grid > .tabs,.grid > .pest{align-self:start;margin-bottom:0}"
    ".pila-exp{display:flex;flex-direction:column;gap:20px;min-width:0}"
    # Pestanas de ambito local (selector de estudiante y expediente). No llevan
    # la clase .tabs para que el kit no las trate como pestanas globales.
    ".pest{display:flex;gap:4px;border-bottom:1px solid var(--gris);"
    "margin-bottom:20px;overflow-x:auto}"
    ".pest button{background:transparent;border:none;border-bottom:2px solid "
    "transparent;padding:10px 14px;font-family:var(--sans);font-size:14px;"
    "font-weight:600;color:var(--tinta-2);cursor:pointer;white-space:nowrap}"
    ".pest button.activo{color:var(--azul-real);border-bottom-color:var(--azul-real)}"
    ".celda-sub{font-size:12px;color:var(--tinta-2);margin-top:2px}"
    ".diag-contexto{display:block}"
    ".aviso.leida{opacity:.6}"
    ".aviso.leida .aviso-titulo{font-weight:600}"
    # Tarjetas de Inicio: la vista previa y el enlace los aporta el kit
    # (.metrica-enlace/.mini-prev). Aqui solo se agrega la flecha visible y la
    # nota inferior, sin tocar los estilos compartidos.
    ".metrica-flecha{margin-left:auto;flex:0 0 26px;width:26px;height:26px;"
    "border-radius:50%;display:flex;align-items:center;justify-content:center;"
    "color:var(--azul-real);background:var(--azul-08);"
    "transition:background .15s ease,color .15s ease,transform .15s ease}"
    ".metrica-enlace:hover .metrica-flecha,.metrica-enlace:focus-visible "
    ".metrica-flecha{background:var(--azul-real);color:var(--blanco);"
    "transform:translateX(2px)}"
    ".metrica-nota{margin-top:10px;font-size:13px;font-weight:600;"
    "color:var(--tinta-2)}"
    "@media (prefers-reduced-motion:reduce){.metrica-flecha{transition:none}}"
    "@media (max-width:479px){.acciones-rapidas{grid-template-columns:minmax(0,1fr)}}"
)

DOCENTE_JS = """
(function () {
  "use strict";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  var GUARDAR = {
    "guardar-avance": "Avance registrado",
    "guardar-calificacion": "Calificación guardada",
    "devolver-tarea": "Tarea devuelta al estudiante",
    "asignar-tarea": "Tarea asignada",
    "generar-asesoria": "Asesoría generada",
    "confirmar-asesoria": "Asesoría confirmada",
    "reprogramar-asesoria": "Nueva fecha propuesta",
    "rechazar-asesoria": "Solicitud rechazada",
    "guardar-recomendaciones": "Recomendaciones guardadas"
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
    no.addEventListener("click", function (e) { e.stopPropagation(); cerrarModal(); });
    var si = document.createElement("button");
    si.className = "btn btn-peligro";
    si.textContent = "Confirmar";
    si.addEventListener("click", function (e) {
      e.stopPropagation();
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

  /* Emprendimientos asignados: el selector de estudiante queda justo encima de
     la tabla; al elegir un estudiante se sustituye la tabla por las pestanas de
     sus emprendimientos (uno por emprendimiento). */
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
          var t = $(".pest button", sec);
          if (t) t.click();
        }
      }
    };
    selEst.addEventListener("change", pintar);
    if (selEst.value) pintar();
  }

  /* Expediente: cada emprendimiento tiene su propia seccion ya renderizada.
     El enlace llega con ?emp=<slug> y aqui se muestra solo la que corresponde
     (el titulo, el breadcrumb y la pestana del navegador acompanan). */
  (function () {
    var secs = $$("[data-exp-perfil]");
    if (!secs.length) return;
    var m = location.search.match(/[?&]emp=([^&]+)/);
    var clave = m ? decodeURIComponent(m[1]) : "";
    var hay = secs.filter(function (s) {
      return s.getAttribute("data-exp-perfil") === clave;
    })[0];
    if (!hay) hay = secs[0];
    secs.forEach(function (s) { s.hidden = s !== hay; });
    var nombre = hay.getAttribute("data-exp-nombre") || "";
    var h1 = $("main h1");
    if (h1 && nombre) h1.textContent = nombre;
    var miga = $(".crumbs b");
    if (miga && nombre) miga.textContent = nombre;
    if (nombre) document.title = nombre + " — SGEMD";
  })();

  /* Inicio: calendario de compromisos. Al hacer clic en un dia cambia el panel
     visible; el dia de hoy queda seleccionado al cargar la pagina. */
  var calDoc = $("[data-cal-doc]");
  if (calDoc) {
    var celdas = $$("[data-dia]", calDoc);
    var paneles = $$("[data-dia-panel]", calDoc);
    var rotulo = $("[data-dia-titulo]", calDoc);
    var verDia = function (dia, etiqueta) {
      celdas.forEach(function (c) {
        var es = c.getAttribute("data-dia") === dia;
        c.classList.toggle("activo", es);
        c.setAttribute("aria-pressed", es ? "true" : "false");
      });
      var hay = false;
      paneles.forEach(function (p) {
        if (p.getAttribute("data-dia-panel") === dia) hay = true;
      });
      paneles.forEach(function (p) {
        var k = p.getAttribute("data-dia-panel");
        p.hidden = hay ? (k !== dia) : (k !== "sin");
      });
      if (rotulo) rotulo.textContent = etiqueta || ("Dia " + dia);
    };
    celdas.forEach(function (c) {
      c.addEventListener("click", function () {
        verDia(c.getAttribute("data-dia"), c.getAttribute("data-etiqueta"));
      });
    });
    var hoyCal = $('[data-dia="' + calDoc.getAttribute("data-hoy") + '"]', calDoc);
    if (hoyCal) {
      verDia(calDoc.getAttribute("data-hoy"), hoyCal.getAttribute("data-etiqueta"));
    }
  }

  /* Recomendar evento: el selector por emprendimiento marca (o quita) a todo el
     grupo; la seleccion individual se puede ajustar despues. */
  var rec = $("[data-recomendar]");
  if (rec) {
    var selGrupo = $("[data-recomendar-grupo]", rec);
    var chks = $$("input[type=checkbox][data-est]", rec);
    if (selGrupo) {
      selGrupo.addEventListener("change", function () {
        var g = selGrupo.value;
        chks.forEach(function (c) {
          var emps = (c.getAttribute("data-emp") || "").split("|");
          if (g === "__todos__") c.checked = true;
          else if (g === "__ninguno__") c.checked = false;
          else c.checked = emps.indexOf(g) !== -1;
        });
      });
    }
  }

  /* Pestanas locales (selector de estudiante y expediente). El kit alterna
     todos los [data-panel-nombre] de la pagina, por eso estas usan su propio
     contrato y aqui solo se conmutan los paneles hermanos de la barra. */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-tab-local]");
    if (!b) return;
    e.preventDefault();
    e.stopPropagation();
    var barra = b.closest("[data-tabs-local]");
    if (!barra) return;
    var clave = b.getAttribute("data-tab-local");
    $$("button[data-tab-local]", barra).forEach(function (o) {
      var es = o === b;
      o.classList.toggle("activo", es);
      o.setAttribute("aria-selected", es ? "true" : "false");
    });
    var caja = barra.parentNode;
    Array.prototype.forEach.call(caja.children, function (p) {
      if (p.hasAttribute("data-tab-panel")) {
        p.hidden = p.getAttribute("data-tab-panel") !== clave;
      }
    });
  }, true);

  /* ---- controlador de tablas del docente ------------------------------- */
  /* Mismo contrato que el paginador del administrador, pero con los ganchos
     del rol ([data-filtro], [data-pag-doc]). Corta las filas de verdad: el
     kit solo movia la etiqueta "Mostrando X a Y". */
  function norm(txt) {
    return (txt || "").toLowerCase().normalize("NFD")
      .replace(/[\\u0300-\\u036f]/g, "").trim();
  }

  var ZONAS = [];

  function crearZona(zona) {
    var tabla = $("table.tabla", zona);
    if (!tabla) return null;
    var filas = $$("tbody tr", tabla);
    var control = $("[data-pag-doc]", zona);
    var tam = control ? (parseInt(control.dataset.pagTam, 10) || 5) : 0;
    var buscador = $(".buscador input", zona);
    var filtros = $$("[data-filtro='1'], [data-diag-emp]", zona);
    var contador = $("[data-resultados]", zona);
    var vacio = $("[data-vacio]", zona);
    var pagina = 1;

    function coincide(fila) {
      var q = buscador ? norm(buscador.value) : "";
      if (q && norm(fila.textContent).indexOf(q) < 0) return false;
      for (var i = 0; i < filtros.length; i++) {
        var sel = filtros[i];
        var valor = norm(sel.value);
        if (!valor) continue;
        var col = parseInt(sel.dataset.filtroCol, 10);
        if (isNaN(col)) continue;
        var celda = fila.children[col];
        if (!celda) continue;
        var texto = norm(celda.textContent);
        /* Una opcion puede agrupar varios estados ("En revision|Devuelta"):
           se acepta la fila si coincide cualquiera de ellos. */
        var opt = sel.options[sel.selectedIndex];
        var multi = opt ? opt.getAttribute("data-valores") : null;
        if (multi) {
          var partes = multi.split("|"), hallado = false;
          for (var k = 0; k < partes.length; k++) {
            if (texto.indexOf(norm(partes[k])) >= 0) { hallado = true; break; }
          }
          if (!hallado) return false;
        } else if (texto.indexOf(valor) < 0) {
          return false;
        }
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

    if (buscador) {
      var tb = null;
      buscador.addEventListener("input", function () {
        clearTimeout(tb);
        /* 240 ms: despues del filtro del kit (220 ms) para que el corte de
           paginas sea el ultimo en aplicarse. */
        tb = setTimeout(function () { pagina = 1; aplicar(); }, 240);
      });
      buscador.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          clearTimeout(tb);
          pagina = 1;
          aplicar();
        }
      });
    }
    filtros.forEach(function (f) {
      if (f.tagName === "SELECT") {
        f.addEventListener("change", function () { pagina = 1; aplicar(); });
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
    return { zona: zona, aplicar: aplicar };
  }

  $$("[data-tabla-zona]").forEach(function (z) {
    var c = crearZona(z);
    if (c) ZONAS.push(c);
  });

  function refrescarZona(el) {
    for (var i = 0; i < ZONAS.length; i++) {
      if (ZONAS[i].zona.contains(el)) { ZONAS[i].aplicar(); return; }
    }
  }

  /* Diagnostico: el emprendimiento elegido cambia KPIs, graficas, datos e
     historial; ademas acota las opciones de "Proyecto / grupo" a su grupo. */
  var diagEmp = $("[data-diag-emp]");
  if (diagEmp) {
    var diagProy = $("[data-diag-proyecto]");
    var diagCtx = $$("[data-diag-contexto]");
    var diagEmps = $$("option", diagEmp).slice(1).map(function (o) {
      return o.value;
    });
    var pintarDiag = function () {
      var op = diagEmp.selectedOptions[0];
      var clave = (op && op.getAttribute("data-slug")) || "todos";
      diagCtx.forEach(function (c) {
        c.hidden = c.getAttribute("data-diag-contexto") !== clave;
      });
      if (diagProy) {
        var lista = diagEmp.value ? [diagEmp.value] : diagEmps;
        var h = '<option value="">Todos los proyectos</option>';
        lista.forEach(function (x) {
          h += '<option value="' + x + '">' + x + "</option>";
        });
        diagProy.innerHTML = h;
        diagProy.value = "";
      }
      refrescarZona(diagEmp);
    };
    diagEmp.addEventListener("change", pintarDiag);
  }

  /* Aplica un valor a los filtros de la pagina comparando con el valor exacto
     de cada opcion. Devuelve true si encontro donde aplicarlo. */
  function filtrarPor(val) {
    var sels = document.querySelectorAll("select[data-filtro]");
    for (var i = 0; i < sels.length; i++) {
      var s = sels[i], ok = false;
      for (var j = 0; j < s.options.length; j++) {
        if (s.options[j].value === val) { ok = true; break; }
      }
      if (ok) { s.value = val; s.dispatchEvent(new Event("change")); return true; }
    }
    return false;
  }

  function aplicarFiltroDesdeURL() {
    var m = location.search.match(/[?&]f=([^&]+)/);
    if (m) filtrarPor(decodeURIComponent(m[1].split("+").join(" ")));
    /* ?emp=<emprendimiento> preselecciona el filtro del mismo nombre (Tareas,
       Asesorias). No interfiere con el ?emp= del expediente: alli no hay
       filtros de tabla que coincidan con un slug. */
    var e = location.search.match(/[?&]emp=([^&]+)/);
    if (e) filtrarPor(decodeURIComponent(e[1].split("+").join(" ")));
  }

  /* ?vista=tabla abre directamente la pestana Tabla de Emprendimientos, para
     que el clic en una tarjeta muestre el resultado ya filtrado. */
  function aplicarVistaDesdeURL() {
    var m = location.search.match(/[?&]vista=([^&]+)/);
    if (!m || m[1] !== "tabla") return;
    var b = document.querySelector(
      '#vista-emprendimientos button[data-panel="tabla"]');
    if (b) b.click();
  }

  function aplicarURL() {
    aplicarFiltroDesdeURL();
    aplicarVistaDesdeURL();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", aplicarURL);
  } else {
    aplicarURL();
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("button, a.btn");
    if (!b) return;
    var acc = b.getAttribute("data-accion");
    if (!acc) return;

    if (acc === "marcar-todo-leido") {
      e.preventDefault();
      e.stopPropagation();
      confirmar("Marcar todo como leído",
        "Se archivaran todas las notificaciones pendientes.",
        function () {
          $$(".aviso").forEach(function (av) {
            av.classList.add("leida");
            $$("[data-accion='marcar-leida']", av).forEach(function (m) {
              m.disabled = true;
              m.textContent = "Leída";
            });
          });
          var c = $(".count");
          if (c) c.textContent = "0";
          toast("Notificaciones marcadas como leidas", "ok");
        });
      return;
    }
    if (acc === "marcar-leida") {
      e.preventDefault();
      e.stopPropagation();
      var av = b.closest(".aviso");
      if (av && !av.classList.contains("leida")) {
        av.classList.add("leida");
        b.disabled = true;
        b.textContent = "Leída";
        var cuenta = $(".count");
        if (cuenta) {
          cuenta.textContent = String(Math.max(0,
            (parseInt(cuenta.textContent, 10) || 0) - 1));
        }
      }
      toast("Notificación marcada como leída", "ok");
      return;
    }
    if (acc === "filtrar-notificacion") {
      e.preventDefault();
      e.stopPropagation();
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
      e.preventDefault();
      e.stopPropagation();
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
    if (GUARDAR[acc]) {
      e.preventDefault();
      e.stopPropagation();
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
# 24 asesorias: la tabla declara 24 registros y ahora el paginador los pagina de
# verdad (antes habia 6 filas y el control prometia 24).
ASESORIAS = [
    ("ASES-019", "EcoPack", "Lucía Fernández", "Ambiental",
     "Confirmada", "26 nov 2024, 08:00", "Virtual",
     "FASE 3 - Validación: usabilidad"),
    ("ASES-024", "Muebles Origen", "Andrés Felipe", "Muebles",
     "Pendiente de confirmar", "25 nov 2024, 10:00", "Presencial",
     "FASE 2 - Prototipo: proveedores"),
    ("ASES-015", "Sabor y Sabe", "Mariana López", "Alimentos",
     "Pendiente de confirmar", "22 nov 2024, 10:00", "Modalidad mixta",
     "FASE 2 - Prototipo: costos"),
    ("ASES-017", "Aromas del Sur", "Sofía Ramírez", "Alimentos",
     "Pendiente de confirmar", "21 nov 2024, 11:00", "Presencial",
     "FASE 1 - Ideación: cliente"),
    ("ASES-012", "EcoPack", "Lucía Fernández", "Ambiental",
     "Pendiente de confirmar", "20 nov 2024, 09:00", "Presencial",
     "FASE 3 - Validación: prueba con usuarios"),
    ("ASES-018", "Muebles Origen", "Andrés Felipe", "Muebles",
     "Confirmada", "19 nov 2024, 15:00", "Modalidad mixta",
     "FASE 2 - Prototipo: mobiliario"),
    ("ASES-016", "Krea Textil", "Jhon Ospina", "Moda",
     "Confirmada", "18 nov 2024, 09:00", "Virtual",
     "Tarea: catálogo de productos"),
    ("ASES-013", "Krea Textil", "Jhon Ospina", "Moda",
     "Confirmada", "14 nov 2024, 15:30", "Virtual",
     "Tarea: Perfil en redes sociales"),
    ("ASES-014", "Sabor y Sabe", "Mariana López", "Alimentos",
     "Confirmada", "12 nov 2024, 10:00", "Modalidad mixta",
     "FASE 2 - Prototipo: empaque"),
    ("ASES-020", "Muebles Origen", "Andrés Felipe", "Muebles",
     "Finalizada", "07 nov 2024, 10:00", "Presencial",
     "FASE 2 - Prototipo: materiales"),
    ("ASES-011", "Sabor y Sabe", "Mariana López", "Alimentos",
     "Finalizada", "05 nov 2024, 10:00", "Presencial",
     "FASE 2 - Prototipo: precios"),
    ("ASES-021", "Aromas del Sur", "Camilo Rojas", "Alimentos",
     "Finalizada", "04 nov 2024, 14:00", "Virtual",
     "FASE 1 - Ideación: propuesta de valor"),
    ("ASES-008", "Muebles Origen", "Andrés Felipe", "Muebles",
     "Confirmada", "04 nov 2024, 11:00", "Presencial",
     "FASE 2 - Prototipo: acabados"),
    ("ASES-010", "Krea Textil", "Jhon Ospina", "Moda",
     "Finalizada", "31 oct 2024, 14:00", "Virtual",
     "Tarea: Análisis de competencia"),
    ("ASES-022", "Sabor y Sabe", "Diego Torres", "Alimentos",
     "Finalizada", "30 oct 2024, 09:00", "Modalidad mixta",
     "FASE 1 - Ideación: segmento"),
    ("ASES-023", "Krea Textil", "Mariana López", "Moda",
     "Cancelada por el estudiante", "29 oct 2024, 16:00", "Virtual",
     "Tarea: presupuesto de telas"),
    ("ASES-009", "EcoPack", "Lucía Fernández", "Ambiental",
     "Cancelada por el estudiante", "28 oct 2024, 11:00", "Presencial",
     "FASE 1 - Ideación: problema"),
    ("ASES-007", "Aromas del Sur", "Sofía Ramírez", "Alimentos",
     "Cancelada por el estudiante", "25 oct 2024, 10:00", "Virtual",
     "FASE 1 - Ideación: entrevistas"),
    ("ASES-006", "EcoPack", "Diego Torres", "Ambiental",
     "Finalizada", "24 oct 2024, 09:00", "Presencial",
     "FASE 2 - Prototipo: empaque reciclado"),
    ("ASES-005", "Sabor y Sabe", "Diego Torres", "Alimentos",
     "Finalizada", "22 oct 2024, 15:00", "Virtual",
     "FASE 1 - Ideación: problema"),
    ("ASES-004", "Krea Textil", "Jhon Ospina", "Moda",
     "Finalizada", "21 oct 2024, 11:00", "Virtual",
     "Tarea: análisis de competencia"),
    ("ASES-003", "EcoPack", "Lucía Fernández", "Ambiental",
     "Finalizada", "18 oct 2024, 10:00", "Modalidad mixta",
     "FASE 2 - Prototipo: prototipo v1"),
    ("ASES-002", "Aromas del Sur", "Camilo Rojas", "Alimentos",
     "Finalizada", "16 oct 2024, 09:00", "Presencial",
     "FASE 1 - Ideación: cliente"),
    ("ASES-001", "Muebles Origen", "Andrés Felipe", "Muebles",
     "Finalizada", "14 oct 2024, 14:00", "Virtual",
     "FASE 1 - Ideación: problema"),
]

# Avances del emprendimiento: (fecha, fase, descripcion, calificacion, evidencia).
# Un juego por emprendimiento para que el expediente de cada uno muestre lo suyo.
AVANCES_EMP = {
    "Sabor y Sabe": [
        ("12 nov 2024", "FASE 2",
         "Prototipo de empaque listo para 20 unidades", 92, "Con evidencia"),
        ("05 nov 2024", "FASE 2",
         "Definición de precios y punto de equilibrio", 88, "Con evidencia"),
        ("28 oct 2024", "FASE 1",
         "Diagnóstico inicial y problema claro", 81, "Sin evidencia"),
    ],
    "Krea Textil": [
        ("14 nov 2024", "FASE 1",
         "Perfil de cliente y propuesta de valor", 85, "Con evidencia"),
        ("31 oct 2024", "FASE 1",
         "Análisis de competencia del sector moda", 79, "Con evidencia"),
        ("22 oct 2024", "FASE 1",
         "Entrevistas iniciales con compradores", 74, "Sin evidencia"),
    ],
    "EcoPack": [
        ("09 nov 2024", "FASE 3",
         "Prueba de resistencia del empaque reciclado", 95, "Con evidencia"),
        ("31 oct 2024", "FASE 2",
         "Prototipo v2 con materiales locales", 90, "Con evidencia"),
        ("18 oct 2024", "FASE 2",
         "Ficha técnica de materiales", 86, "Con evidencia"),
    ],
    "Aromas del Sur": [
        ("06 nov 2024", "FASE 1",
         "Perfil del cliente ideal", 72, "Con evidencia"),
        ("24 oct 2024", "FASE 1",
         "Propuesta de valor inicial", 68, "Sin evidencia"),
        ("16 oct 2024", "FASE 1",
         "Entrevistas con usuarios", 64, "Sin evidencia"),
    ],
    "Muebles Origen": [
        ("04 nov 2024", "FASE 2",
         "Selección de maderas y acabados", 88, "Con evidencia"),
        ("25 oct 2024", "FASE 1",
         "Diagnóstico del taller y capacidad", 83, "Con evidencia"),
        ("14 oct 2024", "FASE 1",
         "Problema y segmento del cliente", 77, "Sin evidencia"),
    ],
}

# Tareas del docente: (titulo, emprendimiento, estudiante, prioridad, vence, estado).
# 23 registros: es el total que declara la tabla, para que las 5 paginas
# muestren filas distintas.
TAREAS_DOC = [
    ("Evidencia fotografica del punto de venta", "Sabor y Sabe", "Mariana López",
     "Alta", "12 nov 2024", "En revision"),
    ("Lista de precios del catálogo", "Sabor y Sabe", "Diego Torres",
     "Media", "13 nov 2024", "Devuelta"),
    ("Presupuesto de insumos", "Sabor y Sabe", "Mariana López",
     "Media", "15 nov 2024", "Completada"),
    ("Ficha técnica del producto", "Sabor y Sabe", "Mariana López",
     "Baja", "19 nov 2024", "Pendiente"),
    ("Registro fotografico del taller", "Sabor y Sabe", "Diego Torres",
     "Media", "20 nov 2024", "Completada"),
    ("Perfil en redes sociales", "Krea Textil", "Jhon Ospina",
     "Baja", "16 nov 2024", "Pendiente"),
    ("Cotización con proveedores", "Krea Textil", "Mariana López",
     "Alta", "17 nov 2024", "En revision"),
    ("Patronaje de la primera colección", "Krea Textil", "Jhon Ospina",
     "Media", "21 nov 2024", "Pendiente"),
    ("Catálogo de telas", "Krea Textil", "Jhon Ospina",
     "Baja", "22 nov 2024", "Completada"),
    ("Prueba de color y acabados", "Krea Textil", "Mariana López",
     "Media", "23 nov 2024", "Devuelta"),
    ("Prototipo de empaque", "EcoPack", "Lucía Fernández",
     "Alta", "14 nov 2024", "En revision"),
    ("Ficha de materiales reciclados", "EcoPack", "Lucía Fernández",
     "Alta", "15 nov 2024", "Completada"),
    ("Prueba de resistencia del empaque", "EcoPack", "Diego Torres",
     "Alta", "18 nov 2024", "En revision"),
    ("Registro de proveedores locales", "EcoPack", "Lucía Fernández",
     "Media", "24 nov 2024", "Pendiente"),
    ("Encuesta a usuarios", "EcoPack", "Diego Torres",
     "Media", "25 nov 2024", "Completada"),
    ("Análisis de competencia", "Aromas del Sur", "Sofía Ramírez",
     "Media", "18 nov 2024", "Pendiente"),
    ("Perfil del cliente ideal", "Aromas del Sur", "Sofía Ramírez",
     "Alta", "16 nov 2024", "Completada"),
    ("Prueba de aromas con usuarios", "Aromas del Sur", "Camilo Rojas",
     "Media", "19 nov 2024", "En revision"),
    ("Etiqueta y empaque del producto", "Aromas del Sur", "Sofía Ramírez",
     "Baja", "26 nov 2024", "Pendiente"),
    ("Medición del taller", "Muebles Origen", "Andrés Felipe",
     "Media", "17 nov 2024", "Completada"),
    ("Selección de maderas", "Muebles Origen", "Andrés Felipe",
     "Alta", "20 nov 2024", "En revision"),
    ("Ficha de acabados", "Muebles Origen", "Andrés Felipe",
     "Media", "22 nov 2024", "Devuelta"),
    ("Cotización de transporte", "Muebles Origen", "Andrés Felipe",
     "Baja", "27 nov 2024", "Pendiente"),
]

PRIO_AS = {"Alta": "b-amarillo", "Media": "b-azul", "Baja": "b-linea"}
ESTADO_TAREA = {"En revision": "b-amarillo", "Completada": "b-azul",
                "Pendiente": "b-neutra", "Devuelta": "b-neutra"}

# Diagnostico generado: (origen, detalle, emprendimiento, estudiante, tema,
# estado, fecha). `origen` usa exactamente las opciones del filtro para que el
# select filtre de verdad; el detalle se conserva como segunda linea.
DIAGNOSTICOS = [
    ("Fases y tareas clave", "FASE 2 en curso", "Sabor y Sabe",
     "Mariana López", "Prototipo y precios", "En curso", "12 nov 2024"),
    ("Solo por tareas clave", "2 de 5 tareas clave", "Sabor y Sabe",
     "Diego Torres", "Empaque y costos", "En curso", "08 nov 2024"),
    ("Fases y tareas clave", "FASE 1 completada", "Sabor y Sabe",
     "Mariana López", "Problema y perfil", "Completado", "28 oct 2024"),
    ("Solo por fases (4)", "FASE 1 en curso", "Krea Textil",
     "Jhon Ospina", "Cliente y propuesta", "En curso", "06 nov 2024"),
    ("Solo por tareas clave", "1 de 4 tareas clave", "Krea Textil",
     "Jhon Ospina", "Validación con usuarios", "Pendiente", "Sin fecha"),
    ("Fases y tareas clave", "FASE 1 completada", "Krea Textil",
     "Mariana López", "Problema y perfil", "Completado", "30 oct 2024"),
    ("Fases y tareas clave", "FASE 3 en curso", "EcoPack",
     "Lucía Fernández", "Validación con usuarios", "En curso", "10 nov 2024"),
    ("Solo por fases (4)", "FASE 2 completada", "EcoPack",
     "Lucía Fernández", "Prototipo y materiales", "Completado", "31 oct 2024"),
    ("Solo por tareas clave", "1 de 4 tareas clave", "EcoPack",
     "Diego Torres", "Resistencia del empaque", "Pendiente", "Sin fecha"),
    ("Solo por fases (4)", "FASE 1 en curso", "Aromas del Sur",
     "Sofía Ramírez", "Problema y cliente", "En curso", "07 nov 2024"),
    ("Solo por tareas clave", "0 de 4 tareas clave", "Aromas del Sur",
     "Camilo Rojas", "Entrevistas", "Pendiente", "Sin fecha"),
    ("Fases y tareas clave", "FASE 1 completada", "Aromas del Sur",
     "Sofía Ramírez", "Propuesta de valor", "Completado", "24 oct 2024"),
    ("Fases y tareas clave", "FASE 2 en curso", "Muebles Origen",
     "Andrés Felipe", "Prototipo y materiales", "En curso", "11 nov 2024"),
    ("Solo por tareas clave", "2 de 4 tareas clave", "Muebles Origen",
     "Andrés Felipe", "Acabados", "En curso", "09 nov 2024"),
    ("Solo por fases (4)", "FASE 1 completada", "Muebles Origen",
     "Andrés Felipe", "Problema y perfil", "Completado", "25 oct 2024"),
]

COMP_LABELS = ["Visión", "Creatividad", "Resiliencia", "Liderazgo",
               "Trabajo en equipo", "Toma de decisiones"]

# Contexto del diagnostico por emprendimiento: lo que cambia en pantalla al
# elegir uno en el filtro. Antes todo esto estaba escrito a mano para Sabor y
# Sabe, sin importar el emprendimiento elegido.
DIAG_EMP = {
    "Sabor y Sabe": {
        "fases": [("FASE 1 - Ideación", 100, AZUL),
                  ("FASE 2 - Prototipo", 62, AZUL),
                  ("FASE 3 - Validación", 24, AMAR),
                  ("FASE 4 - Formalización", 0, "#bbbbbb")],
        "comportamiento": [85, 78, 70, 82, 88, 66],
        "fases_completadas": "1 de 4",
        "pct_fases": 25,
        "tareas_clave": "2 de 5",
        "pct_tareas": 40,
        "puntaje": "7.8",
        "ultima_revision": "12 nov 2024, 09:14",
        "recomendaciones": "Canal de venta y presupuesto de publicidad",
        "historial": [
            ("12", "nov", "Diagnóstico FASE 2 en curso", "62% de la fase", ""),
            ("28", "oct", "Diagnóstico FASE 1", "Puntaje 7.8 de 10", ""),
        ],
    },
    "Krea Textil": {
        "fases": [("FASE 1 - Ideación", 28, AZUL),
                  ("FASE 2 - Prototipo", 0, AZUL),
                  ("FASE 3 - Validación", 0, AMAR),
                  ("FASE 4 - Formalización", 0, "#bbbbbb")],
        "comportamiento": [72, 88, 64, 70, 74, 68],
        "fases_completadas": "0 de 4",
        "pct_fases": 7,
        "tareas_clave": "1 de 4",
        "pct_tareas": 25,
        "puntaje": "6.9",
        "ultima_revision": "06 nov 2024, 16:20",
        "recomendaciones": "Cerrar el perfil del cliente y el análisis de competencia",
        "historial": [
            ("06", "nov", "Diagnóstico FASE 1 en curso", "28% de la fase", ""),
            ("30", "oct", "Diagnóstico FASE 1", "Puntaje 6.9 de 10", ""),
        ],
    },
    "EcoPack": {
        "fases": [("FASE 1 - Ideación", 100, AZUL),
                  ("FASE 2 - Prototipo", 100, AZUL),
                  ("FASE 3 - Validación", 84, AMAR),
                  ("FASE 4 - Formalización", 0, "#bbbbbb")],
        "comportamiento": [88, 82, 90, 76, 84, 80],
        "fases_completadas": "2 de 4",
        "pct_fases": 50,
        "tareas_clave": "3 de 4",
        "pct_tareas": 75,
        "puntaje": "8.6",
        "ultima_revision": "10 nov 2024, 11:05",
        "recomendaciones": "Documentar la prueba de resistencia y el plan de producción",
        "historial": [
            ("10", "nov", "Diagnóstico FASE 3 en curso", "84% de la fase", ""),
            ("31", "oct", "Diagnóstico FASE 2", "Puntaje 8.6 de 10", ""),
        ],
    },
    "Aromas del Sur": {
        "fases": [("FASE 1 - Ideación", 15, AZUL),
                  ("FASE 2 - Prototipo", 0, AZUL),
                  ("FASE 3 - Validación", 0, AMAR),
                  ("FASE 4 - Formalización", 0, "#bbbbbb")],
        "comportamiento": [68, 74, 62, 66, 71, 58],
        "fases_completadas": "0 de 4",
        "pct_fases": 4,
        "tareas_clave": "0 de 4",
        "pct_tareas": 0,
        "puntaje": "6.2",
        "ultima_revision": "07 nov 2024, 09:40",
        "recomendaciones": "Completar entrevistas y definir la propuesta de valor",
        "historial": [
            ("07", "nov", "Diagnóstico FASE 1 en curso", "15% de la fase", ""),
            ("24", "oct", "Diagnóstico FASE 1", "Puntaje 6.2 de 10", ""),
        ],
    },
    "Muebles Origen": {
        "fases": [("FASE 1 - Ideación", 100, AZUL),
                  ("FASE 2 - Prototipo", 55, AZUL),
                  ("FASE 3 - Validación", 0, AMAR),
                  ("FASE 4 - Formalización", 0, "#bbbbbb")],
        "comportamiento": [80, 72, 84, 78, 76, 74],
        "fases_completadas": "1 de 4",
        "pct_fases": 25,
        "tareas_clave": "2 de 4",
        "pct_tareas": 50,
        "puntaje": "7.5",
        "ultima_revision": "11 nov 2024, 15:30",
        "recomendaciones": "Cerrar cotizaciones de proveedores y transporte",
        "historial": [
            ("11", "nov", "Diagnóstico FASE 2 en curso", "55% de la fase", ""),
            ("25", "oct", "Diagnóstico FASE 1", "Puntaje 7.5 de 10", ""),
        ],
    },
}

TIPO_EMP = {
    "Sabor y Sabe": "Comercio",
    "Krea Textil": "Manufactura",
    "EcoPack": "Manufactura",
    "Aromas del Sur": "Comercio",
    "Muebles Origen": "Manufactura",
}

COMENTARIOS_EMP = {
    "Sabor y Sabe": [
        ("Carlos Mendoza", "12 nov 2024",
         "Buen avance en el prototipo. Falta medir el costo unitario de los empaques."),
        ("Mariana López", "11 nov 2024",
         "Adjunte las fotos del punto de venta y la lista de precios."),
    ],
    "Krea Textil": [
        ("Carlos Mendoza", "14 nov 2024",
         "El análisis de competencia está bien; aterricen el precio de la primera colección."),
        ("Jhon Ospina", "13 nov 2024",
         "Subimos el catálogo de telas y el perfil del cliente."),
    ],
    "EcoPack": [
        ("Carlos Mendoza", "09 nov 2024",
         "La prueba de resistencia quedó documentada. Falta el plan de producción."),
        ("Lucía Fernández", "08 nov 2024",
         "Adjuntamos la ficha técnica y las fotos del prototipo v2."),
    ],
    "Aromas del Sur": [
        ("Carlos Mendoza", "06 nov 2024",
         "Faltan entrevistas antes de cerrar la propuesta de valor."),
        ("Sofía Ramírez", "05 nov 2024",
         "Programamos tres entrevistas para esta semana."),
    ],
    "Muebles Origen": [
        ("Carlos Mendoza", "04 nov 2024",
         "Buen avance en materiales; revisen el costo del transporte."),
        ("Andrés Felipe", "03 nov 2024",
         "Actualizamos la medición del taller y los acabados."),
    ],
}

# Grupo de cada emprendimiento: un emprendimiento puede tener varios estudiantes
# y un estudiante puede tener varios emprendimientos (relación N:N).
# Campos: (estudiante, codigo, sede). El código es el mismo ID de 6 dígitos que
# usa el administrador en la gestión de perfiles.
ESTUDIANTES_EMP = {
    "Sabor y Sabe": [("Mariana López", "912646", "Sede Norte"),
                     ("Diego Torres", "912658", "Sede Norte")],
    "Krea Textil": [("Jhon Ospina", "912647", "Sede Centro"),
                    ("Mariana López", "912646", "Sede Norte")],
    "EcoPack": [("Lucía Fernández", "912648", "Sede Norte"),
                ("Diego Torres", "912658", "Sede Norte")],
    "Aromas del Sur": [("Sofía Ramírez", "912649", "Sede Sur"),
                       ("Camilo Rojas", "912651", "Sede Sur")],
    "Muebles Origen": [("Andrés Felipe", "912650", "Sede Centro")],
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

# Eventos del programa para recomendar a los estudiantes. Son los mismos eventos
# que ve el estudiante en su vista de Eventos (fuente de referencia).
# Campos: (nombre, tipo, fecha, modalidad, organizador, cupos).
EVENTOS = [
    ("Startup Minuto de Dios", "Conferencia", "21 nov 2024, 08:00", "Presencial",
     "Dirección Académica", "40 cupos"),
    ("Capacitación en modelado de negocios", "Taller", "21 nov 2024, 14:00",
     "Virtual", "Coordinación Académica", "120 cupos"),
    ("Asesoría grupal de empleabilidad", "Asesoría", "26 nov 2024, 10:00",
     "Presencial", "Bienestar Estudiantil", "25 cupos"),
    ("Showroom de emprendimientos", "Muestra", "02 dic 2024, 09:00", "Presencial",
     "Dirección Académica", "60 cupos"),
]

# Recomendaciones ya enviadas por el docente: (estudiante, evento, estado, fecha).
RECOMENDACIONES = [
    ("Mariana López", "Startup Minuto de Dios", "Aceptada", "12 nov 2024"),
    ("Diego Torres", "Capacitación en modelado de negocios", "Enviada", "11 nov 2024"),
    ("Jhon Ospina", "Showroom de emprendimientos", "Aceptada", "10 nov 2024"),
]

# Compromisos propios del calendario del Inicio (tareas y eventos del día),
# por día de noviembre de 2024. Formato: día -> [(hora, título, meta, badge)].
# Las asesorías no se escriben aquí: dashboard() las agrega desde ASESORIAS
# para que el calendario no se separe de la vista de Asesorías.
COMPROMISOS_DIA = {
    12: [
        ("10:00", "Asesoría con Sabor y Sabe", "Mariana López · Modalidad mixta",
         badge("Confirmada", "b-azul")),
        ("14:00", "Revisar evidencia de EcoPack", "Lucía Fernández · 3 archivos",
         badge("Por revisar", "b-amarillo")),
        ("16:30", "Calificar tarea de Krea Textil", "Jhon Ospina · Evidencia",
         badge("Pendiente", "b-linea")),
    ],
    20: [
        ("09:00", "Asesoría con EcoPack", "Lucía Fernández · Presencial",
         badge("Por confirmar", "b-amarillo")),
    ],
    21: [
        ("08:00", "Startup Minuto de Dios", "Auditorio principal, sede Norte",
         badge("Evento", "b-azul", "calendar")),
        ("14:00", "Capacitación en modelado de negocios", "Sala virtual institucional",
         badge("Evento", "b-azul", "calendar")),
    ],
    26: [
        ("10:00", "Asesoría grupal de empleabilidad", "Sala de reuniones 204",
         badge("Evento", "b-azul", "calendar")),
    ],
}


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


def _metrica_enlace(ic, lbl, val, uni, barra, nota, href, prev_titulo,
                    prev_texto, cta, aria_val=None):
    """Tarjeta de resumen que ademas abre la vista correspondiente.

    Al pasar el mouse (o al enfocar con el teclado) muestra una mini vista
    previa con lo que hay dentro; el clic navega. Se arma con las clases del
    kit (.metrica-enlace/.mini-prev) pero con dos ajustes locales: el nombre
    accesible del enlace es fijo (aria-label) y la preview queda oculta a los
    lectores de pantalla (aria-hidden), para que no cambie al mostrarse.

    `aria_val` permite que el lector de pantalla anuncie el dato completo
    ("1 de 4") cuando en pantalla el numero y la unidad van separados."""
    anuncio = val if aria_val is None else aria_val
    return (
        '<a class="card metrica metrica-enlace" href="%s" '
        'aria-label="%s: %s. %s">'
        '<div class="metrica-top"><span class="metrica-ico">%s</span>'
        '<div><div class="metrica-lbl">%s</div>'
        '<div class="metrica-val">%s<span class="u">%s</span></div></div>'
        '<span class="metrica-flecha" aria-hidden="true">%s</span></div>'
        '<div class="barra"><span style="width:%d%%"></span></div>'
        '<div class="metrica-nota">%s</div>'
        '<span class="mini-prev" aria-hidden="true"><b>%s</b><span>%s</span>'
        '<em>%s %s</em></span></a>'
        % (href, lbl, anuncio, cta, ico(ic, 18), lbl, val, uni, ico("der", 14),
           barra, nota, prev_titulo, prev_texto, ico("der", 12), cta)
    )


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


ESTADO_VIS = {"En revision": "En revisión"}


def _estado_vis(estado):
    """Texto visible de un estado, sin tocar el valor interno.

    Los datos y los filtros siguen usando "En revision" (contrato de
    ?f=En+revision); solo la insignia se muestra acentuada."""
    return ESTADO_VIS.get(estado, estado)


def _filtro(aria, opciones, col, extra="", valores=None, etiquetas=None):
    """Select de filtro de la tabla.

    `valores` permite que una opcion represente varios valores de la celda:
    {etiqueta: "En revision|Devuelta"} agrega data-valores y el JS del rol
    acepta la fila cuando coincide cualquiera de ellos.

    `etiquetas` separa lo que se ve de lo que se filtra: {valor: "texto"} deja
    el `value` intacto (contratos como ?f=En+revision) y muestra el texto
    acentuado."""
    valores = valores or {}
    etiquetas = etiquetas or {}
    opts = '<option value="">%s</option>' % opciones[0]
    for o in opciones[1:]:
        extra_opt = (' data-valores="%s"' % valores[o]) if o in valores else ""
        opts += '<option value="%s"%s>%s</option>' % (
            o, extra_opt, etiquetas.get(o, o))
    return ('<select class="filtro" data-filtro="1" data-filtro-col="%d" '
            'aria-label="%s"%s>%s</select>' % (col, aria, extra, opts))


def _tabs_local(items):
    """Pestanas de ambito local: cada item es (id-panel, etiqueta).

    No usan `data-panel` ni la clase `.tabs`: el kit alterna TODOS los
    `[data-panel-nombre]` de la pagina, y con pestanas anidadas ocultaba los
    contenedores externos (selector de estudiante en blanco). El JS del rol
    alterna solo los paneles hermanos de la barra.
    """
    h = '<div class="pest" data-tabs-local>'
    for i, (pid, etiqueta) in enumerate(items):
        h += ('<button type="button" role="tab" aria-selected="%s" class="%s" '
              'data-tab-local="%s">%s</button>'
              % ("true" if i == 0 else "false", "activo" if i == 0 else "",
                 pid, etiqueta))
    return h + "</div>"


def _panel_local(clave, contenido, activo=False):
    return '<div data-tab-panel="%s"%s>%s</div>' % (
        clave, "" if activo else " hidden", contenido)


def _paginas_doc(desde, hasta, total, tabla_id):
    """Paginador de tabla del docente. Se marca `data-pag-doc` (no
    `data-paginacion`) para que el kit no lo toque: el corte real de filas lo
    hace el JS del rol, igual que el administrador con su propio paginador."""
    return paginas(desde, hasta, total, tabla_id=tabla_id).replace(
        "data-pag-adm", "data-pag-doc")


def _tabs(items):
    """Pestanas del rol: cada item es (id-panel, etiqueta).

    Delega en el helper compartido (mismo patron que el rol Estudiante), que
    espera (etiqueta, id-panel); aqui se invierte para conservar el orden que ya
    usan las vistas del docente. El id-panel debe casar con data-panel-nombre."""
    return tabs_paneles([(etiqueta, pid) for pid, etiqueta in items])


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


def _tabla_con_titulo(titulo, cabeceras, filas, pag=""):
    h = tabla(cabeceras, filas).replace(
        '<table class="tabla">',
        '<table class="tabla"><caption class="visually-hidden">%s</caption>' % titulo, 1)
    if pag:
        # El pie de paginacion vive dentro de la tarjeta de la tabla (antes
        # quedaba suelto debajo, con un borde superior sin tarjeta).
        h = h.replace('</div><div data-vacio', "</div>%s<div data-vacio" % pag, 1)
    return h


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
        ("eventos.html", "35 Docente - Eventos", eventos),
        ("evento-detalle-startup.html", "36 Docente - Detalle del evento (conferencia)",
         evento_detalle_startup),
        ("evento-detalle-capacitacion.html", "37 Docente - Detalle del evento (taller)",
         evento_detalle_capacitacion),
        ("evento-detalle-asesoria-grupal.html",
         "38 Docente - Detalle del evento (asesoría)", evento_detalle_asesoria_grupal),
        ("evento-detalle-showroom.html", "39 Docente - Detalle del evento (muestra)",
         evento_detalle_showroom),
        ("perfil.html", "40 Docente - Mi perfil", perfil),
        ("configuracion.html", "41 Docente - Configuración", configuracion),
        ("contrasena.html", "42 Docente - Cambiar contraseña", contrasena),
        ("notificaciones.html", "43 Docente - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_doc):
        reg("docente", arch, tit, _envolver(fn), i)


# --- 21. Dashboard -----------------------------------------------------------
# --- 21. Inicio --------------------------------------------------------------
_MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


def _fecha_orden(texto):
    """Convierte '14 nov 2024, 15:30' en una tupla ordenable."""
    m = re.match(r"(\d{1,2})\s+([a-z]{3})\s+(\d{4})(?:,\s*(\d{1,2}):(\d{2}))?",
                 texto)
    if not m:
        return (0, 0, 0, 0, 0)
    dia, mes, anio, hora, minuto = m.groups()
    return (int(anio), _MESES.get(mes, 0), int(dia), int(hora or 0),
            int(minuto or 0))


def _fecha_corta(texto):
    """'14 nov 2024, 15:30' -> '14 nov'."""
    return re.sub(r"\s+\d{4}(?=,|$)", "", texto.split(",")[0])


def _badge_asesoria(estado):
    """Etiqueta del estado de una asesoría, igual que en su vista."""
    if estado == "Confirmada":
        return badge("Confirmada", "b-azul")
    if estado == "Finalizada":
        return badge("Finalizada", "b-linea")
    if estado == "Cancelada por el estudiante":
        return badge("Cancelada", "b-neutra")
    return badge("Por confirmar", "b-amarillo")


def dashboard():
    """Inicio del docente.

    Las cuatro tarjetas se calculan con los mismos datos que alimentan sus
    vistas de destino y funcionan como enlaces: al pasar el cursor muestran
    una mini vista previa y al hacer clic abren esa vista."""
    emp_total = len(ASIGNADOS)
    emp_evid = sum(1 for a in ASIGNADOS if a[6])
    nov = [a for a in ASESORIAS if "nov 2024" in a[5]]
    nov_conf = sum(1 for a in nov if a[4] == "Confirmada")
    nov_pend = sum(1 for a in nov if a[4] == "Pendiente de confirmar")
    nov_fin = sum(1 for a in nov if a[4] == "Finalizada")
    futuras = sorted((a for a in nov
                      if _fecha_orden(a[5])[:3] > _fecha_orden("12 nov 2024")[:3]),
                     key=lambda a: _fecha_orden(a[5]))
    siguiente = futuras[0]
    revisar = [t for t in TAREAS_DOC if t[5] == "En revision"]
    rev_alta = sum(1 for t in revisar if t[3] == "Alta")
    avances = [(emp, x) for emp, lista in AVANCES_EMP.items() for x in lista]
    av_evid = sum(1 for _, x in avances if x[4] == "Con evidencia")
    ultimo = max(avances, key=lambda p: _fecha_orden(p[1][0]))
    alta = sum(1 for t in TAREAS_DOC if t[3] == "Alta")
    media = sum(1 for t in TAREAS_DOC if t[3] == "Media")
    baja = sum(1 for t in TAREAS_DOC if t[3] == "Baja")

    cartera = " · ".join("%s %d %%" % (a[0], a[3]) for a in ASIGNADOS[:3])
    cuerpo = '<div class="grid g-4">' + _metrica_enlace(
        "maleta", "Emprendimientos asignados", str(emp_total), "", 100,
        "%d activos" % emp_total, "emprendimientos.html",
        "Tus emprendimientos",
        "%s · %d en cartera · %d con evidencia"
        % (cartera, emp_total, emp_evid), "Ver emprendimientos")
    cuerpo += _metrica_enlace(
        "chat", "Asesorías del mes", str(len(nov)), "",
        int(round(nov_fin * 100.0 / len(nov))),
        "%d completadas" % nov_fin, "asesorias.html",
        "Asesorías de noviembre",
        "%d agendadas · %d por agendar · %d completadas · Próxima: %s, %s"
        % (nov_conf, nov_pend, nov_fin, _fecha_corta(siguiente[5]),
           siguiente[1]), "Ver asesorías")
    cuerpo += _metrica_enlace(
        "checklist", "Tareas por revisar", str(len(revisar)), "",
        int(round(len(revisar) * 100.0 / len(TAREAS_DOC))),
        "%d de prioridad alta" % rev_alta,
        "tareas.html?f=En+revision", "Tareas en revisión",
        "%d alta · %d media · %s (%s)"
        % (rev_alta, len(revisar) - rev_alta, revisar[0][0], revisar[0][1]),
        "Ver tareas en revisión")
    cuerpo += _metrica_enlace(
        "trend", "Avances registrados", str(len(avances)), "",
        int(round(av_evid * 100.0 / len(avances))),
        "%d con evidencia" % av_evid, "emprendimientos.html",
        "Avances de tus emprendimientos",
        "%d con evidencia · %d sin evidencia · Último: %s, %s"
        % (av_evid, len(avances) - av_evid, _fecha_corta(ultimo[1][0]),
           ultimo[0]), "Ver avances por emprendimiento")
    cuerpo += "</div>"
    cuerpo += _sep()
    # La gráfica ocupa el ancho completo (barras responsivas) para que cada
    # emprendimiento se lea grande y centrado, en lugar de quedar encajonada.
    cuerpo += card("Avance por emprendimiento", barras_h(
        "", "", [a[0] for a in ASIGNADOS], [a[3] for a in ASIGNADOS],
        maximo=100, unidad="%", ancho=760, pad_l=200, pad_r=64, alto_fila=40,
        responsive=True))
    cuerpo += _sep()
    # Compromisos del calendario: lo propio del día (tareas y eventos) más las
    # asesorías reales del mes desde ASESORIAS, sin duplicar las ya listadas.
    compromisos = {dia: list(items) for dia, items in COMPROMISOS_DIA.items()}
    for a in nov:
        dia = _fecha_orden(a[5])[2]
        if dia < 12:
            continue
        titulo = "Asesoría con %s" % a[1]
        items = compromisos.setdefault(dia, [])
        if any(i[1] == titulo for i in items):
            continue
        items.append((a[5].split(", ")[1], titulo,
                      "%s · %s" % (a[2], a[6]), _badge_asesoria(a[4])))
        items.sort(key=lambda i: i[0])
    compromisos = {dia: agenda([("Agenda del día", items)])
                   for dia, items in sorted(compromisos.items())}
    vacio = estado_vacio(
        "Sin compromisos",
        "No tienes asesorías, tareas ni eventos agendados para este día.",
        icono="calendar")
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Actividad reciente", _tabla_con_titulo(
        "Actividad reciente del docente",
        ["Fecha", "Emprendimiento", "Acción registrada", "@ACC"],
        [["12 nov 2024", "Sabor y Sabe", "Registraste un avance de fase",
          _acc(_a("eye", "Ver avance", "avance-detalle.html"))],
         ["11 nov 2024", "Sabor y Sabe", "Calificaste un avance con 92 de 100",
          _acc(_a("eye", "Ver avance", "avance-detalle.html"))],
         ["11 nov 2024", "EcoPack", "Confirmaste la asesoría del 26 de noviembre",
          _acc(_a("eye", "Ver asesoría", "asesoria-detalle.html"))],
         ["08 nov 2024", "Sabor y Sabe", "Asignaste la tarea de evidencia fotografica",
          _acc(_a("eye", "Ver tarea", "tarea-detalle.html"))]]))
    cuerpo += card("Calendario y compromisos",
                   calendario_interactivo("noviembre", 2024, compromisos, hoy=12,
                                          vacio=vacio),
                   hint="<span>Haz clic en un día</span>")
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones rápidas", '<div class="acciones-rapidas">'
                   + _lnk("avance-form.html", "edit", "Registrar avance")
                   + _lnk("tareas.html", "check", "Calificar", "btn btn-secundario")
                   + _lnk("diagnostico-revision.html", "clipboard", "Revisar diagnóstico",
                          "btn btn-secundario")
                   + _lnk("asesoria-form.html", "chat", "Generar asesoría",
                          "btn btn-secundario")
                   + "</div>")
    proximas = [("Hoy", [("10:00", "Sabor y Sabe",
                          "Mariana López · Modalidad mixta",
                          badge("Confirmada", "b-azul"))])]
    for a in futuras[:2]:
        proximas.append((_fecha_corta(a[5]), [(
            a[5].split(", ")[1], a[1], "%s · %s" % (a[2], a[6]),
            _badge_asesoria(a[4]))]))
    cuerpo += card("Próximas asesorías", agenda(proximas))
    cuerpo += card("Carga semanal", stacked_tareas(
        [("alta", alta, AZUL), ("media", media, "#162644"),
         ("baja", baja, "#bbbbbb")], "tareas"))
    cuerpo += "</div></div>"
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama de tus emprendimientos asignados y tu carga de trabajo.",
                 acciones=_lnk("asesoria-form.html", "plus", "Generar asesoría"))


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
    pag = _paginas_doc(1, 6, len(filas), "tabla-asesorias")
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo(
                        "Asesorías agendadas, completadas y por agendar",
                        ["Código", "Emprendimiento", "Estudiante", "Tema",
                         "Estado", "Fecha y hora", "Modalidad", "@ACC"], filas,
                        pag=pag))
    return shell(R, "asesorias", "Mis asesorías", cuerpo,
                 migas=["Inicio", "Mis asesorías"],
                 sub="Todas tus asesorías: por agendar, agendadas y completadas.",
                 acciones=_lnk("asesoria-form.html", "plus", "Registrar asesoría"))


# --- 23. Detalle de asesoria -------------------------------------------------
def asesoria_detalle():
    cuerpo = steps(["Solicitud recibida", "Confirmar fecha", "Registrar sesión",
                    "Cerrar asesoría"], 1)
    cuerpo += _sep_lg()
    cuerpo += metricas([
        ("chat", "Modalidad", "Mixta", "", 60, "Sala 3 / enlace"),
        ("reloj", "Duración", "60", "min", 60, "10:00 a 11:00"),
        ("users", "Agendada a", "2", "estudiantes", 100, "Todo el grupo"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Solicitud del estudiante", lista_def([
        ("Estudiante que solicita", "Mariana López"),
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
        ("Estado de revisión", badge(_estado_vis(rev), col)),
        ("Evidencia", badge("Con evidencia" if evid else "Sin evidencia",
                            "b-azul" if evid else "b-amarillo")),
        ("Última actividad", act),
    ])) + card("Estudiantes del grupo", lista_def(
        [(n, "%s · %s" % (cod, sede)) for n, cod, sede in roster_de(emp)]))
    der = card("Acciones", '<div class="acciones-col">'
               + _lnk("emprendimiento-expediente.html?emp=%s" % _slug(emp),
                      "eye", "Abrir expediente")
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
        tabs = _tabs_local([(_slug(e), e) for e in emps])
        paneles = "".join(
            _panel_local(_slug(e), _emp_resumen(e), activo=(i == 0))
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
    total = len(ASIGNADOS)
    con_evid = [a[0] for a in ASIGNADOS if a[6]]
    atencion = [a[0] for a in ASIGNADOS if REVISION[a[0]][0] in ("En revision",
                                                                "Devuelta")]
    n_rev = sum(1 for e in atencion if REVISION[e][0] == "En revision")
    n_dev = len(atencion) - n_rev
    cartera = " · ".join("%s %d %%" % (a[0], a[3]) for a in ASIGNADOS[:3])
    detalle_at = " · ".join(
        "%s %s" % (e, "en revisión" if REVISION[e][0] == "En revision"
                   else "devuelta") for e in atencion)
    # Las tres tarjetas abren la pestana Tabla con el filtro ya aplicado: el
    # dato que muestran es exactamente el conjunto de filas que se ve al hacer
    # clic (5, 3 y 2 resultados).
    cuerpo += '<div class="grid g-3">'
    cuerpo += _metrica_enlace(
        "maleta", "Asignados", str(total), "", 100,
        "%d expedientes" % total,
        "emprendimientos.html?vista=tabla", "Tus emprendimientos",
        "%s · %d en cartera" % (cartera, total), "Ver la tabla completa")
    cuerpo += _metrica_enlace(
        "upload", "Con evidencia", str(len(con_evid)), "",
        int(round(len(con_evid) * 100.0 / total)), "%d de %d" % (len(con_evid),
                                                                 total),
        "emprendimientos.html?vista=tabla&f=" + quote_plus("Con evidencia"),
        "Con evidencia", ", ".join(con_evid) + " · %d de %d expedientes"
        % (len(con_evid), total), "Ver los %d expedientes" % len(con_evid))
    cuerpo += _metrica_enlace(
        "alerta", "Requieren atención", str(len(atencion)), "",
        int(round(len(atencion) * 100.0 / total)),
        "%d en revisión · %d devuelta" % (n_rev, n_dev),
        "emprendimientos.html?vista=tabla&f=" + quote_plus("Requieren atención"),
        "Requieren atención", detalle_at, "Ver los %d casos" % len(atencion))
    cuerpo += "</div>"
    cuerpo += _sep()

    tarjetas = '<div class="emp-grid">'
    for emp, sector, etapa, avance, asesoria, act, _evid in ASIGNADOS:
        pie = ('<a class="btn btn-sm btn-secundario" '
               'href="emprendimiento-expediente.html?emp=%s">'
               "Abrir expediente</a>" % _slug(emp))
        grupo = estudiantes_de(emp)
        meta = ("1 estudiante" if len(grupo) == 1
                else "%d estudiantes" % len(grupo)) + " · " + sector
        tarjetas += tarjeta_emp("maleta", emp, meta, avance,
                                etapa, "%d%%" % avance, pie)
    tarjetas += "</div>"
    tarjetas += ('<p class="nota-foot">Última actividad registrada en el expediente '
                 "de cada estudiante.</p>")

    filas = []
    for emp, sector, etapa, avance, ases, act, evid in ASIGNADOS:
        rev, col = REVISION[emp]
        filas.append([
            "<b>%s</b>" % emp,
            ", ".join(estudiantes_de(emp)),
            sector, etapa, _barra(avance), badge(_estado_vis(rev), col),
            badge("Con evidencia" if evid else "Sin evidencia",
                  "b-azul" if evid else "b-amarillo"),
            act,
            '<a class="btn btn-sm btn-secundario" '
            'href="emprendimiento-expediente.html?emp=%s">Abrir</a>' % _slug(emp),
        ])
    filtros = (_filtro("Filtrar por etapa",
                       ["Todas las etapas", "FASE 1 - Ideación", "FASE 2 - Prototipo",
                        "FASE 3 - Validación"], 3)
               + _filtro("Filtrar por sector",
                         ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                          "Muebles"], 2)
               + _filtro("Filtrar por estado de revisión",
                         ["Todos los estados", "En revisión", "Devuelta",
                          "Requieren atención"], 5,
                         valores={"Requieren atención": "En revision|Devuelta"})
               + _filtro("Filtrar por evidencia",
                         ["Toda la evidencia", "Con evidencia", "Sin evidencia"], 6)
               + _contador(len(filas)))
    tabla_proy = _zona(toolbar(filtros=filtros) + _tabla_con_titulo(
        "Proyectos asignados al docente",
        ["Emprendimiento", "Estudiante", "Sector", "Etapa", "Avance",
         "Estado de revisión", "Evidencia", "Última actividad", "@ACC"], filas))

    opts = '<option value="">Todos los estudiantes</option>'
    for est in TODOS_ESTUDIANTES:
        if emprendimientos_de(est):
            opts += '<option value="%s">%s</option>' % (est, est)
    selector = ('<div class="campo"><label for="sel-estudiante">Ver emprendimientos '
                'por estudiante</label>'
                '<select class="filtro" id="sel-estudiante" '
                'aria-label="Ver emprendimientos por estudiante">%s</select>'
                '<div class="ayuda">Al elegir un estudiante se muestran sus '
                "emprendimientos como pestañas.</div></div>" % opts)

    # El selector queda justo encima de la tabla; al elegir un estudiante, el
    # resultado intercambia la tabla por las pestañas de sus emprendimientos.
    resultado = ('<div id="resultado-emprendimientos">'
                 + '<div id="lista-emprendimientos">' + tabla_proy + "</div>"
                 + '<div id="detalle-estudiante" hidden>'
                 + _secciones_estudiantes() + "</div>"
                 + "</div>")

    # Pestañas Tarjetas / Tabla con el estilo del rol Estudiante.
    cuerpo += ('<div id="vista-emprendimientos">'
               + _tabs([("tarjetas", "Tarjetas"), ("tabla", "Tabla")])
               + _panel("tarjetas", tarjetas, activo=True)
               + _panel("tabla", selector + resultado)
               + "</div>")
    return shell(R, "emprendimientos", "Emprendimientos asignados", cuerpo,
                 migas=["Inicio", "Emprendimientos asignados"],
                 sub="Tus emprendimientos asignados y los de cada estudiante.")


# --- 26. Expediente ----------------------------------------------------------
def _exp_metricas(emp):
    """Metricas reales del emprendimiento (antes eran cifras de Sabor y Sabe)."""
    a = INFO_EMP[emp]
    av = AVANCES_EMP[emp]
    prom = int(round(sum(x[3] for x in av) / max(1, len(av))))
    tareas = [t for t in TAREAS_DOC if t[1] == emp]
    hechas = len([t for t in tareas if t[5] == "Completada"])
    por_cal = len([t for t in tareas if t[5] == "En revision"])
    pct_ev = int(round(hechas * 100 / max(1, len(tareas))))
    pend = next((t[4] for t in tareas if t[5] == "En revision"), "")
    return metricas([
        ("trend", "Avance de fase", str(a[3]), "%", a[3], a[2]),
        ("medalla", "Promedio de calificación", str(prom), "/ 100", prom,
         "%d avances calificados" % len(av)),
        ("clipboard", "Tareas con evidencia", str(hechas), "/ %d" % len(tareas),
         pct_ev, "%d sin adjuntar" % (len(tareas) - hechas)),
        ("checklist", "Calificaciones por hacer", str(por_cal), "",
         min(100, por_cal * 20),
         ("Vence el %s" % pend) if pend else "Sin pendientes"),
    ])


def _exp_panel_avances(emp):
    filas = [[fecha, fase, desc, badge("%d de 100" % nota, "b-azul"),
              _acc(_a("eye", "Ver avance", "avance-detalle.html"))]
             for fecha, fase, desc, nota, _evid in AVANCES_EMP[emp]]
    return _tabla_con_titulo(
        "Avances y calificaciones de %s" % emp,
        ["Fecha", "Fase", "Descripción del avance", "Calificación", "@ACC"], filas)


def _exp_panel_tareas(emp):
    cols = [("Por calificar", []), ("Devueltas al estudiante", []),
            ("Calificadas", [])]
    for titulo, _e, estu, prio, vence, estado in TAREAS_DOC:
        if _e != emp:
            continue
        if estado == "En revision":
            pie = _lnk("tarea-detalle.html", "check", "Calificar",
                       "btn btn-sm btn-primario")
            col = 0
        elif estado == "Devuelta":
            pie = _lnk("tarea-detalle.html", "eye", "Ver",
                       "btn btn-sm btn-secundario")
            col = 1
        elif estado == "Completada":
            pie = _lnk("tarea-detalle.html", "eye", "Ver",
                       "btn btn-sm btn-secundario")
            col = 2
        else:
            pie = _lnk("tareas.html", "eye", "Revisar",
                       "btn btn-sm btn-secundario")
            col = 0
        cols[col][1].append((titulo, "%s · Vence %s" % (estu, vence),
                             badge(prio, PRIO_AS[prio]), pie))
    return kanban(cols)


def _exp_panel_asesorias(emp):
    filas = [[cod, fecha, mod, badge(estado, ESTADOS_AS[estado]),
              _acc(_a("eye", "Ver asesoría", "asesorias.html"))]
             for cod, e, _estu, _sec, estado, fecha, mod, _tema in ASESORIAS
             if e == emp]
    return (tabla(["Código", "Fecha y hora", "Modalidad", "Estado", "@ACC"], filas)
            + '<div class="form-acciones">'
            + _lnk("asesorias.html", "chat", "Ver todas las asesorías",
                   "btn btn-secundario") + "</div>")


def _exp_panel_diag(emp):
    d = DIAG_EMP[emp]
    return (lista_def([
        ("Última revisión", d["ultima_revision"]),
        ("Puntaje heurístico", "%s de 10" % d["puntaje"]),
        ("Fases completadas", d["fases_completadas"]),
        ("Recomendaciones enviadas", d["recomendaciones"]),
    ]) + '<div class="form-acciones">' + _lnk(
        "diagnostico-revision.html", "clipboard", "Revisar y recomendar")
        + "</div>")


def _exp_panel_comentarios(emp):
    return ('<div class="comentarios">'
            + "".join(_comentario(a, f, t) for a, f, t in COMENTARIOS_EMP[emp])
            + "</div>"
            + '<div class="comentario-form">'
            + _campo_libre("com-obs-%s" % _slug(emp), "Observación",
                           "Escribe una observacion para el estudiante")
            + _bt("publicar-comentario", "enviar", "Publicar comentario")
            + "</div>")


def _exp_seccion(emp, activo=False):
    """Expediente completo de un emprendimiento, listo para conmutar con ?emp=."""
    a = INFO_EMP[emp]
    cuerpo = _exp_metricas(emp) + _sep()
    cuerpo += '<div class="grid g-2-1"><div class="pila-exp">'
    cuerpo += _tabs_local([
        ("avances", "Avances"), ("tareas", "Tareas"),
        ("asesorias", "Asesorías"), ("diag", "Diagnóstico"),
        ("com", "Comentarios")])
    cuerpo += _panel_local("avances", _exp_panel_avances(emp), activo=True)
    cuerpo += _panel_local("tareas", _exp_panel_tareas(emp))
    cuerpo += _panel_local("asesorias", _exp_panel_asesorias(emp))
    cuerpo += _panel_local("diag", _exp_panel_diag(emp))
    cuerpo += _panel_local("com", _exp_panel_comentarios(emp))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Nombre", emp),
        ("Tipo", TIPO_EMP[emp]),
        ("Sector", a[1]),
        ("Etapa", a[2]),
    ]))
    cuerpo += card("Estudiantes del grupo", lista_def(
        [(n, "%s · %s" % (cod, sede)) for n, cod, sede in roster_de(emp)])
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
    return ('<section data-exp-perfil="%s" data-exp-nombre="%s"%s>%s</section>'
            % (_slug(emp), emp, "" if activo else " hidden", cuerpo))


def emprendimiento_expediente():
    """Expediente académico por emprendimiento (se elige con ?emp=<slug>)."""
    primero = ASIGNADOS[0][0]
    cuerpo = "".join(_exp_seccion(a[0], activo=(i == 0))
                     for i, a in enumerate(ASIGNADOS))
    return shell(R, "emprendimientos", primero, cuerpo,
                 migas=["Inicio", "Emprendimientos asignados", primero],
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
        ("Estudiante", "Mariana López"),
        ("Fase", "FASE 2 - Prototipo"),
        ("Fecha", "12 nov 2024"),
        ("Estado de revisión", badge("En revisión", "b-amarillo")),
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
               + select("Estado de revisión",
                        ["Pendiente", "En revisión", "Calificada", "Devuelta"],
                        valor="En revisión")
               + select("Evidencia", ["Con evidencia", "Sin evidencia"],
                        valor="Con evidencia"))
    izq += card("Descripción del avance", campo(
        "Descripción", alto=True,
        valor="Prototipo de empaque listo para 20 unidades, con ficha técnica y "
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
def _diag_kpis(emp):
    """KPIs del emprendimiento elegido (o del conjunto si emp es None).

    Cada tarjeta es un enlace con vista previa: lleva al expediente del
    emprendimiento, a la revision de diagnosticos o a sus tareas. En el
    contexto agregado ("Todos") los destinos son las vistas generales."""
    if emp:
        d = DIAG_EMP[emp]
        n_fases = int(d["fases_completadas"].split(" de ")[0])
        n_tareas, tot_tareas = [int(x) for x in d["tareas_clave"].split(" de ")]
        pend = tot_tareas - n_tareas
        fases = " · ".join("F%d %d %%" % (i + 1, f[1])
                           for i, f in enumerate(d["fases"]))
        return ('<div class="grid g-4">'
                + _metrica_enlace(
                    "trend", "Fases completadas", str(n_fases), "de 4",
                    d["pct_fases"], d["fases_completadas"] + " fases",
                    "emprendimiento-expediente.html?emp=%s" % _slug(emp),
                    "Fases de %s" % emp, fases, "Ver el expediente",
                    aria_val="%s de 4" % n_fases)
                + _metrica_enlace(
                    "clipboard", "Diagnósticos", "3", "", 100,
                    "3 de 3 registrados", "diagnostico-revision.html",
                    "Diagnósticos de %s" % emp,
                    "3 registrados · Último: %s · %s de 10"
                    % (d["ultima_revision"], d["puntaje"]),
                    "Ver los diagnósticos")
                + _metrica_enlace(
                    "checklist", "Tareas clave", str(n_tareas),
                    "de %d" % tot_tareas, d["pct_tareas"],
                    "%d pendiente%s" % (pend, "" if pend == 1 else "s"),
                    "tareas.html?emp=" + quote_plus(emp),
                    "Tareas clave de %s" % emp,
                    "%d de %d completadas · %d pendiente%s"
                    % (n_tareas, tot_tareas, pend, "" if pend == 1 else "s"),
                    "Ver las tareas",
                    aria_val="%d de %d" % (n_tareas, tot_tareas))
                + _metrica_enlace(
                    "medalla", "Puntaje heurístico", d["puntaje"], "/ 10",
                    int(float(d["puntaje"]) * 10), "Revisión del docente",
                    "diagnostico-revision.html", "Puntaje de %s" % emp,
                    "%s de 10 · Recomendación: %s"
                    % (d["puntaje"], d["recomendaciones"]),
                    "Ver la revisión", aria_val="%s de 10" % d["puntaje"])
                + "</div>")
    n_fases = sum(int(DIAG_EMP[e]["fases_completadas"].split(" de ")[0])
                  for e in EMPRESAS)
    n_tareas = sum(int(DIAG_EMP[e]["tareas_clave"].split(" de ")[0])
                   for e in EMPRESAS)
    tot_tareas = sum(int(DIAG_EMP[e]["tareas_clave"].split(" de ")[1])
                     for e in EMPRESAS)
    tot_fases = 4 * len(EMPRESAS)
    pct_fases = int(round(n_fases * 100 / tot_fases))
    pct_tareas = int(round(n_tareas * 100 / max(1, tot_tareas)))
    ultima = max((DIAG_EMP[e]["ultima_revision"] for e in EMPRESAS),
                 key=_fecha_orden)
    return ('<div class="grid g-4">'
            + _metrica_enlace(
                "maleta", "Emprendimientos", str(len(EMPRESAS)), "", 100,
                "Cartera del docente", "emprendimientos.html",
                "Tus emprendimientos",
                "%s · %d en cartera" % (" · ".join(EMPRESAS[:3]),
                                        len(EMPRESAS)),
                "Ver emprendimientos")
            + _metrica_enlace(
                "trend", "Fases completadas", str(n_fases),
                "de %d" % tot_fases, pct_fases, "%d%% del total" % pct_fases,
                "emprendimientos.html", "Avance por fases",
                "%d de %d fases completadas en %d emprendimientos"
                % (n_fases, tot_fases, len(EMPRESAS)), "Ver emprendimientos",
                aria_val="%d de %d" % (n_fases, tot_fases))
            + _metrica_enlace(
                "clipboard", "Diagnósticos", str(len(DIAGNOSTICOS)), "", 100,
                "%d por emprendimiento" % (len(DIAGNOSTICOS) // len(EMPRESAS)),
                "diagnostico-revision.html", "Diagnósticos del periodo",
                "%d registrados · Última revisión: %s"
                % (len(DIAGNOSTICOS), ultima), "Ver la revisión")
            + _metrica_enlace(
                "checklist", "Tareas clave", str(n_tareas),
                "de %d" % tot_tareas, pct_tareas,
                "%d pendientes" % (tot_tareas - n_tareas), "tareas.html",
                "Tareas clave del programa",
                "%d de %d completadas · %d pendientes"
                % (n_tareas, tot_tareas, tot_tareas - n_tareas),
                "Ver las tareas",
                aria_val="%d de %d" % (n_tareas, tot_tareas))
            + "</div>")


def _diag_fases(emp):
    if emp:
        return DIAG_EMP[emp]["fases"]
    out = []
    for i, (fase, _v, color) in enumerate(DIAG_EMP[EMPRESAS[0]]["fases"]):
        prom = int(round(sum(DIAG_EMP[e]["fases"][i][1] for e in EMPRESAS)
                         / len(EMPRESAS)))
        out.append((fase, prom, color))
    return out


def _diag_comportamiento(emp):
    if emp:
        return DIAG_EMP[emp]["comportamiento"]
    return [int(round(sum(DIAG_EMP[e]["comportamiento"][i] for e in EMPRESAS)
                       / len(EMPRESAS)))
            for i in range(len(COMP_LABELS))]


def _diag_historial(emp):
    if emp:
        return linea_tiempo([
            (dia, mes, titulo, "%s · %s" % (emp, sub), href)
            for dia, mes, titulo, sub, href in DIAG_EMP[emp]["historial"]])
    items = []
    for e in EMPRESAS:
        dia, mes, titulo, sub, href = DIAG_EMP[e]["historial"][0]
        items.append((dia, mes, titulo, "%s · %s" % (e, sub), href))
    return linea_tiempo(items)


def _diag_datos(emp):
    if emp:
        a = INFO_EMP[emp]
        return card("Datos del emprendimiento", lista_def([
            ("Emprendimiento", emp),
            ("Sector", a[1]),
            ("Etapa", a[2]),
            ("Grupo", " · ".join(estudiantes_de(emp))),
        ]))
    return card("Datos de los emprendimientos", lista_def([
        (e, "%s · %s" % (INFO_EMP[e][1], INFO_EMP[e][2])) for e in EMPRESAS]))


def _diag_contexto(emp, activo=False):
    """Bloque de informacion que cambia al elegir el emprendimiento."""
    clave = _slug(emp) if emp else "todos"
    titulo_fases = "Avance por fases" if emp else "Avance por fases (promedio)"
    comportamiento = _diag_comportamiento(emp)
    cuerpo = _diag_kpis(emp)
    cuerpo += '<div class="grid g-2">'
    cuerpo += card(titulo_fases, progreso_fases(_diag_fases(emp)))
    cuerpo += card("Comportamiento", barras_h(
        "", "", COMP_LABELS, comportamiento, maximo=100, unidad="%"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2-1"><div class="grid">'
    cuerpo += card("Historial de diagnósticos" if emp
                   else "Historial de diagnósticos recientes",
                   _diag_historial(emp))
    cuerpo += "</div><div class=\"grid\">%s</div></div>" % _diag_datos(emp)
    return ('<div data-diag-contexto="%s"%s>%s</div>'
            % (clave, "" if activo else " hidden", cuerpo))


def _diag_filtro_emp():
    opts = '<option value="" data-slug="todos">Todos los emprendimientos</option>'
    for e in EMPRESAS:
        opts += '<option value="%s" data-slug="%s">%s</option>' % (e, _slug(e), e)
    return ('<select class="filtro" data-filtro="off" data-diag-emp '
            'data-filtro-col="1" aria-label="Filtrar por emprendimiento">%s</select>' % opts)


def _diag_filtro_proyecto():
    opts = '<option value="">Todos los proyectos</option>'
    for e in EMPRESAS:
        opts += "<option>%s</option>" % e
    return ('<select class="filtro" data-filtro="1" data-diag-proyecto '
            'data-filtro-col="1" aria-label="Filtrar por proyecto o grupo">%s</select>'
            % opts)


def diagnostico():
    cuerpo = callout(
        "Elige el emprendimiento y filtra por estudiante o proyecto. El "
        "diagnóstico se calcula por la <b>completación de las 4 fases</b> o por "
        "una serie de <b>tareas clave</b> completadas.", "bombilla")
    cuerpo += _sep()
    filtros = (_diag_filtro_emp()
               + _filtro("Filtrar por estudiante",
                         ["Todos los estudiantes"] + TODOS_ESTUDIANTES, 2)
               + _diag_filtro_proyecto()
               + _filtro("Filtrar por origen del diagnóstico",
                         ["Todos los orígenes", "Fases y tareas clave",
                          "Solo por fases (4)", "Solo por tareas clave"], 0)
               + _filtro("Filtrar por estado",
                         ["Todos los estados", "Completado", "En curso",
                          "Pendiente"], 4)
               + _contador(len(DIAGNOSTICOS)))
    filas = [['<span>%s</span><div class="celda-sub">%s</div>' % (origen, detalle),
              emp, estu, tema,
              badge(estado, "b-azul" if estado == "Completado"
                    else "b-amarillo" if estado == "En curso" else "b-linea"),
              fecha,
              _acc(_a("eye", "Revisar", "diagnostico-revision.html"))]
             for origen, detalle, emp, estu, tema, estado, fecha in DIAGNOSTICOS]
    contextos = _diag_contexto(None, activo=True)
    contextos += "".join(_diag_contexto(e) for e in EMPRESAS)
    pag = _paginas_doc(1, 5, len(filas), "tabla-diagnosticos")
    cuerpo += _zona(toolbar(buscar=True, filtros=filtros)
                    + contextos
                    + _tabla_con_titulo(
                        "Diagnósticos por fase o tareas clave",
                        ["Origen", "Emprendimiento", "Estudiante", "Tema", "Estado",
                         "Fecha", "@ACC"], filas, pag=pag))
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
        ("trend", "Puntaje heurístico", "7.8", "/ 10", 78, "28 oct 2024"),
        ("clipboard", "Fases completadas", "1", "de 4", 25, "FASE 1"),
        ("checklist", "Tareas clave", "2", "de 5", 40, "3 pendientes"),
    ])
    cuerpo += _sep()
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la revisión", lista_def([
        ("Estudiante", "Mariana López"),
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
    cuerpo += card("Pendientes de revisión", _tabla_con_titulo(
        "Pendientes de revisión del diagnóstico",
        ["Estudiante", "Emprendimiento", "Fecha", "@ACC"],
        [["Jhon Ospina", "Krea Textil", "30 oct 2024",
          _acc(_a("eye", "Revisar", "diagnostico-revision.html"))],
         ["Sofía Ramírez", "Aromas del Sur", "02 nov 2024",
          _acc(_a("eye", "Revisar", "diagnostico-revision.html"))]]))
    cuerpo += "</div></div>"
    return shell(R, "diagnostico", "Revisión del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico", "Revisión"],
                 sub="Revisa los resultados y deja recomendaciones al estudiante.",
                 acciones=_lnk("diagnostico.html", "izq", "Volver",
                               "btn btn-secundario"))


def _cuerpo_tarea():
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
            badge(_estado_vis(estado), ESTADO_TAREA[estado]),
            _acc(*acciones),
        ])
    empresas_tar = [e for e in EMPRESAS if any(t[1] == e for t in TAREAS_DOC)]
    filtros = (_filtro("Filtrar por estado",
                       ["Todos los estados", "Pendiente", "En revision",
                        "Devuelta", "Completada"], 5,
                       etiquetas={"En revision": "En revisión"})
               + _filtro("Filtrar por prioridad",
                         ["Toda la prioridad", "Alta", "Media", "Baja"], 3)
               + _filtro("Filtrar por emprendimiento",
                         ["Todos los emprendimientos"] + empresas_tar, 1)
               + _contador(len(filas)))
    cuerpo = callout("La tarea se considera <b>completada</b> cuando el estudiante "
                     "adjunta al menos una evidencia.", "bombilla")
    cuerpo += '<div id="form-tarea" hidden>' + _cuerpo_tarea() + "</div>"
    cuerpo += _sep()
    pag = _paginas_doc(1, 5, len(filas), "tabla-tareas")
    cuerpo += _zona(toolbar(filtros=filtros)
                    + _tabla_con_titulo("Tareas asignadas por revisar",
                                        ["Tarea", "Emprendimiento", "Estudiante",
                                         "Prioridad", "Vence", "Estado", "@ACC"], filas,
                                        pag=pag))
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
        ("Estudiante", "Mariana López"),
        ("Entregada", "12 nov 2024, 16:40"),
        ("Vence", "12 nov 2024"),
    ]))
    der += card("Calificación", circular(92, "Calificación", "Sobre 100")
                + campo("Puntaje (0 a 100)", tipo="number", valor="92")
                + select("Resultado",
                         ["Aprobada", "En revisión", "Devuelta"], valor="Aprobada"))
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
        ("Estudiante", "Lucía Fernández"),
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


# --- 35. Eventos (recomendaciones a estudiantes) -----------------------------
def _badge_modalidad(mod):
    return badge(mod, "b-azul" if mod == "Virtual" else "b-neutra",
                 "play" if mod == "Virtual" else "")


# Vistas de detalle de cada evento para el docente (espejo del rol Estudiante).
EVENTO_ARCHIVO = {
    "Startup Minuto de Dios": "evento-detalle-startup.html",
    "Capacitación en modelado de negocios": "evento-detalle-capacitacion.html",
    "Asesoría grupal de empleabilidad": "evento-detalle-asesoria-grupal.html",
    "Showroom de emprendimientos": "evento-detalle-showroom.html",
}


def _recomendar_form(evento):
    """Selector para recomendar un evento por emprendimiento o por estudiante.

    El desplegable marca o quita a todo el grupo de un emprendimiento (o a todos
    los estudiantes); la lista de casillas permite ajustar uno por uno despues.
    """
    opts = ('<option value="__todos__">Todos mis estudiantes</option>'
            '<option value="__ninguno__">Quitar selección</option>')
    for emp in EMPRESAS:
        opts += '<option value="%s">%s</option>' % (emp, emp)
    cajas = ""
    for est in TODOS_ESTUDIANTES:
        emps = "|".join(emprendimientos_de(est))
        cajas += ('<label class="chk"><input type="checkbox" data-est="%s" '
                  'data-emp="%s"> %s</label>' % (est, emps, est))
    return (
        '<div data-recomendar>'
        '<div class="campo"><label for="sel-grupo">Seleccionar por emprendimiento'
        '</label><select class="filtro" id="sel-grupo" data-recomendar-grupo>%s</select>'
        '</div>'
        '<div class="nota-foot">Elige un emprendimiento para marcar todo su grupo; '
        'después puedes ajustar la selección estudiante por estudiante.</div>'
        '<div class="grid g-2" style="gap:0 18px">%s</div>'
        '</div>' % (opts, cajas)
    )


def eventos():
    """Eventos del programa: el docente recomienda a sus estudiantes participar.

    Sigue el patron de la vista de Eventos del estudiante (tabla + calendario +
    tarjeta lateral). Cada evento abre su detalle, con la informacion completa y
    la recomendacion a estudiantes individuales o a todo un emprendimiento.
    """
    filas = []
    for nombre, tipo, fecha, mod, org, _cupos in EVENTOS:
        arch = EVENTO_ARCHIVO[nombre]
        filas.append([
            "<b>%s</b>" % nombre, tipo, fecha, _badge_modalidad(mod), org,
            _acc(_a("eye", "Ver evento", arch),
                 _a("enviar", "Recomendar a estudiantes", arch)),
        ])
    enviadas = []
    for est, ev, estado, fecha in RECOMENDACIONES:
        col = "b-linea" if estado == "Aceptada" else "b-amarillo"
        enviadas.append([
            "<b>%s</b>" % est, ev, badge(estado, col), fecha,
            _acc(_a("eye", "Ver evento", EVENTO_ARCHIVO[ev])),
        ])
    cuerpo = metricas([
        ("calendar", "Eventos disponibles", "%d" % len(EVENTOS), "", 60, None),
        ("enviar", "Recomendaciones enviadas", "%d" % len(RECOMENDACIONES), "", 45,
         "+2 este mes"),
        ("check", "Recomendaciones aceptadas", "2", "", 40, None),
    ])
    cuerpo += _sep()
    cuerpo += (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Próximos eventos", tabla(
            ["Evento", "Tipo", "Fecha y hora", "Modalidad", "Organizador", "@ACC"],
            filas, id="tabla-eventos"))
        + card("Recomendaciones enviadas", tabla(
            ["Estudiante", "Evento", "Estado", "Fecha", "@ACC"],
            enviadas, id="tabla-recomendaciones"))
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Calendario de noviembre",
               '<div style="border:1px solid #bbbbbb;border-radius:8px;overflow:hidden">'
               + calendario("noviembre", 2024) + "</div>")
        + card("Cómo recomendar un evento",
               '<div style="font-size:13px;color:#162644">Abre <b>Ver evento</b> en '
               "la tabla, revisa la información completa y elige a tus estudiantes: "
               "por emprendimiento (todo el grupo) o uno por uno. Ellos reciben el "
               "aviso en su bandeja y confirman su participación.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Eventos del programa para recomendar a tus estudiantes.")


# --- 36-39. Detalle del evento (docente) -------------------------------------
def _evento_detalle_doc(evento, fecha, modalidad, organizador, lugar, cupos, consiste,
                        extra_html="", virtual=False):
    """Detalle del evento para el docente: información completa + recomendar.

    Espeja el detalle que ve el Estudiante (misma información del evento), pero la
    acción no es inscribirse: el docente recomienda el evento a estudiantes
    individuales o a todo un emprendimiento.
    """
    datos = lista_def([
        ("Fecha y hora", fecha),
        ("Modalidad", _badge_modalidad(modalidad)),
        ("Lugar", lugar),
        ("Organiza", organizador),
        ("Cupos disponibles", cupos),
    ])
    acceso = ""
    if virtual:
        acceso = card("Acceso al evento virtual",
                      lista_def([
                          ("Enlace", '<a href="https://meet.minutodedios.edu.co/'
                                     'capacitacion-modelado">meet.minutodedios.edu.co/'
                                     "capacitacion-modelado</a>"),
                          ("ID de la reunión", "482 913 776"),
                          ("Requisitos", "Conexión estable y audífonos."),
                      ]),
                      hint="<span>Los estudiantes lo reciben al confirmar</span>")
    cuerpo = (
        callout("En qué consiste: " + consiste, "libro")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(evento, datos + ('<div class="divisor"></div>' + extra_html
                                if extra_html else ""))
        + acceso
        + card("Recomendar a estudiantes",
               _recomendar_form(evento) + '<div class="divisor"></div>'
               + _campo_libre("msg-recomendar", "Mensaje (opcional)",
                              "Escribe un mensaje motivando la participación.")
               + '<div style="display:flex;justify-content:flex-end;gap:10px;'
                 'margin-top:14px">'
               + '<a class="btn btn-secundario" href="eventos.html">Cancelar</a>'
               + _bt("guardar-recomendaciones", "enviar", "Enviar recomendación")
               + "</div>",
               hint="<span>Individual o por emprendimiento</span>")
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Cómo funciona",
               '<div style="font-size:13px;color:#162644">Elige el emprendimiento '
               "para marcar a todo su grupo o selecciona estudiantes uno por uno, "
               "escribe un mensaje y envía la recomendación. Cada estudiante la "
               "recibe en su bandeja de notificaciones y confirma su "
               "participación.</div>")
        + card("Después de recomendar",
               '<div style="font-size:13px;color:#162644">Sigue el estado en '
               "<b>Eventos</b>: verás quién aceptó la recomendación y quién la "
               "tiene pendiente.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", evento, cuerpo,
                 migas=["Inicio", "Eventos", evento],
                 sub="Detalle del evento y recomendación a tus estudiantes.",
                 acciones='<a class="btn btn-secundario" href="eventos.html">%s Volver</a>'
                          % ico("izq", 16))


def evento_detalle_startup():
    return _evento_detalle_doc(
        "Startup Minuto de Dios", "21 nov 2024, 08:00 - 12:00", "Presencial",
        "Dirección Académica", "Auditorio principal, sede Norte", "40 cupos",
        "una conferencia para presentar la ruta del programa Startup Minuto de Dios, "
        "los criterios de evaluación y los testimonios de emprendimientos que ya "
        "pasaron por el proceso. Al final hay un espacio de preguntas con la "
        "dirección académica.")


def evento_detalle_capacitacion():
    return _evento_detalle_doc(
        "Capacitación en modelado de negocios", "21 nov 2024, 14:00 - 16:30",
        "Virtual", "Coordinación Académica", "Sala virtual institucional", "120 cupos",
        "un taller virtual para construir el modelo de negocio (clientes, propuesta "
        "de valor, canales e ingresos) con ejercicios guiados sobre el propio "
        "emprendimiento del estudiante.",
        virtual=True)


def evento_detalle_asesoria_grupal():
    return _evento_detalle_doc(
        "Asesoría grupal de empleabilidad", "26 nov 2024, 10:00 - 11:30", "Presencial",
        "Bienestar Estudiantil", "Sala de reuniones 204", "25 cupos",
        "una asesoría en grupo sobre empleabilidad y emprendimiento: cómo presentar "
        "el proyecto, armar la hoja de vida y preparar una entrevista.",
        extra_html=steps(["Recomienda el evento a los estudiantes del grupo.",
                          "Ellos llevan su proyecto y su hoja de vida.",
                          "Participan y reciben la retroalimentación del grupo.",
                          "Se registra el acta de participación."]))


def evento_detalle_showroom():
    return _evento_detalle_doc(
        "Showroom de emprendimientos", "02 dic 2024, 09:00 - 15:00", "Presencial",
        "Dirección Académica", "Plaza central, sede Norte", "60 cupos",
        "una muestra abierta donde cada estudiante presenta su emprendimiento a "
        "visitantes y jurados. Habrá un espacio asignado por emprendimiento y una "
        "rúbrica de evaluación.",
        extra_html='<div class="nota-foot">El montaje del stand está a cargo de cada '
                   "emprendimiento; la institución entrega la mesa y la "
                   "señalización.</div>")


# --- 37. Mi perfil (dashboard de la cuenta) ----------------------------------
def _tarjeta_emp_asignado(emp):
    """Tarjeta de un emprendimiento asignado dentro del perfil del docente."""
    a = INFO_EMP[emp]
    sector, etapa, avance = a[1], a[2], a[3]
    grupo = estudiantes_de(emp)
    meta = ("1 estudiante" if len(grupo) == 1
            else "%d estudiantes" % len(grupo)) + " · " + sector
    return tarjeta_emp("maleta", emp, meta, avance, etapa, "%d%%" % avance)


def perfil():
    """Perfil del docente: dashboard de la cuenta.

    Cabecera con foto y datos, sus emprendimientos asignados y el estado de la
    cuenta. La edición de los datos vive en Configuración (configuracion.html).
    """
    cuerpo = (
        '<div class="card"><div class="card-body">'
        '<div class="perfil-cab">'
        '<div class="perfil-foto"><span>CM</span></div>'
        '<div class="perfil-datos">'
        '<h2 class="perfil-nombre">Carlos Alejandro Mendoza Rios</h2>'
        '<div class="perfil-usuario">carlos.mendoza@sgemd.edu.co &middot; '
        "Docente de emprendimiento</div>"
        '<p class="perfil-bio">Acompañas a los emprendimientos del programa '
        "Startup Minuto de Dios: revisas avances y diagnósticos, calificas tareas "
        "y confirmas las asesorías de tus estudiantes.</p>"
        '<div class="perfil-meta">'
        '<span>%s DOCENTE</span>'
        '<span>%s Rectoría Bogotá &middot; Sede Norte</span>'
        '<span>%s %d emprendimientos asignados</span>'
        '<span>%s %d estudiantes a cargo</span>'
        "</div></div>"
        '<div class="perfil-acciones">'
        '<a class="btn btn-secundario" href="configuracion.html">%s Editar perfil</a>'
        "</div></div></div></div>"
        % (ico("user", 15), ico("home", 15), ico("maleta", 15), len(ASIGNADOS),
           ico("users", 15), len(TODOS_ESTUDIANTES), ico("edit", 15))
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Mis emprendimientos asignados",
               '<div class="grid g-2">'
               + "".join(_tarjeta_emp_asignado(a[0]) for a in ASIGNADOS)
               + "</div>")
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Estado de la cuenta", lista_def([
            ("Estado", badge("Activo", "b-azul", "check")),
            ("Emprendimientos asignados", "%d" % len(ASIGNADOS)),
            ("Asesorías del mes", "14"),
            ("Tareas por revisar", "9"),
            ("Fecha de registro", "15 ago 2024"),
        ]),
            accion='<button class="btn btn-secundario btn-sm" data-accion="cerrar-sesion">%s '
                   "Cerrar sesión</button>" % ico("salir", 15))
        + card("Notificaciones", '<div style="font-size:13px;color:#162644">Tienes '
               "3 avisos sin leer: una asesoría por confirmar, una evidencia por "
               "calificar y un diagnóstico por revisar.</div>",
               accion='<a class="btn btn-secundario btn-sm" href="notificaciones.html">%s '
                      "Ver notificaciones</a>" % ico("bell", 15))
        + "</div></div>"
        + '<div style="height:20px"></div>'
        + '<div style="display:flex;gap:10px;flex-wrap:wrap">'
        + '<a class="btn btn-acento" href="configuracion.html">%s '
        "Editar perfil y configuración</a>" % ico("edit", 16)
        + "</div>"
    )
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Tu cuenta, tus emprendimientos asignados y tu actividad.")


# --- 38. Configuracion (edicion del perfil) ----------------------------------
def configuracion():
    """Configuración del docente: datos, ubicación, cuenta y contraseña.

    Es la pantalla de edición que se abre desde el perfil (dashboard). Los campos
    institucionales los mantiene el ADMINISTRADOR.
    """
    cuerpo = (
        callout("Aquí actualizas tus datos y la configuración de tu cuenta. Los "
                "campos con el candado los mantiene el <b>ADMINISTRADOR</b> de la "
                "institución.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Datos personales",
               '<div class="grid g-2" style="gap:0 16px">'
               + campo("Nombres", valor="Carlos Alejandro")
               + campo("Apellidos", valor="Mendoza Rios")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + select("Tipo de documento", ["CC", "CE"], valor="CC", req=True)
               + campo("Número de documento", valor="79 456 123",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Correo institucional", valor="carlos.mendoza@sgemd.edu.co",
                       tipo="email", bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + campo("Correo personal", valor="carlos.mendoza@correo.com",
                       tipo="email")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Teléfono", valor="+57 300 555 0142", tipo="tel", req=True)
               + campo("Título / especialidad",
                       valor="Magíster en Innovación y Emprendimiento")
               + "</div>"
               + campo("Área de conocimiento", valor="Emprendimiento e innovación")
               + '<div style="display:flex;justify-content:flex-end;gap:10px">'
               + '<button class="btn btn-secundario" data-accion="cancelar-perfil">'
                 "Cancelar</button>"
               + '<button class="btn btn-primario" data-accion="guardar-perfil">%s '
                 "Guardar cambios</button>" % ico("check", 16)
               + "</div>")
        + card("Ubicación",
               '<div class="grid g-2" style="gap:0 16px">'
               + select("Región / Rectoría",
                        ["Rectoría Bogotá", "Rectoría Medellín", "Rectoría Cali"],
                        valor="Rectoría Bogotá")
               + select("Departamento",
                        ["Cundinamarca", "Antioquia", "Valle del Cauca"],
                        valor="Cundinamarca")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Ciudad", valor="Bogotá")
               + select("Sede", ["Sede Norte", "Sede Centro", "Sede Sur"],
                        valor="Sede Norte")
               + "</div>")
        + card("Configuraciones",
               _chk("Avisos de nuevas asesorías", True)
               + _chk("Recordatorios de tareas por revisar", True)
               + _chk("Resumen semanal por correo", False)
               + _chk("Recomendaciones de eventos a mis estudiantes", True))
        + card("Accesos y seguridad", lista_def([
            ("Último ingreso", "12 nov 2024, 07:42 · Bogotá"),
            ("Estado de la cuenta", badge("Activo", "b-azul", "check")),
            ("Rol", badge("DOCENTE", "b-azul", "user")),
        ]))
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Foto del docente",
               '<div style="display:flex;align-items:center;gap:16px">'
               '<div class="perfil-foto" style="width:96px;height:96px;flex:0 0 96px">'
               "<span>CM</span></div>"
               '<div><div style="font-size:13px;color:#162644">Sube una imagen en '
               "formato <b>PNG</b> o JPG, de máximo 2 MB.</div>"
               '<div style="margin-top:10px">'
               '<button class="btn btn-secundario btn-sm" data-accion="cambiar-foto">%s '
               "Subir imagen</button></div></div></div>" % ico("upload", 15))
        + card("Seguridad", lista_def([
            ("Contraseña", "Actualizada hace 3 meses"),
            ("Verificación en dos pasos", "Activada"),
            ("Último acceso", "Hoy, 07:42"),
        ]),
            accion='<a class="btn btn-secundario btn-sm" href="contrasena.html">%s '
                   "Cambiar contraseña</a>" % ico("lock", 15))
        + "</div></div>"
    )
    return shell(R, "configuracion", "Configuración", cuerpo,
                 migas=["Inicio", "Mi perfil", "Configuración"],
                 sub="Edita tus datos personales, tu ubicación y la configuración "
                     "de tu cuenta.",
                 acciones='<a class="btn btn-secundario" href="perfil.html">%s '
                          "Volver al perfil</a>" % ico("izq", 16))


# --- 39. Cambiar contrasena --------------------------------------------------
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


# --- 40. Notificaciones ------------------------------------------------------
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
             + _ba("marcar-leida", "check", "Marcar como leída")),
            ("reloj", "Revisión de diagnóstico pendiente",
             "Emprendimientos · Krea Textil · Sin revisar hace 3 días",
             "diagnostico.html", "alta",
             '<a class="btn btn-sm btn-primario" href="diagnostico.html">Revisar</a>'
             + _ba("marcar-leida", "check", "Marcar como leída")),
        ]),
        ("Hoy", [
            ("bell", "Solicitud de asesoría de Mariana López",
             "Asesorías · Modalidad mixta · 10:00",
             "asesoria-detalle.html", "media",
             '<a class="btn btn-sm btn-primario" href="asesoria-detalle.html">Confirmar</a>'
             + _ba("marcar-leida", "check", "Marcar como leída")),
            ("upload", "Evidencia enviada: Sabor y Sabe",
             "Emprendimientos · Prototipo · Entregada 16:40",
             "tarea-detalle.html", "media",
             '<a class="btn btn-sm btn-primario" href="tarea-detalle.html">Calificar</a>'
             + _ba("marcar-leida", "check", "Marcar como leída")),
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
        ("alerta", "Requieren acción hoy", "2", "", 40, None),
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
               "30 días después de resolverse.</p>")
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Lo que debes revisar, ordenado por urgencia.",
                 acciones=_bt("marcar-todo-leido", "check", "Marcar todo como leído",
                              "btn btn-secundario"))
