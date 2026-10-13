# -*- coding: utf-8 -*-
"""Rol ESTUDIANTE — 26 pantallas."""

from lib_ui import (
    shell, metricas, metricas_enlace, opciones_card, tabla, toolbar, paginas, badge,
    campo, select, callout, card, estado_vacio, lista_def, steps, tabs, tabs_paneles,
    ico, boton_accion, ico, linea_tiempo, kanban, agenda, NOTIFS_EST,
)
from lib_charts import (
    barras, barras_h, lineas, donut, circular, progreso_fases, stacked_tareas,
    velocidad, AZUL, PROF, GRIS, AMAR,
)

R = "estudiante"

# --- Tareas por emprendimiento (fuente unica) --------------------------------
# El Inicio, el plan de trabajo y la vista de Tareas leen de aqui, de modo que
# las tres pantallas muestran las mismas tareas, los mismos estados y las mismas
# fechas. Campos: (titulo, prioridad, estado, fase, fecha_limite, fecha_envio,
# detalle).
TAREAS_EMP = [
    ("Sabor y Sabe", "emp-sabor", [
        ("Definir clientes potenciales", "Alta", "Completada", 1,
         "05 nov 2024", "28 oct 2024", "tarea-detalle-completada-clientes.html"),
        ("Validar la solución con 10 usuarios", "Media", "Completada", 1,
         "10 nov 2024", "01 nov 2024", "tarea-detalle-completada-usuarios.html"),
        ("Definir el precio de venta final", "Alta", "Completada", 1,
         "30 oct 2024", "08 nov 2024", "tarea-detalle-completada-precio.html"),
        ("Levantar el modelo de negocio", "Alta", "En revisión", 2,
         "04 nov 2024", "04 nov 2024", "tarea-detalle-en-revision.html"),
        ("Registrar las ventas de la semana", "Media", "En curso", 2,
         "15 nov 2024", "—", "tarea-detalle.html"),
        ("Actualizar el inventario de insumos", "Media", "Pendiente", 2,
         "13 nov 2024", "—", "tarea-detalle.html"),
        ("Subir evidencia fotografica del punto de venta", "Alta", "Pendiente", 2,
         "Hoy", "—", "tarea-detalle.html"),
    ]),
    ("Mochilas Origen", "emp-mochilas", [
        ("Definir la idea y el problema que ataca", "Alta", "Completada", 1,
         "20 sep 2024", "19 sep 2024", "tarea-detalle.html"),
        ("Identificar clientes potenciales", "Media", "En curso", 1,
         "18 nov 2024", "—", "tarea-detalle.html"),
        ("Validar la solución con usuarios", "Media", "Pendiente", 1,
         "25 nov 2024", "—", "tarea-detalle.html"),
    ]),
]

# Nombre y color de cada estado de tarea (los mismos en plan, tareas y detalle).
ESTADO_BADGE = {
    "Completada": ("b-linea", "check"),
    "En curso": ("b-azul", "engranaje"),
    "En revisión": ("b-amarillo", "reloj"),
    "Pendiente": ("b-neutra", "reloj"),
}
# Orden de las columnas del tablero: lo que falta primero, lo hecho al final.
ESTADOS_KANBAN = ["Pendiente", "En curso", "En revisión", "Completada"]

# Las cuatro fases del programa y el avance declarado por emprendimiento.
FASES_META = [
    ("FASE 1", "Ideación y priorización de ideas"),
    ("FASE 2", "Estructuración y ejecución"),
    ("FASE 3", "Consolidación del proceso"),
    ("FASE 4", "Escalamiento"),
]
AVANCE_FASES = {"Sabor y Sabe": [100, 62, 0, 0], "Mochilas Origen": [24, 0, 0, 0]}
# Avance general y fase en curso (los declara el docente; son la firma del plan).
AVANCE_GENERAL = {"Sabor y Sabe": (62, "FASE 2 · Ejecución"),
                  "Mochilas Origen": (24, "FASE 1 · Ideación")}

# Tareas por completar (pendientes y en curso) que resume el Inicio: misma
# fuente que el desplegable de opciones y que la vista de Tareas.
TAREAS_PEND = [
    (t[4], t[0], t[1], t[6])
    for t in TAREAS_EMP[0][2] if t[2] in ("Pendiente", "En curso")
]


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
        ("evento-detalle-startup.html", "18a Estudiante - Detalle evento (Startup Minuto de Dios)",
         evento_detalle_startup),
        ("evento-detalle-capacitacion.html", "18b Estudiante - Detalle evento (Capacitación virtual)",
         evento_detalle_capacitacion),
        ("evento-detalle-asesoria-grupal.html", "18c Estudiante - Detalle evento (Asesoría grupal)",
         evento_detalle_asesoria_grupal),
        ("evento-detalle-showroom.html", "18d Estudiante - Detalle evento (Showroom)",
         evento_detalle_showroom),
        ("perfil.html", "19 Estudiante - Mi perfil", perfil),
        ("configuracion.html", "19b Estudiante - Configuración (editar perfil)", configuracion),
        ("seguimiento-detalle.html", "13b Estudiante - Detalle del seguimiento", seguimiento_detalle),
        ("notificaciones.html", "20 Estudiante - Notificaciones", notificaciones),
    ]
    for i, (arch, tit, fn) in enumerate(p):
        reg("estudiante", arch, tit, fn, i)


# --- 1. Dashboard ------------------------------------------------------------
def dashboard():
    cuerpo = (
        # Mini pestaña superior, estilo notificación: resume las tareas
        # pendientes y lleva a la vista de Tareas al hacer clic.
        '<a class="mini-aviso" href="tareas.html">'
        '<span class="mini-aviso-ico">%s</span>'
        '<div><b>Tienes 3 tareas por completar.</b> La más próxima vence hoy: '
        "la evidencia fotografica del punto de venta.</div>"
        '<span class="mini-aviso-cta">Ver tareas %s</span></a>'
        % (ico("checklist", 18), ico("der", 14))
        + '<div style="height:20px"></div>'
        + callout(
            "Tu cuenta esta <b>Limitada</b>. Ya puedes entrar al sistema, pero el modulo de "
            "<b>Diagnóstico</b> permanece bloqueado hasta que un administrador active tu cuenta.",
            "escudo",
        )
        + '<div style="height:20px"></div>'
        # Cada metrica es un enlace: al pasar el mouse muestra una mini vista
        # previa con lo que hay dentro de esa vista; al hacer clic navega a ella.
        + metricas_enlace([
            ("maleta", "Mi emprendimiento", "1", "activo", 100, "1 registrado",
             "emprendimientos.html", "Mi emprendimiento",
             "Sabor y Sabe: diagnóstico, avance por fase y expediente del negocio."),
            ("target", "Diagnóstico", "Pendiente", "", 0, "",
             "diagnostico.html", "Diagnóstico",
             "Cuestionario de 22 preguntas sobre perfil, problema, propuesta, mercado y capacidad."),
            ("checklist", "Tareas completadas", "3", "de 7", 43, "",
             "tareas.html", "Tareas",
             "Tus 7 tareas del plan, separadas por emprendimiento y por estado."),
            ("chat", "Asesorías realizadas", "3", "", 100, "",
             "asesorias.html", "Asesorías",
             "Historial de asesorías, horarios y estado de confirmación."),
        ])
        + '<div style="height:20px"></div>'
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
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2">'
        + card(
            "Tareas por completar",
            '<div class="lista-def" style="padding:4px 0">'
            + "".join(
                '<div class="def-row"><dt style="flex:0 0 auto">%s</dt>'
                '<dd style="flex:1"><a href="%s">%s</a></dd>'
                '<dd style="flex:0 0 auto">%s</dd></div>'
                % (f, href, d, badge(p, "b-amarillo" if p == "Alta" else "b-linea",
                                     "alerta" if p == "Alta" else "reloj"))
                for f, d, p, href in TAREAS_PEND
            )
            + "</div>"
            + '<div style="height:12px"></div>'
            # Desplegable con las opciones de tareas: cada opción es un enlace a
            # su vista, igual que la campana de notificaciones.
            + '<details class="desplegable"><summary>%s Opciones de tareas</summary>'
            '<div class="desp-lista">%s</div></details>'
            % (ico("checklist", 16), "".join(
                '<a class="desp-item" href="%s">%s<b>%s</b><span>%s</span></a>'
                % (href, ico("alerta" if p == "Alta" else "reloj", 16), d, f)
                for f, d, p, href in TAREAS_PEND)),
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
        + '<div class="grid" style="gap:20px">'
        + card(
            "Movimiento en el plan",
            '<div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap">'
            + circular(d["pct"], "avance", d["fase"])
            + '<div style="flex:1;min-width:300px">'
            + '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px">'
            + "".join(
                '<div style="border:1px solid #bbbbbb;border-radius:8px;padding:12px 14px">'
                '<div style="font-size:13px;color:#162644">%s</div>'
                '<div style="font-size:20px;font-weight:700;color:#051533">%s</div>'
                '<div style="font-size:13px;color:#162644">%s</div></div>'
                % (lbl, val, det)
                for lbl, val, det in d["kpis"]
            )
            + "</div></div></div>",
        )
        + card(
            "Avance por fases",
            progreso_fases(d["fases"]),
            hint="Las fases se habilitan en orden segun el avance del docente asignado",
        )
        + "</div>"
        + '<div class="grid" style="gap:20px">'
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
                    '<div style="font-size:13px;color:#162644">Tu cuenta está en estado '
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
                    '<div style="font-size:13px;color:#162644">Este emprendimiento aún no tiene '
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
        + '<div style="height:20px"></div>'
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
def _avance_fases_emp(nombre):
    """Avance por fase de un emprendimiento (se imprime en el expediente)."""
    filas = ""
    for (cod, desc), p in zip(FASES_META, AVANCE_FASES[nombre]):
        filas += ('<div style="display:flex;align-items:center;gap:10px;padding:6px 0;font-size:13px">'
                  '<i style="width:10px;height:10px;border-radius:2px;background:%s;flex:0 0 10px"></i>'
                  '<span style="flex:1;color:#162644">%s · %s</span>'
                  '<b style="color:#051533">%d%%</b></div>'
                  % (AZUL if p > 0 else GRIS, cod, desc, p))
    return ('<div style="margin-bottom:16px">'
            '<div style="font-size:13px;font-weight:700;color:#051533;margin-bottom:4px">%s</div>'
            "%s</div>" % (nombre, filas))


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
        + '<div style="height:20px"></div>'
        # El expediente que se exporta: avance por fase y el historial del
        # negocio, para que el PDF no sea solo el listado.
        + '<div class="grid g-2">'
        + card("Avance por fase del expediente",
               "".join(_avance_fases_emp(n) for n, _, _ in TAREAS_EMP))
        + card("Historial del expediente", linea_tiempo([
            ("12", "oct", "Emprendimiento registrado",
             "Sabor y Sabe · diagnóstico inicial habilitado.", ""),
            ("03", "sep", "Emprendimiento registrado",
             "Mochilas Origen · a la espera de docente asignado.", ""),
            ("20", "oct", "Plan de trabajo cargado",
             "El docente Carlos Mendoza cargó las cuatro fases de Sabor y Sabe.", ""),
            ("04", "nov", "Asesoría realizada",
             "Se revisó el modelo de negocio y los apuntes de la fase 2.", ""),
            ("08", "nov", "Avance de fase registrado",
             "Se definió el precio de venta final con margen del 35 %.", ""),
        ]))
        + "</div>"
    )
    return shell(R, "emprendimientos", "Mi emprendimiento", cuerpo,
                 migas=["Inicio", "Mi emprendimiento"],
                 sub="Listado de tus emprendimientos y su estado actual.",
                 acciones='<button class="btn btn-secundario" data-accion="exportar-expediente">%s Exportar expediente</button>' % ico("download", 16)
                          + '<a class="btn btn-acento" href="diagnostico.html">%s Crear emprendimiento</a>' % ico("plus", 16))


# --- 4. Detalle del emprendimiento ------------------------------------------
def emprendimiento_detalle():
    # --- Panel: Resumen -----------------------------------------------------
    panel_resumen = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
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
            '<p style="font-size:13px;color:#162644">Sabor y Sabe es un emprendimiento de '
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
        + '<div class="grid" style="gap:20px">'
        + card("Docente asignado", '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
             '<span class="avatar" style="width:44px;height:44px;flex:0 0 44px;font-size:14px">CM</span>'
             '<div><div style="font-weight:600">Carlos Mendoza</div>'
             '<div style="font-size:13px;color:#162644">Docente &middot; Áreas de flipped classroom y e-learning</div>'
             "</div></div>"
             '<a class="btn btn-secundario btn-sm" href="solicitar-asesoria.html" style="width:100%">'
             + ico("chat", 15) + " Solicitar asesoría</a>")
        + card("Acciones disponibles",
               '<div style="display:flex;flex-direction:column;gap:10px">'
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
        + '<div style="height:16px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Estado del diagnóstico", lista_def([
            ("Estado", badge("En progreso", "b-amarillo", "reloj")),
            ("Secciones completadas", "3 de 5"),
            ("Última actualización", "12 de octubre de 2024"),
            ("Responsable", "Tu (estudiante)"),
        ])
            + '<div style="display:flex;gap:10px;margin-top:14px">'
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
        + '<div class="grid" style="gap:20px">'
        + card("Para qué sirve", '<p style="font-size:13px;color:#162644">Tus respuestas se '
               "convierten en la caracterización y la valoración del emprendimiento. Con eso "
               "el docente arma el plan de trabajo y las tareas que verás en las otras "
               "pestañas.</p>")
        + "</div></div>"
    )

    # --- Panel: Plan de trabajo ---------------------------------------------
    panel_plan = (
        callout("El plan de trabajo lo construye el docente que tienes asignado y tu solo "
                "puedes consultar su avance y completar las tareas.", "escudo")
        + '<div style="height:16px"></div>'
        + card("Avance por fase", lista_def([
            ("FASE 1 · Ideación", badge("Completada", "b-azul", "check")),
            ("FASE 2 · Ejecución", badge("En curso", "b-amarillo", "engranaje")),
            ("FASE 3 · Crecimiento", badge("Pendiente", "b-neutra", "reloj")),
            ("FASE 4 · Consolidación", badge("No iniciada", "b-neutra", "reloj")),
        ])
            + '<div style="display:flex;gap:10px;margin-top:14px">'
            '<a class="btn btn-acento" href="plan-trabajo.html">' + ico("layers", 16) + " Abrir plan de trabajo</a>"
            "</div>")
        + card("Tareas del plan",
               '<p style="font-size:13px;color:#162644">Tienes <b>3 tareas activas</b>: '
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
        + '<div style="height:16px"></div>'
        + tabla(["Fecha", "Tipo de registro", "Registrado por"], filas_seg)
        + '<div style="height:12px"></div>'
        + '<a class="btn btn-secundario" href="seguimiento.html">' + ico("eye", 16) + " Ver historial completo</a>"
    )

    # --- Panel: Tareas ------------------------------------------------------
    filas_tar = [
        ["Levantar precios de la competencia", badge("Alta", "b-azul", "alerta"),
         "12 nov 2024", badge("Pendiente", "b-amarillo", "reloj"),
         _a("eye", "Ver detalle", "tarea-detalle.html")],
        ["Subir evidencia fotografica del punto de venta", badge("Media", "b-neutra", "reloj"),
         "15 nov 2024", badge("En revisión", "b-azul", "reloj"),
         _a("eye", "Ver detalle", "tarea-detalle-en-revision.html")],
        ["Definir el margen por producto", badge("Alta", "b-azul", "alerta"),
         "10 nov 2024", badge("Completada", "b-linea", "check"),
         _a("eye", "Ver detalle", "tarea-detalle-completada-precio.html")],
    ]
    panel_tareas = (
        callout("Estas son las tareas activas del plan. Completa las pendientes y sube la "
                "evidencia para que el docente las revise.", "doc")
        + '<div style="height:16px"></div>'
        + tabla(["Tarea", "Prioridad", "Fecha límite", "Estado", "@ACC"], filas_tar)
        + '<div style="height:12px"></div>'
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
        + '<div style="height:16px"></div>'
        + tabla(["Fecha", "Motivo", "Docente", "Estado"], filas_ase)
        + '<div style="height:12px"></div>'
        + '<div style="display:flex;gap:10px">'
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
        + '<div style="height:20px"></div>'
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
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(
            "Datos que puedes editar",
            campo("Nombre del emprendimiento", valor="Sabor y Sabe", req=True,
                  ayuda="Entre 4 y 80 caracteres.")
            + campo("Descripción", alto=True,
                    valor="Emprendimiento de alimentos y bebidas que prepara y comercializa "
                          "snacks artesanales a base de frutos secos y granola, con ventas en "
                          "el campus y por pedido a domicilio dentro del municipio.",
                    ph="Describe que vendes, a quien y como lo haces")
            + '<div class="grid g-2" style="gap:0 16px">'
            + campo("Instagram", valor="@saborysabe.md", ph="@usuario")
            + campo("WhatsApp Business", valor="300 555 4412", tipo="tel")
            + "</div>"
            + campo("Tienda propia (sitio web)", valor="", ph="https://")
            + '<div style="display:flex;gap:10px;justify-content:flex-end;padding-top:8px">'
            + '<a class="btn btn-secundario" href="emprendimiento-detalle.html">Cancelar</a>'
            + '<button class="btn btn-primario" data-accion="guardar-emprendimiento">%s Guardar cambios</button></div>' % ico("check", 16),
        )
        + "</div>"
        + '<div class="grid" style="gap:20px">'
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
CONTADOR_DIAG = ('<span data-contador-diagnostico style="font-size:13px;color:#162644">'
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
            # Selector por tarjetas: se elige una opción y su descripción queda
            # visible bajo el título (nada de escribirla a mano).
            '<div class="campo"><label>Qué tipo de emprendimiento es?'
            '<span class="req">*</span></label>'
            + opciones_card("tipo_emprendimiento", [
                ("Pequeño", "Opera con recursos propios y un alcance local."),
                ("Escalable", "Puede crecer rápido y replicarse en otros mercados."),
                ("Social", "Su objetivo principal es generar impacto social."),
                ("Ambiental", "Reduce el impacto ambiental en toda su operación."),
                ("Cultural", "Valoriza la identidad y el patrimonio local."),
                ("Intraemprendimiento", "Innovación dentro de una organización que ya existe."),
            ])
            + "</div>",
            '<div class="campo"><label>A qué sector productivo pertenece?'
            '<span class="req">*</span></label>'
            + opciones_card("sector_productivo", [
                ("Sector primario", "Extracción y materias primas."),
                ("Sector secundario", "Industria y transformación."),
                ("Sector terciario", "Servicios y comercio."),
                ("Sector cuaternario", "Tecnología, información y conocimiento."),
                ("Sector quinario", "Servicios sociales, bienestar e impacto."),
            ], seleccion=1)
            + "</div>",
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
            campo("Quién es tu cliente ideal (perfil)?", valor="Estudiantes de 18-25 que cuidan su alimentacion",
                  req=True),
            campo("Cuántos clientes potenciales estimas?", valor="Unos 400 estudiantes del campus", req=True),
            select("Cuál es tu estrategia de precio?",
                   ["Economía (bajo costo)", "Valor medio", "Premium"], valor="Valor medio", req=True),
            campo("Qué canales usarás para llegarles?", valor="Punto de venta en cafeteria y WhatsApp", req=True),
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
                '<span style="font-size:13px;color:#162644">%s</span>'
                '<div style="display:flex;gap:10px">'
                '<button class="btn btn-secundario" data-accion="guardar-borrador">Guardar borrador</button>'
                '%s%s</div></div></div></div>'
                % (i, oculta, i + 1, n, titulo, bloques, CONTADOR_DIAG, anterior, siguiente))

    paneles = "".join(panel(i, t, "".join(b)) for i, (t, b) in enumerate(preguntas))
    cuerpo = (
        steps([s[0].split(" y ")[0] for s in SECCIONES], 0)
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">' + paneles + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Cómo va el cuestionario",
               barras_h("", "", ["Perfil", "Problema", "Propuesta", "Mercado", "Capacidad"],
                        [100, 0, 0, 0, 0], maximo=100, unidad="%"),
               hint="5 secciones")
        + card("Puedes pausar cuando quieras",
               '<div style="font-size:13px;color:#162644">Tu respuesta se guarda como '
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
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Comportamiento entrepreneurial", barras_h(
            "", "", ["Visión", "Creatividad", "Resiliencia", "Liderazgo", "Trabajo en equipo",
                     "Capacidad de decisión"],
            [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
        + card("Distribución de las respuestas", donut(
            "", "", [("Problema claro", 82, AZUL), ("Propuesta de valor", 74, AZUL),
                     ("Mercado definido", 61, AZUL), ("Viabilidad financiera", 55, AMAR)], "% respuestas"))
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Recomendaciones del docente",
               '<div class="lista-def" style="padding:4px 0">'
               + "".join(
                   '<div style="display:flex;gap:10px;padding:11px 0;border-bottom:1px solid #bbbbbb">'
                   '<span style="color:#004a93;flex:0 0 18px">%s</span>'
                   '<div style="font-size:13px;color:#051533">%s</div></div>' % (ico("alerta", 16), t)
                   for t in [
                       "Definir con más precisión el canal de venta digital.",
                       "Separar el presupuesto de insumos del presupuesto de publicidad.",
                       "Registrar el costo fijo mensual para calcular el punto de equilibrio.",
                   ]
               )
               + "</div>")
        + card("Puntaje por dimensión",
               '<div style="font-size:13px;color:#162644">Este resultado es una foto del momento. '
               "Volveras a responder el diagnóstico al cierre de cada fase.</div>")
        + "</div></div>"
    )
    return shell(R, "diagnostico", "Resultado del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnóstico", "Resultado"],
                 sub="Puntaje, comportamiento entrepreneurial y recomendaciones del docente.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s Descargar PDF</button>' % ico("download", 16)
                          + '<button class="btn btn-primario">%s Volver a responder</button>' % ico("clipboard", 16))


# --- 8. Plan de trabajo ------------------------------------------------------
def _conteos_estado(tareas):
    """Cuántas tareas hay en cada estado (alimenta la gráfica del plan)."""
    return [sum(1 for t in tareas if t[2] == e) for e in ESTADOS_KANBAN]


def _fila_tarea(t):
    """Fila de una tarea dentro de una fase del plan; navega a su detalle."""
    tit, pri, est, fase, lim, env, href = t
    col = ESTADO_BADGE[est]
    return (
        '<a class="fila-tarea" href="%s" title="Abrir el detalle de la tarea">'
        '<span class="fila-ico">%s</span>'
        '<span class="fila-txt">%s'
        '<span class="fila-sub">Fecha límite %s &middot; Envío %s</span></span>%s</a>'
        % (href, ico("checklist", 16), tit, lim, env, badge(est, col[0], col[1]))
    )


def _bloques_plan(nombre):
    """Plan de trabajo de un emprendimiento: las cuatro fases y su resumen.

    Las tareas salen de TAREAS_EMP —la misma fuente que la vista de Tareas— y
    cada una navega a su detalle, así que el plan y el tablero nunca se
    contradicen. Cada fase se abre desde su título.
    """
    tareas = [e[2] for e in TAREAS_EMP if e[0] == nombre][0]
    bloques = ""
    for i, (cod, desc) in enumerate(FASES_META, start=1):
        pct = AVANCE_FASES[nombre][i - 1]
        propias = [t for t in tareas if t[3] == i]
        filas = "".join(_fila_tarea(t) for t in propias) if propias else (
            '<div class="nota-foot" style="padding:10px 0">'
            "Aún no hay tareas asignadas en esta fase.</div>")
        cab = AMAR if 0 < pct < 100 else (AZUL if pct == 100 else GRIS)
        bloques += (
            '<div class="card"><div class="card-head">'
            '<span style="background:%s;color:%s;border-radius:6px;padding:3px 9px;'
            'font-size:13px;font-weight:700;letter-spacing:.04em">%s</span>'
            '<h3><a class="fase-link" href="tareas.html" '
            'title="Ver las tareas de la fase">%s</a></h3>'
            '<span style="font-weight:700;font-size:13px;color:#051533">%d%%</span></div>'
            '<div class="card-body sin-pad"><div style="padding:6px 20px 14px">%s</div>'
            '<div style="padding:0 20px 16px"><div class="barra"><span style="width:%d%%;'
            'background:%s"></span></div></div></div></div>'
            % (cab, "#051533" if cab == AMAR else "#ffffff", cod, desc, pct, filas, pct, cab)
        )
    hechas = sum(1 for t in tareas if t[2] == "Completada")
    pct, fase = AVANCE_GENERAL[nombre]
    conteos = _conteos_estado(tareas)
    return (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">' + bloques + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Avance general", '<div style="text-align:center">'
             + circular(pct, "avance", fase)
             + '<p style="font-size:13px;color:#162644;margin-top:8px">'
               "%d de %d tareas completadas.</p></div>" % (hechas, len(tareas)))
        + card("Tareas por estado", barras_h(
             "", "Distribución de las tareas del plan", ESTADOS_KANBAN, conteos,
             maximo=max(conteos + [1]), unidad=" tareas"))
        + "</div></div>"
    )


def plan_trabajo():
    paneles = [(n, pid) for n, pid, _ in TAREAS_EMP]
    cuerpo = (
        callout("El plan de trabajo lo construye el docente que tienes asignado y tu solo "
                "puedes consultar su avance y completar las tareas.", "escudo")
        + '<div style="height:20px"></div>'
        + tabs_paneles(paneles)
        + '<div style="height:20px"></div>'
        + "".join(
            '<div data-panel-nombre="%s"%s>%s</div>'
            % (pid, "" if i == 0 else " hidden", _bloques_plan(n))
            for i, (n, pid) in enumerate(paneles)
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
        ("08 nov 2024", "Comentario", "Se recuerda cargar la evidencia fotografica de cada venta "
         "en las tareas asignadas.", "Carlos Mendoza"),
        ("12 nov 2024", "Avance de fase", "Se define el precio de venta final con margen "
         "del 35 por ciento.", "Carlos Mendoza"),
    ]:
        filas.append([f, badge(est, "b-azul" if "Avance" in est else "b-neutra",
                               "trend" if "Avance" in est else "chat"), desc, doc,
                      _acc(_a("eye", "Ver detalle", "seguimiento-detalle.html"))])
    cuerpo = (
        callout("El seguimiento es de <b>solo lectura</b>. Los registros los crea el docente o el "
                "administrador segun las reglas de gestión.", "escudo")
        + '<div style="height:20px"></div>'
        + tabla(["Fecha", "Tipo de registro", "Título", "Registrado por", "@ACC"], filas)
        + paginas(1, 4, 4)
        + '<div style="height:20px"></div>'
        + card("Frecuencia con que te acompaña el docente",
               barras_h("", "", ["FASE 1 · Oct 2024", "FASE 2 · Nov 2024"],
                        [4, 3], maximo=6, unidad=" registros"))
    )
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Historial de los acompañamientos registrados por tu docente.")


def seguimiento_detalle():
    """Detalle de un registro del historial de seguimiento (solo lectura).

    Se abre desde la columna de acciones del historial; conserva el mismo tono
    de solo lectura y muestra el avance del emprendimiento en ese momento.
    """
    cuerpo = (
        callout("Este registro lo creó el docente que tienes asignado. El seguimiento "
                "es de <b>solo lectura</b> para el estudiante.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Datos del registro", lista_def([
            ("Título", "Se define el precio de venta final"),
            ("Tipo de registro", badge("Avance de fase", "b-azul", "trend")),
            ("Fecha", "12 de noviembre de 2024"),
            ("Fase", "FASE 2 · Estructuración y ejecución"),
            ("Emprendimiento", "Sabor y Sabe"),
            ("Registrado por", "Carlos Mendoza"),
        ]))
        + card("Descripción",
               '<p style="font-size:13px;color:#162644">Se define el precio de venta final '
               "de cada producto con base en el análisis de costos y el margen acordado. El "
               "precio queda sustentado en la cartelera del punto de venta.</p>")
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Avance al momento del registro",
               '<div style="text-align:center">'
               + circular(62, "avance", "FASE 2 · Ejecución") + "</div>")
        + card("Cómo leer el seguimiento",
               '<div style="font-size:13px;color:#162644">Cada registro documenta un avance '
               "concreto del emprendimiento. La frecuencia de acompañamiento se calcula sobre "
               "estos registros y alimenta el estado de seguimiento.</div>")
        + "</div></div>"
    )
    return shell(R, "seguimiento", "Detalle del seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Detalle del registro"],
                 sub="Registro del acompañamiento del docente (solo lectura).",
                 acciones='<a class="btn btn-secundario" href="seguimiento.html">%s Volver</a>' % ico("izq", 16))


# --- 10. Tareas (lista) ------------------------------------------------------
# Rótulo de las columnas del tablero y notas de las tareas ya calificadas.
KANBAN_TITULO = {"Pendiente": "Pendientes", "En curso": "En curso",
                 "En revisión": "En revisión", "Completada": "Completadas"}
NOTAS = {"Definir clientes potenciales": 92,
         "Validar la solución con 10 usuarios": 85,
         "Definir el precio de venta final": 90}


def _kanban_emp(nombre):
    """Tablero de tareas de un emprendimiento: una columna por estado.

    Los estados son los mismos del plan de trabajo (pendiente, en curso, en
    revisión y completada), así que el plan y el tablero siempre coinciden.
    """
    tareas = [e[2] for e in TAREAS_EMP if e[0] == nombre][0]
    columnas = []
    for est in ESTADOS_KANBAN:
        tarjetas = []
        for tit, pri, _, fase, lim, env, href in [t for t in tareas if t[2] == est]:
            if est == "Completada":
                meta = "Enviada el %s" % env
                pie = badge("Calificada %d" % NOTAS.get(tit, 0), "b-linea", "check")
            elif est == "En revisión":
                meta = "Enviada el %s · esperando calificación" % env
                pie = badge("En revisión", "b-amarillo", "reloj")
            elif est == "En curso":
                meta = "Vence %s" % lim
                pie = badge("En curso", "b-azul", "engranaje")
            else:
                meta = "Vence %s" % lim
                pie = badge("Alta" if pri == "Alta" else "Media",
                            "b-azul" if pri == "Alta" else "b-neutra",
                            "alerta" if pri == "Alta" else "reloj")
            tarjetas.append((tit, "Fase %d · %s" % (fase, meta), pie,
                             '<a class="btn btn-sm btn-secundario" href="%s">Abrir</a>' % href))
        columnas.append((KANBAN_TITULO[est], tarjetas))
    return kanban(columnas)


def tareas():
    """Tablero por emprendimiento y por estado: qué está haciendo y qué falta.

    Cada emprendimiento tiene su propia pestaña, igual que Estado de seguimiento
    y Plan de trabajo, para no mezclar las tareas de dos negocios.
    """
    paneles = [(n, pid) for n, pid, _ in TAREAS_EMP]
    partes = []
    for i, (n, pid) in enumerate(paneles):
        tareas_emp = [e[2] for e in TAREAS_EMP if e[0] == n][0]
        total = len(tareas_emp) or 1
        conteos = _conteos_estado(tareas_emp)
        por = conteos[0] + conteos[1]

        def pct(k):
            return int(round(k * 100.0 / total))

        partes.append(
            '<div data-panel-nombre="%s"%s>%s</div>'
            % (pid, "" if i == 0 else " hidden",
               metricas([
                   ("checklist", "Tareas asignadas", str(total), "en total", 100, ""),
                   ("reloj", "Por completar", str(por), "", pct(por), ""),
                   ("alerta", "En revisión", str(conteos[2]), "", pct(conteos[2]), ""),
                   ("check", "Completadas", str(conteos[3]), "", pct(conteos[3]), ""),
               ])
               + '<div style="height:20px"></div>'
               + _kanban_emp(n))
        )
    cuerpo = (
        tabs_paneles(paneles)
        + '<div style="height:20px"></div>'
        + "".join(partes)
        + '<p class="nota-foot">Arrastra no aplica: cada tarea se mueve cuando el docente '
          "la califica.</p>"
    )
    return shell(R, "tareas", "Mis tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Tus tareas por emprendimiento y por estado.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s Descargar reporte</button>' % ico("download", 16))


# --- 11. Detalle de tarea ----------------------------------------------------
def tarea_detalle():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Subir evidencia fotografica del punto de venta",
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", "12 de noviembre de 2024"),
                   ("Fecha de envío", badge("Pendiente de envío", "b-neutra", "reloj")),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("Pendiente", "b-amarillo", "reloj")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p style="font-size:13px;color:#162644">Adjunta al menos tres fotografias del '
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
        + '<div class="grid" style="gap:20px">'
        + card("Marcar como completada", '<p style="font-size:13px;color:#162644">'
             "Solo puedes marcar la tarea como completada si adjuntaste al menos un archivo "
             "de evidencia.</p>"
             '<button class="btn btn-acento" style="width:100%%;margin-top:14px" '
             'data-accion="marcar-completada" disabled>'
             "%s Marcar como completada</button>"
             '<div class="nota-foot">El botón se habilita cuando exista evidencia adjunta.</div>'
             % ico("check", 16))
        + card("Comentarios del docente",
               _comentario("Recuerda que las fotos deben incluir la fecha de toma para "
                           "validar la evidencia.", "09 nov 2024"))
        + "</div></div>"
    )
    return shell(R, "tareas", "Subir evidencia fotografica del punto de venta", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Detalle de la tarea asignada.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s '
                          'Descargar ficha</button>'
                          ' <a class="btn btn-secundario" href="tareas.html">%s Volver</a>'
                          % (ico("download", 16), ico("izq", 16)))


def _comentario(txt, fecha, autor="Carlos Mendoza", rol="Docente", ini="CM"):
    """Comentario del docente: avatar, nombre, rol, fecha y el texto."""
    return (
        '<div class="coment"><span class="avatar">%s</span>'
        '<div style="flex:1;min-width:0">'
        '<div class="coment-cab"><b>%s</b><span class="who-role">%s</span>'
        "<time>%s</time></div>"
        '<div class="coment-txt">%s</div></div></div>'
        % (ini, autor, rol, fecha, txt)
    )


def _puntualidad(retraso):
    """Badge de puntualidad; retraso = días de retraso (0 = a tiempo)."""
    if retraso > 0:
        return badge("Entregada %d día%s tarde" % (retraso, "" if retraso == 1 else "s"),
                     "b-amarillo", "reloj")
    return badge("Entregada a tiempo", "b-linea", "check")


def _archivos_cargados(archivos):
    """Lista de evidencia ya cargada (solo lectura): sin opción de adjuntar ni quitar."""
    filas = ""
    for nombre, tam, dia in archivos:
        filas += (('<div class="def-row">' + ico("clip", 16)
                   + '<dd style="color:#051533"><b>%s</b><br>'
                     '<span style="font-size:13px;color:#162644">%s · %s</span></dd>'
                   + '<dt style="flex:0 0 auto">%s</dt></div>')
                  % (nombre, tam, dia, badge("Enviado", "b-neutra", "check")))
    return '<div class="lista-def" style="padding:4px 0">%s</div>' % filas


def tarea_detalle_en_revision():
    """Tarea EN REVISION: evidencia ya enviada y sin opciones de carga."""
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Levantar el modelo de negocio",
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", "04 de noviembre de 2024"),
                   ("Fecha de envío", "04 de noviembre de 2024 " + _puntualidad(0)),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("En revisión", "b-azul", "reloj")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p style="font-size:13px;color:#162644">Elabora el lienzo del modelo de negocio '
                 "de Sabor y Sabe. Adjunta el lienzo diligenciado y los apuntes de tu docente.</p>")
        + card("Evidencia adjunta",
               _archivos_cargados([
                   ("lienzo-modelo-negocio.pdf", "1.4 MB", "04 nov 2024"),
                   ("apuntes-revision.jpg", "2.1 MB", "04 nov 2024"),
                   ("foto-tablero.jpg", "3.2 MB", "04 nov 2024"),
               ]),
               hint='<span>3 archivos enviados</span>')
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("En revisión por el docente",
               '<p style="font-size:13px;color:#162644">Tu evidencia fue enviada el '
               "<b>04 de noviembre de 2024</b> y ya no puede modificarse. El docente la "
               "revisara y te asignara una calificación.</p>"
               '<div class="nota-foot">La tarea quedara en Completadas cuando el docente la califique.</div>')
        + card("Comentarios del docente",
               _comentario("Tu evidencia está en validación. Recuerda que debe incluir "
                           "la fecha de toma.", "04 nov 2024"))
        + "</div></div>"
    )
    return shell(R, "tareas", "Levantar el modelo de negocio", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Tarea enviada a revisión. La evidencia ya esta cargada.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s '
                          'Descargar ficha</button>'
                          ' <a class="btn btn-secundario" href="tareas.html">%s Volver</a>'
                          % (ico("download", 16), ico("izq", 16)))


def _tarea_completada(titulo, nota, fecha_limite, fecha_envio, retraso, fecha_coment,
                      descripcion, archivos, comentario):
    """Detalle de una tarea COMPLETADA: calificación, evidencia cargada y solo lectura."""
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(titulo,
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha límite", fecha_limite),
                   ("Fecha de envío", fecha_envio + " " + _puntualidad(retraso)),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("Completada · Calificada %d" % nota, "b-linea", "check")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripción de la tarea</h3>'
                 '<p style="font-size:13px;color:#162644">%s</p>' % descripcion)
        + card("Evidencia adjunta",
               _archivos_cargados(archivos),
               hint='<span>%d archivos enviados</span>' % len(archivos))
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Calificación",
               circular(nota, "Calificación", "Completada el %s" % fecha_coment)
               + '<p style="font-size:13px;color:#162644;margin-top:8px">'
                 "<b>Felicitaciones.</b> Esta tarea fue calificada y entregada y ya no puede "
                 "modificarse.</p>")
        + card("Comentarios del docente", _comentario(comentario, fecha_coment))
        + "</div></div>"
    )
    return shell(R, "tareas", titulo, cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Tarea completada y calificada por el docente.",
                 acciones='<button class="btn btn-secundario" data-accion="descargar">%s '
                          'Descargar ficha</button>'
                          ' <a class="btn btn-secundario" href="tareas.html">%s Volver</a>'
                          % (ico("download", 16), ico("izq", 16)))


def tarea_detalle_completada_precio():
    return _tarea_completada(
        "Definir el precio de venta final", 90,
        "30 de octubre de 2024", "08 de noviembre de 2024", 9, "08 nov 2024",
        "Define el precio de venta final de cada producto con base en el análisis de costos "
        "y el margen acordado con tu docente.",
        [("analisis-costos.pdf", "1.2 MB", "07 nov 2024"),
         ("tabla-precios.xlsx", "840 KB", "07 nov 2024"),
         ("foto-cartelera.jpg", "2.6 MB", "08 nov 2024")],
        "Excelente análisis de costos. El precio final queda sustentado con el margen esperado.")


def tarea_detalle_completada_usuarios():
    return _tarea_completada(
        "Validar la solución con 10 usuarios", 85,
        "10 de noviembre de 2024", "01 de noviembre de 2024", 0, "01 nov 2024",
        "Realiza la validación de la solución con al menos 10 usuarios y adjunta el registro "
        "de sus respuestas y comentarios.",
        [("registro-validaciones.pdf", "1.8 MB", "31 oct 2024"),
         ("tabla-respuestas.xlsx", "620 KB", "01 nov 2024")],
        "Validación completa. Ajusta el horario de toma de datos para la siguiente ronda.")


def tarea_detalle_completada_clientes():
    return _tarea_completada(
        "Definir clientes potenciales", 92,
        "05 de noviembre de 2024", "28 de octubre de 2024", 0, "28 oct 2024",
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
        + '<div style="height:20px"></div>'
        + metricas([
            ("maleta", "Emprendimientos", "2", "activos", 100, "Sabor y Sabe · Mochilas Origen"),
            ("chat", "Asesorías realizadas", "3", "", 100, ""),
            ("reloj", "Programadas", "3", "", 100, ""),
            ("check", "Confirmadas", "2", "", 67, ""),
        ])
        + '<div style="height:20px"></div>'
        + card("Próximas asesorías", linea_tiempo([
            ("14", "nov", "Asesoría con Laura Sanchez",
             "14:30 - 15:30 · Presencial · Pendiente de confirmar · Mochilas Origen",
             '<div style="margin-top:10px">'
             + badge("Pendiente de confirmar", "b-amarillo", "reloj")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("19", "nov", "Asesoría con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Confirmada · Sabor y Sabe",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("12", "nov", "Asesoría con Carlos Mendoza",
             "10:00 - 11:00 · Virtual · Confirmada · Sabor y Sabe",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
        ]), sin_pad=False)
        + '<div style="height:20px"></div>'
        + card("Asesorías realizadas", linea_tiempo([
            ("04", "nov", "Asesoría con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Realizada · Sabor y Sabe",
             '<div style="margin-top:10px">'
             + badge("Realizada", "b-linea", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-acta\">Ver acta</button></div>"),
        ]))
    )
    return shell(R, "asesorias", "Mis asesorías", cuerpo,
                 migas=["Inicio", "Asesorías"],
                 sub="Historial y próximas asesorías de tus emprendimientos.",
                 acciones='<a class="btn btn-acento" href="solicitar-asesoria.html">%s Solicitar asesoría</a>'
                          % ico("plus", 16))


# --- 13. Solicitar asesoria --------------------------------------------------
def solicitar_asesoria():
    cuerpo = (
        callout("Tu solicitud enviara al docente asignado. <b>No puedes elegir libremente el "
                "docente ni el horario</b>: el docente o el administrador confirmaran la fecha.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(
            "Datos de la solicitud",
            select("Emprendimiento", ["Sabor y Sabe"], req=True)
            + campo("Docente asignado", valor="Carlos Mendoza",
                    bloqueo="El docente se asigna segun las reglas del programa, no por el estudiante.")
            + '<div class="grid g-2" style="gap:0 16px">'
            + campo("Fecha preferida", tipo="date", ph="2024-11-20", req=True,
                    ayuda="Es una preferencia. La fecha final la confirma el docente.")
            + campo("Hora preferida", tipo="time", valor="10:00", req=True,
                    ayuda="Propuesta; el docente ajusta si lo necesita.")
            + "</div>"
            + campo("Temas a tratar", alto=True,
                    ph="Describe los temas que quieres tratar en la asesoría",
                    ayuda="Mientras más concreto, mejor podremos preparar la sesión.")
            + '<div class="divisor"></div>'
            + '<div style="display:flex;justify-content:flex-end;gap:10px">'
            + '<a class="btn btn-secundario" href="asesorias.html">Cancelar</a>'
            + '<button class="btn btn-acento" data-accion="enviar-solicitud">%s Enviar solicitud</button></div>' % ico("enviar", 16),
        )
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Cómo funciona",
               '<div class="lista-def" style="padding:4px 0">'
               + "".join(
                   '<div style="display:flex;gap:10px;padding:11px 0;border-bottom:1px solid #bbbbbb">'
                   '<span style="flex:0 0 20px;width:20px;height:20px;border-radius:999px;'
                   'background:%s;color:%s;display:flex;align-items:center;justify-content:center;'
                   'font-size:13px;font-weight:700">%d</span>'
                   '<span style="font-size:13px;color:#051533">%s</span></div>'
                   % (AZUL, "#ffffff", i + 1, t)
                   for i, t in enumerate([
                       "Envias la solicitud con tus temas.",
                       "El docente recibe la notificación y responde.",
                       "Se confirma la fecha y la modalidad.",
                       "Asistis y la asesoría queda registrada.",
                   ])
               )
               + "</div>")
        + "</div></div>"
    )
    return shell(
        R, "asesorias", "Solicitar asesoría", cuerpo,
        migas=["Inicio", "Asesorías", "Solicitar"],
        sub="Registra tu solicitud. El docente confirmara fecha y modalidad.",
        acciones='<a class="btn btn-secundario" href="asesorias.html">%s Volver</a>' % ico("izq", 16),
    )


# --- 14. Eventos -------------------------------------------------------------
def eventos():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Próximos eventos", tabla(
            ["Evento", "Tipo", "Fecha y hora", "Modalidad", "Organizador", "@ACC"],
            [['<b>Startup Minuto de Dios</b>', "Conferencia",
              "21 nov 2024, 08:00", "Presencial", "Dirección Académica",
              _acc(_a("eye", "Ver detalle", "evento-detalle-startup.html"),
                   _b("calendar", "Inscribirme"))],
             ['<b>Capacitación en modelado de negocios</b>', "Taller",
              "21 nov 2024, 14:00", "Virtual", "Coordinación Académica",
              _acc(_a("eye", "Ver detalle", "evento-detalle-capacitacion.html"),
                   _b("calendar", "Inscribirme"))],
             ['<b>Asesoría grupal de empleabilidad</b>', "Asesoría",
              "26 nov 2024, 10:00", "Presencial", "Bienestar Estudiantil",
              _acc(_a("eye", "Ver detalle", "evento-detalle-asesoria-grupal.html"),
                   _b("calendar", "Inscribirme"))],
             ['<b>Showroom de emprendimientos</b>', "Muestra",
              "02 dic 2024, 09:00", "Presencial", "Dirección Académica",
              _acc(_a("eye", "Ver detalle", "evento-detalle-showroom.html"),
                   _b("calendar", "Inscribirme"))]],
            id="tabla-proximos"))
        + '<div data-listado-inscritos>'
        + card("Eventos en los que ya estas inscrito", tabla(
            ["Evento", "Fecha y hora", "Modalidad", "@ACC"],
            [['<b>Conferencia: Claves del emprendimiento digital</b>', "15 nov 2024, 08:00",
              "Virtual", badge("Inscrito", "b-linea", "check")]],
            id="tabla-inscritos")) + "</div>"
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Calendario de noviembre",
               '<div style="border:1px solid #bbbbbb;border-radius:8px;overflow:hidden">'
               + _calendario("noviembre", 2024)
               + "</div>")
        + card("Cómo inscribirte",
               '<div style="font-size:13px;color:#162644">Abre el detalle de un evento para ver '
               "en qué consiste; al inscribirte, aparece en tu panel y recibes recordatorio el día "
               "anterior. Si el evento es <b>virtual</b>, el enlace de acceso se habilita después "
               "de inscribirte.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Eventos, talleres y asesorías de la institución.")


def _evento_detalle(evento, fecha, modalidad, organizador, lugar, cupos, consiste,
                    extra_html="", virtual=False):
    """Detalle de un evento: en qué consiste, los datos y la inscripción.

    Si el evento es virtual, el enlace de acceso empieza oculto y se muestra al
    inscribirse (misma logica que el resto de accesos virtuales del sistema).
    """
    datos = lista_def([
        ("Fecha y hora", fecha),
        ("Modalidad", badge(modalidad, "b-azul" if modalidad == "Virtual" else "b-neutra",
                            "play" if modalidad == "Virtual" else "")),
        ("Lugar", lugar),
        ("Organiza", organizador),
        ("Cupos disponibles", cupos),
    ])
    acceso = ""
    if virtual:
        acceso = (
            '<div id="acceso-virtual" hidden>'
            + card("Acceso al evento virtual",
                   lista_def([
                       ("Enlace", '<a href="https://meet.minutodedios.edu.co/capacitacion-modelado">'
                                  "meet.minutodedios.edu.co/capacitacion-modelado</a>"),
                       ("ID de la reunión", "482 913 776"),
                       ("Requisitos", "Conexión estable y audífonos."),
                   ]),
                   hint="<span>Visible después de inscribirte</span>")
            + "</div>"
        )
    cuerpo = (
        callout("En qué consiste: " + consiste, "libro")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(evento, datos + '<div class="divisor"></div>' + extra_html,
               accion='<button class="btn btn-acento btn-sm" data-accion="inscribirse">%s '
                      "Inscribirme</button>" % ico("calendar", 15))
        + acceso
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Después de inscribirte",
               '<div style="font-size:13px;color:#162644">El evento aparecerá en tu panel y '
               "recibirás un recordatorio el día anterior. Puedes cancelar tu inscripción desde "
               "este mismo detalle mientras el evento no haya comenzado.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", evento, cuerpo,
                 migas=["Inicio", "Eventos", evento],
                 sub="Detalle del evento y su inscripción.",
                 acciones='<a class="btn btn-secundario" href="eventos.html">%s Volver</a>'
                          % ico("izq", 16))


def evento_detalle_startup():
    return _evento_detalle(
        "Startup Minuto de Dios", "21 nov 2024, 08:00 - 12:00", "Presencial",
        "Dirección Académica", "Auditorio principal, sede Norte", "40 cupos",
        "una conferencia para presentar la ruta del programa Startup Minuto de Dios, los "
        "criterios de evaluación y los testimonios de emprendimientos que ya pasaron por el "
        "proceso. Al final hay un espacio de preguntas con la dirección académica.")


def evento_detalle_capacitacion():
    return _evento_detalle(
        "Capacitación en modelado de negocios", "21 nov 2024, 14:00 - 16:30", "Virtual",
        "Coordinación Académica", "Sala virtual institucional", "120 cupos",
        "un taller virtual para construir el modelo de negocio (clientes, propuesta de valor, "
        "canales e ingresos) con ejercicios guiados sobre tu propio emprendimiento.",
        virtual=True)


def evento_detalle_asesoria_grupal():
    return _evento_detalle(
        "Asesoría grupal de empleabilidad", "26 nov 2024, 10:00 - 11:30", "Presencial",
        "Bienestar Estudiantil", "Sala de reuniones 204", "25 cupos",
        "una asesoría en grupo sobre empleabilidad y emprendimiento: cómo presentar tu proyecto, "
        "armar tu hoja de vida y preparar una entrevista.", 
        extra_html=steps(["Inscríbete en el evento.",
                          "Lleva tu proyecto y tu hoja de vida.",
                          "Participa y recibe la retroalimentación del grupo.",
                          "Recibe el acta de participación."]))


def evento_detalle_showroom():
    return _evento_detalle(
        "Showroom de emprendimientos", "02 dic 2024, 09:00 - 15:00", "Presencial",
        "Dirección Académica", "Plaza central, sede Norte", "60 cupos",
        "una muestra abierta donde cada estudiante presenta su emprendimiento a visitantes y "
        "jurados. Habrá un espacio asignado por emprendimiento y una rúbrica de evaluación.",
        extra_html='<div class="nota-foot">El montaje del stand está a cargo de cada '
                   "emprendimiento; la institución entrega la mesa y la señalización.</div>")


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
def _tarjeta_emp(nombre, tareas):
    """Tarjeta de un emprendimiento dentro del perfil (enlaza a su detalle)."""
    pct, fase = AVANCE_GENERAL[nombre]
    hechas = sum(1 for t in tareas if t[2] == "Completada")
    return (
        '<a class="card metrica perfil-repo" href="emprendimiento-detalle.html">'
        '<div class="metrica-top"><span class="metrica-ico">%s</span>'
        '<div><div class="metrica-lbl">%s</div>'
        '<div class="metrica-val" style="font-size:16px">%s</div></div></div>'
        '<p style="font-size:13px;color:#162644;margin-top:8px">%s</p></a>'
        % (ico("maleta", 18), nombre, "%d%% · %s" % (pct, fase),
           "%d de %d tareas completadas en el plan." % (hechas, len(tareas)))
    )


def perfil():
    """Perfil del estudiante: sus datos basicos y sus emprendimientos.

    Cabecera con foto y datos arriba, los emprendimientos abajo y un boton para
    editar que lleva a Configuracion (alli se cambian los datos y la contraseña).
    """
    cuerpo = (
        '<div class="card"><div class="card-body">'
        '<div class="perfil-cab">'
        '<div class="perfil-foto"><span>ML</span></div>'
        '<div class="perfil-datos">'
        '<h2 class="perfil-nombre">Mariana Lopez Herrera</h2>'
        '<div class="perfil-usuario">mariana.lopez@minutodedios.edu.co &middot; '
        "Número de estudiante 2024105678</div>"
        '<p class="perfil-bio">Estudiante de Ingeniería Industrial (quinto semestre), modalidad '
        "presencial, sede Norte. Emprendedora a cargo de Sabor y Sabe y Mochilas Origen dentro "
        "del programa Startup Minuto de Dios.</p>"
        '<div class="perfil-meta">'
        '<span>%s ESTUDIANTE</span>'
        '<span>%s Cúcuta, Norte de Santander</span>'
        '<span>%s 2 emprendimientos activos</span>'
        "</div></div>"
        '<div class="perfil-acciones">'
        '<a class="btn btn-secundario" href="configuracion.html">%s Editar perfil</a>'
        "</div></div></div></div>"
        % (ico("user", 15), ico("home", 15), ico("maleta", 15), ico("edit", 15))
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Mis emprendimientos",
               '<div class="grid g-2">'
               + "".join(_tarjeta_emp(n, t) for n, _, t in TAREAS_EMP)
               + "</div>")
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Estado de la cuenta", lista_def([
            ("Estado", badge("Limitado", "b-amarillo", "lock")),
            ("Emprendimientos", "2"),
            ("Tareas por completar", str(len(TAREAS_PEND))),
            ("Fecha de registro", "12 oct 2024"),
        ]),
            accion='<button class="btn btn-secundario btn-sm" data-accion="cerrar-sesion">%s '
                   "Cerrar sesión</button>" % ico("salir", 15))
        + card("Notificaciones", '<div style="font-size:13px;color:#162644">Tienes '
               "%d avisos sin leer: una asesoría confirmada, una tarea nueva y un avance de "
               "seguimiento."
               "</div>" % sum(1 for n in NOTIFS_EST if n[0]),
               accion='<a class="btn btn-secundario btn-sm" href="notificaciones.html">%s '
                      "Ver notificaciones</a>" % ico("bell", 15))
        + "</div></div>"
        + '<div style="height:20px"></div>'
        + '<div style="display:flex;gap:10px;flex-wrap:wrap">'
        + '<a class="btn btn-acento" href="configuracion.html">%s Editar perfil y configuración</a>'
        % ico("edit", 16)
        + "</div>"
    )
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Tus datos básicos y los emprendimientos que tienes a cargo.")


# --- 15b. Configuracion (edicion del perfil) ---------------------------------
def configuracion():
    """Configuración del estudiante: datos personales, académicos y contraseña.

    Es la pantalla de edición que se abre desde el perfil. Los campos
    institucionales los mantiene el ADMINISTRADOR.
    """
    cuerpo = (
        callout("Aquí actualizas tus datos y tu contraseña. Los campos con el candado los "
                "mantiene el <b>ADMINISTRADOR</b> de la institución.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Datos personales",
               '<div class="grid g-2" style="gap:0 16px">'
               + campo("Nombres", valor="Mariana") + campo("Apellidos", valor="Lopez Herrera")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + select("Tipo de documento", ["CC", "TI", "Cédula de extranjería"],
                        valor="CC", req=True)
               + campo("Número de documento", valor="1020304050",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Número de estudiante", valor="2024105678",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + campo("Fecha de nacimiento", tipo="date", valor="1999-04-18")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Correo personal", valor="mariana.lopez@correo.com", tipo="email")
               + campo("Correo institucional", valor="mariana.lopez@minutodedios.edu.co",
                       tipo="email", bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Celular", valor="300 555 4412", tipo="tel", req=True)
               + campo("Celular 2 (opcional)", tipo="tel", ph="Opcional",
                       ayuda="Déjalo vacío si no tienes un segundo número.")
               + "</div>"
               + '<div class="grid g-3" style="gap:0 16px">'
               + campo("Departamento", valor="Norte de Santander")
               + campo("Ciudad", valor="Cúcuta")
               + campo("Sede", valor="Sede Norte")
               + "</div>"
               + '<div style="display:flex;justify-content:flex-end;gap:10px">'
               + '<button class="btn btn-secundario" data-accion="cancelar-perfil">Cancelar</button>'
               + '<button class="btn btn-primario" data-accion="guardar-perfil">%s '
                 "Guardar cambios</button>" % ico("check", 16) + "</div>")
        + card("Datos académicos",
               '<div class="grid g-2" style="gap:0 16px">'
               + select("Nivel académico", ["Pregrado", "Posgrado"], valor="Pregrado", req=True)
               + campo("Programa académico", valor="Ingeniería Industrial",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + select("Semestre", ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto",
                                     "Sexto", "Séptimo", "Octavo", "Noveno", "Décimo"],
                        valor="Quinto", req=True)
               + select("Modalidad", ["Presencial", "Virtual"], valor="Presencial", req=True)
               + "</div>"
               + '<div class="nota-foot">Estos datos determinan los eventos y las '
                 "convocatorias que te llegan.</div>")
        + card("Cambiar contraseña",
               '<div class="grid g-3" style="gap:0 16px">'
               + campo("Contraseña actual", tipo="password", ph="••••••••")
               + campo("Nueva contraseña", tipo="password", ph="Mínimo 8 caracteres")
               + campo("Repetir nueva contraseña", tipo="password", ph="••••••••")
               + "</div>"
               '<div style="display:flex;justify-content:flex-end">'
               '<button class="btn btn-secundario" data-accion="actualizar-contrasena">'
               "Actualizar contraseña</button></div>")
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Foto del estudiante",
               '<div style="display:flex;align-items:center;gap:16px">'
               '<div class="perfil-foto" style="width:96px;height:96px;flex:0 0 96px">'
               "<span>ML</span></div>"
               '<div><div style="font-size:13px;color:#162644">Sube una imagen en formato '
               "<b>PNG</b> o JPG, de máximo 2 MB.</div>"
               '<div style="margin-top:10px">'
               '<button class="btn btn-secundario btn-sm" data-accion="cambiar-foto">%s '
               "Subir imagen</button></div></div></div>" % ico("upload", 15))
        + card("Accesos y seguridad", lista_def([
            ("Último ingreso", "12 nov 2024, 08:14 · Cúcuta"),
            ("Estado de la cuenta", badge("Limitado", "b-amarillo", "lock")),
            ("Rol", badge("ESTUDIANTE", "b-amarillo", "user")),
        ]))
        + "</div></div>"
    )
    return shell(R, "configuracion", "Configuración", cuerpo,
                 migas=["Inicio", "Mi perfil", "Configuración"],
                 sub="Edita tus datos personales, académicos y tu contraseña.",
                 acciones='<a class="btn btn-secundario" href="perfil.html">%s Volver al perfil</a>'
                          % ico("izq", 16))


# --- 16. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja de avisos; la campana del encabezado lee la misma fuente.

    Cada aviso es un enlace a la vista donde se resuelve, y los filtros de la
    columna derecha muestran y ocultan sin tocar el contenido.
    """
    no_leidas = sum(1 for n in NOTIFS_EST if n[0])
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + '<div class="card"><div class="card-head"><h3>Bandeja de notificaciones</h3>'
          '<span class="hint" id="contador-no-leidas">%d sin leer</span></div>'
          '<div class="card-body sin-pad">' % no_leidas
        + "".join(
            '<a class="notif%s" href="%s" data-tipo="%s" data-i="%d">'
            '<span class="notif-ico">%s</span>'
            '<div class="notif-cuerpo"><h3>%s</h3><p>%s</p><time>%s</time></div>'
            '<span class="notif-flecha">%s</span>%s</a>'
            % (" no-leida" if leer else "", href, tipo, i, ico(ic, 17), t, txt, f,
               ico("der", 16), '<span class="notif-dot"></span>' if leer else "")
            for i, (leer, t, txt, f, ic, tipo, href) in enumerate(NOTIFS_EST)
        )
        + "</div></div>"
        + "</div>"
        + '<div class="grid" style="gap:20px">'
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
                 for t in ["Correo electronico", "Notificaciones en el sistema",
                           "Recordatorio de tareas"])
             + '<div class="nota-foot">Un administrador puede ajustar estas preferencias.</div>'
         + "</div>")
        + "</div></div>"
    )
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Alertas de tareas, asesorías y seguimiento.",
                 acciones='<button class="btn btn-secundario" '
                          'data-accion="marcar-todas-como-leidas">%s Marcar todas como leídas'
                          "</button>" % ico("check", 16))