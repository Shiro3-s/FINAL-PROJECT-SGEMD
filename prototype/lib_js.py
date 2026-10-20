"""Comportamiento de las 60 pantallas, en un unico bloque inline.

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
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + (d || 16) + '" height="' + (d || 16) +
      '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + camino + '"/></svg>';
  }
  var ICO = {
    check: "M20 6 9 17l-5-5", x: "M18 6 6 18M6 6l12 12", lapiz: "M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7",
    ojo: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z", alerta: "M12 9v4M12 17h.01",
    info: "M12 16v-4M12 8h.01", descargar: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    clip: "M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48",
    upload: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12",
    doc: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8"
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
  function abrirDrawer(titulo, items, pie) {
    cerrarDrawer();
    var d = document.createElement("aside");
    d.className = "sg-drawer";
    d.setAttribute("aria-label", titulo);
    d.innerHTML = '<div class="sg-drawer-head"><h2>' + esc(titulo) + "</h2>" +
      '<button class="icon-btn drawer-x" aria-label="Cerrar">' + icono(ICO.x, 18) + "</button></div>" +
      '<ul class="sg-drawer-lista">' + items.map(function (t) {
        return "<li>" + icono(ICO.info, 15) + "<span>" + esc(t) + "</span></li>";
      }).join("") + "</ul>" +
      (pie || "");
    document.body.appendChild(d);
    var o = $("#ov");
    if (o) o.classList.add("visible");
    $(".drawer-x", d).addEventListener("click", cerrarDrawer);
  }
  /* Variante con HTML ya construido: la usa la campana para clonar las mismas
     4 notificaciones de la bandeja, con su enlace a la vista que referencian. */
  function abrirDrawerHTML(titulo, itemsHTML, pie) {
    cerrarDrawer();
    var d = document.createElement("aside");
    d.className = "sg-drawer";
    d.setAttribute("aria-label", titulo);
    d.innerHTML = '<div class="sg-drawer-head"><h2>' + esc(titulo) + "</h2>" +
      '<button class="icon-btn drawer-x" aria-label="Cerrar">' + icono(ICO.x, 18) + "</button></div>" +
      '<ul class="sg-drawer-lista">' + itemsHTML + "</ul>" +
      (pie || "");
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

  /* Rechazo con motivo: modal con textarea + aviso. Reutilizado por la bandeja
     de solicitudes y por la revision de emprendimientos. */
  function rechazarConMotivo(titulo, aviso, msgOk, alRechazar) {
    abrirModal(titulo,
      '<div class="campo"><label for="m-motivo">Motivo del rechazo</label>' +
      '<textarea id="m-motivo" rows="3" placeholder="Explica brevemente el motivo"></textarea></div>' +
      '<p class="modal-aviso">' + esc(aviso) + "</p>",
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Rechazar", clase: "btn btn-peligro", alClic: function () {
            toast(msgOk, "ok");
            if (alRechazar) alRechazar();
          } }
      ]);
  }

  /* Revision de emprendimiento: lee los datos de la fila (dataset) y ofrece
     aprobar o rechazar. Los botones abren un segundo modal, por eso llevan
     cerrar:false (abrirModal ya reemplaza el modal abierto). */
  function revisarEmprendimiento(boton) {
    var d = boton.dataset;
    abrirModal("Revisar emprendimiento",
      '<p class="confirm-texto"><b>Emprendimiento:</b> ' + esc(d.emp || "") + "<br>" +
      "<b>Código:</b> " + esc(d.cod || "") + "<br>" +
      "<b>Estudiante:</b> " + esc(d.estu || "") + "<br>" +
      "<b>Sector:</b> " + esc(d.sector || "") + "<br>" +
      "<b>Tipo:</b> " + esc(d.tipo || "") + "<br>" +
      "<b>Etapa:</b> " + esc(d.etapa || "") + "<br>" +
      "<b>Docente:</b> " + esc(d.docente || "") + "</p>",
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        { txt: "Rechazar", clase: "btn btn-peligro", cerrar: false, alClic: function () {
            rechazarConMotivo("Rechazar emprendimiento",
              "Se notificará al estudiante con este motivo.", "Emprendimiento rechazado");
          } },
        { txt: "Aprobar", clase: "btn btn-primario", cerrar: false, alClic: function () {
            confirmar("Aprobar emprendimiento",
              "El emprendimiento " + (d.emp || "") + " pasará a estado Aprobado y quedará listo para asignar docente.",
              function () { toast("Emprendimiento aprobado", "ok"); });
          } }
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

  /* --- acordeon del menu lateral (grupos desplegables) ------------------- */
  /* Los grupos existen en el NAV jerarquico de Estudiante, Docente y
     Administrador (ver NAV en lib_ui). El grupo con la pagina activa viene
     marcado "abierto" desde el servidor; los demas recuerdan su estado
     entre paginas con localStorage. El click en el boton nav-label togglea
     la clase y su aria-expanded. */
  var CLAVE_NAV = "sgemd:v1:nav:acordeon";
  function navLeer() {
    try { return JSON.parse(localStorage.getItem(CLAVE_NAV)) || []; } catch (e) { return []; }
  }
  function navGuardar(grupos) {
    try { localStorage.setItem(CLAVE_NAV, JSON.stringify(grupos)); } catch (e) {}
  }
  $$(".nav-group").forEach(function (g) {
    var etiqueta = g.getAttribute("data-grupo");
    if ($(".activo", g) || navLeer().indexOf(etiqueta) >= 0) {
      g.classList.add("abierto");
      var lbl = $(".nav-label", g);
      if (lbl) lbl.setAttribute("aria-expanded", "true");
    }
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

  /* --- buscador sobre tablas -------------------------------------------- */
  /* El alcance depende de donde este el buscador. Si vive dentro de la tarjeta
     de la tabla se limita a ella; si esta en la barra de herramientas de la
     pagina (admin/usuarios.html tiene dos tablas) filtra todas, que es lo que
     espera quien escribe en un buscador de cabecera. */
  function alcance(input) {
    var tarjeta = input.closest(".card");
    if (input.closest(".tabla-envoltura") || (tarjeta && $("table.tabla", tarjeta))) return [tarjeta || input.closest(".tabla-envoltura")];
    var zonas = $$(".tabla-envoltura");
    return zonas.length ? zonas : [document];
  }
  /* Estados vacios de listas y tablas (hallazgo MEDIO P6-P10). Cada bloque
     [data-vacio] arranca oculto y se muestra solo cuando su lista queda sin
     items visibles (datos vacios o filtro sin resultados). El alcance es el
     contenedor marcado con data-vacio-lista, la tarjeta/envoltura de tabla
     mas cercana, o el nodo padre; data-vacio-fuente permite apuntar al
     selector concreto de los items de esa lista. */
  function vacioRefrescar() {
    $$("[data-vacio]").forEach(function (v) {
      var sel = v.getAttribute("data-vacio-fuente");
      var caja = v.closest("[data-vacio-lista]") || v.closest(".tabla-envoltura, .card") || v.parentNode;
      var items;
      if (sel) items = $$(sel, caja);
      else if ($("table.tabla", caja)) items = $$("table.tabla tbody tr", caja);
      else items = $$("[data-buscar], .notif", caja);
      if (!sel && !items.length && !$("table.tabla", caja)) return; /* no es una lista */
      var ver = items.filter(function (i) { return !i.hidden; }).length;
      v.hidden = ver > 0;
    });
  }
  function filtrar(input) {
    var q = input.value.trim().toLowerCase();
    var n = 0;
    alcance(input).forEach(function (caja) {
      var tabla = $("table.tabla", caja);
      var filas = tabla ? $$("tbody tr", tabla) : $$("[data-buscar]", caja);
      filas.forEach(function (fila) {
        var hit = !q || fila.textContent.toLowerCase().indexOf(q) >= 0;
        fila.hidden = !hit;
        if (hit) n++;
      });
    });
    var aviso = $("[data-resultados]", input.closest("[data-tabla-zona]") || document);
    if (aviso) aviso.textContent = n + (n === 1 ? " resultado" : " resultados");
    vacioRefrescar();
  }
  $$('input[type="text"][placeholder*="Buscar" i], .buscador input')
    .forEach(function (i) {
      var t;
      i.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { filtrar(i); }, 220); });
      i.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); filtrar(i); } });
    });

  /* --- filtros y chips --------------------------------------------------- */
  function aplicarFiltros() {
    var zona = $("[data-tabla-zona]") || document;
    var tabla = $("table.tabla", zona);
    var selects = $$("select.filtro, select[data-filtro]", zona).filter(function (s) {
      return s.dataset.filtro !== "off";
    });
    var chips = $$(".chip.activo", zona).map(function (c) { return c.dataset.chip; });
    var input = $(".buscador input", zona);
    var q = ((input && input.value) || "").trim().toLowerCase();
    var filas = $$("tbody tr", tabla || zona);
    var n = 0;
    filas.forEach(function (f) {
      var txt = f.textContent.toLowerCase();
      /* Un select filtra cuando el texto de la opcion elegida aparece en la
         fila. La columna se acota con data-filtro-col para no depender del
         texto completo de la celda. */
      var okSel = selects.every(function (s) {
        if (!s.value) return true;
        var opcion = (s.selectedOptions[0] ? s.selectedOptions[0].textContent : "").trim().toLowerCase();
        if (!opcion) return true;
        var col = s.dataset.filtroCol;
        if (col !== undefined && col !== "") {
          var celda = f.children[parseInt(col, 10)];
          return !!celda && celda.textContent.toLowerCase().indexOf(opcion) >= 0;
        }
        return txt.indexOf(opcion) >= 0;
      });
      var okChip = chips.every(function (c) { return !c || txt.indexOf(c.toLowerCase()) >= 0; });
      var okQ = !q || txt.indexOf(q) >= 0;
      f.hidden = !(okSel && okChip && okQ);
      if (!f.hidden) n++;
    });
    var r = $("[data-resultados]", zona);
    if (r) r.textContent = n + (n === 1 ? " resultado" : " resultados");
    guardar({ filtros: n });
    vacioRefrescar();
  }
  $$("[data-filtro]:not([data-filtro='off']), .chip").forEach(function (c) {
    c.addEventListener("click", function () {
      c.classList.toggle("activo");
      aplicarFiltros();
    });
  });
  $$("select[data-filtro]:not([data-filtro='off'])").forEach(function (s) { s.addEventListener("change", aplicarFiltros); });

  /* --- estado de cuenta (Activo/Limitado/Inactivo) ----------------------- */
  $$("select.sel-estado").forEach(function (s) {
    var actual = s.value;
    s.addEventListener("change", function () {
      var nuevo = s.value, nombre = s.dataset.nombre || "la cuenta";
      s.value = actual;
      var aviso = nuevo === "Inactivo"
        ? "La cuenta perderá el acceso hasta que la reactives."
        : (nuevo === "Limitado"
            ? "La cuenta conserva su registro pero con acceso restringido."
            : "La cuenta recuperará el acceso completo.");
      abrirModal("Cambiar estado de la cuenta",
        '<p class="confirm-texto">¿Cambiar el acceso de <b>' + esc(nombre) +
        '</b> a <b>' + esc(nuevo) + '</b>?</p>' +
        '<p class="modal-aviso">' + aviso + '</p>',
        [
          { txt: "Cancelar", clase: "btn btn-secundario" },
          { txt: "Confirmar", clase: "btn btn-primario", alClic: function () {
              actual = nuevo;
              s.value = nuevo;
              toast("Estado actualizado a " + nuevo, "ok");
          } }
        ]);
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

  function accionDe(boton) {
    if (boton.dataset.accion) return boton.dataset.accion;
    return slug(boton.textContent) || slug(boton.getAttribute("aria-label") || "");
  }

  /* Persistencia de formularios del prototipo (PE1 perfil, EE1 editar
     emprendimiento). Se serializa por la etiqueta del <label>, igual que el
     diagnostico (DG4), y se ignoran los campos bloqueados por rol. */
  function etiquetaCampo(box) {
    var l = $("label", box);
    return l ? l.textContent.replace(/\*/g, "").replace(/\s+/g, " ").trim() : "";
  }
  function serializarCampos(raiz) {
    var datos = {};
    $$(".campo", raiz).forEach(function (box) {
      var c = $("input, select, textarea", box);
      if (!c || c.disabled) return;
      datos[etiquetaCampo(box) || c.id] = c.value;
    });
    return datos;
  }
  function restaurarCampos(raiz, datos) {
    if (!datos || typeof datos !== "object") return;
    var porEtiqueta = {};
    Object.keys(datos).forEach(function (k) { porEtiqueta[k.toLowerCase()] = datos[k]; });
    $$(".campo", raiz).forEach(function (box) {
      var c = $("input, select, textarea", box);
      if (!c || c.disabled) return;
      var k = etiquetaCampo(box).toLowerCase();
      if (porEtiqueta[k] != null) c.value = porEtiqueta[k];
    });
  }

  function abrirEditor(titulo, registro) {
    abrirModal(titulo,
      '<div class="campo"><label for="m-campo">Detalle del registro</label>' +
      '<input id="m-campo" type="text" value="' + esc(registro) + '"></div>' +
      '<p class="modal-aviso">Prototipo: el cambio se guarda solo en este navegador.</p>',
      [
        { txt: "Cancelar", clase: "btn btn-secundario" },
        {
          txt: "Guardar", clase: "btn btn-primario", alClic: function () {
            toast("Cambios guardados", "ok");
          }
        }
      ]);
  }

  /* Abre en un modal el formulario que la pagina dejo oculto por id. Se usa
     para fusionar en la pantalla de gestion los formularios de edicion de
     docente/estudiante, que antes eran paginas aparte. */
  var SEQ_FORM = 0;
  /* A34: copia del formulario con ids (y labels for) re-sufijados "-mN" para
     que el modal no duplique los ids del original oculto. Devuelve null si el
     contenedor no existe. */
  function plantillaModal(id) {
    var plantilla = document.getElementById(id);
    if (!plantilla) return null;
    SEQ_FORM += 1;
    var suf = "-m" + SEQ_FORM;
    return plantilla.innerHTML
      .replace(/id="([^"]+)"/g, function (m0, x) { return 'id="' + x + suf + '"'; })
      .replace(/for="([^"]+)"/g, function (m0, x) { return 'for="' + x + suf + '"'; });
  }
  function abrirFormulario(titulo, idForm, boton, txtOk, mensaje) {
    var htmlPlant = plantillaModal(idForm);
    if (!htmlPlant) { abrirEditor(titulo, celdaDe(boton)); return; }
    abrirModal(titulo, htmlPlant, [
      { txt: "Cancelar", clase: "btn btn-secundario" },
      { txt: txtOk || "Guardar", clase: "btn btn-primario", alClic: function () {
        toast(mensaje || "Cambios guardados", "ok");
      } }
    ]);
  }

  /* Nueva/editar asesoria: reusa el formulario #form-asesoria y, al editar,
     prefilla los campos con los data-* de la fila. */
  function abrirFormAsesoria(boton) {
    var d = boton ? boton.dataset : null;
    var editar = !!(d && d.cod);
    abrirFormulario(editar ? "Editar asesoría" : "Nueva asesoría",
      "form-asesoria", boton,
      editar ? "Guardar cambios" : "Crear asesoría",
      editar ? "Cambios guardados en la asesoría" : "Asesoría creada");
    if (editar && d) {
      var m = $(".modal");
      if (!m) return;
      [["estudiante", d.estu], ["docente", d.doc], ["fecha", d.fecha],
       ["hora", d.hora], ["tema", d.tema], ["modalidad", d.mod],
       ["estado", d.estado]].forEach(function (p) {
        var el = m.querySelector("[name='" + p[0] + "']");
        if (el && p[1]) el.value = p[1];
      });
    }
  }

  /* A07: edicion de emprendimiento desde el registro maestro. Reusa el
     formulario #form-emprendimiento y prefilla con los data-* de la fila. */
  function abrirFormEmprendimiento(boton) {
    var d = boton ? boton.dataset : null;
    if (!d || !d.emp) return;
    abrirFormulario("Editar emprendimiento", "form-emprendimiento", boton,
      "Guardar cambios", "Cambios guardados en el emprendimiento");
    var m = $(".modal");
    if (!m) return;
    /* El campo "Código" se pinta con bloqueo (sin name): se setea directo. */
    var cod = m.querySelector("input[disabled]");
    if (cod && d.cod) cod.value = d.cod;
    [["nombre", d.emp], ["estudiante", d.estu],
     ["sector", d.sector], ["tipo", d.tipo], ["etapa", d.etapa],
     ["avance", d.avance], ["docente", d.doc]].forEach(function (p) {
      var el = m.querySelector("[name='" + p[0] + "']");
      if (el && p[1]) el.value = p[1];
    });
  }

  /* --- ficha de un registro (detalle real, no el modal generico) -------- */
  /* Item 2: en vez del texto de relleno "Detalle del registro", se arma una
     ficha con los datos reales de la fila/tarjeta que disparo el boton. Las
     celdas de las tablas ya traen data-label (ver lib_ui.tabla). */
  function fichaDe(boton) {
    var filas = [];
    var texto = celdaDe(boton);
    var titulo = "Detalle del registro";
    var cont = boton.closest("tr") || boton.closest("article, li, .aviso, .card");
    if (cont) {
      var tds = $$("td", cont).filter(function (td) {
        return !td.classList.contains("acc") && !td.classList.contains("sel");
      });
      if (tds.length) {
        var tabla = boton.closest("table");
        var ths = tabla ? $$("thead th", tabla) : [];
        tds.forEach(function (td, i) {
          var lbl = td.getAttribute("data-label");
          if (!lbl && ths.length === tds.length) {
            lbl = ths[i].textContent.replace(/\s+/g, " ").trim();
          }
          filas.push([lbl || ("Campo " + (i + 1)), td.innerHTML]);
        });
        var t0 = tds[0].textContent.replace(/\s+/g, " ").trim();
        if (t0) titulo = t0;
      } else {
        var h = $(".ln-titulo", cont) || $(".kan-card-titulo", cont) ||
                $(".aviso-titulo", cont) || $("h3, h4, strong, b", cont);
        if (h) titulo = h.textContent.replace(/\s+/g, " ").trim();
        var fecha = $(".ln-fecha", cont);
        if (fecha) filas.push(["Fecha", fecha.textContent.replace(/\s+/g, " ").trim()]);
        var meta = $(".ln-meta, .kan-meta, .aviso-meta", cont);
        if (meta) filas.push(["Detalle", meta.textContent.replace(/\s+/g, " ").trim()]);
        $$("dt", cont).forEach(function (dt) {
          filas.push([
            dt.textContent.replace(/\s+/g, " ").trim(),
            dt.nextElementSibling ? dt.nextElementSibling.innerHTML : ""
          ]);
        });
        var bd = $$(".badge", cont);
        if (bd.length) {
          filas.push(["Estado", bd.map(function (x) { return x.outerHTML; }).join(" ")]);
        }
      }
    }
    return { titulo: titulo, filas: filas, texto: texto };
  }
  function htmlFicha(f, nota) {
    var h;
    if (f.filas.length) {
      h = '<dl class="lista-def">';
      f.filas.forEach(function (kv) {
        h += '<div class="def-row"><dt>' + esc(kv[0]) + '</dt><dd>' + kv[1] + '</dd></div>';
      });
      h += "</dl>";
    } else {
      h = '<p class="confirm-texto">' + esc(f.texto) + '</p>';
    }
    if (nota) h += '<p class="modal-aviso">' + esc(nota) + '</p>';
    return h;
  }

  /* --- kanban (A03) -------------------------------------------------------- */
  /* Mueve una tarjeta entre columnas del kanban de eventos, ajusta su pie
     (badge + acciones) y actualiza los contadores y las notas de columna vacia. */
  function kanbanColumnas(titulo) {
    var col = null;
    $$(".kan-col").forEach(function (c) {
      var t = c.querySelector(".kan-titulo");
      if (t && t.textContent === titulo) col = c;
    });
    return col;
  }
  function kanbanContar() {
    $$(".kan-col").forEach(function (c) {
      var n = c.querySelector(".kan-n");
      if (n) n.textContent = String(c.querySelectorAll(".kan-card").length);
    });
  }
  function kanbanMover(card, tituloDestino, badgeHTML, pieHTML) {
    var pie = card.querySelector(".kan-foot");
    if (pie) pie.innerHTML = (badgeHTML || "") + (pieHTML || "");
    var origen = card.closest(".kan-col");
    var destino = kanbanColumnas(tituloDestino);
    if (destino) {
      var v = destino.querySelector(".kan-empty");
      if (v) destino.insertBefore(card, v);
      else destino.appendChild(card);
    }
    if (origen && !origen.querySelector(".kan-card") &&
        !origen.querySelector(".kan-empty")) {
      var e = document.createElement("div");
      e.className = "kan-empty";
      e.textContent = "Sin pendientes";
      origen.appendChild(e);
    }
    kanbanContar();
  }
  function editarEventoLink() {
    return '<a class="btn btn-sm btn-secundario" href="evento-form.html">Editar</a>';
  }
  function botonAprobarEvento(b) {
    var d = b.dataset;
    var f = {
      titulo: "Detalle del evento",
      filas: [
        ["Evento", esc(d.titulo || "")],
        ["Fecha y hora", esc(d.fecha || "")],
        ["Lugar", esc(d.lugar || "")],
        ["Confirmados", esc((d.confirmados || "") + " confirmaciones")],
        ["Dirigido a", esc(d.sector || "")],
      ],
    };
    var nota = "Se publicará y notificará a los estudiantes del sector correspondiente.";
    abrirModal("Aprobar evento", htmlFicha(f, nota), [
      { txt: "Cancelar", clase: "btn btn-secundario" },
      { txt: "Publicar y notificar", clase: "btn btn-primario", alClic: function () {
          var card = b.closest(".kan-card");
          kanbanMover(card, "Publicado",
            '<span class="badge b-azul">' + icono(ICO.check, 12) + " Publicado</span>",
            editarEventoLink());
          toast("Evento publicado y notificado a los estudiantes", "ok");
        } }
    ]);
  }

  /* --- descargas reales (item 3) ---------------------------------------- */
  function descargarArchivo(nombre, contenido, mime) {
    try {
      var blob = new Blob([contenido], { type: mime || "text/plain;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
      return true;
    } catch (err) { return false; }
  }
  function csvDeTabla() {
    var t = $("main table.tabla") || $("table.tabla");
    if (!t) return null;
    var filas = [];
    $$("tr", t).forEach(function (tr) {
      var celdas = $$("th, td", tr).filter(function (c) {
        return !c.classList.contains("acc") && !c.classList.contains("sel") && !$("input", c);
      }).map(function (c) {
        return '"' + c.textContent.replace(/\s+/g, " ").trim().replace(/"/g, '""') + '"';
      });
      if (celdas.length) filas.push(celdas.join(";"));
    });
    return filas.length ? "\uFEFF" + filas.join("\r\n") : null;
  }
  /* A27: pantallas sin tabla (metricas, tableros) exportan un resumen de los
     indicadores mostrados en lugar de no exportar nada. */
  function csvDeMetricas() {
    var tiles = $$(".metricas .metrica, .grid.g-4 > .metrica, .metrica");
    var filas = [];
    tiles.forEach(function (t) {
      var lbl = $(".metrica-lbl", t), val = $(".metrica-val", t);
      if (lbl && val) {
        filas.push('"' + lbl.textContent.trim().replace(/"/g, '""') + '";' +
          '"' + val.textContent.replace(/\s+/g, " ").trim().replace(/"/g, '""') + '"');
      }
    });
    return filas.length ? "\uFEFF" + filas.join("\r\n") : null;
  }
  /* F1 (vista #10): plantilla de exportacion de reportes. Se descarga con la
     misma cabecera que el reporte maestro para cargar la informacion luego. */
  function csvPlantillaReporte() {
    var filas = [
      '"Emprendimiento";"Docente";"Estudiante";"Sector";"Etapa";"% de avance";"Horas trabajadas";"Nota promedio"',
      '"";"";"";"";"";"";"";""',
    ];
    return "\uFEFF" + filas.join("\r\n");
  }
  function tablaComoHTML() {
    var t = $("main table.tabla") || $("table.tabla");
    if (!t) return "";
    var c = t.cloneNode(true);
    $$("th.acc, td.acc, input, button, a.table-act", c).forEach(function (n) { n.remove(); });
    return c.outerHTML;
  }
  /* Item 3: documento imprimible de la pantalla. Si hay tabla principal se
     imprime la tabla; si no (tarjetas, kanban, linea de tiempo) se imprime una
     copia legible del contenido, sin controles ni paneles ocultos. */
  function vistaDocumento() {
    var t = tablaComoHTML();
    if (t) return t;
    var main = $("main.content") || $("main");
    if (!main) return "";
    var c = main.cloneNode(true);
    $$("button, input, select, textarea, script, .tabs, .toolbar, .buscador, .crumbs, .page-head, [hidden]", c)
      .forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
    return c.innerHTML;
  }
  function tituloPagina() {
    var h = $("main .page-head h1") || $("main h1");
    return h ? h.textContent.replace(/\s+/g, " ").trim() : document.title;
  }
  var CSS_DOC =
    "body{font-family:Inter,Arial,sans-serif;color:#051533;margin:36px;line-height:1.5}" +
    "h1{font-size:20px;margin:0 0 6px}.doc-meta{color:#162644;font-size:13px;margin-bottom:18px}" +
    "dl.lista-def{margin:0}dl.lista-def .def-row{display:flex;gap:12px;border-bottom:1px solid #bbbbbb;padding:7px 0}" +
    "dt{width:190px;color:#162644;font-size:13px}dd{margin:0;flex:1;font-size:13px}" +
    "table{border-collapse:collapse;width:100%;font-size:13px;margin-top:12px}" +
    "th,td{border:1px solid #bbbbbb;padding:6px 8px;text-align:left}th{background:#ffffff}" +
    "footer{margin-top:24px;font-size:13px;color:#162644;border-top:1px solid #bbbbbb;padding-top:8px}" +
    "h2,h3{font-size:14px;margin:14px 0 4px}ul{margin:8px 0 8px 18px}li{margin:2px 0}" +
    ".badge{display:inline-block;border:1px solid #bbbbbb;border-radius:999px;padding:1px 7px;font-size:13px;margin-right:4px}" +
    ".card{margin:10px 0;border:1px solid #bbbbbb;border-radius:6px;padding:8px 10px}" +
    ".kan-col,.ln-item,.aviso{margin-bottom:8px}" +
    /* Kanban, tarjetas y avisos se imprimen como bloques apilados y legibles
       (tareas.html no tiene tabla principal: su PDF se arma con el contenido). */
    ".kanban,.kanban[data-cols]{display:block;grid-template-columns:none}" +
    ".kan-col{border:1px solid #bbbbbb;border-radius:6px;padding:8px 10px;margin-bottom:10px}" +
    ".kan-head{display:flex;justify-content:space-between;font-weight:700;font-size:13px;margin-bottom:6px}" +
    ".kan-card{border:1px solid #bbbbbb;border-radius:6px;padding:6px 8px;margin-bottom:6px}" +
    ".kan-card-titulo{font-weight:600;font-size:13px}.kan-meta,.kan-foot{font-size:13px;color:#162644}" +
    ".grid,.emp-grid{display:block}" +
    ".metrica{border:1px solid #bbbbbb;border-radius:6px;padding:8px 10px;margin:8px 0}" +
    ".metrica-val{font-size:18px;font-weight:700}.metrica-lbl{font-size:13px;color:#162644}" +
    ".barra{height:6px;background:#bbbbbb;border-radius:999px;margin-top:6px}" +
    ".barra span{display:block;height:6px;background:#004a93;border-radius:999px}" +
    ".mini-aviso,.metrica-enlace{display:block;border:0;padding:0;background:none}.mini-prev,.chip{display:none}" +
    "details>*{display:block!important}details>summary{display:none}" +
    ".desp-item{display:block;border-bottom:1px solid #bbbbbb;padding:5px 0;font-size:13px}" +
    ".emp-card,.aviso-grp,.notif{border:1px solid #bbbbbb;border-radius:6px;padding:8px 10px;margin-bottom:8px}" +
    ".tabs,.crumbs,.page-head,.acciones,.toolbar,.paginacion{display:none}" +
    ".linea{display:block}.ln-dia,.ln-mes{font-weight:700}" +
    ".coment{margin:8px 0}.coment-txt{border-left:3px solid #004a93;padding:6px 10px;background:#ffffff}";
  function imprimirDocumento(titulo, cuerpoHTML) {
    var w = window.open("", "_blank");
    if (!w) { toast("Activa las ventanas emergentes para generar el PDF", "info"); return false; }
    w.document.write(
      "<!DOCTYPE html>" + "<" + 'html lang="es"><head><meta charset="utf-8"><title>' + esc(titulo) + "</title>" +
      "<style>" + CSS_DOC + "</style></head><body><h1>" + esc(titulo) + "</h1>" +
      '<div class="doc-meta">SGEMD &middot; Centro Progresa EPE &ndash; UNIMINUTO &middot; ' +
      new Date().toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" }) + "</div>" +
      (cuerpoHTML || "") +
      "<footer>Documento generado desde el prototipo SGEMD.</footer></body>" + "</" + "html>");
    w.document.close();
    w.focus();
    setTimeout(function () { try { w.print(); } catch (e) {} }, 350);
    return true;
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("button, a.btn");
    if (!b) return;
    /* Acordeon del menu: el nav-label es boton propio, no pasa por el switch */
    if (b.classList.contains("nav-label")) {
      var gr = b.closest(".nav-group");
      if (!gr) return;
      var abrir = !gr.classList.contains("abierto");
      gr.classList.toggle("abierto", abrir);
      b.setAttribute("aria-expanded", abrir ? "true" : "false");
      var lista = navLeer();
      var etiqueta = gr.getAttribute("data-grupo");
      var idx = lista.indexOf(etiqueta);
      if (abrir && idx < 0) lista.push(etiqueta);
      if (!abrir && idx >= 0) lista.splice(idx, 1);
      navGuardar(lista);
      return;
    }
    var accion = accionDe(b);
    var registro = celdaDe(b);

    /* Un enlace con destino real navega: el shell lo pone en el <a> y el
       prototipo no lo reescribe. Los href="#" si se atienden aqui. */
    if (b.tagName === "A" && b.getAttribute("href") !== "#") return;

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
      case "detalle": {
        /* Item 2: ficha con los datos reales del registro seleccionado. */
        e.preventDefault();
        var ficha = fichaDe(b);
        abrirModal(ficha.titulo,
          htmlFicha(ficha, "Vista del prototipo: los datos provienen del registro seleccionado; en producción se cargaría el expediente completo."),
          [
            { txt: "Cerrar", clase: "btn btn-secundario" },
            {
              txt: "Generar PDF", clase: "btn btn-primario", alClic: function () {
                imprimirDocumento(ficha.titulo, htmlFicha(ficha, ""));
              }
            }
          ]);
        break;
      }

      case "ver-acta": {
        e.preventDefault();
        var acta = fichaDe(b);
        acta.titulo = "Acta de la asesoría";
        abrirModal(acta.titulo,
          htmlFicha(acta, "Acta de compromiso y confidencialidad del componente de Emprendimiento (Centro Progresa EPE — UNIMINUTO)."),
          [
            { txt: "Cerrar", clase: "btn btn-secundario" },
            {
              txt: "Descargar acta", clase: "btn btn-primario", alClic: function () {
                imprimirDocumento(acta.titulo, htmlFicha(acta, ""));
              }
            }
          ]);
        break;
      }

      case "editar-docente":
        e.preventDefault();
        abrirFormulario("Editar docente", "form-docente", b);
        break;

      case "editar-estudiante":
        e.preventDefault();
        abrirFormulario("Editar estudiante", "form-estudiante", b);
        break;

      case "nuevo-docente":
        e.preventDefault();
        abrirFormulario("Nuevo docente", "form-nuevo-docente", b,
          "Crear docente", "Docente creado. Se enviará el correo de activación.");
        break;

      case "nuevo-estudiante":
        e.preventDefault();
        abrirFormulario("Nuevo estudiante", "form-nuevo-estudiante", b,
          "Crear estudiante", "Estudiante creado. Se enviará el correo de activación.");
        break;

      case "dar-de-baja":
        /* A-4: baja lógica con efecto en cascada. Las asignaciones,
           solicitudes y comentarios del usuario quedan inactivos. */
        e.preventDefault();
        var filaBaja = filaDe(b);
        var nomBaja = "";
        if (filaBaja && filaBaja.children[1]) {
          nomBaja = (filaBaja.children[1].textContent || "")
            .replace(/\s+/g, " ").trim();
        }
        confirmar("Dar de baja",
          "Se dará de baja a " + (nomBaja || "este usuario") + ". Sus asignaciones, " +
          "solicitudes y comentarios quedarán inactivos. Puedes revertirlo cambiando " +
          "el estado de acceso a Activo.",
          function () {
            if (filaBaja) filaBaja.remove();
            toast("Usuario dado de baja. Cascada aplicada.", "ok");
            if (typeof vacioRefrescar === "function") vacioRefrescar();
          });
        break;

      case "solicitud-aprobar":
        e.preventDefault();
        confirmar("Aprobar solicitud",
          "Se aplicará el cambio y se notificará al solicitante. ¿Confirmas la aprobación?",
          function () { toast("Solicitud aprobada", "ok"); });
        break;

      case "solicitud-rechazar":
        e.preventDefault();
        rechazarConMotivo("Rechazar solicitud",
          "El solicitante recibirá este motivo en su notificación.", "Solicitud rechazada");
        break;

      case "revisar-emprendimiento":
        e.preventDefault();
        revisarEmprendimiento(b);
        break;

      case "nueva-asesoria":
        e.preventDefault();
        abrirFormAsesoria(b);
        break;

      case "editar-asesoria":
        e.preventDefault();
        abrirFormAsesoria(b);
        break;

      case "editar-emprendimiento":
        /* A07: abre el formulario real de edicion del emprendimiento. */
        e.preventDefault();
        abrirFormEmprendimiento(b);
        break;

      case "ver-instrumento": {
        /* A16: desplega el instrumento del diagnostico (solo lectura). */
        e.preventDefault();
        var instr = document.getElementById("contenido-instrumento");
        if (!instr) { toast("Instrumento no disponible", "error"); break; }
        abrirModal("Instrumento del diagnóstico", instr.innerHTML,
          [{ txt: "Cerrar", clase: "btn btn-primario" }]);
        break;
      }

      case "cancelar-asesoria": {
        e.preventDefault();
        var dd = b.dataset;
        confirmar("Cancelar asesoría",
          "Se cancelará la asesoría de " + (dd.estu || "se") +
          " del " + (dd.fecha || "esa fecha") +
          (dd.hora ? " a las " + dd.hora : "") + ". ¿Confirmas?",
          function () { toast("Asesoría cancelada", "ok"); });
        break;
      }

      case "aprobar-evento": {
        e.preventDefault();
        botonAprobarEvento(b);
        break;
      }

      case "rechazar-evento": {
        e.preventDefault();
        var cardEv = b.closest(".kan-card");
        rechazarConMotivo("Rechazar evento",
          "El evento volverá a borrador y su autor será notificado.",
          "Evento rechazado",
          function () {
            kanbanMover(cardEv, "Borrador",
              '<span class="badge b-neutra">' + icono(ICO.alerta, 12) + " Rechazado</span>",
              editarEventoLink());
          });
        break;
      }

      case "editar":
        e.preventDefault();
        abrirEditor("Editar registro", registro);
        break;

      case "registrar-avance":
        e.preventDefault();
        var fila = filaDe(b);
        if (!fila) return;
        var cod = fila.dataset.cod;
        var emp = fila.dataset.emp;
        var estu = fila.dataset.estu;
        var etapa = fila.dataset.etapa;
        var avanceActual = Number(fila.dataset.avance || 0);
        // Llenar prefill en el formulario embebido
        document.querySelector("[name=emp]").value = emp;
        document.querySelector("[name=estu]").value = estu;
        document.querySelector("[name=etapa]").value = etapa;
        document.querySelector("[name=avance]").value = Math.round(avanceActual);
        abrirFormulario("Registrar avance", "form-avance", b, "Guardar", "Avance guardado");
        break;

      case "asignar-docente":
        e.preventDefault();
        var fila = filaDe(b);
        if (!fila) return;
        var cod = fila.dataset.cod;
        var emp = fila.dataset.emp;
        var estu = fila.dataset.estu;
        // Prefill: bloquear campos Estudiante/Emprendimiento/Correo
        var modal = document.querySelector("#form-asignar-docente");
        if (modal) {
          modal.querySelector("[name=estudiante]").value = estu;
          modal.querySelector("[name=emprendimiento]").value = emp;
          modal.querySelector("[name=correo]").value = CORREOS_EST[estu] || "";
          // Bloquear inputs
          var campos = modal.querySelectorAll("input, select");
          campos.forEach(function(c) { c.disabled = true; });
          // Mostrar badge asignado
          var badge = modal.querySelector(".badge-asignado");
          if (badge) badge.textContent = "Asignado a " + estu;
          // Refrescar vacío
          if (typeof vacioRefrescar === "function") vacioRefrescar();
          abrirModal("Asignar docente", plantillaModal("form-asignar-docente"), [
            { txt: "Cancelar", clase: "btn btn-secundario" },
            { txt: "Confirmar", clase: "btn btn-primario", alClic: function() {
              // Guardar asignación y cerrar
              toast("Docente asignado", "ok");
              if (typeof vacioRefrescar === "function") vacioRefrescar();
              cerrarModal();
            } }
          ]);
        }
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
      case "descargar-pdf": {
        /* Item 3: descarga real. Se abre un documento imprimible para que el
           usuario lo guarde como PDF (no hay backend en el prototipo). */
        e.preventDefault();
        var rotulo = b.textContent.replace(/\s+/g, " ").trim() || "Documento";
        imprimirDocumento(rotulo + " - " + tituloPagina(),
          '<p class="doc-meta">' + esc(tituloPagina()) + "</p>" + vistaDocumento());
        toast("Abriendo documento para guardar como PDF…", "info");
        break;
      }

      case "exportar":
      case "exportar-reporte": {
        /* A27: exporta CSV de la tabla de la pantalla y, si no hay tabla
           (paginas de metricas/tablero), un resumen de las metricas. */
        var csv = csvDeTabla() || csvDeMetricas();
        e.preventDefault();
        if (csv) {
          descargarArchivo(slug(tituloPagina() || "reporte") + ".csv", csv, "text/csv;charset=utf-8");
          toast("Reporte exportado (CSV)", "ok");
        } else {
          toast("Esta pantalla no tiene tabla para exportar", "info");
        }
        break;
      }

      case "exportar-expediente": {
        /* El boton "Exportar" de Mi emprendimiento genera el expediente: el
           reporte completo de la pantalla, listo para guardar como PDF. */
        e.preventDefault();
        imprimirDocumento("Expediente - " + tituloPagina(),
          '<p class="doc-meta">' + esc(tituloPagina()) +
          " &middot; reporte completo</p>" + vistaDocumento());
        toast("Abriendo el expediente para guardar como PDF…", "info");
        break;
      }

      case "cambiar-foto": {
        /* Subida de la imagen del estudiante (PNG/JPG) con vista previa real. */
        e.preventDefault();
        var inpFoto = document.createElement("input");
        inpFoto.type = "file";
        inpFoto.accept = "image/png,image/jpeg";
        inpFoto.addEventListener("change", function () {
          var f = inpFoto.files && inpFoto.files[0];
          if (!f) return;
          var caja = $(".perfil-foto");
          if (caja) {
            caja.innerHTML = '<img src="' + URL.createObjectURL(f) + '" alt="Foto del estudiante">';
          }
          toast("Imagen actualizada: " + f.name, "ok");
        });
        inpFoto.click();
        break;
      }

      case "inscribirse":
        e.preventDefault();
        var_inscribir(b);
        break;

      case "seccion-siguiente":
        /* DG1: navega al siguiente panel del cuestionario y actualiza los pasos. */
        e.preventDefault();
        if (panelesDiag.length) {
          var sig = Math.min(diagPanelActual() + 1, panelesDiag.length - 1);
          diagMostrar(sig);
          guardar({ seccionDiag: sig });
        }
        break;

      case "seccion-anterior":
        e.preventDefault();
        if (panelesDiag.length) {
          var ant = Math.max(diagPanelActual() - 1, 0);
          diagMostrar(ant);
          guardar({ seccionDiag: ant });
        }
        break;

      case "enviar-diagnostico":
        /* DG4: persiste el envio del cuestionario completo. Al terminar se
           vuelve a la pagina de resultados (E001: re-responder y regresar). */
        e.preventDefault();
        guardar({ enviado: true, fecha: new Date().toISOString().slice(0, 10) });
        toast("Diagnóstico enviado al docente", "ok");
        b.innerHTML = "Diagnóstico enviado " + icono(ICO.check, 15);
        b.disabled = true;
        setTimeout(function () { location.href = "diagnostico-resultados.html"; }, 750);
        break;

      case "guardar-borrador":
        /* DG4: el avance real del formulario se persiste en localStorage. */
        e.preventDefault();
        var borrador = {};
        $$(".campo input, .campo select, .campo textarea").forEach(function (c) {
          var lbl = c.closest(".campo") ? $("label", c.closest(".campo")) : null;
          borrador[lbl ? lbl.textContent.replace(/\s+/g, " ").trim() : c.id] = c.value;
        });
        guardar({ borrador: borrador, seccionDiag: panelesDiag.length ? diagPanelActual() : null });
        toast("Borrador guardado. Puedes retomar donde quedaste.", "ok");
        break;

      case "guardar-y-salir":
        e.preventDefault();
        var borrador2 = {};
        $$(".campo input, .campo select, .campo textarea").forEach(function (c) {
          var lbl = c.closest(".campo") ? $("label", c.closest(".campo")) : null;
          borrador2[lbl ? lbl.textContent.replace(/\s+/g, " ").trim() : c.id] = c.value;
        });
        guardar({ borrador: borrador2, seccionDiag: panelesDiag.length ? diagPanelActual() : null });
        toast("Avance guardado. Volviendo al inicio…", "ok");
        setTimeout(function () { location.href = "dashboard.html"; }, 800);
        break;

      case "enviar-solicitud":
        /* SA3: "Enviar solicitud" crea la solicitud de asesoria (persistencia
           local del prototipo), la guarda en el estado de la pagina y deja el
           boton en estado "enviada" para que no se duplique. */
        e.preventDefault();
        var cardSol = b.closest(".card");
        var datosSol = {};
        if (cardSol) {
          $$("input, select, textarea", cardSol).forEach(function (c) {
            if (!c.value) return;
            var e2 = c.closest(".campo") ? $("label", c.closest(".campo")) : null;
            var k = e2 ? e2.textContent.replace(/\s+/g, " ").trim() : (c.placeholder || c.name || "campo");
            datosSol[k] = c.value;
          });
        }
        guardar({ solicitud: datosSol, enviada: true, fecha: new Date().toISOString().slice(0, 10) });
        toast("Solicitud enviada al docente", "ok");
        b.innerHTML = "Solicitud enviada " + icono(ICO.check, 15);
        b.disabled = true;
        break;

      case "guardar-perfil":
        /* PE1: persiste los datos personales del perfil (localStorage). */
        e.preventDefault();
        var activo = document.querySelector(".campos-perfil") || b.closest(".card") || document;
        guardar({ perfil: serializarCampos(activo) });
        toast("Datos personales guardados", "ok");
        break;

      case "cancelar-perfil":
        /* PE4: descarta la edición y repone lo último guardado. */
        e.preventDefault();
        var guardadoPerfil = store(true);
        restaurarCampos(document, guardadoPerfil && guardadoPerfil.perfil);
        toast("Cambios descartados", "info");
        break;

      case "actualizar-contrasena":
        /* PE2: valida contraseña actual + nueva + confirmación. El prototipo
           no guarda la contraseña (la spec: nunca se devuelve ni se muestra);
           solo deja constancia de que se cambió. */
        e.preventDefault();
        var claves = $$('input[type="password"]', b.closest(".card") || document);
        var vActual = claves[0] ? claves[0].value : "";
        var vNueva = claves[1] ? claves[1].value : "";
        var vRepetir = claves[2] ? claves[2].value : "";
        if (!vActual || !vNueva || !vRepetir) {
          toast("Completa la contraseña actual, la nueva y su confirmación", "error");
          break;
        }
        if (vNueva.length < 8) {
          toast("La nueva contraseña debe tener al menos 8 caracteres", "error");
          break;
        }
        if (vNueva === vActual) {
          toast("La nueva contraseña debe ser distinta de la actual", "error");
          break;
        }
        if (vNueva !== vRepetir) {
          toast("La nueva contraseña y su confirmación no coinciden", "error");
          break;
        }
        guardar({ claveCambiada: new Date().toISOString().slice(0, 10) });
        claves.forEach(function (c) { c.value = ""; });
        toast("Contraseña actualizada correctamente", "ok");
        break;

      case "guardar-emprendimiento":
        /* EE1: persiste los datos editables del emprendimiento. */
        e.preventDefault();
        guardar({ emprendimiento: serializarCampos(b.closest(".card") || document) });
        toast("Cambios guardados en el emprendimiento", "ok");
        break;

      case "guardar":
      case "guardar-cambios":
      case "guardar-recomendaciones":
      case "enviar":
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

      case "adjuntar-evidencias":
        /* TD1: abre el input file real de la tarea (o cae al fallback generico). */
        e.preventDefault();
        if (evInput) evInput.click();
        else pedirArchivo(b);
        break;

      case "quitar-adjunto":
        /* TD2: quita un adjunto de la lista y persiste el estado. */
        e.preventDefault();
        var nombreAdj = b.dataset.nombre || "";
        evArchivos = evArchivos.filter(function (f) { return f.nombre !== nombreAdj; });
        pintarAdjuntos();
        guardar({ adjuntos: evArchivos });
        toast("Adjunto quitado", "info");
        break;

      case "marcar-completada":
        /* TD3: solo se puede marcar con evidencia adjunta; persiste el estado. */
        e.preventDefault();
        if (!evArchivos.length) {
          toast("Adjunta al menos un archivo de evidencia", "error");
          break;
        }
        guardar({ completada: true, adjuntos: evArchivos });
        b.disabled = true;
        b.innerHTML = "Completada " + icono(ICO.check, 15);
        toast("Tarea enviada a revisión", "ok");
        break;

      case "notificaciones":
        e.preventDefault();
        var fuenteN = $("[data-notif-fuente]");
        if (fuenteN) {
          abrirDrawerHTML("Notificaciones", fuenteN.innerHTML,
            '<div class="sg-drawer-pie">' +
            '<button class="btn btn-acento" data-accion="ver-todas-notificaciones">' +
            icono(ICO.doc, 16) + " Ver todas las notificaciones</button></div>");
          break;
        }
        abrirDrawer("Notificaciones", [
          "Nueva revisión de tu Startup Week II",
          "Tu docente registró un avance",
          "Se publicó un evento nuevo",
          "Recordatorio: evidencia de tarea pendiente"
        ], '<div class="sg-drawer-pie">' +
          '<button class="btn btn-acento" data-accion="ver-todas-notificaciones">' +
          icono(ICO.doc, 16) + " Ver todas las notificaciones</button></div>");
        break;

      case "ver-todas-notificaciones":
        /* La campana de la esquina superior derecha reemplaza al item del menu
           lateral: "Ver todas" navega a la bandeja completa. */
        e.preventDefault();
        cerrarDrawer();
        location.href = "notificaciones.html";
        break;

      case "cerrar-sesion":
        e.preventDefault();
        confirmar("Cerrar sesión", "¿Seguro que quieres cerrar tu sesión?", cerrarSesion);
        break;

      case "marcar-todas-como-leidas":
        e.preventDefault();
        var porLeer = 0;
        $$(".notif").forEach(function (n) {
          if (n.classList.contains("no-leida")) {
            n.classList.remove("no-leida");
            var punto = $(".notif-dot", n);
            if (punto) punto.remove();
            porLeer++;
          }
        });
        $$(".aviso").forEach(function (aviso) {
          var leer = $('[data-accion="aprobar"]', aviso);
          if (leer && !leer.classList.contains("hecho")) {
            leer.classList.add("hecho");
            leer.setAttribute("aria-pressed", "true");
            porLeer++;
          }
        });
        if (typeof notifRefrescar === "function") notifRefrescar();
        if (typeof notifPersistir === "function") notifPersistir();
        toast(porLeer ? "Todas las notificaciones marcadas como leídas" : "No hay notificaciones sin leer", porLeer ? "ok" : "info");
        break;

        /* F1 (vista #10): los botones de las pantallas de flujo sin accion
         asignada ahora ejecutan su transicion correspondiente. */
      case "confirmar-asignacion":
        e.preventDefault();
        confirmar("Confirmar asignación",
          "Se confirmará la asignación de Carlos Mendoza como docente de Aromas del Sur (2 h por semana).",
          function () {
            toast("Asignación confirmada", "ok");
            setTimeout(function () { window.location.href = "asignaciones.html"; }, 750);
          });
        break;

      case "publicar-evento":
        e.preventDefault();
        confirmar("Publicar evento",
          "El evento quedará visible para docentes y estudiantes. ¿Publicar?",
          function () {
            toast("Evento publicado", "ok");
            setTimeout(function () { window.location.href = "eventos.html"; }, 750);
          });
        break;

      case "crear-respaldo":
        e.preventDefault();
        confirmar("Crear respaldo",
          "Se generará un respaldo completo de la base de datos (aprox. 84 MB).",
          function () {
            var tarjeta = b.closest(".card");
            var tb = tarjeta ? $("tbody", tarjeta) : null;
            if (tb) {
              var f = document.createElement("tr");
              var d = new Date();
              var hh = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
              var fecha = d.getDate() + " " + ["ene", "feb", "mar", "abr", "may", "jun",
                "jul", "ago", "sep", "oct", "nov", "dic"][d.getMonth()] + " " +
                d.getFullYear() + ", " + hh;
              var cod = "BKP-" + d.getFullYear() + ("0" + (d.getMonth() + 1)).slice(-2) +
                ("0" + d.getDate()).slice(-2) + "-" + hh.replace(":", "");
              f.innerHTML =
                "<td><b>" + cod + "</b></td><td>Completo</td><td>" + fecha + "</td>" +
                "<td>84 MB</td><td>Exitosa</td>" +
                '<td class="acciones-cell"><button data-accion="descargar" title="Descargar" ' +
                'aria-label="Descargar">' + icono(ICO.descargar, 16) + "</button></td>";
              tb.insertBefore(f, tb.firstElementChild);
            }
            toast("Respaldo creado", "ok");
          });
        break;

      case "generar-reporte":
        e.preventDefault();
        confirmar("Generar reporte",
          "Se generará el reporte maestro para 46 emprendimientos (aprox. 1.284 filas). El archivo quedará disponible en Reportes.",
          function () { toast("Reporte en cola de generación", "info"); });
        break;

      case "descargar-plantilla":
        e.preventDefault();
        descargarArchivo("plantilla-reporte.csv", csvPlantillaReporte(), "text/csv;charset=utf-8");
        toast("Plantilla descargada", "ok");
        break;

      case "asignar-tarea":
        e.preventDefault();
        abrirFormulario("Asignar tarea", "form-tarea", b, "Crear tarea", "Tarea asignada");
        break;

      case "editar-tarea":
        e.preventDefault();
        abrirFormulario("Editar tarea", "form-tarea", b, "Guardar cambios",
          "Tarea actualizada");
        break;

      case "eliminar-tarea":
        e.preventDefault();
        var filaTarea = filaDe(b);
        var titTarea = "";
        if (filaTarea && filaTarea.children[0]) {
          titTarea = (filaTarea.children[0].textContent || "")
            .replace(/\s+/g, " ").trim();
        }
        confirmar("Eliminar tarea",
          "Se eliminará: " + (titTarea || "la tarea") + ". Los estudiantes " +
          "dejarán de verla. Esta acción no se puede deshacer.",
          function () {
            if (filaTarea) filaTarea.remove();
            toast("Tarea eliminada", "ok");
            if (typeof vacioRefrescar === "function") vacioRefrescar();
          });
        break;

      case "nueva-tarea":
        /* V3: alta real. El modal reutiliza #form-tarea y, al confirmar,
           lee los campos y agrega la fila a la tabla del admin. */
        e.preventDefault();
        var plantNueva = plantillaModal("form-tarea");
        if (!plantNueva) break;
        abrirModal("Nueva tarea", plantNueva, [
          { txt: "Cancelar", clase: "btn btn-secundario" },
          { txt: "Crear tarea", clase: "btn btn-primario", alClic: function (veloT) {
              var vals = {};
              $$(".campo", veloT).forEach(function (c) {
                var lbl = $("label", c);
                var el = $("input, select, textarea", c);
                if (lbl && el) {
                  vals[lbl.textContent.replace(/\*/g, "").replace(/\s+/g, " ")
                    .trim().toLowerCase()] = el.value;
                }
              });
              var titT = (vals["título de la tarea"] || "").trim() || "Nueva tarea";
              var empT = (vals["emprendimiento"] || "").trim();
              if (!empT || empT.indexOf("- Elegir") === 0) empT = "Sin emprendimiento";
              var estT = (vals["estudiante"] || "").trim();
              if (!estT || estT.indexOf("- Elegir") === 0) estT = "Sin estudiante";
              var prioT = (vals["prioridad"] || "Media").trim() || "Media";
              var venceT = (vals["vence el"] || "").trim() || "Sin fecha";
              if (/^\d{4}-\d{2}-\d{2}$/.test(venceT)) {
                var mesesT = ["ene", "feb", "mar", "abr", "may", "jun", "jul",
                              "ago", "sep", "oct", "nov", "dic"];
                var pT = venceT.split("-");
                venceT = parseInt(pT[2], 10) + " " +
                  mesesT[parseInt(pT[1], 10) - 1] + " " + pT[0];
              }
              var prioCls = prioT === "Alta" ? "b-amarillo"
                : prioT === "Baja" ? "b-linea" : "b-azul";
              var tbT = document.querySelector("#zona-tareas tbody");
              if (tbT) {
                var filaN = document.createElement("tr");
                filaN.innerHTML =
                  '<td data-label="Tarea"><b>' + esc(titT) + "</b></td>" +
                  '<td data-label="Emprendimiento">' + esc(empT) + "</td>" +
                  '<td data-label="Estudiante">' + esc(estT) + "</td>" +
                  '<td data-label="Prioridad"><span class="badge ' + prioCls + '">' +
                    esc(prioT) + "</span></td>" +
                  '<td data-label="Vence">' + esc(venceT) + "</td>" +
                  '<td data-label="Estado"><span class="badge b-neutra">Pendiente</span></td>' +
                  '<td class="acc" data-label="Acciones"><div class="acciones-cell">' +
                    '<button data-accion="editar-tarea" title="Editar" aria-label="Editar">' +
                      icono(ICO.lapiz, 16) + "</button>" +
                    '<button data-accion="eliminar-tarea" title="Eliminar" aria-label="Eliminar">' +
                      icono(ICO.x, 16) + "</button>" +
                  "</div></td>";
                tbT.insertBefore(filaN, tbT.firstElementChild);
              }
              toast("Tarea asignada", "ok");
            } }
        ]);
        break;

      case "ver-tareas":
        /* Emprendimientos -> baja suave al tablero de tareas de la vista. */
        e.preventDefault();
        var zonaT = document.getElementById("zona-tareas");
        if (zonaT) zonaT.scrollIntoView({ behavior: "smooth", block: "start" });
        break;

      default:
        var propio = (b.textContent || "").replace(/\s+/g, " ").trim();
        if (!propio) break;
        e.preventDefault();
        toast(propio, "info");
    }
  });

  function var_inscribir(b) {
    var fila = filaDe(b);
    var tP = $("#tabla-proximos");
    var tI = $("#tabla-inscritos");
    if (tP && tI && fila) {
      /* EV2: inscripcion real entre las dos tablas de la vista de eventos. */
      var inscribir = tP.contains(fila);
      moverEvento(fila, tP, tI, inscribir);
      toast(inscribir ? "Inscripción registrada. El evento aparece en tu panel." : "Inscripción cancelada",
            inscribir ? "ok" : "info");
      return;
    }
    var dentro = b.classList.toggle("hecho");
    b.setAttribute("aria-pressed", dentro ? "true" : "false");
    /* En el detalle de un evento virtual, inscribirse revela el enlace de
       acceso a la sala; al cancelar la inscripcion vuelve a ocultarse. */
    var acceso = $("#acceso-virtual");
    if (acceso) acceso.hidden = !dentro;
    toast(dentro ? "Inscripción registrada" : "Inscripción cancelada", dentro ? "ok" : "info");
  }

  /* EV2: mueve una fila de la tabla de proximos a la de inscritos (o viceversa).
     Cada fila movida guarda su HTML original (data-original) para poder
     restaurar la inscripcion al cancelarla. El estado persiste en localStorage
     con la lista de eventos inscritos (por nombre). */
  function moverEvento(fila, tProc, tInsc, inscribir) {
    var tbProc = $("tbody", tProc);
    var tbInsc = $("tbody", tInsc);
    if (!tbProc || !tbInsc) return;
    if (inscribir) {
      var celdas = $$("td", fila);
      if (celdas.length < 4) return;
      var tr = document.createElement("tr");
      tr.setAttribute("data-original", fila.outerHTML.replace(/"/g, "&quot;"));
      var colTxt = [
        celdas[0].innerHTML,
        celdas[2].innerHTML,
        celdas[3].innerHTML
      ];
      colTxt.forEach(function (html, idx) {
        var td = document.createElement("td");
        td.innerHTML = html;
        if (idx === 1) td.dataset.label = "Fecha y hora";
        if (idx === 2) td.dataset.label = "Modalidad";
        tr.appendChild(td);
      });
      var tdA = document.createElement("td");
      tdA.className = "acc";
      tdA.appendChild(badgeJS("Inscrito"));
      var btn = document.createElement("button");
      btn.className = "btn btn-sm btn-secundario";
      btn.dataset.accion = "inscribirse";
      btn.title = "Cancelar inscripción";
      btn.textContent = "Cancelar";
      tdA.appendChild(btn);
      tr.appendChild(tdA);
      tbInsc.appendChild(tr);
      fila.parentNode.removeChild(fila);
    } else {
      var original = fila.getAttribute("data-original");
      if (original) {
        var aux = document.createElement("tbody");
        aux.innerHTML = original.replace(/&quot;/g, '"');
        var restaurada = aux.firstElementChild;
        if (restaurada) tbProc.appendChild(restaurada);
      }
      fila.parentNode.removeChild(fila);
    }
    guardar({ eventosInscritos: nombresEventos() });
  }

  function nombresEventos() {
    var tI = $("#tabla-inscritos");
    var out = [];
    if (!tI) return out;
    $$("tbody tr", tI).forEach(function (tr) {
      var td = tr.children[0];
      if (td) out.push(td.textContent.replace(/\s+/g, " ").trim());
    });
    return out;
  }

  function badgeJS(txt) {
    var s = document.createElement("span");
    s.className = "badge b-linea";
    s.innerHTML = icono(ICO.check, 12);
    s.appendChild(document.createTextNode(" " + txt));
    return s;
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

  /* --- evidencia de tarea (TD1-TD3) -------------------------------------- */
  /* La zona de carga es un <label for="evidencia-real"> con un input file real
     (oculto). Al elegir/droppear archivos se pinta la lista de adjuntos con
     nombre, tamano y fecha, se actualiza el contador y se habilita el boton
     "Marcar como completada". El estado persiste en localStorage (prototipo). */
  var evInput = $("#evidencia-real");
  var evLista = $("#adjuntos-lista");
  var evArchivos = [];
  function fmtEv(n) {
    if (n >= 1048576) return (n / 1048576).toFixed(1) + " MB";
    return Math.max(1, Math.round(n / 1024)) + " KB";
  }
  function pintarAdjuntos() {
    if (!evLista) return;
    var contador = $("#contador-adjuntos");
    if (contador) contador.textContent = evArchivos.length === 1 ? "1 archivo" : evArchivos.length + " archivos";
    if (!evArchivos.length) {
      evLista.innerHTML = "<div class=\"vacio\">" + icono(ICO.doc, 40) +
        "<h3>Todavia no has adjuntado evidencia</h3>" +
        "<p>Cuando subas los archivos apareceran aqui con su fecha de carga.</p>" +
        '<button class="btn btn-secundario" data-accion="adjuntar-evidencias">' + icono(ICO.clip, 16) +
        " Adjuntar ahora</button></div>";
      var btnCompletarInicial = $("[data-accion='marcar-completada']");
      if (btnCompletarInicial) btnCompletarInicial.disabled = true;
      return;
    }
    var filas = evArchivos.map(function (f) {
      return '<div class="lista-def" style="padding:4px 0"><div class="def-row">' +
        icono(ICO.clip, 16) + "<dd style=\"color:#051533\"><b>" + esc(f.nombre) + "</b>" +
        '<br><span style="font-size:13px;color:#162644">' + esc(f.tam) + " · " + esc(f.dia) + "</span></dd>" +
        '<dt style="flex:0 0 auto"><button class="icon-btn" data-accion="quitar-adjunto" ' +
        'data-nombre="' + esc(f.nombre) + '" aria-label="Quitar ' + esc(f.nombre) + '">' +
        icono(ICO.x, 14) + "</button></dt></div></div>";
    }).join("");
    evLista.innerHTML = filas +
      '<div style="margin-top:12px;text-align:right"><button class="btn btn-secundario btn-sm" ' +
      'data-accion="adjuntar-evidencias">' + icono(ICO.clip, 15) + " Adjuntar m&aacute;s</button></div>";
    var btnCompletar = $("[data-accion='marcar-completada']");
    if (btnCompletar) btnCompletar.disabled = evArchivos.length === 0;
  }
  function anadirEvidencias(lista) {
    Array.prototype.forEach.call(lista || [], function (f) {
      if (evArchivos.length >= 5) { toast("Máximo 5 archivos por tarea", "error"); return; }
      evArchivos.push({ nombre: f.name, tam: fmtEv(f.size), dia: new Date().toLocaleDateString("es-CO") });
    });
    pintarAdjuntos();
    guardar({ adjuntos: evArchivos });
  }
  if (evInput && evInput.addEventListener) {
    evInput.addEventListener("change", function () {
      anadirEvidencias(evInput.files);
      evInput.value = "";
    });
    var zonaEv = evInput.closest(".drop") || evInput.parentNode;
    if (zonaEv) {
      ["dragover", "dragleave"].forEach(function (tipo) {
        zonaEv.addEventListener(tipo, function (e) {
          e.preventDefault();
          zonaEv.classList.toggle("sobre", tipo === "dragover");
        });
      });
      zonaEv.addEventListener("drop", function (e) {
        e.preventDefault();
        zonaEv.classList.remove("sobre");
        anadirEvidencias(e.dataTransfer.files);
      });
    }
  }

  /* --- cuestionario por secciones (DG1/DG3/DG4) -------------------------- */
  /* El diagnostico son 5 paneles data-panel-nombre="seccion-N". Los botones
     Siguiente/Anterior navegan entre paneles y el contador cuenta las
     preguntas reales respondidas (22 campos), no un texto fijo. */
  var panelesDiag = $$("[data-panel-nombre^='seccion-']");
  function diagPanelActual() {
    for (var i = 0; i < panelesDiag.length; i++) {
      if (!panelesDiag[i].hidden) return i;
    }
    return 0;
  }
  function diagContar() {
    var respondidas = 0, total = 0;
    panelesDiag.forEach(function (p) {
      $$(".campo input, .campo select, .campo textarea", p).forEach(function (c) {
        total++;
        if (c.value && c.value.trim()) respondidas++;
      });
    });
    var r = respondidas + " de " + total + " preguntas respondidas";
    $$("[data-contador-diagnostico]").forEach(function (x) { x.textContent = "Progreso: " + r; });
    return r;
  }
  function diagMostrar(i) {
    panelesDiag.forEach(function (p, j) {
      p.hidden = j !== i;
    });
    var pasos = $$(".steps .step");
    pasos.forEach(function (st, j) {
      st.className = "step" + (j < i ? " hecho" : j === i ? " activo" : "");
      var num = $("i", st);
      if (num) num.textContent = j + 1;
      if (j < i) st.querySelector("i").innerHTML = icono(ICO.check, 14);
    });
    diagContar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /* --- bandeja de notificaciones (NO2/NO3) ------------------------------- */
  /* Los chip[data-chip] filtran la bandeja por tipo/estado y un clic sobre
     una notificacion pendiente la marca como leida. Ambos estados persisten
     en localStorage (prototipo). */
  var notifs = $$(".notif");
  function notifRefrescar() {
    var n = 0;
    notifs.forEach(function (x) { if (x.classList.contains("no-leida")) n++; });
    var c = $("#contador-no-leidas");
    if (c) c.textContent = n + (n === 1 ? " sin leer" : " sin leer");
    return n;
  }
  function notifPersistir() {
    var leidas = [];
    notifs.forEach(function (x) {
      if (!x.classList.contains("no-leida")) leidas.push(x.dataset.i);
    });
    guardar({ notifsLeidas: leidas });
  }
  function notifFiltro(f) {
    notifs.forEach(function (x) {
      var ok = f === "todas" ||
        (f === "sin-leer" && x.classList.contains("no-leida")) ||
        x.dataset.tipo === f;
      x.hidden = !ok;
    });
    vacioRefrescar();
  }
  if (notifs.length) {
    $$(".chip[data-chip]").forEach(function (ch) {
      ch.addEventListener("click", function () {
        $$(".chip[data-chip]").forEach(function (o) { o.classList.toggle("on", o === ch); });
        notifFiltro(ch.dataset.chip);
        notifRefrescar();
      });
    });
    notifs.forEach(function (x) {
      x.addEventListener("click", function () {
        if (x.classList.contains("no-leida")) {
          x.classList.remove("no-leida");
          var dot = $(".notif-dot", x);
          if (dot) dot.remove();
          notifRefrescar();
          notifPersistir();
        }
      });
    });
    notifRefrescar();
  }

  /* --- validacion de formularios ----------------------------------------- */
  /* Los envoltorios .vista-form (un <form> por vista admin) quedan fuera:
     su proposito es semantico y las acciones reales viajan por data-accion,
     asi que validarlos aqui mostraria "Guardado correctamente" en cada clic. */
  $$("form:not(.vista-form)").forEach(function (f) {
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

  /* --- arrastrar y soltar (kanban) --------------------------------------- */
  /* Solo en Admin y Estudiante: la vista de Docente conserva su tablero
     inerte a propósito (no se toca ese rol). */
  if (location.pathname.indexOf("/docente/") === -1) {
  $$(".kanban, [data-kanban]").forEach(function (tablero) {
    var arrastre = null;
    $$(".kan-col", tablero).forEach(function (col) {
      col.addEventListener("dragover", function (e) { e.preventDefault(); col.classList.add("sobre"); });
      col.addEventListener("dragleave", function () { col.classList.remove("sobre"); });
      col.addEventListener("drop", function (e) {
        e.preventDefault();
        col.classList.remove("sobre");
        if (!arrastre) return;
        col.appendChild(arrastre);
        var estado = { tablero: tablero.dataset.kanban || "kanban", tareas: [] };
        $$(".kan-col", tablero).forEach(function (c) {
          $$(".kan-card", c).forEach(function (k) { estado.tareas.push(k.textContent.replace(/\s+/g, " ").trim().slice(0, 40)); });
        });
guardar(estado);
        toast("Tarea movida a " + nombreCol(col), "ok");
      });
    });
    $$(".kan-card", tablero).forEach(function (k) {
      k.setAttribute("draggable", "true");
      k.addEventListener("dragstart", function () { arrastre = k; k.classList.add("arrastrando"); });
      k.addEventListener("dragend", function () { k.classList.remove("arrastrando"); arrastre = null; });
    });
  });
  }
  function nombreCol(col) {
    var h = $(".kan-titulo, h3, .hint", col);
    return (h && h.textContent.replace(/\s+/g, " ").trim()) || "la columna";
  }

  /* --- paginacion -------------------------------------------------------- */
  /* EM5: el control ya trae `data-paginacion` (ver lib_ui.paginas). Aquí se
     mueve de página, se actualiza "Mostrando X a Y de Z" y se recuerda la
     página. En el prototipo los datos vienen recortados, pero el control deja
     de ser un toast: navega, respeta los bordes y persiste el estado. */
  $$("[data-paginacion]").forEach(function (p) {
    var total = parseInt(p.dataset.pagRegs, 10) || 0;
    var tam = parseInt(p.dataset.pagTam, 10) || 1;
    var nPag = parseInt(p.dataset.pagTotal, 10) || 1;
    var actual = parseInt(p.dataset.pagActual, 10) || 1;
    var previoPag = store(true);
    if (previoPag && previoPag.pagina && previoPag.pagina.n) {
      actual = Math.min(Math.max(1, previoPag.pagina.n), nPag);
    }
    function pintarPag() {
      $$("button[data-pagina]", p).forEach(function (o) {
        var v = o.dataset.pagina;
        if (v === "prev") o.disabled = actual <= 1;
        else if (v === "next") o.disabled = actual >= nPag;
        else {
          var num = parseInt(v, 10) || 1;
          o.classList.toggle("btn-acento", num === actual);
          o.classList.toggle("btn-secundario", num !== actual);
          if (num === actual) o.setAttribute("aria-current", "page");
          else o.removeAttribute("aria-current");
        }
      });
      var desde = (actual - 1) * tam + 1;
      var hasta = Math.min(actual * tam, total);
      var t = $("[data-pag-texto]", p);
      if (t) t.textContent = "Mostrando " + desde + " a " + hasta + " de " + total;
      p.dataset.pagActual = actual;
    }
    $$("button[data-pagina]", p).forEach(function (b) {
      b.addEventListener("click", function (ev) {
        ev.stopPropagation();
        var v = b.dataset.pagina;
        if (v === "prev") actual = Math.max(1, actual - 1);
        else if (v === "next") actual = Math.min(nPag, actual + 1);
        else actual = parseInt(v, 10) || 1;
        pintarPag();
        guardar({ pagina: { n: actual } });
      });
    });
    pintarPag();
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
  function cerrarSesion() {
    /* Logout unico del prototipo (BT4): borra la clave de la pagina, la sesion
       de "sgemd:sesion" (la escribe login.html en compartido/) y redirige. */
    store(null, true, null);
    try {
      localStorage.removeItem("sgemd:sesion");
      sessionStorage.removeItem("sgemd:sesion");
    } catch (x) {}
    location.href = rutaLogin();
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
        /* Estudiante y docente tienen una vista de configuración propia; en
           administrador el menú conserva "Preferencias" (sin vista). */
        var carpeta = location.pathname.split("/").slice(-2, -1)[0];
        var conConfiguracion = carpeta === "estudiante" || carpeta === "docente";
        m.innerHTML = '<button data-accion="perfil">Mi perfil</button>' +
          (conConfiguracion
            ? '<button data-accion="configuracion">Configuración</button>'
            : '<button data-accion="preferencias">Preferencias</button>') +
          '<button data-accion="cerrar-sesion">Cerrar sesión</button>';
        w.parentNode.appendChild(m);
        $$("button", m).forEach(function (b) {
          b.addEventListener("click", function (e) {
            e.stopPropagation();
            abierto = false;
            m.remove();
            if (b.dataset.accion === "perfil") {
              /* El perfil se abre desde el mini menu de la esquina superior
                 derecha; navega a la misma vista que tenia el menu lateral. */
              location.href = "perfil.html";
              return;
            }
            if (b.dataset.accion === "configuracion") {
              location.href = "configuracion.html";
              return;
            }
            if (b.dataset.accion === "cerrar-sesion") {
              confirmar("Cerrar sesión", "¿Seguro que quieres cerrar tu sesión?", cerrarSesion);
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

  /* --- estado inicial ----------------------------------------------------- */
  var previo = store(true);
  if (previo && previo.tab != null) {
    var barra = $(".tabs");
    if (barra) {
      var b = $$("button", barra)[previo.tab];
      if (b) b.click();
    }
  }
  /* DG4: retomar el cuestionario en el punto guardado (seccion + respuestas). */
  if (previo && previo.borrador && typeof previo.borrador === "object" && panelesDiag.length) {
    var porLabel = {};
    Object.keys(previo.borrador).forEach(function (k) {
      porLabel[k.toLowerCase().replace(/\s+/g, " ").trim()] = previo.borrador[k];
    });
    panelesDiag.forEach(function (p) {
      $$(".campo", p).forEach(function (campoBox) {
        var lbl = $("label", campoBox);
        if (!lbl) return;
        var c = $("input, select, textarea", campoBox);
        if (!c) return;
        var k = lbl.textContent.replace(/\s+/g, " ").trim().toLowerCase();
        if (porLabel[k] != null && !(c.value && c.value.trim())) c.value = porLabel[k];
      });
    });
    if (previo.seccionDiag != null) diagMostrar(previo.seccionDiag);
    else diagContar();
  }
  /* PE1/EE1: restaurar los datos guardados del perfil y de la edición. */
  if (previo && previo.perfil) restaurarCampos(document, previo.perfil);
  if (previo && previo.emprendimiento) restaurarCampos(document, previo.emprendimiento);
  if (previo && Array.isArray(previo.adjuntos) && evLista) {
    evArchivos = previo.adjuntos;
    pintarAdjuntos();
  }
  /* EV2: restaurar las inscripciones a eventos guardadas en localStorage. */
  if (previo && Array.isArray(previo.eventosInscritos) && previo.eventosInscritos.length) {
    var tP = $("#tabla-proximos"), tI = $("#tabla-inscritos");
    if (tP && tI) {
      $$("tbody tr", tP).forEach(function (f) {
        var td0 = f.children[0];
        var nombre = td0 ? td0.textContent.replace(/\s+/g, " ").trim() : "";
        if (previo.eventosInscritos.indexOf(nombre) >= 0) moverEvento(f, tP, tI, true);
      });
    }
  }
  /* NO3: restaurar notificaciones leidas. */
  if (previo && Array.isArray(previo.notifsLeidas) && notifs.length) {
    var setL = {};
    previo.notifsLeidas.forEach(function (i) { setL[i] = true; });
    notifs.forEach(function (n) {
      if (setL[n.dataset.i] && n.classList.contains("no-leida")) {
        n.classList.remove("no-leida");
        var dot = $(".notif-dot", n);
        if (dot) dot.remove();
      }
    });
    notifRefrescar();
  }
  if (previo && previo.completada && $("[data-accion='marcar-completada']")) {
    var bComp = $("[data-accion='marcar-completada']");
    bComp.disabled = true;
    bComp.innerHTML = "Completada " + icono(ICO.check, 15);
  }
  /* Calendario de Inicio: el dia con evento abre un modal en la misma
     pagina (sin redireccionar). El detalle viaja en data-ev-*. */
  $$(".cal-dia-btn").forEach(function (celda) {
    celda.addEventListener("click", function () {
      var titulo = celda.getAttribute("data-ev-titulo");
      var detalle = celda.getAttribute("data-ev-detalle") || "";
      abrirModal(titulo,
        "<p><b>" + esc(titulo) + "</b></p><p>" + esc(detalle) + "</p>",
        [
          { txt: "Ver en Eventos", clase: "btn btn-primario",
            alClic: function () { location.href = "eventos.html"; } },
          { txt: "Cerrar", clase: "btn btn-secundario" }
        ]);
    });
  });
  /* Estado inicial de los estados vacios de listas y tablas. */
  vacioRefrescar();
  document.documentElement.classList.add("js-listo");
})();
"""