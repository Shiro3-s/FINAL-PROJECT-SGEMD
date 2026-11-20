# -*- coding: utf-8 -*-
"""Rol SUPER ADMIN - gestion de perfiles.

Reglas del rol (segun el alcance del proyecto):
  - Su unica responsabilidad es la gestion de perfiles de usuario.
  - Puede crear, consultar, editar, activar/desactivar y ajustar permisos.
  - Solo asigna los tres roles existentes: Estudiante, Docente y Administrador.
  - No crea otros Super Admin ni cambia el rol de un perfil.
  - Nada se elimina: retirar el acceso es desactivar la cuenta.
  - No gestiona emprendimientos, asesorias, eventos, tareas, diagnosticos ni
    informacion academica: esas vistas no existen en este modulo.

Cada persona tiene dos identificadores distintos y obligatorios al crear:
  - Identificacion: documento personal (cedula, tarjeta, etc.).
  - ID institucional: codigo que asigna la universidad (estudiante, docente o
    administrador).

Los datos de los perfiles se toman de los registros que ya existen en el
prototipo (paginas_admin.DOCENTES / ESTUDIANTES y la cuenta institucional del
administrador). No se inventan usuarios. Las altas y ediciones del modulo viven
en localStorage porque el prototipo no tiene backend.
"""

import json
from urllib.parse import quote

from lib_ui import (
    shell, metricas_enlace, badge, campo, callout, card, estado_vacio,
    formulario, lista_def, steps, ico, th, NAV,
)
from paginas_admin import DOCENTES, ESTUDIANTES, CORREOS_EST, SEDE_EST, ADMIN_CSS

R = "superadmin"

_MESES = ["ene", "feb", "mar", "abr", "may", "jun",
          "jul", "ago", "sep", "oct", "nov", "dic"]

# Fecha de referencia del prototipo (los datos de ejemplo viven en nov 2024).
HOY = "12 nov 2024"

ROLES_ASIGNABLES = ["Estudiante", "Docente", "Administrador"]
ROLES_ORDEN = ["Docente", "Estudiante", "Administrador"]

# Todos los correos institucionales usan el mismo dominio.
DOMINIO = "uniminuto.edu.co"


def _correo_institucional(correo):
    """Normaliza un correo existente al dominio institucional vigente."""
    base = (correo or "").split("@")[0].strip()
    return "%s@%s" % (base, DOMINIO)


# --- Permisos reales del sistema ---------------------------------------------
# Se derivan del menu lateral de cada rol: cada modulo y cada vista existente
# se convierte en un permiso. No se agregan funcionalidades que el prototipo
# no tenga. Super Admin queda fuera: no es un rol asignable.
def _permisos_por_rol():
    out = {}
    for rol, items in NAV.items():
        if rol == R:
            continue
        modulos = []
        for e in items:
            if len(e) >= 3:
                modulos.append({"modulo": e[0], "items": [e[0]]})
            else:
                modulos.append({"modulo": e[0], "items": [h[0] for h in e[1]]})
        out[rol.capitalize()] = modulos
    return out


PERMISOS_ROL = _permisos_por_rol()


def _permisos_defecto(rol):
    return ["%s::%s" % (m["modulo"], it)
            for m in PERMISOS_ROL[rol] for it in m["items"]]


# --- Perfiles existentes ------------------------------------------------------
# Se reutilizan los datos de las vistas actuales. La identificacion personal
# solo se conoce cuando el prototipo la muestra (Mariana y Carlos). El resto
# queda vacio: no se inventan documentos. El ID institucional es el codigo que
# ya usan las vistas (912646, DOC-014, etc.).
_IDENTIFICACION = {
    "912646": "1020304050",   # Mariana Lopez
    "DOC-014": "79 456 123",  # Carlos Mendoza
}

PERFILES = []

for _cod, _nom, _correo, _area, _carga, _emp, _estado in DOCENTES:
    PERFILES.append({
        "clave": _correo_institucional(_correo),
        "identificacion": _IDENTIFICACION.get(_cod, ""),
        "id_institucional": _cod,
        "nombre": _nom,
        "correo": _correo_institucional(_correo),
        "rol": "Docente",
        "estado": _estado,
        "fecha": "",
        "origen": "docente",
        "detalle": {
            "Area de conocimiento": _area,
            "Carga semanal": _carga,
            "Emprendimientos asignados": _emp,
        },
        "permisos": _permisos_defecto("Docente"),
        "password": "",
        "debe_cambiar": False,
    })

for _cod, _nom, _sector, _emp, _etapa, _avance, _estado in ESTUDIANTES:
    PERFILES.append({
        "clave": _correo_institucional(CORREOS_EST[_nom]),
        "identificacion": _IDENTIFICACION.get(_cod, ""),
        "id_institucional": _cod,
        "nombre": _nom,
        "correo": _correo_institucional(CORREOS_EST[_nom]),
        "rol": "Estudiante",
        "estado": _estado,
        "fecha": "12 mar 2024" if _cod == "912646" else "",
        "origen": "estudiante",
        "detalle": {
            "Sector": _sector,
            "Emprendimiento": _emp,
            "Etapa": _etapa,
            "Avance": "%d%%" % _avance,
            "Sede": SEDE_EST.get(_nom, ""),
        },
        "permisos": _permisos_defecto("Estudiante"),
        "password": "",
        "debe_cambiar": False,
    })

# Cuenta institucional del administrador: ya existe en ROLES/perfil/configuracion.
PERFILES.append({
    "clave": "adm:" + _correo_institucional("ana.restrepo@sgemd.edu.co"),
    "identificacion": "",
    "id_institucional": "",
    "nombre": "Ana Restrepo",
    "correo": _correo_institucional("ana.restrepo@sgemd.edu.co"),
    "rol": "Administrador",
    "estado": "Activo",
    "fecha": "",
    "origen": "administrador",
    "detalle": {
        "Cargo": "Administradora del programa",
        "Teléfono": "+57 301 555 0199",
        "Zona horaria": "America/Bogota",
        "Sede principal": "Sede Norte",
    },
    "permisos": _permisos_defecto("Administrador"),
    "password": "",
    "debe_cambiar": False,
})

# Cuenta propia del Super Admin. No forma parte de la tabla de perfiles
# gestionados: vive en su propia vista (Mi perfil) y en su propia clave de
# localStorage para no mezclarse con los usuarios creados.
CUENTA_SA = {
    "nombre": "Laura Gómez",
    "identificacion": "52 789 431",
    "id_institucional": "SA-001",
    "correo": "laura.gomez@uniminuto.edu.co",
    "cargo": "Super Administradora SGEMD",
    "telefono": "+57 310 555 0142",
    "fecha": "8 ene 2024",
    "password": "superadmin",
}


def _permisos_completos(p):
    return set(p["permisos"] or []) >= set(_permisos_defecto(p["rol"]))


def _estado(p):
    """Estado visible: Inactivo manda; si faltan permisos, es Limitado."""
    if p.get("estado") == "Inactivo":
        return "Inactivo"
    return "Activo" if _permisos_completos(p) else "Limitado"


def _total(rol=None):
    return sum(1 for p in PERFILES if rol is None or p["rol"] == rol)


def _activos(rol=None):
    return sum(1 for p in PERFILES
               if _estado(p) == "Activo" and (rol is None or p["rol"] == rol))


def _inactivos(rol=None):
    return sum(1 for p in PERFILES
               if _estado(p) == "Inactivo" and (rol is None or p["rol"] == rol))


def _limitados(rol=None):
    return sum(1 for p in PERFILES
               if _estado(p) == "Limitado" and (rol is None or p["rol"] == rol))


def _estado_badge(estado):
    tipo = {"Activo": "b-azul", "Limitado": "b-amarillo",
            "Inactivo": "b-neutra"}.get(estado, "b-neutra")
    icono = {"Activo": "check", "Limitado": "alerta",
             "Inactivo": "lock"}.get(estado, "lock")
    return badge(estado, tipo, icono)


# --- Tabla de perfiles --------------------------------------------------------
_CABECERAS = ["Nombre completo", "Correo institucional", "Identificación",
              "ID institucional", "Rol", "Estado", "Fecha de creación", "@ACC"]


def _acciones_perfil(p):
    clave = quote(p["clave"], safe="")
    nombre = p["nombre"]

    def enlace(archivo, icono, etiqueta, aria):
        return ('<a class="table-act" href="%s?clave=%s" title="%s" '
                'aria-label="%s">%s</a>'
                % (archivo, clave, etiqueta, aria, ico(icono, 16)))

    return (
        '<button type="button" class="table-act" data-sa-accion="ver" '
        'data-clave="%s" title="Ver detalle" aria-label="Ver detalle de %s">%s</button>'
        % (p["clave"], nombre, ico("eye", 16))
        + enlace("editar-perfil.html", "edit", "Editar perfil",
                 "Editar el perfil de %s" % nombre)
        + enlace("permisos.html", "sliders", "Gestionar permisos",
                 "Gestionar permisos de %s" % nombre)
    )


def _fila_perfil(p):
    return (
        '<tr data-clave="%s">'
        '<td data-label="Nombre completo"><b>%s</b></td>'
        '<td data-label="Correo institucional">%s</td>'
        '<td data-label="Identificación">%s</td>'
        '<td data-label="ID institucional"><span class="sa-tabla-id">%s</span></td>'
        '<td data-label="Rol">%s</td>'
        '<td data-label="Estado">%s</td>'
        '<td data-label="Fecha de creación">%s</td>'
        '<td class="acc" data-label="Acciones">%s</td>'
        '</tr>'
        % (p["clave"], p["nombre"], p["correo"],
           p["identificacion"] or "&mdash;", p["id_institucional"] or "&mdash;",
           p["rol"], _estado_badge(_estado(p)), p["fecha"] or "&mdash;",
           _acciones_perfil(p))
    )


def _toolbar(solo_activos=False):
    roles = '<option value="">Todos los roles</option>' + "".join(
        '<option value="%s">%s</option>' % (r, r) for r in ROLES_ASIGNABLES)
    estados = ('<select class="filtro" id="sa-filtro-estado" data-filtro="off" '
               'aria-label="Filtrar por estado">'
               '<option value="">Todos los estados</option>'
               '<option value="Activo">Activo</option>'
               '<option value="Limitado">Limitado</option>'
               '<option value="Inactivo">Inactivo</option></select>')
    return (
        '<div class="toolbar">'
        '<div class="adm-busca">%s<input type="text" id="sa-buscar" '
        'placeholder="Nombre, correo, identificación o ID institucional" autocomplete="off" '
        'aria-label="Filtrar perfiles"></div>'
        '<select class="filtro" id="sa-filtro-rol" data-filtro="off" '
        'aria-label="Filtrar por rol">%s</select>'
        '%s'
        '<select class="filtro" id="sa-orden" data-filtro="off" '
        'aria-label="Ordenar perfiles">'
        '<option value="nombre">Nombre A-Z</option>'
        '<option value="nombre-desc">Nombre Z-A</option>'
        '<option value="rol">Rol</option>'
        '<option value="estado">Estado</option>'
        '<option value="fecha">Fecha de creación</option>'
        '</select>'
        '<button type="button" class="btn btn-secundario btn-sm" '
        'data-accion="exportar">%s Exportar CSV</button>'
        '<a class="btn btn-primario btn-sm" href="crear-perfil.html">%s Nuevo perfil</a>'
        '</div>'
        % (ico("search", 16), roles,
           "" if solo_activos else estados,
           ico("download", 16), ico("plus", 16))
    )


def _paginacion(total, tam=8):
    n = max(1, (total + tam - 1) // tam)
    botones = (
        '<button type="button" class="btn btn-secundario btn-sm" '
        'data-sa-pagina="prev" disabled>%s Anterior</button>' % ico("izq", 14)
    )
    botones += (
        '<button type="button" class="btn btn-sm btn-acento" '
        'data-sa-pagina="1" aria-current="page">1</button>'
    )
    botones += (
        '<button type="button" class="btn btn-secundario btn-sm" '
        'data-sa-pagina="next"%s>Siguiente %s</button>'
        % (" disabled" if n <= 1 else "", ico("der", 14))
    )
    return (
        '<div class="paginacion" id="sa-paginacion" data-tam="%d">'
        '<span id="sa-contador">Mostrando 1 a %d de %d</span>'
        '<div class="pag">%s</div></div>'
        % (tam, min(tam, total), total, botones)
    )


def _tabla_perfiles(id_vista, perfiles, solo_activos=False):
    filas = "".join(_fila_perfil(p) for p in perfiles)
    h = ('<div class="card tabla-envoltura" id="%s" data-solo-activos="%d">'
         % (id_vista, 1 if solo_activos else 0))
    h += _toolbar(solo_activos)
    h += ('<div class="tabla-scroll"><table class="tabla" id="sa-tabla">'
          '<caption class="visually-hidden">Perfiles registrados en el sistema</caption>'
          '<thead><tr>%s</tr></thead><tbody id="sa-cuerpo">%s</tbody></table></div>'
          % ("".join(th(c) for c in _CABECERAS), filas))
    h += ('<div data-sa-vacio hidden>%s</div>'
          % estado_vacio("Sin resultados",
                         "No hay perfiles que coincidan con la búsqueda o los "
                         "filtros actuales.", "", "search"))
    h += _paginacion(len(perfiles))
    h += "</div>"
    return h


def _resumen():
    return (
        '<div class="sa-resumen">'
        '<span>Perfiles registrados: <b data-sa-count="total">%d</b></span>'
        '<span class="sa-punto" aria-hidden="true"></span>'
        '<span>Activos: <b data-sa-count="activos">%d</b></span>'
        '<span class="sa-punto" aria-hidden="true"></span>'
        '<span>Inactivos: <b data-sa-count="inactivos">%d</b></span>'
        '<span class="sa-punto" aria-hidden="true"></span>'
        '<span>Limitados: <b data-sa-count="limitados">%d</b></span>'
        '</div>'
        % (_total(), _activos(), _inactivos(), _limitados())
    )


def _campo_password(id_input, etiqueta, ayuda, req=False,
                    ph="Mínimo 8 caracteres"):
    """Campo de contraseña con generador al lado (sin backend, todo simulado)."""
    return (
        '<div class="campo"><label for="%s">%s%s</label>'
        '<div class="sa-password">'
        '<input id="%s" name="password" type="password" value="" '
        'placeholder="%s" autocomplete="new-password">'
        '<button type="button" class="btn btn-secundario btn-sm" '
        'data-sa-generar="%s">%s Generar</button>'
        '</div><div class="ayuda">%s%s</div></div>'
        % (id_input, etiqueta, '<span class="req">*</span>' if req else "",
           id_input, ph, id_input, ico("rayo", 14), ico("alerta", 13), ayuda)
    )


def _campo_estado():
    return (
        '<label class="sa-switch" for="sa-edit-activo">'
        '<input type="checkbox" id="sa-edit-activo">'
        '<span class="sa-switch-pista" aria-hidden="true"></span>'
        '<span class="sa-switch-texto"><b>Cuenta activa</b>'
        '<small id="sa-edit-activo-txt">Actívala para permitir el acceso.</small>'
        '</span></label>'
    )


# --- Panel principal ----------------------------------------------------------
def _acceso(icono, titulo, texto, href):
    return (
        '<a class="sa-acceso" href="%s">'
        '<span class="sa-acceso-ico">%s</span>'
        '<div><b>%s</b><span>%s</span></div>'
        '<span class="sa-acceso-flecha" aria-hidden="true">%s</span></a>'
        % (href, ico(icono, 18), titulo, texto, ico("der", 16))
    )


def _distribucion():
    h = '<dl class="lista-def">'
    for rol in ROLES_ORDEN:
        h += (
            '<div class="def-row" data-sa-rol="%s">'
            '<dt>%s</dt>'
            '<dd>Total: <span data-campo="total">%d</span> &middot; '
            'activos: <span data-campo="activos">%d</span> &middot; '
            'limitados: <span data-campo="limitados">%d</span> &middot; '
            'inactivos: <span data-campo="inactivos">%d</span></dd>'
            '</div>'
            % (rol, rol, _total(rol), _activos(rol), _limitados(rol),
               _inactivos(rol))
        )
    return h + "</dl>"


def dashboard():
    total = _total()
    activos = _activos()
    inactivos = _inactivos()
    limitados = _limitados()
    pct = lambda n: int(round(n * 100.0 / max(1, total)))
    cuerpo = metricas_enlace([
        ("users", "Perfiles registrados", str(total), "", 100, None,
         "perfiles.html", "Todos los perfiles",
         "%d cuentas registradas: estudiantes, docentes y administradores." % total),
        ("check", "Perfiles activos", str(activos), "", pct(activos), None,
         "perfiles-activos.html", "Perfiles activos",
         "%d cuentas con acceso y todos sus permisos activos." % activos),
        ("lock", "Perfiles inactivos", str(inactivos), "", pct(inactivos), None,
         "perfiles.html?estado=Inactivo", "Perfiles inactivos",
         "%d cuentas bloqueadas que no pueden iniciar sesión." % inactivos),
        ("alerta", "Perfiles limitados", str(limitados), "", pct(limitados), None,
         "perfiles.html?estado=Limitado", "Perfiles limitados",
         "%d cuentas con permisos incompletos." % limitados),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card(
        "Accesos del módulo",
        _acceso("plus", "Crear perfil",
                "Alta guiada en tres fases: datos, rol y permisos.",
                "crear-perfil.html")
        + _acceso("users", "Gestión de perfiles",
                  "Consulta, edición, permisos y estado de las cuentas.",
                  "perfiles.html")
        + _acceso("check", "Perfiles activos",
                  "Solo las cuentas que hoy pueden iniciar sesión.",
                  "perfiles-activos.html"),
        hint="Solo perfiles y accesos",
    )
    cuerpo += card("Distribución por rol", _distribucion(),
                   hint="Datos existentes del prototipo")
    cuerpo += "</div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += callout(
        "El Super Admin <b>no</b> gestiona emprendimientos, asesorías, eventos, "
        "tareas ni diagnósticos. Tampoco modifica información académica ni "
        "puede crear otro Super Admin.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += card("Reglas de integridad del módulo", lista_def([
        ("Roles asignables", "Estudiante, Docente y Administrador."),
        ("Eliminación", "No existe: nada se borra. El acceso se controla con el "
                        "estado Activo/Inactivo."),
        ("Permisos", "Si faltan permisos del rol, el perfil queda como Limitado."),
        ("Datos", "Identificación personal e ID institucional; correo @uniminuto.edu.co."),
    ]))
    return shell(R, "dashboard", "Panel principal", cuerpo,
                 migas=["Inicio", "Panel principal"],
                 sub="Gestión de perfiles y accesos del sistema SGEMD.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 2: creación de perfiles -------------------------------------------
def crear_perfil():
    cuerpo = callout(
        "La <b>identificación</b> es el documento personal y el <b>ID "
        "institucional</b> es el código que asigna la universidad. Ambos son "
        "obligatorios, igual que el correo <b>@uniminuto.edu.co</b>. Solo se "
        "pueden crear perfiles de Estudiante, Docente o Administrador.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div id="sa-steps">%s</div>' % steps(
        ["Información básica", "Rol", "Permisos"], 0)
    cuerpo += '<div id="sa-form-crear">'

    cuerpo += '<div class="sa-paso" data-paso="1">'
    cuerpo += card(
        "Fase 1 · Información básica",
        '<div class="grid g-2">'
        + campo("Nombre completo", req=True, ph="Ej. Mariana López",
                name="nombre")
        + campo("Identificación personal", req=True, ph="Ej. 1020304050",
                name="identificacion",
                ayuda="Documento de identidad de la persona.")
        + "</div>"
        + '<div class="grid g-2">'
        + campo("ID institucional", req=True, ph="Ej. 912646 o DOC-015",
                name="id_institucional",
                ayuda="Código que la universidad asigna a estudiantes, docentes "
                      "y administradores.")
        + campo("Correo institucional", tipo="email", req=True,
                ph="nombre.apellido@uniminuto.edu.co", name="correo",
                ayuda="Debe terminar en @uniminuto.edu.co. El correo y los "
                      "identificadores no pueden repetirse.")
        + "</div>"
        + _campo_password(
            "sa-password-crear", "Contraseña provisional",
            "La persona deberá cambiarla en su primer inicio de sesión. "
            "Usa Generar para proponer una contraseña segura.", req=True)
        + '<p class="modal-aviso">La contraseña se guarda solo en este navegador '
          'porque el prototipo no tiene backend.</p>'
    )
    cuerpo += "</div>"

    cuerpo += '<div class="sa-paso" data-paso="2" hidden>'
    cuerpo += card(
        "Fase 2 · Rol del perfil",
        '<p class="sa-nota">Selecciona el rol que tendrá la cuenta. Los '
        'permisos de la siguiente fase se cargan según esta elección.</p>'
        + '<div class="radio-grupo">'
        + '<label class="radio-card" for="sa-rol-est"><input type="radio" '
          'name="rol" id="sa-rol-est" value="Estudiante">'
          '<div><strong>Estudiante</strong><small>Accede a su emprendimiento, '
          'diagnóstico, plan de trabajo, tareas, asesorías y eventos.</small></div></label>'
        + '<label class="radio-card" for="sa-rol-doc"><input type="radio" '
          'name="rol" id="sa-rol-doc" value="Docente">'
          '<div><strong>Docente</strong><small>Acompaña emprendimientos '
          'asignados, registra asesorías y revisa tareas y diagnósticos.</small></div></label>'
        + '<label class="radio-card" for="sa-rol-adm"><input type="radio" '
          'name="rol" id="sa-rol-adm" value="Administrador">'
          '<div><strong>Administrador</strong><small>Gestiona perfiles, '
          'asignaciones, emprendimientos, eventos, reportes y respaldos.</small></div></label>'
        + "</div>"
        + '<div class="campo-error" id="sa-error-rol" role="alert" hidden></div>'
    )
    cuerpo += "</div>"

    cuerpo += '<div class="sa-paso" data-paso="3" hidden>'
    cuerpo += card(
        "Fase 3 · Configuración de permisos",
        '<p class="sa-nota">Estos son los permisos que existen para el rol '
        'seleccionado. Arrancan con la configuración predeterminada del rol y '
        'puedes ajustarlos antes de crear el perfil. Si retiras alguno, el '
        'perfil quedará como <b>Limitado</b>.</p>'
        '<div id="sa-permisos-crear">'
        + estado_vacio("Selecciona un rol",
                       "Vuelve a la fase 2 para elegir el rol del perfil.",
                       "", "user")
        + "</div>"
        '<p class="modal-aviso">El permiso de Inicio es base del rol y no se '
        'puede retirar. No se pueden asignar permisos de otro rol.</p>'
    )
    cuerpo += "</div>"

    cuerpo += (
        '<div class="sa-pasos-pie">'
        '<a class="btn btn-secundario" href="perfiles.html">Cancelar</a>'
        '<div class="fila-fin">'
        '<button type="button" class="btn btn-secundario" id="sa-atras" hidden>Atrás</button>'
        '<button type="button" class="btn btn-primario" id="sa-continuar">Continuar</button>'
        '<button type="button" class="btn btn-primario" id="sa-crear" hidden>Crear perfil</button>'
        '</div></div>'
    )
    cuerpo += "</div>"

    cuerpo += '<div id="sa-exito" hidden>'
    cuerpo += card(
        "Perfil creado",
        '<div class="sa-exito">'
        '<span class="sa-exito-ico">%s</span>'
        '<h3 id="sa-exito-nombre">Perfil</h3>'
        '<p>El perfil quedó registrado como <b id="sa-exito-rol">—</b> y ya '
        'aparece en la gestión de perfiles. La persona deberá cambiar su '
        'contraseña provisional en el primer inicio de sesión.</p>'
        '<dl class="lista-def">'
        '<div class="def-row"><dt>Correo institucional</dt>'
        '<dd id="sa-exito-correo">—</dd></div>'
        '<div class="def-row"><dt>Identificación personal</dt>'
        '<dd id="sa-exito-identificacion">—</dd></div>'
        '<div class="def-row"><dt>ID institucional</dt>'
        '<dd id="sa-exito-id">—</dd></div>'
        '<div class="def-row"><dt>Contraseña provisional</dt>'
        '<dd><code class="sa-code" id="sa-exito-password">—</code></dd></div>'
        '<div class="def-row"><dt>Permisos</dt>'
        '<dd id="sa-exito-permisos">—</dd></div>'
        '</dl>'
        '<div class="fila-fin" style="margin-top:18px">'
        '<button type="button" class="btn btn-secundario" id="sa-otro">Crear otro perfil</button>'
        '<a class="btn btn-primario" href="perfiles.html">Ver gestión de perfiles</a>'
        '<a class="btn btn-secundario" href="perfiles-activos.html">Ver perfiles activos</a>'
        '</div></div>'
        % ico("check", 26)
    )
    cuerpo += "</div>"

    cuerpo = formulario("crear-perfil", cuerpo)
    return shell(R, "crear-perfil", "Crear perfil", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Crear perfil"],
                 sub="Alta de un perfil en tres fases: información, rol y permisos.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 3: gestión de perfiles --------------------------------------------
def perfiles():
    cuerpo = callout(
        "Los perfiles <b>no se eliminan</b>. Para retirar el acceso, abre "
        "<b>Editar perfil</b> y desactiva la cuenta; para ajustar sus permisos, "
        "usa <b>Gestión de permisos</b>. Un perfil con permisos incompletos se "
        "muestra como <b>Limitado</b>.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _resumen()
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_perfiles("sa-perfiles-vista", PERFILES)
    cuerpo = formulario("perfiles", cuerpo)
    return shell(R, "perfiles", "Gestión de perfiles", cuerpo,
                 migas=["Inicio", "Gestión de perfiles"],
                 sub="Consulta y administración de los perfiles registrados: "
                     "datos, permisos y estado.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 4: perfiles activos -----------------------------------------------
def perfiles_activos():
    activos = [p for p in PERFILES if _estado(p) == "Activo"]
    cuerpo = callout(
        "Esta vista muestra únicamente perfiles <b>Activos</b>: cuentan con "
        "acceso habilitado y todos los permisos de su rol. Los perfiles "
        "limitados o inactivos se gestionan desde la vista general.", "check")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _resumen()
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_perfiles("sa-perfiles-activos-vista", activos, solo_activos=True)
    cuerpo = formulario("perfiles-activos", cuerpo)
    return shell(R, "perfiles-activos", "Perfiles activos", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Perfiles activos"],
                 sub="Cuentas que actualmente pueden iniciar sesión en el sistema.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 5: edición de un perfil -------------------------------------------
def editar_perfil():
    cuerpo = '<div id="sa-editar-vacio" hidden>%s</div>' % estado_vacio(
        "Perfil no encontrado",
        "No hay un perfil asociado a este enlace. Vuelve a la gestión de "
        "perfiles y elige Editar perfil.",
        '<a class="btn btn-primario" href="perfiles.html">Volver a la gestión</a>',
        "user")
    cuerpo += '<div id="sa-editar-contenido" hidden>'
    cuerpo += callout(
        "Los cambios se guardan en este navegador. El perfil no se elimina: "
        "para retirar el acceso, desactiva la cuenta desde el estado.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Datos del perfil",
        '<div class="grid g-2">'
        + campo("Nombre completo", req=True, name="nombre",
                ph="Nombre y apellidos")
        + campo("Identificación personal", name="identificacion",
                ph="Documento de identidad",
                ayuda="Obligatoria al crear el perfil. En registros antiguos "
                      "puede aparecer sin diligenciar.")
        + "</div>"
        + '<div class="grid g-2">'
        + campo("ID institucional", name="id_institucional",
                ph="Código asignado por la universidad",
                ayuda="Identificador institucional de estudiante, docente o "
                      "administrador.")
        + '<div class="campo"><label>Rol</label>'
          '<div class="sa-readonly" id="sa-edit-rol">—</div>'
          '<div class="ayuda">El rol no se puede cambiar desde esta vista.</div></div>'
        + "</div>"
        + campo("Correo institucional", tipo="email", req=True, name="correo",
                ph="nombre.apellido@uniminuto.edu.co",
                ayuda="Dominio obligatorio: @uniminuto.edu.co.")
    )
    cuerpo += card(
        "Estado de la cuenta",
        _campo_estado()
        + '<div class="sa-estado-fila"><span id="sa-edit-estado-badge"></span>'
          '<span class="sa-mini">Así se verá el perfil en los listados.</span></div>'
        + '<p class="modal-aviso">Al desactivar la cuenta, la persona deja de '
          'aparecer en Perfiles activos y no puede iniciar sesión. Sus datos y '
          'permisos se conservan.</p>'
    )
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Contraseña",
        _campo_password(
            "sa-edit-password", "Nueva contraseña",
            "Déjala vacía para conservar la contraseña actual. Si la persona "
            "no puede cambiarla, el administrador puede asignar una nueva.")
        + '<p class="sa-nota" id="sa-edit-password-estado"></p>'
    )
    cuerpo += card(
        "Permisos",
        '<div class="sa-perm-resumen"><span id="sa-edit-perm-badge"></span>'
        '<span class="sa-mini" id="sa-edit-perm-resumen">—</span></div>'
        '<a class="btn btn-secundario btn-sm" id="sa-edit-perm-link" '
        'href="permisos.html">%s Gestionar permisos</a>'
        '<p class="modal-aviso">Si se retiran permisos del rol, el perfil pasa '
        'automáticamente a <b>Limitado</b>.</p>' % ico("sliders", 16)
    )
    cuerpo += "</div></div>"
    cuerpo += (
        '<div class="sa-pasos-pie">'
        '<a class="btn btn-secundario" href="perfiles.html">Volver a la gestión</a>'
        '<div class="fila-fin">'
        '<a class="btn btn-secundario" id="sa-edit-permisos" href="permisos.html">'
        + ico("sliders", 16) + ' Permisos</a>'
        '<button type="button" class="btn btn-primario" id="sa-edit-guardar">'
        + ico("check", 16) + ' Guardar cambios</button>'
        '</div></div>'
    )
    cuerpo += "</div>"
    cuerpo = formulario("editar-perfil", cuerpo)
    return shell(R, "editar-perfil", "Editar perfil", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Editar perfil"],
                 sub="Datos, estado y contraseña del perfil seleccionado.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 6: gestión de permisos --------------------------------------------
def permisos():
    cuerpo = '<div id="sa-permisos-vacio" hidden>%s</div>' % estado_vacio(
        "Perfil no encontrado",
        "No hay un perfil asociado a este enlace. Vuelve a la gestión de "
        "perfiles y elige Gestión de permisos.",
        '<a class="btn btn-primario" href="perfiles.html">Volver a la gestión</a>',
        "user")
    cuerpo += '<div id="sa-permisos-contenido" hidden>'
    cuerpo += callout(
        "Los permisos se toman de las vistas reales de cada rol. El permiso de "
        "<b>Inicio</b> es la base de la cuenta y no se puede retirar. Si falta "
        "algún permiso del rol, el perfil queda como <b>Limitado</b>.", "sliders")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Perfil",
        '<dl class="lista-def" id="sa-perm-ficha"></dl>'
    )
    cuerpo += card(
        "Permisos por módulo",
        '<div id="sa-perm-caja"></div>'
        '<p class="modal-aviso">Solo se muestran los permisos que existen para '
        'este rol. No se pueden asignar permisos de otro rol.</p>'
    )
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Estado del perfil",
        '<div class="sa-perm-resumen"><span id="sa-perm-estado"></span>'
        '<span class="sa-mini" id="sa-perm-resumen">—</span></div>'
        '<p class="modal-aviso">El estado se calcula automáticamente: si la '
        'cuenta está activa y conserva todos los permisos del rol es '
        '<b>Activo</b>; si le falta alguno es <b>Limitado</b>; si fue '
        'desactivada es <b>Inactivo</b>.</p>'
    )
    cuerpo += card(
        "Acciones",
        '<div class="fila-col">'
        '<button type="button" class="btn btn-secundario" id="sa-perm-restablecer">'
        + ico("sliders", 16) + ' Restablecer permisos del rol</button>'
        '<button type="button" class="btn btn-primario" id="sa-perm-guardar">'
        + ico("check", 16) + ' Guardar permisos</button>'
        '</div>'
    )
    cuerpo += "</div></div>"
    cuerpo += (
        '<div class="sa-pasos-pie">'
        '<a class="btn btn-secundario" href="perfiles.html">Volver a la gestión</a>'
        '<div class="fila-fin">'
        '<a class="btn btn-secundario" id="sa-perm-link-editar" href="editar-perfil.html">'
        + ico("edit", 16) + ' Editar datos</a>'
        '</div></div>'
    )
    cuerpo += "</div>"
    cuerpo = formulario("permisos", cuerpo)
    return shell(R, "permisos", "Gestión de permisos", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Gestión de permisos"],
                 sub="Activa o retira los permisos que existen para el rol del perfil.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- Vista 7: perfil del propio Super Admin ----------------------------------
def mi_perfil():
    cuerpo = callout(
        "Esta es tu cuenta de Super Admin. Puedes actualizar tus datos y tu "
        "contraseña sin salir del módulo. El rol Super Admin no se puede "
        "cambiar y esta cuenta no aparece en la gestión de perfiles.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Datos personales",
        '<div class="grid g-2">'
        + campo("Nombre completo", req=True, name="nombre",
                ph="Nombre y apellidos")
        + campo("Identificación personal", req=True, name="identificacion",
                ph="Documento de identidad")
        + "</div>"
        + '<div class="grid g-2">'
        + campo("ID institucional", req=True, name="id_institucional",
                ph="Código asignado por la universidad")
        + '<div class="campo"><label>Rol</label>'
          '<div class="sa-readonly">Super Admin</div>'
          '<div class="ayuda">Rol fijo de la cuenta de administración.</div></div>'
        + "</div>"
        + campo("Correo institucional", tipo="email", req=True, name="correo",
                ph="nombre.apellido@uniminuto.edu.co",
                ayuda="Dominio obligatorio: @uniminuto.edu.co.")
    )
    cuerpo += card(
        "Cuenta institucional",
        '<div class="grid g-2">'
        + campo("Cargo", name="cargo", ph="Cargo en la institución")
        + campo("Teléfono", tipo="tel", name="telefono", ph="+57 ...")
        + "</div>"
        + lista_def([
            ("Rol", "Super Admin"),
            ("Fecha de creación", CUENTA_SA["fecha"]),
            ("Alcance", "Gestión de perfiles y accesos"),
        ])
    )
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card(
        "Acciones",
        '<div class="fila-col">'
        '<button type="button" class="btn btn-primario" id="sa-mi-guardar">'
        + ico("check", 16) + ' Guardar cambios</button>'
        '<a class="btn btn-secundario" href="dashboard.html">Volver al panel</a>'
        '</div>'
    )
    cuerpo += "</div></div>"
    cuerpo = formulario("mi-perfil", cuerpo)
    return shell(R, "mi-perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Tus datos como Super Admin.",
                 extra_head=ADMIN_CSS + SA_CSS)


# --- CSS propio del módulo ----------------------------------------------------
# Reutiliza los tokens y los componentes de lib_css. Solo agrega piezas de
# presentación propias del módulo (resumen, accesos, permisos, interruptor y
# campo de contraseña con generador).
SA_CSS = """
.sa-resumen{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  padding:14px 18px;border:1px solid var(--gris);border-radius:var(--r-sm);
  background:var(--blanco);font-size:13px;color:var(--tinta-2)}
.sa-resumen b{font-size:18px;color:var(--tinta);margin-right:4px}
.sa-punto{width:4px;height:4px;border-radius:999px;background:var(--gris)}
.sa-acceso{display:flex;align-items:center;gap:14px;padding:14px 0;
  border-bottom:1px solid var(--gris);color:var(--tinta);text-decoration:none}
.sa-acceso:last-child{border-bottom:0}
.sa-acceso:hover b{color:var(--azul-real)}
.sa-acceso-ico{flex:0 0 42px;width:42px;height:42px;border-radius:999px;
  display:flex;align-items:center;justify-content:center;
  background:var(--azul-06);color:var(--azul-real)}
.sa-acceso div{flex:1;min-width:0}
.sa-acceso b{display:block;font-size:14px}
.sa-acceso span{display:block;font-size:13px;color:var(--tinta-2);margin-top:2px}
.sa-acceso-flecha{flex:0 0 auto;color:var(--azul-real)}
.sa-paso>.card{margin:0}
.sa-pasos-pie,.fila-fin{display:flex;align-items:center;justify-content:flex-end;
  gap:10px;flex-wrap:wrap}
.sa-pasos-pie{justify-content:space-between;margin-top:20px}
.sa-nota{font-size:13px;color:var(--tinta-2);line-height:1.6;margin-bottom:14px}
.sa-perms{display:grid;gap:12px}
.sa-perm-mod{border:1px solid var(--gris);border-radius:var(--r-sm);
  padding:12px 14px;margin:0;background:var(--blanco)}
.sa-perm-mod legend{font-size:13px;font-weight:700;color:var(--tinta);padding:0 6px}
.sa-perm{display:flex;align-items:flex-start;gap:8px;font-size:13px;
  color:var(--tinta-2);padding:4px 0;cursor:pointer}
.sa-perm input{accent-color:var(--azul-real);margin-top:2px}
.sa-perm-titulo{font-size:14px;font-weight:700;color:var(--tinta);margin:18px 0 10px}
.sa-subt{font-size:13px;font-weight:700;color:var(--tinta);margin:16px 0 6px;
  letter-spacing:.06em;text-transform:uppercase}
.sa-exito{text-align:left}
.sa-exito h3{font-size:20px;margin:0 0 6px}
.sa-exito p{font-size:14px;color:var(--tinta-2);line-height:1.6;margin-bottom:12px}
.sa-exito-ico{display:inline-flex;align-items:center;justify-content:center;
  width:54px;height:54px;border-radius:999px;background:var(--amarillo);
  color:var(--tinta);margin-bottom:12px}
.sa-readonly{display:flex;align-items:center;min-height:40px;padding:8px 12px;
  border:1px solid var(--gris);border-radius:var(--r-sm);
  background:var(--noche-03);font-size:14px;color:var(--tinta);font-weight:600}
.sa-password{display:flex;gap:8px;align-items:stretch}
.sa-password input{flex:1;min-width:0}
.sa-password .btn{white-space:nowrap;align-self:stretch}
.sa-code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
  background:var(--noche-03);border:1px solid var(--gris);border-radius:6px;
  padding:2px 8px;color:var(--tinta);font-size:13px}
.sa-tabla-id{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
  font-size:13px;color:var(--tinta)}
a.table-act{text-decoration:none}
.sa-switch{position:relative;display:flex;align-items:center;gap:12px;
  padding:12px 14px;border:1px solid var(--gris);border-radius:var(--r-sm);
  background:var(--blanco);cursor:pointer;margin-bottom:12px}
.sa-switch input{position:absolute;opacity:0;width:1px;height:1px}
.sa-switch-pista{position:relative;flex:0 0 44px;width:44px;height:24px;
  border-radius:999px;background:var(--gris);transition:background .18s}
.sa-switch-pista::after{content:"";position:absolute;top:3px;left:3px;
  width:18px;height:18px;border-radius:999px;background:var(--blanco);
  transition:transform .18s}
.sa-switch input:checked + .sa-switch-pista{background:var(--azul-real)}
.sa-switch input:checked + .sa-switch-pista::after{transform:translateX(20px)}
.sa-switch input:focus-visible + .sa-switch-pista{box-shadow:0 0 0 3px var(--azul-12)}
.sa-switch-texto b{display:block;font-size:14px;color:var(--tinta)}
.sa-switch-texto small{display:block;font-size:13px;color:var(--tinta-2)}
.sa-estado-fila,.sa-perm-resumen{display:flex;align-items:center;gap:10px;
  flex-wrap:wrap;margin:10px 0 0}
.sa-mini{font-size:13px;color:var(--tinta-2)}
@media (max-width:767px){
  .sa-resumen{gap:8px}
  .sa-pasos-pie{flex-direction:column;align-items:stretch}
  .sa-pasos-pie .fila-fin{justify-content:stretch}
  .sa-pasos-pie .btn{width:100%}
  .sa-password{flex-direction:column}
  .sa-password .btn{width:100%}
}
"""


# --- Script propio del módulo -------------------------------------------------
# No toca lib_js: filtra su propia tabla (sin .buscador ni data-filtro activos),
# guarda el estado del prototipo en localStorage y reutiliza el marcado de
# modal/toast que ya define el kit compartido.
SA_JS = r"""
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };
  function esc(t) {
    return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function norm(t) {
    return String(t || "").toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim();
  }
  function param(nombre) {
    var m = new RegExp("[?&]" + nombre + "=([^&]*)").exec(location.search || "");
    return m ? decodeURIComponent(m[1].replace(/\+/g, " ")) : "";
  }

  /* Autorizacion simulada: si hay una sesion iniciada con otro rol, este
     modulo no se abre. Sin sesion se permite la revision directa del
     prototipo desde index.html. */
  try {
    var ses = JSON.parse(localStorage.getItem("sgemd:sesion") || "null");
    if (ses && ses.rol && ses.rol !== "Super Admin") {
      location.replace("../compartido/login.html");
      return;
    }
  } catch (x) {}

  var KEY = "sgemd:superadmin:v1";
  var CUENTA_KEY = "sgemd:superadmin:cuenta";
  var BASE = window.SA_PERFILES || [];
  var PERMISOS = window.SA_PERMISOS || {};
  var ICO = window.SA_ICO || {};
  var HOY = window.SA_HOY || "";
  var CUENTA_DEF = window.SA_CUENTA_DEF || {};
  var ROLES = ["Estudiante", "Docente", "Administrador"];
  var VISTA = null;

  function clonar(o) { return JSON.parse(JSON.stringify(o)); }

  function estado() {
    var st = null;
    try { st = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (x) {}
    if (!st || typeof st !== "object") st = {};
    if (!Array.isArray(st.creados)) st.creados = [];
    if (!st.cambios || typeof st.cambios !== "object") st.cambios = {};
    /* La version anterior guardaba bajas logicas. Ya no se elimina nada: si
       existe la coleccion se ignora y se retira del almacen. */
    if (st.bajas) delete st.bajas;
    return st;
  }
  function persistir(st) {
    try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (x) {}
  }
  function lista() {
    var st = estado();
    var out = [];
    function sumar(p) {
      var c = clonar(p);
      var cam = st.cambios[p.clave];
      if (cam) {
        for (var k in cam) {
          if (Object.prototype.hasOwnProperty.call(cam, k)) c[k] = cam[k];
        }
      }
      c.clave = p.clave;
      out.push(c);
    }
    BASE.forEach(sumar);
    st.creados.forEach(sumar);
    return out;
  }
  function buscar(clave) {
    var all = lista();
    for (var i = 0; i < all.length; i++) {
      if (all[i].clave === clave) return all[i];
    }
    return null;
  }
  function guardarCambio(clave, cambio) {
    var st = estado();
    var prev = st.cambios[clave] || {};
    for (var k in cambio) {
      if (Object.prototype.hasOwnProperty.call(cambio, k)) prev[k] = cambio[k];
    }
    st.cambios[clave] = prev;
    persistir(st);
  }
  function crearPerfil(p) {
    var st = estado();
    st.creados.push(p);
    persistir(st);
  }

  /* --- cuenta propia del Super Admin ------------------------------------ */
  function cuentaActual() {
    var c = null;
    try { c = JSON.parse(localStorage.getItem(CUENTA_KEY) || "null"); } catch (x) {}
    if (!c || typeof c !== "object") c = {};
    for (var k in CUENTA_DEF) {
      if (Object.prototype.hasOwnProperty.call(CUENTA_DEF, k) && !c[k]) {
        c[k] = CUENTA_DEF[k];
      }
    }
    return c;
  }
  function guardarCuenta(c) {
    try { localStorage.setItem(CUENTA_KEY, JSON.stringify(c)); } catch (x) {}
  }
  function iniciales(nombre) {
    var partes = String(nombre || "").trim().split(/\s+/).filter(Boolean);
    if (!partes.length) return "SA";
    var a = partes[0].charAt(0);
    var b = partes.length > 1 ? partes[partes.length - 1].charAt(0) : "";
    return (a + b).toUpperCase();
  }
  function syncCuenta() {
    var c = cuentaActual();
    var nom = $(".who-name");
    var av = $(".who .avatar");
    if (nom) nom.textContent = c.nombre;
    if (av) av.textContent = iniciales(c.nombre);
  }

  /* --- estado derivado y permisos ---------------------------------------- */
  function permisosDefecto(rol) {
    var mods = PERMISOS[rol] || [];
    var out = [];
    mods.forEach(function (m) {
      m.items.forEach(function (it) { out.push(m.modulo + "::" + it); });
    });
    return out;
  }
  function permisosActivos(p) {
    var def = permisosDefecto(p.rol);
    var sel = p.permisos || [];
    return def.filter(function (c) { return sel.indexOf(c) >= 0; }).length;
  }
  function permisosCompletos(p) {
    var def = permisosDefecto(p.rol);
    var sel = p.permisos || [];
    for (var i = 0; i < def.length; i++) {
      if (sel.indexOf(def[i]) < 0) return false;
    }
    return true;
  }
  function estadoReal(p) {
    if (p.estado === "Inactivo") return "Inactivo";
    return permisosCompletos(p) ? "Activo" : "Limitado";
  }
  function permisosHTML(rol, seleccionados) {
    var mods = PERMISOS[rol] || [];
    var sel = seleccionados || [];
    var h = '<div class="sa-perms">';
    mods.forEach(function (m) {
      h += '<fieldset class="sa-perm-mod"><legend>' + esc(m.modulo) + "</legend>";
      m.items.forEach(function (it) {
        var clave = m.modulo + "::" + it;
        var base = norm(it) === "inicio";
        var on = base || sel.indexOf(clave) >= 0;
        h += '<label class="sa-perm"><input type="checkbox" data-perm="' +
          esc(clave) + '"' + (on ? " checked" : "") + (base ? " disabled" : "") +
          "> <span>" + esc(it) + "</span></label>";
      });
      h += "</fieldset>";
    });
    return h + "</div>";
  }
  function getPermisos(raiz) {
    var out = [];
    $$("[data-perm]", raiz).forEach(function (c) {
      if (c.checked) out.push(c.getAttribute("data-perm"));
    });
    return out;
  }
  function permisosTexto(p) {
    var mods = PERMISOS[p.rol] || [];
    var sel = p.permisos || [];
    var partes = [];
    mods.forEach(function (m) {
      var items = m.items.filter(function (it) {
        return sel.indexOf(m.modulo + "::" + it) >= 0;
      });
      if (items.length) partes.push("<b>" + esc(m.modulo) + ":</b> " + esc(items.join(", ")));
    });
    return partes.length ? partes.join("<br>") : "Sin permisos configurados.";
  }

  /* --- contrasena provisional -------------------------------------------- */
  function azar(n) {
    if (window.crypto && window.crypto.getRandomValues) {
      var a = new Uint32Array(1);
      window.crypto.getRandomValues(a);
      return a[0] % n;
    }
    return Math.floor(Math.random() * n);
  }
  function generarClave() {
    var may = "ABCDEFGHJKLMNPQRSTUVWXYZ";
    var min = "abcdefghijkmnopqrstuvwxyz";
    var num = "23456789";
    var sim = "!@#$%&*";
    var todos = may + min + num + sim;
    var out = [may, min, num, sim].map(function (grupo) {
      return grupo.charAt(azar(grupo.length));
    });
    while (out.length < 12) out.push(todos.charAt(azar(todos.length)));
    for (var i = out.length - 1; i > 0; i--) {
      var j = azar(i + 1);
      var t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return out.join("");
  }

  /* --- marcado de filas -------------------------------------------------- */
  function badgeHTML(est) {
    var tipo = est === "Activo" ? "b-azul" : (est === "Limitado" ? "b-amarillo" : "b-neutra");
    var ic = est === "Activo" ? "check12" : (est === "Limitado" ? "alerta12" : "lock12");
    return '<span class="badge ' + tipo + '">' + (ICO[ic] || "") + " " + esc(est) + "</span>";
  }
  function accHTML(p) {
    var c = encodeURIComponent(p.clave), n = esc(p.nombre);
    function boton(acc, ic, eti, aria) {
      return '<button type="button" class="table-act" data-sa-accion="' + acc +
        '" data-clave="' + esc(p.clave) + '" title="' + eti + '" aria-label="' + aria + '">' +
        (ICO[ic] || "") + "</button>";
    }
    return boton("ver", "eye", "Ver detalle", "Ver detalle de " + n) +
      '<a class="table-act" href="editar-perfil.html?clave=' + c +
      '" title="Editar perfil" aria-label="Editar el perfil de ' + n + '">' +
      (ICO.edit || "") + "</a>" +
      '<a class="table-act" href="permisos.html?clave=' + c +
      '" title="Gestionar permisos" aria-label="Gestionar permisos de ' + n + '">' +
      (ICO.sliders || "") + "</a>";
  }
  function filaHTML(p) {
    return '<tr data-clave="' + esc(p.clave) + '">' +
      '<td data-label="Nombre completo"><b>' + esc(p.nombre) + "</b></td>" +
      '<td data-label="Correo institucional">' + esc(p.correo) + "</td>" +
      '<td data-label="Identificación">' + esc(p.identificacion || "—") + "</td>" +
      '<td data-label="ID institucional"><span class="sa-tabla-id">' +
      esc(p.id_institucional || "—") + "</span></td>" +
      '<td data-label="Rol">' + esc(p.rol) + "</td>" +
      '<td data-label="Estado">' + badgeHTML(estadoReal(p)) + "</td>" +
      '<td data-label="Fecha de creación">' + esc(p.fecha || "—") + "</td>" +
      '<td class="acc" data-label="Acciones">' + accHTML(p) + "</td>" +
      "</tr>";
  }

  /* --- fechas ------------------------------------------------------------ */
  var MESES = { ene: 1, feb: 2, mar: 3, abr: 4, may: 5, jun: 6,
    jul: 7, ago: 8, sep: 9, oct: 10, nov: 11, dic: 12 };
  function fechaNum(txt) {
    var m = String(txt || "").toLowerCase().match(/^(\d{1,2})\s+([a-z]{3})\s+(\d{4})$/);
    if (!m) return 0;
    return parseInt(m[3], 10) * 10000 + (MESES[m[2]] || 0) * 100 + parseInt(m[1], 10);
  }

  /* --- tabla ------------------------------------------------------------- */
  function contar() {
    var all = lista();
    var c = { total: all.length, activos: 0, inactivos: 0, limitados: 0 };
    all.forEach(function (p) {
      var e = estadoReal(p);
      if (e === "Activo") c.activos++;
      else if (e === "Inactivo") c.inactivos++;
      else if (e === "Limitado") c.limitados++;
    });
    $$("[data-sa-count]").forEach(function (el) {
      var k = el.getAttribute("data-sa-count");
      if (c[k] !== undefined) el.textContent = String(c[k]);
    });
    $$(".metrica").forEach(function (m) {
      var lbl = $(".metrica-lbl", m);
      var val = $(".metrica-val", m);
      if (!lbl || !val) return;
      var mapa = {
        "perfiles registrados": "total",
        "perfiles activos": "activos",
        "perfiles inactivos": "inactivos",
        "perfiles limitados": "limitados"
      };
      var k = mapa[norm(lbl.textContent)];
      if (k !== undefined && val.firstChild) val.firstChild.nodeValue = String(c[k]);
    });
    $$("[data-sa-rol]").forEach(function (row) {
      var rol = row.getAttribute("data-sa-rol");
      var propios = all.filter(function (p) { return p.rol === rol; });
      var act = propios.filter(function (p) { return estadoReal(p) === "Activo"; }).length;
      var ina = propios.filter(function (p) { return estadoReal(p) === "Inactivo"; }).length;
      var lim = propios.filter(function (p) { return estadoReal(p) === "Limitado"; }).length;
      var t = $('[data-campo="total"]', row);
      var a = $('[data-campo="activos"]', row);
      var i = $('[data-campo="inactivos"]', row);
      var l = $('[data-campo="limitados"]', row);
      if (t) t.textContent = String(propios.length);
      if (a) a.textContent = String(act);
      if (i) i.textContent = String(ina);
      if (l) l.textContent = String(lim);
    });
  }

  function comparar(a, b, orden) {
    if (orden === "fecha") {
      var fa = fechaNum(a.fecha), fb = fechaNum(b.fecha);
      if (!fa && !fb) return 0;
      if (!fa) return 1;
      if (!fb) return -1;
      return fb - fa;
    }
    if (orden === "nombre-desc") return norm(b.nombre).localeCompare(norm(a.nombre));
    if (orden === "rol") return norm(a.rol).localeCompare(norm(b.rol)) ||
      norm(a.nombre).localeCompare(norm(b.nombre));
    if (orden === "estado") return norm(estadoReal(a)).localeCompare(norm(estadoReal(b))) ||
      norm(a.nombre).localeCompare(norm(b.nombre));
    return norm(a.nombre).localeCompare(norm(b.nombre));
  }

  function pagHTML(nPag, actual, desde, hasta, total) {
    var h = '<span id="sa-contador">Mostrando ' + desde + " a " + hasta +
      " de " + total + "</span><div class=\"pag\">";
    h += '<button type="button" class="btn btn-secundario btn-sm" data-sa-pagina="prev"' +
      (actual <= 1 ? " disabled" : "") + ">" + (ICO.izq || "") + " Anterior</button>";
    for (var n = 1; n <= nPag; n++) {
      h += '<button type="button" class="btn btn-sm ' +
        (n === actual ? "btn-acento" : "btn-secundario") + '" data-sa-pagina="' + n + '"' +
        (n === actual ? ' aria-current="page"' : "") + ">" + n + "</button>";
    }
    h += '<button type="button" class="btn btn-secundario btn-sm" data-sa-pagina="next"' +
      (actual >= nPag ? " disabled" : "") + ">Siguiente " + (ICO.der || "") + "</button>";
    return h + "</div>";
  }

  function pintar() {
    if (!VISTA) return;
    var tbody = $("#sa-cuerpo");
    var pag = $("#sa-paginacion");
    var vacio = $("[data-sa-vacio]", VISTA.zona);
    if (!tbody) return;
    var all = lista();
    var q = norm(VISTA.busqueda);
    var filas = all.filter(function (p) {
      if (VISTA.soloActivos && estadoReal(p) !== "Activo") return false;
      if (VISTA.rol && p.rol !== VISTA.rol) return false;
      if (VISTA.estado && estadoReal(p) !== VISTA.estado) return false;
      if (q && norm(p.nombre + " " + p.correo + " " + (p.identificacion || "") +
        " " + (p.id_institucional || "")).indexOf(q) < 0) return false;
      return true;
    });
    filas.sort(function (a, b) { return comparar(a, b, VISTA.orden); });
    var total = filas.length;
    var nPag = Math.max(1, Math.ceil(total / VISTA.tam));
    if (VISTA.pagina > nPag) VISTA.pagina = nPag;
    if (VISTA.pagina < 1) VISTA.pagina = 1;
    var ini = (VISTA.pagina - 1) * VISTA.tam;
    var page = filas.slice(ini, ini + VISTA.tam);
    tbody.innerHTML = page.map(filaHTML).join("");
    if (vacio) vacio.hidden = total > 0;
    if (pag) {
      var desde = total ? ini + 1 : 0;
      var hasta = Math.min(ini + VISTA.tam, total);
      pag.innerHTML = pagHTML(nPag, VISTA.pagina, desde, hasta, total);
    }
    contar();
  }

  function initTabla() {
    var zona = $("#sa-perfiles-vista") || $("#sa-perfiles-activos-vista");
    if (!zona) return;
    VISTA = {
      zona: zona,
      soloActivos: zona.getAttribute("data-solo-activos") === "1",
      busqueda: "", rol: "", estado: "", orden: "nombre", pagina: 1, tam: 8
    };
    var est = param("estado");
    if (["Activo", "Limitado", "Inactivo"].indexOf(est) >= 0) VISTA.estado = est;
    var rol = param("rol");
    if (ROLES.indexOf(rol) >= 0) VISTA.rol = rol;
    var q = param("q") || param("busqueda");
    if (q) VISTA.busqueda = q;
    var b = $("#sa-buscar");
    if (b) {
      if (VISTA.busqueda) b.value = VISTA.busqueda;
      b.addEventListener("input", function () {
        VISTA.busqueda = b.value; VISTA.pagina = 1; pintar();
      });
    }
    var fr = $("#sa-filtro-rol");
    if (fr) {
      if (VISTA.rol) fr.value = VISTA.rol;
      fr.addEventListener("change", function () {
        VISTA.rol = fr.value; VISTA.pagina = 1; pintar();
      });
    }
    var fe = $("#sa-filtro-estado");
    if (fe) {
      if (VISTA.estado) fe.value = VISTA.estado;
      fe.addEventListener("change", function () {
        VISTA.estado = fe.value; VISTA.pagina = 1; pintar();
      });
    }
    var fo = $("#sa-orden");
    if (fo) fo.addEventListener("change", function () {
      VISTA.orden = fo.value; VISTA.pagina = 1; pintar();
    });
    pintar();
    window.addEventListener("storage", function (e) {
      if (e.key === KEY) pintar();
    });
    window.addEventListener("pageshow", function () { pintar(); });
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) pintar();
    });
  }

  /* --- modal y toast (mismo marcado del kit) ----------------------------- */
  var veloActual = null;
  function cerrarModal() {
    if (veloActual && veloActual.parentNode) veloActual.parentNode.removeChild(veloActual);
    veloActual = null;
    document.body.classList.remove("sin-scroll");
  }
  function abrirModal(titulo, cuerpo, botones) {
    cerrarModal();
    var velo = document.createElement("div");
    velo.className = "modal-velo";
    velo.innerHTML =
      '<div class="modal" role="dialog" aria-modal="true" aria-labelledby="sa-modal-t">' +
      '<div class="modal-head"><h2 id="sa-modal-t">' + esc(titulo) + "</h2>" +
      '<button type="button" class="icon-btn modal-x" aria-label="Cerrar">' +
      (ICO.x || "×") + "</button></div>" +
      '<div class="modal-cuerpo">' + cuerpo + "</div>" +
      '<div class="modal-foot"></div></div>';
    var pie = $(".modal-foot", velo);
    (botones || [{ txt: "Cerrar", clase: "btn btn-secundario" }]).forEach(function (b) {
      var el = document.createElement("button");
      el.type = "button";
      el.className = b.clase || "btn btn-secundario";
      el.textContent = b.txt;
      el.addEventListener("click", function (e) {
        e.preventDefault(); e.stopPropagation();
        if (b.alClic) {
          var seguir = b.alClic(velo);
          if (seguir === false) return;
        }
        if (b.cerrar !== false) cerrarModal();
      });
      pie.appendChild(el);
    });
    $(".modal-x", velo).addEventListener("click", function (e) {
      e.preventDefault(); cerrarModal();
    });
    velo.addEventListener("click", function (e) { if (e.target === velo) cerrarModal(); });
    document.body.appendChild(velo);
    document.body.classList.add("sin-scroll");
    veloActual = velo;
    return velo;
  }

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
    var ic = tipo === "ok" ? ICO.check : (tipo === "error" ? ICO.alerta : ICO.bombilla);
    t.innerHTML = (ic || "") + "<span>" + esc(msg) + "</span>";
    pila.appendChild(t);
    setTimeout(function () { t.classList.add("va-fuera"); }, 3200);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 3800);
  }

  /* --- validacion -------------------------------------------------------- */
  function limpiarErrores(raiz) {
    $$(".campo-error", raiz || document).forEach(function (e) {
      if (e.id === "sa-error-rol") { e.hidden = true; e.textContent = ""; return; }
      e.remove();
    });
    $$("[aria-invalid]", raiz || document).forEach(function (c) {
      c.removeAttribute("aria-invalid");
    });
  }
  function marcar(campoEl, msg) {
    if (!campoEl) return;
    var caja = campoEl.closest(".campo") || campoEl.parentNode;
    var err = caja.querySelector(".campo-error");
    if (!err) {
      err = document.createElement("span");
      err.className = "campo-error";
      caja.appendChild(err);
    }
    err.textContent = msg;
    campoEl.setAttribute("aria-invalid", "true");
    campoEl.focus();
  }
  function validarDatos(nombre, correo, identificacion, idInstitucional,
                       claveActual, rol, esNuevo, password) {
    if (!nombre) return { campo: "nombre", msg: "El nombre completo es obligatorio." };
    if (!correo) return { campo: "correo", msg: "El correo institucional es obligatorio." };
    if (!/^[a-z0-9._%+-]+@uniminuto\.edu\.co$/i.test(correo)) {
      return { campo: "correo", msg: "Usa un correo institucional @uniminuto.edu.co." };
    }
    if (esNuevo && !identificacion) {
      return { campo: "identificacion", msg: "La identificación personal es obligatoria." };
    }
    if (esNuevo && !idInstitucional) {
      return { campo: "id_institucional", msg: "El ID institucional es obligatorio." };
    }
    if (esNuevo && !password) {
      return { campo: "password", msg: "La contraseña provisional es obligatoria." };
    }
    if (password && password.length < 8) {
      return { campo: "password", msg: "La contraseña debe tener al menos 8 caracteres." };
    }
    var otros = lista().filter(function (p) { return p.clave !== claveActual; });
    /* El correo identifica la cuenta dentro de cada rol: los tres modulos del
       prototipo son independientes. Sin rol elegido (fase 1) se omite esta
       comprobacion y se repite al crear el perfil. */
    if (rol && otros.some(function (p) {
      return p.rol === rol && norm(p.correo) === norm(correo);
    })) {
      return { campo: "correo", msg: "Ya existe un perfil de " + rol + " con este correo institucional." };
    }
    if (identificacion && otros.some(function (p) {
      return norm(p.identificacion || "") === norm(identificacion);
    })) {
      return { campo: "identificacion", msg: "Ya existe un perfil con esta identificación personal." };
    }
    if (idInstitucional && otros.some(function (p) {
      return norm(p.id_institucional || "") === norm(idInstitucional);
    })) {
      return { campo: "id_institucional", msg: "Ya existe un perfil con este ID institucional." };
    }
    return null;
  }

  /* --- acciones sobre un perfil ----------------------------------------- */
  function verPerfil(p) {
    var h = '<dl class="lista-def">';
    h += '<div class="def-row"><dt>Nombre completo</dt><dd><b>' + esc(p.nombre) + "</b></dd></div>";
    h += '<div class="def-row"><dt>Identificación personal</dt><dd>' + esc(p.identificacion || "—") + "</dd></div>";
    h += '<div class="def-row"><dt>ID institucional</dt><dd>' + esc(p.id_institucional || "—") + "</dd></div>";
    h += '<div class="def-row"><dt>Correo institucional</dt><dd>' + esc(p.correo) + "</dd></div>";
    h += '<div class="def-row"><dt>Rol</dt><dd>' + esc(p.rol) + "</dd></div>";
    h += '<div class="def-row"><dt>Estado</dt><dd>' + badgeHTML(estadoReal(p)) + "</dd></div>";
    h += '<div class="def-row"><dt>Fecha de creación</dt><dd>' + esc(p.fecha || "No registrada") + "</dd></div>";
    h += '<div class="def-row"><dt>Contraseña provisional</dt><dd>' +
      (p.password ? "Definida" : "Sin registrar") + "</dd></div>";
    h += "</dl>";
    if (p.detalle) {
      var det = "";
      for (var k in p.detalle) {
        if (Object.prototype.hasOwnProperty.call(p.detalle, k) && p.detalle[k]) {
          det += '<div class="def-row"><dt>' + esc(k) + "</dt><dd>" + esc(p.detalle[k]) + "</dd></div>";
        }
      }
      if (det) h += '<div class="sa-subt">Datos del perfil en el sistema</div><dl class="lista-def">' + det + "</dl>";
    }
    h += '<div class="sa-subt">Permisos configurados</div>';
    h += '<p class="modal-aviso">' + permisosTexto(p) + "</p>";
    abrirModal(p.nombre, h, [
      { txt: "Cerrar", clase: "btn btn-secundario" },
      { txt: "Editar perfil", clase: "btn btn-primario", alClic: function () {
        location.href = "editar-perfil.html?clave=" + encodeURIComponent(p.clave);
      } }
    ]);
  }

  function initEditar() {
    var form = $("#vista-editar-perfil");
    if (!form) return;
    var p = buscar(param("clave"));
    var vacio = $("#sa-editar-vacio");
    var contenido = $("#sa-editar-contenido");
    if (!p) {
      if (vacio) vacio.hidden = false;
      return;
    }
    if (contenido) contenido.hidden = false;

    function llenar() {
      $('[name="nombre"]', form).value = p.nombre || "";
      $('[name="identificacion"]', form).value = p.identificacion || "";
      $('[name="id_institucional"]', form).value = p.id_institucional || "";
      $('[name="correo"]', form).value = p.correo || "";
      $("#sa-edit-rol").textContent = p.rol;
      $("#sa-edit-activo").checked = p.estado !== "Inactivo";
      $("#sa-edit-activo-txt").textContent = p.estado !== "Inactivo"
        ? "La cuenta puede iniciar sesión; el estado depende de sus permisos."
        : "La cuenta está bloqueada y no aparece en Perfiles activos.";
      $("#sa-edit-estado-badge").innerHTML = badgeHTML(estadoReal(p));
      $("#sa-edit-perm-badge").innerHTML = badgeHTML(estadoReal(p));
      $("#sa-edit-password-estado").textContent = p.password
        ? "Este perfil ya tiene una contraseña registrada. Si escribes una nueva, reemplazará la anterior."
        : "Este perfil no tiene contraseña registrada. Puedes asignar una provisional.";
      actualizarResumen();
    }
    function actualizarResumen() {
      var act = permisosActivos(p);
      var tot = permisosDefecto(p.rol).length;
      $("#sa-edit-perm-resumen").textContent = act + " de " + tot +
        " permisos del rol activos" + (act < tot ? " · perfil limitado" : ".");
      var link = $("#sa-edit-perm-link");
      var link2 = $("#sa-edit-permisos");
      var href = "permisos.html?clave=" + encodeURIComponent(p.clave);
      if (link) link.href = href;
      if (link2) link2.href = href;
    }

    llenar();

    $("#sa-edit-activo").addEventListener("change", function () {
      var on = $("#sa-edit-activo").checked;
      $("#sa-edit-activo-txt").textContent = on
        ? "La cuenta puede iniciar sesión; el estado depende de sus permisos."
        : "La cuenta está bloqueada y no aparece en Perfiles activos.";
    });

    $("#sa-edit-guardar").addEventListener("click", function () {
      limpiarErrores(form);
      var nombre = $('[name="nombre"]', form).value.trim();
      var correo = $('[name="correo"]', form).value.trim();
      var ident = $('[name="identificacion"]', form).value.trim();
      var idInst = $('[name="id_institucional"]', form).value.trim();
      var pass = $("#sa-edit-password", form).value;
      var err = validarDatos(nombre, correo, ident, idInst, p.clave, p.rol, false, pass);
      if (err) {
        var mapa = {
          nombre: '[name="nombre"]', correo: '[name="correo"]',
          identificacion: '[name="identificacion"]',
          id_institucional: '[name="id_institucional"]',
          password: "#sa-edit-password"
        };
        marcar($(mapa[err.campo], form), err.msg);
        return;
      }
      var activo = $("#sa-edit-activo").checked;
      var cambio = {
        nombre: nombre, correo: correo, identificacion: ident,
        id_institucional: idInst, estado: activo ? "Activo" : "Inactivo"
      };
      if (pass) {
        cambio.password = pass;
        cambio.debe_cambiar = true;
      }
      guardarCambio(p.clave, cambio);
      p = buscar(p.clave);
      $("#sa-edit-password", form).value = "";
      llenar();
      contar();
      toast("Perfil actualizado correctamente.", "ok");
    });
  }

  function initPermisos() {
    var form = $("#vista-permisos");
    if (!form) return;
    var p = buscar(param("clave"));
    var vacio = $("#sa-permisos-vacio");
    var contenido = $("#sa-permisos-contenido");
    if (!p) {
      if (vacio) vacio.hidden = false;
      return;
    }
    if (contenido) contenido.hidden = false;

    function ficha() {
      var h = "";
      h += '<div class="def-row"><dt>Nombre</dt><dd><b>' + esc(p.nombre) + "</b></dd></div>";
      h += '<div class="def-row"><dt>Identificación</dt><dd>' + esc(p.identificacion || "—") + "</dd></div>";
      h += '<div class="def-row"><dt>ID institucional</dt><dd>' + esc(p.id_institucional || "—") + "</dd></div>";
      h += '<div class="def-row"><dt>Correo</dt><dd>' + esc(p.correo) + "</dd></div>";
      h += '<div class="def-row"><dt>Rol</dt><dd>' + esc(p.rol) + "</dd></div>";
      $("#sa-perm-ficha").innerHTML = h;
      $("#sa-perm-estado").innerHTML = badgeHTML(estadoReal(p));
      var act = permisosActivos(p);
      var tot = permisosDefecto(p.rol).length;
      $("#sa-perm-resumen").textContent = act + " de " + tot +
        " permisos del rol activos" + (act < tot ? " · perfil limitado" : ".");
      var ed = $("#sa-perm-link-editar");
      if (ed) ed.href = "editar-perfil.html?clave=" + encodeURIComponent(p.clave);
    }
    $("#sa-perm-caja").innerHTML = permisosHTML(p.rol, p.permisos);
    ficha();

    $("#sa-perm-caja").addEventListener("change", function () {
      var act = getPermisos($("#sa-perm-caja")).filter(function (c) {
        return permisosDefecto(p.rol).indexOf(c) >= 0;
      }).length;
      var tot = permisosDefecto(p.rol).length;
      $("#sa-perm-resumen").textContent = act + " de " + tot +
        " permisos del rol activos" + (act < tot ? " · perfil limitado" : ".");
    });

    $("#sa-perm-restablecer").addEventListener("click", function () {
      $("#sa-perm-caja").innerHTML = permisosHTML(p.rol, permisosDefecto(p.rol));
      toast("Permisos restablecidos a los del rol. Aún no se han guardado.", "info");
      $("#sa-perm-resumen").textContent = permisosDefecto(p.rol).length + " de " +
        permisosDefecto(p.rol).length + " permisos del rol activos.";
    });

    $("#sa-perm-guardar").addEventListener("click", function () {
      var perms = getPermisos($("#sa-perm-caja"));
      guardarCambio(p.clave, { permisos: perms });
      p = buscar(p.clave);
      ficha();
      contar();
      toast("Permisos actualizados correctamente.", "ok");
    });
  }

  function initMiPerfil() {
    var form = $("#vista-mi-perfil");
    if (!form) return;
    var c = cuentaActual();

    function llenar() {
      $('[name="nombre"]', form).value = c.nombre || "";
      $('[name="identificacion"]', form).value = c.identificacion || "";
      $('[name="id_institucional"]', form).value = c.id_institucional || "";
      $('[name="correo"]', form).value = c.correo || "";
      $('[name="cargo"]', form).value = c.cargo || "";
      $('[name="telefono"]', form).value = c.telefono || "";
    }
    llenar();

    $("#sa-mi-guardar").addEventListener("click", function () {
      limpiarErrores(form);
      var nombre = $('[name="nombre"]', form).value.trim();
      var ident = $('[name="identificacion"]', form).value.trim();
      var idInst = $('[name="id_institucional"]', form).value.trim();
      var correo = $('[name="correo"]', form).value.trim();
      var cargo = $('[name="cargo"]', form).value.trim();
      var tel = $('[name="telefono"]', form).value.trim();
      if (!nombre) { marcar($('[name="nombre"]', form), "El nombre completo es obligatorio."); return; }
      if (!ident) { marcar($('[name="identificacion"]', form), "La identificación personal es obligatoria."); return; }
      if (!idInst) { marcar($('[name="id_institucional"]', form), "El ID institucional es obligatorio."); return; }
      if (!correo) { marcar($('[name="correo"]', form), "El correo institucional es obligatorio."); return; }
      if (!/^[a-z0-9._%+-]+@uniminuto\.edu\.co$/i.test(correo)) {
        marcar($('[name="correo"]', form), "Usa un correo institucional @uniminuto.edu.co.");
        return;
      }
      c.nombre = nombre;
      c.identificacion = ident;
      c.id_institucional = idInst;
      c.correo = correo;
      c.cargo = cargo;
      c.telefono = tel;
      guardarCuenta(c);
      llenar();
      syncCuenta();
      toast("Tu perfil se actualizó correctamente.", "ok");
    });
  }

  /* --- asistente de creacion -------------------------------------------- */
  function initWizard() {
    var form = $("#vista-crear-perfil");
    if (!form) return;
    var paso = 1;
    var rolActual = "";

    function actualizarSteps(actual) {
      $$("#sa-steps .step").forEach(function (s, i) {
        s.className = "step" + (i < actual ? " hecho" : (i === actual ? " activo" : ""));
        var marca = $("i", s);
        if (marca) marca.innerHTML = i < actual ? (ICO.check14 || "✓") : String(i + 1);
      });
    }
    function setPaso(n) {
      paso = Math.min(3, Math.max(1, n));
      $$("[data-paso]", form).forEach(function (p) {
        p.hidden = p.getAttribute("data-paso") !== String(paso);
      });
      actualizarSteps(paso - 1);
      var atras = $("#sa-atras"), cont = $("#sa-continuar"), crea = $("#sa-crear");
      if (atras) atras.hidden = paso === 1;
      if (cont) cont.hidden = paso === 3;
      if (crea) crea.hidden = paso !== 3;
    }
    function mapaErrores() {
      return {
        nombre: '[name="nombre"]', correo: '[name="correo"]',
        identificacion: '[name="identificacion"]',
        id_institucional: '[name="id_institucional"]',
        password: '[name="password"]'
      };
    }
    function validarPaso1() {
      limpiarErrores(form);
      var nombre = $('[name="nombre"]', form).value.trim();
      var correo = $('[name="correo"]', form).value.trim();
      var ident = $('[name="identificacion"]', form).value.trim();
      var idInst = $('[name="id_institucional"]', form).value.trim();
      var pass = $('[name="password"]', form).value;
      var err = validarDatos(nombre, correo, ident, idInst, null, null, true, pass);
      if (err) {
        marcar($(mapaErrores()[err.campo], form), err.msg);
        return false;
      }
      return true;
    }
    function validarPaso2() {
      var marcado = $('input[name="rol"]:checked', form);
      var err = $("#sa-error-rol");
      if (!marcado) {
        if (err) { err.textContent = "Selecciona un rol para el perfil."; err.hidden = false; }
        return false;
      }
      if (err) { err.hidden = true; err.textContent = ""; }
      return true;
    }

    $$('input[name="rol"]', form).forEach(function (r) {
      r.addEventListener("change", function () {
        $$(".radio-card", form).forEach(function (c) {
          var input = $("input", c);
          c.classList.toggle("sel", !!(input && input.checked));
        });
        rolActual = r.value;
        $("#sa-permisos-crear").innerHTML = permisosHTML(rolActual, permisosDefecto(rolActual));
        var err = $("#sa-error-rol");
        if (err) { err.hidden = true; err.textContent = ""; }
      });
    });

    var atras = $("#sa-atras");
    if (atras) atras.addEventListener("click", function () { setPaso(paso - 1); });
    var cont = $("#sa-continuar");
    if (cont) cont.addEventListener("click", function () {
      if (paso === 1 && !validarPaso1()) return;
      if (paso === 2 && !validarPaso2()) return;
      setPaso(paso + 1);
    });
    var crea = $("#sa-crear");
    if (crea) crea.addEventListener("click", function () {
      if (!validarPaso1()) { setPaso(1); return; }
      if (!validarPaso2()) { setPaso(2); return; }
      var rol = $('input[name="rol"]:checked', form).value;
      if (rol === "Super Admin") {
        toast("No se puede crear otro Super Admin.", "error");
        return;
      }
      var errUnico = validarDatos(
        $('[name="nombre"]', form).value.trim(),
        $('[name="correo"]', form).value.trim(),
        $('[name="identificacion"]', form).value.trim(),
        $('[name="id_institucional"]', form).value.trim(),
        null, rol, true, $('[name="password"]', form).value);
      if (errUnico) {
        setPaso(1);
        marcar($(mapaErrores()[errUnico.campo], form), errUnico.msg);
        return;
      }
      var perms = getPermisos($("#sa-permisos-crear"));
      if (!perms.length) { toast("Selecciona al menos un permiso.", "error"); return; }
      var p = {
        clave: "SA-" + Date.now(),
        identificacion: $('[name="identificacion"]', form).value.trim(),
        id_institucional: $('[name="id_institucional"]', form).value.trim(),
        nombre: $('[name="nombre"]', form).value.trim(),
        correo: $('[name="correo"]', form).value.trim(),
        rol: rol,
        estado: "Activo",
        fecha: HOY,
        origen: "creado",
        detalle: {},
        permisos: perms,
        password: $('[name="password"]', form).value,
        debe_cambiar: true
      };
      crearPerfil(p);
      $("#sa-steps").hidden = true;
      $("#sa-form-crear").hidden = true;
      $("#sa-exito").hidden = false;
      var elNom = $("#sa-exito-nombre"), elRol = $("#sa-exito-rol"),
        elCor = $("#sa-exito-correo"), elId = $("#sa-exito-id"),
        elIdent = $("#sa-exito-identificacion"),
        elPass = $("#sa-exito-password"),
        elPer = $("#sa-exito-permisos");
      if (elNom) elNom.textContent = p.nombre;
      if (elRol) elRol.textContent = p.rol;
      if (elCor) elCor.textContent = p.correo;
      if (elId) elId.textContent = p.id_institucional;
      if (elIdent) elIdent.textContent = p.identificacion;
      if (elPass) elPass.textContent = p.password;
      if (elPer) elPer.textContent = perms.length + " permisos activos";
      contar();
      toast("Perfil creado correctamente.", "ok");
      var linkPerfiles = document.querySelector('#sa-exito a[href="perfiles.html"]');
      if (linkPerfiles) linkPerfiles.href = "perfiles.html?q=" + encodeURIComponent(p.nombre);
      var linkActivos = document.querySelector('#sa-exito a[href="perfiles-activos.html"]');
      if (linkActivos) linkActivos.href = "perfiles-activos.html?q=" + encodeURIComponent(p.nombre);
    });
    var otro = $("#sa-otro");
    if (otro) otro.addEventListener("click", function () {
      form.reset();
      limpiarErrores(form);
      $$(".radio-card", form).forEach(function (c) { c.classList.remove("sel"); });
      $("#sa-permisos-crear").innerHTML = estadoVacioPermisos();
      $("#sa-exito").hidden = true;
      $("#sa-steps").hidden = false;
      $("#sa-form-crear").hidden = false;
      setPaso(1);
    });

    setPaso(1);
    var inicial = $('input[name="rol"]:checked', form);
    if (inicial) inicial.dispatchEvent(new Event("change"));
  }

  function estadoVacioPermisos() {
    return '<div class="vacio">' + (ICO.user || "") +
      "<h3>Selecciona un rol</h3><p>Vuelve a la fase 2 para elegir el rol del perfil.</p></div>";
  }

  /* --- generador de contrasena (delegado) -------------------------------- */
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-sa-generar]") : null;
    if (!b) return;
    e.preventDefault();
    var input = document.getElementById(b.getAttribute("data-sa-generar"));
    if (!input) return;
    input.value = generarClave();
    input.type = "text";
    toast("Contraseña generada. Cópiala antes de guardar.", "ok");
  });

  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-sa-accion]") : null;
    if (!b) return;
    e.preventDefault();
    var p = buscar(b.getAttribute("data-clave"));
    if (!p) return;
    var acc = b.getAttribute("data-sa-accion");
    if (acc === "ver") verPerfil(p);
  });

  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest ? e.target.closest("[data-sa-pagina]") : null;
    if (!b || !VISTA || b.disabled) return;
    e.preventDefault();
    var v = b.getAttribute("data-sa-pagina");
    if (v === "prev") VISTA.pagina--;
    else if (v === "next") VISTA.pagina++;
    else VISTA.pagina = parseInt(v, 10) || 1;
    pintar();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarModal();
  });

  function iniciar() {
    syncCuenta();
    initTabla();
    initWizard();
    initEditar();
    initPermisos();
    initMiPerfil();
    contar();
    window.addEventListener("storage", function (e) {
      if (e.key === KEY) contar();
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
"""


# Iconos que el JS necesita. Se generan con el mismo helper del kit para que
# las filas creadas en el navegador se vean iguales a las del HTML inicial.
SA_ICO = {
    "eye": ico("eye", 16),
    "edit": ico("edit", 16),
    "sliders": ico("sliders", 16),
    "lock": ico("lock", 16),
    "check": ico("check", 16),
    "alerta": ico("alerta", 16),
    "x": ico("x", 16),
    "izq": ico("izq", 14),
    "der": ico("der", 14),
    "check14": ico("check", 14),
    "bombilla": ico("bombilla", 16),
    "check12": ico("check", 12),
    "lock12": ico("lock", 12),
    "alerta12": ico("alerta", 12),
    "user": ico("user", 40),
}


def _inyectar(html):
    """Publica los datos del modulo y agrega su JS al final del documento."""
    if "</body>" in html:
        datos = {
            "perfiles": json.dumps(PERFILES, ensure_ascii=False),
            "permisos": json.dumps(PERMISOS_ROL, ensure_ascii=False),
            "hoy": json.dumps(HOY),
            "ico": json.dumps(SA_ICO, ensure_ascii=False),
            "cuenta": json.dumps(CUENTA_SA, ensure_ascii=False),
        }
        js = (
            "window.SA_PERFILES = %(perfiles)s;\n"
            "window.SA_PERMISOS = %(permisos)s;\n"
            "window.SA_HOY = %(hoy)s;\n"
            "window.SA_ICO = %(ico)s;\n"
            "window.SA_CUENTA_DEF = %(cuenta)s;\n" % datos
        )
        js += SA_JS
        html = ("<script>" + js + "</script>\n</body>").join(
            html.rsplit("</body>", 1))
    return html


def _envolver(fn):
    def _render():
        return _inyectar(fn())
    return _render


def registrar(reg):
    paginas_sa = [
        ("dashboard.html", "01 Super Admin - Panel principal", dashboard),
        ("crear-perfil.html", "02 Super Admin - Crear perfil", crear_perfil),
        ("perfiles.html", "03 Super Admin - Gestión de perfiles", perfiles),
        ("perfiles-activos.html", "04 Super Admin - Perfiles activos",
         perfiles_activos),
        ("editar-perfil.html", "05 Super Admin - Editar perfil", editar_perfil),
        ("permisos.html", "06 Super Admin - Gestión de permisos", permisos),
        ("mi-perfil.html", "07 Super Admin - Mi perfil", mi_perfil),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_sa):
        reg("superadmin", arch, tit, _envolver(fn), i)
