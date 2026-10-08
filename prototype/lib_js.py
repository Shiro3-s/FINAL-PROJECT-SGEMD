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
    var selects = $$("select", zona).filter(function (s) { return s.dataset.filtro !== "off"; });
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
  }
  $$("[data-filtro], .chip").forEach(function (c) {
    c.addEventListener("click", function () {
      c.classList.toggle("activo");
      aplicarFiltros();
    });
  });
  $$("select[data-filtro]").forEach(function (s) { s.addEventListener("change", aplicarFiltros); });

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

  document.addEventListener("click", function (e) {
    var b = e.target.closest("button, a.btn");
    if (!b) return;
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
      case "detalle":
        e.preventDefault();
        abrirModal("Detalle del registro",
          '<p class="confirm-texto">' + esc(registro) + "</p>" +
          '<p class="modal-aviso">Vista de prototipo. En producción aquí se cargaría el expediente completo.</p>');
        break;

      case "ver-acta":
        e.preventDefault();
        abrirModal("Acta de la asesoría",
          '<p class="confirm-texto">' + esc(registro) + "</p>" +
          '<p class="modal-aviso">Vista de prototipo. En producción aquí se cargaría el acta firmada con acuerdos y compromisos.</p>');
        break;

      case "editar":
      case "editar-docente":
      case "editar-estudiante":
      case "registrar-avance":
      case "asignar":
      case "editar-sensores":
        e.preventDefault();
        abrirEditor("Editar registro", registro);
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
      case "descargar-pdf":
      case "exportar":
      case "exportar-reporte":
        e.preventDefault();
        toast("Preparando " + (b.textContent.trim() || "la descarga") + "…", "info");
        break;

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
        /* DG4: persiste el envio del cuestionario completo. */
        e.preventDefault();
        guardar({ enviado: true, fecha: new Date().toISOString().slice(0, 10) });
        toast("Diagnóstico enviado al docente", "ok");
        b.textContent = "Diagnóstico enviado ✓";
        b.disabled = true;
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
        b.textContent = "Solicitud enviada ✓";
        b.disabled = true;
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
        b.textContent = "Completada ✓";
        toast("Tarea enviada a revisión", "ok");
        break;

      case "notificaciones":
        e.preventDefault();
        abrirDrawer("Notificaciones", [
          "Nueva revisión de tu Startup Week II",
          "Tu docente registró un avance",
          "Se publicó un evento nuevo",
          "Recordatorio: evidencia de tarea pendiente"
        ]);
        break;

      case "cerrar-sesion":
        e.preventDefault();
        cerrarSesion();
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
        if (typeof notifRefrescar === "function") notifRefrescar();
        if (typeof notifPersistir === "function") notifPersistir();
        toast(porLeer ? "Todas las notificaciones marcadas como leídas" : "No hay notificaciones sin leer", porLeer ? "ok" : "info");
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
      var inscribir = fila.closest(tP) != null;
      moverEvento(fila, tP, tI, inscribir);
      toast(inscribir ? "Inscripción registrada. El evento aparece en tu panel." : "Inscripción cancelada",
            inscribir ? "ok" : "info");
      return;
    }
    var dentro = b.classList.toggle("hecho");
    b.setAttribute("aria-pressed", dentro ? "true" : "false");
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
    s.appendChild(icono(ICO.check, 12));
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
        '<br><span style="font-size:12px;color:#5a6b8c">' + esc(f.tam) + " · " + esc(f.dia) + "</span></dd>" +
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
        m.innerHTML = '<button data-accion="perfil">Mi perfil</button>' +
          '<button data-accion="preferencias">Preferencias</button>' +
          '<button data-accion="cerrar-sesion">Cerrar sesión</button>';
        w.parentNode.appendChild(m);
        $$("button", m).forEach(function (b) {
          b.addEventListener("click", function () {
            abierto = false;
            m.remove();
            if (b.dataset.accion === "cerrar-sesion") {
              cerrarSesion();
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
    bComp.textContent = "Completada ✓";
  }
  document.documentElement.classList.add("js-listo");
})();
"""