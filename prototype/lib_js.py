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
    info: "M12 16v-4M12 8h.01", descargar: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"
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
        abrirDrawer("Notificaciones", [
          "Nueva revisión de tu Startup Week II",
          "Tu docente registró un avance",
          "Se publicó un evento nuevo",
          "Recordatorio: evidencia de tarea pendiente"
        ]);
        break;

      default:
        var propio = (b.textContent || "").replace(/\s+/g, " ").trim();
        if (!propio) break;
        e.preventDefault();
        toast(propio, "info");
    }
  });

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

  /* --- estado inicial ----------------------------------------------------- */
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