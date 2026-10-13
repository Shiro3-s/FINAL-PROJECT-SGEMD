# -*- coding: utf-8 -*-
"""Rol ESTUDIANTE — 16 pantallas."""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, tabs, tabs_paneles, ico, boton_accion, ico, linea_tiempo, kanban,
)
from lib_charts import (
    barras, barras_h, lineas, donut, circular, progreso_fases, stacked_tareas,
    velocidad, AZUL, PROF, GRIS, AMAR,
)

R = "estudiante"


def _acc(*items):
    """Botones de accion de tabla."""
    return "".join(items)


def _b(icono, etiqueta):
    return boton_accion(icono, etiqueta)


def _a(icono, etiqueta, href):
    """Accion de tabla como enlace real (para navegar, no modal)."""
    return ('<a class="table-act" href="%s" title="%s" aria-label="%s">%s</a>'
            % (href, etiqueta, etiqueta, ico(icono, 16)))


def registrar(reg):
    p = [
        ("dashboard.html", "05 Estudiante - Inicio (dashboard)", dashboard),
        ("estado-seguimiento.html", "06 Estudiante - Estado de seguimiento", estado_seguimiento),
        ("emprendimientos.html", "07 Estudiante - Mi emprendimiento (lista)", emprendimientos),
        ("emprendimiento-detalle.html", "08 Estudiante - Detalle del emprendimiento",
         emprendimiento_detalle),
        ("emprendimiento-editar.html", "09 Estudiante - Editar emprendimiento", emprendimiento_editar),
        ("diagnostico.html", "10 Estudiante - Diagnóstico (cuestionario)", diagnostico),
        ("diagnostico-resultados.html", "11 Estudiante - Resultados del diagnóstico", diagnostico_resultados),
        ("plan-trabajo.html", "12 Estudiante - Plan de trabajo", plan_trabajo),
        ("seguimiento.html", "13 Estudiante - Seguimiento (historial)", seguimiento),
        ("tareas.html", "14 Estudiante - Mis tareas", tareas),
        ("tarea-detalle.html", "15 Estudiante - Detalle de tarea (pendiente)", tarea_detalle),
        ("tarea-detalle-en-revision.html", "15b Estudiante - Detalle tarea en revisión",
         tarea_detalle_en_revision),
        ("tarea-detalle-completada-precio.html", "15c Estudiante - Detalle tarea completada (precio)",
         tarea_detalle_completada_precio),
        ("tarea-detalle-completada-usuarios.html", "15d Estudiante - Detalle tarea completada (usuarios)",
         tarea_detalle_completada_usuarios),
        ("tarea-detalle-completada-clientes.html", "15e Estudiante - Detalle tarea completada (clientes)",
         tarea_detalle_completada_clientes),
        ("asesorias.html", "16 Estudiante - Mis asesorías", asesorias),
        ("solicitar-asesoria.html", "17 Estudiante - Solicitar asesoría", solicitar_asesoria),
        ("eventos.html", "18 Estudiante - Eventos", eventos),
        ("perfil.html", "19 Estudiante - Mi perfil", perfil),
        ("notificaciones.html", "20 Estudiante - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(p):
        reg("estudiante", arch, tit, fn, i)


# --- 1. Dashboard ------------------------------------------------------------
def dashboard():
    cuerpo = (
        callout(
            "Tu cuenta está <b>Limitada</b>. Ya puedes entrar al sistema, pero el módulo de "
            "<b>Diagnóstico</b> permanece bloqueado hasta que un administrador active tu cuenta.",
            "escudo",
        )
        + '<div class="sep sep-20"></div>'
        + metricas([
            ("maleta", "Mi emprendimiento", "1", "activo", 100, "1 registrado"),
            ("target", "Diagnóstico", "Pendiente", "", 0, ""),
            ("checklist", "Tareas completadas", "3", "de 7", 43, ""),
            ("chat", "Asesorías realizadas", "3", "", 100, ""),
        ])
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2-1">'
        + card(
            "Progreso de mi emprendimiento",
            '<div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap">'
            + circular(62, "avance", "FASE 2 · Ejecución")
            + '<div style="flex:1;min-width:280px">'
            + progreso_fases([
                ("FASE 1 · Ideación", 100, AZUL),
                ("FASE 2 · Ejecución", 62, AZUL),
                ("FASE 3 · Consolidación", 0, GRIS),
                ("FASE 4 · Escalamiento", 0, GRIS),
            ])
            + "</div></div>",
            accion='<a class="btn btn-secundario btn-sm" href="plan-trabajo.html">Ver plan de trabajo</a>',
        )
        + card(
            "Próximas asesorías",
            '<div class="lista-def" style="padding:4px 0">'
            '<div class="def-row"><dt>Martes 12 nov, 10:00</dt><dd>Modalidad virtual &middot; Confirmada</dd></div>'
            '<div class="def-row"><dt>Jueves 14 nov, 14:30</dt><dd>Presencial &middot; Pendiente de confirmar</dd></div>'
            '<div class="def-row"><dt>Lunes 19 nov, 09:00</dt><dd>Virtual &middot; Confirmada</dd></div>'
            "</div>",
            accion='<a class="btn btn-secundario btn-sm" href="asesorias.html">Ver todas</a>',
        )
        + "</div>"
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2">'
        + card(
            "Tareas pendientes",
            '<div class="lista-def" style="padding:4px 0">'
            + "".join(
                '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">%s</dd>'
                '<dd style="flex:0 0 auto">%s</dd></div>'
                % (t, d, badge(p, "b-amarillo" if p == "Alta" else "b-linea", "alerta" if p == "Alta" else "reloj"))
                for t, d, p in [
                    ("Hoy", "Subir evidencia fotográfica del punto de venta", "Alta"),
                    ("13 nov", "Actualizar el inventario de insumos", "Media"),
                    ("15 nov", "Registrar las ventas de la semana en el formato", "Media"),
                ]
            )
            + "</div>",
            accion='<a class="btn btn-secundario btn-sm" href="tareas.html">Ver todas</a>',
        )
        + card(
            "Avisos de la institución",
            '<div class="lista-def" style="padding:4px 0">'
            '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">'
            "Sesión de capacitación en modelado de negocios: jueves 21 nov, 8:00 a.m.</dd></div>"
            '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">'
            "Convocatoria del evento Startup Minuto de Dios. Postulación hasta el 25 nov.</dd></div>"
            "</div>" % (ico("calendar", 15), ico("rayo", 15)),
        )
        + "</div>"
    )
    return shell(R, "dashboard", "Inicio", cuerpo,
                 sub="Resumen de tu emprendimiento, tareas y asesorías de esta semana.")


# --- 2. Estado de seguimiento ------------------------------------------------
def _estado_emp(d):
    """Paneles internos de 'Estado de seguimiento' por emprendimiento."""
    return (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card(
            "Movimiento en el plan",
            '<div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap">'
            + circular(d["pct"], "avance", d["fase"])
            + '<div style="flex:1;min-width:300px">'
            + '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px">'
            + "".join(
                '<div style="border:1px solid #bbbbbb;border-radius:8px;padding:12px 14px">'
                '<div class="suave">%s</div>'
                '<div style="font-size:20px;font-weight:700;color:#051533">%s</div>'
                '<div class="suave">%s</div></div>'
                % (lbl, val, det)
                for lbl, val, det in d["kpis"]
            )
            + "</div></div></div>",
        )
        + card(
            "Avance por fases",
            progreso_fases(d["fases"]),
            hint="Las fases se habilitan en orden según el avance del docente asignado",
        )
        + "</div>"
        + '<div class="grid">'
        + card(
            "Hitos cumplidos",
            '<div class="lista-def" style="padding:4px 0">'
            + "".join(
                '<div class="def-row"><dt style="flex:0 0 auto">%s</dt>'
                '<dd style="flex:1">%s</dd></div>' % (ico("check", 15), t)
                for t in d["hitos"]
            )
            + "</div>",
        )
        + card(
            "Requisito bloqueante",
            d["bloqueo"]
            + '<div style="margin-top:14px">%s</div>' % d["badge"],
            accion=d["accion"],
        )
        + "</div></div>"
    )


def estado_seguimiento():
    paneles = [
        (
            "Sabor y Sabe",
            "emp-sabor",
            dict(
                pct=62,
                fase="FASE 2 · Ejecución",
                kpis=[
                    ("Fase actual", "FASE 2", "Ejecución y validación"),
                    ("Tareas completadas", "3 / 7", "43% del total asignado"),
                    ("Asesorías recibidas", "3", "última: 04 nov 2024"),
                    ("Seguimientos registrados", "5", "último: 08 nov 2024"),
                ],
                fases=[
                    ("FASE 1 · Ideación y priorización de ideas", 100, AZUL),
                    ("FASE 2 · Estructuración y ejecución", 62, AZUL),
                    ("FASE 3 · Consolidación del proceso", 0, GRIS),
                    ("FASE 4 · Escalamiento", 0, GRIS),
                ],
                hitos=[
                    "Diagnóstico inicial entregado",
                    "Plan de trabajo cargado por el docente",
                    "Primeras ventas registradas",
                    "Perfil de cliente definido",
                ],
                bloqueo=(
                    '<div class="suave">Tu cuenta está en estado '
                    "<b style=\"color:#051533\">Limitado</b>. Mientras no sea activada por un "
                    "administrador, el diagnóstico inicial no puede enviarse.</div>"
                ),
                badge=badge("Cuenta limitada", "b-amarillo", "lock"),
                accion='<a class="btn btn-secundario btn-sm" href="perfil.html">Ver mi perfil</a>',
            ),
        ),
        (
            "Mochilas Origen",
            "emp-mochilas",
            dict(
                pct=24,
                fase="FASE 1 · Ideación",
                kpis=[
                    ("Fase actual", "FASE 1", "Ideación y priorización de ideas"),
                    ("Tareas completadas", "1 / 3", "33% del plan inicial"),
                    ("Asesorías recibidas", "0", "sin docente asignado"),
                    ("Seguimientos registrados", "2", "último: 20 oct 2024"),
                ],
                fases=[
                    ("FASE 1 · Ideación y priorización de ideas", 24, AZUL),
                    ("FASE 2 · Estructuración y ejecución", 0, GRIS),
                    ("FASE 3 · Consolidación del proceso", 0, GRIS),
                    ("FASE 4 · Escalamiento", 0, GRIS),
                ],
                hitos=[
                    "Diagnóstico inicial entregado",
                    "Idea de negocio priorizada",
                ],
                bloqueo=(
                    '<div class="suave">Este emprendimiento aún no tiene '
                    "<b style=\"color:#051533\">docente asignado</b>. El plan de trabajo se "
                    "construye cuando el programa te asigne un docente.</div>"
                ),
                badge=badge("Sin docente asignado", "b-amarillo", "lock"),
                accion='<a class="btn btn-secundario btn-sm" href="emprendimientos.html">Ver emprendimientos</a>',
            ),
        ),
    ]
    cuerpo = (
        tabs_paneles([(n, pid) for n, pid, _ in paneles])
        + '<div class="sep sep-20"></div>'
        + "".join(
            '<div data-panel-nombre="%s"%s>%s</div>' % (pid, "" if i == 0 else " hidden", _estado_emp(d))
            for i, (_, pid, d) in enumerate(paneles)
        )
    )
    return shell(R, "estado-seguimiento", "Estado de seguimiento", cuerpo,
                 migas=["Inicio", "Estado de seguimiento"],
                 sub="Aquí ves cuánto has avanzado y qué te falta por completar, por cada emprendimiento.",
                 acciones='<a class="btn btn-secundario" href="plan-trabajo.html">Plan de trabajo</a>'
                          '<a class="btn btn-acento" href="tareas.html">Ver mis tareas</a>')


# --- 3. Emprendimientos (lista) ---------------------------------------------
def emprendimientos():
    filas = [[
        '<b>Sabor y Sabe</b>', "Alimentos y bebidas", "Alimentos",
        badge("FASE 2 · Ejecución", "b-azul", "engranaje"),
        "12 oct 2024", "Carlos Mendoza",
        _acc(_a("eye", "Ver detalle", "emprendimiento-detalle.html"),
             _a("edit", "Editar", "emprendimiento-editar.html"),
             _b("download", "Descargar expediente")),
    ], [
        '<b>Mochilas Origen</b>', "Moda y accesorios", "Textil",
        badge("FASE 1 · Ideación", "b-amarillo", "bombilla"),
        "03 sep 2024", "Sin asignar",
        _acc(_a("eye", "Ver detalle", "emprendimiento-detalle.html"),
             _b("download", "Descargar expediente")),
    ]]
    cuerpo = (
        toolbar(
            filtros='<select class="filtro" data-filtro="etapa" data-filtro-col="3" '
                    'aria-label="Filtrar por etapa"><option value="">Todas las etapas</option>'
                    "<option>FASE 1 · Ideación</option><option>FASE 2 · Ejecución</option>"
                    "<option>FASE 3 · Consolidación</option><option>FASE 4 · Escalamiento</option></select>"
                   '<select class="filtro" data-filtro="sector" data-filtro-col="2" '
                   'aria-label="Filtrar por sector"><option value="">Todos los sectores</option><option>Alimentos</option>'
                   "<option>Textil</option><option>Servicios</option><option>Tecnología</option></select>",
        )
        + tabla(
            ["Emprendimiento", "Tipo de emprendimiento", "Sector productivo",
             "Etapa actual", "Fecha de creación", "Docente asignado", "@ACC"],
            [[f[0], f[1], f[2], f[3], f[4], f[5], f[6]] for f in filas],
        )
        + paginas(1, 2, 2)
        + '<div class="sep sep-20"></div>'
        + callout(
            "Solo puedes ver los emprendimientos que te pertenecen. Para consultar el de otro "
            "estudiante debes entrar como <b>DOCENTE</b> o <b>ADMINISTRADOR</b>.",
            "escudo",
        )
    )
    return shell(R, "emprendimientos", "Mi emprendimiento", cuerpo,
                 migas=["Inicio", "Mi emprendimiento"],
                 sub="Listado de tus emprendimientos y su estado actual.",
                 acciones='<button class="btn btn-secundario" data-accion="exportar">%s Exportar</button>' % ico("download", 16)
                          + '<a class="btn btn-acento" href="emprendimiento-editar.html">%s Crear emprendimiento</a>' % ico("plus", 16))


# --- 4. Detalle del emprendimiento ------------------------------------------
def emprendimiento_detalle():
    # --- Panel: Resumen -----------------------------------------------------
    panel_resumen = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Datos básicos", lista_def([
            ("Nombre", "Sabor y Sabe"),
            ("Tipo de emprendimiento", "Alimentos y bebidas"),
            ("Sector productivo", "Alimentos"),
            ("Etapa actual", badge("FASE 2 · Ejecución", "b-azul", "engranaje")),
            ("Fecha de creación", "12 de octubre de 2024"),
            ("Estado de la cuenta", badge("Limitado", "b-amarillo", "lock")),
        ]))
        + card(
            "Descripción",
            '<p class="suave">Sabor y Sabe es un emprendimiento de '
            "alimentos y bebidas que prepara y comercializa snacks artesanales a base de "
            "frutos secos y granola, con ventas en el campus y por pedido a domicilio dentro "
            "del municipio.</p>",
        )
        + card("Redes sociales", lista_def([
            ("Instagram", "@saborysabe.md"),
            ("WhatsApp Business", "300 555 4412"),
            ("Tienda propia", "aún no registrada"),
        ]))
        + "</div>"
        + '<div class="grid">'
        + card("Docente asignado", '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
             '<span class="avatar" style="width:44px;height:44px;flex:0 0 44px;font-size:14px">CM</span>'
             '<div><div style="font-weight:600">Carlos Mendoza</div>'
             '<div class="suave">Docente &middot; Áreas de flipped classroom y e-learning</div>'
             "</div></div>"
             '<a class="btn btn-secundario btn-sm" href="solicitar-asesoria.html" style="width:100%">'
             + ico("chat", 15) + " Solicitar asesoría</a>")
        + card("Acciones disponibles",
               '<div class="fila-col">'
               '<a class="btn btn-primario" href="emprendimiento-editar.html" style="width:100%">'
               + ico("edit", 16) + " Editar datos básicos</a>"
               '<a class="btn btn-secundario" href="plan-trabajo.html" style="width:100%">'
               + ico("layers", 16) + " Ver plan de trabajo</a>"
               '<button class="btn btn-secundario" data-accion="descargar" style="width:100%">'
               + ico("download", 16) + " Descargar expediente</button>"
               "</div>"
               '<div class="nota-foot">Solo puedes editar nombre, descripción y redes sociales. '
               "El tipo, el sector, la etapa y el acta los administra el rol ADMINISTRADOR.</div>")
        + "</div></div>"
    )

    # --- Panel: Diagnostico -------------------------------------------------
    panel_diagnostico = (
        callout("El diagnóstico inicial lo respondes una sola vez. Con tus respuestas el "
                "docente construye tu plan de trabajo.", "doc")
        + '<div class="sep sep-16"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Estado del diagnóstico", lista_def([
            ("Estado", badge("En progreso", "b-amarillo", "reloj")),
            ("Secciones completadas", "3 de 5"),
            ("Última actualización", "12 de octubre de 2024"),
            ("Responsable", "Tu (estudiante)"),
        ])
            + '<div class="fila-acciones mt-14">'
            '<a class="btn btn-acento" href="diagnostico.html">' + ico("edit", 16) + " Responder diagnóstico</a>"
            '<a class="btn btn-secundario" href="diagnostico-resultados.html">' + ico("doc", 16) + " Ver resultados</a>"
            "</div>")
        + card("Las 5 secciones", lista_def([
            ("1. Perfil del emprendimiento", badge("Completada", "b-azul", "check")),
            ("2. Problema o necesidad", badge("Completada", "b-azul", "check")),
            ("3. Propuesta de valor", badge("Completada", "b-azul", "check")),
            ("4. Mercado objetivo", badge("Pendiente", "b-neutra", "reloj")),
            ("5. Capacidad operativa y financiera", badge("Pendiente", "b-neutra", "reloj")),
        ]))
        + "</div>"
        + '<div class="grid">'
        + card("Para qué sirve", '<p class="suave">Tus respuestas se '
               "convierten en la caracterización y la valoración del emprendimiento. Con eso "
               "el docente arma el plan de trabajo y las tareas que verás en las otras "
               "pestañas.</p>")
        + "</div></div>"
    )

    # --- Panel: Plan de trabajo ---------------------------------------------
    panel_plan = (
        callout("El plan de trabajo lo construye el docente que tienes asignado y tu solo "
                "puedes consultar su avance y completar las tareas.", "escudo")
        + '<div class="sep sep-16"></div>'
        + card("Avance por fase", lista_def([
            ("FASE 1 · Ideación", badge("Completada", "b-azul", "check")),
            ("FASE 2 · Ejecución", badge("En curso", "b-amarillo", "engranaje")),
            ("FASE 3 · Crecimiento", badge("Pendiente", "b-neutra", "reloj")),
            ("FASE 4 · Consolidación", badge("No iniciada", "b-neutra", "reloj")),
        ])
            + '<div class="fila-acciones mt-14">'
            '<a class="btn btn-acento" href="plan-trabajo.html">' + ico("layers", 16) + " Abrir plan de trabajo</a>"
            "</div>")
        + card("Tareas del plan",
               '<p class="suave">Tienes <b>3 tareas activas</b>: '
               "2 pendientes y 1 en revisión. Mira la pestaña <b>Tareas</b> para el detalle "
               "o el <b>plan de trabajo</b> para el avance por fase.</p>")
    )

    # --- Panel: Seguimiento -------------------------------------------------
    filas_seg = []
    for f, est in [
        ("22 oct 2024", "Avance de fase"),
        ("05 nov 2024", "Avance de fase"),
        ("12 nov 2024", "Comentario"),
    ]:
        filas_seg.append([
            f,
            badge(est, "b-azul" if est == "Avance de fase" else "b-neutra",
                  "trend" if est == "Avance de fase" else "chat"),
            "Carlos Mendoza",
        ])
    panel_seguimiento = (
        callout("El seguimiento es de <b>solo lectura</b>. Los registros los crea el docente "
                "o el administrador.", "escudo")
        + '<div class="sep sep-16"></div>'
        + tabla(["Fecha", "Tipo de registro", "Registrado por"], filas_seg)
        + '<div class="sep sep-12"></div>'
        + '<a class="btn btn-secundario" href="seguimiento.html">' + ico("eye", 16) + " Ver historial completo</a>"
    )

    # --- Panel: Tareas ------------------------------------------------------
    filas_tar = [
        ["Levantar precios de la competencia", badge("Alta", "b-azul", "alerta"),
         "12 nov 2024", badge("Pendiente", "b-amarillo", "reloj"),
         _a("eye", "Ver detalle", "tarea-detalle.html")],
        ["Subir evidencia fotográfica del punto de venta", badge("Media", "b-neutra", "reloj"),
         "15 nov 2024", badge("En revisión", "b-azul", "reloj"),
         _a("eye", "Ver detalle", "tarea-detalle-en-revision.html")],
        ["Definir el margen por producto", badge("Alta", "b-azul", "alerta"),
         "10 nov 2024", badge("Completada", "b-linea", "check"),
         _a("eye", "Ver detalle", "tarea-detalle-completada-precio.html")],
    ]
    panel_tareas = (
        callout("Estas son las tareas activas del plan. Completa las pendientes y sube la "
                "evidencia para que el docente las revise.", "doc")
        + '<div class="sep sep-16"></div>'
        + tabla(["Tarea", "Prioridad", "Fecha límite", "Estado", "@ACC"], filas_tar)
        + '<div class="sep sep-12"></div>'
        + '<a class="btn btn-secundario" href="tareas.html">' + ico("layers", 16) + " Ver todas mis tareas</a>"
    )

    # --- Panel: Asesorias ---------------------------------------------------
    filas_ase = [
        ["15 nov 2024, 09:00", "Asesoría de modelo de negocio", "Carlos Mendoza",
         badge("Confirmada", "b-azul", "check")],
        ["08 nov 2024, 14:00", "Revisión de precios y margen", "Carlos Mendoza",
         badge("Realizada", "b-linea", "check")],
    ]
    panel_asesorias = (
        callout("Puedes <b>solicitar</b> una asesoría y consultar las que ya tienes. La "
                "asignación del docente y la confirmación del horario las hace el rol DOCENTE "
                "o ADMINISTRADOR.", "escudo")
        + '<div class="sep sep-16"></div>'
        + tabla(["Fecha", "Motivo", "Docente", "Estado"], filas_ase)
        + '<div class="sep sep-12"></div>'
        + '<div class="fila-acciones">'
        + '<a class="btn btn-acento" href="solicitar-asesoria.html">' + ico("chat", 16) + " Solicitar asesoría</a>"
        + '<a class="btn btn-secundario" href="asesorias.html">' + ico("eye", 16) + " Ver historial</a>"
        + "</div>"
    )

    # ED1+ED2: cada pestaña alterna un panel (mismo patron que estado-seguimiento
    # y plan-trabajo). Antes los botones no traian data-panel y la pagina solo
    # tenia el contenido de "Resumen": al hacer clic no cambiaba nada.
    paneles = [
        ("Resumen", "resumen", panel_resumen),
        ("Diagnóstico", "diagnostico", panel_diagnostico),
        ("Plan de trabajo", "plan", panel_plan),
        ("Seguimiento", "seguimiento", panel_seguimiento),
        ("Tareas", "tareas", panel_tareas),
        ("Asesorías", "asesorias", panel_asesorias),
    ]
    cuerpo = (
        tabs_paneles([(n, pid) for n, pid, _ in paneles])
        + '<div class="sep sep-20"></div>'
        + "".join(
            '<div data-panel-nombre="%s"%s>%s</div>'
            % (pid, "" if i == 0 else " hidden", cont)
            for i, (_, pid, cont) in enumerate(paneles)
        )
    )
    return shell(R, "emprendimientos", "Sabor y Sabe", cuerpo,
                 migas=["Inicio", "Mi emprendimiento", "Sabor y Sabe"],
                 sub="Detalle de tu emprendimiento.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>' % ico("izq", 16)
                          + '<a class="btn btn-acento" href="emprendimiento-editar.html">%s Editar</a>' % ico("edit", 16))


# --- 5. Editar emprendimiento ------------------------------------------------
def emprendimiento_editar():
    cuerpo = (
        callout("Estás editando <b>Sabor y Sabe</b>. Los cambios de nombre y descripción quedan "
                "registrados en el historial del emprendimiento.", "alerta")
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card(
            "Datos que puedes editar",
            campo("Nombre del emprendimiento", valor="Sabor y Sabe", req=True,
                  ayuda="Entre 4 y 80 caracteres.")
            + campo("Descripción", alto=True,
                    valor="Emprendimiento de alimentos y bebidas que prepara y comercializa "
                          "snacks artesanales a base de frutos secos y granola, con ventas en "
                          "el campus y por pedido a domicilio dentro del municipio.",
                    ph="Describe que vendes, a quien y como lo haces")
            + '<div class="grid g-2 g-col">'
            + campo("Instagram", valor="@saborysabe.md", ph="@usuario")
            + campo("WhatsApp Business", valor="300 555 4412", tipo="tel")
            + "</div>"
            + campo("Tienda propia (sitio web)", valor="", ph="https://")
            + '<div class="fila-fin pt-8">'
            + '<a class="btn btn-secundario" href="emprendimiento-detalle.html">Cancelar</a>'
            + '<button class="btn btn-primario" data-accion="guardar-emprendimiento">%s Guardar cambios</button></div>' % ico("check", 16),
        )
        + "</div>"
        + '<div class="grid">'
        + card(
            "Campos bloqueados para tu rol",
            campo("Tipo de emprendimiento", valor="Alimentos y bebidas",
                  bloqueo="Solo ADMINISTRADOR puede modificarlo.")
            + campo("Sector productivo", valor="Alimentos",
                    bloqueo="Solo ADMINISTRADOR puede modificarlo.")
            + campo("Etapa actual", valor="FASE 2 · Ejecución",
                    bloqueo="Solo DOCENTE y ADMINISTRADOR pueden cambiar la etapa.")
            + campo("Acta de constitución", valor="sin_adjunto.pdf",
                    bloqueo="Solo ADMINISTRADOR puede cargar el acta."),
        )
        + "</div></div>"
    )
    return shell(
        R, "emprendimientos", "Editar emprendimiento", cuerpo,
        migas=["Inicio", "Mi emprendimiento", "Sabor y Sabe", "Editar"],
        sub="Actualiza la información que tienes permitido modificar.",
        acciones='<a class="btn btn-secundario" href="emprendimiento-detalle.html">%s Volver</a>' % ico("izq", 16),
    )


# --- 6. Diagnostico (cuestionario) ------------------------------------------
SECCIONES = [
    ("Perfil del emprendimiento", 5),
    ("Problema o necesidad", 4),
    ("Propuesta de valor", 4),
    ("Mercado objetivo", 4),
    ("Capacidad operativa y financiera", 5),
]

# Contador del cuestionario: el JS lo actualiza contando las preguntas reales
# respondidas entre los 22 campos (DG3), en lugar del texto fijo "5 de 22".
CONTADOR_DIAG = ('<span data-contador-diagnostico class="suave">'
                 "Progreso: contando respuestas…</span>")


def diagnostico():
    """Cuestionario de 5 secciones y 22 preguntas(5+4+4+4+5), con navegacion
    real entre secciones (DG1), contenido completo (DG2) y contador real que
    cuenta las respondidas (DG3). El botón "Enviar diagnóstico" queda en la
    última sección."""
    preguntas = [
        ("Perfil del emprendimiento", [
            campo("Cuál es el nombre de tu emprendimiento?", valor="Sabor y Sabe",
                  ph="Ej. Sabor y Sabe", req=True),
            select("Qué tipo de emprendimiento es?",
                   ["Alimentos y bebidas", "Moda y accesorios", "Servicios", "Tecnología"],
                   valor="Alimentos y bebidas", req=True),
            select("A qué sector productivo pertenece?",
                   ["Alimentos", "Textil", "Servicios", "Tecnología"],
                   valor="Alimentos", req=True),
            campo("Qué producto o servicio ofreces?", alto=True,
                  valor="Snacks artesanales de frutos secos y granola", req=True),
            select("En qué etapa del programa está tu emprendimiento?",
                   ["FASE 1 - Ideación", "FASE 2 - Ejecución",
                    "FASE 3 - Consolidación", "FASE 4 - Escalamiento"],
                   valor="FASE 2 - Ejecución", req=True),
        ]),
        ("Problema o necesidad", [
            campo("Qué problema concreto resuelve tu producto o servicio?",
                  alto=True, valor="Pocas opciones de snacks saludables y accesibles en el campus",
                  ph="Describe el problema", req=True),
            campo("A quién le ocurre ese problema?", valor="Estudiantes y personal del campus",
                  ph="Describe a quien afecta", req=True),
            campo("Cómo lo resuelven hoy (sin tu producto)?",
                  valor="Snacks industriales de baja calidad nutricional", req=True),
            select("Qué tan urgente es el problema para tu cliente?",
                   ["Baja", "Media", "Alta"], valor="Alta", req=True),
        ]),
        ("Propuesta de valor", [
            campo("Cuál es tu propuesta de valor en una frase?", alto=True,
                  valor="Snacks artesanales, saludables y con ingredientes locales", req=True),
            campo("Qué beneficio concreto entrega al cliente?",
                  valor="Alimentacion más sana sin renunciar al sabor ni al precio", req=True),
            select("Qué te diferencia de la competencia?",
                   ["Precio", "Calidad", "Sostenibilidad", "Cercanía con el cliente"],
                   valor="Sostenibilidad", req=True),
            select("Qué necesidad principal cubre?",
                   ["Salud", "Comodidad", "Precio", "Sabor"], valor="Salud", req=True),
        ]),
        ("Mercado objetivo", [
            campo("Quién es tu cliente ideal (perfil)?", valor="Estudiantes de 18-25 que cuidan su alimentación",
                  req=True),
            campo("Cuántos clientes potenciales estimas?", valor="Unos 400 estudiantes del campus", req=True),
            select("Cuál es tu estrategia de precio?",
                   ["Economía (bajo costo)", "Valor medio", "Premium"], valor="Valor medio", req=True),
            campo("Qué canales usarás para llegarles?", valor="Punto de venta en cafetería y WhatsApp", req=True),
        ]),
        ("Capacidad operativa y financiera", [
            select("Con cuántas personas cuenta el equipo?",
                   ["1 (fundador/a)", "2 - 3", "4 - 5", "Más de 5"], valor="2 - 3", req=True),
            campo("Cuál es tu capacidad de producción actual?",
                  valor="80 unidades semanales", req=True),
            select("Llevas registro de costos y ventas?",
                   ["No", "Básico (cuaderno)", "Completo (planilla)"], valor="Básico (cuaderno)", req=True),
            campo("Qué inversión necesitas para crecer?", valor="$ la primera compra de insumos", req=True),
            campo("Cuál es tu meta de ventas del próximo mes?",
                  valor="160 unidades / $480.000", req=True),
        ]),
    ]
    total = sum(len(p) for _, p in preguntas)
    n = len(preguntas)

    def panel(i, titulo, bloques):
        oculta = ' hidden' if i else ''
        anterior = ('<button class="btn btn-secundario" data-accion="seccion-anterior">%s Anterior</button>'
                    % ico("izq", 15)) if i else ''
        siguiente = ('<button class="btn btn-acento" data-accion="enviar-diagnostico">%s Enviar diagnóstico</button>'
                     % ico("enviar", 15)) if i == n - 1 else (
                     '<button class="btn btn-acento" data-accion="seccion-siguiente">%s Siguiente sección</button>'
                     % ico("der", 15))
        return ('<div class="card" data-panel-nombre="seccion-%d"%s>'
                '<div class="card-head"><h3>Sección %d de %d &middot; %s</h3></div>'
                '<div class="card-body">%s<div class="divisor"></div>'
                '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
                '<span class="suave">%s</span>'
                '<div class="fila-acciones">'
                '<button class="btn btn-secundario" data-accion="guardar-borrador">Guardar borrador</button>'
                '%s%s</div></div></div></div>'
                % (i, oculta, i + 1, n, titulo, bloques, CONTADOR_DIAG, anterior, siguiente))

    paneles = "".join(panel(i, t, "".join(b)) for i, (t, b) in enumerate(preguntas))
    cuerpo = (
        steps([s[0].split(" y ")[0] for s in SECCIONES], 0)
        + '<div class="grid g-2-1">'
        + '<div class="grid">' + paneles + "</div>"
        + '<div class="grid">'
        + card("Cómo va el cuestionario",
               barras_h("", "", ["Perfil", "Problema", "Propuesta", "Mercado", "Capacidad"],
                        [100, 0, 0, 0, 0], maximo=100, unidad="%"),
               hint="5 secciones")
        + card("Puedes pausar cuando quieras",
               '<div class="suave">Tu respuesta se guarda como '
               "<b>borrador</b>. Solo se envía al docente cuando completas las 5 secciones "
               "y pulsas <b>Enviar diagnóstico</b>.</div>"
               '<div style="margin-top:12px">%s</div>' % badge("Borrador guardado", "b-linea", "doc"))
        + "</div></div>"
    )
    return shell(R, "diagnostico", "Diagnóstico inicial", cuerpo,
                 migas=["Inicio", "Diagnóstico"],
                 sub="Responde el cuestionario para que el docente pueda construir tu plan de trabajo.",
                 acciones='<button class="btn btn-secundario" data-accion="guardar-y-salir">%s Guardar y salir</button>'
                          % ico("doc", 16))


# --- 7. Resultados del diagnostico ------------------------------------------
def diagnostico_resultados():
    cuerpo = (
        '<div class="grid g-4">'
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Estado del envío</div>'
          '<div class="metrica-val" style="font-size:20px">Enviado</div></div></div>'
          '<div class="nota-foot">Enviado el 28 oct 2024, 09:14</div></div>' % ico("enviar", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Calidad entrepreneurial</div>'
          '<div class="metrica-val">7.8<span class="u">/ 10</span></div></div></div></div>' % ico("medalla", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">NPS estimado</div>'
          '<div class="metrica-val">9</div></div></div></div>' % ico("trend", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Áreas a reforzar</div>'
          '<div class="metrica-val">3</div></div></div></div>' % ico("alerta", 18)
        + "</div>"
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Comportamiento entrepreneurial", barras_h(
            "", "", ["Visión", "Creatividad", "Resiliencia", "Liderazgo", "Trabajo en equipo",
                     "Capacidad de decisión"],
            [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
        + card("Distribución de las respuestas", donut(
            "", "", [("Problema claro", 82, AZUL), ("Propuesta de valor", 74, AZUL),
                     ("Mercado definido", 61, AZUL), ("Viabilidad financiera", 55, AMAR)], "% respuestas"))
        + "</div>"
        + '<div class="grid">'
        + card("Recomendaciones del docente",
               '<div class="lista-def" style="padding:4px 0">'
               + "".join(
                   '<div class="fila-paso">'
                   '<span style="color:#004a93;flex:0 0 18px">%s</span>'
                   '<div class="fuerte">%s</div></div>' % (ico("alerta", 16), t)
                   for t in [
                       "Definir con más precisión el canal de venta digital.",
                       "Separar el presupuesto de insumos del presupuesto de publicidad.",
                       "Registrar el costo fijo mensual para calcular el punto de equilibrio.",
                   ]
               )
               + "</div>")
        + card("Puntaje por dimensión",
               '<div class="suave">Este resultado es una foto del momento. '
               "Volveras a responder el diagnóstico al cierre de cada fase.</div>")
        + "</div></div>"
    )
    return shell(R, "diagnostico", "Resultado del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico", "Resultado"],
                 sub="Puntaje, comportamiento entrepreneurial y recomendaciones del docente.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s Descargar PDF</button>' % ico("download", 16)
                          + '<a class="btn btn-primario" href="diagnostico.html">%s Volver a responder</a>' % ico("clipboard", 16))


# --- 8. Plan de trabajo ------------------------------------------------------
FASES = [
    ("FASE 1", "Ideación y priorización de ideas", 100, [
        ("Definir la idea y el problema que ataca", "Completada"),
        ("Identificar clientes potenciales", "Completada"),
        ("Validar la solución con usuarios", "Completada"),
    ]),
    ("FASE 2", "Estructuración y ejecución", 62, [
        ("Levantar el modelo de negocio", "En curso"),
        ("Definir la mezcla de marketing", "En curso"),
        ("Calcular el punto de equilibrio", "Pendiente"),
        ("Constituir el Startup Minuto de Dios", "Pendiente"),
    ]),
    ("FASE 3", "Consolidación del proceso", 0, [
        ("Formalizar la operación diaria", "Bloqueada"),
        ("Registrar indicadores de venta", "Bloqueada"),
    ]),
    ("FASE 4", "Escalamiento", 0, [
        ("Escalar el modelo de negocio", "Bloqueada"),
        ("Buscar alianzas estratégicas", "Bloqueada"),
    ]),
]


def _bloques_plan(fases, resumen, avance):
    """Plan de trabajo por emprendimiento: fases + columna de resumen."""
    bloques = ""
    for codigo, nombre, pct, tareas in fases:
        filas = ""
        for t, est in tareas:
            col = {"Completada": ("b-linea", "check"), "En curso": ("b-azul", "reloj"),
                   "Pendiente": ("b-amarillo", "bombilla"), "Bloqueada": ("b-neutra", "lock")}[est]
            filas += (
                '<div style="display:flex;align-items:center;gap:12px;padding:10px 0;'
                'border-bottom:1px solid #bbbbbb">'
                '<span style="color:#004a93;flex:0 0 18px">%s</span>'
                '<span class="fuerte" style="flex:1">%s</span>%s</div>'
                % (ico("checklist", 16), t, badge(est, col[0], col[1]))
            )
        cab = AMAR if 0 < pct < 100 else (AZUL if pct == 100 else GRIS)
        bloques += (
            '<div class="card"><div class="card-head">'
            '<span style="background:%s;color:%s;border-radius:6px;padding:3px 9px;'
            'font-size:13px;font-weight:700;letter-spacing:.04em">%s</span>'
            '<h3>%s</h3>'
            '<span class="fuerte" style="font-weight:700">%d%%</span></div>'
            '<div class="card-body sin-pad"><div style="padding:6px 20px 14px">%s</div>'
            '<div style="padding:0 20px 16px"><div class="barra"><span style="width:%d%%;'
            'background:%s"></span></div></div></div></div>'
            % (cab, "#051533" if cab == AMAR else "#ffffff", codigo, nombre, pct, filas, pct, cab)
        )
    return (
        '<div class="grid g-2-1">'
        + '<div class="grid">' + bloques + "</div>"
        + '<div class="grid">'
        + card("Avance general", '<div style="text-align:center">'
             + circular(avance[0], "avance", avance[1]) + "</div>")
        + card("Resumen por estado", stacked_tareas(resumen, "tareas"))
        + "</div></div>"
    )


def plan_trabajo():
    paneles = [
        (
            "Sabor y Sabe",
            "emp-sabor",
            FASES,
            [("Alta", 2, AZUL), ("Media", 3, PROF), ("Baja", 1, GRIS)],
            (62, "FASE 2 · Ejecución"),
        ),
        (
            "Mochilas Origen",
            "emp-mochilas",
            [
                ("FASE 1", "Ideación y priorización de ideas", 24, [
                    ("Definir la idea y el problema que ataca", "Completada"),
                    ("Identificar clientes potenciales", "En curso"),
                    ("Validar la solución con usuarios", "Pendiente"),
                ]),
                ("FASE 2", "Estructuración y ejecución", 0, [
                    ("Levantar el modelo de negocio", "Bloqueada"),
                    ("Definir la mezcla de marketing", "Bloqueada"),
                    ("Calcular el punto de equilibrio", "Bloqueada"),
                    ("Constituir el Startup Minuto de Dios", "Bloqueada"),
                ]),
                ("FASE 3", "Consolidación del proceso", 0, [
                    ("Formalizar la operación diaria", "Bloqueada"),
                    ("Registrar indicadores de venta", "Bloqueada"),
                ]),
                ("FASE 4", "Escalamiento", 0, [
                    ("Escalar el modelo de negocio", "Bloqueada"),
                    ("Buscar alianzas estratégicas", "Bloqueada"),
                ]),
            ],
            [("Alta", 1, AZUL), ("Media", 1, PROF), ("Baja", 1, GRIS)],
            (24, "FASE 1 · Ideación"),
        ),
    ]
    cuerpo = (
        callout("El plan de trabajo lo construye el docente que tienes asignado y tu solo "
                "puedes consultar su avance y completar las tareas.", "escudo")
        + '<div class="sep sep-20"></div>'
        + tabs_paneles([(n, pid) for n, pid, _, _, _ in paneles])
        + '<div class="sep sep-20"></div>'
        + "".join(
            '<div data-panel-nombre="%s"%s>%s</div>' % (pid, "" if i == 0 else " hidden",
                                                         _bloques_plan(fases, resumen, avance))
            for i, (_, pid, fases, resumen, avance) in enumerate(paneles)
        )
    )
    return shell(R, "plan-trabajo", "Plan de trabajo", cuerpo,
                 migas=["Inicio", "Plan de trabajo"],
                 sub="Las cuatro fases del Startup Minuto de Dios y tu avance por emprendimiento.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s Descargar plan</button>' % ico("download", 16))


# --- 9. Seguimiento (historial) --------------------------------------------
def seguimiento():
    filas = []
    for f, est, desc, doc in [
        ("22 oct 2024", "Avance de fase", "Se avanzo en el levantamiento del modelo de negocio y se "
         "acordo definir el canal de venta por redes.", "Carlos Mendoza"),
        ("05 nov 2024", "Avance de fase", "Revisión de ventas de la semana. Se detectó que el margen "
         "es bajo en la granola de cacao; se evalua cambiar el proveedor.", "Carlos Mendoza"),
        ("08 nov 2024", "Comentario", "Se recuerda cargar la evidencia fotográfica de cada venta "
         "en las tareas asignadas.", "Carlos Mendoza"),
        ("12 nov 2024", "Avance de fase", "Se define el precio de venta final con margen "
         "del 35 por ciento.", "Carlos Mendoza"),
    ]:
        filas.append([f, badge(est, "b-azul" if "Avance" in est else "b-neutra",
                               "trend" if "Avance" in est else "chat"), desc, doc,
                      _acc(_b("eye", "Ver detalle"))])
    cuerpo = (
        callout("El seguimiento es de <b>solo lectura</b>. Los registros los crea el docente o el "
                "administrador según las reglas de gestión.", "escudo")
        + '<div class="sep sep-20"></div>'
        + tabla(["Fecha", "Tipo de registro", "Descripción", "Registrado por", "@ACC"], filas)
        + paginas(1, 4, 4)
        + '<div class="sep sep-20"></div>'
        + card("Frecuencia con que te acompaña el docente",
               barras_h("", "", ["FASE 1 · Oct 2024", "FASE 2 · Nov 2024"],
                        [4, 3], maximo=6, unidad=" registros"))
    )
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Historial de los acompañamientos registrados por tu docente.")


# --- 10. Tareas (lista) ------------------------------------------------------
def tareas():
    """Tablero por estado: el estudiante ve que esta haciendo y que falta."""
    cuerpo = (
        metricas([
            ("checklist", "Tareas asignadas", "7", "en total", 100, ""),
            ("check", "Completadas", "3", "", 43, ""),
            ("reloj", "Pendientes", "3", "", 43, ""),
            ("alerta", "En revisión", "1", "", 14, ""),
        ])
        + '<div class="sep sep-20"></div>'
        + kanban([
            ("Pendientes", [
                ("Subir evidencia fotográfica del punto de venta",
                 "Vence hoy · Carlos Mendoza",
                 badge("Alta", "b-azul", "alerta"),
                 '<a class="btn btn-sm btn-primario" href="tarea-detalle.html">'
                 'Abrir</a>'),
                ("Actualizar el inventario de insumos",
                 "Vence 13 nov 2024 · Carlos Mendoza",
                 badge("Media", "b-neutra", "reloj"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Abrir</a>'),
                ("Registrar las ventas de la semana",
                 "Vence 15 nov 2024 · Carlos Mendoza",
                 badge("Media", "b-neutra", "reloj"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Abrir</a>'),
            ]),
            ("En revisión", [
                ("Levantar el modelo de negocio",
                 "Enviada el 04 nov 2024 · esperando calificación",
                 badge("Alta", "b-azul", "alerta"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle-en-revision.html">'
                 'Ver</a>'),
            ]),
            ("Completadas", [
                ("Definir el precio de venta final",
                 "Completada el 08 nov 2024",
                 badge("Calificada 90", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle-completada-precio.html">'
                 'Ver</a>'),
                ("Validar la solución con 10 usuarios",
                 "Completada el 01 nov 2024",
                 badge("Calificada 85", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle-completada-usuarios.html">'
                 'Ver</a>'),
                ("Definir clientes potenciales",
                 "Completada el 28 oct 2024",
                 badge("Calificada 92", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle-completada-clientes.html">'
                 'Ver</a>'),
            ]),
        ])
        + '<p class="nota-foot">Arrastra no aplica: cada tarea se mueve cuando '
          'el docente la califica.</p>'
    )
    return shell(R, "tareas", "Mis tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Tareas que debes completar y su evidencia.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s Descargar reporte</button>' % ico("download", 16))


# --- 11. Detalle de tarea ----------------------------------------------------
def tarea_detalle():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Subir evidencia fotográfica del punto de venta",
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", "12 de noviembre de 2024"),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("Pendiente", "b-amarillo", "reloj")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p class="suave">Adjunta al menos tres fotografías del '
                 "punto de venta con los productos expuestos y la cartelera de precios. La evidencia "
                 "debe mostrar la fecha de toma.</p>")
        + card(
            "Evidencia adjunta",
            '<label class="drop" for="evidencia-real">%s'
            "<b style=\"display:block;color:#051533;font-size:13px\">Arrastra tus archivos aquí "
            "o haz clic para seleccionarlos</b>"
            '<span style="font-size:13px">Formatos admitidos: JPG, PNG o PDF &middot; Máximo 10 MB</span>'
            '<input type="file" id="evidencia-real" multiple accept=".jpg,.jpeg,.png,.pdf" '
            'aria-label="Seleccionar evidencia" style="display:none"></label>'
            % ico("upload", 34),
            hint='<span id="contador-adjuntos">0 archivos</span>')
        + card("Adjuntos",
               '<div id="adjuntos-lista">' + estado_vacio(
                   "Todavía no has adjuntado evidencia",
                   "Cuando subas los archivos aparecerán aquí con su fecha de carga.",
                   '<button class="btn btn-secundario" data-accion="adjuntar-evidencias">%s Adjuntar ahora</button>'
                   % ico("clip", 16), "clip")
               + "</div>")
        + "</div>"
        + '<div class="grid">'
        + card("Marcar como completada", '<p class="suave">'
             "Solo puedes marcar la tarea como completada si adjuntaste al menos un archivo "
             "de evidencia.</p>"
             '<button class="btn btn-acento" style="width:100%%;margin-top:14px" '
             'data-accion="marcar-completada" disabled>'
             "%s Marcar como completada</button>"
             '<div class="nota-foot">El botón se habilita cuando exista evidencia adjunta.</div>'
             % ico("check", 16))
        + card("Comentarios del docente",
               '<div class="lista-def" style="padding:4px 0">'
               '<div class="def-row" style="display:block"><dd style="color:#051533">'
               "Recuerda que las fotos deben incluir la fecha de toma para validar la evidencia."
               '</dd><dt style="flex:0 0 auto;margin-top:6px;font-size:13px">'
               "Carlos Mendoza &middot; 09 nov 2024</dt></div></div>")
        + "</div></div>"
    )
    return shell(R, "tareas", "Subir evidencia fotográfica del punto de venta", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Detalle de la tarea asignada.",
                 acciones='<a class="btn btn-secundario" href="tareas.html">%s Volver</a>' % ico("izq", 16))


def _archivos_cargados(archivos):
    """Lista de evidencia ya cargada (solo lectura): sin opción de adjuntar ni quitar."""
    filas = ""
    for nombre, tam, dia in archivos:
        filas += (('<div class="def-row">' + ico("clip", 16)
                   + '<dd style="color:#051533"><b>%s</b><br>'
                     '<span class="suave">%s · %s</span></dd>'
                   + '<dt style="flex:0 0 auto">%s</dt></div>')
                  % (nombre, tam, dia, badge("Enviado", "b-neutra", "check")))
    return '<div class="lista-def" style="padding:4px 0">%s</div>' % filas


def tarea_detalle_en_revision():
    """Tarea EN REVISION: evidencia ya enviada y sin opciones de carga."""
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Levantar el modelo de negocio",
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", "04 de noviembre de 2024"),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("En revisión", "b-azul", "reloj")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p class="suave">Elabora el lienzo del modelo de negocio '
                 "de Sabor y Sabe. Adjunta el lienzo diligenciado y los apuntes de tu docente.</p>")
        + card("Evidencia adjunta",
               _archivos_cargados([
                   ("lienzo-modelo-negocio.pdf", "1.4 MB", "04 nov 2024"),
                   ("apuntes-revision.jpg", "2.1 MB", "04 nov 2024"),
                   ("foto-tablero.jpg", "3.2 MB", "04 nov 2024"),
               ]),
               hint='<span>3 archivos enviados</span>')
        + "</div>"
        + '<div class="grid">'
        + card("En revisión por el docente",
               '<p class="suave">Tu evidencia fue enviada el '
               "<b>04 de noviembre de 2024</b> y ya no puede modificarse. El docente la "
               "revisará y te asignará una calificación.</p>"
               '<div class="nota-foot">La tarea quedará en Completadas cuando el docente la califique.</div>')
        + card("Comentarios del docente",
               '<div class="lista-def" style="padding:4px 0">'
               '<div class="def-row" style="display:block"><dd style="color:#051533">'
               "Tu evidencia está en validación. Recuerda que debe incluir la fecha de toma."
               '</dd><dt style="flex:0 0 auto;margin-top:6px;font-size:13px">'
               "Carlos Mendoza &middot; 04 nov 2024</dt></div></div>")
        + "</div></div>"
    )
    return shell(R, "tareas", "Levantar el modelo de negocio", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Tarea enviada a revisión. La evidencia ya está cargada.",
                 acciones='<a class="btn btn-secundario" href="tareas.html">%s Volver</a>' % ico("izq", 16))


def _tarea_completada(titulo, nota, fecha_limite, fecha_done, descripcion, archivos, comentario):
    """Detalle de una tarea COMPLETADA: calificación, evidencia cargada y solo lectura."""
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card(titulo,
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", fecha_limite),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("Completada · Calificada %d" % nota, "b-linea", "check")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p class="suave">%s</p>' % descripcion)
        + card("Evidencia adjunta",
               _archivos_cargados(archivos),
               hint='<span>%d archivos enviados</span>' % len(archivos))
        + "</div>"
        + '<div class="grid">'
        + card("Calificación",
               circular(nota, "Calificación", "Completada el %s" % fecha_done)
               + '<p class="suave mt-8">'
                 "<b>Felicitaciones.</b> Esta tarea fue calificada y entregada y ya no puede "
                 "modificarse.</p>")
        + card("Comentarios del docente",
               '<div class="lista-def" style="padding:4px 0">'
               '<div class="def-row" style="display:block"><dd style="color:#051533">'
               + comentario
               + '</dd><dt style="flex:0 0 auto;margin-top:6px;font-size:13px">'
                 "Carlos Mendoza &middot; %s</dt></div></div>" % fecha_done)
        + "</div></div>"
    )
    return shell(R, "tareas", titulo, cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Tarea completada y calificada por el docente.",
                 acciones='<a class="btn btn-secundario" href="tareas.html">%s Volver</a>' % ico("izq", 16))


def tarea_detalle_completada_precio():
    return _tarea_completada(
        "Definir el precio de venta final", 90,
        "30 de octubre de 2024", "08 nov 2024",
        "Define el precio de venta final de cada producto con base en el análisis de costos "
        "y el margen acordado con tu docente.",
        [("analisis-costos.pdf", "1.2 MB", "07 nov 2024"),
         ("tabla-precios.xlsx", "840 KB", "07 nov 2024"),
         ("foto-cartelera.jpg", "2.6 MB", "08 nov 2024")],
        "Excelente análisis de costos. El precio final queda sustentado con el margen esperado.")


def tarea_detalle_completada_usuarios():
    return _tarea_completada(
        "Validar la solución con 10 usuarios", 85,
        "27 de octubre de 2024", "01 nov 2024",
        "Realiza la validación de la solución con al menos 10 usuarios y adjunta el registro "
        "de sus respuestas y comentarios.",
        [("registro-validaciones.pdf", "1.8 MB", "31 oct 2024"),
         ("tabla-respuestas.xlsx", "620 KB", "01 nov 2024")],
        "Validación completa. Ajusta el horario de toma de datos para la siguiente ronda.")


def tarea_detalle_completada_clientes():
    return _tarea_completada(
        "Definir clientes potenciales", 92,
        "22 de octubre de 2024", "28 oct 2024",
        "Segmenta los clientes potenciales del emprendimiento y adjunta el estudio de mercado "
        "que respalda la segmentación.",
        [("estudio-mercado.pdf", "2.3 MB", "28 oct 2024"),
         ("segmentacion-clientes.xlsx", "900 KB", "27 oct 2024")],
        "Segmentación clara y bien sustentada. Considera incluir una etapa de validación.")


# --- 12. Asesorias -----------------------------------------------------------
def asesorias():
    """Línea de tiempo: primero lo que viene, después lo ya realizado."""
    cuerpo = (
        callout("Como estudiante puedes <b>solicitar</b> una asesoría y consultar las que ya "
                "tienes. La asignación del docente y la confirmación del horario los realiza el "
                "rol DOCENTE o ADMINISTRADOR.", "escudo")
        + '<div class="sep sep-20"></div>'
        + metricas([
            ("chat", "Asesorías realizadas", "3", "", 100, ""),
            ("reloj", "Programadas", "3", "", 100, ""),
            ("check", "Confirmadas", "2", "", 67, ""),
        ])
        + '<div class="sep sep-20"></div>'
        + card("Próximas asesorías", linea_tiempo([
            ("14", "nov", "Asesoría con Laura Sánchez",
             "14:30 - 15:30 · Presencial · Pendiente de confirmar",
             '<div style="margin-top:10px">'
             + badge("Pendiente de confirmar", "b-amarillo", "reloj")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("19", "nov", "Asesoría con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Confirmada",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("12", "nov", "Asesoría con Carlos Mendoza",
             "10:00 - 11:00 · Virtual · Confirmada",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
        ]), sin_pad=False)
        + '<div class="sep sep-20"></div>'
        + card("Asesorías realizadas", linea_tiempo([
            ("04", "nov", "Asesoría con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Realizada",
             '<div style="margin-top:10px">'
             + badge("Realizada", "b-linea", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-acta\">Ver acta</button></div>"),
        ]))
    )
    return shell(R, "asesorias", "Mis asesorías", cuerpo,
                 migas=["Inicio", "Asesorías"],
                 sub="Historial y próximas asesorías de tu emprendimiento.",
                 acciones='<a class="btn btn-acento" href="solicitar-asesoria.html">%s Solicitar asesoría</a>'
                          % ico("plus", 16))


# --- 13. Solicitar asesoria --------------------------------------------------
def solicitar_asesoria():
    cuerpo = (
        callout("Tu solicitud enviará al docente asignado. <b>No puedes elegir libremente el "
                "docente ni el horario</b>: el docente o el administrador confirmarán la fecha.", "escudo")
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card(
            "Datos de la solicitud",
            select("Emprendimiento", ["Sabor y Sabe"], req=True)
            + campo("Docente asignado", valor="Carlos Mendoza",
                    bloqueo="El docente se asigna según las reglas del programa, no por el estudiante.")
            + '<div class="grid g-2 g-col">'
            + campo("Fecha preferida", tipo="date", ph="2024-11-20", req=True,
                    ayuda="Es una preferencia. La fecha final la confirma el docente.")
            + campo("Hora preferida", tipo="time", valor="10:00", req=True,
                    ayuda="Propuesta; el docente ajusta si lo necesita.")
            + "</div>"
            + campo("Temas a tratar", alto=True,
                    ph="Describe los temas que quieres tratar en la asesoría",
                    ayuda="Mientras más concreto, mejor podremos preparar la sesión.")
            + '<div class="divisor"></div>'
            + '<div class="fila-fin">'
            + '<a class="btn btn-secundario" href="asesorias.html">Cancelar</a>'
            + '<button class="btn btn-acento" data-accion="enviar-solicitud">%s Enviar solicitud</button></div>' % ico("enviar", 16),
        )
        + "</div>"
        + '<div class="grid">'
        + card("Cómo funciona",
               '<div class="lista-def" style="padding:4px 0">'
               + "".join(
                   '<div class="fila-paso">'
                   '<span style="flex:0 0 20px;width:20px;height:20px;border-radius:999px;'
                   'background:%s;color:%s;display:flex;align-items:center;justify-content:center;'
                   'font-size:13px;font-weight:700">%d</span>'
                   '<span class="fuerte">%s</span></div>'
                   % (AZUL, "#ffffff", i + 1, t)
                   for i, t in enumerate([
                       "Envías la solicitud con tus temas.",
                       "El docente recibe la notificación y responde.",
                       "Se confirma la fecha y la modalidad.",
                       "Asistes y la asesoría queda registrada.",
                   ])
               )
               + "</div>")
        + "</div></div>"
    )
    return shell(
        R, "asesorias", "Solicitar asesoría", cuerpo,
        migas=["Inicio", "Asesorías", "Solicitar"],
        sub="Registra tu solicitud. El docente confirmará fecha y modalidad.",
        acciones='<a class="btn btn-secundario" href="asesorias.html">%s Volver</a>' % ico("izq", 16),
    )


# --- 14. Eventos -------------------------------------------------------------
def eventos():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Próximos eventos", tabla(
            ["Evento", "Tipo", "Fecha y hora", "Modalidad", "Organizador", "@ACC"],
            [['<b>Startup Minuto de Dios</b>', "Conferencia",
              "21 nov 2024, 08:00", "Presencial", "Dirección Académica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Capacitación en modelado de negocios</b>', "Taller",
              "21 nov 2024, 14:00", "Virtual", "Coordinación Académica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Asesoría grupal de empleabilidad</b>', "Asesoría",
              "26 nov 2024, 10:00", "Presencial", "Bienestar Estudiantil",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Showroom de emprendimientos</b>', "Muestra",
              "02 dic 2024, 09:00", "Presencial", "Dirección Académica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))]],
            id="tabla-proximos"))
        + '<div data-listado-inscritos>'
        + card("Eventos en los que ya estas inscrito", tabla(
            ["Evento", "Fecha y hora", "Modalidad", "@ACC"],
            [['<b>Conferencia: Claves del emprendimiento digital</b>', "15 nov 2024, 08:00",
              "Virtual", badge("Inscrito", "b-linea", "check")]],
            id="tabla-inscritos")) + "</div>"
        + "</div>"
        + '<div class="grid">'
        + card("Calendario de noviembre",
               '<div style="border:1px solid #bbbbbb;border-radius:8px;overflow:hidden">'
               + _calendario("noviembre", 2024)
               + "</div>")
        + card("Cómo inscribirte",
               '<div class="suave">Al inscribirte, el evento aparece en '
               "tu panel y recibes recordatorio el día anterior. Puedes cancelar tu inscripción "
               "desde el detalle del evento.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Eventos, talleres y asesorías de la institución.")


def _calendario(mes, anio):
    import calendar
    MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
             "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
             "noviembre": 11, "diciembre": 12}
    m = MESES.get(str(mes).lower(), 11)
    dias = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
    hoy = 12
    habiles = [21, 26, 2]
    primer_dia, n_dias = calendar.monthrange(anio, m)
    h = ('<div class="cal cal-cab">'
         + "".join("<div>%s</div>" % d for d in dias) + "</div>")
    h += '<div class="cal">'
    for _ in range(primer_dia):
        h += '<div class="cal-vacio"></div>'
    for d in range(1, n_dias + 1):
        hoy_ = d == hoy
        even = d in habiles
        h += '<div class="cal-celda%s">%d' % (" hoy" if hoy_ else "", d)
        if even:
            h += '<span class="cal-punto"></span>'
        h += "</div>"
    return h + "</div>"


# --- 15. Perfil --------------------------------------------------------------
def perfil():
    cuerpo = (
        callout("Aquí puedes mantener tus datos personales y tu contraseña. Los campos "
                "institucionales los mantiene el administrador de la institución.", "escudo")
        + '<div class="sep sep-20"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid">'
        + card("Datos personales",
               '<div class="grid g-2 g-col">'
               + campo("Nombres", valor="Mariana") + campo("Apellidos", valor="López Herrera")
               + "</div>"
               + '<div class="grid g-2 g-col">'
               + campo("Tipo de documento", valor="CC")
               + campo("Número de documento", valor="1020304050",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2 g-col">'
               + campo("Correo personal", valor="mariana.lopez@correo.com", tipo="email")
               + campo("Correo institucional", valor="mariana.lopez@minutodedios.edu.co",
                       tipo="email", bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2 g-col">'
               + campo("Teléfono fijo", valor="604 123 4567", tipo="tel")
               + campo("Celular", valor="300 555 4412", tipo="tel")
               + "</div>"
               + '<div class="fila-fin">'
               + '<button class="btn btn-secundario" data-accion="cancelar-perfil">Cancelar</button>'
               + '<button class="btn btn-primario" data-accion="guardar-perfil">%s Guardar cambios</button></div>' % ico("check", 16))
        + card("Cambiar contraseña",
               '<div class="grid g-3 g-col">'
               + campo("Contraseña actual", tipo="password", ph="••••••••")
               + campo("Nueva contraseña", tipo="password", ph="Mínimo 8 caracteres")
               + campo("Repetir nueva contraseña", tipo="password", ph="••••••••")
               + "</div>"
               '<div style="display:flex;justify-content:flex-end">'
               '<button class="btn btn-secundario" data-accion="actualizar-contrasena">Actualizar contraseña</button></div>')
        + "</div>"
        + '<div class="grid">'
        + card("Mi rol en el sistema",
               '<div style="text-align:center;padding:8px 0">'
               '<span class="avatar" style="width:72px;height:72px;margin:0 auto;font-size:20px">ML</span>'
               '<h3 style="margin-top:12px">Mariana López Herrera</h3>'
               '<div style="margin-top:6px">%s</div></div>' % badge("ESTUDIANTE", "b-amarillo", "user"))
        + card("Estado de la cuenta", '<div class="lista-def" style="padding:4px 0">'
             '<div class="def-row"><dt>Estado</dt><dd>%s</dd></div>' % badge("Limitado", "b-amarillo", "lock")
             + '<div class="def-row"><dt>Emprendimientos</dt><dd>2</dd></div>'
             + '<div class="def-row"><dt>Tareas pendientes</dt><dd>4</dd></div>'
             + '<div class="def-row"><dt>Fecha de registro</dt><dd>12 oct 2024</dd></div>'
             "</div>",
             accion='<button class="btn btn-secundario btn-sm" data-accion="cerrar-sesion">%s Cerrar sesión</button>' % ico("salir", 15))
        + "</div></div>"
    )
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Perfil"],
                 sub="Información de tu cuenta y preferencias.")


# --- 16. Notificaciones ------------------------------------------------------
def notificaciones():
    items = [
        (True, "Asesoría confirmada", "Tu asesoría con Carlos Mendoza quedó confirmada para el "
         "martes 12 de noviembre a las 10:00.", "hace 12 minutos", "chat", "asesoria"),
        (True, "Nueva tarea asignada", "Debes subir la evidencia fotográfica del punto de venta "
         "antes del 12 de noviembre.", "hace 2 horas", "checklist", "tarea"),
        (True, "Seguimiento registrado", "Carlos Mendoza registró un avance de fase en tu "
         "emprendimiento Sabor y Sabe.", "ayer, 16:40", "trend", "seguimiento"),
        (False, "Correo verificado", "Tu correo institucional quedó verificado correctamente.",
         "28 oct 2024", "escudo", "sistema"),
        (False, "Bienvenida a SGEMD", "Bienvenida al sistema de gestión de emprendimiento "
         "Minuto de Dios.", "12 oct 2024", "rayo", "sistema"),
    ]
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid">'
        + '<div class="card"><div class="card-head"><h3>Bandeja de notificaciones</h3>'
          '<span class="hint" id="contador-no-leidas">3 sin leer</span></div><div class="card-body sin-pad">'
        + "".join(
            '<div class="notif%s" data-tipo="%s" data-i="%d">'
            '<div style="flex:0 0 34px;width:34px;height:34px;'
            'border-radius:8px;background:rgba(0,74,147,.08);color:#004a93;'
            'display:flex;align-items:center;justify-content:center">%s</div>'
            '<div style="flex:1;min-width:0"><h3>%s</h3><p>%s</p><time>%s</time></div>%s</div>'
            % (" no-leida" if leer else "", tipo, i, ico(ic, 17), t, txt, f,
               '<span class="notif-dot"></span>' if leer else "")
            for i, (leer, t, txt, f, ic, tipo) in enumerate(items)
        )
        + "</div></div>"
        + "</div>"
        + '<div class="grid">'
        + card("Filtros", '<div style="display:flex;flex-direction:column;gap:8px">'
             + "".join('<span class="chip%s" data-chip="%s">%s</span>'
                       % (" on" if i == 0 else "", val, etiqueta)
                       for i, (val, etiqueta) in enumerate(
                           [("todas", "Todas"), ("sin-leer", "Sin leer"),
                            ("tarea", "Tareas"), ("asesoria", "Asesorías"),
                            ("seguimiento", "Seguimiento")]))
             + "</div>")
        + card("Preferencias de notificación", '<div class="lista-def" style="padding:4px 0">'
             + "".join(
                 '<div class="def-row"><dt style="flex:1">%s</dt><dd style="flex:0 0 auto">'
                 '<span class="chip on">Activado</span></dd></div>' % t
                 for t in ["Correo electrónico", "Notificaciones en el sistema", "Recordatorio de tareas"])
             + '<div class="nota-foot">Un administrador puede ajustar estas preferencias.</div>'
         + "</div>")
        + "</div></div>"
    )
    return shell(R, "perfil", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Alertas de tareas, asesorías y seguimiento.",
                 acciones='<button class="btn btn-secundario">%s Marcar todas como leídas</button>'
                          % ico("check", 16))