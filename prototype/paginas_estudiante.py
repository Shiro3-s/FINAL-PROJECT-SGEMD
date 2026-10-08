# -*- coding: utf-8 -*-
"""Rol ESTUDIANTE — 16 pantallas."""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, tabs, ico, boton_accion, ico, linea_tiempo, kanban,
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
        ("diagnostico.html", "10 Estudiante - Diagnostico (cuestionario)", diagnostico),
        ("diagnostico-resultados.html", "11 Estudiante - Resultados del diagnostico", diagnostico_resultados),
        ("plan-trabajo.html", "12 Estudiante - Plan de trabajo", plan_trabajo),
        ("seguimiento.html", "13 Estudiante - Seguimiento (historial)", seguimiento),
        ("tareas.html", "14 Estudiante - Mis tareas", tareas),
        ("tarea-detalle.html", "15 Estudiante - Detalle de tarea", tarea_detalle),
        ("asesorias.html", "16 Estudiante - Mis asesorias", asesorias),
        ("solicitar-asesoria.html", "17 Estudiante - Solicitar asesoria", solicitar_asesoria),
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
            "Tu cuenta esta <b>Limitada</b>. Ya puedes entrar al sistema, pero el modulo de "
            "<b>Diagnostico</b> permanece bloqueado hasta que un administrador active tu cuenta.",
            "escudo",
        )
        + '<div style="height:20px"></div>'
        + metricas([
            ("maleta", "Mi emprendimiento", "1", "activo", 100, "1 registrado"),
            ("target", "Diagnostico", "Pendiente", "", 0, ""),
            ("checklist", "Tareas completadas", "3", "de 7", 43, ""),
            ("chat", "Asesorías realizadas", "3", "", 100, ""),
        ])
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + card(
            "Progreso de mi emprendimiento",
            '<div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap">'
            + circular(62, "avance", "FASE 2 · Ejecucion")
            + '<div style="flex:1;min-width:280px">'
            + progreso_fases([
                ("FASE 1 · Ideacion", 100, AZUL),
                ("FASE 2 · Ejecucion", 62, AZUL),
                ("FASE 3 · Consolidacion", 0, GRIS),
                ("FASE 4 · Escalamiento", 0, GRIS),
            ])
            + "</div></div>",
            accion='<a class="btn btn-secundario btn-sm" href="plan-trabajo.html">Ver plan de trabajo</a>',
        )
        + card(
            "Proximas asesorias",
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
            "Tareas pendientes",
            '<div class="lista-def" style="padding:4px 0">'
            + "".join(
                '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">%s</dd>'
                '<dd style="flex:0 0 auto">%s</dd></div>'
                % (t, d, badge(p, "b-amarillo" if p == "Alta" else "b-linea", "alerta" if p == "Alta" else "reloj"))
                for t, d, p in [
                    ("Hoy", "Subir evidencia fotografica del punto de venta", "Alta"),
                    ("13 nov", "Actualizar el inventario de insumos", "Media"),
                    ("15 nov", "Registrar las ventas de la semana en el formato", "Media"),
                ]
            )
            + "</div>",
            accion='<a class="btn btn-secundario btn-sm" href="tareas.html">Ver todas</a>',
        )
        + card(
            "Avisos de la institucion",
            '<div class="lista-def" style="padding:4px 0">'
            '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">'
            "Sesion de capacitacion en modelado de negocios: jueves 21 nov, 8:00 a.m.</dd></div>"
            '<div class="def-row"><dt style="flex:0 0 auto">%s</dt><dd style="flex:1">'
            "Convocatoria del evento Startup Minuto de Dios. Postulacion hasta el 25 nov.</dd></div>"
            "</div>" % (ico("calendar", 15), ico("rayo", 15)),
        )
        + "</div>"
    )
    return shell(R, "dashboard", "Inicio", cuerpo,
                 sub="Resumen de tu emprendimiento, tareas y asesorias de esta semana.")


# --- 2. Estado de seguimiento ------------------------------------------------
def estado_seguimiento():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(
            "Movimiento en el plan",
            '<div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap">'
            + circular(62, "avance", "FASE 2 · Ejecucion")
            + '<div style="flex:1;min-width:300px">'
            + '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px">'
            + "".join(
                '<div style="border:1px solid #bbbbbb;border-radius:8px;padding:12px 14px">'
                '<div style="font-size:13px;color:#162644">%s</div>'
                '<div style="font-size:20px;font-weight:700;color:#051533">%s</div>'
                '<div style="font-size:13px;color:#162644">%s</div></div>'
                % (lbl, val, det)
                for lbl, val, det in [
                    ("Fase actual", "FASE 2", "Ejecucion y validacion"),
                    ("Tareas completadas", "3 / 7", "43% del total asignado"),
                    ("Asesorias recibidas", "3", "ultima: 04 nov 2024"),
                    ("Seguimientos registrados", "5", "ultimo: 08 nov 2024"),
                ]
            )
            + "</div></div></div>",
        )
        + card(
            "Avance por fases",
            progreso_fases([
                ("FASE 1 · Ideación y priorización de ideas", 100, AZUL),
                ("FASE 2 · Estructuracion y ejecucion", 62, AZUL),
                ("FASE 3 · Consolidacion del proceso", 0, GRIS),
                ("FASE 4 · Escalamiento", 0, GRIS),
            ]),
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
                for t in [
                    "Diagnostico inicial entregado",
                    "Plan de trabajo cargado por el docente",
                    "Primeras ventas registradas",
                    "Perfil de cliente definido",
                ]
            )
            + "</div>",
        )
        + card(
            "Requisito bloqueante",
            '<div style="font-size:13px;color:#162644">Tu cuenta esta en estado '
            "<b style=\"color:#051533\">Limitado</b>. Mientras no sea activada por un "
            "administrador, el diagnostico inicial no puede enviarse.</div>"
            '<div style="margin-top:14px">%s</div>' % badge("Cuenta limitada", "b-amarillo", "lock"),
            accion='<a class="btn btn-secundario btn-sm" href="perfil.html">Ver mi perfil</a>',
        )
        + "</div></div>"
    )
    return shell(R, "estado-seguimiento", "Estado de seguimiento", cuerpo,
                 migas=["Inicio", "Estado de seguimiento"],
                 sub="Aqui ves cuanto has avanzado y que te falta por completar.",
                 acciones='<a class="btn btn-secundario" href="plan-trabajo.html">Plan de trabajo</a>'
                          '<a class="btn btn-acento" href="tareas.html">Ver mis tareas</a>')


# --- 3. Emprendimientos (lista) ---------------------------------------------
def emprendimientos():
    filas = [[
        '<b>Sabor y Sabe</b>', "Alimentos y bebidas", "Alimentos",
        badge("FASE 2 · Ejecucion", "b-azul", "engranaje"),
        "12 oct 2024", "Carlos Mendoza",
        _acc(_a("eye", "Ver detalle", "emprendimiento-detalle.html"),
             _a("edit", "Editar", "emprendimiento-editar.html"),
             _b("download", "Descargar expediente")),
    ], [
        '<b>Mochilas Origen</b>', "Moda y accesorios", "Textil",
        badge("FASE 1 · Ideacion", "b-amarillo", "bombilla"),
        "03 sep 2024", "Sin asignar",
        _acc(_a("eye", "Ver detalle", "emprendimiento-detalle.html"),
             _b("download", "Descargar expediente")),
    ]]
    cuerpo = (
        toolbar(
            filtros='<select class="filtro" data-filtro="etapa" data-filtro-col="3" '
                    'aria-label="Filtrar por etapa"><option value="">Todas las etapas</option>'
                    "<option>FASE 1 · Ideacion</option><option>FASE 2 · Ejecucion</option>"
                    "<option>FASE 3 · Consolidacion</option><option>FASE 4 · Escalamiento</option></select>"
                   '<select class="filtro" data-filtro="sector" data-filtro-col="2" '
                   'aria-label="Filtrar por sector"><option value="">Todos los sectores</option><option>Alimentos</option>'
                   "<option>Textil</option><option>Servicios</option><option>Tecnologia</option></select>",
        )
        + tabla(
            ["Emprendimiento", "Tipo de emprendimiento", "Sector productivo",
             "Etapa actual", "Fecha de creacion", "Docente asignado", "@ACC"],
            [[f[0], f[1], f[2], f[3], f[4], f[5], f[6]] for f in filas],
        )
        + paginas(1, 2, 2)
        + '<div style="height:20px"></div>'
        + callout(
            "Solo puedes ver los emprendimientos que te pertenecen. Para consultar el de otro "
            "estudiante debes entrar como <b>DOCENTE</b> o <b>ADMINISTRADOR</b>.",
            "escudo",
        )
    )
    return shell(R, "emprendimientos", "Mi emprendimiento", cuerpo,
                 migas=["Inicio", "Mi emprendimiento"],
                 sub="Listado de tus emprendimientos y su estado actual.",
                 acciones='<button class="btn btn-secundario">%s Exportar</button>' % ico("download", 16)
                          + '<a class="btn btn-acento" href="emprendimiento-editar.html">%s Crear emprendimiento</a>' % ico("plus", 16))


# --- 4. Detalle del emprendimiento ------------------------------------------
def emprendimiento_detalle():
    cuerpo = (
        tabs(["Resumen", "Diagnostico", "Plan de trabajo", "Seguimiento", "Tareas", "Asesorias"])
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Datos basicos", lista_def([
            ("Nombre", "Sabor y Sabe"),
            ("Tipo de emprendimiento", "Alimentos y bebidas"),
            ("Sector productivo", "Alimentos"),
            ("Etapa actual", badge("FASE 2 · Ejecucion", "b-azul", "engranaje")),
            ("Fecha de creacion", "12 de octubre de 2024"),
            ("Estado de la cuenta", badge("Limitado", "b-amarillo", "lock")),
        ]))
        + card(
            "Descripcion",
            '<p style="font-size:13px;color:#162644">Sabor y Sabe es un emprendimiento de '
            "alimentos y bebidas que prepara y comercializa snacks artesanales a base de "
            "frutos secos y granola, con ventas en el campus y por pedido a domicilio dentro "
            "del municipio.</p>",
        )
        + card("Redes sociales", lista_def([
            ("Instagram", "@saborysabe.md"),
            ("WhatsApp Business", "300 555 4412"),
            ("Tienda propia", "aun no registrada"),
        ]))
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Docente asignado", '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
             '<span class="avatar" style="width:44px;height:44px;flex:0 0 44px;font-size:14px">CM</span>'
             '<div><div style="font-weight:600">Carlos Mendoza</div>'
             '<div style="font-size:13px;color:#162644">Docente &middot; Áreas de flipped classroom y e-learning</div>'
             "</div></div>"
             '<button class="btn btn-secundario btn-sm" style="width:100%%">%s Solicitar asesoria</button>'
             % ico("chat", 15))
        + card("Acciones disponibles",
               '<div style="display:flex;flex-direction:column;gap:10px">'
               '<a class="btn btn-primario" href="emprendimiento-editar.html" style="width:100%%">%s Editar datos basicos</a>'
               '<a class="btn btn-secundario" href="plan-trabajo.html" style="width:100%%">%s Ver plan de trabajo</a>'
               '<button class="btn btn-secundario" style="width:100%%">%s Descargar expediente</button>'
               "</div>"
               '<div class="nota-foot">Solo puedes editar nombre, descripcion y redes sociales. '
               "El tipo, el sector, la etapa y el acta los administra el rol ADMINISTRADOR.</div>"
               % (ico("edit", 16), ico("layers", 16), ico("download", 16)))
        + "</div></div>"
    )
    return shell(R, "emprendimientos", "Sabor y Sabe", cuerpo,
                 migas=["Inicio", "Mi emprendimiento", "Sabor y Sabe"],
                 sub="Detalle de tu emprendimiento.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>' % ico("izq", 16)
                          + '<a class="btn btn-acento" href="emprendimiento-editar.html">%s Editar</a>' % ico("edit", 16))


# --- 5. Editar emprendimiento ------------------------------------------------
def emprendimiento_editar():
    cuerpo = (
        callout("Estás editando <b>Sabor y Sabe</b>. Los cambios de nombre y descripcion quedan "
                "registrados en el historial del emprendimiento.", "alerta")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card(
            "Datos que puedes editar",
            campo("Nombre del emprendimiento", valor="Sabor y Sabe", req=True,
                  ayuda="Entre 4 y 80 caracteres.")
            + campo("Descripcion", alto=True,
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
            + '<button class="btn btn-primario">%s Guardar cambios</button></div>' % ico("check", 16),
        )
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card(
            "Campos bloqueados para tu rol",
            campo("Tipo de emprendimiento", valor="Alimentos y bebidas",
                  bloqueo="Solo ADMINISTRADOR puede modificarlo.")
            + campo("Sector productivo", valor="Alimentos",
                    bloqueo="Solo ADMINISTRADOR puede modificarlo.")
            + campo("Etapa actual", valor="FASE 2 · Ejecucion",
                    bloqueo="Solo DOCENTE y ADMINISTRADOR pueden cambiar la etapa.")
            + campo("Acta de constitucion", valor="sin_adjunto.pdf",
                    bloqueo="Solo ADMINISTRADOR puede cargar el acta."),
        )
        + "</div></div>"
    )
    return shell(
        R, "emprendimientos", "Editar emprendimiento", cuerpo,
        migas=["Inicio", "Mi emprendimiento", "Sabor y Sabe", "Editar"],
        sub="Actualiza la informacion que tienes permitido modificar.",
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
    cuenta las respondidas (DG3). El boton "Enviar diagnostico" queda en la
    ultima seccion."""
    preguntas = [
        ("Perfil del emprendimiento", [
            campo("Cual es el nombre de tu emprendimiento?", valor="Sabor y Sabe",
                  ph="Ej. Sabor y Sabe", req=True),
            select("Que tipo de emprendimiento es?",
                   ["Alimentos y bebidas", "Moda y accesorios", "Servicios", "Tecnologia"],
                   valor="Alimentos y bebidas", req=True),
            select("A que sector productivo pertenece?",
                   ["Alimentos", "Textil", "Servicios", "Tecnologia"],
                   valor="Alimentos", req=True),
            campo("Que producto o servicio ofreces?", alto=True,
                  valor="Snacks artesanales de frutos secos y granola", req=True),
            select("En que etapa del programa esta tu emprendimiento?",
                   ["FASE 1 - Ideacion", "FASE 2 - Ejecucion",
                    "FASE 3 - Consolidacion", "FASE 4 - Escalamiento"],
                   valor="FASE 2 - Ejecucion", req=True),
        ]),
        ("Problema o necesidad", [
            campo("Que problema concreto resuelve tu producto o servicio?",
                  alto=True, valor="Pocas opciones de snacks saludables y accesibles en el campus",
                  ph="Describe el problema", req=True),
            campo("A quien le ocurre ese problema?", valor="Estudiantes y personal del campus",
                  ph="Describe a quien afecta", req=True),
            campo("Como lo resuelven hoy (sin tu producto)?",
                  valor="Snacks industriales de baja calidad nutricional", req=True),
            select("Que tan urgente es el problema para tu cliente?",
                   ["Baja", "Media", "Alta"], valor="Alta", req=True),
        ]),
        ("Propuesta de valor", [
            campo("Cual es tu propuesta de valor en una frase?", alto=True,
                  valor="Snacks artesanales, saludables y con ingredientes locales", req=True),
            campo("Que beneficio concreto entrega al cliente?",
                  valor="Alimentacion mas sana sin renunciar al sabor ni al precio", req=True),
            select("Que te diferencia de la competencia?",
                   ["Precio", "Calidad", "Sostenibilidad", "Cercania con el cliente"],
                   valor="Sostenibilidad", req=True),
            select("Que necesidad principal cubre?",
                   ["Salud", "Comodidad", "Precio", "Sabor"], valor="Salud", req=True),
        ]),
        ("Mercado objetivo", [
            campo("Quien es tu cliente ideal (perfil)?", valor="Estudiantes de 18-25 que cuidan su alimentacion",
                  req=True),
            campo("Cuantos clientes potenciales estimas?", valor="Unos 400 estudiantes del campus", req=True),
            select("Cual es tu estrategia de precio?",
                   ["Economia (bajo costo)", "Valor medio", "Premium"], valor="Valor medio", req=True),
            campo("Que canales usaras para llegarles?", valor="Punto de venta en cafeteria y WhatsApp", req=True),
        ]),
        ("Capacidad operativa y financiera", [
            select("Con cuantas personas cuenta el equipo?",
                   ["1 (fundador/a)", "2 - 3", "4 - 5", "Mas de 5"], valor="2 - 3", req=True),
            campo("Cual es tu capacidad de produccion actual?",
                  valor="80 unidades semanales", req=True),
            select("Llevas registro de costos y ventas?",
                   ["No", "Basico (cuaderno)", "Completo (planilla)"], valor="Basico (cuaderno)", req=True),
            campo("Que inversion necesitas para crecer?", valor="$ la primera compra de insumos", req=True),
            campo("Cual es tu meta de ventas del proximo mes?",
                  valor="160 unidades / $480.000", req=True),
        ]),
    ]
    total = sum(len(p) for _, p in preguntas)
    n = len(preguntas)

    def panel(i, titulo, bloques):
        oculta = ' hidden' if i else ''
        anterior = ('<button class="btn btn-secundario" data-accion="seccion-anterior">%s Anterior</button>'
                    % ico("izq", 15)) if i else ''
        siguiente = ('<button class="btn btn-acento" data-accion="enviar-diagnostico">%s Enviar diagnostico</button>'
                     % ico("enviar", 15)) if i == n - 1 else (
                     '<button class="btn btn-acento" data-accion="seccion-siguiente">%s Siguiente seccion</button>'
                     % ico("der", 15))
        return ('<div class="card" data-panel-nombre="seccion-%d"%s>'
                '<div class="card-head"><h3>Seccion %d de %d &middot; %s</h3></div>'
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
        + card("Como va el cuestionario",
               barras_h("", "", ["Perfil", "Problema", "Propuesta", "Mercado", "Capacidad"],
                        [100, 0, 0, 0, 0], maximo=100, unidad="%"),
               hint="5 secciones")
        + card("Puedes pausar cuando quieras",
               '<div style="font-size:13px;color:#162644">Tu respuesta se guarda como '
               "<b>borrador</b>. Solo se envia al docente cuando completas las 5 secciones "
               "y pulsas <b>Enviar diagnostico</b>.</div>"
               '<div style="margin-top:12px">%s</div>' % badge("Borrador guardado", "b-linea", "doc"))
        + "</div></div>"
    )
    return shell(R, "diagnostico", "Diagnostico inicial", cuerpo,
                 migas=["Inicio", "Diagnostico"],
                 sub="Responde el cuestionario para que el docente pueda construir tu plan de trabajo.",
                 acciones='<button class="btn btn-secundario" data-accion="guardar-y-salir">%s Guardar y salir</button>'
                          % ico("doc", 16))


# --- 7. Resultados del diagnostico ------------------------------------------
def diagnostico_resultados():
    cuerpo = (
        '<div class="grid g-4">'
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Estado del envio</div>'
          '<div class="metrica-val" style="font-size:20px">Enviado</div></div></div>'
          '<div class="nota-foot">Enviado el 28 oct 2024, 09:14</div></div>' % ico("enviar", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Calidad entrepreneurial</div>'
          '<div class="metrica-val">7.8<span class="u">/ 10</span></div></div></div></div>' % ico("medalla", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">NPS estimado</div>'
          '<div class="metrica-val">9</div></div></div></div>' % ico("trend", 18)
        + '<div class="card metrica"><div class="metrica-top"><span class="metrica-ico">%s</span>'
          '<div><div class="metrica-lbl">Areas a reforzar</div>'
          '<div class="metrica-val">3</div></div></div></div>' % ico("alerta", 18)
        + "</div>"
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Comportamiento entrepreneurial", barras_h(
            "", "", ["Vision", "Creatividad", "Resiliencia", "Liderazgo", "Trabajo en equipo",
                     "Capacidad deDecision"],
            [85, 78, 70, 82, 88, 66], maximo=100, unidad="%"))
        + card("Distribucion de las respuestas", donut(
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
                       "Definir con mas precision el canal de venta digital.",
                       "Separar el presupuesto de insumos del presupuesto de publicidad.",
                       "Registrar el costo fijo mensual para calcular el punto de equilibrio.",
                   ]
               )
               + "</div>")
        + card("Puntaje por dimension",
               '<div style="font-size:13px;color:#162644">Este resultado es una foto del momento. '
               "Volveras a responder el diagnostico al cierre de cada fase.</div>")
        + "</div></div>"
    )
    return shell(R, "diagnostico", "Resultado del diagnostico", cuerpo,
                 migas=["Inicio", "Diagnostico", "Resultado"],
                 sub="Puntaje, comportamiento entrepreneurial y recomendaciones del docente.",
                 acciones='<button class="btn btn-secundario">%s Descargar PDF</button>' % ico("download", 16)
                          + '<button class="btn btn-primario">%s Volver a responder</button>' % ico("clipboard", 16))


# --- 8. Plan de trabajo ------------------------------------------------------
FASES = [
    ("FASE 1", "Ideación y priorización de ideas", 100, [
        ("Definir la idea y el problema que ataca", "Completada"),
        ("Identificar clientes potenciales", "Completada"),
        ("Validar la solucion con usuarios", "Completada"),
    ]),
    ("FASE 2", "Estructuracion y ejecucion", 62, [
        ("Levantar el modelo de negocio", "En curso"),
        ("Definir la mezcla de marketing", "En curso"),
        ("Calcular el punto de equilibrio", "Pendiente"),
        ("Constituir el Startup Minuto de Dios", "Pendiente"),
    ]),
    ("FASE 3", "Consolidacion del proceso", 0, [
        ("Formalizar la operacion diaria", "Bloqueada"),
        ("Registrar indicadores de venta", "Bloqueada"),
    ]),
    ("FASE 4", "Escalamiento", 0, [
        ("Escalar el modelo de negocio", "Bloqueada"),
        ("Buscar alianzas estratégicas", "Bloqueada"),
    ]),
]


def plan_trabajo():
    bloques = ""
    for codigo, nombre, pct, tareas in FASES:
        filas = ""
        for t, est in tareas:
            col = {"Completada": ("b-linea", "check"), "En curso": ("b-azul", "reloj"),
                   "Pendiente": ("b-amarillo", "bombilla"), "Bloqueada": ("b-neutra", "lock")}[est]
            filas += (
                '<div style="display:flex;align-items:center;gap:12px;padding:10px 0;'
                'border-bottom:1px solid #bbbbbb">'
                '<span style="color:#004a93;flex:0 0 18px">%s</span>'
                '<span style="flex:1;font-size:13px;color:#051533">%s</span>%s</div>'
                % (ico("checklist", 16), t, badge(est, col[0], col[1]))
            )
        cab = AMAR if codigo == "FASE 2" else (AZUL if codigo == "FASE 1" else GRIS)
        bloques += (
            '<div class="card"><div class="card-head">'
            '<span style="background:%s;color:%s;border-radius:6px;padding:3px 9px;'
            'font-size:13px;font-weight:700;letter-spacing:.04em">%s</span>'
            '<h3>%s</h3>'
            '<span style="font-weight:700;font-size:13px;color:#051533">%d%%</span></div>'
            '<div class="card-body sin-pad"><div style="padding:6px 20px 14px">%s</div>'
            '<div style="padding:0 20px 16px"><div class="barra"><span style="width:%d%%;'
            'background:%s"></span></div></div></div></div>'
            % (cab, "#051533" if codigo == "FASE 2" else "#ffffff", codigo, nombre, pct, filas, pct, cab)
        )
    cuerpo = (
        callout("El plan de trabajo lo construye el docente que tienes asignado y tu solo "
                "puedes consultar su avance y completar las tareas.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">' + bloques + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Avance general", '<div style="text-align:center">'
             + circular(62, "avance", "FASE 2 · Ejecucion") + "</div>")
        + card("Resumen por estado", stacked_tareas([
            ("Alta", 2, AZUL), ("Media", 3, PROF), ("Baja", 1, GRIS)], "tareas"))
        + "</div></div>"
    )
    return shell(R, "plan-trabajo", "Plan de trabajo", cuerpo,
                 migas=["Inicio", "Plan de trabajo"],
                 sub="Las cuatro fases del Startup Minuto de Dios y tu avance en cada una.",
                 acciones='<button class="btn btn-secundario">%s Descargar plan</button>' % ico("download", 16))


# --- 9. Seguimiento (historial) --------------------------------------------
def seguimiento():
    filas = []
    for f, est, desc, doc in [
        ("22 oct 2024", "Avance de fase", "Se avanzo en el levantamiento del modelo de negocio y se "
         "acordo definir el canal de venta por redes.", "Carlos Mendoza"),
        ("05 nov 2024", "Avance de fase", "Revision de ventas de la semana. Se detecto que el margen "
         "es bajo en la granola de cacao; se evalua cambiar el proveedor.", "Carlos Mendoza"),
        ("08 nov 2024", "Comentario", "Se recuerda cargar la evidencia fotografica de cada venta "
         "en las tareas asignadas.", "Carlos Mendoza"),
        ("12 nov 2024", "Avance de fase", "Se define el precio de venta final con margen "
         "del 35 por ciento.", "Carlos Mendoza"),
    ]:
        filas.append([f, badge(est, "b-azul" if "Avance" in est else "b-neutra",
                               "trend" if "Avance" in est else "chat"), desc, doc,
                      _acc(_b("eye", "Ver detalle"))])
    cuerpo = (
        callout("El seguimiento es de <b>solo lectura</b>. Los registros los crea el docente o el "
                "administrador segun las reglas de gestion.", "escudo")
        + '<div style="height:20px"></div>'
        + tabla(["Fecha", "Tipo de registro", "Descripcion", "Registrado por", "@ACC"], filas)
        + paginas(1, 4, 4)
        + '<div style="height:20px"></div>'
        + card("Frecuencia con que te acompanana el docente",
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
        + '<div style="height:20px"></div>'
        + kanban([
            ("Pendientes", [
                ("Subir evidencia fotografica del punto de venta",
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
            ("En revision", [
                ("Levantar el modelo de negocio",
                 "Enviada el 04 nov 2024 · esperando calificacion",
                 badge("Alta", "b-azul", "alerta"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Ver</a>'),
            ]),
            ("Completadas", [
                ("Definir el precio de venta final",
                 "Completada el 08 nov 2024",
                 badge("Calificada 90", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Ver</a>'),
                ("Validar la solucion con 10 usuarios",
                 "Completada el 01 nov 2024",
                 badge("Calificada 85", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Ver</a>'),
                ("Definir clientes potenciales",
                 "Completada el 28 oct 2024",
                 badge("Calificada 92", "b-linea"),
                 '<a class="btn btn-sm btn-secundario" href="tarea-detalle.html">'
                 'Ver</a>'),
            ]),
        ])
        + '<p class="nota-foot">Arrastra no aplica: cada tarea se mueve cuando '
          'el docente la califica.</p>'
    )
    return shell(R, "tareas", "Mis tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Tareas que debes completar y su evidencia.",
                 acciones='<button class="btn btn-secundario">%s Descargar reporte</button>' % ico("download", 16))


# --- 11. Detalle de tarea ----------------------------------------------------
def tarea_detalle():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Subir evidencia fotografica del punto de venta",
               lista_def([
                   ("Prioridad", badge("Alta", "b-azul", "alerta")),
                   ("Fecha limite", "12 de noviembre de 2024"),
                   ("Asignada por", "Carlos Mendoza"),
                   ("Estado", badge("Pendiente", "b-amarillo", "reloj")),
                   ("Emprendimiento", "Sabor y Sabe"),
               ])
               + '<div class="divisor"></div>'
               + '<h3 style="margin-bottom:8px">Descripcion de la tarea</h3>'
                 '<p style="font-size:13px;color:#162644">Adjunta al menos tres fotografias del '
                 "punto de venta con los productos expuestos y la cartelera de precios. La evidencia "
                 "debe mostrar la fecha de toma.</p>")
        + card(
            "Evidencia adjunta",
            '<label class="drop" for="evidencia-real">%s'
            "<b style=\"display:block;color:#051533;font-size:13px\">Arrastra tus archivos aqui "
            "o haz clic para seleccionarlos</b>"
            '<span style="font-size:13px">Formatos admitidos: JPG, PNG o PDF &middot; Maximo 10 MB</span>'
            '<input type="file" id="evidencia-real" multiple accept=".jpg,.jpeg,.png,.pdf" '
            'aria-label="Seleccionar evidencia" style="display:none"></label>'
            % ico("upload", 34),
            hint='<span id="contador-adjuntos">0 archivos</span>')
        + card("Adjuntos",
               '<div id="adjuntos-lista">' + estado_vacio(
                   "Todavia no has adjuntado evidencia",
                   "Cuando subas los archivos apareceran aqui con su fecha de carga.",
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
             '<div class="nota-foot">El boton se habilita cuando exista evidencia adjunta.</div>'
             % ico("check", 16))
        + card("Comentarios del docente",
               '<div class="lista-def" style="padding:4px 0">'
               '<div class="def-row" style="display:block"><dd style="color:#051533">'
               "Recuerda que las fotos deben incluir la fecha de toma para validar la evidencia."
               '</dd><dt style="flex:0 0 auto;margin-top:6px;font-size:13px">'
               "Carlos Mendoza &middot; 09 nov 2024</dt></div></div>")
        + "</div></div>"
    )
    return shell(R, "tareas", "Subir evidencia fotografica del punto de venta", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Detalle de la tarea asignada.",
                 acciones='<a class="btn btn-secundario" href="tareas.html">%s Volver</a>' % ico("izq", 16))


# --- 12. Asesorias -----------------------------------------------------------
def asesorias():
    """Linea de tiempo: primero lo que viene, despues lo ya realizado."""
    cuerpo = (
        callout("Como estudiante puedes <b>solicitar</b> una asesoria y consultar las que ya "
                "tienes. La asignacion del docente y la confirmacion del horario los realiza el "
                "rol DOCENTE o ADMINISTRADOR.", "escudo")
        + '<div style="height:20px"></div>'
        + metricas([
            ("chat", "Asesorias realizadas", "3", "", 100, ""),
            ("reloj", "Programadas", "3", "", 100, ""),
            ("check", "Confirmadas", "2", "", 67, ""),
        ])
        + '<div style="height:20px"></div>'
        + card("Proximas asesorias", linea_tiempo([
            ("14", "nov", "Asesoria con Laura Sanchez",
             "14:30 - 15:30 · Presencial · Pendiente de confirmar",
             '<div style="margin-top:10px">'
             + badge("Pendiente de confirmar", "b-amarillo", "reloj")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("19", "nov", "Asesoria con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Confirmada",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
            ("12", "nov", "Asesoria con Carlos Mendoza",
             "10:00 - 11:00 · Virtual · Confirmada",
             '<div style="margin-top:10px">'
             + badge("Confirmada", "b-azul", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-detalle\">Ver detalle</button></div>"),
        ]), sin_pad=False)
        + '<div style="height:20px"></div>'
        + card("Asesorias realizadas", linea_tiempo([
            ("04", "nov", "Asesoria con Carlos Mendoza",
             "09:00 - 10:00 · Virtual · Realizada",
             '<div style="margin-top:10px">'
             + badge("Realizada", "b-linea", "check")
             + " <button class=\"btn btn-sm btn-secundario\" data-accion=\"ver-acta\">Ver acta</button></div>"),
        ]))
    )
    return shell(R, "asesorias", "Mis asesorias", cuerpo,
                 migas=["Inicio", "Asesorias"],
                 sub="Historial y proximas asesorias de tu emprendimiento.",
                 acciones='<a class="btn btn-acento" href="solicitar-asesoria.html">%s Solicitar asesoria</a>'
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
                    ph="Describe los temas que quieres tratar en la asesoria",
                    ayuda="Mientras mas concreto, mejor podremos preparar la sesion.")
            + '<div class="divisor"></div>'
            + '<div style="display:flex;justify-content:flex-end;gap:10px">'
            + '<a class="btn btn-secundario" href="asesorias.html">Cancelar</a>'
            + '<button class="btn btn-acento" data-accion="enviar-solicitud">%s Enviar solicitud</button></div>' % ico("enviar", 16),
        )
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Como funciona",
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
                       "El docente recibe la notificacion y responde.",
                       "Se confirma la fecha y la modalidad.",
                       "Asistis y la asesoria queda registrada.",
                   ])
               )
               + "</div>")
        + "</div></div>"
    )
    return shell(
        R, "asesorias", "Solicitar asesoria", cuerpo,
        migas=["Inicio", "Asesorias", "Solicitar"],
        sub="Registra tu solicitud. El docente confirmara fecha y modalidad.",
        acciones='<a class="btn btn-secundario" href="asesorias.html">%s Volver</a>' % ico("izq", 16),
    )


# --- 14. Eventos -------------------------------------------------------------
def eventos():
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Proximos eventos", tabla(
            ["Evento", "Tipo", "Fecha y hora", "Modalidad", "Organizador", "@ACC"],
            [['<b>Startup Minuto de Dios</b>', "Conferencia",
              "21 nov 2024, 08:00", "Presencial", "Direccion Academica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Capacitacion en modelado de negocios</b>', "Taller",
              "21 nov 2024, 14:00", "Virtual", "Coordinacion Academica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Asesoria grupal de empleabilidad</b>', "Asesoria",
              "26 nov 2024, 10:00", "Presencial", "Bienestar Estudiantil",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))],
             ['<b>Showroom de emprendimientos</b>', "Muestra",
              "02 dic 2024, 09:00", "Presencial", "Direccion Academica",
              _acc(_b("eye", "Ver detalle"), _b("calendar", "Inscribirme"))]],
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
        + card("Como inscribirte",
               '<div style="font-size:13px;color:#162644">Al inscribirte, el evento aparece en '
               "tu panel y recibes recordatorio el dia anterior. Puedes cancelar tu inscripcion "
               "desde el detalle del evento.</div>")
        + "</div></div>"
    )
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Eventos, talleres y asesorias de la institucion.")


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
        callout("Aqui puedes mantener tus datos personales y tu contrasena. Los campos "
                "institucionales los mantiene el administrador de la institucion.", "escudo")
        + '<div style="height:20px"></div>'
        + '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
        + card("Datos personales",
               '<div class="grid g-2" style="gap:0 16px">'
               + campo("Nombres", valor="Mariana") + campo("Apellidos", valor="Lopez Herrera")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Tipo de documento", valor="CC")
               + campo("Numero de documento", valor="1020304050",
                       bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Correo personal", valor="mariana.lopez@correo.com", tipo="email")
               + campo("Correo institucional", valor="mariana.lopez@minutodedios.edu.co",
                       tipo="email", bloqueo="Solo ADMINISTRADOR puede modificarlo.")
               + "</div>"
               + '<div class="grid g-2" style="gap:0 16px">'
               + campo("Telefono fijo", valor="604 123 4567", tipo="tel")
               + campo("Celular", valor="300 555 4412", tipo="tel")
               + "</div>"
               + '<div style="display:flex;justify-content:flex-end;gap:10px">'
               + '<button class="btn btn-secundario">Cancelar</button>'
               + '<button class="btn btn-primario">%s Guardar cambios</button></div>' % ico("check", 16))
        + card("Cambiar contrasena",
               '<div class="grid g-3" style="gap:0 16px">'
               + campo("Contrasena actual", tipo="password", ph="••••••••")
               + campo("Nueva contrasena", tipo="password", ph="Minimo 8 caracteres")
               + campo("Repetir nueva contrasena", tipo="password", ph="••••••••")
               + "</div>"
               '<div style="display:flex;justify-content:flex-end">'
               '<button class="btn btn-secundario">Actualizar contrasena</button></div>')
        + "</div>"
        + '<div class="grid" style="gap:20px">'
        + card("Mi rol en el sistema",
               '<div style="text-align:center;padding:8px 0">'
               '<span class="avatar" style="width:72px;height:72px;margin:0 auto;font-size:20px">ML</span>'
               '<h3 style="margin-top:12px">Mariana Lopez Herrera</h3>'
               '<div style="margin-top:6px">%s</div></div>' % badge("ESTUDIANTE", "b-amarillo", "user"))
        + card("Estado de la cuenta", '<div class="lista-def" style="padding:4px 0">'
             '<div class="def-row"><dt>Estado</dt><dd>%s</dd></div>' % badge("Limitado", "b-amarillo", "lock")
             + '<div class="def-row"><dt>Emprendimientos</dt><dd>2</dd></div>'
             + '<div class="def-row"><dt>Tareas pendientes</dt><dd>4</dd></div>'
             + '<div class="def-row"><dt>Fecha de registro</dt><dd>12 oct 2024</dd></div>'
             "</div>",
             accion='<button class="btn btn-secundario btn-sm">%s Cerrar sesion</button>' % ico("salir", 15))
        + "</div></div>"
    )
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Perfil"],
                 sub="Informacion de tu cuenta y preferencias.")


# --- 16. Notificaciones ------------------------------------------------------
def notificaciones():
    items = [
        (True, "Asesoria confirmada", "Tu asesoria con Carlos Mendoza quedo confirmada para el "
         "martes 12 de noviembre a las 10:00.", "hace 12 minutos", "chat", "asesoria"),
        (True, "Nueva tarea asignada", "Debes subir la evidencia fotografica del punto de venta "
         "antes del 12 de noviembre.", "hace 2 horas", "checklist", "tarea"),
        (True, "Seguimiento registrado", "Carlos Mendoza registro un avance de fase en tu "
         "emprendimiento Sabor y Sabe.", "ayer, 16:40", "trend", "seguimiento"),
        (False, "Correo verificado", "Tu correo institucional quedo verificado correctamente.",
         "28 oct 2024", "escudo", "sistema"),
        (False, "Bienvenida a SGEMD", "Bienvenida al sistema de gestion de emprendimiento "
         "Minuto de Dios.", "12 oct 2024", "rayo", "sistema"),
    ]
    cuerpo = (
        '<div class="grid g-2-1">'
        + '<div class="grid" style="gap:20px">'
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
        + '<div class="grid" style="gap:20px">'
        + card("Filtros", '<div style="display:flex;flex-direction:column;gap:8px">'
             + "".join('<span class="chip%s" data-chip="%s">%s</span>'
                       % (" on" if i == 0 else "", c.lower().replace(" ", "-"), c)
                       for i, c in enumerate(["Todas", "Sin leer", "Tareas", "Asesorias", "Seguimiento"]))
             + "</div>")
        + card("Preferencias de notificacion", '<div class="lista-def" style="padding:4px 0">'
             + "".join(
                 '<div class="def-row"><dt style="flex:1">%s</dt><dd style="flex:0 0 auto">'
                 '<span class="chip on">Activado</span></dd></div>' % t
                 for t in ["Correo electronico", "Notificaciones en el sistema", "Recordatorio de tareas"])
             + '<div class="nota-foot">Un administrador puede ajustar estas preferencias.</div>'
         + "</div>")
        + "</div></div>"
    )
    return shell(R, "perfil", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Alertas de tareas, asesorias y seguimiento.",
                 acciones='<button class="btn btn-secundario">%s Marcar todas como leidas</button>'
                          % ico("check", 16))