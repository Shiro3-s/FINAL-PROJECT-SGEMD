# -*- coding: utf-8 -*-
"""Componentes de interfaz del prototipo SGEMD."""

import re

from lib_css import LOGO_BLANCO

# --- Iconos (Lucide 24x24, stroke) -------------------------------------------
ICONOS = {
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "pie": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "trend": '<path d="m23 6-9.5 9.5-5-5L1 18"/><path d="m17 6 6 0 0 6"/>',
    "maleta": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect x="2" y="6" width="20" height="14" rx="2"/>',
    "clipboard": '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="m9 14 2 2 4-4"/>',
    "checklist": '<path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "bell": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>',
    "menu": '<path d="M3 12h18M3 6h18M3 18h18"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
    "edit": '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z"/>',
    "trash": '<path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "filter": '<path d="M22 3H2l8 9.46V19l4 2v-8.54z"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "izq": '<path d="m15 18-6-6 6-6"/>',
    "der": '<path d="m9 18 6-6-6-6"/>',
    "abajo": '<path d="m6 9 6 6 6-6"/>',
    "bombilla": '<path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>',
    "engranaje": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/>',
    "arriba": '<path d="M12 19V5M5 12l7-7 7 7"/>',
    "clip": '<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
    "enviar": '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    "alerta": '<path d="m10.29 3.86-8.47 14.14A2 2 0 0 0 3.53 21h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/>',
    "reloj": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "tel": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8M16 17H8M10 9H8"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "rayo": '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    "puntos": '<path d="M12 12h.01M19 12h.01M5 12h.01"/>',
    "salir": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
    "carpeta": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "medalla": '<circle cx="12" cy="8" r="6"/><path d="m15.5 13.5 1.5 8.5-5-3-5 3 1.5-8.5"/>',
    "libro": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "grid": '<path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/>',
    "bd": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "escudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "play": '<path d="m5 3 14 9-14 9z"/>',
    "filtro2": '<path d="M3 6h18M7 12h10M11 18h2"/>',
}


def ico(nombre, tam=18, extra=""):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"%s>%s</svg>'
        % (tam, tam, extra, ICONOS[nombre])
    )


# --- Navegacion por rol ------------------------------------------------------
NAV = {
    "estudiante": [
        ("Inicio", "home", "dashboard"),
        ("Estado de seguimiento", "trend", "estado-seguimiento"),
        ("Mi emprendimiento", "maleta", "emprendimientos"),
        ("Diagnostico", "clipboard", "diagnostico"),
        ("Plan de trabajo", "layers", "plan-trabajo"),
        ("Seguimiento", "doc", "seguimiento"),
        ("Tareas", "checklist", "tareas"),
        ("Asesorias", "chat", "asesorias"),
        ("Eventos", "calendar", "eventos"),
        ("Notificaciones", "bell", "notificaciones"),
        ("Perfil", "user", "perfil"),
    ],
    "docente": [
        ("Inicio", "pie", "dashboard"),
        ("Mis asesorias", "chat", "asesorias"),
        ("Emprendimientos asignados", "maleta", "emprendimientos"),
        ("Seguimiento", "trend", "seguimiento"),
        ("Diagnostico", "clipboard", "diagnostico"),
        ("Tareas", "checklist", "tareas"),
        ("Notificaciones", "bell", "notificaciones"),
        ("Perfil", "user", "perfil"),
    ],
    "administrador": [
        ("Inicio", "grid", "dashboard"),
        ("Gestion de perfiles", "users", "usuarios"),
        ("Emprendimientos", "maleta", "emprendimientos"),
        ("Seguimiento", "trend", "seguimiento"),
        ("Asignaciones", "sliders", "asignaciones"),
        ("Diagnosticos", "clipboard", "diagnosticos"),
        ("Eventos", "calendar", "eventos"),
        ("Asesorias", "chat", "asesorias"),
        ("Reportes", "download", "reportes"),
        ("Notificaciones", "bell", "notificaciones"),
        ("Perfil", "user", "perfil"),
    ],
}

ROLES = {
    "estudiante": ("ESTUDIANTE", "Mariana Lopez", "ML"),
    "docente": ("DOCENTE", "Carlos Mendoza", "CM"),
    "administrador": ("ADMINISTRADOR", "Ana Restrepo", "AR"),
}

# El logo aparece UNA sola vez por pantalla. En escritorio vive en la sidebar
# (siempre visible); el del topbar solo se muestra por CSS cuando la sidebar
# pasa a modo off-canvas (<=1023px), de modo que nunca hay dos a la vez.
# width/height declaran la proporcion intrinseca (600x286 = 2.0979:1) para que el
# navegador reserve la caja antes de pintar y no haya salto de layout.
LOGO_TILE = (
    '<span class="brand-tile">'
    '<img src="%s" width="600" height="286" decoding="async"'
    ' alt="SGEMD, Emprendimiento Minuto de Dios"></span>' % LOGO_BLANCO
)


# Intencion de cada icono de boton. El icono ya distinguia la intencion en el
# diseno (ojo=ver, lapiz=editar, check=aprobar, papelera=borrar); lo que faltaba
# era el gancho legible por maquina. Antes, 130 botones no tenian ni clase ni
# data-*, asi que el JS no tenia forma de saber que hacer con cada uno y acababa
# adivinando por el <path> del SVG. El mapa vive aqui y es el unico sitio que hay
# que tocar para anadir una accion nueva.
ICONO_ACCION = {
    "eye": "ver",
    "edit": "editar",
    "check": "aprobar",
    "trash": "borrar",
    "download": "descargar",
    "x": "cerrar",
    "calendar": "inscribirse",
    "clip": "evidencia",
    "check2": "aprobar",
    "play": "iniciar",
}


def boton_accion(icono, etiqueta, clase=""):
    """Boton de accion de tabla: icono + etiqueta accesible + data-accion."""
    accion = ICONO_ACCION.get(icono, "accion")
    c = ' class="%s"' % clase if clase else ""
    return ('<button%s data-accion="%s" title="%s" aria-label="%s">%s</button>'
            % (c, accion, etiqueta, etiqueta, ico(icono, 16)))


def shell(rol, activo, titulo, cuerpo, migas=None, notif=3, acciones="", sub=None, extra_head=""):
    """Envoltorio completo: sidebar + header + contenido."""
    etiqueta, nombre, iniciales = ROLES[rol]
    items = "".join(
        '<a class="%s" href="%s.html">%s<span>%s</span></a>'
        % ("activo" if clave == activo else "", clave, ico(ic), txt)
        for txt, ic, clave in NAV[rol]
    )
    m = ""
    if migas:
        m = '<div class="crumbs">' + " &rsaquo; ".join(
            '<a href="#">' + x + "</a>" if i < len(migas) - 1 else x
            for i, x in enumerate(migas)
        ) + "</div>"
    encabezado = "<h1>%s</h1>" % titulo
    if sub:
        encabezado += '<p class="sub">%s</p>' % sub
    cab = '<div class="page-head">%s<div class="acciones">%s</div></div>' % (encabezado, acciones)
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titulo)s — SGEMD</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>%(css)s</style>
</head>
<body>
<div class="shell">
  <aside class="sidebar" id="sb">
    <div class="brand">%(logo)s
      <div class="brand-text"><div class="brand-name">SGEMD</div>
      <div class="brand-sub">Emprendimiento Minuto de Dios</div></div>
    </div>
    <nav class="nav">%(items)s</nav>
    <div class="side-foot"><div class="side-card">
      <b>Institucion Minuto de Dios</b>
      <span>Modulo %(rol)s</span>
    </div></div>
  </aside>
  <div class="main">
    <header class="topbar">
      <button class="burger" data-accion="menu" aria-label="Abrir menu" aria-expanded="false">%(ico_menu)s</button>
      <div class="topbar-mark" aria-hidden="true"></div>
      <div class="search">%(ico_search)s
        <input type="text" placeholder="Buscar en el sistema" aria-label="Buscar en el sistema">
      </div>
      <div class="topbar-right">
        <button class="icon-btn" data-accion="notificaciones" aria-label="Notificaciones">%(ico_bell)s<span class="count">%(notif)d</span></button>
        <div class="who"><span class="avatar">%(ini)s</span>
          <div><div class="who-name">%(nombre)s</div><span class="who-role">%(etiqueta)s</span></div>
        </div>
      </div>
    </header>
    <main class="content">%(migas)s%(cab)s%(cuerpo)s</main>
  </div>
</div>
<div class="overlay" id="ov"></div>
<script>%(js)s</script>
</body>
</html>""" % {
        "titulo": titulo,
        "css": CSS,
        "logo": LOGO_TILE,
        "items": items,
        "rol": etiqueta,
        "etiqueta": etiqueta,
        "nombre": nombre,
        "ini": iniciales,
        "notif": notif,
        "ico_menu": ico("menu", 20),
        "ico_search": ico("search", 16),
        "ico_bell": ico("bell", 18),
        "js": JS,
        "migas": m,
        "cab": cab,
        "cuerpo": cuerpo,
    }


from lib_js import JS
from lib_css import CSS  # noqa: E402  (import tardio para evitar ciclo)


# --- Bloques de pagina -------------------------------------------------------
def metricas(items):
    """items: lista de (icono, etiqueta, valor, unidad, barra_%, delta)"""
    out = ['<div class="grid g-4">']
    for ic, lbl, val, uni, barra, delta in items:
        d = '<span class="metrica-delta">%s %s</span>' % (ico("trend", 13), delta) if delta else ""
        out.append(
            '<div class="card metrica"><div class="metrica-top">'
            '<span class="metrica-ico">%s</span>'
            '<div><div class="metrica-lbl">%s</div>'
            '<div class="metrica-val">%s<span class="u">%s</span></div></div>%s</div>'
            '<div class="barra"><span style="width:%d%%"></span></div></div>'
            % (ico(ic, 18), lbl, val, uni, d, barra)
        )
    out.append("</div>")
    return "".join(out)


def th(c):
    """Construye un <th>. Acepta 'Etiqueta', ('num','Etiqueta') o '@ACC'."""
    if c == "@ACC":
        return '<th scope="col" class="acc">Acciones</th>'
    if isinstance(c, tuple):
        return '<th scope="col" class="%s">%s</th>' % (c[0], c[1])
    return '<th scope="col">%s</th>' % c


def _etiqueta(c):
    """Texto plano de una cabecera, para el data-label de la vista tarjeta.

    A 375px la tabla se apila en tarjetas y cada celda necesita saber a que
    columna pertenece; sin esto la fila se lee como un bloque de texto suelto.
    """
    if c == "@ACC":
        return "Acciones"
    if isinstance(c, tuple):
        c = c[1]
    return re.sub(r"<[^>]+>", "", str(c)).strip()


def tabla(cabeceras, filas, con_checkbox=False):
    """cabeceras: lista de 'Etiqueta' | ('num','Etiqueta') | '@ACC'.
    filas: listas de HTML con la misma longitud que cabeceras."""
    cab = ""
    if con_checkbox:
        cab += ('<th scope="col" style="width:44px">'
                '<input type="checkbox" aria-label="Seleccionar todo" '
                'style="accent-color:#004a93;width:16px;height:16px"></th>')
    cab += "".join(th(c) for c in cabeceras)
    sel = ('<td class="sel"><input type="checkbox" aria-label="Seleccionar fila" '
           'style="accent-color:#004a93;width:16px;height:16px"></td>') if con_checkbox else ""
    etiquetas = [_etiqueta(c) for c in cabeceras]
    body = ""
    for f in filas:
        celdas = ""
        for c, x, eti in zip(cabeceras, f, etiquetas):
            if c == "@ACC":
                celdas += '<td class="acc" data-label="%s">%s</td>' % (eti, x)
            elif isinstance(c, tuple) and c[0] == "num":
                celdas += '<td class="num" data-label="%s">%s</td>' % (eti, x)
            else:
                celdas += '<td data-label="%s">%s</td>' % (eti, x)
        body += "<tr>%s%s</tr>" % (sel, celdas)
    return (
        '<div class="card tabla-envoltura"><div class="tabla-scroll">'
        '<table class="tabla"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
        "</div></div>" % (cab, body)
    )


def toolbar(buscar=True, filtros="", acciones="", extra=""):
    s = ""
    if buscar:
        s += ('<div class="buscador crece">%s<input type="text" placeholder="Buscar" aria-label="Buscar"></div>'
              % ico("search", 16))
    return '<div class="toolbar">%s%s%s</div>' % (s, filtros, extra or acciones)


def paginas(desde, hasta, total):
    return (
        '<div class="paginacion"><span>Mostrando %d a %d de %d</span>'
        '<div class="pag"><button class="btn btn-secundario btn-sm">%s Anterior</button>'
        '<button class="btn btn-secundario btn-sm">Siguiente %s</button></div></div>'
        % (desde, hasta, total, ico("izq", 14), ico("der", 14))
    )


def badge(texto, tipo="neutra", icono=None):
    return '<span class="badge b-%s">%s%s</span>' % (
        tipo, ico(icono, 12) if icono else "", texto)


def _fid(prefijo="f"):
    """Id unico por control, para que cada label este asociado al input correcto."""
    global _CONTADOR
    _CONTADOR += 1
    return "%s%d" % (prefijo, _CONTADOR)


_CONTADOR = 0


def campo(label, tipo="text", valor="", ph="", req=False, ayuda="", bloqueo="", alto=False):
    i = _fid("f")
    h = '<div class="campo"><label for="%s">%s%s</label>' % (
        i, label, '<span class="req">*</span>' if req else "")
    if bloqueo:
        h += ('<input id="%s" type="text" value="%s" disabled>'
              '<div class="bloqueo">%s%s</div></div>' % (i, valor, ico("lock", 12), bloqueo))
    elif alto:
        h += '<textarea id="%s" placeholder="%s">%s</textarea>' % (i, ph, valor)
        if ayuda:
            h += '<div class="ayuda">%s%s</div>' % (ico("alerta", 13), ayuda)
        h += "</div>"
    else:
        h += '<input id="%s" type="%s" value="%s" placeholder="%s"%s>' % (
            i, tipo, valor, ph, " required" if req else "")
        if ayuda:
            h += '<div class="ayuda">%s%s</div>' % (ico("alerta", 13), ayuda)
        h += "</div>"
    return h


def select(label, opciones, req=False, bloqueo="", valor=None):
    i = _fid("s")
    h = '<div class="campo"><label for="%s">%s%s</label><select id="%s"%s>' % (
        i, label, '<span class="req">*</span>' if req else "", i,
        " disabled" if bloqueo else "")
    for o in opciones:
        sel = " selected" if valor and o == valor else ""
        h += '<option%s>%s</option>' % (sel, o)
    h += "</select>"
    if bloqueo:
        h += '<div class="bloqueo">%s%s</div>' % (ico("lock", 12), bloqueo)
    h += "</div>"
    return h


def callout(txt, icono="alerta"):
    return '<div class="callout">%s<div>%s</div></div>' % (ico(icono, 18), txt)


def card(titulo, cuerpo, hint="", accion="", sin_pad=False):
    return (
        '<div class="card"><div class="card-head"><h3>%s</h3>%s<span class="hint">%s</span></div>'
        '<div class="card-body%s">%s</div></div>'
        % (titulo, accion, hint, " sin-pad" if sin_pad else "", cuerpo)
    )


def estado_vacio(titulo, txt, accion="", icono="doc"):
    return ('<div class="vacio">%s<h3>%s</h3><p>%s</p>%s</div>'
            % (ico(icono, 40), titulo, txt, accion))


def lista_def(filas):
    h = '<dl class="lista-def">'
    for k, v in filas:
        h += '<div class="def-row"><dt>%s</dt><dd>%s</dd></div>' % (k, v)
    return h + "</dl>"


def steps(items, actual=0):
    h = '<div class="steps">'
    for i, it in enumerate(items):
        if i < actual:
            cls, marca = "hecho", ico("check", 14)
        elif i == actual:
            cls, marca = "activo", str(i + 1)
        else:
            cls, marca = "", str(i + 1)
        h += '<div class="step %s"><i>%s</i><b>%s</b></div>' % (cls, marca, it)
        if i < len(items) - 1:
            h += '<div class="step-line"></div>'
    return h + "</div>"


def tabs(items, activo=0):
    h = '<div class="tabs">'
    for i, it in enumerate(items):
        h += '<button class="%s">%s</button>' % ("activo" if i == activo else "", it)
    return h + "</div>"


# --- Bloques de listado alternativos -----------------------------------------
# Complementan a tabla() para que las pantallas de un mismo rol no repitan
# siempre el mismo arquetipo visual: lista agrupada por urgencia, tablero,
# linea de tiempo, agenda por dia, tarjetas con avance y distribucion.
_URGENCIA = {"alta": "alta", "media": "media", "baja": "baja"}


def _aviso(estado):
    return _URGENCIA.get(estado, "baja")


def aviso_grupo(titulo, items):
    """items: (icono, titulo, meta, href, estado, acciones_html)."""
    h = ('<section class="aviso-grp"><div class="aviso-grp-head">'
         '<h3 class="aviso-grp-titulo">%s</h3>'
         '<span class="aviso-grp-n">%d</span></div>' % (titulo, len(items)))
    for ic, tit, meta, href, estado, acc in items:
        h += ('<article class="aviso u-%s"><span class="aviso-ico">%s</span>'
              '<div class="aviso-txt"><a class="aviso-titulo" href="%s">%s</a>'
              '<div class="aviso-meta">%s</div></div>'
              '<div class="aviso-acc">%s</div></article>'
              % (_aviso(estado), ico(ic, 18), href, tit, meta, acc))
    return h + "</section>"


def lista_avisos(grupos):
    """grupos: lista de (titulo, items) tal como los recibe aviso_grupo."""
    return '<div class="avisos">' + "".join(
        aviso_grupo(t, it) for t, it in grupos) + "</div>"


def kanban(columnas):
    """columnas: lista de (titulo, [(titulo, meta, badge_html, pie_html)])."""
    h = '<div class="kanban">'
    for titulo, tarjetas in columnas:
        h += ('<section class="kan-col"><div class="kan-head">'
              '<span class="kan-titulo">%s</span>'
              '<span class="kan-n">%d</span></div>' % (titulo, len(tarjetas)))
        for t, meta, bd, pie in tarjetas:
            h += ('<article class="kan-card"><div class="kan-card-titulo">%s</div>'
                  '<div class="kan-meta">%s</div>'
                  '<div class="kan-foot">%s%s</div></article>' % (t, meta, bd, pie))
        if not tarjetas:
            h += '<div class="kan-empty">Sin pendientes</div>'
        h += "</section>"
    return h + "</div>"


def linea_tiempo(items):
    """items: lista de (dia, mes, titulo, meta, extra_html)."""
    h = '<ol class="linea">'
    for dia, mes, titulo, meta, extra in items:
        h += ('<li class="ln-item"><div class="ln-fecha"><b>%s</b><span>%s</span></div>'
              '<div class="ln-cuerpo"><div class="ln-titulo">%s</div>'
              '<div class="ln-meta">%s</div>%s</div></li>'
              % (dia, mes, titulo, meta, extra))
    return h + "</ol>"


def agenda(dias):
    """dias: lista de (etiqueta, [(hora, titulo, meta, badge_html)])."""
    h = '<div class="agenda">'
    for etiqueta, eventos in dias:
        n = len(eventos)
        h += ('<section class="ag-dia"><div class="ag-dia-h"><b>%s</b>'
              '<span>%d %s</span></div>'
              % (etiqueta, n, "evento" if n == 1 else "eventos"))
        for hora, titulo, meta, bd in eventos:
            h += ('<article class="ag-ev"><span class="ag-hora">%s</span>'
                  '<div class="ag-txt"><div class="ag-titulo">%s</div>'
                  '<div class="ag-meta">%s</div></div>%s</article>'
                  % (hora, titulo, meta, bd))
        h += "</section>"
    return h + "</div>"


def tarjeta_emp(icono, titulo, meta, avance, pie_izq, pie_der, extra=""):
    barra = ""
    if avance is not None:
        barra = ('<div class="barra amarilla" style="margin-top:14px">'
                 '<span style="width:%d%%"></span></div>' % avance)
    return ('<article class="emp-card"><div class="emp-top">'
            '<span class="emp-ico">%s</span><div class="emp-txt">'
            '<div class="emp-titulo">%s</div><div class="emp-meta">%s</div>'
            '</div></div>%s%s<div class="emp-foot"><span>%s</span>'
            '<b>%s</b></div></article>'
            % (ico(icono, 20), titulo, meta, barra, extra, pie_izq, pie_der))


def distribucion(filas):
    """filas: lista de (rango, cantidad, porcentaje_ancho)."""
    h = '<div class="dist">'
    for rango, cant, pct in filas:
        h += ('<div class="dist-row"><span class="dist-lbl">%s</span>'
              '<span class="dist-bar"><i style="width:%d%%"></i></span>'
              '<span class="dist-val">%s</span></div>' % (rango, pct, cant))
    return h + "</div>"