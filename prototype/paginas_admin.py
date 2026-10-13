# -*- coding: utf-8 -*-
"""Rol ADMINISTRADOR - 21 pantallas.

Reglas del rol:
  - Gestiona perfiles de docentes y estudiantes, y sus asignaciones.
  - Aprueba solicitudes, crea eventos y modera comentarios.
  - Ve el seguimiento de todos los emprendimientos, no solo los asignados.
  - Exporta reportes en CSV y PDF.
"""

from lib_ui import (
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, lista_def, steps, ico, boton_accion, ico, agenda, distribucion,
    lista_avisos, kanban, linea_tiempo, chip, zona_filtros, boton_exportar,
    steps, tabs, campo_check, campo_radio_cards, campo_archivo, grupo_campos,
    contador,
)
from lib_charts import barras, barras_h, lineas, donut, AZUL, AMAR
import json
import datos_admin as D

R = "administrador"

CONDICION_ACADEMICA = D.CONDICION_ACADEMICA
SEMESTRES = D.SEMESTRES
TIPO_EMPRENDIMIENTO = D.TIPO_EMPRENDIMIENTO

BADGE = {
    "activo": "b-azul",
    "confirmado": "b-azul",
    "finalizada": "b-linea",
    "en revision": "b-amarillo",
    "pendiente": "b-amarillo",
    "vencido": "b-amarillo",
    "aprobado": "b-azul",
    "rechazado": "b-neutra",
    "en espera": "b-amarillo",
    "borrado": "b-neutra",
    "visible": "b-azul",
    "oculto": "b-neutra",
}

ETAPAS = ["FASE 1 - Ideacion", "FASE 2 - Prototipo",
          "FASE 3 - Validacion", "FASE 4 - Formalizacion"]

DOCENTES = [
    ("DOC-014", "Carlos Mendoza", "carlos.mendoza@sgemd.edu.co", "Alimentos",
     "3 h", "8", "Activo"),
    ("DOC-013", "Paula Andrea Rios", "paula.rios@sgemd.edu.co", "Moda",
     "2h", "5", "Activo"),
    ("DOC-012", "Hector Vargas", "hector.vargas@sgemd.edu.co", "Muebles",
     "4h", "6", "Activo"),
    ("DOC-011", "Ninafq Beltran", "nina.beltran@sgemd.edu.co", "Ambiental",
     "3h", "7", "Inactivo"),
    ("DOC-010", "Rafael Nieto", "rafael.nieto@sgemd.edu.co", "Tecnologia",
     "5h", "4", "Activo"),
]

ESTUDIANTES = [
    ("EST-087", "Mariana Lopez", "Alimentos", "Sabor y Sabe",
     "FASE 2 - Prototipo", 62, "Activo"),
    ("EST-086", "Jhon Ospina", "Moda", "Krea Textil",
     "FASE 1 - Ideacion", 28, "Activo"),
    ("EST-085", "Lucia Fernandez", "Ambiental", "EcoPack",
     "FASE 3 - Validacion", 84, "Activo"),
    ("EST-084", "Sofia Ramirez", "Alimentos", "Aromas del Sur",
     "FASE 1 - Ideacion", 15, "Activo"),
    ("EST-083", "Andres Felipe", "Muebles", "Muebles Origen",
     "FASE 2 - Prototipo", 55, "Inactivo"),
]

EMPRENDIMIENTOS = [
    ("EMP-041", "Sabor y Sabe", "Mariana Lopez", "Alimentos", "Comercio",
     "FASE 2 - Prototipo", 62, "Carlos Mendoza"),
    ("EMP-040", "Krea Textil", "Jhon Ospina", "Moda", "Moda",
     "FASE 1 - Ideacion", 28, "Paula Andrea Rios"),
    ("EMP-039", "EcoPack", "Lucia Fernandez", "Ambiental", "Industrial",
     "FASE 3 - Validacion", 84, "Hector Vargas"),
    ("EMP-038", "Aromas del Sur", "Sofia Ramirez", "Alimentos", "Alimentos",
     "FASE 1 - Ideacion", 15, "Sin asignar"),
    ("EMP-037", "Muebles Origen", "Andres Felipe", "Muebles", "Artesanal",
     "FASE 2 - Prototipo", 55, "Ninafq Beltran"),
]


def _b(icono, etiqueta):
    return boton_accion(icono, etiqueta)


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _barra(pct):
    """Barra de avance. Solo el ancho es dinamico: el resto va en la clase,
    para no llenar la pagina de estilos en linea."""
    return ('<div class="barra avance"><span style="width:%d%%"></span></div>'
            '<span class="pct">%d%%</span>' % (pct, pct))


def _sel(etiqueta, opciones, col=None, primera="Todas"):
    """Select de faceta. La primera opcion vale "" para no filtrar nada."""
    opts = '<option value="">%s</option>' % primera if primera else ""
    opts += "".join("<option>%s</option>" % o for o in opciones)
    c = ' data-filtro-col="%s"' % col if col is not None else ""
    return '<select class="filtro" aria-label="%s"%s>%s</select>' % (etiqueta, c, opts)


def registrar(reg):
    paginas_adm = [
        ("dashboard.html", "33 Administrador - Inicio (dashboard)", dashboard),
        ("usuarios.html", "34 Administrador - Gestion de perfiles", usuarios),
        ("usuario-docente.html", "35 Administrador - Editar docente", usuario_docente),
        ("usuario-estudiante.html", "36 Administrador - Editar estudiante", usuario_estudiante),
        ("emprendimientos.html", "37 Administrador - Emprendimientos", emprendimientos),
        ("emprendimiento-plan.html", "38 Administrador - Plan de trabajo del emprendimiento",
         emprendimiento_plan),
        ("seguimiento.html", "39 Administrador - Seguimiento (lista)", seguimiento),
        ("seguimiento-dashboard.html", "40 Administrador - Tablero de seguimiento",
         seguimiento_dashboard),
        ("asignar-emprendimiento.html", "41 Administrador - Asignar emprendimiento",
         asignar_emprendimiento),
        ("comentarios.html", "42 Administrador - Moderacion de comentarios", comentarios),
        ("asesorias.html", "43 Administrador - Metricas de asesorias", asesorias),
        ("eventos.html", "44 Administrador - Eventos", eventos),
        ("evento-form.html", "45 Administrador - Crear evento", evento_form),
        ("asignaciones.html", "46 Administrador - Asignaciones", asignaciones),
        ("trazabilidad.html", "47 Administrador - Trazabilidad de asignaciones",
         trazabilidad),
        ("diagnosticos.html", "48 Administrador - Diagnosticos respondidos", diagnosticos),
        ("reportes.html", "49 Administrador - Exportar reportes", reportes),
        ("sedes-carreras.html", "50 Administrador - Sedes y carreras", sedes_carreras),
        ("perfil.html", "51 Administrador - Mi perfil", perfil),
        ("notificaciones.html", "52 Administrador - Notificaciones", notificaciones),
        ("ayuda.html", "53 Administrador - Ayuda y soporte", ayuda),
        ("inscripciones.html", "54 Administrador - Bandeja de inscripciones", inscripciones),
        ("actas.html", "55 Administrador - Actas de compromiso", actas),
        ("inscripcion-detalle.html", "56 Administrador - Expediente de inscripcion",
         inscripcion_detalle),
        ("caracterizacion-form.html", "57 Administrador - Formulario 2 de caracterizacion",
         caracterizacion_form),
        ("diagnostico-generado.html", "58 Administrador - Caracterizacion y diagnostico",
         diagnostico_generado),
        ("inscripcion-form.html", "59 Administrador - Formulario 1 de inscripcion",
         inscripcion_form),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_adm):
        reg("admin", arch, tit, fn, i)


def _btn(icono, texto, href="#", clase="btn btn-primario"):
    return '<a class="%s" href="%s">%s %s</a>' % (clase, href, ico(icono, 16), texto)


def _b_accion(icono_, etiqueta, accion, extra=""):
    """Boton de accion con intencion propia (data-accion) y atributos extra.

    Los botones de la tabla necesitan datos (codigo, columna) que la heuristica
    por icono no alcanza a expresar; aqui el data-accion llega explicito.
    """
    return ('<button data-accion="%s" title="%s" aria-label="%s"%s>%s</button>'
            % (accion, etiqueta, etiqueta, extra, ico(icono_, 16)))


def _ficha(href, etiqueta, icono_="doc"):
    """Enlace a una pantalla secundaria desde la fila de una tabla."""
    return ('<a class="acc-enlace" href="%s" title="%s" aria-label="%s">%s</a>'
            % (href, etiqueta, etiqueta, ico(icono_, 16)))


def _seed(datos_id, datos):
    """Dataset del administrador para lib_js: JSON embebido en la pagina.

    El CRUD de usuarios y la asignacion de asesoria leen estos datos en tiempo
    de ejecucion; nada viaja por fetch (las pantallas son documentos autonomas).
    """
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return '<script type="application/json" id="%s">%s</script>' % (datos_id, js)


def _esc(txt):
    return (str(txt).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


esc = _esc


def _boton_nuevo(etiqueta, accion="nuevo-fila"):
    return ('<button class="btn btn-primario" data-accion="%s">%s %s</button>'
            % (accion, ico("plus", 16), etiqueta))


def form_acciones(titulo, campos_html, exito="Cambios guardados correctamente",
                  etiqueta="Guardar cambios", extra="", iconos="check",
                  ok_id="acceso-ok", estricto=False):
    """Formulario de verdad (un <form>), no un div con campos sueltos.

    `data-form-simulado` es lo que reconoce _interaccion.py: al enviar en
    blanco marca cada obligatorio con .campo-error y aria-invalid; al enviar
    completo muestra el panel de confirmacion. `ok_id` debe ser unico en la
    pagina: una pantalla puede tener mas de un formulario (el id lo comprueba
    _estructura.py). `estricto` activa ademas la validacion al perder el foco y
    el boton apagado mientras falte algo.
    """
    acciones = ('<div class="form-acciones">'
                '<button type="submit" class="btn btn-primario">%s %s</button>'
                % (ico(iconos, 16), etiqueta))
    if extra:
        acciones += extra
    return card(titulo,
                '<form data-form-simulado data-exito="%s"%s novalidate>%s%s</form>'
                '<div id="%s" class="acceso-ok" role="status" hidden>%s %s</div>'
                '<p class="form-aviso" data-faltan role="status"></p>'
                % (_esc(exito), ' data-validacion="estricta"' if estricto else "",
                   campos_html, acciones + "</div>",
                   ok_id, ico("check", 16), exito))


def tabla_crud(clave, columnas, filas, campos, badges=(), tonos=None, nueva="",
               singular="registro", crear=None, id_tabla=None, id_col=None,
               prefijo="", ancha=False, oculta=None, cortas=None):
    """Tabla que el motor CRUD de lib_js puede crear, editar y borrar.

    columnas: lista de (campo, etiqueta) o (campo, etiqueta, "num").
    filas: lista de dict con una clave por columna (la clave `id_col` identifica).
    campos: campos editables del modal: n, l, t (text/select/area/date/number),
            o (opciones), req, ph, def y ayuda.
    `cortas`: {campo: {valor: etiqueta corta}} para que un enumerado largo
    ocupe una badge en vez de estirar la tabla; el texto completo queda en el
    title de la celda y en el modal de detalle.

    El HTML se pinta aqui para que la lista sea buscable y filtrable como
    cualquier otra tabla; el seed JSON lleva los mismos datos para que el JS
    repinte, edite y persista sin volver al servidor.
    """
    cab = [(c[0], c[1], "num") if len(c) > 2 else c[1] for c in columnas]
    cab.append("@ACC")
    id_campo = id_col or columnas[0][0]
    cuerpo = []
    for f in filas:
        celdas = []
        for c in columnas:
            v = f.get(c[0], "")
            corta = (cortas or {}).get(c[0], {}).get(str(v))
            if corta:
                v = ('<span class="badge b-%s" title="%s">%s</span>'
                     % ((tonos or {}).get(str(v), "linea"), _esc(v), esc(corta)))
            elif c[0] in badges:
                v = badge(str(v), (tonos or {}).get(str(v), "linea"))
            celdas.append(v)
        ident = _esc(f.get(id_campo, ""))
        celdas.append(_acc(
            _b_accion("eye", "Ver detalle", "ver-fila", ' data-id="%s"' % ident),
            _b_accion("edit", "Editar %s" % singular, "editar-fila", ' data-id="%s"' % ident),
            _b_accion("trash", "Eliminar %s" % singular, "borrar-fila", ' data-id="%s"' % ident)))
        cuerpo.append(celdas)
    seed = {
        "clave": clave, "singular": singular,
        "nuevo": nueva or ("Nuevo %s" % singular),
        "crear": crear or ("Crear %s" % singular),
        "id": id_campo, "prefijo": prefijo,
        "columnas": [{"n": c[0], "l": c[1]} for c in columnas],
        "badges": list(badges), "tonos": tonos or {},
        "campos": campos, "filas": filas,
    }
    return (_seed("datos-lista", seed)
            + tabla(cab, cuerpo, id=id_tabla, tbody_attr=" data-crud-tbody",
                    ancha=ancha, oculta=oculta, con_checkbox=True,
                    ordenable=True))


def zona_crud(clave, titulo, columnas, filas, campos, filtros="", chips="",
              singular="registro", nueva=None, badges=(), tonos=None,
              id_col=None, prefijo="", exportar=True, hint="", cuerpo_extra="",
              ancha=False, oculta=None, cortas=None):
    """Tarjeta + zona de filtros + tabla CRUD: el bloque de casi toda pantalla.

    Junta lo que el administrador necesita en cada listado: buscar, afinar por
    facetas, crear, editar, ver, eliminar, restaurar y exportar lo filtrado.
    `ancha` y `oculta` se pasan a tabla(): la primera cambia a vista ficha en
    tablet, la segunda pliega las columnas que sobran por debajo de 1280px.
    """
    etiqueta = nueva or ("Nuevo %s" % singular)
    tid = "tabla-%s" % clave
    acciones = _boton_nuevo(etiqueta)
    if exportar:
        acciones += boton_exportar("Exportar CSV", tabla_id=tid)
    cuerpo = zona_filtros(
        tabla_crud(clave, columnas, filas, campos, badges=badges, tonos=tonos,
                   singular=singular, nueva=etiqueta, id_tabla=tid,
                   id_col=id_col, prefijo=prefijo, ancha=ancha, oculta=oculta,
                   cortas=cortas),
        filtros=filtros, chips=chips, acciones=acciones)
    return card(titulo, cuerpo + cuerpo_extra, hint=hint)


TONOS = {"Activo": "azul", "Aprobado": "azul", "Aprobada": "azul",
         "Confirmada": "azul", "Confirmado": "azul", "Finalizada": "linea",
         "Finalizado": "linea", "Publicado": "azul", "Inactivo": "neutra",
         "Rechazado": "neutra", "Rechazada": "neutra",
         "Oculto": "neutra", "Borrado": "neutra", "Pendiente": "amarillo",
         "En_revision": "amarillo", "Agendada": "amarillo",
         "Borrador": "neutra", "En espera": "amarillo",
         "Sin confirmar": "amarillo", "Vencida": "amarillo",
         "Abierta": "amarillo", "Cerrada": "neutra", "Leida": "linea",
         "En revision": "amarillo", "Verificado": "azul",
         "Al dia": "azul", "En riesgo": "amarillo",
         "Avance parcial": "amarillo", "Alta": "amarillo",
         "Media": "linea", "Baja": "neutra"}


# --- 33. Dashboard -----------------------------------------------------------
def dashboard():
    u = D.resumen()
    cuerpo = metricas([
        ("users", "Estudiantes registrados", str(u["total"]), "", 84, "+12 este mes"),
        ("maleta", "Formalizados", str(u["formalizadas"]), "", 72, None),
        ("alerta", "Sin docente asignado", str(u["sin_docente"]), "", 88, "por asignar"),
        ("medalla", "Avance promedio", str(u["avance_promedio"]), "%", 78, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Emprendimientos por sede", barras(
        "", "", [s for s, _ in D.POR_SEDE], [n for _, n in D.POR_SEDE],
        unidad=" proyectos"))
    cuerpo += card("Estudiantes por tipo de perfil", barras_h(
        "", "", [t for t, _ in D.POR_TIPO], [n for _, n in D.POR_TIPO], color=AMAR))
    cuerpo += zona_filtros(
        tabla(["Fecha", "Accion del administrador", "@ACC"],
              [["%s" % p["fecha"],
                "Cargo el emprendimiento %s (%s)" % (p["codigo"], p["nombre"]),
                _acc(_b("eye", "Ver detalle"))] for p in D.PROYECTOS[:4]],
              id="tabla-actividad"),
        buscar=False,
        acciones=boton_exportar("CSV", tabla_id="tabla-actividad"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Pendientes de decision", lista_def([
        ("Emprendimientos sin docente", str(u["sin_docente"])),
        ("Empresas formalizadas", str(u["formalizadas"])),
        ("Retiros registrados", str(len(D.RETIROS))),
        ("Programas academicos", str(u["programas"])),
    ]))
    cuerpo += card("Proyectos por estado", donut(
        "", "", [(e, c, AZUL if e == "Empresa Formalizada" else
                  (AMAR if e == "Unidad Productiva" else "#bbbbbb"))
                 for e, c in D.POR_ESTADO], "proyectos"))
    cuerpo += "</div></div>"
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama institucional de usuarios, emprendimientos y seguimiento.",
                 acciones=_btn("download", "Exportar reportes", "reportes.html"))


# --- 34. Gestion de perfiles -------------------------------------------------
def usuarios():
    """Docentes (asesores) y estudiantes con datos reales del programa.

    Cada fila lleva botones con data-codigo para que lib_js abra el modal de
    edicion prellenado o alterne el estado de acceso, y la pagina embebe el
    dataset ([data-usuarios]) con todo lo que el modal necesita.
    """
    pro = D.PROYECTOS
    areas = ["Alimentos", "Moda", "Ambiental", "Tecnologia", "Muebles"]
    docentes = []
    filas_doc = []
    for i, nom in enumerate(D.ASESORES):
        est = "Activo" if i != 3 else "Inactivo"
        cod = "DOC-%03d" % (i + 1)
        cor = "%s@sgemd.edu.co" % nom.split()[0].lower().replace("ñ", "n")
        docentes.append({
            "codigo": cod, "nombres": nom, "apellidos": "", "correo": cor,
            "area": areas[i % len(areas)], "carga": str(2 + i),
            "emp": str(5 + i), "estado": est, "tipo": "docente",
        })
        filas_doc.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % nom, badge("Docente", "b-linea"),
            areas[i % len(areas)], "—", "—",
            badge(est, "b-azul" if est == "Activo" else "b-neutra"),
_acc(_b_accion("eye", "Ver ficha del docente", "ver-usuario",
                           ' data-tipo="docente" data-codigo="%s"' % cod),
                  _ficha("usuario-docente.html", "Ficha completa del docente"),
                  _b_accion("edit", "Editar docente", "gestion-usuario",
                            ' data-tipo="docente" data-codigo="%s"' % cod),
                  _b_accion("lock", "Alternar acceso", "alternar-estado",
                            ' data-codigo="%s" data-col="6"' % cod)),
        ])
    estudiantes = []
    filas_est = []
    for i, p in enumerate(pro):
        cod = "EST-%03d" % (i + 1)
        est = "Activo" if i not in (12, 45) else "Inactivo"
        estudiantes.append({
            "codigo": cod, "nombres": p["nombre"], "apellidos": "",
            "correo": "est.%03d@sgemd.edu.co" % (i + 1),
            "programa": p["programa"], "sede": p["sede"],
            "emprendimiento": p["emprendimiento"], "estado": est,
            "tipo": "estudiante",
        })
        filas_est.append([
            "<b>%s</b>" % cod, "<b>%s</b>" % p["nombre"], badge("Estudiante", "b-azul"),
            p["programa"], p["emprendimiento"], badge(p["sede"], "b-linea"),
            badge(est, "b-azul" if est == "Activo" else "b-neutra"),
            _acc(_b_accion("eye", "Ver ficha del estudiante", "ver-usuario",
                             ' data-tipo="estudiante" data-codigo="%s"' % cod),
                  _ficha("usuario-estudiante.html", "Ficha completa del estudiante"),
                  _b_accion("edit", "Editar estudiante", "gestion-usuario",
                            ' data-tipo="estudiante" data-codigo="%s"' % cod),
                  _b_accion("lock", "Alternar acceso", "alternar-estado",
                            ' data-codigo="%s" data-col="6"' % cod)),
        ])
    filas = filas_doc + filas_est
    cuerpo = callout("Los perfiles de estudiante se editan desde su cuenta. El "
                     "administrador puede activar o desactivar el acceso.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("users", "Docentes (asesores)", str(len(D.ASESORES)), "", 40, None),
        ("users", "Estudiantes", str(len(pro)), "", 92, "+11"),
        ("alerta", "Retiros registrados", str(len(D.RETIROS)), "", 6, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_filtros(
        tabla(["Codigo", "Nombre", "Rol", "Programa o area", "Emprendimiento",
               "Sede", "Estado", "@ACC"], filas, id="tabla-usuarios", ancha=True,
        oculta={"md": [4], "sm": [3]}),
        filtros=_sel("Rol", ["Docente", "Estudiante"], col=2)
                 + _sel("Sede", D.SEDES, col=5)
                 + _sel("Programa", D.PROGRAMAS, col=3)
                 + _sel("Estado", ["Activo", "Inactivo"], col=6),
        acciones=boton_exportar("CSV", tabla_id="tabla-usuarios"),
        chips=chip("Activo", col=6) + chip("Inactivo", col=6))
    cuerpo += paginas(1, 10, len(filas))
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += tabs(["Por rol", "Por sede", "Por area"], 0)
    cuerpo += card("Estudiantes por tipo de perfil", barras_h(
        "Estudiantes por tipo de perfil", "Perfil de los estudiantes registrados",
        [t for t, _ in D.POR_TIPO], [n for _, n in D.POR_TIPO], color=AMAR))
    cuerpo += card("Usuarios por sede", barras(
        "Usuarios por sede", "Docentes y estudiantes por campus",
        [s for s, _ in D.POR_SEDE], [n for _, n in D.POR_SEDE],
        unidad=" usuarios"))
    cuerpo += card("Docentes por area", donut(
        "Docentes por area", "Cobertura de las areas de acompanamiento",
        [(a, 2 if a in ("Alimentos", "Moda") else 1, AZUL)
         for a in areas[:5]], "docentes"))
    cuerpo += "</div>"
    cuerpo += _seed("datos-usuarios", {
        "sedes": D.SEDES, "programas": D.PROGRAMAS, "areas": areas,
        "condiciones": CONDICION_ACADEMICA,
        "estudia": D.CONDICION_SI_ESTUDIA,
        "tipos": D.TIPO_EMPRENDIMIENTO,
        "etiqueta_tipo": D.ETIQUETA_TIPO,
        "perfil": D.PERFIL,
        "docentes": docentes, "estudiantes": estudiantes,
    })
    return shell(R, "usuarios", "Gestion de perfiles", cuerpo,
                 migas=["Inicio", "Gestion de perfiles"],
                 sub="Altas, edicion y estado de acceso de docentes y estudiantes.",
                 acciones='<button class="btn btn-primario" data-accion="nuevo-usuario">%s Nuevo usuario</button>'
                          % ico("plus", 16)
                          + boton_exportar("Informe imprimible", tipo="reporte"))


# --- 35. Editar docente ------------------------------------------------------
def usuario_docente():
    """Ficha completa del docente. Antes eran nueve campos; ahora el formulario
    cubre identidad, formacion, disponibilidad, areas y seguridad, y el propio
    formulario guarda con validacion estricta (boton apagado mientras falte)."""
    cuerpo = steps(["Identificacion", "Formacion", "Disponibilidad", "Areas",
                    "Seguridad"], 1)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones(
        "Identificacion",
        grupo_campos("Datos basicos",
                     campo("Codigo", valor="DOC-014",
                           bloqueo="Codigo asignado por el sistema")
                     + campo("Nombres", valor="Carlos Alejandro", req=True, requerido=True)
                     + campo("Apellidos", valor="Mendoza Rios", req=True, requerido=True))
        + grupo_campos("Contacto",
                       campo("Correo institucional", tipo="email",
                             valor="carlos.mendoza@sgemd.edu.co", req=True, requerido=True)
                       + campo("Telefono", tipo="tel", valor="+57 300 555 0142")
                       + campo("Correo alterno", tipo="email", valor="cmendoza@correo.com")),
        exito="Identificacion guardada. El docente recibe un aviso por correo.",
        etiqueta="Guardar identificacion", ok_id="acceso-ok-id", estricto=True)
    cuerpo += form_acciones(
        "Formacion academica",
        select("Titulo profesional", ["Ingeniero", "Licenciado", "Tecnologo",
                                      "Especialista", "Magister"],
               req=True, valor="Ingeniero", requerido=True)
        + campo("Anio de graduacion", tipo="number", valor="2014")
        + select("Universidad", ["Universidad de Ibague", "UNIMINUTO",
                                 "Universidad de los Andes", "SENA"], valor="UNIMINUTO")
        + campo("Titulo de postgrado", valor="Especializacion en gestion de proyectos"),
        exito="Formacion academica guardada.", etiqueta="Guardar formacion",
        ok_id="acceso-ok-form")
    cuerpo += form_acciones(
        "Disponibilidad y agenda",
        campo("Horas de asesoria por semana", tipo="number", valor="3", ph="De 1 a 20")
        + select("Modalidad preferida", ["Presencial", "Virtual", "Mixta"],
                 valor="Mixta")
        + campo("Horario de atencion", valor="Martes y jueves, 14:00 a 17:00")
        + campo("Emprendimientos asignados", tipo="number", valor="8",
                bloqueo="Se actualiza desde Asignaciones"),
        exito="Disponibilidad guardada.", etiqueta="Guardar disponibilidad",
        ok_id="acceso-ok-disp")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Area de conocimiento", campo_radio_cards(
        "Area principal",
        ["Alimentos", "Moda", "Ambiental", "Tecnologia", "Muebles"],
        valor="Alimentos"))
    cuerpo += card("Areas secundarias", campo_check(
        "Puede acompanar en otras areas", ayuda="Amplia su disponibilidad"),
        campo_check("Acompana Volcanoes", ayuda="Marcar si aplica"),
        campo_check("Coordina brigadas", ayuda="Marcar si aplica"))
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Ultimo acceso", "Hoy, 07:42"),
        ("Asesorias realizadas", "31"),
        ("Promedio de calificacion", "89 de 100"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-secundario" data-accion="alternar-estado">%s Desactivar acceso</button>'
                     % ico("lock", 16)
                   + '<a class="btn btn-secundario" href="usuarios.html">%s Volver</a>'
                     % ico("izq", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "historial-docente", "Historial de cambios",
        [("codigo", "Codigo"), ("fecha", "Fecha"), ("campo", "Campo"),
         ("antes", "Valor anterior"), ("despues", "Valor nuevo")],
        [{"codigo": "HIS-%03d" % (i + 1), "fecha": f, "campo": c,
          "antes": a, "despues": d}
         for i, (f, c, a, d) in enumerate([
             ("12 nov 2024", "Horas de asesoria", "2 h", "3 h"),
             ("28 oct 2024", "Area de conocimiento", "Moda", "Alimentos"),
             ("15 oct 2024", "Correo institucional", "cmendoza@correo.com",
              "carlos.mendoza@sgemd.edu.co"),
         ])],
        [{"n": "fecha", "l": "Fecha", "t": "date", "req": True},
         {"n": "campo", "l": "Campo modificado", "t": "text", "req": True},
         {"n": "antes", "l": "Valor anterior", "t": "text"},
         {"n": "despues", "l": "Valor nuevo", "t": "text", "req": True}],
        singular="cambio", nueva="Registrar cambio", prefijo="HIS-",
        exportar=False,
        hint="Todo cambio en la ficha queda registrado: el docente puede "
             "saber quien modifico que.")
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "carga-docente", "Emprendimientos asignados al docente",
        [("codigo", "Codigo"), ("emprendimiento", "Emprendimiento"),
         ("estudiante", "Estudiante"), ("sede", "Sede"),
         ("etapa", "Etapa"), ("estado", "Estado")],
        [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
          "estudiante": p["nombre"], "sede": p["sede"], "etapa": p["etapa"],
          "estado": "En curso" if p["docente"] != "Sin asignar" else "Sin asignar"}
         for p in D.PROYECTOS if p["docente"] != "Sin asignar"][:8],
        [{"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "sede", "l": "Sede", "t": "select", "o": D.SEDES, "req": True},
         {"n": "etapa", "l": "Etapa", "t": "select", "o": ETAPAS, "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["En curso", "Finalizado", "Reasignado"]}],
        singular="asignacion", nueva="Nueva asignacion", prefijo="AD-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Sede", D.SEDES, col=3),
        hint="Aqui se reflejan los cambios hechos desde Asignaciones.")
    return shell(R, "usuarios", "Editar docente", cuerpo,
                 migas=["Inicio", "Gestion de perfiles", "Editar docente"],
                 sub="Actualiza los datos institutionales del docente.",
                 acciones=_btn("check", "Guardar"))


# --- 36. Editar estudiante ---------------------------------------------------
def usuario_estudiante():
    """Ficha del estudiante. El estudiante edita su cuenta: el administrador no
    toca nombre ni correo, pero si mantiene los datos que el servicio necesita
    para el flujo (contacto, direccion, condicion academica, emergencia) y
    controla el acceso."""
    cuerpo = callout("El estudiante edita su cuenta: nombre, apellidos y correo no "
                     "se tocan aqui. El administrador mantiene los datos de "
                     "contacto, la condicion academica y el acceso.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("trend", "Avance del emprendimiento", "62", "%", 62, "FASE 2"),
        ("chat", "Asesorias recibidas", "3", "", 40, None),
        ("medalla", "Calificacion promedio", "91", "/ 100", 91, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones(
        "Identificacion",
        grupo_campos("Datos que edita el estudiante",
                     campo("Codigo", valor="EST-087",
                           bloqueo="Codigo asignado por el sistema")
                     + campo("Nombres", valor="Mariana",
                             bloqueo="Los edita el estudiante")
                     + campo("Apellidos", valor="Lopez",
                             bloqueo="Los edita el estudiante")
                     + campo("Correo institucional", tipo="email",
                             valor="mariana.lopez@sgemd.edu.co",
                             bloqueo="Los edita el estudiante")),
        exito="Identificacion sin cambios.", etiqueta="Guardar identificacion",
        ok_id="acceso-ok-est-id")
    cuerpo += form_acciones(
        "Contacto",
        campo("Correo alterno", tipo="email", valor="mariana.personal@correo.com")
        + campo("Telefono", tipo="tel", valor="+57 315 555 0140")
        + campo("Direccion", valor="Calle 12 #4-56, Ibague")
        + campo("Ciudad", valor="Ibague")
        + campo("Fecha de nacimiento", tipo="date", valor="2002-08-14")
        + select("Genero", ["Femenino", "Masculino", "Otro", "Prefiere no decir"],
                 valor="Femenino"),
        exito="Datos de contacto guardados.", etiqueta="Guardar contacto",
        ok_id="acceso-ok-est-cont", estricto=True)
    cuerpo += form_acciones(
        "Condicion academica",
        select("Condicion academica", CONDICION_ACADEMICA,
               req=True, valor="Estudiante Pregrado", requerido=True)
        + campo("Semestre", tipo="number", valor="6",
                ayuda="Solo aplica si sigue estudiando")
        + select("Programa", D.PROGRAMAS, req=True,
                 valor="Licenciatura en Educacion Infantil", requerido=True)
        + select("Tipo de emprendimiento", D.TIPO_EMPRENDIMIENTO,
                 req=True, valor="Idea de negocio", requerido=True,
                 bloqueo="Se define en la inscripcion y no se cambia aqui"),
        exito="Condicion academica guardada.", etiqueta="Guardar condicion",
        ok_id="acceso-ok-est-cond")
    cuerpo += form_acciones(
        "Emergencia y datos personales",
        campo("Nombre del contacto de emergencia", valor="Claudia Lopez",
              req=True, requerido=True)
        + campo("Telefono de emergencia", tipo="tel", valor="+57 315 555 0199",
                req=True, requerido=True)
        + campo("Parentesco", valor="Madre")
        + campo_check("Autorizo el tratamiento de mis datos personales",
                      ayuda="Obligatorio para gestionar el acompañamiento",
                      marcado=True, requerido=True),
        exito="Contacto de emergencia y autorizacion guardados.",
        etiqueta="Guardar emergencia", ok_id="acceso-ok-est-emg", estricto=True)
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Emprendimiento y etapa", lista_def([
        ("Emprendimiento", "Sabor y Sabe"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente asignado", "Carlos Mendoza"),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Estado del acceso", lista_def([
        ("Estado", "Activo"),
        ("Fecha de registro", "12 mar 2024"),
        ("Ultimo acceso", "Hoy, 08:02"),
        ("Asesorias recibidas", "3"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-secundario" data-accion="alternar-estado">%s Desactivar acceso</button>'
                     % ico("lock", 16)
                   + '<a class="btn btn-secundario" href="usuarios.html">%s Volver</a>'
                     % ico("izq", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "academico-estudiante", "Condicion academica del estudiante",
        [("codigo", "Codigo"), ("estudiante", "Estudiante"),
         ("condicion", "Condicion academica"), ("semestre", "Semestre"),
         ("programa", "Programa"), ("estado", "Estado")],
        [{"codigo": "AC-0%d" % (i + 1), "estudiante": p["nombre"],
          "condicion": "Estudiante Pregrado" if i % 3 else "Egresado Pregrado",
          "semestre": "" if i % 3 == 2 else str(3 + (i % 7)),
          "programa": p["programa"], "estado": "Verificado"}
         for i, p in enumerate(D.PROYECTOS[:6])],
        [{"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "condicion", "l": "Condicion academica", "t": "select",
          "o": CONDICION_ACADEMICA, "req": True},
         {"n": "semestre", "l": "Semestre", "t": "number",
          "ayuda": "Solo aplica si el estudiante sigue studying"},
         {"n": "programa", "l": "Programa", "t": "select",
          "o": D.PROGRAMAS, "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Verificado", "Pendiente"]}],
        singular="condicion", nueva="Nueva condicion", prefijo="AC-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Condicion", CONDICION_ACADEMICA, col=2)
                 + _sel("Estado", ["Verificado", "Pendiente"], col=5)),
        hint="El semestre solo se diligencia cuando la condicion academica "
             "indica que sigue estudiando.")
    return shell(R, "usuarios", "Editar estudiante", cuerpo,
                 migas=["Inicio", "Gestion de perfiles", "Editar estudiante"],
                 sub="Gestiona el acceso del estudiante a la plataforma.",
                 acciones=_btn("check", "Guardar"))


# --- 37. Emprendimientos -----------------------------------------------------
def emprendimientos():
    """Registro maestro: los 90 emprendimientos reales con facetas y descarga."""
    pro = D.PROYECTOS
    cuerpo = callout("Como administrador tu ves <b>todos</b> los emprendimientos, "
                     "tengan o no docente asignado.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("maleta", "Total registrados", str(D.resumen()["total"]), "", 72, "+5"),
        ("trend", "Empresas formalizadas", str(D.resumen()["formalizadas"]), "", 62, None),
        ("alerta", "Sin docente asignado", str(D.resumen()["sin_docente"]), "", 18, None),
    ])
    cuerpo += '<div class="sep"></div>'
    filas = []
    for p in pro:
        estado = p["estado"]
        filas.append([
            "<b>%s</b>" % p["emprendimiento"], "<b>%s</b>" % p["codigo"],
            p["nombre"], p["programa"], badge(p["sede"], "b-linea"),
            badge(p["etapa"], "b-linea"), _barra(p["avance"]),
            p["docente"] if p["docente"] != "Sin asignar"
            else badge("Sin asignar", "b-amarillo"),
            _acc(_b("eye", "Abrir plan"),
                  _ficha("emprendimiento-plan.html", "Abrir plan", "trend"),
                  _b_accion("edit", "Editar", "editar",
                            ' data-codigo="%s"' % p["codigo"]),
                  _b_accion("trash", "Retirar emprendimiento",
                            "retirar-emprendimiento",
                            ' data-codigo="%s"' % p["codigo"])),
        ])
    cuerpo += zona_filtros(
        tabla(["Empresa", "Codigo", "Estudiante", "Programa", "Sede",
               "Etapa", "Avance", "Docente asignado", "@ACC"],
              filas, id="tabla-emprendimientos", ancha=True,
              oculta={"lg": [5], "md": [3], "sm": [2]}),
        filtros=_sel("Sede", D.SEDES, col=4)
                 + _sel("Programa", D.PROGRAMAS, col=3)
                 + _sel("Etapa", sorted({p["etapa"] for p in pro}), col=5)
                 + _sel("Docente", D.ASESORES + ["Sin asignar"], col=7),
        acciones=boton_exportar("CSV", tabla_id="tabla-emprendimientos")
                 + boton_exportar("Informe imprimible", tipo="reporte")
                 + _boton_nuevo("Nuevo emprendimiento", "nuevo-emprendimiento"),
        chips=chip("Sin docente", col=7))
    cuerpo += paginas(1, 10, len(pro))
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Emprendimientos por sede", barras(
        "Emprendimientos por sede", "Distribucion institucional",
        [s for s, _ in D.POR_SEDE], [n for _, n in D.POR_SEDE],
        unidad=" proyectos"))
    cuerpo += card("Estado de cada emprendimiento", donut(
        "Estado del emprendimiento", "Las tres categorias del proceso",
        [(e, n, AZUL if e == "Empresa Formalizada" else
          (AMAR if e == "Unidad Productiva" else "#bbbbbb"))
         for e, n in D.POR_ESTADO], "emprendimientos"))
    cuerpo += card("Ultimas altas al programa", linea_tiempo([
        (pro[0]["fecha"].split()[0], pro[0]["fecha"].split()[1].upper()[:3],
         "Alta de %s" % pro[0]["emprendimiento"],
         "%s · %s" % (pro[0]["nombre"], pro[0]["sede"]),
         badge(pro[0]["estado"], "b-linea")),
        (pro[1]["fecha"].split()[0], pro[1]["fecha"].split()[1].upper()[:3],
         "Alta de %s" % pro[1]["emprendimiento"],
         "%s · %s" % (pro[1]["nombre"], pro[1]["sede"]),
         badge(pro[1]["estado"], "b-linea")),
        (pro[2]["fecha"].split()[0], pro[2]["fecha"].split()[1].upper()[:3],
         "Alta de %s" % pro[2]["emprendimiento"],
         "%s · %s" % (pro[2]["nombre"], pro[2]["sede"]),
         badge(pro[2]["estado"], "b-linea")),
    ]))
    cuerpo += "</div>"
    cuerpo += _seed("datos-asignacion", {
        "asesores": D.ASESORES,
        "sin_docente": [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
                         "nombre": p["nombre"], "programa": p["programa"]}
                        for p in pro if p["docente"] == "Sin asignar"],
    })
    return shell(R, "emprendimientos", "Emprendimientos", cuerpo,
                 migas=["Inicio", "Emprendimientos"],
                 sub="Todos los emprendimientos registrados en el programa.",
                 acciones='<button class="btn btn-primario" data-accion="asignar-asesoria">%s Asignar asesoria</button>'
                          % ico("user", 16)
                          + _btn("sliders", "Asignar emprendimiento",
                                 "asignar-emprendimiento.html", "btn btn-secundario"))


# --- 38. Plan de trabajo -----------------------------------------------------
def emprendimiento_plan():
    """Plan operativo del admin: fases, carga y estado, sin notas academicas."""
    cuerpo = metricas([
        ("layers", "Fases completadas", "1", "/ 4", 25, "FASE 2 en curso"),
        ("checklist", "Tareas en curso", "4", "/ 11", 36, "2 sin responsable"),
        ("reloj", "Dias sin avance", "6", "", 40, "Ultimo: 05 nov 2024"),
        ("calendar", "Asesorias programadas", "3", "", 60, "1 por confirmar"),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Plan de trabajo por fase", tabla(
        ["Fase", "Tareas", "Completadas", "Avance", "Estado", "@ACC"],
        [[badge(ETAPAS[0], "b-linea"), "3", "3", "100%",
          badge("Finalizada", "b-azul"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[1], "b-linea"), "5", "4", "80%",
          badge("En curso", "b-amarillo"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[2], "b-linea"), "4", "1", "25%",
          badge("Pendiente", "b-neutra"), _acc(_b("eye", "Ver detalle"))],
         [badge(ETAPAS[3], "b-linea"), "2", "0", "0%",
          badge("No iniciada", "b-neutra"), _acc(_b("eye", "Ver detalle"))]],
        oculta={"sm": [1, 2], "md": [2]}))
    cuerpo += card("Hitos de la fase actual", linea_tiempo([
        ("12", "nov", "Cierre de prototipo y control de calidad",
         "Responsable: Mariana Lopez · 5 tareas abiertas",
         '<div style="margin-top:10px">' + badge("En curso", "b-amarillo", "reloj")
         + '</div>'),
        ("20", "nov", "Revision tecnica con el docente",
         "Responsable: Carlos Mendoza · Confirmado",
         '<div style="margin-top:10px">' + badge("Confirmado", "b-azul", "check")
         + '</div>'),
        ("28", "nov", "Prueba de ventas en punto real",
         "Responsable: equipo del emprendimiento · Sin asignar",
         '<div style="margin-top:10px">' + badge("Sin asignar", "b-amarillo")
         + '</div>'),
        ("05", "dic", "Evaluacion y cierre de FASE 2",
         "Comite academico · Pendiente",
         '<div style="margin-top:10px">' + badge("Pendiente", "b-neutra")
         + '</div>'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Codigo", "EMP-041"),
        ("Nombre", "Sabor y Sabe"),
        ("Tipo", "Comercio"),
        ("Sector", "Alimentos"),
        ("Etapa", "FASE 2 - Prototipo"),
        ("Docente", "Carlos Mendoza"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<a class="btn btn-primario" href="seguimiento-dashboard.html">'
                     "%s Ver seguimiento</a>" % ico("trend", 16)
                   + '<a class="btn btn-secundario" href="asignar-emprendimiento.html">'
                     "%s Reasignar docente</a>" % ico("sliders", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "tareas", "Tareas del plan de trabajo",
        [("codigo", "Codigo"), ("tarea", "Tarea"), ("fase", "Fase"),
         ("responsable", "Responsable"), ("vencimiento", "Vence"),
         ("estado", "Estado")],
        [{"codigo": "TSK-%03d" % (i + 1), "tarea": t, "fase": f,
          "responsable": r, "vencimiento": v, "estado": e}
         for i, (t, f, r, v, e) in enumerate([
             ("Definir precio de venta unitario", ETAPAS[1], "Mariana Lopez",
              "12 nov 2024", "Finalizada"),
             ("Registrar compras de insumos", ETAPAS[1], "Mariana Lopez",
              "12 nov 2024", "Finalizada"),
             ("Revision tecnica con el docente", ETAPAS[1], "Carlos Mendoza",
              "20 nov 2024", "En revision"),
             ("Prueba de ventas en punto real", ETAPAS[1], "Sin asignar",
              "28 nov 2024", "Pendiente"),
             ("Evaluacion y cierre de FASE 2", ETAPAS[1], "Comite academico",
              "05 dic 2024", "Pendiente"),
             ("Diseno de la etiqueta", ETAPAS[0], "Mariana Lopez",
              "05 nov 2024", "Finalizada"),
         ])],
        [{"n": "tarea", "l": "Tarea", "t": "text", "req": True},
         {"n": "fase", "l": "Fase", "t": "select", "o": ETAPAS, "req": True},
         {"n": "responsable", "l": "Responsable", "t": "select",
          "o": ["Mariana Lopez", "Carlos Mendoza", "Sin asignar",
                "Comite academico"], "req": True},
         {"n": "vencimiento", "l": "Vence", "t": "date", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Pendiente", "En revision", "Finalizada", "Vencida"]}],
        singular="tarea", nueva="Nueva tarea",
        oculta={"sm": [2]}, prefijo="TSK-",
        badges=("estado", "fase"), tonos=TONOS,
        filtros=(_sel("Estado", ["Pendiente", "En revision", "Finalizada",
                                 "Vencida"], col=5)
                 + _sel("Responsable", ["Mariana Lopez", "Carlos Mendoza",
                                         "Sin asignar"], col=3)),
        chips=(chip("Sin responsable", col=3, valor="Sin asignar")
               + chip("Vencidas", col=5, valor="Vencida")),
        hint="El docente crea las tareas; el administrador puede reasignarlas "
             "o cerrarlas.")
    return shell(R, "emprendimientos", "Plan de trabajo", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Plan de trabajo"],
                 sub="Plan, fases y carga de trabajo del emprendimiento EMP-041.",
                 acciones='<a class="btn btn-secundario" href="emprendimientos.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 39. Seguimiento (lista) -------------------------------------------------
def seguimiento():
    """Salud global primero; la tabla es solo la cola de alertas."""
    pro = D.PROYECTOS
    al_dia = sum(1 for p in pro if p["avance"] >= 55)
    riesgo = sum(1 for p in pro if p["avance"] < 30)
    medio = len(pro) - al_dia - riesgo
    pct_al = round(al_dia * 100 / len(pro))
    cuerpo = callout("Vista institucional del seguimiento. El docente registra los "
                     "avances de los emprendimientos asignados.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("trend", "Al dia", str(al_dia), "", pct_al, None),
        ("alerta", "En riesgo (<30%)", str(riesgo), "", round(riesgo * 100 / max(1, len(pro))), None),
        ("alerta", "Avance parcial", str(medio), "", round(medio * 100 / len(pro)), None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Salud del seguimiento", '<div class="card-body">'
                   + distribucion([
                       ("Al dia", str(al_dia), pct_al),
                       ("Avance parcial", str(medio), round(medio * 100 / len(pro))),
                       ("En riesgo", str(riesgo), round(riesgo * 100 / len(pro))),
                   ])
                   + '<p class="nota-foot">%d de %d emprendimientos avanzan dentro '
                     'del plazo de la fase actual.</p></div>' % (al_dia, len(pro)))
    alertas = []
    for p in pro:
        if p["avance"] < 60:
            alertas.append((
                "trend", "%s · %s" % (p["emprendimiento"], p["nombre"]),
                "%s · %s · %d%% de avance" % (p["etapa"], p["docente"], p["avance"]),
                "emprendimiento-plan.html",
                "alta" if p["avance"] < 30 else "media",
                _b("edit", "Registrar avance") + " " + _b("eye", "Ver detalle")))
    cuerpo += card("Requieren atencion (%d)" % len(alertas),
                   '<div class="card-body">'
                   + lista_avisos([("Sin avance reciente", alertas[:6])])
                   + '</div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    carga = {}
    for p in pro:
        d = p["docente"]
        if d != "Sin asignar":
            carga[d] = carga.get(d, 0) + 1
    mx = max(carga.values()) if carga else 1
    cuerpo += card("Docentes con mayor carga", '<div class="card-body">'
                   + distribucion([(n, str(c), round(c * 100 / mx))
                                   for n, c in sorted(carga.items(),
                                                      key=lambda kv: kv[1], reverse=True)[:5]])
                   + '</div>')
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + _btn("grid", "Ver tablero", "seguimiento-dashboard.html",
                          "btn btn-secundario")
                   + _btn("download", "Exportar", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += card("Avance por sede", barras(
        "Avance por sede", "Promedio institucional de cada campus",
        [s for s, _ in D.POR_SEDE],
        [round(sum(p["avance"] for p in pro if p["sede"] == s)
               / max(1, sum(1 for p in pro if p["sede"] == s)))
         for s, _ in D.POR_SEDE], maximo=100, unidad="%"))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "seguimiento", "Tabla de seguimiento",
        [("codigo", "Codigo"), ("emprendimiento", "Emprendimiento"),
         ("estudiante", "Estudiante"), ("docente", "Docente"),
         ("etapa", "Etapa"), ("avance", "Avance", "num"), ("estado", "Estado")],
        [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
          "estudiante": p["nombre"], "docente": p["docente"], "etapa": p["etapa"],
          "avance": p["avance"],
          "estado": "Al dia" if p["avance"] >= 55 else
                    ("En riesgo" if p["avance"] < 30 else "Avance parcial")}
         for p in pro[:14]],
        [{"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "docente", "l": "Docente", "t": "select",
          "o": D.ASESORES + ["Sin asignar"], "req": True},
         {"n": "etapa", "l": "Etapa", "t": "select", "o": ETAPAS, "req": True},
         {"n": "avance", "l": "Avance (%)", "t": "number", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Al dia", "Avance parcial", "En riesgo"]}],
        singular="seguimiento", nueva="Nuevo seguimiento",
        ancha=True, oculta={"sm": [3]}, prefijo="SEG-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Docente", list(D.ASESORES) + ["Sin asignar"], col=3)
                 + _sel("Estado", ["Al dia", "Avance parcial", "En riesgo"], col=6)),
        chips=(chip("Al dia", col=6, valor="Al dia")
               + chip("En riesgo", col=6, valor="En riesgo")),
        hint="La tabla es el respaldo editable de las barras de arriba.")
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Salud del seguimiento de los %d emprendimientos." % len(pro))


# --- 40. Tablero de seguimiento ----------------------------------------------
def seguimiento_dashboard():
    pro = D.PROYECTOS
    cuerpo = metricas([
        ("trend", "Avances del mes", "61", "", 88, "+14"),
        ("checklist", "Tareas sin calificar", "11", "", 34, None),
        ("alerta", "Emprendimientos en riesgo", "9", "", 20, None),
        ("medalla", "Promedio institucional", "87", "", 87, "+2"),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Avance acumulado por mes", lineas(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"],
        [("Avances", [12, 19, 27, 41, 61], AZUL),
         ("Tareas", [9, 14, 20, 33, 52, ], AMAR)], unidad=""))
    cuerpo += card("Avance por emprendimiento", barras_h(
        "", "", [e[1] for e in EMPRENDIMIENTOS], [e[6] for e in EMPRENDIMIENTOS],
        maximo=100, unidad="%"))
    cuerpo += card("Rendimiento por docente", barras(
        "", "", ["C. Mendoza", "P. Rios", "H. Vargas", "N. Beltran", "R. Nieto"],
        [92, 86, 84, 78, 74], maximo=100, unidad=" de 100"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Salud de los seguimiento", donut(
        "", "", [("Al dia", 31, AZUL), ("En riesgo", 9, AMAR),
                 ("Inactivos", 6, "#bbbbbb")], "emprendimientos"))
    cuerpo += card("Acciones sugeridas", lista_def([
        ("Asignar docente a 3 emprendimientos", "Sin asignar"),
        ("Contactar 6 estudiantes inactivos", "15 dias sin avance"),
        ("Revisar 5 diagnosticos", "Sin revision"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "alertas", "Emprendimientos en riesgo",
        [("codigo", "Codigo"), ("emprendimiento", "Emprendimiento"),
         ("docente", "Docente"), ("motivo", "Motivo"),
         ("estado", "Estado")],
        [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
          "docente": p["docente"],
          "motivo": "Sin avance desde hace 15 dias",
          "estado": "Abierta" if p["avance"] < 30 else "En revision"}
         for p in sorted(pro, key=lambda x: x["avance"])[:8]],
        [{"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "docente", "l": "Docente", "t": "select",
          "o": D.ASESORES + ["Sin asignar"], "req": True},
         {"n": "motivo", "l": "Motivo", "t": "area", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Abierta", "En revision", "Cerrada"]}],
        singular="alerta", nueva="Nueva alerta", prefijo="ALT-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Estado", ["Abierta", "En revision", "Cerrada"], col=4),
        chips=(chip("Abiertas", col=4, valor="Abierta")
               + chip("Cerradas", col=4, valor="Cerrada")),
        hint="Cada alerta cerrada exige un motivo en el plan de trabajo.")
    return shell(R, "seguimiento", "Tablero de seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Tablero"],
                 sub="Metricas consolidadas de seguimiento institucional.",
                 acciones=_btn("download", "Exportar", "reportes.html", "btn btn-secundario"))


# --- 41. Asignar emprendimiento ---------------------------------------------
def asignar_emprendimiento():
    sin_doc = [p for p in D.PROYECTOS if p["docente"] == "Sin asignar"]
    carga = {}
    for p in D.PROYECTOS:
        d = p["docente"]
        if d != "Sin asignar":
            carga[d] = carga.get(d, 0) + 1
    cuerpo = steps(["Seleccionar emprendimiento", "Elegir docente",
                    "Confirmar asignación"], 1)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Emprendimiento sin docente (%d de %d)" % (min(8, len(sin_doc)), len(sin_doc)), tabla(
        ["Codigo", "Emprendimiento", "Estudiante", "Sector", "Etapa", "@ACC"],
        [["<b>%s</b>" % p["codigo"], "<b>%s</b>" % p["emprendimiento"], p["nombre"],
          p["programa"], badge(p["etapa"], "b-linea"),
          _acc(_b_accion("check", "Seleccionar", "seleccionar",
                         ' data-codigo="%s"' % p["codigo"]))]
         for p in sin_doc[:8]], oculta={"sm": [1, 3], "md": [3]}))
    cuerpo += card("Docente disponible", tabla(
        ["Docente", "Area", "Carga actual", "Horas disponibles", "@ACC"],
        [["<b>%s</b>" % d, p, "%d h de 12 h" % min(12, carga.get(d, 0)),
          "%d h" % max(0, 12 - min(12, carga.get(d, 0))),
          _acc(_b_accion("check", "Seleccionar", "seleccionar",
                         ' data-docente="%s"' % d))]
for d, p in zip(D.ASESORES, ["Alimentos", "Moda", "Ambiental",
                                       "Tecnologia", "Muebles"])], oculta={"sm": [1]}))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Asignacion seleccionada", lista_def([
        ("Emprendimiento", "Aromas del Sur"),
        ("Estudiante", "Sofia Ramirez"),
        ("Docente", "Carlos Mendoza"),
        ("Horas asignadas", "2 h por semana"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-primario" data-accion="confirmar-asignacion">%s Confirmar asignación</button>'
                     % ico("check", 16)
                   + "<button class='btn btn-secundario' data-accion='cancelar-asignacion'>%s Cancelar</button>"
                     % ico("x", 16)
                   + "</div>"
                     '<div class="nota-foot">El docente y el estudiante reciben una '
                     "notificacion con la asignacion.</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "sin-docente", "Pendientes de asignar docente",
        [("codigo", "Codigo"), ("emprendimiento", "Emprendimiento"),
         ("estudiante", "Estudiante"), ("sede", "Sede"),
         ("programa", "Programa"), ("prioridad", "Prioridad")],
        [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
          "estudiante": p["nombre"], "sede": p["sede"], "programa": p["programa"],
          "prioridad": "Alta" if p["avance"] >= 50 else "Media"}
         for p in sin_doc[:12]],
        [{"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "sede", "l": "Sede", "t": "select", "o": D.SEDES, "req": True},
         {"n": "programa", "l": "Programa", "t": "select",
          "o": D.PROGRAMAS, "req": True},
         {"n": "prioridad", "l": "Prioridad", "t": "select",
          "o": ["Alta", "Media", "Baja"], "def": "Media", "req": True}],
        singular="pendiente", nueva="Nuevo pendiente",
        oculta={"sm": [4]}, prefijo="PEN-",
        badges=("prioridad",), tonos=TONOS,
        filtros=(_sel("Sede", D.SEDES, col=3)
                 + _sel("Prioridad", ["Alta", "Media", "Baja"], col=5)),
        chips=chip("Prioridad alta", col=5, valor="Alta"),
        hint="Un empathize solo sale de esta lista cuando tiene docente asignado.")
    return shell(R, "asignaciones", "Asignar emprendimiento", cuerpo,
                 migas=["Inicio", "Asignaciones", "Asignar emprendimiento"],
                 sub="Asigna un docente a los emprendimientos que aun no lo tienen.",
                 acciones='<a class="btn btn-secundario" href="asignaciones.html">%s Volver</a>'
                          % ico("izq", 16))


# --- 42. Moderacion de comentarios -------------------------------------------
def comentarios():
    """Dos colas lado a lado: lo reportado y lo visible. Sin tabla."""
    cuerpo = callout("Solo los comentarios <b>reportados</b> requieren moderacion. "
                     "Borrar un comentario es permanente.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("alerta", "Reportados", "3", "", 25, None),
        ("chat", "Visibles", "27", "", 90, "+4"),
        ("trash", "Borrados este mes", "2", "", 12, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Cola de moderacion (3)", lista_avisos([
        ("Requieren decision", [
            ("chat", "Comentario reportado en Sabor y Sabe",
             "Estudiante · EMP-041 · 12 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Lenguaje inapropiado en Krea Textil",
             "Docente · EMP-040 · 12 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
            ("chat", "Comentario duplicado en EcoPack",
             "Estudiante · EMP-039 · 11 nov 2024", "comentarios.html",
             "alta", _b("check", "Aprobar") + " " + _b("trash", "Borrar")),
        ]),
    ]))
    cuerpo += card("Publicados recientemente", '<div class="card-body">'
                   + '<div class="grid" style="gap:10px">'
                   + '<div class="fila-simple"><div><b>Consulta sobre el evento de costos</b>'
                     '<div class="nota-foot">Docente · EMP-041 · 10 nov 2024</div></div>'
                     '<div class="fila-acciones">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Sugerencia para el plan de trabajo</b>'
                     '<div class="nota-foot">Docente · EMP-037 · 09 nov 2024</div></div>'
                     '<div class="fila-acciones">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '<div class="fila-simple"><div><b>Duda sobre el costo de insumos</b>'
                     '<div class="nota-foot">Estudiante · EMP-035 · 08 nov 2024</div></div>'
                     '<div class="fila-acciones">' + _b("eye", "Ver")
                     + _b("x", "Ocultar") + '</div></div>'
                   + '</div></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Reglas de moderacion", lista_def([
        ("Reportado", "3 en cola"),
        ("Visible", "27 publicados"),
        ("Oculto", "5 ocultos"),
        ("Borrado", "2 este mes"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<a class="btn btn-primario" href="comentarios.html">%s '
                     'Moderar cola</a>' % ico("check", 16)
                   + '<a class="btn btn-secundario" href="reportes.html">%s '
                     'Ver reportes</a>' % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "comentarios", "Cola de moderacion",
        [("codigo", "Codigo"), ("comentario", "Comentario"),
         ("autor", "Autor"), ("emprendimiento", "Emprendimiento"),
         ("motivo", "Motivo del reporte"), ("estado", "Decision")],
        [{"codigo": "CMT-0%d" % (i + 1), "comentario": c, "autor": a,
          "emprendimiento": e, "motivo": m, "estado": "Pendiente"}
         for i, (c, a, e, m) in enumerate([
             ("Comentario reportado en Sabor y Sabe", "Estudiante",
              "EMP-041", "Lenguaje inapropiado"),
             ("Lenguaje inapropiado en Krea Textil", "Docente",
              "EMP-040", "Lenguaje inapropiado"),
             ("Comentario duplicado en EcoPack", "Estudiante",
              "EMP-039", "Contenido duplicado"),
         ])],
        [{"n": "comentario", "l": "Comentario", "t": "area", "req": True},
         {"n": "autor", "l": "Autor", "t": "select",
          "o": ["Estudiante", "Docente", "Administrador"], "req": True},
         {"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "motivo", "l": "Motivo del reporte", "t": "text", "req": True},
         {"n": "estado", "l": "Decision", "t": "select",
          "o": ["Pendiente", "Aprobado", "Oculto", "Borrado"]}],
        singular="comentario", nueva="Nuevo comentario",
        oculta={"sm": [2]}, prefijo="CMT-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Decision", ["Pendiente", "Aprobado", "Oculto",
                                   "Borrado"], col=5),
        chips=(chip("Pendientes", col=5, valor="Pendiente")
               + chip("Borrados", col=5, valor="Borrado")),
        hint="Borrar un comentario es definitivo; las demas decisiones quedan "
             "registradas en la columna Decision.")
    return shell(R, "comentarios", "Moderacion de comentarios", cuerpo,
                 migas=["Inicio", "Moderacion de comentarios"],
                 sub="Aprueba, oculta o borra comentarios de la comunidad.")


# --- 43. Metricas de asesorias -----------------------------------------------
ASESORIAS = [
    ("ASE-012", "14 nov 2024", "Mariana Lopez", "Sabor y Sabe", "Carlos Mendoza", "Finalizada", "2 h"),
    ("ASE-011", "13 nov 2024", "Jhon Ospina", "Krea Textil", "Paula Andrea Rios", "Confirmada", "1 h"),
    ("ASE-010", "12 nov 2024", "Lucia Fernandez", "EcoPack", "Hector Vargas", "Sin confirmar", "1 h"),
    ("ASE-009", "11 nov 2024", "Sofia Ramirez", "Aromas del Sur", "Carlos Mendoza", "Finalizada", "3 h"),
    ("ASE-008", "08 nov 2024", "Andres Felipe", "Muebles Origen", "Rafael Nieto", "Cancelada", "0 h"),
    ("ASE-007", "07 nov 2024", "Mariana Lopez", "Sabor y Sabe", "Hector Vargas", "Finalizada", "2 h"),
    ("ASE-006", "05 nov 2024", "Lucia Fernandez", "EcoPack", "Ninafq Beltran", "Confirmada", "1 h"),
    ("ASE-005", "04 nov 2024", "Jhon Ospina", "Krea Textil", "Paula Andrea Rios", "Finalizada", "2 h"),
]

CAMPO_ASESORIA = [
    {"n": "fecha", "l": "Fecha", "t": "date", "req": True},
    {"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
    {"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
    {"n": "docente", "l": "Docente asesor", "t": "select", "o": D.ASESORES + ["Sin asignar"], "req": True},
    {"n": "estado", "l": "Estado", "t": "select",
     "o": ["Agendada", "Confirmada", "Finalizada", "Sin confirmar", "Cancelada"],
     "def": "Agendada", "req": True},
    {"n": "duracion", "l": "Duración (horas)", "t": "number", "ph": "2"},
]


def asesorias():
    cuerpo = metricas([
        ("chat", "Asesorias este mes", "38", "", 84, "+9"),
        ("reloj", "Promedio de respuesta", "4.2", " h", 42, "-0.6"),
        ("checklist", "Asesorias finalizadas", "31", "", 82, None),
        ("alerta", "Sin confirmar", "5", "", 22, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Asesorias por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [18, 24, 29, 33, 38],
        unidad=" asesorías"))
    cuerpo += card("Asesorias por sector", barras_h(
        "", "", ["Alimentos", "Moda", "Ambiental", "Muebles", "Tecnologia"],
        [16, 10, 7, 3, 2], color=AMAR))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Estado de las asesorias", donut(
        "", "", [("Finalizadas", 31, AZUL), ("Confirmadas", 7, AMAR),
                 ("Sin confirmar", 5, "#bbbbbb"), ("Canceladas", 3, "#bbbbbb")],
        "asesorias"))
    cuerpo += card("Docentes con mejor respuesta", lista_def([
        ("Hector Vargas", "1.8 h promedio"),
        ("Paula Andrea Rios", "2.4 h promedio"),
        ("Carlos Mendoza", "3.1 h promedio"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "asesorias", "Registro de asesorias",
        [("codigo", "Código"), ("fecha", "Fecha"), ("estudiante", "Estudiante"),
         ("emprendimiento", "Emprendimiento"), ("docente", "Docente"),
         ("estado", "Estado"), ("duracion", "Horas", "num")],
        [dict(zip(("codigo", "fecha", "estudiante", "emprendimiento",
                   "docente", "estado", "duracion"), a)) for a in ASESORIAS],
        CAMPO_ASESORIA,
        singular="asesoría", nueva="Nueva asesoría",
        ancha=True, oculta={"md": [3]},
        prefijo="ASE-", badges=("estado",), tonos=TONOS,
        filtros=(_sel("Estado", ["Finalizada", "Confirmada", "Sin confirmar",
                                 "Cancelada"], col=5)
                 + _sel("Docente", list(D.ASESORES), col=4)),
        chips=(chip("Finalizadas", col=5, valor="Finalizada")
               + chip("Confirmadas", col=5, valor="Confirmada")
               + chip("Sin confirmar", col=5, valor="Sin confirmar")))
    return shell(R, "asesorias", "Metricas de asesorias", cuerpo,
                 migas=["Inicio", "Asesorias"],
                 sub="Indicadores de uso y gestion del registro de asesorias.",
                 acciones=_btn("download", "Exportar", "reportes.html", "btn btn-secundario"))


# --- 44. Eventos -------------------------------------------------------------
EVENTOS = [
    ("EVT-007", "Feria de emprendedores", "22 nov 2024", "14:00", "Plaza central",
     "Todos", "120", "Publicado"),
    ("EVT-006", "Jornada de mentoria", "25 nov 2024", "08:30", "Sala 2",
     "Alimentos", "30", "Por aprobar"),
    ("EVT-005", "Taller de costos y precios", "18 nov 2024", "09:00", "Auditorio A",
     "Alimentos", "40", "Publicado"),
    ("EVT-004", "Charla: opciones de financiamiento", "04 nov 2024", "10:00",
     "Auditorio B", "Moda", "60", "Finalizado"),
    ("EVT-003", "Charla: marco legal para negocios", "02 dic 2024", "10:00",
     "Auditorio B", "Todos", "80", "Borrador"),
    ("EVT-002", "Taller de modelo de negocio", "28 oct 2024", "09:00", "Sala 1",
     "Ambiental", "35", "Finalizado"),
    ("EVT-001", "Encuentro de vendredi", "20 oct 2024", "15:00", "Auditorio A",
     "Todos", "100", "Finalizado"),
]

CAMPO_EVENTO = [
    {"n": "titulo", "l": "Titulo del evento", "t": "text", "req": True},
    {"n": "fecha", "l": "Fecha", "t": "date", "req": True},
    {"n": "hora", "l": "Hora de inicio", "t": "time", "req": True},
    {"n": "lugar", "l": "Lugar", "t": "text", "req": True},
    {"n": "dirigido", "l": "Dirigido a", "t": "select",
     "o": ["Todos", "Alimentos", "Moda", "Ambiental", "Muebles", "Tecnologia"],
     "def": "Todos", "req": True},
    {"n": "cupo", "l": "Cupo maximo", "t": "number", "req": True},
    {"n": "estado", "l": "Estado", "t": "select",
     "o": ["Borrador", "Por aprobar", "Publicado", "Finalizado"],
     "def": "Borrador", "req": True},
]


def eventos():
    """Pipeline editorial: el admin aprueba y publica, no solo lista."""
    cuerpo = metricas([
        ("calendar", "Eventos publicados", "2", "", 40, None),
        ("reloj", "Por aprobar", "1", "", 20, None),
        ("doc", "Borradores", "1", "", 20, None),
        ("users", "Confirmaciones", "141", "", 88, "+37"),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += kanban([
        ("Por aprobar", [
            ("<b>Jornada de mentoria</b>",
             "25 nov 2024, 08:30 · Sala 2 · 14 confirmados",
             badge("1 solicitud", "b-amarillo", "reloj"),
             '<a class="btn btn-sm btn-primario" href="evento-form.html">'
             'Aprobar</a>'),
        ]),
        ("Borrador", [
            ("<b>Charla: marco legal para negocios</b>",
             "02 dic 2024, 10:00 · Auditorio B",
             badge("Sin publicar", "b-neutra"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
        ]),
        ("Publicado", [
            ("<b>Taller de costos y precios</b>",
             "18 nov 2024, 09:00 · Auditorio A",
             badge("32 de 40 cupos", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
            ("<b>Feria de emprendedores</b>",
             "22 nov 2024, 14:00 · Plaza central",
             badge("86 de 120 cupos", "b-azul"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Editar</a>'),
        ]),
        ("Finalizados", [
            ("<b>Charla: opciones de financiamiento</b>",
             "04 nov 2024, 10:00 · Auditorio B · 48 asistentes",
             badge("Cerrado", "b-linea"),
             '<a class="btn btn-sm btn-secundario" href="evento-form.html">'
             'Ver</a>'),
        ]),
    ])
    cuerpo += ('<p class="nota-foot">Publicar un evento notifica a los estudiantes '
               'del sector correspondiente.</p>')
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Confirmaciones por evento", barras(
        "Confirmaciones por evento", "Participacion de los últimos eventos",
        [e[1][:16] for e in EVENTOS[:5]],
        [24, 14, 32, 48, 86], unidad=" asistentes"))
    cuerpo += card("Cupos y ocupacion", donut(
        "Ocupacion de cupos", "Eventos finalizados frente a los activos",
        [("Finalizados", 3, AZUL), ("Publicados", 2, AMAR),
         ("Sin publicar", 2, "#bbbbbb")], "eventos"))
    cuerpo += "</div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "eventos", "Listado de eventos",
        [("codigo", "Código"), ("titulo", "Evento"), ("fecha", "Fecha"),
         ("hora", "Hora"), ("lugar", "Lugar"), ("dirigido", "Dirigido a"),
         ("cupo", "Cupo", "num"), ("estado", "Estado")],
        [dict(zip(("codigo", "titulo", "fecha", "hora", "lugar",
                   "dirigido", "cupo", "estado"), e)) for e in EVENTOS],
        CAMPO_EVENTO,
        singular="evento", nueva="Nuevo evento",
        ancha=True, oculta={"md": [5]}, prefijo="EVT-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Estado", ["Borrador", "Por aprobar", "Publicado",
                                 "Finalizado"], col=7)
                 + _sel("Dirigido a", ["Todos", "Alimentos", "Moda",
                                       "Ambiental", "Muebles"], col=5)),
        chips=(chip("Publicados", col=7, valor="Publicado")
               + chip("Por aprobar", col=7, valor="Por aprobar")
               + chip("Borradores", col=7, valor="Borrador")),
        cuerpo_extra=('<p class="nota-foot">El listado es el respaldo editable del '
                      'tablero: el <a href="evento-form.html">formulario de evento</a> '
                      'crea uno nuevo con el mismo juego de campos.</p>'))
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Aprueba y publica eventos del programa.",
                 acciones=_btn("plus", "Crear evento", "evento-form.html"))


# --- 45. Crear evento --------------------------------------------------------
def evento_form():
    cuerpo = callout("Guarda el evento como <b>borrador</b> mientras defines la "
                     "fecha y el lugar. Publicarlo notifica a los estudiantes "
                     "del sector y lo mueve en el tablero de Eventos.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += steps(["Datos del evento", "Fecha y lugar", "Publicar"], 1)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones(
        "Datos del evento",
        campo("Titulo del evento", valor="Taller de costos y precios",
                req=True, requerido=True)
        + select("Dirigido a", ["Todos los estudiantes",
                                "Solo Alimentos", "Solo Moda",
                                "Solo Ambiental", "Solo Muebles"],
                 req=True, requerido=True, valor="Alimentos")
        + campo("Descripcion", alto=True,
                valor="Taller practico para calcular el costo de insumos y "
                      "definir el punto de equilibrio de un emprendimiento.",
                ph="De que tratara el evento")
        + campo("Cupo maximo", tipo="number", valor="40",
                ph="Numero de asistentes"),
        exito="Evento guardado. Queda en la lista de eventos para publicarlo.",
        estricto=True,
        etiqueta="Guardar evento")
    cuerpo += form_acciones(
        "Fecha y lugar",
        campo("Fecha", tipo="date", valor="2024-11-18", req=True, requerido=True)
        + campo("Hora de inicio", tipo="time", valor="09:00", req=True, requerido=True)
        + campo("Hora de cierre", tipo="time", valor="11:00", req=True, requerido=True)
        + campo("Lugar", valor="Auditorio A")
        + campo("Link de inscripcion", valor="sgemd.edu.co/eventos/taller-costos"),
        exito="Fecha y lugar guardados.", etiqueta="Guardar fecha y lugar",
        estricto=True,
        ok_id="acceso-ok-fecha")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Visibilidad", lista_def([
        ("Visibilidad", "Visible para Alimentos"),
        ("Confirmaciones", "32 de 40"),
        ("Recordatorio", "Un dia antes"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-primario" data-accion="publicar-evento">%s Publicar evento</button>'
                     % ico("enviar", 16)
                   + '<a class="btn btn-secundario" href="eventos.html">%s Volver a eventos</a>'
                     % ico("izq", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "evento-inscriptos", "Confirmaciones del evento",
        [("codigo", "Codigo"), ("asistente", "Asistente"),
         ("programa", "Programa"), ("confirmacion", "Confirmacion")],
        [{"codigo": "CNF-%03d" % (i + 1), "asistente": p["nombre"],
          "programa": p["programa"],
          "confirmacion": "Confirmada" if i % 4 else "Pendiente"}
         for i, p in enumerate(D.PROYECTOS[:8])],
        [{"n": "asistente", "l": "Asistente", "t": "text", "req": True},
         {"n": "programa", "l": "Programa", "t": "select",
          "o": D.PROGRAMAS, "req": True},
         {"n": "confirmacion", "l": "Confirmacion", "t": "select",
          "o": ["Pendiente", "Confirmada", "Cancelada"]}],
        singular="asistente", nueva="Nuevo asistente", prefijo="CNF-",
        badges=("confirmacion",), tonos=TONOS,
        filtros=_sel("Programa", D.PROGRAMAS, col=2),
        hint="Publicar el evento notifica a los estudiantes del sector.")
    return shell(R, "eventos", "Crear evento", cuerpo,
                 migas=["Inicio", "Eventos", "Crear evento"],
                 sub="Publica un evento y notifica a los asistentes.",
                 acciones=_btn("check", "Guardar"))


# --- 46. Asignaciones ---------------------------------------------------------
def asignaciones():
    """Carga de docentes arriba, cola de asignaciones pendientes abajo."""
    pro = D.PROYECTOS
    sin_doc = [p for p in pro if p["docente"] == "Sin asignar"]
    vigentes = len(pro) - len(sin_doc)
    carga = {}
    for p in pro:
        d = p["docente"]
        if d != "Sin asignar":
            carga[d] = carga.get(d, 0) + 1
    mx = max(carga.values()) if carga else 1
    cuerpo = callout("Un docente puede tener hasta <b>12 emprendimientos</b>. "
                     "La carga semanal se descuenta del cupo disponible.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("sliders", "Asignaciones vigentes", str(vigentes), "", 93, None),
        ("alerta", "Sin docente", str(len(sin_doc)), "", round(len(sin_doc) * 100 / len(pro)), None),
        ("reloj", "Carga promedio", "%.1f" % (vigentes / max(1, len(carga))), " h", 62, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Cupo ocupado por docente", '<div class="card-body">'
                   + distribucion([(n, "%d h" % c, round(c * 100 / mx))
                                   for n, c in sorted(carga.items(),
                                                      key=lambda kv: kv[1], reverse=True)[:5]])
                   + '<p class="nota-foot">Cupo maximo de 12 h por docente.</p></div>')
    cuerpo += card("Pendientes de asignar (%d)" % len(sin_doc), tabla(
        ["Emprendimiento", "Estudiante", "Programa", "Sede", "@ACC"],
        [["<b>%s %s</b>" % (p["codigo"], p["emprendimiento"]), p["nombre"],
          p["programa"], badge(p["sede"], "b-linea"),
          _acc(_b_accion("check", "Asignar", "asignar-asesoria",
                         ' data-codigo="%s"' % p["codigo"]))]
         for p in sin_doc[:5]]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Resumen", lista_def([
        ("Vigentes", "%d de %d" % (vigentes, len(pro))),
        ("Pendientes", str(len(sin_doc))),
        ("Cupo total", "12 por docente"),
        ("Carga promedio", "%.1f h semanales" % (vigentes / max(1, len(carga)))),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + _btn("plus", "Asignar emprendimiento", "asignar-emprendimiento.html")
                   + _btn("download", "Exportar", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += card("Cupo libre por docente", barras_h(
        "Cupo libre por docente", "Horas disponibles frente a las 12 h semanales",
        [n for n, _ in sorted(carga.items(), key=lambda kv: kv[1], reverse=True)[:5]],
        [max(0, 12 - min(12, c)) for _, c in
         sorted(carga.items(), key=lambda kv: kv[1], reverse=True)[:5]],
        maximo=12, unidad=" h libres", color=AMAR))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "carga", "Carga por docente",
        [("codigo", "Codigo"), ("docente", "Docente"), ("sede", "Sede"),
         ("emprendimientos", "Emprendimientos", "num"),
         ("carga", "Carga semanal", "num"), ("estado", "Estado")],
        [{"codigo": "CAR-%03d" % (i + 1), "docente": d, "sede": "Ibagué",
          "emprendimientos": c, "carga": round(c * 1.5, 1),
          "estado": "Activo" if c <= 10 else "Inactivo"}
         for i, (d, c) in enumerate(sorted(carga.items(),
                                            key=lambda kv: -kv[1]))],
        [{"n": "docente", "l": "Docente", "t": "select", "o": D.ASESORES, "req": True},
         {"n": "sede", "l": "Sede", "t": "select", "o": D.SEDES, "req": True},
         {"n": "emprendimientos", "l": "Emprendimientos asignados",
          "t": "number", "req": True},
         {"n": "carga", "l": "Carga semanal (h)", "t": "number", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Activo", "Inactivo"]}],
        singular="carga", nueva="Nueva carga", prefijo="CAR-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Estado", ["Activo", "Inactivo"], col=5)
                 + _sel("Docente", list(D.ASESORES), col=1)),
        hint="El cupo maximo es 12 h semanales; al superarlo la asignacion queda inactiva.")
    cuerpo += _seed("datos-asignacion", {
        "asesores": D.ASESORES,
        "sin_docente": [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
                         "nombre": p["nombre"], "programa": p["programa"]}
                        for p in sin_doc[:5]],
    })
    return shell(R, "asignaciones", "Asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones"],
                 sub="Docente asignado por emprendimiento y carga semanal.")


# --- 48. Diagnosticos -------------------------------------------------------
def diagnosticos():
    """Grafico de puntajes + cola de revision. No es una tabla de resultados."""
    pro = D.PROYECTOS
    sin_rev = [p for p in pro if p["docente"] == "Sin asignar"]
    mejores = sorted(pro, key=lambda p: -p["avance"])[:5]
    b0 = sum(1 for p in pro if p["avance"] >= 90)
    b1 = sum(1 for p in pro if 70 <= p["avance"] < 90)
    b2 = sum(1 for p in pro if 50 <= p["avance"] < 70)
    b3 = sum(1 for p in pro if p["avance"] < 50)
    cuerpo = metricas([
        ("clipboard", "Diagnosticos respondidos", str(len(pro)), "", 88, None),
        ("reloj", "Sin revision", str(len(sin_rev)), "", 22, None),
        ("medalla", "Avance promedio", str(D.resumen()["avance_promedio"]), "%", 74, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Puntaje por emprendimiento", '<div class="card-body">'
                   + barras_h("", "Porcentaje de avance registrado", [
                       p["emprendimiento"] for p in mejores],
                       [p["avance"] for p in mejores], maximo=100)
                   + '</div>')
    cuerpo += card("Rendimiento del grupo", '<div class="card-body">'
                   + distribucion([
                       ("90 - 100", str(b0), round(b0 * 100 / len(pro))),
                       ("70 - 89", str(b1), round(b1 * 100 / len(pro))),
                       ("50 - 69", str(b2), round(b2 * 100 / len(pro))),
                       ("Menos de 50", str(b3), round(b3 * 100 / len(pro))),
                   ])
                   + '<p class="nota-foot">La mayoria de los estudiantes se ubica '
                     'en avance de fase 1 y 2.</p></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Pendientes de revision (%d)" % len(sin_rev), '<div class="card-body">'
                   + lista_avisos([
                       ("Sin revision del docente", [
                           ("clipboard", "%s · %s" % (p["emprendimiento"], p["nombre"]),
                            "Sin docente asignado · %s" % p["fecha"],
                            "diagnosticos.html", "alta",
                            _b("check", "Revisar")) for p in sin_rev[:5]
                       ]),
                   ]) + '</div>')
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + _btn("download", "Exportar resultados", "reportes.html",
                          "btn btn-secundario")
                   + _btn("doc", "Ver formato del instrumento",
                          "../estudiante/diagnostico.html", "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "diagnosticos", "Resultados del diagnostico",
        [("codigo", "Codigo"), ("emprendimiento", "Emprendimiento"),
         ("estudiante", "Estudiante"), ("sede", "Sede"),
         ("puntaje", "Puntaje", "num"), ("estado", "Estado")],
        [{"codigo": p["codigo"], "emprendimiento": p["emprendimiento"],
          "estudiante": p["nombre"], "sede": p["sede"], "puntaje": p["avance"],
          "estado": "En revision" if p["docente"] == "Sin asignar" else "Aprobado"}
         for p in pro[:12]],
        [{"n": "emprendimiento", "l": "Emprendimiento", "t": "text", "req": True},
         {"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "sede", "l": "Sede", "t": "select", "o": D.SEDES, "req": True},
         {"n": "puntaje", "l": "Puntaje (0-100)", "t": "number", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Pendiente", "En revision", "Aprobado", "Rechazado"]}],
        singular="diagnostico", nueva="Nuevo resultado",
        oculta={"sm": [2, 3]}, prefijo="DG-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Sede", D.SEDES, col=3)
                 + _sel("Estado", ["Pendiente", "En revision", "Aprobado",
                                   "Rechazado"], col=5)),
        chips=(chip("Sin revision", col=5, valor="En revision")
               + chip("Aprobados", col=5, valor="Aprobado")),
        hint="El puntaje alimenta el grafico de arriba y el plan de trabajo del docente.")
    return shell(R, "diagnosticos", "Diagnosticos respondidos", cuerpo,
                 migas=["Inicio", "Diagnosticos"],
                 sub="Resultados del diagnostico de los estudiantes.")


# --- 49. Exportar reportes ---------------------------------------------------
def reportes():
    u = D.resumen()
    pro = D.PROYECTOS
    sedes = sorted({p["sede"] for p in pro})
    programas = sorted({p["programa"] for p in pro})
    tipos = sorted({p["tipo"] for p in pro})
    filas = [[p["codigo"], "<b>%s</b>" % p["emprendimiento"], p["nombre"],
              p["programa"], badge(p["sede"], "b-linea"), p["tipo"],
              p["etapa"], p["docente"]]
             for p in pro]
    cuerpo = '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Filtros del reporte",
                   select("Tipo de reporte", ["Seguimiento", "Asesorias",
                                              "Emprendimientos", "Diagnosticos"],
                          req=True, valor="Seguimiento")
                   + select("Periodo", ["Ultimos 30 dias", "Ultimos 3 meses",
                                        "Todo el periodo"], req=True,
                            valor="Todo el periodo")
                   + select("Sede", sedes, req=True, valor="Todas")
                   + select("Carrera (programa)", programas, req=True, valor="Todos")
                   + select("Tratamiento", tipos, req=True, valor="Todos")
                   + select("Docente", ["Todos los docentes"] + D.ASESORES,
                            req=True, valor="Todos los docentes")
                   + campo("Enviar por correo", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co"))
    cuerpo += zona_filtros(
        tabla(["#", "Emprendimiento", "Estudiante", "Programa", "Sede",
               "Tratamiento", "Etapa", "Docente"],
              filas, id="tabla-reporte", ancha=True,
               oculta={"lg": [6], "md": [4]}),
        filtros=_sel("Sede", sedes, col=4)
                 + _sel("Carrera", programas, col=3)
                 + _sel("Tratamiento", tipos, col=5),
        acciones=boton_exportar("CSV", tabla_id="tabla-reporte")
                 + boton_exportar("Informe imprimible", tipo="reporte"))
    cuerpo += ('<p class="nota-foot">El CSV respeta lo filtrado: si eliges una '
               'sede, un programa o un tratamiento, solo se exporta ese tramo.</p>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Resumen de la exportacion",
                   lista_def([
                       ("Emprendimientos incluidos", str(u["total"])),
                       ("Sedes", str(u["sedes"])),
                       ("Programas academicos", str(u["programas"])),
                       ("Tratamientos", str(len(tipos))),
                       ("Sin docente asignado", str(u["sin_docente"])),
                   ]))
    cuerpo += card("Emprendimientos por sede", barras(
        "Emprendimientos por sede", "Distribucion institucional",
        [s for s, _ in D.POR_SEDE], [n for _, n in D.POR_SEDE],
        unidad=" proyectos"))
    cuerpo += card("Tratamientos", donut(
        "Tratamientos", "Perfil de los estudiantes",
        [(t, n, AZUL if i == 0 else (AMAR if i == 1 else "#bbbbbb"))
         for i, (t, n) in enumerate(D.POR_TIPO)], "estudiantes"))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + boton_exportar("Generar reporte", tipo="reporte",
                                    clase="btn btn-primario")
                   + '<button class="btn btn-secundario">%s Descargar plantilla</button>'
                     % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    return shell(R, "reportes", "Exportar reportes", cuerpo,
                 migas=["Inicio", "Reportes"],
                 sub="Genera y descarga reportes institucionales en CSV o PDF.",
                 acciones=_btn("check", "Generar"))


# --- 50. Sedes y carreras ------------------------------------------------------
def sedes_carreras():
    """Oferta academica por sede, normalizada (Ibague/Lerida legibles)."""
    norm = {"Ibague": "Ibagué", "Lerida": "Lérida"}
    filas = []
    for car, mod, dur, campus, sede in D.SEDES_CARRERAS:
        s = norm.get(sede, sede)
        filas.append([badge(car, "b-linea"), mod, dur,
                      campus if campus else "Sin campus", badge(s, "b-azul"),
                      _acc(_b("eye", "Ver detalle"))])
    por_sede = {}
    for car, mod, dur, campus, sede in D.SEDES_CARRERAS:
        s = norm.get(sede, sede)
        por_sede[s] = por_sede.get(s, 0) + 1
    por_campus = {}
    for car, mod, dur, campus, sede in D.SEDES_CARRERAS:
        c = campus if campus else "Sin campus"
        por_campus[c] = por_campus.get(c, 0) + 1
    cuerpo = callout("La oferta academica se concentra en <b>Ibagué</b> y "
                     "<b>Lérida</b>; la matricula no implica sede unica.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("libro", "Carreras ofertadas", str(len(D.SEDES_CARRERAS)), "", 100, None),
        ("grid", "Sedes con oferta", "2", "", 100, None),
        ("bd", "Programas (sin duplicar)", str(len({c for c, *_ in D.SEDES_CARRERAS})), "", 72, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += zona_filtros(
        tabla(["Carrera", "Modalidad", "Duracion", "Campus", "Sede", "@ACC"],
              filas, id="tabla-carreras", oculta={"lg": [1], "md": [2]}),
        filtros=_sel("Sede", sorted(por_sede), col=4)
                 + _sel("Modalidad", [
                     "Presencial", "A Distancia", "Presencial / Distancia",
                     "A Distancia / Presencial"], col=1),
        acciones=boton_exportar("CSV", tabla_id="tabla-carreras")
                 + boton_exportar("Informe imprimible", tipo="reporte"),
        chips=chip("Ibagué", col=4) + chip("Lérida", col=4))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Distribucion por sede",
                   '<div class="card-body">'
                   + "".join('<div class="dist-row"><span class="dist-lbl">%s</span>'
                             '<span class="dist-bar"><i style="width:%d%%"></i></span>'
                             '<span class="dist-val">%s</span></div>'
                             % (s, round(n * 100 / len(D.SEDES_CARRERAS)), str(n))
                             for s, n in sorted(por_sede.items(),
                                                key=lambda kv: kv[1], reverse=True))
                   + '<p class="nota-foot">Lérida programa oferta a distancia.</p></div>')
    cuerpo += card("Oferta por campus", '<div class="card-body">'
                   + lista_def([(c, str(n)) for c, n in sorted(
                       por_campus.items(), key=lambda kv: kv[1], reverse=True)])
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Carreras por modalidad", barras_h(
        "Carreras por modalidad", "Como se ofrecen los programas",
        ["Presencial", "A Distancia", "Presencial / Distancia",
         "A Distancia / Presencial"],
        [sum(1 for c, *_ in D.SEDES_CARRERAS if m == c) or 0
         for m in ["Presencial", "A Distancia", "Presencial / Distancia",
                   "A Distancia / Presencial"]], color=AMAR))
    cuerpo += card("Estudiantes por sede", donut(
        "Estudiantes por sede", "Onde se matriculan los estudiantes",
        [(s, n, AZUL) for s, n in D.POR_SEDE], "estudiantes"))
    cuerpo += card("Notas de la oferta", lista_avisos([
        ("Cobertura por sede", [
            ("grid", "Ibagué concentra la oferta presencial",
             "Campus principal ·admisión por cohorte", "sedes-carreras.html",
             "alta", badge(str(len(D.SEDES_CARRERAS)), "b-linea")),
            ("doc", "Lérida trabaja a distancia",
             "Oferta en modalidad A Distancia", "sedes-carreras.html",
             "media", badge("Sin campus", "b-neutra")),
        ]),
    ]))
    cuerpo += "</div>"
    return shell(R, "sedes-carreras", "Sedes y carreras", cuerpo,
                 migas=["Inicio", "Sedes y carreras"],
                 sub="Oferta academica de cada sede: programas, modalidades y campus.")


# --- 51. Mi perfil -----------------------------------------------------------
def perfil():
    cuerpo = metricas([
        ("users", "Usuarios gestionados", "128", "", 84, "+12"),
        ("medalla", "Reportes generados", "24", "", 62, "+4"),
        ("alerta", "Decisiones pendientes", "6", "", 20, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones("Datos personales", campo("Nombres", valor="Ana", req=True, requerido=True)
                   + campo("Apellidos", valor="Restrepo", req=True, requerido=True)
                   + campo("Correo institucional", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Telefono", tipo="tel", valor="+57 301 555 0199"))
    cuerpo += form_acciones("Zona horaria", campo("Zona horaria", valor="America/Bogota")
                   + campo("Cargo", valor="Administradora del programa",
                           bloqueo="El cargo lo asigna la institucion"),
                   etiqueta="Guardar zona horaria", ok_id="acceso-ok-zona",
        estricto=True)
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Seguridad", lista_def([
        ("Contrasena", "Actualizada hace 2 meses"),
        ("Verificacion en dos pasos", "Activada"),
        ("Ultimo acceso", "Hoy, 07:15"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-secundario">%s Cambiar contrasena</button>'
                     % ico("lock", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "sesiones", "Sesiones activas",
        [("codigo", "Codigo"), ("dispositivo", "Dispositivo"),
         ("navegador", "Navegador"), ("inicio", "Inicio"),
         ("estado", "Estado")],
        [{"codigo": "SES-0%d" % (i + 1), "dispositivo": d, "navegador": nv,
          "inicio": f, "estado": "Activa" if i == 0 else "Cerrada"}
         for i, (d, nv, f) in enumerate([
             ("Chrome · Windows", "Chrome 120", "Hoy, 07:15"),
             ("Safari · iPhone", "Safari 17", "Ayer, 18:40"),
             ("Edge · Windows", "Edge 120", "11 nov 2024"),
         ])],
        [{"n": "dispositivo", "l": "Dispositivo", "t": "text", "req": True},
         {"n": "navegador", "l": "Navegador", "t": "text", "req": True}],
        singular="sesion", nueva="Nueva sesion", prefijo="SES-",
        badges=("estado",), tonos=TONOS, exportar=False,
        chips=chip("Activas", col=4, valor="Activa"),
        hint="Cerrar una sesion termina el acceso de ese dispositivo.")
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Actualiza tus datos y revisa tu actividad.")


# --- 52. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja del administrador: registro de trabajo por dia, no tabla.

    Aqui el objetivo es trazabilidad (que se aprobo, cuando y quien), asi que
    la pantalla es un historial agrupado por fecha y las metricas son de
    gobernanza, no de pendientes del rol.
    """
    dias = [
        ("Hoy, 12 de noviembre", [
            ("08:15", "3 emprendimientos siguen sin docente",
             "Asignaciones · Sin docente asignado",
             '<a class="btn btn-sm btn-primario" href="asignar-emprendimiento.html">'
             'Asignar</a>'),
            ("09:40", "5 diagnosticos sin revision",
             "Diagnosticos · Enviados por estudiantes",
             '<a class="btn btn-sm btn-primario" href="diagnosticos.html">'
             'Revisar</a>'),
        ]),
        ("Ayer, 11 de noviembre", [
            ("16:40", "Evento por aprobar: Jornada de mentoria",
             "Eventos · Creado por docente tutor",
             '<a class="btn btn-sm btn-secundario" href="eventos.html">'
             'Aprobar</a>'),
            ("11:05", "Moderaste 3 comentarios reportados",
             "Moderacion · Cola de reportes",
             '<a class="btn btn-sm btn-secundario" href="comentarios.html">'
             'Ver cola</a>'),
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
        ("bell", "Sin leer", "2", "", 18, None),
        ("check", "Aprobaciones del mes", "24", "", 62, None),
        ("users", "Docentes activos", "8", "", 88, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += agenda(dias)
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "notificaciones", "Bandeja de notificaciones",
        [("codigo", "Codigo"), ("fecha", "Fecha"), ("titulo", "Notificacion"),
         ("origen", "Origen"), ("estado", "Estado")],
        [{"codigo": "NTF-%03d" % (i + 1), "fecha": f, "titulo": t,
          "origen": o, "estado": e}
         for i, (f, t, o, e) in enumerate([
             ("12 nov 08:15", "3 emprendimientos siguen sin docente",
              "Asignaciones", "Pendiente"),
             ("12 nov 09:40", "5 diagnosticos sin revision",
              "Diagnosticos", "Pendiente"),
             ("11 nov 16:40", "Evento por aprobar: Jornada de mentoria",
              "Eventos", "Leida"),
             ("11 nov 11:05", "Moderaste 3 comentarios reportados",
              "Moderacion", "Leida"),
             ("12 nov 18:20", "Reporte de seguimiento generado",
              "Reportes", "Leida"),
             ("12 nov 10:12", "Docente asignado a EcoPack",
              "Asignaciones", "Cerrada"),
         ])],
        [{"n": "titulo", "l": "Notificacion", "t": "text", "req": True},
         {"n": "origen", "l": "Origen", "t": "select",
          "o": ["Asignaciones", "Diagnosticos", "Eventos", "Moderacion",
                "Reportes", "Usuarios"], "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Pendiente", "Leida", "Cerrada"]}],
        singular="notificacion", nueva="Nueva notificacion", prefijo="NTF-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Origen", ["Asignaciones", "Diagnosticos", "Eventos",
                                "Moderacion", "Reportes"], col=3),
        chips=chip("Sin leer", col=4, valor="Pendiente"))
    cuerpo += '<p class="nota-foot">El registro conserva 90 dias y se puede '\
              'exportar desde Reportes.</p>'
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Registro de aprobaciones y decisiones del equipo.",
                 acciones='<button class="btn btn-secundario" data-accion="marcar-todo-leido">'
                          '%s Marcar todo como leido</button>' % ico("check", 16))


# --- 47. Trazabilidad de asignaciones ----------------------------------------
def trazabilidad():
    """Bitacora unica de una asignacion: del diagnostico a la asesoria actual."""
    p = next((x for x in D.PROYECTOS if x["docente"] != "Sin asignar"),
             D.PROYECTOS[0])
    docente = p["docente"]
    cuerpo = metricas([
        ("doc", "Asesorias realizadas", "2", "", 55, None),
        ("grid", "Seguimientos", "1", "", 40, None),
        ("users", "Docentes asignados", "1", "", 30, None),
        ("reloj", "Meses activo", "4", "", 80, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Linea de tiempo de la asignacion", linea_tiempo([
        ("12", "SEP", "Asignacion inicial",
         "Docente: %s" % docente, badge("Sistemas", "b-azul", "check")),
        ("28", "SEP", "Diagnostico enviado por el estudiante",
         "%s · %s" % (p["nombre"], p["fecha"]), badge("Completo", "b-azul")),
        ("24", "OCT", "Asesoria 1 · Plan de ventas",
         "Duracion: 60 min · virtual", badge("Registrada", "b-linea")),
        ("14", "NOV", "Seguimiento de la fase",
         "%s · %d%% de avance" % (p["etapa"], p["avance"]), badge("En curso", "b-amarillo")),
        ("05", "DIC", "Asesoria 2 · Prototipo y costos",
         "Duracion: 45 min · en sede", badge("Registrada", "b-linea")),
        ("09", "ENE", "Plantilla de plan firmada",
         "Formato descargado por el estudiante", badge("Hecho", "b-neutra", "check")),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Datos de la asignacion", lista_def([
        ("Emprendimiento", "%s %s" % (p["codigo"], p["emprendimiento"])),
        ("Estudiante", p["nombre"]),
        ("Programa", p["programa"]),
        ("Sede", p["sede"]),
        ("Tratamiento", p["tipo"]),
        ("Docente", docente),
    ]))
    cuerpo += card("Asesorias realizadas", lista_def([
        ("24 oct 2024", "Plan de ventas y canales digitales"),
        ("05 dic 2024", "Prototipo, costos fijos y punto de equilibrio"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + _btn("plus", "Asignar asesoria", "asignar-emprendimiento.html",
                          "btn btn-secundario")
                   + _btn("download", "Exportar trazabilidad", "reportes.html",
                          "btn btn-secundario")
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Avance de la asesoria", barras(
        "Avance de la asesoria", "Hitos cumplidos por mes",
        ["SEP", "OCT", "NOV", "DIC", "ENE"], [20, 45, 70, 88, 100],
        maximo=100, unidad="%"))
    cuerpo += card("Horas por tipo de asesoria", barras_h(
        "Horas por tipo de asesoria", "Reparto de las seis sesiones",
        ["Diagnostico", "Plan de ventas", "Prototipo", "Evaluacion"],
        [6, 4, 3, 2], unidad=" h", color=AMAR))
    cuerpo += "</div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "bitacora", "Bitacora editable de la asignacion",
        [("codigo", "Codigo"), ("fecha", "Fecha"), ("hito", "Hito"),
         ("responsable", "Responsable"), ("estado", "Estado")],
        [{"codigo": "BIT-0%d" % (i + 1), "fecha": f, "hito": h,
          "responsable": r, "estado": e}
         for i, (f, h, r, e) in enumerate([
             ("12 sep 2024", "Asignacion inicial de docente", "Ana Restrepo", "Aprobada"),
             ("28 sep 2024", "Diagnostico enviado", p["nombre"], "Aprobada"),
             ("24 oct 2024", "Registro de asesoria 1", docente, "Confirmada"),
             ("14 nov 2024", "Seguimiento de fase", docente, "En revision"),
             ("05 dic 2024", "Registro de asesoria 2", docente, "Confirmada"),
         ])],
        [{"n": "fecha", "l": "Fecha", "t": "date", "req": True},
         {"n": "hito", "l": "Hito", "t": "text", "req": True},
         {"n": "responsable", "l": "Responsable", "t": "text", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Aprobada", "Confirmada", "En revision", "Pendiente"]}],
        singular=" hito", nueva="Nuevo hito", prefijo="BIT-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Estado", ["Aprobada", "Confirmada", "En revision",
                                "Pendiente"], col=4),
        hint="Lo que ves en la linea de tiempo es el resumen; esta tabla es el "
             "registro que se puede corregir y exportar.")
    return shell(R, "trazabilidad", "Trazabilidad de asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones", "Trazabilidad"],
                 sub="Historial completo de una asignacion y su bitacora de asesorias.")


# --- 53. Ayuda y soporte -----------------------------------------------------
def ayuda():
    cuerpo = callout("Este panel reune las herramientas de administracion del "
                     "programa: usuarios, asignaciones, carrera, reportes y "
                     "eventos. Todo se guarda localmente en tu navegador.",
                     "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("libro", "Secciones", "12", "", 100, None),
        ("users", "Perfiles gestionados", str(D.resumen()["total"]), "", 100, None),
        ("check", "Truco del dia", "CSV respeta lo filtrado", "", 100, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Gestion de usuarios", lista_def([
        ("Crear un usuario", "Pulsa 'Nuevo usuario' en Gestion de perfiles y llena el modal."),
        ("Activar o bloquear", "Usa el candado de la fila; el estado se conserva al recargar."),
        ("Editar datos", "Pulsa el lapiz de la fila para abrir el formulario del rol."),
    ]))
    cuerpo += card("Asignaciones y asesorias", lista_def([
        ("Asignar una asesoria", "Desde Emprendimientos o Asignaciones pulsa 'Asignar asesoria'."),
        ("Llego al cupo", "Cada docente admite hasta 12 emprendimientos."),
        ("Ver la bitacora", "La pestaña Trazabilidad muestra la historia completa."),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Reportes y exportaciones", lista_def([
        ("Generar un reporte", "Elige sede, carrera o tratamiento, y el CSV sale filtrado."),
        ("Informe imprimible", "Genera la vista para imprimir con el mismo filtro."),
        ("Enviar por correo", "El reporte se descarga localmente; el correo es opcional."),
    ]))
    cuerpo += card("Sedes y carreras", lista_def([
        ("Oferta academica", "La vista Sedes y carreras lista la oferta por sede."),
        ("Campus", "El estudiante no queda atado a una sede unica."),
        ("Mas ayuda", "Contacta a la coordinacion academica del programa."),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "ayuda", "Preguntas frecuentes",
        [("codigo", "Codigo"), ("tema", "Tema"), ("pregunta", "Pregunta"),
         ("respuesta", "Respuesta corta"), ("estado", "Estado")],
        [{"codigo": "FAQ-%03d" % (i + 1), "tema": t, "pregunta": q,
          "respuesta": r, "estado": "Publicado"}
         for i, (t, q, r) in enumerate([
             ("Usuarios", "Como creo un usuario nuevo",
              "Pulsa Nuevo usuario y elige el rol: los campos cambian segun el tipo"),
             ("Usuarios", "Como bloqueo el acceso de alguien",
              "El candado de la fila alterna Activo/Inactivo y se recuerda al recargar"),
             ("Asesorias", "Como asigno un docente asesor",
              "Desde Emprendimientos o Asignaciones, con el boton Asignar asesoria"),
             ("Reportes", "El CSV trae todos los registros",
              "No: el CSV descarga solo lo que queda visible tras filtrar"),
             ("Flujo", "Cuando puedo asignar docente",
              "Cuando el acta de compromiso y confidencialidad este aprobada"),
             ("Flujo", "Que tipo de emprendimiento es valido",
              "Solo tres: idea de negocio, unidad productiva o empresa formalizada"),
         ])],
        [{"n": "tema", "l": "Tema", "t": "select",
          "o": ["Usuarios", "Asesorias", "Reportes", "Flujo"], "req": True},
         {"n": "pregunta", "l": "Pregunta", "t": "text", "req": True},
         {"n": "respuesta", "l": "Respuesta corta", "t": "area", "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Publicado", "Borrador"]}],
        singular="pregunta", nueva="Nueva pregunta", prefijo="FAQ-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Tema", ["Usuarios", "Asesorias", "Reportes", "Flujo"], col=1),
        chips=(chip("Usuarios", col=1, valor="Usuarios")
               + chip("Flujo", col=1, valor="Flujo")))
    cuerpo += ('<p class="nota-foot">Ayuda generica del modulo; el documento '
               'institucional de procesos esta disponible en Reportes.</p>')
    return shell(R, "ayuda", "Ayuda y soporte", cuerpo,
                 migas=["Inicio", "Ayuda"],
                 sub="Preguntas frecuentes para operar el panel de administracion.")


# --- 54. Bandeja de inscripciones ---------------------------------------------
CAMPOS_INSCRIPCION = [
    {"n": "estudiante", "l": "Nombre del estudiante", "t": "text", "req": True},
    {"n": "programa", "l": "Programa", "t": "select",
     "o": D.PROGRAMAS, "req": True},
    {"n": "sede", "l": "Sede", "t": "select", "o": D.SEDES, "req": True},
    {"n": "condicion", "l": "Condicion academica", "t": "select",
     "o": D.CONDICION_ACADEMICA, "def": "Estudiante Pregrado", "req": True},
    {"n": "semestre", "l": "Semestre", "t": "number",
     "ayuda": "Solo si la condicion academica indica que sigue estudiando",
     "dep": {"campo": "condicion", "valores": D.CONDICION_SI_ESTUDIA}},
    {"n": "tipo", "l": "Tipo de emprendimiento", "t": "select",
     "o": D.TIPO_EMPRENDIMIENTO, "req": True,
     "ayuda": "Solo tres opciones: el documento lo exige para poder categorizar"},
    {"n": "estado", "l": "Estado del flujo", "t": "select",
     "o": D.ESTADOS_FLUJO_INSCRIP, "def": "Inscrito", "req": True},
    {"n": "acta", "l": "Acta de compromiso", "t": "select",
     "o": D.ESTADOS_ACTA, "def": "Pendiente", "req": True},
]


def _fila_inscripcion(i):
    (cod, nombre, programa, sede, cond, sem, tipo, fecha, estado, acta) = i
    return {"codigo": cod, "estudiante": nombre, "programa": programa, "sede": sede,
            "condicion": cond, "semestre": sem or "-", "tipo": tipo,
            "estado": estado, "acta": acta}


def inscripciones():
    f = D.resumen_flujo()
    cuerpo = callout("El estudiante se inscribe por su cuenta. Aqui se le envia el "
                     "correo de bienvenida, se agenda la <b>primera asesoria</b> y "
                     "se le habilita el formulario de caracterizacion.", "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("clipboard", "Inscripciones totales", str(f["inscripciones"]), "", 100, "+3"),
        ("calendar", "Sin primera asesoria", str(f["sin_asesoria"]), "", 18, "agendar"),
        ("reloj", "Esperando acta", str(f["actas_pendientes"]), "", 60, "revisar"),
        ("check", "Con docente asignado", str(
            sum(1 for i in D.INSCRIPCIONES if i[8] == "Docente asignado")),
         "", 40, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Inscripciones por estado del flujo", barras_h(
        "Estado del flujo", "De la inscripcion al acompañamiento",
        [s for s, _ in
         sorted(((s, sum(1 for i in D.INSCRIPCIONES if i[8] == s))
                 for s in D.ESTADOS_FLUJO_INSCRIP), key=lambda x: -x[1])],
        [n for _, n in
         sorted(((s, sum(1 for i in D.INSCRIPCIONES if i[8] == s))
                 for s in D.ESTADOS_FLUJO_INSCRIP), key=lambda x: -x[1])]))
    cuerpo += card("Condicion academica de los inscritos", donut(
        "Condicion academica", "Solo se puede filtrar por las cuatro opciones",
        [(c, sum(1 for i in D.INSCRIPCIONES if i[4] == c), AZUL)
         for c in D.CONDICION_ACADEMICA], "inscritos"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Reglas del proceso", lista_def([
        ("Semestre", "Solo aplica si sigue estudiando"),
        ("Tipo de emprendimiento", "Tres opciones, sin texto libre"),
        ("Asignar docente", "Requiere acta aprobada"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<a class="btn btn-primario" href="actas.html">%s Revisar actas</a>'
                     % ico("clipboard", 16)
                   + '<a class="btn btn-secundario" href="inscripcion-detalle.html">%s Ver expediente</a>'
                     % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "inscripciones", "Bandeja de inscripciones",
        [("codigo", "Codigo"), ("estudiante", "Estudiante"),
         ("programa", "Programa"), ("sede", "Sede"),
         ("condicion", "Condicion academica"), ("semestre", "Semestre"),
         ("tipo", "Tipo de emprendimiento"), ("estado", "Estado del flujo"),
         ("acta", "Acta")],
        [_fila_inscripcion(i) for i in D.INSCRIPCIONES],
        CAMPOS_INSCRIPCION,
        singular="inscripcion", nueva="Nueva inscripcion",
        ancha=True, oculta={"lg": [2, 4], "md": [6], "sm": [3, 5]},
cortas={"condicion": {"Estudiante Pregrado": "Estudiante", "Estudiante Posgrado": "Posgrado", "Egresado Pregrado": "Egresado", "Egresado no Graduado": "No graduado"}, "tipo": {"Idea de negocio": "Idea", "Unidad productiva": "Unidad", "Empresa formalizada": "Empresa"}}, prefijo="INS-",
        badges=("estado", "acta"), tonos=TONOS,
        filtros=(_sel("Sede", D.SEDES, col=3)
                 + _sel("Programa", D.PROGRAMAS, col=2)
                 + _sel("Condicion", D.CONDICION_ACADEMICA, col=4)
                 + _sel("Semestre", D.SEMESTRES, col=5, primera="Todos")),
        chips=(chip("Sin primera asesoria", col=7, valor="Inscrito")
               + chip("Formulario 2 habilitado", col=7,
                      valor="Formulario 2 habilitado")
               + chip("Acta pendiente", col=8, valor="Pendiente")),
        hint="Cada fila es una inscripcion real del formulario 1; el estado "
             "del flujo es lo que habilita el formulario 2 y la firma del acta.")
    return shell(R, "inscripciones", "Inscripciones", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Inscripciones"],
                 sub="Bandeja del formulario 1 y control del flujo de atencion.")


# --- 55. Actas de compromiso y confidencialidad ------------------------------
def actas():
    f = D.resumen_flujo()
    cuerpo = callout("El <b>acta firmada es requisito para asignar docente</b>. "
                     "Mientras este en Pendiente o En revision, el estudiante "
                     "queda bloqueado en ese paso.", "alerta")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("clipboard", "Actas recibidas", str(len(D.ACTAS)), "", 100, "+2"),
        ("reloj", "Pendientes de revision", str(f["actas_pendientes"]), "", 60, None),
        ("check", "Aprobadas", str(f["actas_aprobadas"]), "", 40, None),
        ("alerta", "Sin acta no se asigna", str(f["sin_docente_por_acta"]), "", 50, "bloqueadas"),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Actas por estado", barras(
        "Actas por estado", "Revisión del acta de compromiso",
        ["Pendiente", "En revision", "Aprobada", "Rechazada"],
        [sum(1 for a in D.ACTAS if a[5] == e)
         for e in ["Pendiente", "En revision", "Aprobada", "Rechazada"]],
        unidad=" actas"))
    cuerpo += card("Como circula el acta", steps([
        "El estudiante descarga el formato en blanco",
        "Lo diligencia, lo firma y lo sube escaneado",
        "La asesora revisa y aprueba o rechaza",
        "Solo con el acta aprobada se asigna docente",
    ], 2))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Formato oficial", lista_def([
        ("Documento", "Acta de compromiso y confidencialidad"),
        ("Quien firma", "El estudiante"),
        ("Cuando", "Antes de la asignacion de docente"),
        ("Revisa", "La asesora de emprendimiento"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<a class="btn btn-primario" href="inscripciones.html">%s Ver inscripciones</a>'
                     % ico("clipboard", 16)
                   + '<button class="btn btn-secundario" data-accion="descargar">%s Descargar formato</button>'
                     % ico("download", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += form_acciones(
        "Subir el acta firmada",
        callout("El estudiante descarga el formato en blanco, lo diligencia, lo "
                "firma y lo sube escaneado. La asesora revisa y aprueba antes de "
                "que se le pueda asignar docente.", "bombilla")
        + campo_archivo("Archivo firmado", acepta=".pdf,.jpg,.png", requerido=True)
        + campo("Observacion de la asesora", alto=True,
                ph="Por que se aprueba o se rechaza")
        + '<div class="form-aviso">%s El archivo queda adjunto a la ficha del '
          'estudiante.</div>' % ico("clip", 14),
        exito="Acta subida. Queda en estado Pendiente de revision.",
        etiqueta="Subir acta", ok_id="acceso-ok-acta", estricto=True)
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "actas", "Actas de compromiso y confidencialidad",
        [("codigo", "Codigo"), ("estudiante", "Estudiante"),
         ("envio", "Enviada"), ("revision", "Revisada"),
         ("revisor", "Revisor"), ("estado", "Estado")],
        [{"codigo": a[0], "estudiante": a[1], "envio": a[2],
          "revision": a[3] or "-", "revisor": a[4], "estado": a[5]}
         for a in D.ACTAS],
        [{"n": "estudiante", "l": "Estudiante", "t": "text", "req": True},
         {"n": "envio", "l": "Fecha de envio", "t": "date", "req": True},
         {"n": "revision", "l": "Fecha de revision", "t": "date"},
         {"n": "revisor", "l": "Revisor", "t": "text",
          "ayuda": "Vacio mientras el acta no se ha revisado"},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": D.ESTADOS_ACTA, "def": "Pendiente", "req": True}],
        singular="acta", nueva="Nueva acta", prefijo="ACT-",
        badges=("estado",), tonos=TONOS,
        filtros=(_sel("Estado", D.ESTADOS_ACTA, col=5)
                 + _sel("Revisor", ["Ana Restrepo", "Sin revisar"], col=4)),
        chips=(chip("Pendientes", col=5, valor="Pendiente")
               + chip("En revision", col=5, valor="En revision")
               + chip("Aprobadas", col=5, valor="Aprobada")),
        hint="Aprueba o rechaza el acta: el estado decide si el estudiante "
             "puede recibir docente.")
    return shell(R, "actas", "Actas de compromiso", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Actas"],
                 sub="Carga, revision y aprobacion del acta de compromiso.")


# --- 56. Expediente de una inscripcion ---------------------------------------
def inscripcion_detalle():
    i = D.INSCRIPCIONES[2]
    cod, nombre, programa, sede, cond, sem, tipo, fecha, estado, acta = i
    cuerpo = metricas([
        ("clipboard", "Hitos completados", "6", "/ 6", 100, None),
        ("calendar", "Asesorias realizadas", "3", "", 60, None),
        ("reloj", "Dias en el proceso", "38", "", 70, None),
        ("check", "Acta", acta, "", 100 if acta == "Aprobada" else 20, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += steps(["Inscripcion", "Primera asesoria", "Formulario 2",
                     "Caracterizacion", "Acta firmada", "Docente asignado"], 5)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Datos de la inscripcion", lista_def([
        ("Codigo", cod),
        ("Estudiante", nombre),
        ("Programa", programa),
        ("Sede", sede),
        ("Condicion academica", cond),
        ("Semestre", sem or "No aplica"),
        ("Tipo de emprendimiento", tipo),
        ("Fecha de inscripcion", fecha),
    ]))
    cuerpo += card("Linea de tiempo del expediente", linea_tiempo([
        ("02", "NOV", "Inscripcion registrada",
         "%s · %s" % (nombre, fecha), badge("Hecho", "b-azul", "check")),
        ("04", "NOV", "Correo de bienvenida enviado",
         "Asesora de emprendimiento", badge("Hecho", "b-azul")),
        ("06", "NOV", "Primera asesoria agendada",
         "Reunion de socializacion del servicio", badge("Hecho", "b-azul")),
        ("08", "NOV", "Formulario 2 habilitado",
         "Caracterizacion y valoracion", badge("Hecho", "b-azul")),
        ("12", "NOV", "Caracterizacion y valoracion generadas",
         "Diagnostico listo para el docente", badge("Hecho", "b-azul")),
        ("13", "NOV", "Acta firmada y subida",
         "Aprobada por la asesora", badge("Hecho", "b-azul", "check")),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Estado del acta", lista_def([
        ("Estado", acta),
        ("Fecha de envio", "13 nov 2024"),
        ("Revisada por", "Ana Restrepo"),
        ("Requisito de docente", "Cumplido"),
    ]))
    cuerpo += card("Siguiente paso",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-secundario" data-accion="habilitar-form2">'
                     '%s Habilitar formulario 2</button>' % ico("clipboard", 16)
                   + '<button class="btn btn-primario" data-accion="asignar-docente" '
                     'data-acta="Aprobada">%s Asignar docente</button>' % ico("sliders", 16)
                   + '<a class="btn btn-secundario" href="inscripciones.html">%s Volver a inscripciones</a>'
                     % ico("izq", 16)
                   + "</div>"
                     '<p class="nota-foot">El boton queda bloqueado mientras el '
                     'acta no este aprobada.</p>')
    cuerpo += card("Ejemplo bloqueado",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-secundario" data-accion="asignar-docente" '
                     'data-acta="Pendiente">%s Asignar docente (sin acta aprobada)</button>'
                     % ico("sliders", 16)
                   + "</div>"
                     '<p class="nota-foot">Este boton lleva el acta en Pendiente: al '
                     'pulsarlo explica la regla en vez de fallar en silencio.</p>'
                   + '<div style="height:12px"></div>'
                   + linea_tiempo([
                       ("14", "NOV", "Intento de asignacion bloqueado",
                        "El acta estaba en revision",
                        '<div style="margin-top:10px">'
                        + badge("Bloqueado", "b-amarillo", "alerta") + "</div>"),
                   ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "expediente", "Evidencias del expediente",
        [("codigo", "Codigo"), ("fecha", "Fecha"), ("evidencia", "Evidencia"),
         ("responsable", "Responsable"), ("estado", "Estado")],
        [{"codigo": "EVD-%03d" % (i2 + 1), "fecha": f, "evidencia": e,
          "responsable": r, "estado": "Aprobado"}
         for i2, (f, e, r) in enumerate([
             ("02 nov 2024", "Formulario 1 de inscripcion", nombre),
             ("06 nov 2024", "Registro de la primera asesoria", "Ana Restrepo"),
             ("12 nov 2024", "Formulario 2 de caracterizacion", nombre),
             ("12 nov 2024", "Valoracion y diagnostico generados", "Plataforma"),
             ("13 nov 2024", "Acta firmada escaneada", nombre),
         ])],
        [{"n": "fecha", "l": "Fecha", "t": "date", "req": True},
         {"n": "evidencia", "l": "Evidencia", "t": "text", "req": True},
         {"n": "responsable", "l": "Responsable", "t": "select",
          "o": [nombre, "Ana Restrepo", "Plataforma", "Docente asignado"],
          "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Pendiente", "Aprobado", "Rechazado"]}],
        singular="evidencia", nueva="Nueva evidencia",
        oculta={"sm": [2]}, prefijo="EVD-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Estado", ["Pendiente", "Aprobado", "Rechazado"], col=4),
        hint="Las seis evidencias del proceso son obligatorias: inscripcion, "
             "reunion inicial, caracterizacion, asignacion, asistencia y seguimiento.")
    return shell(R, "inscripciones", "Expediente de inscripcion", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Inscripciones", "Expediente"],
                 sub="Expediente completo de %s con su linea de tiempo." % nombre)


# --- 57. Formulario 2: caracterizacion y valoracion -------------------------
# Las seis secciones son las del documento FLUJO-DE-ATENCION.md (3.1). El
# formulario lo responde el estudiante, lo habilita la asesora y de el salen
# dos resultados: la caracterizacion y la valoracion (diagnostico).
SECCIONES_F2 = [
    ("1. Informacion general del emprendedor",
     ["Nombre completo", "Tipo de documento", "Numero de documento",
      "Fecha de nacimiento", "Genero", "Ciudad de residencia", "Correo",
      "Telefono"]),
    ("2. Informacion general de la empresa",
     ["Nombre del emprendimiento", "Tipo de emprendimiento",
      "Sector economico", "Fecha de inicio", "Numero de empleados",
      "Direccion del local"]),
    ("3. Modelo de negocio",
     ["Que problema resuelve", "A quien le resuelve el problema",
      "Como gana dinero", "Principales insumos", "Mayor dificultad"]),
    ("4. Marketing y mercadeo",
     ["A que clientes le vende", "Como se da a conocer",
      "Canales de venta", "Precio promedio", "Tasa de recompra"]),
    ("5. Producto y servicio",
     ["Que vende exactamente", "En que se diferencia",
      "Cual es su capacidad de produccion", "Registros o permisos"]),
    ("6. Administrativo, financiero y legal",
     ["Forma juridica", "Registrado en camara de comercio",
      "Declara impuestos", "Financiaamiento", "Tiene local propio"]),
]

CONDICIONES = ["Fuerte", "Media", "Baja"]
ASPECTOS = ["Estado", "Tendencia", "Riesgo"]


def _campo_texto(nombre, etiqueta, req=False, area=False, ayuda=""):
    if area:
        return campo(etiqueta, alto=True, ph="Escribe aqui", req=req,
                     requerido=req, ayuda=ayuda)
    return campo(etiqueta, ph="Escribe aqui", req=req, requerido=req, ayuda=ayuda)


def caracterizacion_form():
    """Formulario 2. Se responde por secciones; el estudiante puede salir y
    volver porque el borrador queda guardado en el navegador."""
    cuerpo = callout("Este es el <b>formulario 2</b> del proceso. Lo habilita la "
                     "asesora en la primera asesoria. Al enviarlo, la plataforma "
                     "genera la caracterizacion y la valoracion (diagnostico).",
                     "bombilla")
    cuerpo += '<div class="sep"></div>'
    cuerpo += steps(["Habilitado", "Seccion 1 a 3", "Seccion 4 a 6", "Enviado",
                     "Diagnostico"], 1)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += metricas([
        ("clipboard", "Secciones completas", "2", "/ 6", 33, None),
        ("doc", "Borrador guardado", "Ayer 18:40", "", 40, None),
        ("reloj", "Enviar antes de", "20 nov 2024", "", 60, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones(
        "Seccion 1. Informacion general del emprendedor",
        _campo_texto("n", "Nombre completo", req=True)
        + select("Tipo de documento", ["Cedula de ciudadania",
                                       "Cedula de extraterrestria", "Pasaporte"],
                 req=True, requerido=True, valor="Cedula de ciudadania")
        + campo("Numero de documento", valor="1020304050", req=True, requerido=True)
        + campo("Fecha de nacimiento", tipo="date", valor="2002-08-14", req=True,
                requerido=True)
        + select("Genero", ["Femenino", "Masculino", "Otro", "Prefiere no decir"],
                 req=True, requerido=True, valor="Femenino")
        + campo("Ciudad de residencia", valor="Ibague", req=True, requerido=True)
        + campo("Correo", tipo="email", valor="mariana.lopez@sgemd.edu.co",
                req=True, requerido=True)
        + campo("Telefono", tipo="tel", valor="+57 315 555 0140", req=True,
                requerido=True),
        exito="Seccion 1 guardada.", etiqueta="Guardar seccion 1",
        ok_id="acceso-ok-f2-1")
    cuerpo += form_acciones(
        "Seccion 2. Informacion general de la empresa",
        campo("Nombre del emprendimiento", valor="Sabor y Sabe", req=True,
              requerido=True)
        + select("Tipo de emprendimiento", D.TIPO_EMPRENDIMIENTO, req=True,
                 requerido=True, valor="Idea de negocio")
        + select("Sector economico", ["Alimentos", "Moda", "Ambiental",
                                      "Tecnologia", "Muebles"],
                 req=True, requerido=True, valor="Alimentos")
        + campo("Fecha de inicio", tipo="date", valor="2024-03-01")
        + campo("Numero de empleados", tipo="number", valor="2")
        + campo("Direccion del local", valor="Calle 12 #4-56"),
        exito="Seccion 2 guardada.", etiqueta="Guardar seccion 2",
        ok_id="acceso-ok-f2-2")
    cuerpo += form_acciones(
        "Seccion 3. Modelo de negocio",
        _campo_texto("p1", "Que problema resuelve", req=True, area=True,
                     ayuda="Sea concreto: una o dos frases")
        + _campo_texto("p2", "A quien le resuelve el problema", req=True, area=True)
        + _campo_texto("p3", "Como gana dinero", req=True, area=True)
        + _campo_texto("p4", "Principales insumos", area=True)
        + _campo_texto("p5", "Mayor dificultad a la fecha", area=True),
        exito="Seccion 3 guardada.", etiqueta="Guardar seccion 3",
        ok_id="acceso-ok-f2-3")
    cuerpo += form_acciones(
        "Seccion 4. Marketing y mercadeo",
        _campo_texto("m1", "A que clientes le vende", req=True, area=True)
        + _campo_texto("m2", "Como se da a conocer", area=True)
        + _campo_texto("m3", "Canales de venta", area=True)
        + campo("Precio promedio", valor="18.000")
        + campo("Tasa de recompra", valor="35%"),
        exito="Seccion 4 guardada.", etiqueta="Guardar seccion 4",
        ok_id="acceso-ok-f2-4")
    cuerpo += form_acciones(
        "Seccion 5. Producto y servicio",
        _campo_texto("s1", "Que vende exactamente", req=True, area=True)
        + _campo_texto("s2", "En que se diferencia", area=True)
        + campo("Capacidad de produccion", valor="120 unidades al mes")
        + campo("Registros o permisos", valor="Registro sanitario en tramite"),
        exito="Seccion 5 guardada.", etiqueta="Guardar seccion 5",
        ok_id="acceso-ok-f2-5")
    cuerpo += form_acciones(
        "Seccion 6. Administrativo, financiero y legal",
        select("Forma juridica", ["Natural", "Sociedad de hecho",
                                 "Sociedad limitada", "SAS"], req=True,
               requerido=True, valor="Natural")
        + campo_check("Esta registrado en camara de comercio")
        + campo_check("Declara impuestos")
        + campo("Financiamiento", valor="Ahorro propio y apoyo familiar")
        + campo_check("Tiene local propio", ayuda="Propio o arrendado"),
        exito="Seccion 6 guardada. Ya se puede enviar el formulario.",
        etiqueta="Guardar seccion 6", ok_id="acceso-ok-f2-6", estricto=True)
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Enviar el formulario", '<div class="col-acciones">'
                   + '<button class="btn btn-primario" data-accion="generar-diagnostico">'
                     "%s Generar caracterizacion y diagnostico</button>"
                     % ico("rayo", 16)
                   + '<button class="btn btn-secundario" data-accion="guardar-borrador">'
                     "%s Guardar borrador</button>" % ico("doc", 16)
                   + "</div>"
                   + '<p class="nota-foot">Al enviarlo, el estudiante deja de '
                     "poder editar y la asesora revisa el resultado.</p>")
    cuerpo += card("Secciones del formulario", lista_def(
        [(t, "%d campos" % len(c)) for t, c in SECCIONES_F2]))
    cuerpo += card("Como se usa", lista_def([
        ("Quien lo responde", "El estudiante, con el formulario habilitado"),
        ("Cuando se habilita", "En la primera asesoria"),
        ("Que produce", "Caracterizacion y valoracion"),
        ("Quien lo revisa", "La asesora de emprendimiento"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += card("Avance del formulario", '<div class="card-body">'
                   + distribucion([
                       ("Secciones completas", "2 de 6", 33),
                       ("Campos respondidos", "21 de 38", 55),
                       ("Evidencias con el acta", "2 de 3", 66),
                   ])
                   + '<p class="nota-foot">El formulario puede enviarse con las '
                     "seis secciones completas; las evidencias se exigen para "
                     "asignar docente.</p></div>")
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "evidencias-f2", "Evidencias obligatorias del proceso",
        [("codigo", "Codigo"), ("evidencia", "Evidencia"), ("fecha", "Fecha"),
         ("responsable", "Responsable"), ("estado", "Estado")],
        [{"codigo": "EV1", "evidencia": "Inscripcion (formulario 1)",
          "fecha": "02 nov 2024", "responsable": "Estudiante", "estado": "Aprobado"},
         {"codigo": "EV2", "evidencia": "Reunion inicial de socializacion",
          "fecha": "06 nov 2024", "responsable": "Asesora", "estado": "Aprobado"},
         {"codigo": "EV3", "evidencia": "Caracterizacion y valoracion (formulario 2)",
          "fecha": "Pendiente", "responsable": "Estudiante", "estado": "Pendiente"},
         {"codigo": "EV4", "evidencia": "Asignacion de docente",
          "fecha": "Pendiente", "responsable": "Asesora", "estado": "Pendiente"},
         {"codigo": "EV5", "evidencia": "Asistencia a asesorias",
          "fecha": "Pendiente", "responsable": "Docente", "estado": "Pendiente"},
         {"codigo": "EV6", "evidencia": "Seguimiento del docente",
          "fecha": "Pendiente", "responsable": "Docente", "estado": "Pendiente"}],
        [{"n": "evidencia", "l": "Evidencia", "t": "text", "req": True},
         {"n": "fecha", "l": "Fecha", "t": "date", "req": True},
         {"n": "responsable", "l": "Responsable", "t": "select",
          "o": ["Estudiante", "Asesora", "Docente", "Plataforma"], "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Pendiente", "Aprobado", "Rechazado"]}],
        singular="evidencia", nueva="Nueva evidencia", prefijo="EV-",
        badges=("estado",), tonos=TONOS, exportar=False,
        filtros=_sel("Estado", ["Pendiente", "Aprobado", "Rechazado"], col=4),
        hint="Las seis evidencias son obligatorias: sin las cuatro primeras no "
             "se puede asignar docente.")
    return shell(R, "inscripciones", "Formulario 2 de caracterizacion", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Inscripciones",
                        "Formulario 2"],
                 sub="Caracterizacion y valoracion del emprendimiento.",
                 acciones='<a class="btn btn-secundario" href="inscripcion-detalle.html">'
                          "%s Volver al expediente</a>" % ico("izq", 16))


# --- 58. Caracterizacion y diagnostico generado ------------------------------
def diagnostico_generado():
    """Resultado del formulario 2: la caracterizacion identifica al Prinzip y al
    emprendimiento; la valoracion analiza cada seccion con fortalezas y
    oportunidades de mejora."""
    cuerpo = callout("La plataforma genero este resultado a partir del "
                     "<b>formulario 2</b>. La asesora puede ajustarlo antes de "
                     "que llegue al docente.", "rayo")
    cuerpo += '<div class="sep"></div>'
    cuerpo += metricas([
        ("medalla", "Fortalezas detectadas", "9", "", 72, None),
        ("alerta", "Oportunidades de mejora", "11", "", 58, None),
        ("trend", "Seccion mas debil", "Administrativo", "", 30, None),
        ("check", "Puntaje general", "62", "/ 100", 62, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Caracterizacion del emprendimiento", lista_def([
        ("Emprendedor", "Mariana Lopez"),
        ("Emprendimiento", "Sabor y Sabe"),
        ("Tipo", "Idea de negocio"),
        ("Sector", "Alimentos"),
        ("Forma juridica", "Natural"),
        ("Inicio", "Marzo 2024"),
        ("Empleados", "2"),
    ]))
    cuerpo += card("Valoracion por seccion", '<div class="card-body">'
                   + "".join('<div class="fn-item"><div class="fn-titulo">%s</div>'
                             '<div class="fn-tags">%s</div></div>'
                             % (t, "".join(
                                 '<span class="badge %s">%s</span>' % (
                                     "b-azul" if a.startswith("F") else "b-amarillo",
                                     ASPECTOS[i] + ": " + a)
                                 for i, a in enumerate(
                                     [f, t_, r][:3])))
                             for t, f, t_, r in [
                                 ("Modelo de negocio", "Fuerte", "Estable", "Bajo"),
                                 ("Marketing y mercadeo", "Media", "Creciente", "Medio"),
                                 ("Producto y servicio", "Fuerte", "Estable", "Bajo"),
                                 ("Administrativo y legal", "Baja", "Incipiente", "Alto"),
                             ])
                   + "</div>")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Fortalezas", lista_def([
        ("Modelo de negocio", "Bien estructurado segun las respuestas"),
        ("Producto y servicio", "Producto definido y con capacidad de produccion"),
        ("Precio", "Competitivo frente al mercado del sector"),
    ]))
    cuerpo += card("Oportunidades de mejora", lista_def([
        ("Parte administrativa y legal", "Sin forma juridica definida ni registro"),
        ("Camara de comercio", "No esta registrado"),
        ("Financiamiento", "Depende de ahorro propio"),
        ("Local", "No tiene local propio"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<a class="btn btn-primario" href="caracterizacion-form.html">'
                     "%s Editar formulario 2</a>" % ico("edit", 16)
                   + '<button class="btn btn-secundario" data-accion="descargar">'
                     "%s Descargar diagnostico</button>" % ico("download", 16)
                   + '<button class="btn btn-secundario" data-accion="asignar-docente" '
                     'data-acta="Aprobada">%s Asignar docente</button>' % ico("sliders", 16)
                   + "</div>")
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += card("Recomendacion de la asesora", '<div class="card-body">'
                   + callout("El diagnostico sugiere empezar por la parte "
                             "administrativo-financiera: es la seccion mas debil "
                             "y la que mas afecta la formalizacion.", "alerta")
                   + '<div class="sep"></div>'
                   + _campo_texto("r", "Comentario para el docente", area=True,
                                  ayuda="Se envia junto al diagnostico")
                   + '<div class="form-acciones">'
                     '<button class="btn btn-primario" data-accion="guardar">'
                     "%s Guardar comentario</button></div>" % ico("check", 16)
                   + "</div>")
    return shell(R, "inscripciones", "Caracterizacion y diagnostico", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Inscripciones",
                        "Diagnostico"],
                 sub="Resultado generado a partir del formulario 2.",
                 acciones='<a class="btn btn-secundario" href="inscripcion-detalle.html">'
                          "%s Volver al expediente</a>" % ico("izq", 16))

# --- 59. Formulario 1: inscripcion del estudiante ---------------------------
# Es el primer paso del proceso (FLUJO-DE-ATENCION.md, paso 1). Lo llena el
# estudiante por su cuenta; la asesora lo recibe en la bandeja, lo revisa y lo
# habilita para la primera asesoria.
def inscripcion_form():
    i = D.INSCRIPCIONES[0]
    cod, nombre, programa, sede, cond, sem, tipo, fecha, estado, acta = i
    cuerpo = callout("Este es el <b>formulario 1</b> de inscripcion. Lo responde el "
                     "estudiante por su cuenta; al enviarlo le llega la "
                     "notificacion a la asesora y queda en la bandeja.", "clipboard")
    cuerpo += '<div class="sep"></div>'
    cuerpo += steps(["Inscripcion", "Revision de la asesora",
                     "Primera asesoria", "Formulario 2"], 1)
    cuerpo += '<div class="sep-lg"></div>'
    cuerpo += metricas([
        ("clipboard", "Campos del formulario", "18", "", 100, None),
        ("check", "Campos completos", "18", "/ 18", 100, None),
        ("reloj", "Enviado", fecha, "", 100, None),
        ("bell", "Estado del flujo", "En revision", "", 30, None),
    ])
    cuerpo += '<div class="sep"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid g-gap">'
    cuerpo += form_acciones(
        "1. Datos personales del estudiante",
        grupo_campos("Identificacion",
                     campo("Codigo de inscripcion", valor=cod,
                           bloqueo="Lo asigna el sistema")
                     + campo("Nombres", valor="Mariana", req=True, requerido=True)
                     + campo("Apellidos", valor="Lopez", req=True, requerido=True)
                     + campo("Tipo de documento", req=True, requerido=True)
                     + campo("Numero de documento", valor="1020304050", req=True,
                             requerido=True)
                     + campo("Fecha de nacimiento", tipo="date", valor="2002-08-14",
                             req=True, requerido=True)
                     + campo("Correo institucional", tipo="email",
                             valor="mariana.lopez@sgemd.edu.co", req=True,
                             requerido=True)
                     + campo("Telefono", tipo="tel", valor="+57 315 555 0140",
                             req=True, requerido=True)
                     + campo("Ciudad de residencia", valor="Ibague", req=True,
                             requerido=True)),
        exito="Datos personales guardados.", etiqueta="Guardar datos",
        ok_id="acceso-ok-if-1", estricto=True)
    cuerpo += form_acciones(
        "2. Datos academicos",
        select("Sede", D.SEDES, req=True, requerido=True, valor=sede)
        + select("Programa", D.PROGRAMAS, req=True, requerido=True, valor=programa)
        + select("Condicion academica", D.CONDICION_ACADEMICA, req=True,
                 requerido=True, valor=cond)
        + campo("Semestre", tipo="number", valor=sem or "6",
                ayuda="Solo si la condicion academica indica que sigue estudiando")
        + campo("Telefono de emergencia", tipo="tel", valor="+57 315 555 0199")
        + campo("Contacto de emergencia", valor="Claudia Lopez"),
        exito="Datos academicos guardados.", etiqueta="Guardar academicos",
        ok_id="acceso-ok-if-2", estricto=True)
    cuerpo += form_acciones(
        "3. El emprendimiento",
        campo("Nombre del emprendimiento", valor="Sabor y Sabe", req=True,
              requerido=True)
        + campo_radio_cards("Tipo de emprendimiento", D.TIPO_EMPRENDIMIENTO,
                            valor=tipo)
        + campo("Sector economico", valor="Alimentos")
        + campo("Fecha de inicio", tipo="date", valor="2024-03-01")
        + campo("Numero de personas", tipo="number", valor="2")
        + campo("Quien se entero del servicio", valor="Tecnologia en Gestion Comercial"),
        exito="Datos del emprendimiento guardados.",
        etiqueta="Guardar emprendimiento", ok_id="acceso-ok-if-3", estricto=True)
    cuerpo += form_acciones(
        "4. Motivacion y autorizacion",
        _campo_texto("m1", "Por que se inscribio en el servicio", req=True,
                     area=True, ayuda="Cuenta en una o dos frases")
        + _campo_texto("m2", "Que espera del acompanamiento", area=True)
        + campo_check("Autorizo el tratamiento de mis datos personales",
                      ayuda="Obligatorio para gestionar el acompañamiento",
                      marcado=True, requerido=True)
        + campo_check("Acepto la politica de tratamiento de datos", marcado=True,
                      requerido=True),
        exito="Formulario completo. Queda enviado a la asesora.",
        etiqueta="Enviar formulario 1", ok_id="acceso-ok-if-4", estricto=True)
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-gap">'
    cuerpo += card("Estado del formulario", lista_def([
        ("Estado del flujo", estado),
        ("Fecha de envio", fecha),
        ("Correo institucional", "mariana.lopez@sgemd.edu.co"),
        ("Revisado por", "Pendiente"),
        ("Acta", acta),
    ]))
    cuerpo += card("Acciones",
                   '<div class="col-acciones">'
                   + '<button class="btn btn-primario" data-accion="notificar-revision">'
                     "%s Notificar a la asesora</button>" % ico("bell", 16)
                   + '<button class="btn btn-secundario" data-accion="habilitar-form2">'
                     "%s Habilitar formulario 2</button>" % ico("clipboard", 16)
                   + '<a class="btn btn-secundario" href="inscripcion-detalle.html">'
                     "%s Ver expediente</a>" % ico("doc", 16)
                   + "</div>")
    cuerpo += card("Que sigue", lista_def([
        ("1", "Revision de la asesora"),
        ("2", "Correo de bienvenida y agenda de la primera asesoria"),
        ("3", "Formulario 2 de caracterizacion y valoracion"),
        ("4", "Acta firmada y asignacion de docente"),
    ]))
    cuerpo += card("Ingreso al servicio por mes", barras(
        "Ingreso al servicio por mes", "Inscripciones recibidas en el periodo",
        ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        [6, 9, 12, 14, 18, 11], unidad=" inscripciones"))
    cuerpo += card("Pendientes de esta inscripcion", lista_avisos([
        ("Antes de la primera asesoria", [
            ("clipboard", "Revisar los datos del formulario 1",
             "La asesora confirma sede, programa y condicion academica",
             "inscripcion-form.html", "alta",
             badge("18 de 18", "b-azul")),
            ("mail", "Enviar el correo de bienvenida",
             "Reunamonos para el proceso de Gizgado",
             "inscripcion-form.html", "media",
             badge("Pendiente", "b-amarillo")),
        ]),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep"></div>'
    cuerpo += zona_crud(
        "inscripcion-datos", "Datos declarados por el estudiante",
        [("codigo", "Campo"), ("valor", "Valor declarado"),
         ("seccion", "Seccion"), ("estado", "Estado")],
        [{"codigo": c, "valor": v, "seccion": sec, "estado": "Verificado"}
         for c, v, sec in [
             ("Nombre", "Sabor y Sabe", "Emprendimiento"),
             ("Tipo", tipo, "Emprendimiento"),
             ("Sede", sede, "Academica"),
             ("Programa", programa, "Academica"),
             ("Condicion", cond, "Academica"),
             ("Semestre", sem or "No aplica", "Academica"),
             ("Ciudad", "Ibague", "Personal"),
             ("Contacto de emergencia", "Claudia Lopez", "Personal"),
         ]],
        [{"n": "valor", "l": "Valor declarado", "t": "text", "req": True},
         {"n": "seccion", "l": "Seccion", "t": "select",
          "o": ["Personal", "Academica", "Emprendimiento", "Motivacion"],
          "req": True},
         {"n": "estado", "l": "Estado", "t": "select",
          "o": ["Verificado", "Pendiente", "Rechazado"]}],
        singular="dato", nueva="Nuevo dato", prefijo="ID-",
        badges=("estado",), tonos=TONOS,
        filtros=_sel("Seccion", ["Personal", "Academica", "Emprendimiento",
                                 "Motivacion"], col=2),
        hint="Cada dato declarado por el estudiante queda con su seccion, para "
             "revisarlo rapido cuando la asesora recibe la inscripcion.")
    return shell(R, "inscripciones", "Formulario 1 de inscripcion", cuerpo,
                 migas=["Inicio", "Acompanamiento", "Inscripciones",
                        "Formulario 1"],
                 sub="Datos que declara el estudiante al inscribirse.",
                 acciones='<a class="btn btn-secundario" href="inscripciones.html">'
                          "%s Volver a la bandeja</a>" % ico("izq", 16))

