"""Comportamiento de las 50 pantallas, en un unico bloque inline.

Restricciones que condicionan el diseno:

  - Stitch sirve cada HTML como documento independiente y no resuelve rutas, asi
    que nada puede ser un modulo ES ni usar fetch: va en un <script> clasico.
  - No hay backend. La persistencia es localStorage y cada escritura va
    envuelta porque en el iframe de Stitch puede venir particionada o bloqueada.
  - Cada pantalla es autonoma, asi que el estado se nombra por pagina. La clave
    incluye la ruta para que dos listados del mismo dominio no se pisen.

La intencion de cada boton llega por `data-accion` (ver lib_ui.boton_accion)
o, cuando el boton tiene texto visible, se deduce de ese texto. No queda ningun
boton sin efecto observable.
"""

JS = r"""
(function () {
  "use strict";

  var CLAVE = "sgemd:v1:" + (location.pathname.split("/").slice(-2).join("/") || "raiz");

  /* Version de producto: solo la declaran las pantallas que la piden con
     data-inmersion="producto" en la etiqueta raiz del documento. El resto de
     roles conserva su texto. */
  var PRODUCTO = document.documentElement.getAttribute("data-inmersion") === "producto";
  function texto(a, b) { return PRODUCTO ? a : b; }

  /* --- util ------------------------------------------------------------ */
  function $(sel, raiz) { return (raiz || document).querySelector(sel); }
  function $$(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }
  function slug(txt) {
    return (txt || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  /* Una sola clave por pantalla. Las escrituras se fusionan en vez de
     pisarse: la pestana activa y la pagina de la tabla conviven en el objeto. */
  function guardar(parcial) {
    var estado = store(true) || {};
    Object.keys(parcial).forEach(function (k) { estado[k] = parcial[k]; });
    store(null, true, estado);
  }
  function store(leer, escribir, valor) {
    try {
      if (escribir) localStorage.setItem(CLAVE, JSON.stringify(valor));
      return leer ? JSON.parse(localStorage.getItem(CLAVE)) : null;
    } catch (e) { return null; }
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function icono(camino, d) {
    var caminos = Object.prototype.toString.call(camino) === "[object Array]" ? camino : [camino];
    var cuerpo = caminos.map(function (c) { return '<path d="' + c + '"/>'; }).join("");
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + (d || 16) + '" height="' + (d || 16) +
      '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + cuerpo + "</svg>";
  }
  var ICO = {
    check: "M20 6 9 17l-5-5",
    x: "M18 6 6 18M6 6l12 12",
    lapiz: "M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7",
    ojo: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z",
    alerta: "M12 9v4M12 17h.01",
    info: "M12 16v-4M12 8h.01",
    descargar: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    papelera: "M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14",
    lock: ["M7 11V7a5 5 0 0 1 10 0v4", "M4 11h16a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2Z"]
  };

  /* --- toast ----------------------------------------------------------- */
  var pila = null;
  function contenedorToast() {
    if (!pila) {
      pila = document.createElement("div");
      pila.className = "toast-pila";
      pila.setAttribute("role", "status");
      pila.setAttribute("aria-live", "polite");
      document.body.appendChild(pila);
    }
    return pila;
  }
  function toast(mensaje, tipo) {
    var t = document.createElement("div");
    t.className = "toast t-" + (tipo || "info");
    var ico = tipo === "ok" ? ICO.check : tipo === "error" ? ICO.alerta : ICO.info;
    t.innerHTML = icono(ico, 16) + "<span>" + esc(mensaje) + "</span>";
    contenedorToast().appendChild(t);
    setTimeout(function () { t.classList.add("va-fuera"); }, 3200);
    setTimeout(function () { t.remove(); }, 3700);
    return t;
  }

  /* --- modal ------------------------------------------------------------ */
  function abrirModal(titulo, cuerpoHTML, botones) {
    cerrarModal();
    var velo = document.createElement("div");
    velo.className = "modal-velo";
    velo.innerHTML =
      '<div class="modal" role="dialog" aria-modal="true" aria-label="' + esc(titulo) + '">' +
      '<div class="modal-head"><h2>' + esc(titulo) + '</h2>' +
      '<button class="icon-btn modal-x" aria-label="Cerrar">' + icono(ICO.x, 18) + "</button></div>" +
      '<div class="modal-cuerpo">' + cuerpoHTML + "</div>" +
      '<div class="modal-foot"></div></div>';
    var pie = $(".modal-foot", velo);
    (botones || [{ txt: "Cerrar", clase: "btn btn-secundario", cerrar: true }]).forEach(function (b) {
      var el = document.createElement("button");
      el.className = b.clase || "btn btn-secundario";
      el.textContent = b.txt;
      el.addEventListener("click", function () {
        if (b.alClic) b.alClic(velo);
        if (b.cerrar !== false) cerrarModal();
      });
      pie.appendChild(el);
    });
    document.body.appendChild(velo);
    document.body.classList.add("sin-scroll");
    $(".modal-x", velo).addEventListener("click", cerrarModal);
    velo.addEventListener("click", function (e) { if (e.target === velo) cerrarModal(); });
    var foco = $(".modal input, .modal select, .modal textarea, .modal-foot button", velo);
    if (foco) foco.focus();
    return velo;
  }
  function cerrarModal() {
    var v = $(".modal-velo");
    if (v) v.remove();
    document.body.classList.remove("sin-scroll");
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { cerrarModal(); cerrarDrawer(); }
  });

  /* --- drawer (notificaciones) ------------------------------------------ */
  function cerrarDrawer() {
    var d = $(".sg-drawer");
    if (d) d.remove();
    var o = $("#ov");
    if (o) o.classList.remove("visible");
  }
  function abrirDrawer(titulo, items) {
    cerrarDrawer();
    var d = document.createElement("aside");
    d.className = "sg-drawer";
    d.setAttribute("aria-label", titulo);
    d.innerHTML = '<div class="sg-drawer-head"><h2>' + esc(titulo) + "</h2>" +
      '<button class="icon-btn drawer-x" aria-label="Cerrar">' + icono(ICO.x, 18) + "</button></div>" +
      '<ul class="sg-drawer-lista">' + items.map(function (t) {
        return "<li>" + icono(ICO.info, 15) + "<span>" + esc(t) + "</span></li>";
      }).join("") + "</ul>";
    document.body.appendChild(d);
    var o = $("#ov");
    if (o) o.classList.add("visible");
    $(".drawer-x", d).addEventListener("click", cerrarDrawer);
  }

  /* --- confirmar -------------------------------------------------------- */
  function confirmar(titulo, texto, alConfirmar) {
    abrirModal(titulo, '<p class="confirm-texto">' + esc(texto) + "</p>", [
      { txt: "Cancelar", clase: "btn btn-secundario" },
      { txt: "Confirmar", clase: "btn btn-peligro", alClic: alConfirmar }
    ]);
  }

  /* --- barra lateral ---------------------------------------------------- */
  var sb = $("#sb"), ov = $("#ov");
  function abrirSB(abrir) {
    if (!sb) return;
    sb.classList.toggle("abierto", abrir);
    if (ov) ov.classList.toggle("visible", abrir);
    $$(".burger").forEach(function (b) {
      b.setAttribute("aria-expanded", abrir ? "true" : "false");
    });
  }
  if (ov) ov.addEventListener("click", function () { abrirSB(false); });
  if (sb) sb.addEventListener("click", function (e) {
    if (window.innerWidth < 1024 && e.target.closest("a")) abrirSB(false);
  });

  /* --- pestanas --------------------------------------------------------- */
  $$(".tabs").forEach(function (barra) {
    var btns = $$("button", barra);
    btns.forEach(function (b, i) {
      b.setAttribute("role", "tab");
      b.addEventListener("click", function () {
        btns.forEach(function (o, j) {
          o.classList.toggle("activo", i === j);
          o.setAttribute("aria-selected", i === j ? "true" : "false");
        });
        var destino = b.dataset.panel;
        if (destino) {
          $$("[data-panel-nombre]").forEach(function (p) {
            p.hidden = p.dataset.panelNombre !== destino;
          });
        }
        guardar({ tab: destino || i });
      });
    });
  });

  /* --- buscador y facetas ------------------------------------------------ */
  /* Una "zona" ([data-tabla-zona]) agrupa buscador, facetas y su tabla. El
     texto, los select y los chips se combinan en un unico filtro y el
     resultado se cuenta en [data-resultados]. Fuera de una zona, el buscador
     de la barra superior filtra todas las tablas de la pagina. */
  function filasTabla(tabla) { return $$("tbody tr", tabla); }

  function aplicarZona(zona) {
    var tabla = $("table.tabla", zona);
    if (!tabla) return;
    var input = $("[data-busca], .buscador input", zona);
    var q = ((input && input.value) || "").trim().toLowerCase();
    var selects = $$("select", zona).filter(function (s) { return s.dataset.filtro !== "off"; });
    var chips = $$(".chip.activo", zona).map(function (c) {
      return (c.dataset.chip || c.textContent).trim().toLowerCase();
    });
    var n = 0;
    filasTabla(tabla).forEach(function (f) {
      var txt = f.textContent.toLowerCase();
      var okQ = !q || txt.indexOf(q) >= 0;
      /* Un select filtra cuando el texto de la opcion elegida aparece en la
         celda de data-filtro-col (o en toda la fila si no se acota). */
      var okSel = selects.every(function (s) {
        if (!s.value) return true;
        var op = (s.selectedOptions[0] ? s.selectedOptions[0].textContent : "").trim().toLowerCase();
        if (!op) return true;
        var col = s.dataset.filtroCol;
        if (col !== undefined && col !== "") {
          var celda = f.children[parseInt(col, 10)];
          return !!celda && celda.textContent.toLowerCase().indexOf(op) >= 0;
        }
        return txt.indexOf(op) >= 0;
      });
      var okChip = chips.every(function (c) { return !c || txt.indexOf(c) >= 0; });
      f.hidden = !(okQ && okSel && okChip);
      if (!f.hidden) n++;
    });
    var r = $("[data-resultados]", zona);
    if (r) r.textContent = n + (n === 1 ? " resultado" : " resultados");
    guardar({ filtros: n });
  }

  function filtrarTodas(input) {
    var q = input.value.trim().toLowerCase();
    $$(".tabla-envoltura").forEach(function (caja) {
      var tabla = $("table.tabla", caja);
      if (!tabla) return;
      filasTabla(tabla).forEach(function (fila) {
        fila.hidden = !!q && fila.textContent.toLowerCase().indexOf(q) < 0;
      });
    });
  }

  $$('button[data-export="csv"]').forEach(function (b) { pintarSelectorAmbito(b); });

  $$("[data-tabla-zona]").forEach(function (zona) {
    var input = $("[data-busca], .buscador input", zona);
    var t;
    if (input) {
      input.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { aplicarZona(zona); }, 180); });
      input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); aplicarZona(zona); } });
    }
    $$("select", zona).forEach(function (s) { s.addEventListener("change", function () { aplicarZona(zona); }); });
    $$(".chip", zona).forEach(function (c) {
      c.addEventListener("click", function () { c.classList.toggle("activo"); aplicarZona(zona); });
    });
  });

  if (PRODUCTO) {
    /* El buscador del administrador tambien encuentra pantallas: escribe "acta"
       y aparece el enlace, sin tener que recorrer el menu. */
    $$('.search input').forEach(function (i) {
      var lista = document.createElement("div");
      lista.className = "search-lista";
      document.body.appendChild(lista);
      var t;
      i.addEventListener("input", function () {
        clearTimeout(t);
        t = setTimeout(function () {
          var q = i.value.trim().toLowerCase();
          if (q.length < 2) { lista.innerHTML = ""; lista.hidden = true; return; }
          var hits = $$(".nav a").filter(function (a) {
            return a.textContent.toLowerCase().indexOf(q) >= 0;
          }).slice(0, 6);
          lista.innerHTML = hits.map(function (a) {
            return '<a href="' + a.getAttribute("href") + '">'
              + icono(ICO.info, 14) + esc(a.textContent.trim()) + "</a>";
          }).join("");
          lista.hidden = !hits.length;
        }, 160);
      });
      i.addEventListener("blur", function () {
        setTimeout(function () { lista.hidden = true; }, 180);
      });
    });
  }

  $$('input[type="text"][placeholder*="Buscar" i], .buscador input').forEach(function (i) {
    if (i.closest("[data-tabla-zona]")) return;
    var t;
    i.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { filtrarTodas(i); }, 220); });
    i.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); filtrarTodas(i); } });
  });

  /* --- menu lateral agrupado -------------------------------------------- */
  $$(".nav-label").forEach(function (b) {
    b.addEventListener("click", function () {
      var g = b.closest(".nav-group");
      if (!g) return;
      var abierto = g.classList.toggle("abierto");
      b.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
  });

  /* --- seleccion de filas ------------------------------------------------ */
  $$("table.tabla").forEach(function (t) {
    var maestro = $('thead input[type="checkbox"]', t);
    if (!maestro) return;
    maestro.addEventListener("change", function () {
      $$('tbody input[type="checkbox"]', t).forEach(function (c) {
        c.checked = maestro.checked;
        c.closest("tr").classList.toggle("seleccionada", maestro.checked);
      });
      var n = $$('tbody input[type="checkbox"]:checked', t).length;
      toast(n ? n + " fila(s) seleccionada(s)" : "Selección limpiada", "info");
    });
    $$('tbody input[type="checkbox"]', t).forEach(function (c) {
      c.addEventListener("change", function () {
        c.closest("tr").classList.toggle("seleccionada", c.checked);
      });
    });
  });

  /* --- acciones ---------------------------------------------------------- */
  function celdaDe(boton) {
    var fila = boton.closest("tr, article, li, .aviso, .card");
    if (fila && !fila.hidden && fila.textContent.trim()) {
      var t = fila.textContent.replace(/\s+/g, " ").trim();
      return t.length > 96 ? t.slice(0, 96) + "…" : t;
    }
    return boton.dataset.rotulo || boton.getAttribute("aria-label") || "el registro";
  }
  function filaDe(boton) { return boton.closest("tr, article, li"); }

  /* --- descargas reales -------------------------------------------------- */
  /* `data-export="csv"` vuelca la tabla (solo filas visibles, respetando los
     filtros) y `data-export="reporte"` abre una vista imprimible de la pagina
     con sus graficas. Sin data-export, un boton de descarga suelto sigue
     avisando por toast. */
  function tituloPagina() {
    var h1 = $("main.content h1, .page-head h1");
    return (h1 && h1.textContent.trim()) || (document.title || "SGEMD").split(" — ")[0];
  }

  function bajarArchivo(nombre, contenido, mime) {
    try {
      var blob = new Blob(["\ufeff" + contenido], { type: mime || "text/csv;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      return true;
    } catch (err) { return false; }
  }

  /* Ambito de la descarga. Antes solo se podia sacar "lo que se ve", que no
     responde a "dame todo el listado" ni a "dame una carrera entera". */
  function filasDeExport(tabla, ambito) {
    var todas = $$("tbody tr", tabla);
    if (!ambito || ambito === "visibles") {
      return todas.filter(function (tr) { return !tr.hidden; });
    }
    if (ambito === "todas") return todas;
    var col = parseInt(ambito, 10);
    if (isNaN(col)) return todas.filter(function (tr) { return !tr.hidden; });
    return todas.filter(function (tr) {
      var td = tr.children[col];
      return td && td.textContent.trim() === ambito;
    });
  }

  function csvDeTabla(tabla, ambito) {
    var todas = $$("thead th", tabla);
    var cols = [];
    todas.forEach(function (h, i) {
      if (h.classList.contains("acc") || h.classList.contains("sel")) return;
      if (h.querySelector("input")) return;
      cols.push(i);
    });
    function linea(celdas) {
      return celdas.map(function (c) {
        var s = String(c).replace(/\s+/g, " ").trim();
        return /[";\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
      }).join(";");
    }
    var out = [linea(cols.map(function (i) { return todas[i].textContent; }))];
    filasDeExport(tabla, ambito).forEach(function (tr) {
      out.push(linea(cols.map(function (i) {
        var td = tr.children[i];
        return td ? td.textContent : "";
      })));
    });
    return out.join("\r\n");
  }

  function exportarCSV(b) {
    var tabla = b.dataset.tabla ? document.getElementById(b.dataset.tabla) : $("table.tabla[data-tabla]");
    if (!tabla) { toast("No hay datos para exportar", "error"); return; }
    var ambito = b.dataset.ambito || "visibles";
    var filas = filasDeExport(tabla, ambito);
    if (!filas.length) {
      toast("No hay filas con ese criterio", "error");
      return;
    }
    var sufijo = "";
    if (ambito === "todas") sufijo = "-todo-el-listado";
    else if (ambito !== "visibles") sufijo = "-" + slug(ambito);
    var ok = bajarArchivo(slug(tituloPagina()) + sufijo + ".csv", csvDeTabla(tabla, ambito));
    var que = ambito === "visibles" ? "lo que estas viendo"
            : ambito === "todas" ? "todo el listado"
            : "el programa " + ambito;
    toast(ok ? "Descargado " + que + " (" + filas.length + " fila(s))"
             : "No se pudo descargar", ok ? "ok" : "error");
  }

  /* El selector de alcance aparece junto al boton cuando la tabla tiene datos
     de verdad. Sin el, un boton de mas seria un control sin efecto. */
  function pintarSelectorAmbito(boton) {
    if ($("#ambito-export")) return;
    var tabla = boton.dataset.tabla ? document.getElementById(boton.dataset.tabla) : $("table.tabla[data-tabla]");
    if (!tabla) return;
    var total = $$("tbody tr", tabla).length;
    if (total < 2) return;
    var sel = document.createElement("select");
    sel.id = "ambito-export";
    sel.className = "filtro";
    /* data-filtro="off": la zona trata todo select como faceta y filtraria las
       filas por el texto del alcance, que no es lo que se quiere al cambiar de
       ambito de descarga. */
    sel.setAttribute("data-filtro", "off");
    sel.setAttribute("aria-label", "Alcance de la descarga");
    sel.innerHTML = '<option value="visibles">Lo que veo</option>'
      + '<option value="todas">Todo el listado (' + total + ")</option>";
    /* Una carrera o sector es la tercera respuesta: se ofrece la columna que
       el administrador ya usa como faceta. */
    var facetas = $$("select.filtro", boton.closest("[data-tabla-zona]") || document);
    facetas.forEach(function (f) {
      var col = f.dataset.filtroCol;
      if (col === undefined || col === "" || f.options.length < 3) return;
      if (boton.closest("[data-crud-zona]")) return;
      for (var i = 0; i < f.options.length; i++) {
        var o = f.options[i];
        if (!o.value) continue;
        var opt = document.createElement("option");
        opt.value = o.textContent.trim();
        opt.textContent = "Solo: " + o.textContent.trim();
        sel.appendChild(opt);
      }
    });
    sel.addEventListener("change", function () {
      boton.dataset.ambito = sel.value;
      boton.title = "Descargar " + sel.options[sel.selectedIndex].textContent.toLowerCase();
    });
    boton.parentNode.insertBefore(sel, boton);
  }

  function estiloReporte() {
    return "body{font-family:Inter,Arial,sans-serif;color:#051533;margin:26px}" +
      "h1{font-size:22px;margin:0 0 4px;letter-spacing:-.01em}" +
      ".rep-cab{border-bottom:2px solid #004a93;padding-bottom:10px;margin-bottom:18px}" +
      ".rep-cab p{margin:0;color:#162644;font-size:12px}" +
      ".card,.emp-card,.aviso-grp,.kan-col,.ag-dia,.modal{border:1px solid #bbbbbb;border-radius:8px;padding:12px;margin-bottom:14px;break-inside:avoid}" +
      ".card-head h3{font-size:14px;margin:0 0 6px}" +
      "table.tabla{width:100%;border-collapse:collapse;font-size:12px}" +
      "table.tabla th,table.tabla td{border:1px solid #bbbbbb;padding:6px 8px;text-align:left}" +
      "table.tabla thead th{background:#162644;color:#fff}" +
      ".metrica-lbl{font-size:11px;color:#162644}.metrica-val{font-size:20px;font-weight:800}" +
      ".grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}" +
      ".badge{border:1px solid #bbbbbb;border-radius:999px;padding:2px 8px;font-size:11px}" +
      ".b-azul{background:#004a93;color:#fff}.b-amarillo{background:#ffd300}" +
      ".barra{background:#bbbbbb;height:6px;border-radius:999px;overflow:hidden}" +
      ".barra span{display:block;height:100%;background:#004a93}" +
      "@media print{@page{margin:14mm}.card{break-inside:avoid}}";
  }

  function reporteImprimible() {
    var contenido = $("main.content");
    if (!contenido) { toast("Nada que imprimir", "info"); return; }
    var clon = contenido.cloneNode(true);
    $$("button, .toolbar, .acciones, .paginacion, .no-print", clon).forEach(function (x) { x.remove(); });
    $$("[hidden]", clon).forEach(function (x) { x.hidden = false; });
    var w = window.open("", "_blank");
    if (!w) { toast("Permite las ventanas emergentes para imprimir", "error"); return; }
    w.document.write(
      '<!doctype html><' + 'html lang="es"><head><meta charset="utf-8">' +
      "<title>" + esc(tituloPagina()) + " — SGEMD</title><style>" + estiloReporte() + "</style></" + "head><body>" +
      '<header class="rep-cab"><h1>' + esc(tituloPagina()) + "</h1>" +
      "<p>SGEMD · Informe generado el " + new Date().toLocaleDateString("es-CO") + "</p></header>" +
      clon.innerHTML + "</body></" + "html>");
    w.document.close();
    w.focus();
    setTimeout(function () { w.print(); }, 400);
  }

  function exportar(b) {
    var tipo = b.dataset.export || "reporte";
    if (tipo === "csv") { exportarCSV(b); return; }
    reporteImprimible();
  }

  function accionDe(boton) {
    if (boton.dataset.accion) return boton.dataset.accion;
    return slug(boton.textContent) || slug(boton.getAttribute("aria-label") || "");
  }

  function abrirEditor(titulo, registro) {
    abrirModal(titulo,
      '<div class="campo"><label for="m-campo">Detalle del registro</label>' +
      '<input id="m-campo" type="text" value="' + esc(registro) + '"></div>' +
      '<p class="modal-aviso">' + texto('El registro queda actualizado en la ficha.') + '</p>',
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Guardar", clase: "btn btn-primario", alClic: function () {
            toast("Cambios guardados", "ok");
          }
        }
      ]);
  }

  /* --- administrador: CRUD de usuarios y asignacion de asesoria --------- */
  /* Los datos viajan en <script type="application/json"> (ver _seed en
     paginas_admin) y las escrituras de sesion usan claves con dominio fijo
     para no chocar con el estado por pantalla (CLAVE). */
  var CLAVE_USUARIOS = "sgemd:v1:admin:usuarios";
  var CLAVE_ASIGNA = "sgemd:v1:admin:asignaciones";
  function leerAdmin(clave, porDefecto) {
    try { return JSON.parse(localStorage.getItem(clave)) || porDefecto; }
    catch (e) { return porDefecto; }
  }
  function guardarAdmin(clave, datos) {
    try { localStorage.setItem(clave, JSON.stringify(datos)); } catch (e) {}
  }
  function semilla(id) {
    var n = document.getElementById(id);
    if (!n) return null;
    try { return JSON.parse(n.textContent); } catch (e) { return null; }
  }
  function badgesEstado(estado) {
    return '<span class="badge ' + (estado === "Activo" ? "b-azul" : "b-neutra") + '">' + estado + "</span>";
  }
  function bLinea(txt) { return '<span class="badge b-linea">' + esc(txt) + "</span>"; }
  function opcionesSelect(opciones, seleccionado) {
    return (opciones || []).map(function (o) {
      return "<option" + (o === seleccionado ? " selected" : "") + ">" + esc(o) + "</option>";
    }).join("");
  }
  /* Sedes para los modales que las necesitan sin seed propio. */
  function semillaOpc(id, porDefecto) {
    var n = document.getElementById(id);
    if (!n) return porDefecto;
    try { return JSON.parse(n.textContent) || porDefecto; }
    catch (e) { return porDefecto; }
  }
  function btnGestionUsuario(tipo, codigo) {
    return '<button data-accion="gestion-usuario" data-tipo="' + tipo + '" data-codigo="' + codigo +
      '" title="Editar" aria-label="Editar ' + tipo + '">' + icono(ICO.lapiz, 16) + "</button>";
  }
  function btnAlternarEstado(codigo, col) {
    return '<button data-accion="alternar-estado" data-codigo="' + codigo + '" data-col="' + col +
      '" title="Alternar acceso" aria-label="Alternar acceso">' + icono(ICO.lock, 16) + "</button>";
  }
  function filaDocente(d, est) {
    return "<tr><td><b>" + esc(d.codigo) + "</b></td><td><b>" + esc(d.nombres) + "</b></td>" +
      "<td>" + bLinea("Docente") + "</td><td>" + esc(d.area || "General") + "</td>" +
      "<td>" + esc(d.emprendimiento || d.emp || "0") + "</td>" +
      "<td>" + bLinea(d.sede || "—") + "</td><td>" + badgesEstado(est) + "</td>" +
      "<td><div class='acciones'>" + btnGestionUsuario("docente", d.codigo) +
      btnAlternarEstado(d.codigo, "6") + "</div></td></tr>";
  }
  function filaEstudiante(d, est) {
    return "<tr><td><b>" + esc(d.codigo) + "</b></td><td><b>" + esc(d.nombres) + "</b></td>" +
      "<td>" + bLinea("Estudiante") + "</td><td>" + esc(d.programa) + "</td><td>" + esc(d.emprendimiento || "Por asignar") + "</td>" +
      "<td>" + bLinea(d.sede) + "</td><td>" + badgesEstado(est) + "</td>" +
      "<td><div class='acciones'>" +
      "<button data-accion='ver' data-tipo='ver' title='Ver' aria-label='Ver estudiante'>" +
      icono(ICO.ojo, 16) + "</button>" +
      btnGestionUsuario("estudiante", d.codigo) +
      btnAlternarEstado(d.codigo, "6") + "</div></td></tr>";
  }
  function siguienteCodigo(tipo) {
    var s = semilla("datos-usuarios");
    var n = 0, base = "EST-";
    if (tipo === "docente") {
      base = "DOC-";
      n = (s && s.docentes ? s.docentes.length : 0) + 1;
    } else {
      n = (s && s.estudiantes ? s.estudiantes.length : 0) + 1;
    }
    var c = base + ("000" + n).slice(-3);
    while (document.querySelector('[data-codigo="' + c + '"]')) {
      n++;
      c = base + ("000" + n).slice(-3);
    }
    return c;
  }
  function estadoPersistido(codigo) {
    var u = leerAdmin(CLAVE_USUARIOS, {});
    return (u.estados || {})[codigo];
  }
  function guardarEstado(codigo, estado) {
    var u = leerAdmin(CLAVE_USUARIOS, {});
    if (!u.estados) u.estados = {};
    u.estados[codigo] = estado;
    guardarAdmin(CLAVE_USUARIOS, u);
  }
  function pinRegistro(d, tipo) {
    var s = semilla("datos-usuarios");
    if (!s) return;
    var arr = tipo === "docente" ? s.docentes : s.estudiantes;
    for (var i = 0; i < arr.length; i++) if (arr[i].codigo === d.codigo) arr[i] = d;
  }
  function actualizarFila(boton, d, tipo) {
    var f = filaDe(boton);
    if (!f) return;
    if (tipo === "docente") {
      f.children[1].innerHTML = "<b>" + esc(d.nombres) + "</b>";
      f.children[2].textContent = d.correo;
      f.children[3].textContent = d.area;
      f.children[4].textContent = d.carga + " h";
    } else {
      f.children[1].innerHTML = "<b>" + esc(d.nombres) + "</b>";
      f.children[2].textContent = d.programa;
      f.children[3].textContent = d.emprendimiento;
      f.children[4].innerHTML = bLinea(d.sede);
    }
  }
  function var_editarUsuario(b) {
    var tipo = b.dataset.tipo || "estudiante";
    var codigo = b.dataset.codigo;
    var s = semilla("datos-usuarios");
    if (!s) { toast("Datos no disponibles en esta pantalla", "error"); return; }
    var d = null;
    (tipo === "docente" ? s.docentes : s.estudiantes).forEach(function (x) {
      if (x.codigo === codigo) d = x;
    });
    if (!d) { toast("No se encontró " + codigo, "error"); return; }
    var campos =
      '<div class="campo"><label for="m-nom">Nombres</label><input id="m-nom" type="text" value="' + esc(d.nombres) + '"></div>' +
      '<div class="campo"><label for="m-cor">Correo institucional</label><input id="m-cor" type="email" value="' + esc(d.correo) + '"></div>';
    if (tipo === "docente") {
      campos += '<div class="campo"><label for="m-are">Área de acompañamiento</label><select id="m-are">' +
        opcionesSelect(s.areas || [], d.area) + "</select></div>" +
        '<div class="campo"><label for="m-emp">Emprendimientos asignados</label><input id="m-emp" type="number" min="0" value="' + esc(d.emprendimiento || d.emp || "0") + '"></div>' +
        '<div class="campo"><label for="m-sed2">Sede (opcional)</label><select id="m-sed2">' +
        opcionesSelect(s.sedes || [], d.sede) + "</select></div>";
    } else {
      campos += '<div class="campo"><label for="m-pro">Programa</label><select id="m-pro">' +
        opcionesSelect(s.programas || [], d.programa) + "</select></div>" +
        '<div class="campo"><label for="m-emp2">Emprendimiento (opcional)</label><input id="m-emp2" type="text" value="' + esc(d.emprendimiento || "") + '"></div>' +
        '<div class="campo"><label for="m-sed">Sede</label><select id="m-sed">' +
        opcionesSelect(s.sedes || [], d.sede) + "</select></div>";
    }
    abrirModal("Editar " + (tipo === "docente" ? "docente" : "estudiante") + " · " + codigo,
      campos + '<p class="modal-aviso">' + texto('El registro queda actualizado en la ficha.') + '</p>',
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Guardar cambios", clase: "btn btn-primario", cerrar: false,
          alClic: function (velo) {
            var nom = $("#m-nom", velo), cor = $("#m-cor", velo);
            if (!nom.value.trim() || !cor.value.trim()) { toast("Completa los campos obligatorios", "error"); return; }
            d.nombres = nom.value.trim();
            d.correo = cor.value.trim();
            if (tipo === "docente") {
              d.area = $("#m-are", velo).value;
              d.emprendimiento = $("#m-emp", velo).value || "0";
              d.emp = d.emprendimiento;
              d.sede = $("#m-sed2", velo).value || "—";
            } else {
              d.programa = $("#m-pro", velo).value;
              d.sede = $("#m-sed", velo).value;
              d.emprendimiento = $("#m-emp2", velo).value || "Por asignar";
            }
            actualizarFila(b, d, tipo);
            toast("Cambios guardados en " + codigo, "ok");
            cerrarModal();
          }
        }
      ]);
  }
  function insertarUsuario(us, tipo) {
    var s = semilla("datos-usuarios");
    if (s) (tipo === "docente" ? s.docentes : s.estudiantes).push(us);
    var t = document.getElementById(tipo === "docente" ? "tabla-docentes" : "tabla-estudiantes");
    var tb = t && t.querySelector("tbody");
    var tabla = document.getElementById("tabla-usuarios");
    if (!tb && tabla) tb = tabla.querySelector("tbody");
    if (tb) tb.insertAdjacentHTML("beforeend", tipo === "docente" ? filaDocente(us, us.estado) : filaEstudiante(us, us.estado));
  }
  /* --- modelo de perfil ------------------------------------------------- */
  /* Un solo diccionario de campos para docente y estudiante (datos_admin.PERFIL)
     alimenta el alta, la edicion y la ficha. Antes cada sitio tenia su propia
     lista y el perfil se creaba con tres campos y despues se editaba con cuatro. */
  function perfilCampos(tipo) {
    var s = semilla("datos-usuarios");
    if (!s || !s.perfil) return [];
    return s.perfil.filter(function (c) { return c.roles === "ambos" || c.roles === tipo; });
  }

  function controlPerfil(c, valor) {
    var id = "pf-" + slug(c.clave);
    var req = c.req ? ' required aria-required="true"' : "";
    var ay = c.ayuda ? '<span class="hint">' + esc(c.ayuda) + "</span>" : "";
    if (c.t === "select") {
      return '<div class="campo"><label for="' + id + '">' + esc(c.l)
        + (c.req ? '<span class="req">*</span>' : "") + '</label><select id="' + id
        + '" data-n="' + esc(c.clave) + '"' + req + ">"
        + opcionesSelect(c.o || [], valor == null ? (c.def || "") : valor)
        + "</select>" + ay + "</div>";
    }
    if (c.t === "check") {
      return '<label class="chk"><input type="checkbox" data-n="' + esc(c.clave)
        + '"' + (valor ? " checked" : "") + req + "> <span><b>" + esc(c.l)
        + "</b>" + ay + "</span></label>";
    }
    if (c.t === "area") {
      return '<div class="campo"><label for="' + id + '">' + esc(c.l)
        + (c.req ? '<span class="req">*</span>' : "") + '</label><textarea id="' + id
        + '" data-n="' + esc(c.clave) + '" placeholder="' + esc(c.l) + '"' + req
        + ">" + esc(valor == null ? "" : valor) + "</textarea>" + ay + "</div>";
    }
    return '<div class="campo"><label for="' + id + '">' + esc(c.l)
      + (c.req ? '<span class="req">*</span>' : "") + '</label><input id="' + id
      + '" type="' + esc(c.t || "text") + '" data-n="' + esc(c.clave) + '" value="'
      + esc(valor == null ? (c.def || "") : valor) + '" placeholder="' + esc(c.l)
      + '"' + req + ">" + ay + "</div>";
  }

  function formularioPerfil(tipo, persona) {
    return perfilCampos(tipo).map(function (c) {
      return controlPerfil(c, persona ? persona[c.clave] : null);
    }).join("");
  }

  function leerPerfil(velo) {
    var datos = {};
    $$("[data-n]", velo).forEach(function (c) {
      datos[c.dataset.n] = c.type === "checkbox" ? !!c.checked : c.value.trim();
    });
    return datos;
  }

  /* Un alta o una edicion se guarda con el mismo camino: los campos que quedan
     vacios se limpian, para que el perfil no arrastre datos del anterior. */
  function guardarPerfil(tipo, persona, velo, alTerminar) {
    var datos = leerPerfil(velo);
    var faltan = $$("[required]", velo).filter(function (c) {
      return c.type === "checkbox" ? !c.checked : !c.value.trim();
    });
    if (faltan.length) {
      toast(faltan.length + " campo(s) obligatorio(s) por completar", "error");
      faltan[0].focus();
      return;
    }
    var correo = (datos.correo || "").trim();
    if (correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
      toast("Revisa el correo institucional", "error");
      var cc = $('[data-n="correo"]', velo);
      if (cc) cc.focus();
      return;
    }
    var codigo = siguienteCodigo(tipo);
    var registro = { codigo: codigo, tipo: tipo, estado: "Activo" };
    if (persona) registro.estado = persona.estado || "Activo";
    Object.keys(datos).forEach(function (k) { registro[k] = datos[k]; });
    registro.codigo = persona ? persona.codigo : codigo;
    registro.nombres = [datos.nombres || "", datos.apellidos || ""].join(" ").trim();
    var u = leerAdmin(CLAVE_USUARIOS, {});
    if (!u.creados) u.creados = [];
    u.creados = u.creados.filter(function (x) { return x.codigo !== registro.codigo; });
    u.creados.push(registro);
    guardarAdmin(CLAVE_USUARIOS, u);
    pinRegistro(registro, tipo);
    insertarUsuario(registro, tipo);
    if (alTerminar) alTerminar(registro);
    return registro;
  }

  function nuevoUsuario() {
    if (!semilla("datos-usuarios")) {
      toast("Datos no disponibles en esta pantalla", "error");
      return;
    }
    abrirModal("Nuevo perfil",
      '<div class="campo"><label for="m-tipo">Tipo de perfil</label><select id="m-tipo">' +
      '<option value="estudiante">Estudiante</option>' +
      '<option value="docente">Docente (asesor)</option></select></div>' +
      '<div id="cuerpo-perfil"></div>' +
      '<p class="modal-aviso">El perfil nace con acceso Activo y queda en la ' +
      "tabla de esta pantalla.</p>",
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Crear perfil", clase: "btn btn-primario", cerrar: false,
          alClic: function (velo) {
            var tipo = $("#m-tipo", velo).value;
            var r = guardarPerfil(tipo, null, velo, function (reg) {
              toast(reg.codigo + " creado con acceso activo", "ok");
            });
            if (r) cerrarModal();
          }
        }
      ]);
    var selTipo = $("#m-tipo");
    function pintar() {
      $("#cuerpo-perfil").innerHTML = formularioPerfil(selTipo.value, null);
      enlazarCondicionales($("#cuerpo-perfil"), perfilCampos(selTipo.value));
    }
    selTipo.addEventListener("change", pintar);
    pintar();
  }

  function alternarEstado(b) {
    var codigo = b.dataset.codigo;
    var col = parseInt(b.dataset.col, 10);
    var base = null;
    var s = semilla("datos-usuarios");
    if (s) {
      (s.docentes || []).concat(s.estudiantes || []).forEach(function (x) {
        if (x.codigo === codigo) base = x;
      });
    }
    var actual = estadoPersistido(codigo) || (base && base.estado) || "Activo";
    var nuevo = actual === "Inactivo" ? "Activo" : "Inactivo";
    guardarEstado(codigo, nuevo);
    if (base) base.estado = nuevo;
    var f = filaDe(b);
    if (f && f.children[col]) f.children[col].innerHTML = badgesEstado(nuevo);
    var et = nuevo === "Activo" ? "activado" : "desactivado";
    toast(codigo + ": acceso " + et, nuevo === "Activo" ? "ok" : "info");
  }
  function pintarAsignacion(boton, docente, codigo) {
    var f = filaDe(boton);
    if (f && f.children[7]) {
      f.children[7].innerHTML = "<b>" + esc(docente) + "</b>";
    } else if (f) {
      f.remove();
    }
    if (codigo) {
      var s = semilla("datos-asignacion");
      if (s && s.sin_docente) s.sin_docente = s.sin_docente.filter(function (x) { return x.codigo !== codigo; });
    }
  }
  function asignarAsesoria(b) {
    var s = semilla("datos-asignacion");
    if (!s || !s.asesores || !s.asesores.length) { toast("Datos de asignación no disponibles", "error"); return; }
    var asig = leerAdmin(CLAVE_ASIGNA, {});
    var codigo = b.dataset.codigo || "";
    var o = codigo;
    if (!o && s.sin_docente && s.sin_docente.length) o = s.sin_docente[0].codigo;
    var previo = o ? asig[o] : "";
    var opciones = s.asesores.map(function (d) {
      return "<option" + (d === previo ? " selected" : "") + ">" + esc(d) + "</option>";
    }).join("");
    abrirModal("Asignar asesoria",
      '<div class="campo"><label for="m-asesor">Docente asesor</label><select id="m-asesor">' +
      opciones + "</select></div>" +
      '<p class="modal-aviso">El docente recibe la notificación de la nueva asignación.</p>',
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Asignar", clase: "btn btn-primario", cerrar: false,
          alClic: function (velo) {
            var d = $("#m-asesor", velo).value;
            if (!d) { toast("Elige un docente", "error"); return; }
            if (o) asig[o] = d;
            guardarAdmin(CLAVE_ASIGNA, asig);
            pintarAsignacion(b, d, codigo);
            toast("Asesoría asignada a " + d, "ok");
            cerrarModal();
          }
        }
      ]);
  }
  /* --- administrador: motor CRUD generico de listas ---------------------- */
  /* Una pantalla declara su listado en <script type="application/json"
     id="datos-lista"> (helper tabla_crud de paginas_admin): clave, columnas,
     campos editables, badges y filas. El HTML lo pinta el generador, de modo
     que la lista es real y los filtros la alcanzan; aqui solo se resuelven el
     alta, la edicion, el borrado y su persistencia. */
  function cfgCrud() { return semilla("datos-lista"); }

  function claveCrud(cfg) {
    return "sgemd:v1:admin:crud:" + (cfg.clave || slug(tituloPagina()));
  }

  function leerCrud(cfg) {
    return leerAdmin(claveCrud(cfg), {creados: [], editados: {}, borrados: []});
  }

  function guardarCrud(cfg, datos) { guardarAdmin(claveCrud(cfg), datos); }

  function idCrud(cfg, fila) {
    return String(fila.id != null ? fila.id : fila[cfg.id || cfg.columnas[0].n]);
  }

  /* Una celda sale como texto plano salvo que su columna este declarada en
     `badges`: ahi el estado se lee como etiqueta y no como palabra suelta. */
  function celdaCrud(cfg, col, valor) {
    var txt = esc(valor == null ? "" : valor);
    if ((cfg.badges || []).indexOf(col.n) < 0) return txt;
    return '<span class="badge ' + ((cfg.tonos || {})[txt] || "b-linea") + '">' + txt + "</span>";
  }

  function botonesCrud(id) {
    return '<button data-accion="ver-fila" data-id="' + esc(id) + '" title="Ver"' +
      ' aria-label="Ver detalle">' + icono(ICO.ojo, 16) + "</button>" +
      '<button data-accion="editar-fila" data-id="' + esc(id) + '" title="Editar"' +
      ' aria-label="Editar registro">' + icono(ICO.lapiz, 16) + "</button>" +
      '<button data-accion="borrar-fila" data-id="' + esc(id) + '" title="Eliminar"' +
      ' aria-label="Eliminar registro">' + icono(ICO.papelera, 16) + "</button>";
  }

  function filaCrud(cfg, fila) {
    var id = idCrud(cfg, fila);
    var celdas = cfg.columnas.map(function (col) {
      return '<td data-label="' + esc(col.l) + '">' + celdaCrud(cfg, col, fila[col.n]) + "</td>";
    }).join("");
    return '<tr data-id="' + esc(id) + '">' + celdas +
      '<td class="acc" data-label="Acciones"><div class="acciones-cell">' +
      botonesCrud(id) + "</div></td></tr>";
  }

  /* Repinta el <tbody> desde la semilla mas lo que el usuario creo, edito o
     borro en este navegador. Es la unica fuente de verdad: recargar no pierde
     nada y el borrado es recuperable desde el boton "Restaurar". */
  function pintarCrud(cfg) {
    var cuerpo = $("[data-crud-tbody]");
    if (!cuerpo || !cfg) return;
    var d = leerCrud(cfg);
    var base = (cfg.filas || []).map(function (f) {
      var g = {};
      Object.keys(f).forEach(function (k) { g[k] = f[k]; });
      var guardado = d.editados[idCrud(cfg, f)];
      if (guardado) Object.keys(guardado).forEach(function (k) { g[k] = guardado[k]; });
      return g;
    });
    var todos = base.concat(d.creados).filter(function (f) {
      return d.borrados.indexOf(idCrud(cfg, f)) < 0;
    });
    cuerpo.innerHTML = todos.map(function (f) { return filaCrud(cfg, f); }).join("");
    var zona = cuerpo.closest("[data-tabla-zona]");
    if (zona) aplicarZona(zona);
    botonRestaurar(cfg, d);
  }

  function botonRestaurar(cfg, d) {
    var previo = $("#btn-restaurar");
    if (previo) previo.remove();
    if (!d.borrados.length) return;
    var b = document.createElement("button");
    b.id = "btn-restaurar";
    b.className = "btn btn-secundario btn-sm";
    b.setAttribute("data-accion", "restaurar-filas");
    b.innerHTML = icono(ICO.papelera, 14) + " Restaurar " + d.borrados.length + " eliminado(s)";
    var barra = $(".toolbar", cfgCrudZona()) || $(".toolbar");
    if (barra) barra.appendChild(b);
  }

  function cfgCrudZona() { return $("[data-crud-tbody]") ? $("[data-crud-tbody]").closest("[data-tabla-zona]") : null; }

  /* El codigo del alta sigue el prefijo de la columna clave: si la semilla
     termina en 12, el siguiente registro es 13. */
  function siguienteIdCrud(cfg) {
    var pre = cfg.prefijo || "";
    var d = leerCrud(cfg);
    var n = 0;
    (cfg.filas || []).concat(d.creados).forEach(function (f) {
      var m = String(idCrud(cfg, f)).match(/(\d+)\s*$/);
      if (m) n = Math.max(n, parseInt(m[1], 10));
    });
    return pre + ("00" + (n + 1)).slice(-3);
  }

  function controlCrud(campo, valor) {
    var id = "crud-" + slug(campo.n);
    var req = campo.req ? ' required aria-required="true"' : "";
    var datos = ' data-n="' + esc(campo.n) + '"';
    if (campo.t === "select") {
      return '<select id="' + id + '"' + datos + req + ">" +
        opcionesSelect(campo.o || [], valor == null ? "" : valor) + "</select>";
    }
    if (campo.t === "area") {
      return '<textarea id="' + id + '"' + datos + ' placeholder="' + esc(campo.ph || campo.l) +
        '"' + req + ">" + esc(valor == null ? "" : valor) + "</textarea>";
    }
    return '<input id="' + id + '"' + datos + ' type="' + esc(campo.t || "text") + '" value="' +
      esc(valor == null ? "" : valor) + '" placeholder="' + esc(campo.ph || campo.l) + '"' + req + ">";
  }

  function formularioCrud(cfg, fila) {
    return (cfg.campos || []).map(function (c) {
      return '<div class="campo"><label for="crud-' + slug(c.n) + '">' + esc(c.l) +
        (c.req ? '<span class="req">*</span>' : "") + "</label>" +
        controlCrud(c, fila ? fila[c.n] : (c.def || "")) +
        (c.ayuda ? '<span class="hint">' + esc(c.ayuda) + "</span>" : "") + "</div>";
    }).join("");
  }

  /* Campo condicional: `dep` declara de que control depende y con que valores
     se habilita. El caso real es el semestre, que solo tiene sentido si el
     estudiante sigue estudiando. */
  function enlazarCondicionales(raiz, campos) {
    (campos || []).forEach(function (c) {
      if (!c.dep) return;
      var destino = $('[data-n="' + slug(c.n) + '"]', raiz);
      var origen = $('[data-n="' + slug(c.dep.campo) + '"]', raiz);
      if (!destino || !origen) return;
      function aplicar() {
        var habilitado = (c.dep.valores || []).indexOf(origen.value) >= 0;
        destino.disabled = !habilitado;
        if (!habilitado) destino.value = "";
      }
      origen.addEventListener("change", aplicar);
      aplicar();
    });
  }

  function abrirCrud(cfg, fila) {
    var editando = !!fila;
    var velo = abrirModal(
      editando ? "Editar " + (cfg.singular || "registro") : (cfg.nuevo || "Nuevo registro"),
      "<form data-crud novalidate>" + formularioCrud(cfg, fila) +
      '<p class="modal-aviso">' + texto('Al guardar, el registro queda actualizado y el cambio queda registrado.') + '</p></form>',
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: editando ? "Guardar cambios" : (cfg.crear || "Crear"),
          clase: "btn btn-primario", cerrar: false,
          alClic: function (velo) {
            var d = leerCrud(cfg);
            var nuevo = {};
            var faltan = [];
            $$("[data-n]", velo).forEach(function (c) {
              var v = (c.value || "").trim();
              if (c.required && !v) faltan.push(c);
              nuevo[c.dataset.n] = v;
            });
            if (faltan.length) {
              toast(faltan.length + " campo(s) obligatorio(s)", "error");
              faltan[0].focus();
              return;
            }
            if (editando) {
              var id = idCrud(cfg, fila);
              nuevo.id = id;
              d.editados[id] = nuevo;
              guardarCrud(cfg, d);
              pintarCrud(cfg);
              toast("Registro actualizado", "ok");
            } else {
              nuevo.id = siguienteIdCrud(cfg);
              d.creados.push(nuevo);
              guardarCrud(cfg, d);
              pintarCrud(cfg);
              toast(nuevo.id + " creado", "ok");
            }
            cerrarModal();
          }
        }
      ]);
    /* Los campos que dependen de otro (semestre segun condicion academica) se
       resuelven con el modal ya montado, para que arranquen en su estado. */
    enlazarCondicionales(velo, cfg.campos);
  }

  function verCrud(cfg, fila) {
    var cuerpo = cfg.columnas.map(function (col) {
      return '<div class="def-row"><dt>' + esc(col.l) + "</dt><dd>" +
        celdaCrud(cfg, col, fila[col.n]) + "</dd></div>";
    }).join("");
    abrirModal("Detalle del " + (cfg.singular || "registro"), '<dl class="lista-def">' + cuerpo + "</dl>", [
      { txt: "Cerrar", clase: "btn btn-secundario" },
      { txt: "Editar", clase: "btn btn-primario", cerrar: false,
        alClic: function () { cerrarModal(); abrirCrud(cfg, fila); } }
    ]);
  }

  /* Editar un perfil abre exactamente el mismo formulario del alta, con los
     valores cargados: asi no hay dos formularios que se queden distintos.
     La ficha de solo lectura es verUsuario, que esta mas abajo. */
  function editarPerfil(tipo, codigo) {
    var s = semilla("datos-usuarios");
    if (!s) { toast("Datos no disponibles en esta pantalla", "error"); return; }
    var persona = null;
    (tipo === "docente" ? s.docentes : s.estudiantes).forEach(function (x) {
      if (x.codigo === codigo) persona = x;
    });
    (leerAdmin(CLAVE_USUARIOS, {}).creados || []).forEach(function (x) {
      if (x.codigo === codigo) persona = x;
    });
    if (!persona) { toast("Perfil no encontrado", "error"); return; }
    abrirModal("Editar " + ((s.etiqueta_tipo || {})[tipo] || tipo).toLowerCase() + " " + codigo,
      '<div id="cuerpo-perfil">' + formularioPerfil(tipo, persona) + "</div>"
      + '<p class="modal-aviso">'
      + (texto("Al guardar, el cambio queda registrado en el historial del perfil.",
               "El cambio se guarda en este navegador."))
      + "</p>",
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Guardar cambios", clase: "btn btn-primario", cerrar: false,
          alClic: function (velo) {
            var r = guardarPerfil(tipo, persona, velo, function (reg) {
              toast(reg.codigo + ": cambios guardados", "ok");
            });
            if (r) cerrarModal();
          }
        }
      ]);
    enlazarCondicionales($("#cuerpo-perfil"), perfilCampos(tipo));
  }

  function verUsuario(tipo, codigo) {
    var s = semilla("datos-usuarios");
    if (!s) { toast("Datos no disponibles", "error"); return; }
    var lista = tipo === "docente" ? (s.docentes || []) : (s.estudiantes || []);
    var u = null;
    lista.forEach(function (x) { if (x.codigo === codigo) u = x; });
    (u ? [] : (leerAdmin(CLAVE_USUARIOS, {}).creados || [])).forEach(function (x) {
      if (x.codigo === codigo) u = x;
    });
    if (!u) { toast("Usuario no encontrado", "error"); return; }
    var cuerpo = '<div class="def-row"><dt>Codigo</dt><dd><b>' + esc(u.codigo)
      + "</b></dd></div><div class=\"def-row\"><dt>Rol</dt><dd>"
      + esc((s.etiqueta_tipo || {})[tipo] || tipo) + "</dd></div>";
    /* Las etiquetas salen del modelo, no de una lista aparte: asi la ficha no
       puede quedar por detras del formulario. */
    cuerpo += perfilCampos(tipo).map(function (c) {
      var v = u[c.clave];
      if (c.t === "check") return v
        ? '<div class="def-row"><dt>' + esc(c.l) + "</dt><dd>Si</dd></div>" : "";
      if (v === undefined || v === null || v === "") return "";
      return '<div class="def-row"><dt>' + esc(c.l) + "</dt><dd>" + esc(v) + "</dd></div>";
    }).join("");
    cuerpo += '<div class="def-row"><dt>Estado</dt><dd>' + badgesEstado(u.estado)
      + "</dd></div>";
    abrirModal("Ficha del usuario", '<dl class="lista-def">' + cuerpo + "</dl>", [
      { txt: "Cerrar", clase: "btn btn-secundario" },
      { txt: "Editar", clase: "btn btn-primario", cerrar: false,
        alClic: function () {
          cerrarModal();
          var boton = document.createElement("button");
          boton.dataset.accion = "gestion-usuario";
          boton.dataset.tipo = tipo;
          boton.dataset.codigo = codigo;
          var_editarUsuario(boton);
        } }
    ]);
  }

  /* Que se pierde al borrar. Sin esto el dialogo dice "Se eliminará: EMP-041
     Sabor y Sabe..." y quien decide no sabe si arrastra el historial. */
  function perdidaAlBorrar(cfg, fila) {
    var clave = (cfg.columnas || [])[0];
    var nombre = fila[clave] || "";
    var descargas = cfg.filas.length;
    if (descargas > 40) {
      return " Se sale de los listados y de los informes, y deja de contar en "
        + "las metricas del panel.";
    }
    if (descargas > 10) {
      return " Se sale de " + descargas + " listados y de los informes de "
        + "este tipo de registro.";
    }
    return " Se sale de " + descargas + " listados. Puedes restaurarlo con el "
      + "boton Restaurar de la barra.";
  }

  function borrarCrud(cfg, fila) {
    var id = idCrud(cfg, fila);
    confirmar("Eliminar " + (cfg.singular || "registro") + " " + id,
      "Vas a eliminar " + (fila[(cfg.columnas || [])[1].n] || id) + "." + perdidaAlBorrar(cfg, fila),
      function () {
        var d = leerCrud(cfg);
        d.borrados.push(id);
        delete d.editados[id];
        guardarCrud(cfg, d);
        pintarCrud(cfg);
        toast(id + " eliminado. Puedes restaurarlo desde la barra", "ok");
      });
  }

  function restaurarCrud(cfg) {
    var d = leerCrud(cfg);
    d.borrados = [];
    guardarCrud(cfg, d);
    pintarCrud(cfg);
    toast("Registros eliminados restaurados", "ok");
  }

  /* Busca una fila por su clave en la semilla y le superpone lo editado: el
     registro que ve el usuario es el que despues se guarda. */
  function buscarCrud(cfg, id) {
    var d = leerCrud(cfg);
    var base = (cfg.filas || []).concat(d.creados).filter(function (f) {
      return idCrud(cfg, f) === String(id);
    })[0];
    if (!base) return null;
    var g = {};
    Object.keys(base).forEach(function (k) { g[k] = base[k]; });
    var guardado = d.editados[id];
    if (guardado) Object.keys(guardado).forEach(function (k) { g[k] = guardado[k]; });
    return g;
  }

  function aplicarPersistidoUsuarios() {
    var s = semilla("datos-usuarios");
    if (!s) return;
    var u = leerAdmin(CLAVE_USUARIOS, {});
    var estados = u.estados || {};
    (u.creados || []).forEach(function (d) {
      if (document.querySelector('[data-codigo="' + d.codigo + '"]')) return;
      var arr = d.tipo === "docente" ? s.docentes : s.estudiantes;
      arr.push(d);
      insertarUsuario(d, d.tipo);
    });
    $$('[data-accion="alternar-estado"]').forEach(function (b) {
      var cod = b.dataset.codigo, est = estados[cod];
      if (!est) return;
      var f = filaDe(b);
      var col = parseInt(b.dataset.col, 10);
      if (f && f.children[col]) f.children[col].innerHTML = badgesEstado(est);
    });
  }
  aplicarPersistidoUsuarios();

  document.addEventListener("click", function (e) {
    var b = e.target.closest("button, a.btn");
    if (!b) return;
    var accion = accionDe(b);
    var registro = celdaDe(b);

    /* Un enlace con destino real navega: el shell lo pone en el <a> y el
       prototipo no lo reescribe. Los href="#" si se atienden aqui. */
    if (b.tagName === "A" && b.getAttribute("href") !== "#") return;

    /* Los botones del pie del modal y las chips ya tienen su propio handler;
       aqui no se atienden para evitar el doble disparo (toast + accion). */
    if (b.closest(".modal, .chip")) return;

    switch (accion) {
      case "menu":
        e.preventDefault();
        abrirSB(!sb.classList.contains("abierto"));
        break;

      case "ver":
      case "ver-detalle":
      case "vista-previa":
      case "revisar":
      case "abrir-plan":
      case "ver-evidencia":
      case "ver-historial":
      case "detalle":
        e.preventDefault();
        abrirModal("Detalle del registro",
          '<div class="def-row"><dt>Registro</dt><dd>' + esc(registro) + "</dd></div>"
          + (PRODUCTO
            ? '<p class="modal-aviso">Las evidencias y el historial completo estan en la ficha del registro.</p>'
            : '<p class="modal-aviso">Vista de prototipo. En produccion aqui se cargaria el expediente completo.</p>'));
        break;

      case "editar":
      case "registrar-avance":
      case "asignar":
      case "editar-sensores":
        e.preventDefault();
        /* Si la pantalla tiene motor CRUD, se edita con el formulario de esa
           lista (mismos campos, validacion y persistencia). Si no, al editor
           simple de siempre. */
        var cfgED = cfgCrud();
        var filaED = cfgED ? buscarCrud(cfgED, b.dataset.codigo || b.dataset.id) : null;
        if (filaED) abrirCrud(cfgED, filaED);
        else abrirEditor("Editar registro", registro);
        break;

      case "editar-docente":
      case "editar-estudiante":
        e.preventDefault();
        editarPerfil(b.dataset.tipo || "estudiante", b.dataset.codigo);
        break;

      case "aprobar":
      case "revisar-aprobacion":
      case "marcar-como-leida":
      case "calificar":
        e.preventDefault();
        b.classList.toggle("hecho");
        b.setAttribute("aria-pressed", b.classList.contains("hecho") ? "true" : "false");
        toast(b.classList.contains("hecho") ? "Aprobado" : "Aprobación revertida", "ok");
        break;

      case "gestion-usuario":
        e.preventDefault();
        editarPerfil(b.dataset.tipo || "estudiante", b.dataset.codigo);
        break;

      case "nuevo-usuario":
        e.preventDefault();
        nuevoUsuario();
        break;

      case "nuevo-fila":
        e.preventDefault();
        if (cfgCrud()) abrirCrud(cfgCrud(), null);
        break;

      case "editar-fila":
        e.preventDefault();
        var cfgE = cfgCrud();
        if (cfgE) {
          var filaE = buscarCrud(cfgE, b.dataset.id);
          if (filaE) abrirCrud(cfgE, filaE);
        }
        break;

      case "ver-fila":
        e.preventDefault();
        var cfgV = cfgCrud();
        if (cfgV) {
          var filaV = buscarCrud(cfgV, b.dataset.id);
          if (filaV) verCrud(cfgV, filaV);
        }
        break;

      case "ver-usuario":
        e.preventDefault();
        verUsuario(b.dataset.tipo, b.dataset.codigo);
        break;

      case "borrar-fila":
        e.preventDefault();
        var cfgB = cfgCrud();
        if (cfgB) {
          var filaB = buscarCrud(cfgB, b.dataset.id);
          if (filaB) borrarCrud(cfgB, filaB);
        }
        break;

      case "restaurar-filas":
        e.preventDefault();
        if (cfgCrud()) restaurarCrud(cfgCrud());
        break;

      case "nuevo-emprendimiento":
        /* El registro maestro no usa el motor CRUD (cada fila trae barra de
           avance y badges): se resuelve con el mismo formulario generico. */
        e.preventDefault();
        abrirModal("Nuevo emprendimiento",
          '<div class="campo"><label for="m-emp-n">Nombre del emprendimiento</label>'
          + '<input id="m-emp-n" type="text" required aria-required="true"></div>'
          + '<div class="campo"><label for="m-emp-e">Estudiante</label>'
          + '<input id="m-emp-e" type="text" required aria-required="true"></div>'
          + '<div class="campo"><label for="m-emp-s">Sede</label>'
          + '<select id="m-emp-s">' + opcionesSelect(semillaOpc("sedes", ["Ibagué"]), "Ibagué")
          + "</select></div>",
          [
            { txt: "Cancelar", clase: "btn btn-secundario" },
            { txt: "Crear", clase: "btn btn-primario", cerrar: false,
              alClic: function (velo) {
                var n = $("#m-emp-n", velo).value.trim();
                var e = $("#m-emp-e", velo).value.trim();
                if (!n || !e) { toast("Completa nombre y estudiante", "error"); return; }
                var tabla = document.getElementById("tabla-emprendimientos");
                if (!tabla) { toast("Listado no disponible", "error"); return; }
                var tr = document.createElement("tr");
                tr.innerHTML = "<td><b>" + esc(n) + "</b></td><td><b>EMP-NUEVO</b></td>"
                  + "<td>" + esc(e) + "</td><td>—</td><td>—</td><td>—</td>"
                  + '<td><div class="barra"><span style="width:0%"></span></div>'
                  + '<span style="font-size:13px;color:#162644">0%</span></td>'
                  + '<td><span class="badge b-amarillo">Sin asignar</span></td>'
                  + '<td class="acc" data-label="Acciones"></td>';
                $("tbody", tabla).insertBefore(tr, $("tbody", tabla).firstChild);
                toast(n + " creado", "ok");
              } }
          ]);
        break;

      case "retirar-emprendimiento":
        e.preventDefault();
        confirmar("Retirar emprendimiento",
          "El emprendimiento sale del listado y deja de contar en las metricas.",
          function () {
            var f = filaDe(b);
            if (f) f.remove();
            toast("Emprendimiento retirado", "ok");
          });
        break;

      case "asignar-docente":
        /* Regla del proceso (FLUJO-DE-ATENCION.md, paso 6): el acta firmada es
           requisito para asignar docente. El boton se explica en vez de fallar
           en silencio, para que se sepa que falta. */
        e.preventDefault();
        var acta = b.dataset.acta || "Pendiente";
        if (acta !== "Aprobada") {
          abrirModal("Acta pendiente",
            '<p class="confirm-texto">No se puede asignar docente: el acta de '
            + 'compromiso y confidencialidad esta en <b>' + esc(acta) + "</b>.</p>"
            + '<p class="modal-aviso">El estudiante debe firmar y subir el acta, '
            + 'y la asesora debe aprobarla.</p>',
            [
              { txt: "Entendido", clase: "btn btn-secundario" },
              { txt: "Ir a actas", clase: "btn btn-primario",
                alClic: function () { location.href = "actas.html"; } }
            ]);
          return;
        }
        confirmar("Asignar docente",
          "El estudiante y el docente recibir la notificacion de la asignacion.",
          function () { toast("Docente asignado. Comienza el acompanamiento", "ok"); });
        break;

      case "publicar-evento":
        e.preventDefault();
        confirmar("Publicar evento",
          "Se notificara a los estudiantes del sector correspondiente.",
          function () { toast("Evento publicado", "ok"); });
        break;

      case "habilitar-form2":
        e.preventDefault();
        confirmar("Habilitar el formulario 2",
          "El estudiante podra responder la caracterizacion y valoracion. "
          + "Antes de esto no accede a ninguna otra opcion de la plataforma.",
          function () {
            toast("Formulario 2 habilitado. El estudiante recibio el aviso", "ok");
            var cfgH = cfgCrud();
            if (cfgH) {
              var dH = leerCrud(cfgH);
              dH.habilitado = true;
              guardarCrud(cfgH, dH);
            }
          });
        break;

      case "generar-diagnostico":
        e.preventDefault();
        confirmar("Generar caracterizacion y diagnostico",
          "Con las respuestas del formulario 2 se generan la caracterizacion y "
          + "la valoracion. El estudiante deja de poder editarlo.",
          function () {
            guardar({ generado: true });
            toast("Diagnostico generado", "ok");
            setTimeout(function () { location.href = "diagnostico-generado.html"; }, 700);
          });
        break;

      case "ordenar":
        e.preventDefault();
        ordenarTabla(b);
        break;

      case "aplicar-masivo":
        e.preventDefault();
        accionMasiva(b);
        break;

      case "deshacer":
        e.preventDefault();
        deshacerBorrado();
        break;

      case "marcar-todo-leido":
        e.preventDefault();
        var cfgL = cfgCrud();
        if (!cfgL) break;
        var dL = leerCrud(cfgL);
        var nL = 0;
        (cfgL.filas || []).forEach(function (f) {
          var idL = idCrud(cfgL, f);
          if (dL.editados[idL] && dL.editados[idL].estado === "Pendiente") return;
          var gL = dL.editados[idL] || {};
          var baseL = {};
          Object.keys(f).forEach(function (k) { baseL[k] = f[k]; });
          Object.keys(gL).forEach(function (k) { baseL[k] = gL[k]; });
          if (baseL.estado !== "Pendiente") return;
          baseL.estado = "Leida";
          baseL.id = idL;
          dL.editados[idL] = baseL;
          nL++;
        });
        guardarCrud(cfgL, dL);
        pintarCrud(cfgL);
        toast(nL ? nL + " notificacion(es) marcadas como leidas" : "No habia nada sin leer", "ok");
        break;

      case "alternar-estado":
        e.preventDefault();
        alternarEstado(b);
        break;

      case "asignar-asesoria":
        e.preventDefault();
        asignarAsesoria(b);
        break;

      case "confirmar-asignacion":
        e.preventDefault();
        toast("Asignación confirmada. El docente y el estudiante recibirán notificación.", "ok");
        break;

      case "cancelar-asignacion":
        e.preventDefault();
        cerrarModal();
        toast("Asignación cancelada", "info");
        break;

      case "seleccionar":
        e.preventDefault();
        var fila = filaDe(b);
        if (fila) fila.classList.toggle("seleccionada");
        b.setAttribute("aria-pressed", fila && fila.classList.contains("seleccionada") ? "true" : "false");
        break;

      case "borrar":
        e.preventDefault();
        confirmar("Eliminar registro", "Se eliminará: " + registro + ". Esta acción no se puede deshacer.", function () {
          var f = filaDe(b);
          if (f) f.remove();
          toast("Registro eliminado", "ok");
        });
        break;

      case "cerrar":
      case "ocultar":
        e.preventDefault();
        var alvo = b.closest(".aviso, .alerta, .card, tr, li");
        if (alvo) alvo.remove();
        toast("Oculto", "info");
        break;

      case "descargar":
      case "descargar-expediente":
      case "descargar-pdf":
        e.preventDefault();
        if (b.dataset.export) { exportar(b); }
        else { toast("Preparando " + (b.textContent.trim() || "la descarga") + "…", "info"); }
        break;

      case "exportar":
      case "exportar-reporte":
        e.preventDefault();
        exportar(b);
        break;

      case "inscribirse":
        e.preventDefault();
        var_inscribir(b);
        break;

      case "guardar":
      case "guardar-cambios":
      case "guardar-borrador":
      case "guardar-y-salir":
      case "guardar-recomendaciones":
      case "enviar":
      case "enviar-solicitud":
      case "crear":
      case "crear-emprendimiento":
      case "nuevo":
        e.preventDefault();
        toast("Guardado correctamente", "ok");
        break;

      case "cancelar":
        e.preventDefault();
        cerrarModal();
        toast("Cancelado", "info");
        break;

      case "adjuntar":
      case "adjuntar-archivo":
      case "adjuntar-ahora":
        e.preventDefault();
        pedirArchivo(b);
        break;

      case "notificaciones":
        e.preventDefault();
        abrirDrawer("Notificaciones", textosNotificacion());
        break;

      default:
        var propio = (b.textContent || "").replace(/\s+/g, " ").trim();
        if (!propio) break;
        e.preventDefault();
        toast(propio, "info");
    }
  });

  /* --- notificaciones ----------------------------------------------------- */
  /* El drawer ya no es un texto fijo: si la pantalla tiene la lista de
     notificaciones (data-lista="notificaciones") se leen de ahi, con el
     estado real de cada aviso. En las demas pantallas sigue el ejemplo. */
  function textosNotificacion() {
    var cfg = cfgCrud();
    if (cfg && cfg.clave === "notificaciones") {
      var d = leerCrud(cfg);
      var base = (cfg.filas || []).map(function (f) {
        var g = {};
        Object.keys(f).forEach(function (k) { g[k] = f[k]; });
        var e = d.editados[idCrud(cfg, f)];
        if (e) Object.keys(e).forEach(function (k) { g[k] = e[k]; });
        return g;
      });
      var todas = base.concat(d.creados).filter(function (f) {
        return d.borrados.indexOf(idCrud(cfg, f)) < 0;
      });
      if (todas.length) {
        return todas.slice(0, 8).map(function (f) {
          return f.estado + ": " + f.titulo + " (" + f.origen + ")";
        });
      }
    }
    return [
      "Nueva revision de tu Startup Week II",
      "Tu docente registro un avance",
      "Se publico un evento nuevo",
      "Recordatorio: evidencia de tarea pendiente"
    ];
  }

  function pendienteNotificacion() {
    var cfg = cfgCrud();
    if (!cfg || cfg.clave !== "notificaciones") return 0;
    var d = leerCrud(cfg);
    var n = 0;
    (cfg.filas || []).concat(d.creados).forEach(function (f) {
      var id = idCrud(cfg, f);
      if (d.borrados.indexOf(id) >= 0) return;
      var e = d.editados[id];
      var estado = e && e.estado ? e.estado : f.estado;
      if (estado === "Pendiente") n++;
    });
    return n;
  }

  function var_inscribir(b) {
    var dentro = b.classList.toggle("hecho");
    b.setAttribute("aria-pressed", dentro ? "true" : "false");
    toast(dentro ? "Inscripción registrada" : "Inscripción cancelada", dentro ? "ok" : "info");
  }

  function pedirArchivo(b) {
    var input = document.createElement("input");
    input.type = "file";
    input.addEventListener("change", function () {
      var f = input.files && input.files[0];
      toast(f ? "Adjuntado: " + f.name : "Sin archivo", f ? "ok" : "info");
      if (f) b.textContent = f.name.length > 22 ? f.name.slice(0, 22) + "…" : f.name;
    });
    input.click();
  }

  /* --- validacion de formularios ----------------------------------------- */
  $$("form").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var malos = $$("[required]", f).filter(function (c) { return !c.value.trim(); });
      $$(".campo-error", f).forEach(function (x) { x.remove(); });
      malos.forEach(function (c) {
        var e2 = document.createElement("span");
        e2.className = "campo-error";
        e2.textContent = "Este campo es obligatorio";
        (c.closest(".campo") || c.parentNode).appendChild(e2);
        c.setAttribute("aria-invalid", "true");
      });
      if (malos.length) {
        toast(malos.length + " campo(s) por completar", "error");
        malos[0].focus();
        return;
      }
      /* Formulario de verdad: el panel de confirmacion vive junto al formulario
         para que quien lo usa vea el resultado sin salir de la pantalla. */
      var ok = $("[data-exito]", f.parentNode);
      if (ok) {
        ok.hidden = false;
        ok.textContent = f.dataset.exito || "Cambios guardados correctamente";
      }
      toast("Guardado correctamente", "ok");
    });
    $$("[required]", f).forEach(function (c) {
      c.addEventListener("input", function () {
        c.removeAttribute("aria-invalid");
        var err = c.closest(".campo") && $(".campo-error", c.closest(".campo"));
        if (err) err.remove();
      });
    });
  });

  /* Validacion estricta: solo la piden las pantallas que lo declaran con
     data-validacion="estricta". Marca al perder el foco, no solo al enviar, y
     mantiene el boton de guardar apagado mientras falte algo. Asi el resto de
     pantallas se comportan exactamente igual que hasta ahora. */
  $$('form[data-validacion="estricta"]').forEach(function (f) {
    var boton = $('button[type="submit"]', f);
    function faltan() {
      return $$("[required]", f).filter(function (c) { return !c.value.trim(); });
    }
    function refrescar() {
      var n = faltan().length;
      if (boton) boton.disabled = n > 0;
      var pie = $("[data-faltan]", f.parentNode || document);
      if (pie) pie.textContent = n ? n + " campo(s) por completar" : "Listo para guardar";
      f.classList.toggle("invalido", n > 0);
    }
    $$("[required]", f).forEach(function (c) {
      c.addEventListener("blur", function () {
        if (c.value.trim()) {
          c.removeAttribute("aria-invalid");
          var e3 = c.closest(".campo") && $(".campo-error", c.closest(".campo"));
          if (e3) e3.remove();
        } else {
          c.setAttribute("aria-invalid", "true");
          var e4 = c.closest(".campo");
          if (e4 && !$(".campo-error", e4)) {
            var e5 = document.createElement("span");
            e5.className = "campo-error";
            e5.textContent = "Este campo es obligatorio";
            e4.appendChild(e5);
          }
        }
        refrescar();
      });
      c.addEventListener("input", refrescar);
    });
    refrescar();
  });

  /* Zona de arrastrar y soltar para la carga del acta firmada. El input real
     sigue siendo el control accesible; la zona solo lo dispara. */
  $$(".drop[data-archivo]").forEach(function (zona) {
    var input = $("input[type=file]", zona);
    if (!input) return;
    function recibido(fichero) {
      if (!fichero) return;
      zona.classList.remove("arrastrando");
      var b = $("b", zona);
      if (b) b.textContent = fichero.name;
      var meta = $(".nombre", zona);
      if (meta) meta.textContent = Math.round(fichero.size / 1024) + " KB";
      var aviso = $(".form-aviso", zona);
      if (aviso) aviso.textContent = "Archivo listo para subir";
      input.setAttribute("aria-invalid", "false");
    }
    zona.addEventListener("click", function () { input.click(); });
    zona.addEventListener("dragover", function (e) {
      e.preventDefault();
      zona.classList.add("arrastrando");
    });
    zona.addEventListener("dragleave", function () { zona.classList.remove("arrastrando"); });
    zona.addEventListener("drop", function (e) {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        recibido(e.dataTransfer.files[0]);
      }
    });
    input.addEventListener("change", function () { recibido(input.files[0]); });
  });

  /* Contador de caracteres para los textareas largos (actas, diagnostico). */
  $$("[data-contador-for]").forEach(function (c) {
    var t = document.getElementById(c.dataset.contadorFor);
    if (!t) return;
    function pintar() {
      var n = (t.value || "").length;
      c.textContent = t.maxLength ? n + " / " + t.maxLength : n + " caracteres";
    }
    t.addEventListener("input", pintar);
    pintar();
  });

  /* --- arrastrar y soltar (kanban) --------------------------------------- */
  $$(".kanban, [data-kanban]").forEach(function (tablero) {
    var arrastre = null;
    $$(".k-col, .kanban-col", tablero).forEach(function (col) {
      col.addEventListener("dragover", function (e) { e.preventDefault(); col.classList.add("sobre"); });
      col.addEventListener("dragleave", function () { col.classList.remove("sobre"); });
      col.addEventListener("drop", function (e) {
        e.preventDefault();
        col.classList.remove("sobre");
        if (!arrastre) return;
        col.appendChild(arrastre);
        var estado = { tablero: tablero.dataset.kanban || "kanban", tareas: [] };
        $$(".kanban-col", tablero).forEach(function (c) {
          $$(".k-card", c).forEach(function (k) { estado.tareas.push(k.textContent.replace(/\s+/g, " ").trim().slice(0, 40)); });
        });
guardar(estado);
        toast("Tarea movida a " + nombreCol(col), "ok");
      });
    });
    $$(".k-card", tablero).forEach(function (k) {
      k.setAttribute("draggable", "true");
      k.addEventListener("dragstart", function () { arrastre = k; k.classList.add("arrastrando"); });
      k.addEventListener("dragend", function () { k.classList.remove("arrastrando"); arrastre = null; });
    });
  });
  function nombreCol(col) {
    var h = $(".k-col-t, .kanban-col-t, h3, .hint", col);
    return (h && h.textContent.replace(/\s+/g, " ").trim()) || "la columna";
  }

  /* --- paginacion -------------------------------------------------------- */
  $$("[data-paginacion]").forEach(function (p) {
    $$("button", p).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", p).forEach(function (o) { o.classList.toggle("activo", o === b); });
        guardar({ pagina: b.textContent.trim() });
        toast("Página " + b.textContent.trim(), "info");
      });
    });
  });

  /* --- menu de usuario ---------------------------------------------------- */
  /* Las pantallas de rol viven en estudiante/, docente/ y admin/, y el acceso
     esta en compartido/. Sin esto, "login.html" desde una subcarpeta no
     resuelve y el cierre de sesion deja al usuario en un 404. */
  function rutaLogin() {
    return location.pathname.indexOf("compartido/") >= 0
      ? "login.html"
      : "../compartido/login.html";
  }
  $$(".who").forEach(function (w) {
    w.setAttribute("tabindex", "0");
    w.setAttribute("role", "button");
    var abierto = false;
    function alternar() {
      abierto = !abierto;
      var m = $(".who-menu", w.parentNode);
      if (!m) {
        m = document.createElement("div");
        m.className = "who-menu";
        m.innerHTML = '<button data-accion="perfil">Mi perfil</button>' +
          '<button data-accion="preferencias">Preferencias</button>' +
          '<button data-accion="cerrar-sesion">Cerrar sesión</button>';
        w.parentNode.appendChild(m);
        $$("button", m).forEach(function (b) {
          b.addEventListener("click", function () {
            abierto = false;
            m.remove();
            if (b.dataset.accion === "cerrar-sesion") {
              /* La sesion la abre el login en compartido/login.html bajo
                 "sgemd:sesion"; se borra de localStorage y de sessionStorage
                 para que un logout no deje nada detrás. */
              store(null, true, null);
              try {
                localStorage.removeItem("sgemd:sesion");
                sessionStorage.removeItem("sgemd:sesion");
              } catch (x) {}
              location.href = rutaLogin();
              return;
            }
            toast(b.textContent.trim() + ": disponible en el módulo correspondiente", "info");
          });
        });
      }
      m.classList.toggle("visible", abierto);
    }
    w.addEventListener("click", function (e) { e.stopPropagation(); alternar(); });
    w.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); alternar(); } });
  });
  document.addEventListener("click", function () {
    $$(".who-menu.visible").forEach(function (m) { m.classList.remove("visible"); });
  });

  /* --- interactividad de las tablas ------------------------------------- */
  /* Ordenar por columna: se compara el texto de la celda. Con numeracion
     tabular se detecta la columna de numeros y se ordenan como numero, no como
     texto (si no, "9" queda despues de "80"). */
  function valorCelda(td) {
    return (td ? td.textContent : "").replace(/\\s+/g, " ").trim();
  }
  function ordenarTabla(boton) {
    var th = boton.closest("th");
    if (!th) return;
    var tabla = th.closest("table");
    var i = $$("th", tabla).indexOf(th);
    var ascendente = th.dataset.orden !== "asc";
    $$("th", tabla).forEach(function (o) { delete o.dataset.orden; });
    th.dataset.orden = ascendente ? "asc" : "desc";
    th.setAttribute("aria-sort", ascendente ? "ascending" : "descending");
    var cuerpo = $("tbody", tabla);
    var filas = $$("tr", cuerpo);
    var numerica = filas.some(function (f) {
      return /^-?[\\d.,]+%?$/.test(valorCelda(f.children[i]));
    });
    filas.sort(function (a, c) {
      var va = valorCelda(a.children[i]);
      var vc = valorCelda(c.children[i]);
      if (numerica) {
        var na = parseFloat(va.replace("%", "").replace(/\\./g, "").replace(",", ".")) || 0;
        var nc = parseFloat(vc.replace("%", "").replace(/\\./g, "").replace(",", ".")) || 0;
        return ascendente ? na - nc : nc - na;
      }
      return ascendente ? va.localeCompare(vc, "es") : vc.localeCompare(va, "es");
    });
    filas.forEach(function (f) { cuerpo.appendChild(f); });
    guardar({ orden: i, ascendente: ascendente });
    toast("Tabla ordenada por " + th.textContent.trim(), "info");
  }

  /* Acciones en bloque sobre las filas marcadas. La barra aparece sola
     cuando hay alguna marcada, para no recargar con botones sin uso. */
  function barraMasiva() {
    var previa = $(".barra-masiva");
    if (previa) previa.remove();
    var marcadas = $$('tbody input[type="checkbox"]:checked');
    if (!marcadas.length) return;
    var barra = document.createElement("div");
    barra.className = "barra-masiva";
    barra.innerHTML = "<b>" + marcadas.length + " seleccionada(s)</b>"
      + '<button class="btn btn-sm btn-secundario" data-accion="aplicar-masivo" '
      + 'data-masivo="aprobar">Aprobar</button>'
      + '<button class="btn btn-sm btn-secundario" data-accion="aplicar-masivo" '
      + 'data-masivo="asignar">Asignar asesor</button>'
      + '<button class="btn btn-sm btn-peligro" data-accion="aplicar-masivo" '
      + 'data-masivo="borrar">Eliminar</button>'
      + '<button class="btn btn-sm btn-secundario" data-accion="deshacer">'
      + "Deshacer eliminados</button>";
    var zona = marcadas[0].closest("[data-tabla-zona]");
    (zona || document.body).insertBefore(barra, (zona || document.body).firstChild);
  }

  function accionMasiva(b) {
    var marcadas = $$('tbody input[type="checkbox"]:checked');
    if (!marcadas.length) { toast("No hay filas seleccionadas", "info"); return; }
    var tipo = b.dataset.masivo;
    var filas = marcadas.map(function (c) { return c.closest("tr"); });
    if (tipo === "aprobar") {
      filas.forEach(function (f) {
        var celda = f.querySelector("td:nth-last-child(2)");
        if (celda) celda.innerHTML = badgesEstado("Aprobado");
      });
      toast(filas.length + " registro(s) aprobados", "ok");
    } else if (tipo === "asignar") {
      toast(filas.length + " asignacion(es) en cola", "ok");
    } else if (tipo === "borrar") {
      confirmar("Eliminar " + filas.length + " registro(s)",
        "Se eliminan los registros marcados. Puedes restaurarlos despues.",
        function () {
          var cfg = cfgCrud();
          if (cfg) {
            var d = leerCrud(cfg);
            filas.forEach(function (f) {
              var id = f.dataset.id;
              if (id && d.borrados.indexOf(id) < 0) d.borrados.push(id);
            });
            guardarCrud(cfg, d);
            pintarCrud(cfg);
          } else {
            filas.forEach(function (f) { f.remove(); });
          }
          toast(filas.length + " registro(s) eliminados", "ok");
        });
    }
  }

  var ultimoBorrado = [];
  function deshacerBorrado() {
    var cfg = cfgCrud();
    if (!cfg) { toast("Nada que restaurar", "info"); return; }
    var d = leerCrud(cfg);
    if (!d.borrados.length) { toast("No hay eliminados que restaurar", "info"); return; }
    d.borrados = [];
    guardarCrud(cfg, d);
    pintarCrud(cfg);
    toast("Registros eliminados restaurados", "ok");
  }

  /* Edicion en linea: doble clic en una celda que no sea de acciones la
     convierte en un campo, y Enter o el foco la devuelven a texto. */
  $$("table.tabla tbody td:not(.acc)").forEach(function (td) {
    td.setAttribute("tabindex", "0");
    td.addEventListener("dblclick", function () {
      if (td.querySelector("input")) return;
      var antes = valorCelda(td);
      var input = document.createElement("input");
      input.type = "text";
      input.value = antes;
      input.className = "celda-edit";
      td.textContent = "";
      td.appendChild(input);
      input.focus();
      input.select();
      function cerrar() {
        td.textContent = input.value.trim() || antes;
      }
      input.addEventListener("blur", cerrar);
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") cerrar();
        if (e.key === "Escape") { input.value = antes; cerrar(); }
      });
    });
  });

  /* La barra de acciones en bloque aparece y desaparece sola con la seleccion. */
  document.addEventListener("change", function (e) {
    if (e.target && e.target.type === "checkbox" && e.target.closest("table.tabla")) {
      barraMasiva();
    }
  });

  /* Los encabezados ordenables llevan el boton con su accion; el resto de
     cabeceras no se tocan. */
  $$("th[data-ordenable] button[data-accion='ordenar']").forEach(function () {
    if (!$$("button[data-accion='ordenar']").length) return;
  });

  /* --- estado inicial ----------------------------------------------------- */
  var cfgInicial = cfgCrud();
  if (cfgInicial) pintarCrud(cfgInicial);
  var previo = store(true);
  if (previo && previo.tab != null) {
    var barra = $(".tabs");
    if (barra) {
      var b = $$("button", barra)[previo.tab];
      if (b) b.click();
    }
  }
  document.documentElement.classList.add("js-listo");
})();
"""