# -*- coding: utf-8 -*-
"""Rol ADMINISTRADOR - 19 pantallas.

Reglas del rol:
  - Gestiona perfiles de docentes y estudiantes, y sus asignaciones.
  - Aprueba solicitudes, crea eventos y modera comentarios.
  - Ve el seguimiento de todos los emprendimientos, no solo los asignados.
  - Exporta reportes en CSV y PDF.
  - Configura el programa (sedes, etapas, cupos, notificaciones) desde su
    propia vista de Configuración.
"""

import json
import unicodedata

from lib_ui import (calendario, calendario_interactivo, agenda,
    shell, metricas, tabla, toolbar, paginas, badge, campo, select, callout,
    card, estado_vacio, formulario, lista_def, steps, ico, boton_accion, distribucion,
    lista_avisos, kanban, linea_tiempo, tabs_paneles, NOTIFS_ADMIN,
    th, _etiqueta,
)
from lib_charts import barras, barras_h, lineas, donut, AZUL, AMAR, GRIS

R = "administrador"

SEDES = ["Sede Norte", "Sede Centro", "Sede Sur"]

BADGE = {
    "activo": "b-azul",
    "confirmado": "b-azul",
    "finalizada": "b-linea",
    "en revisión": "b-amarillo",
    "pendiente": "b-amarillo",
    "vencido": "b-amarillo",
    "aprobado": "b-azul",
    "rechazado": "b-neutra",
    "en espera": "b-amarillo",
    "borrado": "b-neutra",
    "visible": "b-azul",
    "oculto": "b-neutra",
    "programada": "b-amarillo",
    "confirmada": "b-azul",
    "en curso": "b-azul",
    "finalizada": "b-linea",
    "cancelada": "b-neutra",
}

ETAPAS = ["FASE 1 - Ideación", "FASE 2 - Prototipo",
          "FASE 3 - Validación", "FASE 4 - Formalización"]

# Abreviaturas de mes para _fmt_fecha (índice 0-based).
_MESES = ["ene", "feb", "mar", "abr", "may", "jun",
          "jul", "ago", "sep", "oct", "nov", "dic"]

DOCENTES = [
    ("DOC-014", "Carlos Mendoza", "carlos.mendoza@sgemd.edu.co", "Alimentos",
     "3 h", "8", "Activo"),
    ("DOC-013", "Paula Andrea Rios", "paula.rios@sgemd.edu.co", "Moda",
     "2h", "5", "Activo"),
    ("DOC-012", "Hector Vargas", "hector.vargas@sgemd.edu.co", "Muebles",
     "4h", "6", "Activo"),
    ("DOC-011", "Ninafq Beltran", "nina.beltran@sgemd.edu.co", "Ambiental",
     "3h", "7", "Inactivo"),
    ("DOC-010", "Rafael Nieto", "rafael.nieto@sgemd.edu.co", "Tecnología",
     "5h", "4", "Activo"),
]

ESTUDIANTES = [
    ("912646", "Mariana López", "Alimentos", "Sabor y Sabe",
     "FASE 2 - Prototipo", 62, "Activo"),
    ("912647", "Jhon Ospina", "Moda", "Krea Textil",
     "FASE 1 - Ideación", 28, "Activo"),
    ("912648", "Lucía Fernández", "Ambiental", "EcoPack",
     "FASE 3 - Validación", 84, "Activo"),
    ("912649", "Sofía Ramírez", "Alimentos", "Aromas del Sur",
     "FASE 1 - Ideación", 15, "Activo"),
    ("912650", "Andrés Felipe", "Muebles", "Muebles Origen",
     "FASE 2 - Prototipo", 55, "Inactivo"),
    ("912651", "Camilo Rojas", "Tecnología", "TechNova",
     "FASE 1 - Ideación", 12, "Activo"),
    ("912652", "Valentina Ortega", "Moda", "Aura Design",
     "FASE 2 - Prototipo", 47, "Activo"),
    ("912653", "Diego Peralta", "Muebles", "WoodCraft",
     "FASE 1 - Ideación", 24, "Activo"),
    ("912654", "Laura Martínez", "Ambiental", "BioEco",
     "FASE 3 - Validación", 76, "Activo"),
    ("912655", "Sebastián Torres", "Alimentos", "Gourmet Fresh",
     "FASE 2 - Prototipo", 58, "Activo"),
    ("912656", "Ana Restrepo", "Tecnología", "SmartApp",
     "FASE 1 - Ideación", 19, "Activo"),
    ("912657", "Mateo Gómez", "Moda", "Urban Style",
     "FASE 1 - Ideación", 31, "Activo"),
]

EMPRENDIMIENTOS = [
    ("EMP-041", "Sabor y Sabe", "Mariana López", "mariana.lopez@sgemd.edu.co",
     "Alimentos", "Comercio", "FASE 2 - Prototipo", 62, "Carlos Mendoza",
     "carlos.mendoza@sgemd.edu.co", "Sede Norte"),
    ("EMP-040", "Krea Textil", "Jhon Ospina", "jhon.ospina@sgemd.edu.co",
     "Moda", "Moda", "FASE 1 - Ideación", 28, "Paula Andrea Rios",
     "paula.rios@sgemd.edu.co", "Sede Centro"),
    ("EMP-039", "EcoPack", "Lucía Fernández", "lucia.fernandez@sgemd.edu.co",
     "Ambiental", "Industrial", "FASE 3 - Validación", 84, "Hector Vargas",
     "hector.vargas@sgemd.edu.co", "Sede Sur"),
    ("EMP-038", "Aromas del Sur", "Sofía Ramírez", "sofia.ramirez@sgemd.edu.co",
     "Alimentos", "Alimentos", "FASE 1 - Ideación", 15, "Sin asignar",
     "", "Sede Norte"),
    ("EMP-037", "Muebles Origen", "Andrés Felipe", "andres.felipe@sgemd.edu.co",
     "Muebles", "Artesanal", "FASE 2 - Prototipo", 55, "Ninafq Beltran",
     "nina.beltran@sgemd.edu.co", "Sede Centro"),
    ("EMP-036", "TechNova", "Camilo Rojas", "camilo.rojas@sgemd.edu.co",
     "Tecnología", "Software", "FASE 1 - Ideación", 12, "Rafael Nieto",
     "rafael.nieto@sgemd.edu.co", "Sede Norte"),
    ("EMP-035", "Aura Design", "Valentina Ortega", "valentina.ortega@sgemd.edu.co",
     "Moda", "Moda", "FASE 2 - Prototipo", 47, "Paula Andrea Rios",
     "paula.rios@sgemd.edu.co", "Sede Sur"),
    ("EMP-034", "WoodCraft", "Diego Peralta", "diego.peralta@sgemd.edu.co",
     "Muebles", "Artesanal", "FASE 1 - Ideación", 24, "Sin asignar",
     "", "Sede Centro"),
    ("EMP-033", "BioEco", "Laura Martínez", "laura.martinez@sgemd.edu.co",
     "Ambiental", "Industrial", "FASE 3 - Validación", 76, "Hector Vargas",
     "hector.vargas@sgemd.edu.co", "Sede Norte"),
    ("EMP-032", "Gourmet Fresh", "Sebastián Torres", "sebastian.torres@sgemd.edu.co",
     "Alimentos", "Alimentos", "FASE 2 - Prototipo", 58, "Carlos Mendoza",
     "carlos.mendoza@sgemd.edu.co", "Sede Sur"),
    ("EMP-031", "SmartApp", "Ana Restrepo", "ana.restrepo@sgemd.edu.co",
     "Tecnología", "Software", "FASE 1 - Ideación", 19, "Rafael Nieto",
     "rafael.nieto@sgemd.edu.co", "Sede Centro"),
    ("EMP-030", "Urban Style", "Mateo Gómez", "mateo.gomez@sgemd.edu.co",
     "Moda", "Moda", "FASE 1 - Ideación", 31, "Sin asignar",
     "", "Sede Norte"),
]

# Bandeja de solicitudes pendientes (D1/D2/D4).
SOLIC_DESBLOQUEOS = [
    ("912650", "Andres Felipe", "Estudiante", "Cuenta inactiva por 90 días sin acceso",
     "05 nov 2024"),
    ("DOC-011", "Ninafq Beltran", "Docente", "Bloqueo por intentos fallidos de acceso",
     "04 nov 2024"),
    ("912651", "Camilo Rojas", "Estudiante", "Reactivar para retomar su emprendimiento",
     "02 nov 2024"),
    ("912652", "Valentina Ortega", "Estudiante", "Cuenta limitada a petición; solicita reactivar",
     "01 nov 2024"),
]

SOLIC_PARALELOS = [
    ("912647", "Jhon Ospina", "Krea Textil", "Krea Accesorios", "Moda", "06 nov 2024"),
    ("912649", "Sofia Ramirez", "Aromas del Sur", "Café del Sur", "Alimentos", "05 nov 2024"),
    ("912653", "Diego Peralta", "Muebles Origen", "Muebles Origen Kids", "Muebles", "03 nov 2024"),
]

SOLIC_CITAS = [
    ("Mariana López", "Sabor y Sabe", "Carlos Mendoza", "12 nov 2024, 10:00",
     "Revisión del prototipo de empaque"),
    ("Lucia Fernandez", "EcoPack", "Hector Vargas", "13 nov 2024, 14:00",
     "Asesoría sobre costos de producción"),
    ("Jhon Ospina", "Krea Textil", "Paula Andrea Rios", "14 nov 2024, 09:00",
     "Validación de mercado para nueva línea"),
]

# Programa de asesorias (A08): fields = cod, estudiante, docente, fecha (ISO),
# hora, tema, modalidad, estado. Los nombres deben existir en ESTUDIANTES/DOCENTES
# para poder prefiltarlos en el formulario de edicion.
ASESORIAS = [
    ("ASE-012", "Mariana López", "Carlos Mendoza", "2024-11-12", "10:00",
     "Revisión del prototipo de empaque", "Virtual", "Programada"),
    ("ASE-011", "Lucia Fernandez", "Hector Vargas", "2024-11-13", "14:00",
     "Asesoría sobre costos de producción", "Presencial", "Confirmada"),
    ("ASE-010", "Jhon Ospina", "Paula Andrea Rios", "2024-11-14", "09:00",
     "Validación de mercado para nueva línea", "Virtual", "En curso"),
    ("ASE-009", "Sofia Ramirez", "Carlos Mendoza", "2024-11-08", "16:00",
     "Plan financiero y fuentes de financiación", "Virtual", "Finalizada"),
    ("ASE-008", "Andres Felipe", "Ninafq Beltran", "2024-11-07", "11:00",
     "Costos y margen en la línea de muebles", "Presencial", "Cancelada"),
    ("ASE-007", "Mariana López", "Hector Vargas", "2024-11-06", "15:00",
     "Impacto ambiental del empaque", "Virtual", "Finalizada"),
]

def _sin_tildes(txt):
    """Texto sin tildes ni ñ, en minúsculas: base de correos y comparaciones."""
    s = unicodedata.normalize("NFKD", txt or "")
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


def _correo(nombre):
    """Correo institucional a partir del nombre: sin tildes y con puntos."""
    base = _sin_tildes(nombre).replace(" ", ".")
    return "%s@sgemd.edu.co" % base


# Correo institucional derivado del nombre del estudiante
CORREOS_EST = {e[1]: _correo(e[1]) for e in ESTUDIANTES}

# Indice de estudiantes por ID de 6 dígitos y por nombre normalizado (para
# cruzar las bandejas de solicitudes, que escriben el nombre sin tildes).
ID_EST = {e[0]: e for e in ESTUDIANTES}
EST_POR_NOMBRE = {_sin_tildes(e[1]): e for e in ESTUDIANTES}

# Sede de cada estudiante, deducida del emprendimiento que tiene asignado.
SEDE_EST = {e[2]: e[10] for e in EMPRENDIMIENTOS}

# --- Fichas de detalle (vistas propias con ?clave= / ?cod=) -------------------
# Cada vista dedicada del admin recibe sus datos por query string y los pinta
# con los atributos data-campo / data-badge / data-valor. Estos diccionarios son
# la fuente unica de esas fichas.

SOLICITUDES_DET = {}
for _i, (_c, _n, _r, _m, _f) in enumerate(SOLIC_DESBLOQUEOS, 1):
    SOLICITUDES_DET["SOL-D%02d" % _i] = {
        "id": "SOL-D%02d" % _i, "tipo": "Desbloqueo de cuenta", "codigo": _c,
        "solicitante": _n, "rol": _r, "fecha": _f, "motivo": _m,
        "correo": CORREOS_EST.get(_n, _sin_tildes(_n).replace(" ", ".")
                                  + "@sgemd.edu.co"),
        "accion": "Reactivar la cuenta y notificar al solicitante.",
        "detalle": "La cuenta está bloqueada o inactiva. Al aprobar, el sistema "
                   "restablece el acceso con el estado Activo y registra la "
                   "decisión en la bitácora.",
        "clase": "b-linea",
    }
for _i, (_c, _n, _emp, _nu, _s, _f) in enumerate(SOLIC_PARALELOS, 1):
    SOLICITUDES_DET["SOL-P%02d" % _i] = {
        "id": "SOL-P%02d" % _i, "tipo": "Emprendimiento en paralelo",
        "codigo": _c, "solicitante": _n, "rol": "Estudiante", "fecha": _f,
        "motivo": "Pasa de %s a %s (sector %s)." % (_emp, _nu, _s),
        "correo": CORREOS_EST.get(_n, ""),
        "accion": "Habilitar el segundo emprendimiento y asignar docente.",
        "detalle": "El estudiante conserva su emprendimiento actual y suma %s. "
                   "Revisa la capacidad docente antes de aprobar." % _nu,
        "clase": "b-linea",
    }
for _i, (_n, _e, _d, _f, _m) in enumerate(SOLIC_CITAS, 1):
    SOLICITUDES_DET["SOL-C%02d" % _i] = {
        "id": "SOL-C%02d" % _i, "tipo": "Cita de asesoría",
        "codigo": (EST_POR_NOMBRE.get(_sin_tildes(_n), ("",))[0] or "—"), "solicitante": _n, "rol": "Estudiante",
        "fecha": _f, "motivo": _m, "correo": CORREOS_EST.get(_n, ""),
        "accion": "Confirmar la cita con %s y notificar el horario." % _d,
        "detalle": "La cita fue propuesta por el estudiante para el "
                   "emprendimiento %s. El docente sugerido es %s." % (_e, _d),
        "clase": "b-linea",
    }

# Ficha del docente/estudiante: alimenta usuario-detalle y los formularios.
USUARIOS_DET = {}
for _cod, _nom, _correo, _area, _carga, _emp, _est in DOCENTES:
    USUARIOS_DET[_cod] = {
        "tipo": "docente", "codigo": _cod, "nombre": _nom, "correo": _correo,
        "area": _area, "carga": _carga, "emprendimientos": _emp,
        "estado": _est, "telefono": "+57 300 555 0142",
        "ultimo_acceso": "Hoy, 07:42", "registro": "12 mar 2024",
        "clase": "b-azul" if _est == "Activo" else "b-amarillo",
        "nombres": _nom.split(" ")[0], "apellidos": " ".join(_nom.split(" ")[1:]),
        "nota": "Docente de acompañamiento del programa.",
    }
for _cod, _nom, _sec, _emp, _et, _av, _est in ESTUDIANTES:
    USUARIOS_DET[_cod] = {
        "tipo": "estudiante", "codigo": _cod, "nombre": _nom,
        "correo": CORREOS_EST.get(_nom, ""), "sector": _sec,
        "emprendimiento": _emp, "etapa": _et, "avance": "%d%%" % _av,
        "sede": SEDE_EST.get(_nom, ""), "estado": _est,
        "telefono": "+57 301 555 0199", "ultimo_acceso": "Hoy, 08:02",
        "registro": "12 mar 2024",
        "clase": "b-azul" if _est == "Activo" else "b-amarillo",
        "nombres": _nom.split(" ")[0], "apellidos": " ".join(_nom.split(" ")[1:]),
        "nota": "El estudiante edita sus datos personales; el administrador "
                "gestiona el estado de acceso.",
    }

# Ficha completa del emprendimiento (ver, editar y registrar avance).
EMP_DET = {}
for _cod, _emp, _estu, _correo_est, _sector, _tipo, _etapa, _av, _doc, _correo_doc, _sede in EMPRENDIMIENTOS:
    EMP_DET[_cod] = {
        "codigo": _cod, "nombre": _emp, "estudiante": _estu,
        "correo": _correo_est, "est_id": (EST_POR_NOMBRE.get(_sin_tildes(_estu), ("",))[0] or "—"),
        "sector": _sector, "tipo": _tipo, "etapa": _etapa,
        "avance": str(_av), "docente": _doc,
        "correo_doc": _correo_doc, "sede": _sede,
        "clase": "b-azul" if _doc != "Sin asignar" else "b-amarillo",
        "docente_txt": _doc if _doc != "Sin asignar" else "Sin docente asignado",
        "estado": ("Al día" if _av >= 60 else
                   ("Sin avance" if _av == 0 else "En riesgo")),
        "descripcion": ("Emprendimiento del sector %s en la etapa %s. Acompañado "
                        "por el programa SGEMD." % (_sector, _etapa)),
    }

# Ficha de la asesoria (ver y editar).
ASES_DET = {}
for _cod, _estu, _doc, _fecha, _hora, _tema, _mod, _est in ASESORIAS:
    ASES_DET[_cod] = {
        "codigo": _cod, "estudiante": _estu, "docente": _doc,
        "fecha": _fecha, "hora": _hora, "tema": _tema, "modalidad": _mod,
        "estado": _est, "clase": BADGE.get(_est.lower(), "b-neutra"),
        "emprendimiento": next((e[2] for e in ESTUDIANTES if e[1] == _estu), ""),
        "lugar": ("meet.sgemd.edu.co/ases-" + _cod.split("-")[-1]
                  if _mod == "Virtual" else "Sala 3 · Bloque B"),
        "nota": "Sesión de acompañamiento del programa.",
    }

# Ficha del evento (tarjetas, ver y editar).
EVENTOS_DET = {
    "taller-costos": {
        "ev": "taller-costos", "titulo": "Taller de costos y precios",
        "fecha": "18 nov 2024", "hora": "09:00 - 11:00",
        "formato": "Presencial", "lugar": "Auditorio A",
        "lugar_etiqueta": "Ubicación", "enlace": "",
        "descripcion": "Taller práctico para calcular el costo de insumos y "
                       "definir el punto de equilibrio de un emprendimiento.",
        "cupos": "32 de 40 cupos", "estado": "Publicado", "clase": "b-azul",
        "dirigido": "Todos los estudiantes", "recordatorio": "Un día antes",
    },
    "feria-emprendedores": {
        "ev": "feria-emprendedores", "titulo": "Feria de emprendedores",
        "fecha": "22 nov 2024", "hora": "14:00 - 18:00",
        "formato": "Mixto", "lugar": "Plaza central",
        "lugar_etiqueta": "Ubicación", "enlace": "meet.sgemd.edu.co/feria-2024",
        "descripcion": "Muestra de los emprendimientos del programa con "
                       "compradores y aliados del ecosistema.",
        "cupos": "86 de 120 cupos", "estado": "Publicado", "clase": "b-azul",
        "dirigido": "Todos los estudiantes", "recordatorio": "Dos días antes",
    },
    "jornada-mentoria": {
        "ev": "jornada-mentoria", "titulo": "Jornada de mentoría",
        "fecha": "25 nov 2024", "hora": "08:30 - 12:00",
        "formato": "Virtual", "lugar": "",
        "lugar_etiqueta": "Enlace de conexión",
        "enlace": "meet.sgemd.edu.co/mentoria-2024",
        "descripcion": "Encuentro con mentores para revisar la propuesta de "
                       "valor y el plan de crecimiento de cada emprendimiento.",
        "cupos": "14 confirmados", "estado": "Por aprobar", "clase": "b-amarillo",
        "dirigido": "Todos los estudiantes", "recordatorio": "Un día antes",
    },
    "marco-legal": {
        "ev": "marco-legal", "titulo": "Charla: marco legal para negocios",
        "fecha": "02 dic 2024", "hora": "10:00 - 11:30",
        "formato": "Presencial", "lugar": "Auditorio B",
        "lugar_etiqueta": "Ubicación", "enlace": "",
        "descripcion": "Aspectos legales básicos para formalizar un "
                       "emprendimiento: constitución, impuestos y contratos.",
        "cupos": "0 de 50 cupos", "estado": "Borrador", "clase": "b-neutra",
        "dirigido": "Todos los estudiantes", "recordatorio": "Un día antes",
    },
    "financiamiento": {
        "ev": "financiamiento", "titulo": "Charla: opciones de financiamiento",
        "fecha": "04 nov 2024", "hora": "10:00 - 12:00",
        "formato": "Presencial", "lugar": "Auditorio B",
        "lugar_etiqueta": "Ubicación", "enlace": "",
        "descripcion": "Convocatorias, fondos y programas de crédito "
                       "disponibles para emprendimientos en etapa temprana.",
        "cupos": "48 asistentes", "estado": "Finalizado", "clase": "b-linea",
        "dirigido": "Todos los estudiantes", "recordatorio": "Un día antes",
    },
}


# Enlaces contextuales de cada ficha (los consumen las vistas de detalle).
for _k, _v in USUARIOS_DET.items():
    _v["editar_url"] = ("usuario-docente.html?cod=%s" % _k
                        if _v["tipo"] == "docente"
                        else "usuario-estudiante.html?cod=%s" % _k)
    _v["area_txt"] = _v.get("area") or _v.get("sector", "—")
    _v["carga_txt"] = _v.get("carga") or _v.get("etapa", "—")
    _v["emp_txt"] = _v.get("emprendimiento") or _v.get("emprendimientos", "—")
    _v["avance_txt"] = _v.get("avance", "—")
    _v["sede_txt"] = _v.get("sede", "—")
for _k, _v in EMP_DET.items():
    _v["detalle_url"] = "emprendimiento-detalle.html?cod=%s" % _k
    _v["editar_url"] = "emprendimiento-editar.html?cod=%s" % _k
    _v["avance_url"] = "avance-form.html?cod=%s" % _k
    _v["asignar_url"] = "asignacion-form.html?cod=%s" % _k
    _v["seguimiento_url"] = "seguimiento-detalle.html?cod=%s" % _k
    _v["diagnostico_url"] = "diagnostico-detalle.html?cod=%s" % _k
for _k, _v in ASES_DET.items():
    _v["detalle_url"] = "asesoria-detalle.html?cod=%s" % _k
    _v["editar_url"] = "asesoria-form.html?cod=%s" % _k
for _k, _v in EVENTOS_DET.items():
    _v["editar_url"] = "evento-form.html?ev=%s" % _k
    _v["ver_url"] = "evento-detalle.html?ev=%s" % _k


def _aplicar_datos(datos, param="cod", defecto=""):
    """Script de pagina que pinta la ficha seleccionada por query string.

    Los elementos con data-campo reciben texto, los data-badge reciben la clase
    de color, los data-valor rellenan inputs y selects y los data-enlace
    actualizan el href de un boton."""
    return ("<script>window.__DET=%s;(function(){"
            "var q=new URLSearchParams(location.search);var k=q.get('%s');"
            "var D=window.__DET;var d=D[k]||D['%s'];if(!d)return;"
            "document.querySelectorAll('[data-campo]').forEach(function(el){"
            "var f=el.getAttribute('data-campo');"
            "if(d[f]!==undefined)el.textContent=d[f];});"
            "document.querySelectorAll('[data-badge]').forEach(function(el){"
            "var f=el.getAttribute('data-badge');"
            "if(d[f])el.className='badge '+d[f];});"
            "document.querySelectorAll('[data-valor]').forEach(function(el){"
            "var f=el.getAttribute('data-valor');"
            "if(d[f]!==undefined)el.value=d[f];});"
            "document.querySelectorAll('[data-enlace]').forEach(function(el){"
            "var f=el.getAttribute('data-enlace');"
            "if(d[f]!==undefined)el.setAttribute('href',d[f]);});"
            "document.querySelectorAll('[data-si-vacio]').forEach(function(el){"
            "var f=el.getAttribute('data-si-vacio');if(!d[f])el.style.display='none';});"
            "})();</script>"
            % (json.dumps(datos, ensure_ascii=False), param, defecto))


def _volver(href, texto="Volver"):
    return ('<a class="btn btn-secundario" href="%s">%s %s</a>'
            % (href, ico("izq", 16), texto))


def _estado_badge(estado):
    return badge(estado, BADGE.get(str(estado).lower(), "b-neutra"))


def _estudiante(nombre):
    """Registro de ESTUDIANTES a partir del nombre (con o sin tildes)."""
    return EST_POR_NOMBRE.get(_sin_tildes(nombre))


def _id_estudiante(nombre):
    """ID de 6 dígitos del estudiante; si no se conoce, devuelve el código
   legacy para que la vista no se rompa."""
    est = _estudiante(nombre)
    return est[0] if est else "—"

# Eventos del calendario navegable de Eventos: día de noviembre de 2024 -> html.
# Se pinta con calendario_interactivo (data-cal-doc) y lo controla ADMIN_JS.

EVENTOS_CAL = {
    18: "<b>Taller de costos y precios</b><br/>Auditorio A · 32 de 40 cupos · Publicado",
    22: "<b>Feria de emprendedores</b><br/>Plaza central · 86 de 120 cupos · Publicado",
    25: "<b>Jornada de mentoria</b><br/>Sala 2 · 14 confirmados · Por aproximado",
}

# Script JS propio del rol administrador para calendario navegable (idéntico
# a la lógica del rol docente, pero inyectado aquí para no añadir cases
# genéricos a lib_js).
# Script JS propio del rol administrador: controlador de tablas con
# buscador, filtros y paginacion propias, fichas de registro, enlaces
# profundos, toasts y modales propios y calendario de eventos. Vive en
# el rol (y no en lib_js) para no tocar el kit compartido ni los otros
# roles.
ADMIN_JS = r"""
(function () {
  "use strict";

  /* ===================================================================
     Script propio del rol ADMINISTRADOR.

     El kit compartido (lib_js) resuelve buscador, filtros y paginacion de
     UNA sola tabla por pagina: se agarra del primer [data-tabla-zona] y de
     los .buscador. Varias pantallas del admin tienen dos tablas, asi que
     aqui hay un controlador por tabla.

     Regla de convivencia (para no tocar lib_js y no romper otros roles):
       - los controles del admin se marcan con data-filtro="off" para que
         el kit los ignore;
       - el buscador del admin no usa la clase .buscador ni la palabra
         "Buscar" en el placeholder, asi que el kit no lo engancha;
       - la paginacion del admin se marca data-pag-adm (no data-paginacion),
         de modo que el kit no la mueve;
       - la visibilidad de las filas la lleva solo este script.
     =================================================================== */

  /* ---- utilidades ----------------------------------------------------- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };
  var norm = function (s) {
    return String(s == null ? "" : s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };
  var ICO = {
    check: "M20 6 9 17l-5-5",
    x: "M18 6 6 18M6 6l12 12",
    alerta: "M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0ZM12 9v4M12 17h.01",
    bombilla: "M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z",
    ojo: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7zM12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
    correo: "M4 4h16v16H4zM4 6l8 6 8-6"
  };
  var svg = function (d, n) {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + (n || 16) + '" height="' +
      (n || 16) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ' +
      'aria-hidden="true"><path d="' + d + '"/></svg>';
  };
  var dato = function (fila, attr) {
    var key = String(attr).replace(/-([a-z])/g, function (m, c) { return c.toUpperCase(); });
    return fila.dataset[key];
  };

  /* ---- toast propio (el kit lo esconde dentro de su IIFE) -------------- */
  var pilaToast = null;
  function toast(mensaje, tipo) {
    if (!pilaToast) {
      pilaToast = document.createElement("div");
      pilaToast.className = "toast-pila";
      pilaToast.setAttribute("role", "status");
      pilaToast.setAttribute("aria-live", "polite");
      document.body.appendChild(pilaToast);
    }
    var t = document.createElement("div");
    t.className = "toast t-" + (tipo || "info");
    t.innerHTML = svg(tipo === "ok" ? ICO.check : (tipo === "error" ? ICO.alerta : ICO.bombilla), 16) +
      "<span>" + esc(mensaje) + "</span>";
    pilaToast.appendChild(t);
    setTimeout(function () { t.classList.add("va-fuera"); }, 3200);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 3800);
  }

  /* ---- modal propio (mismo marcado que el del kit) --------------------- */
  function cerrarModal() {
    var v = $(".modal-velo");
    if (v) v.remove();
    document.body.classList.remove("sin-scroll");
  }
  function abrirModal(titulo, cuerpo, botones) {
    cerrarModal();
    var velo = document.createElement("div");
    velo.className = "modal-velo";
    velo.innerHTML =
      '<div class="modal" role="dialog" aria-modal="true" aria-label="' + esc(titulo) + '">' +
      '<div class="modal-head"><h2>' + esc(titulo) + '</h2>' +
      '<button class="icon-btn modal-x" aria-label="Cerrar">' + svg(ICO.x, 18) + "</button></div>" +
      '<div class="modal-cuerpo">' + cuerpo + "</div>" +
      '<div class="modal-foot"></div></div>';
    var pie = $(".modal-foot", velo);
    (botones || [{ txt: "Cerrar", clase: "btn btn-secundario" }]).forEach(function (b) {
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
    return velo;
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarModal();
  });

  /* ---- calendario interactivo de eventos ------------------------------- */
  var calDoc = document.querySelector("[data-cal-doc]");
  if (calDoc) {
    var celdas = Array.prototype.slice.call(calDoc.querySelectorAll("[data-dia]"));
    var paneles = Array.prototype.slice.call(calDoc.querySelectorAll("[data-dia-panel]"));
    var rotulo = calDoc.querySelector("[data-dia-titulo]");
    var verDia = function (dia, etiqueta) {
      celdas.forEach(function (c) {
        var es = c.getAttribute("data-dia") === String(dia);
        c.classList.toggle("activo", es);
        c.setAttribute("aria-pressed", es ? "true" : "false");
      });
      var hay = false;
      paneles.forEach(function (p) {
        if (p.getAttribute("data-dia-panel") === String(dia)) hay = true;
      });
      paneles.forEach(function (p) {
        var k = p.getAttribute("data-dia-panel");
        p.hidden = hay ? (k !== String(dia)) : (k !== "sin");
      });
      if (rotulo) rotulo.textContent = etiqueta || ("Dia " + dia);
    };
    celdas.forEach(function (c) {
      c.addEventListener("click", function () {
        verDia(c.getAttribute("data-dia"), c.getAttribute("data-etiqueta"));
      });
    });
    var hoyAttr = calDoc.getAttribute("data-hoy");
    var hoyCal = calDoc.querySelector('[data-dia="' + hoyAttr + '"]');
    if (hoyCal) verDia(hoyAttr, hoyCal.getAttribute("data-etiqueta"));
  }

  /* ---- controlador de tablas del admin --------------------------------- */
  var ZONAS = [];

  function crearZona(zona) {
    var tabla = $("table.tabla", zona);
    if (!tabla) return null;
    var tid = (zona.getAttribute("data-tabla-zona") || "").replace(/^adm-/, "");
    var filas = $$("tbody tr", tabla);
    var control = $("[data-pag-adm]", zona);
    var tam = control ? (parseInt(control.dataset.pagTam, 10) || 5) : 0;
    var buscador = $("[data-adm-busca]", zona);
    var filtros = $$("[data-filtro-adm]", zona);
    var contador = $("[data-resultados]", zona);
    var vacio = $("[data-vacio]", zona);
    var pagina = 1;

    function coincide(fila) {
      var q = buscador ? norm(buscador.value) : "";
      if (q && norm(fila.textContent).indexOf(q) < 0) return false;
      for (var i = 0; i < filtros.length; i++) {
        var sel = filtros[i];
        var col = parseInt(sel.dataset.col, 10);
        if (isNaN(col)) continue;
        var celda = fila.children[col];
        if (!celda) continue;
        /* Si la celda declara data-valor se compara contra ese valor (por
           ejemplo un <select> de estado, cuyo textContent trae todas las
           opciones). Si la celda trae un <select>, manda su valor actual,
           para que el filtro siga a la cuenta despues de cambiarla. */
        var selCelda = celda.querySelector("select");
        var propio = selCelda ? selCelda.value : celda.getAttribute("data-valor");
        var txt = norm(propio === null ? celda.textContent : propio);
        var valor = "";
        if (sel.tagName === "SELECT") {
          if (!sel.value) continue;
          valor = norm(sel.value || (sel.selectedOptions[0] ? sel.selectedOptions[0].textContent : ""));
        } else {
          valor = norm(sel.value);
          if (!valor) continue;
        }
        if (valor && txt.indexOf(valor) < 0) return false;
      }
      return true;
    }

    function visibles() {
      return filas.filter(coincide);
    }

    function pintarPag(nPag) {
      var pag = control ? $(".pag", control) : null;
      if (!pag) return;
      var tplPrev = control.querySelector("template[data-pg-ico-prev]");
      var tplNext = control.querySelector("template[data-pg-ico-next]");
      var ip = tplPrev ? tplPrev.innerHTML : "";
      var inx = tplNext ? tplNext.innerHTML : "";
      var h = '<button class="btn btn-secundario btn-sm" data-pagina="prev"' +
        (pagina <= 1 ? " disabled" : "") + ">" + ip + " Anterior</button>";
      for (var n = 1; n <= nPag; n++) {
        h += '<button class="btn btn-sm ' + (n === pagina ? "btn-acento" : "btn-secundario") +
          '" data-pagina="' + n + '"' + (n === pagina ? ' aria-current="page"' : "") + ">" + n + "</button>";
      }
      h += '<button class="btn btn-secundario btn-sm" data-pagina="next"' +
        (pagina >= nPag ? " disabled" : "") + ">Siguiente " + inx + "</button>";
      pag.innerHTML = h;
    }

    function aplicar() {
      var vis = visibles();
      var nPag = tam ? Math.max(1, Math.ceil(vis.length / tam)) : 1;
      if (pagina > nPag) pagina = nPag;
      if (pagina < 1) pagina = 1;
      var desde = (pagina - 1) * tam;
      var hasta = tam ? Math.min(desde + tam, vis.length) : vis.length;
      filas.forEach(function (f) { f.hidden = true; });
      vis.slice(desde, hasta).forEach(function (f) { f.hidden = false; });
      if (contador) {
        contador.textContent = vis.length + (vis.length === 1 ? " resultado" : " resultados");
      }
      if (vacio) vacio.hidden = vis.length > 0;
      if (control) {
        control.dataset.pagActual = pagina;
        control.dataset.pagTotal = nPag;
        control.dataset.pagRegs = vis.length;
        var t = $("[data-pag-texto]", control);
        if (t) {
          t.textContent = "Mostrando " + (vis.length && tam ? desde + 1 : 0) +
            " a " + hasta + " de " + vis.length;
        }
        pintarPag(nPag);
      }
      return vis;
    }

    function irA(fila) {
      var vis = visibles();
      var i = vis.indexOf(fila);
      if (i < 0) return false;
      pagina = tam ? Math.floor(i / tam) + 1 : 1;
      aplicar();
      return true;
    }

    function limpiar() {
      if (buscador) buscador.value = "";
      filtros.forEach(function (f) { f.value = ""; });
      pagina = 1;
      aplicar();
    }

    if (buscador) {
      var t = null;
      buscador.addEventListener("input", function () {
        clearTimeout(t);
        t = setTimeout(function () { pagina = 1; aplicar(); }, 220);
      });
      buscador.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          clearTimeout(t);
          pagina = 1;
          aplicar();
        }
      });
    }
    filtros.forEach(function (f) {
      if (f.tagName === "SELECT") {
        f.addEventListener("change", function () { pagina = 1; aplicar(); });
      } else {
        var tt = null;
        f.addEventListener("input", function () {
          clearTimeout(tt);
          tt = setTimeout(function () { pagina = 1; aplicar(); }, 220);
        });
      }
    });
    if (control) {
      control.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-pagina]");
        if (!b || b.disabled) return;
        e.preventDefault();
        e.stopPropagation();
        var nPag = parseInt(control.dataset.pagTotal, 10) || 1;
        var v = b.dataset.pagina;
        if (v === "prev") pagina = Math.max(1, pagina - 1);
        else if (v === "next") pagina = Math.min(nPag, pagina + 1);
        else pagina = parseInt(v, 10) || 1;
        aplicar();
      });
    }
    aplicar();
    return {
      tid: tid, zona: zona, filas: filas,
      aplicar: aplicar, irA: irA, limpiar: limpiar
    };
  }

  $$("[data-tabla-zona]").forEach(function (z) {
    var c = crearZona(z);
    if (c) ZONAS.push(c);
  });

  function zonaDe(fila) {
    var z = fila.closest("[data-tabla-zona]");
    for (var i = 0; i < ZONAS.length; i++) {
      if (ZONAS[i].zona === z) return ZONAS[i];
    }
    return null;
  }

  /* ---- fichas de registro --------------------------------------------- */
  var FICHAS = {
    estudiante: {
      titulo: "est-nombre",
      campos: [["ID de estudiante", "est-id"], ["Nombre", "est-nombre"],
               ["Correo institucional", "est-correo"], ["Sector", "est-sector"],
               ["Emprendimiento", "est-emp"], ["Etapa", "est-etapa"],
               ["Sede", "est-sede"], ["Avance", "est-avance"],
               ["Estado de la cuenta", "est-estado"]],
      correo: "est-correo"
    },
    emprendimiento: {
      titulo: "emp-nombre",
      campos: [["Código", "emp-cod"], ["Emprendimiento", "emp-nombre"],
               ["ID de estudiante", "emp-est-id"], ["Estudiante", "emp-est-nombre"],
               ["Correo institucional", "emp-est-correo"], ["Sector", "emp-sector"],
               ["Tipo", "emp-tipo"], ["Etapa", "emp-etapa"],
               ["Avance", "emp-avance"], ["Sede", "emp-sede"],
               ["Docente asignado", "emp-docente"]],
      correo: "emp-est-correo"
    },
    docente: {
      titulo: "doc-nombre",
      campos: [["Código", "doc-cod"], ["Nombre", "doc-nombre"],
               ["Correo institucional", "doc-correo"], ["Área", "doc-area"],
               ["Carga semanal", "doc-carga"], ["Emprendimientos", "doc-emp"],
               ["Estado de la cuenta", "doc-estado"]],
      correo: "doc-correo"
    },
    solicitud: {
      titulo: "sol-nombre",
      campos: [["Código", "sol-id"], ["Solicitante", "sol-nombre"],
               ["Tipo de solicitud", "sol-tipo"], ["Detalle", "sol-detalle"],
               ["Fecha", "sol-fecha"]],
      correo: "sol-correo"
    }
  };

  function fichaHTML(fila, tipo) {
    var def = FICHAS[tipo];
    if (!def) return "";
    var h = '<dl class="lista-def">';
    def.campos.forEach(function (c) {
      var v = dato(fila, c[1]);
      if (!v) return;
      h += '<div class="def-row"><dt>' + esc(c[0]) + "</dt><dd>" + esc(v) + "</dd></div>";
    });
    h += "</dl>";
    var correo = def.correo ? dato(fila, def.correo) : "";
    if (correo) {
      h += '<p class="modal-aviso">Contacto directo: <a href="mailto:' + esc(correo) + '">' +
        esc(correo) + "</a></p>";
    }
    return h;
  }

  function abrirFicha(fila, tipo) {
    var def = FICHAS[tipo];
    if (!def || !fila) return;
    var titulo = dato(fila, def.titulo) || "Ficha";
    abrirModal(titulo, fichaHTML(fila, tipo), [
      { txt: "Cerrar", clase: "btn btn-secundario" }
    ]);
  }

  /* ---- panel de detalle de una solicitud ------------------------------- */
  function abrirSolicitud(fila) {
    if (!fila) return;
    var tipo = dato(fila, "sol-tipo") || "Solicitud";
    var cod = dato(fila, "sol-id") || "";
    var nombre = dato(fila, "sol-nombre") || "";
    var detalle = dato(fila, "sol-detalle") || "Sin detalle registrado.";
    var fecha = dato(fila, "sol-fecha") || "";
    var cuerpo =
      '<dl class="lista-def">' +
      '<div class="def-row"><dt>Código</dt><dd>' + esc(cod) + "</dd></div>" +
      '<div class="def-row"><dt>Solicitante</dt><dd>' + esc(nombre) + "</dd></div>" +
      '<div class="def-row"><dt>Tipo</dt><dd>' + esc(tipo) + "</dd></div>" +
      '<div class="def-row"><dt>Fecha</dt><dd>' + esc(fecha) + "</dd></div>" +
      "</dl>" +
      '<p class="modal-aviso"><b>Detalle:</b> ' + esc(detalle) + "</p>" +
      '<div class="form-acciones">' +
      '<button class="btn btn-primario btn-sm" data-accion="solicitud-aprobar">Aprobar</button>' +
      '<button class="btn btn-secundario btn-sm" data-accion="solicitud-rechazar">Rechazar</button>' +
      "</div>";
    abrirModal("Detalle de la solicitud", cuerpo, [
      { txt: "Cerrar", clase: "btn btn-secundario" }
    ]);
  }

  /* ---- reasignar docente (tabla de asignaciones) ----------------------- */
  /* El formulario vive en la pagina (#form-asignar-docente, oculto) y aqui
     solo se clona, se rellena con los data-* de la fila y se abre. */
  function abrirReasignar(fila) {
    if (!fila) return;
    var actual = fila.dataset.docente || "";
    var pendiente = !actual || actual === "Sin asignar" ||
      actual === "Sin docente asignado";
    var plantilla = $("#form-asignar-docente");
    var cuerpo = plantilla
      ? plantilla.innerHTML
      : '<p><b>Proyecto:</b> ' + esc(fila.dataset.proyecto || "") + "</p>";
    var velo = abrirModal(pendiente ? "Asignar docente" : "Reasignar docente",
      cuerpo, [{
        txt: "Confirmar asignación", clase: "btn btn-primario", cerrar: false,
        alClic: function () {
          var sel = $("#docente-asignacion", velo);
          var nuevo = sel ? sel.value : "";
          if (!nuevo) return;
          fila.dataset.docente = nuevo.split(" · ")[0];
          var celdas = fila.children;
          var col = parseInt(fila.dataset.colDocente, 10);
          if (!isNaN(col) && celdas[col]) celdas[col].textContent = fila.dataset.docente;
          var btn = $("[data-adm-accion='reasignar']", fila);
          if (btn) {
            btn.setAttribute("title", "Reasignar docente");
            btn.setAttribute("aria-label", "Reasignar docente");
          }
          toast("Docente asignado correctamente", "ok");
          cerrarModal();
        }
      }, { txt: "Cancelar", clase: "btn btn-secundario" }]);
    /* Rellena el clon con los datos de la fila. */
    var llenar = function (sel2, valor) {
      var el = $(sel2, velo);
      if (el && valor) el.value = valor;
    };
    llenar("#asg-estudiante", fila.dataset.estudiante);
    llenar("#asg-emprendimiento", fila.dataset.proyecto);
    llenar("#asg-correo", fila.dataset.correo);
    var selDoc = $("#docente-asignacion", velo);
    if (selDoc) {
      var coincide = false;
      for (var i = 0; i < selDoc.options.length; i++) {
        if (selDoc.options[i].value === actual) coincide = true;
      }
      selDoc.value = coincide ? actual : "";
    }
    return velo;
  }

  /* ---- atajo del menu: #asignar-docente abre la cola pendiente ---------- */
  function abrirAsignarPendiente() {
    var filas = $$("tr[data-proyecto]");
    for (var i = 0; i < filas.length; i++) {
      var d = filas[i].dataset.docente || "";
      if (!d || d === "Sin asignar" || d === "Sin docente asignado") {
        filas[i].scrollIntoView({ block: "center" });
        abrirReasignar(filas[i]);
        return;
      }
    }
    toast("No hay emprendimientos sin docente asignado", "info");
  }

  /* ---- acciones propias del admin (data-adm-accion) -------------------- */
  $$("[data-adm-accion]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var accion = b.dataset.admAccion;
      var fila = b.closest("tr");
      if (accion === "ficha") abrirFicha(fila, b.dataset.ficha);
      else if (accion === "solicitud") abrirSolicitud(fila);
      else if (accion === "reasignar") abrirReasignar(fila);
    });
  });

  /* ---- interruptor de graficos (barras / anillo) ----------------------- */
  $$("[data-adm-grafico]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var tipo = b.dataset.admGrafico;
      var zona = b.closest(".card") || document;
      $$("[data-grafico-vista]", zona).forEach(function (v) {
        v.hidden = v.getAttribute("data-grafico-vista") !== tipo;
      });
      $$("[data-adm-grafico]", zona).forEach(function (o) {
        o.classList.toggle("btn-acento", o === b);
        o.classList.toggle("btn-secundario", o !== b);
        o.setAttribute("aria-pressed", o === b ? "true" : "false");
      });
    });
  });

  /* ---- prefill del modal de avance ------------------------------------ */
  /* El kit clona el formulario con innerHTML, asi que al abrirlo se pierde la
     opcion marcada del <select> y los valores escritos a mano. Este bloque
     corre despues del handler del kit (el script del admin va detras) y los
     vuelve a poner con los data-* de la fila. */
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest
      ? e.target.closest('[data-accion="registrar-avance"]') : null;
    if (!b) return;
    var fila = b.closest("tr");
    if (!fila) return;
    var d = fila.dataset || {};
    var campos = { emp: d.emp, estu: d.estu, etapa: d.etapa, avance: d.avance };
    for (var nombre in campos) {
      var el = document.querySelector(".modal [name=" + nombre + "]");
      if (el && campos[nombre] !== undefined && campos[nombre] !== "") {
        el.value = campos[nombre];
      }
    }
  });

  /* ---- enlaces profundos: #est-912646, #emp-EMP-041, #doc-DOC-014 ----- */
  function abrirHash() {
    var hash = (location.hash || "").replace("#", "");
    if (!hash) return;
    if (hash === "asignar-docente") { abrirAsignarPendiente(); return; }
    var corte = hash.indexOf("-");
    if (corte < 0) return;
    var tipo = hash.slice(0, corte);
    var id = hash.slice(corte + 1);
    var attr = { est: "est-id", emp: "emp-id", doc: "doc-id", sol: "sol-id" }[tipo];
    if (!attr) return;
    var fila = $("tr[data-" + attr + '="' + id + '"]');
    if (!fila) {
      toast("No encontramos el registro " + id, "error");
      return;
    }
    var z = zonaDe(fila);
    if (z) {
      z.limpiar();
      z.irA(fila);
    }
    fila.scrollIntoView({ block: "center" });
    fila.classList.add("adm-resaltada");
    setTimeout(function () { fila.classList.remove("adm-resaltada"); }, 2600);
    var ficha = $("[data-adm-accion='ficha']", fila);
    if (ficha) ficha.click();
  }
  window.addEventListener("hashchange", abrirHash);
  abrirHash();

  /* ---- el admin tambien tiene vista de configuracion -------------------- */
  /* El kit arma el mini menu con "Preferencias" para el admin; aqui se
     cambia por "Configuracion", que si tiene vista propia. */
  if (window.MutationObserver) {
    var obs = new MutationObserver(function () {
      $$(".who-menu").forEach(function (m) {
        var b = $("button[data-accion='preferencias']", m);
        if (!b) return;
        b.dataset.accion = "configuracion";
        b.textContent = "Configuracion";
      });
    });
    obs.observe(document.body, { childList: true, subtree: true });
  }
})();
"""


# CSS propio del administrador. Se inyecta en el <style> de la pagina con
# shell(extra_head=...) para no tocar lib_css, que se comparte con los demas
# roles. Solo usa tokens de la paleta del sistema.
ADMIN_CSS = """
/* Buscador propio del admin: no usa la clase .buscador porque el kit
   compartido se engancha a ".buscador input" y filtraria la primera tabla
   de la pagina, no la que el admin quiere. */
.adm-busca{display:flex;align-items:center;gap:8px;flex:1 1 240px;min-width:min(200px,100%);
  padding:0 12px;background:var(--blanco);border:1px solid var(--gris);
  border-radius:var(--r-sm)}
.adm-busca svg{flex:0 0 16px;color:var(--gris)}
.adm-busca input{flex:1;min-width:0;border:0;outline:none;background:transparent;
  font-family:inherit;font-size:13px;color:var(--tinta);padding:9px 0}
.adm-busca input::placeholder{color:var(--gris)}
.adm-busca:focus-within{border-color:var(--azul-real);box-shadow:0 0 0 3px var(--azul-12)}
/* Fila que destaca un enlace profundo (#est-912646) */
tr.adm-resaltada>td{background:var(--azul-08)}
tr.adm-resaltada>td:first-child{box-shadow:inset 3px 0 0 var(--amarillo)}
/* La cabecera de la zona del admin muestra el total de resultados */
.adm-zona .card-head .hint{white-space:nowrap;font-weight:600}
/* Navegacion por secciones de Configuracion */
.cfg-nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.cfg-nav-item{padding:8px 14px;border:1px solid var(--gris);border-radius:999px;
  text-decoration:none;color:var(--tinta);font-size:13px;font-weight:600}
.cfg-nav-item:hover{border-color:var(--azul-real);color:var(--azul-real)}
.cfg-seccion{margin-bottom:24px;scroll-margin-top:16px}
.cfg-titulo{font-size:18px;margin:0 0 12px;padding-bottom:8px;
  border-bottom:1px solid var(--gris)}
/* Tarjetas de evento con imagen (Eventos del admin) */
.ev-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));gap:16px}
.ev-card{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);
  overflow:hidden;display:flex;flex-direction:column}
.ev-img{position:relative;height:132px;display:flex;align-items:center;justify-content:center;
  color:var(--blanco);background:linear-gradient(135deg,var(--azul-noche),var(--azul-real))}
.ev-img.g1{background:linear-gradient(135deg,var(--azul-profundo),var(--azul-real))}
.ev-img.g2{background:linear-gradient(135deg,var(--azul-real),var(--azul-profundo));box-shadow:inset 0 -4px 0 var(--amarillo)}
.ev-img.g3{background:linear-gradient(135deg,var(--azul-noche),var(--azul-profundo));box-shadow:inset 0 -4px 0 var(--amarillo)}
.ev-img.g4{background:linear-gradient(135deg,var(--azul-profundo),var(--azul-noche))}
.ev-img svg{opacity:.9}
.ev-body{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px;flex:1}
.ev-body h3{margin:0;font-size:16px;color:var(--tinta)}
.ev-meta{font-size:13px;color:var(--tinta-2);display:flex;flex-wrap:wrap;gap:4px 12px}
.ev-meta span{display:inline-flex;align-items:center;gap:4px}
.ev-foot{margin-top:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.ev-hero{height:220px;border-radius:var(--r-md);display:flex;align-items:center;
  justify-content:center;color:var(--blanco);background:linear-gradient(135deg,var(--azul-noche),var(--azul-real));
  margin-bottom:16px}
.ev-hero.g1{background:linear-gradient(135deg,var(--azul-profundo),var(--azul-real))}
.ev-hero.g2{background:linear-gradient(135deg,var(--azul-real),var(--azul-profundo));box-shadow:inset 0 -4px 0 var(--amarillo)}
.ev-hero.g3{background:linear-gradient(135deg,var(--azul-noche),var(--azul-profundo));box-shadow:inset 0 -4px 0 var(--amarillo)}
.ev-hero.g4{background:linear-gradient(135deg,var(--azul-profundo),var(--azul-noche))}
.ev-preview{height:150px;border-radius:var(--r-sm);display:flex;align-items:center;
  justify-content:center;color:var(--blanco);background:linear-gradient(135deg,var(--azul-noche),var(--azul-real));
  margin-bottom:12px}
.ev-preview.has-img{background-size:cover;background-position:center}
@media (max-width:479px){
  .ev-hero{height:160px}
  .cfg-nav-item{flex:1 1 calc(50% - 8px);text-align:center}
}
"""


def _adm_busca(tid, etiqueta="Nombre, ID o correo"):
    """Buscador de una tabla del admin.

    No usa la clase .buscador (el kit compartido se engancha a ".buscador input"
    y filtraria otra tabla) ni la palabra "Buscar" en el placeholder (el kit
    tambien engancha los input[type=text] cuyo placeholder la contenga)."""
    return ('<div class="adm-busca">%s<input type="text" class="filtro" '
            'data-adm-busca="%s" placeholder="%s" autocomplete="off" '
            'aria-label="Filtrar %s"></div>'
            % (ico("search", 16), tid, etiqueta, etiqueta))


def _adm_filtro(tid, etiqueta, opciones, col, texto=False):
    """Filtro por columna de una tabla del admin.

    data-filtro="off" deja el control fuera del kit compartido. El valor de
    cada opcion es el texto exacto que aparece en la celda, que es lo que
    compara el controlador del admin."""
    if texto:
        return ('<input type="text" class="filtro" data-filtro="off" '
                'data-filtro-adm="%s" data-col="%d" placeholder="%s" '
                'autocomplete="off" aria-label="%s">'
                % (tid, col, etiqueta, etiqueta))
    ops = '<option value="">%s</option>' % opciones[0] + "".join(
        '<option value="%s">%s</option>' % (o, o) for o in opciones[1:])
    return ('<select class="filtro" data-filtro="off" data-filtro-adm="%s" '
            'data-col="%d" aria-label="%s">%s</select>'
            % (tid, col, etiqueta, ops))


def _ficha(tipo, etiqueta="Ver"):
    """Boton de ficha de un registro. El controlador del admin (ADMIN_JS)
    arma el modal con los datos que la fila lleva en data-*."""
    return ('<button class="table-act" data-adm-accion="ficha" data-ficha="%s" '
            'title="%s" aria-label="%s">%s</button>'
            % (tipo, etiqueta, etiqueta, ico("eye", 16)))


def _tabla_adm(tid, titulo, cabeceras, filas, sub="", por_pagina=5,
               caption="", buscador=None, filtros="", acciones="", extra=""):
    """Tabla del admin con buscador, filtros por columna y paginacion propias.

    La zona se marca con data-tabla-zona="adm-<tid>": el controlador del admin
    (ADMIN_JS) filtra, cuenta y pagina SOLO esa tabla. El kit compartido
    resuelve una unica tabla por pagina (toma la primera [data-tabla-zona]),
    asi que las vistas del admin con dos tablas necesitan este camino propio.

    filas: lista de dicts con "celdas" (HTML de cada celda) y "attrs"
    (data-* de la fila: identificadores y datos de la ficha). Una celda puede
    ser ("html", "valor"): el "valor" es lo que comparan los filtros (util para
    un <select> de estado, cuyo textContent trae todas las opciones)."""
    cab = "".join(th(c) for c in cabeceras)
    etiquetas = [_etiqueta(c) for c in cabeceras]
    body = ""
    for fila in filas:
        attrs = "".join(' data-%s="%s"' % (k, v)
                        for k, v in fila.get("attrs", {}).items() if v)
        celdas = ""
        for c, x, eti in zip(cabeceras, fila["celdas"], etiquetas):
            valor = ""
            if isinstance(x, tuple):
                x, valor = x[0], x[1]
            if c == "@ACC":
                celdas += '<td class="acc" data-label="%s">%s</td>' % (eti, x)
            elif isinstance(c, tuple) and c[0] == "num":
                celdas += '<td class="num" data-label="%s">%s</td>' % (eti, x)
            elif valor:
                celdas += '<td data-label="%s" data-valor="%s">%s</td>' % (eti, valor, x)
            else:
                celdas += '<td data-label="%s">%s</td>' % (eti, x)
        body += "<tr%s>%s</tr>" % (attrs, celdas)
    cap = ('<caption class="visually-hidden">%s</caption>' % caption) if caption else ""
    h = '<div class="card adm-zona" data-tabla-zona="adm-%s">' % tid
    h += ('<div class="card-head"><div><h3>%s</h3>%s</div>'
          '<span class="hint" data-resultados>0 resultados</span></div>'
          % (titulo, ('<p class="sub">%s</p>' % sub) if sub else ""))
    h += '<div class="toolbar">'
    h += buscador if buscador is not None else _adm_busca(tid)
    h += filtros
    h += acciones
    h += "</div>"
    h += ('<div class="tabla-scroll"><table class="tabla" id="adm-%s">%s'
          "<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>"
          % (tid, cap, cab, body))
    h += ('<div data-vacio hidden>%s</div>'
          % estado_vacio("Sin resultados",
                         "No hay registros que coincidan con los filtros actuales.",
                         "", "checklist"))
    h += paginas(1, por_pagina, len(filas), tam=por_pagina, tabla_id=tid)
    h += extra
    h += "</div>"
    return h


def _fmt_fecha(iso):
    """Convierte 2024-11-12 a '12 nov 2024' para mostrar en tabla/cancelacion."""
    try:
        anio, mes, dia = iso.split("-")
        return "%d %s %s" % (int(dia), _MESES[int(mes) - 1], anio)
    except (ValueError, AttributeError):
        return iso


def _b(icono, etiqueta, accion=""):
    """Botón de fila. Con accion explicita emite ese data-accion; sin ella
    cae en el mapa ICONO_ACCION (evita que 'Seleccionar' dispare 'aprobar')."""
    if accion:
        return ('<button data-accion="%s" title="%s" aria-label="%s">%s</button>'
                % (accion, etiqueta, etiqueta, ico(icono, 16)))
    return boton_accion(icono, etiqueta)


def _acc(*items):
    return '<div class="acciones-cell">%s</div>' % "".join(items)


def _nuevo(accion, etiqueta):
    """Botón primario de alta para la cabecera de una tarjeta."""
    return ('<button class="btn btn-primario btn-sm" data-accion="%s">%s %s</button>'
            % (accion, ico("plus", 16), etiqueta))


def _nuevo_link(href, etiqueta, clase="btn btn-primario btn-sm"):
    """Alta que abre una vista propia (no un modal)."""
    return ('<a class="%s" href="%s">%s %s</a>'
            % (clase, href, ico("plus", 16), etiqueta))


def _ver_link(href, etiqueta="Ver detalle", icono="doc"):
    """Acción de fila que abre la vista completa del registro."""
    return ('<a class="table-act" href="%s" title="%s" aria-label="%s">%s</a>'
            % (href, etiqueta, etiqueta, ico(icono, 16)))


def _editar_link(href, etiqueta, icono="edit"):
    return ('<a class="table-act" href="%s" title="%s" aria-label="%s">%s</a>'
            % (href, etiqueta, etiqueta, ico(icono, 16)))


def _solic(accion, icono, etiqueta):
    """Botón de acción de la bandeja de solicitudes (Aprobar/Rechazar)."""
    return ('<button data-accion="%s" title="%s" aria-label="%s">%s</button>'
            % (accion, etiqueta, etiqueta, ico(icono, 16)))


def _detalle(tipo, etiqueta="Ver detalle", href=""):
    """Acción de detalle: enlace a la vista propia o botón del panel interno."""
    if href:
        return _ver_link(href, etiqueta)
    return ('<button class="table-act" data-adm-accion="%s" title="%s" '
            'aria-label="%s">%s</button>' % (tipo, etiqueta, etiqueta, ico("eye", 16)))


def _check(etiqueta, activo=False):
    """Casilla de verificacion (usa la clase .chk del kit)."""
    return ('<label class="chk"><input type="checkbox"%s> %s</label>'
            % (" checked" if activo else "", etiqueta))


def _revisar(cod, emp, estu, sector, tipo, etapa, docente):
    """Botón por fila para abrir la revisión de un emprendimiento (datos en dataset)."""
    return ('<button data-accion="revisar-emprendimiento" title="Revisar" aria-label="Revisar" '
            'data-emp="%s" data-cod="%s" data-estu="%s" data-sector="%s" data-tipo="%s" '
            'data-etapa="%s" data-docente="%s">%s</button>'
            % (emp, cod, estu, sector, tipo, etapa, docente, ico("check", 16)))


def _sel_estado(cod, nombre, estado):
    """Selector de estado de acceso por fila (Activo/Limitado/Inactivo).
    data-filtro='off' evita que el buscador/filtros de tabla lo tomen como filtro."""
    opciones = "".join('<option%s>%s</option>' % (" selected" if o == estado else "", o)
                       for o in ("Activo", "Limitado", "Inactivo"))
    return ('<select class="sel-estado" data-filtro="off" data-cod="%s" data-nombre="%s" '
            'aria-label="Estado de la cuenta de %s">%s</select>'
            % (cod, nombre, nombre, opciones))


def _asesoria(accion, icono, etiqueta, cod="", estu="", doc="", fecha="", hora="",
              tema="", mod="", est=""):
    """Botón por fila del programa de asesorías; los datos opcionales viajan en
    data-* para prefill del modal de edición o para el mensaje de cancelacion."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("cod", cod), ("estu", estu), ("doc", doc), ("fecha", fecha),
        ("hora", hora), ("tema", tema), ("mod", mod), ("estado", est)) if v)
    return ('<button data-accion="%s"%s title="%s" aria-label="%s">%s</button>'
            % (accion, extra, etiqueta, etiqueta, ico(icono, 16)))


def _evento(accion, icono, etiqueta, titulo="", fecha="", lugar="",
            confirmados="", sector="", primario=False):
    """Botón de aprobación/rechazo de eventos pendientes (A03); los datos del
    evento viajan en data-* para armar la ficha del modal de aprobación."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("titulo", titulo), ("fecha", fecha), ("lugar", lugar),
        ("confirmados", confirmados), ("sector", sector)) if v)
    cls = "btn-primario" if primario else "btn-secundario"
    return ('<button class="btn btn-sm %s" data-accion="%s"%s title="%s" '
            'aria-label="%s">%s</button>'
            % (cls, accion, extra, etiqueta, etiqueta, ico(icono, 14)))


def _barra(pct):
    """A30: sin hex inline; min-width y el estilo del porcentaje viven en
    .barra-celda / .barra-pct (lib_css). El ancho de la barra es dato (%)."""
    return ('<div class="barra barra-celda"><span style="width:%d%%"></span></div>'
            '<span class="barra-pct">%d%%</span>' % (pct, pct))


def _sel(etiqueta, opciones, extra=""):
    """Select de filtro de tabla. Emite data-filtro para que el JS lo escuche;
    la primera opción ('Todos/Todas...') va con value='' para no filtrar."""
    primero, resto = opciones[0], opciones[1:]
    pops = '<option value="">%s</option>' % primero + "".join(
        "<option>%s</option>" % o for o in resto)
    return '<select class="filtro" data-filtro="%s" aria-label="%s" %s>%s</select>' % (
        _slug(etiqueta), etiqueta, extra, pops)


def _slug(txt):
    """Versión Python del slug JS (para data-filtro)."""
    s = "".join(ch for ch in unicodedata.normalize("NFD", txt)
                if unicodedata.category(ch) != "Mn")
    return "-".join(s.lower().split())


def data_filtro_col(col):
    """Acota un filtro a la columna (indice 0-based) de la tabla."""
    return 'data-filtro-col="%d"' % col


def _js_admin():
    return ADMIN_JS


# Datos que el JS del admin necesita en el ambito global: el kit compartido
# usa CORREOS_EST al asignar docente y aqui no existe (vive en Python), asi que
# se publica en la pagina del admin. Se agregan tambien las variantes sin
# tildes porque algunas bandejas escriben el nombre asi.
CORREOS_EST_JS = {}
for _nombre, _correo in CORREOS_EST.items():
    CORREOS_EST_JS[_nombre] = _correo
    CORREOS_EST_JS[_sin_tildes(_nombre)] = _correo

# [codigo, nombre, correo] de cada docente registrado, para el selector del
# modal de asignar/reasignar docente.
ADMIN_DOCENTES = [[d[0], d[1], d[2]] for d in DOCENTES]


def _inyectar(html):
    """Inyecta el JS propio del administrador (tablas, fichas, calendario) y los
    datos globales que el kit compartido espera."""
    if "</body>" in html:
        js = ("window.CORREOS_EST = %s;\nwindow.ADMIN_DOCENTES = %s;\n"
              % (json.dumps(CORREOS_EST_JS, ensure_ascii=False),
                 json.dumps(ADMIN_DOCENTES, ensure_ascii=False)))
        js += _js_admin()
        html = ("<script>" + js + "</script>\n</body>").join(
            html.rsplit("</body>", 1))
    return html


def _envolver(fn):
    def _render():
        return _inyectar(fn())
    return _render


def _btn(icono, texto, href="#", clase="btn btn-primario"):
    return '<a class="%s" href="%s">%s %s</a>' % (clase, href, ico(icono, 16), texto)


def _exportar(etiqueta, clase="btn btn-secundario"):
    """Botón de exportación real (A27): dispara el caso JS 'exportar' (CSV de la
    tabla o, si no hay tabla, resumen de métricas) en vez de navegar a reportes."""
    return ('<button class="%s" data-accion="exportar">%s %s</button>'
            % (clase, ico("download", 16), etiqueta))


def _emp(accion, icono, etiqueta, cod="", emp="", estu="", sector="", tipo="",
         etapa="", avance="", docente=""):
    """Botón por fila del registro de emprendimientos; los datos viajan en
    data-* para el prefill del modal de edición (A07)."""
    extra = "".join(' data-%s="%s"' % (k, v) for k, v in (
        ("cod", cod), ("emp", emp), ("estu", estu), ("sector", sector),
        ("tipo", tipo), ("etapa", etapa), ("avance", avance),
        ("doc", docente)) if v)
    return ('<button data-accion="%s"%s title="%s" aria-label="%s">%s</button>'
            % (accion, extra, etiqueta, etiqueta, ico(icono, 16)))


def _coment(autor, rol, ini, fecha, txt):
    """Comentario con avatar, autor, rol y fecha (C13)."""
    return ('<div class="coment"><span class="avatar">%s</span>'
            '<div style="flex:1;min-width:0">'
            '<div class="coment-cab"><b>%s</b><span class="who-role">%s</span>'
            "<time>%s</time></div>"
            '<div class="coment-txt">%s</div></div></div>'
            % (ini, autor, rol, fecha, txt))


def _tabla_t(cabeceras, filas, titulo):
    """Tabla con caption oculto para lectores de pantalla (C6)."""
    return tabla(cabeceras, filas, caption=titulo)


def _drop():
    """Zona de adjuntos .drop (C3): mismo marcado y ids que tarea-detalle.

    lib_js cuelga el input #evidencia-real; el contador y la lista usan los
    mismos ids del flujo estudiante para que el kit funcione sin cambios."""
    return ('<label class="drop" for="evidencia-real">%s'
            '<b class="drop-tit">Arrastra tus '
            'archivos aquí o haz clic para seleccionarlos</b>'
            '<span class="drop-nota">Formatos admitidos: JPG, PNG o PDF '
            '&middot; Máximo 10 MB</span>'
            '<input type="file" id="evidencia-real" multiple '
            'accept=".jpg,.jpeg,.png,.pdf" aria-label="Seleccionar archivos" '
            'style="display:none"></label>' % ico("upload", 34))


def _vacio(fuente, titulo, txt, icono="doc"):
    """Estado vacio enlazado a su lista (hallazgo MEDIO P6-P10).

    fuente: selector CSS de los items dentro del mismo contenedor (.card,
    .tabla-envoltura o [data-vacio-lista]). Arranca oculto y lib_js lo
    muestra cuando la lista queda sin items visibles."""
    return ('<div data-vacio data-vacio-fuente="%s" hidden>%s</div>'
            % (fuente, estado_vacio(titulo, txt, "", icono)))


# --- 33. Dashboard -----------------------------------------------------------

def dashboard():
    """Inicio del admin: panorama con los datos reales del programa.

    El grafico de sede trae dos vistas (barras y anillo) que se alternan con
    el interruptor de la tarjeta; el cambio lo lleva ADMIN_JS."""
    por_sede = [(s, sum(1 for e in EMPRENDIMIENTOS if e[10] == s)) for s in SEDES]
    por_sector = []
    for s in ["Alimentos", "Moda", "Ambiental", "Tecnología", "Muebles"]:
        n = sum(1 for e in EMPRENDIMIENTOS if e[4] == s)
        if n:
            por_sector.append((s, n))
    activos = sum(1 for d in DOCENTES if d[6] == "Activo")
    prom = round(sum(e[7] for e in EMPRENDIMIENTOS) / float(len(EMPRENDIMIENTOS)))
    cuerpo = metricas([
        ("users", "Usuarios activos", str(activos + len(ESTUDIANTES)), "", 84, "+12 este mes"),
        ("maleta", "Emprendimientos", str(len(EMPRENDIMIENTOS)), "", 72, "+5"),
        ("trend", "Tareas del programa", str(len(TAREAS_ADM)), "", 88, "+14"),
        ("medalla", "Avance promedio", str(prom), "%", prom, "+3"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Avance de fase por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [12, 19, 27, 41, 61],
        unidad=" avances"))
    cuerpo += card("Emprendimientos por sede",
                   '<div data-grafico-vista="barras">%s</div>'
                   '<div data-grafico-vista="anillo" hidden>%s</div>'
                   % (barras("", "", [s.replace("Sede ", "") for s, _ in por_sede],
                             [n for _, n in por_sede], unidad=" ventures", alto=200),
                      donut("", "", [(s, n, AZUL) for s, n in por_sede],
                            "emprendimientos")),
                   accion=('<div class="acciones" role="group" aria-label="Tipo de gráfico">'
                           '<button class="btn btn-sm btn-acento" data-adm-grafico="barras">Barras</button>'
                           '<button class="btn btn-sm btn-secundario" data-adm-grafico="anillo">Anillo</button>'
                           '</div>'))
    cuerpo += card("Emprendimientos por sector", barras_h(
        "", "", [s for s, _ in por_sector], [n for _, n in por_sector], color=AMAR))
    cuerpo += card("Actividad reciente (Agenda)", agenda([
        ("12 nov 2024, 08:30 – Asesoría", [("08:30", "EcoPack - Carlos Mendoza", "", "")]),
        ("12 nov 2024, 11:00 – Evento", [("11:00", "Taller de costos - Confirmado", "", "")]),
        ("11 nov 2024, 15:00 – Comentario", [("15:00", "Pendiente de moderación", "", "")]),
    ]) + _vacio(".ag-ev", "Sin actividad programada",
                "Cuando haya asesorías, eventos o comentarios pendientes "
                "aparecerán aquí con su fecha y hora.", "calendar"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Calendario", calendario("noviembre", 2024, hoy=12, marcados=(18, 22),
                                       eventos={18: ("Taller de costos y precios",
                                                  "Auditorio A – 32 de 40 cupos – Publicado"),
                                              22: ("Feria de emprendedores",
                                                  "Plaza central – 86 de 120 cupos – Publicado")}))
    cuerpo += card("Pendientes de decisión", lista_def([
        ("<a href='asignaciones.html'>Emprendimientos sin docente</a>",
         str(sum(1 for e in EMPRENDIMIENTOS if e[8] == "Sin asignar"))),
        ("<a href='eventos.html'>Eventos por aprobar</a>", "1"),
        ("<a href='diagnosticos.html'>Diagnósticos sin revisar</a>", "5"),
    ]))
    cuerpo += card("Distribución de usuarios", donut(
        "", "", [("Docentes", len(DOCENTES), AZUL),
                 ("Estudiantes", len(ESTUDIANTES), AMAR)], "usuarios"))
    cuerpo += "</div></div>"
    cuerpo = formulario("dashboard", cuerpo)
    return shell(R, "dashboard", "Inicio", cuerpo,
                 migas=["Inicio"],
                 sub="Panorama institucional de usuarios, emprendimientos y seguimiento.",
                 extra_head=ADMIN_CSS,
                 acciones=_btn("download", "Exportar reportes", "reportes.html"))
# --- 34. Gestión de perfiles -------------------------------------------------
def usuarios():
    """Gestión de perfiles: docentes y estudiantes en tablas propias.

    Cada tabla tiene su buscador, sus filtros y su paginacion: el kit
    compartido solo resuelve una tabla por pagina, asi que aqui cada zona
    la lleva el controlador del admin (ADMIN_JS)."""
    filas_doc = []
    for cod, nom, correo, area, carga, emp, estado in DOCENTES:
        filas_doc.append({
            "attrs": {"doc-id": cod, "doc-cod": cod, "doc-nombre": nom, "doc-correo": correo,
                      "doc-area": area, "doc-carga": carga,
                      "doc-emp": emp, "doc-estado": estado},
            "celdas": [
                "<b>%s</b>" % cod, "<b>%s</b>" % nom, correo, area,
                carga, emp,
                (_sel_estado(cod, nom, estado), estado),
                _acc(_ficha("docente"),
                     _ver_link("usuario-detalle.html?cod=%s" % cod),
                     _editar_link("usuario-docente.html?cod=%s" % cod, "Editar docente"),
                     '<button data-accion="dar-de-baja" title="Dar de baja" '
                     'aria-label="Dar de baja a %s">%s</button>' % (nom, ico("trash", 16))),
            ],
        })
    filas_est = []
    for cod, nom, sec, emp, et, av, est in ESTUDIANTES:
        filas_est.append({
            "attrs": {"est-id": cod, "est-nombre": nom,
                      "est-correo": CORREOS_EST.get(nom, ""), "est-sector": sec,
                      "est-emp": emp, "est-etapa": et, "est-sede": SEDE_EST.get(nom, ""),
                      "est-avance": "%d%%" % av, "est-estado": est},
            "celdas": [
                "<b>%s</b>" % cod, "<b>%s</b>" % nom, CORREOS_EST.get(nom, ""),
                sec, emp, badge(et, "b-linea"), _barra(av),
                (_sel_estado(cod, nom, est), est),
                _acc(_ficha("estudiante"),
                     _ver_link("usuario-detalle.html?cod=%s" % cod),
                     _editar_link("usuario-estudiante.html?cod=%s" % cod,
                                  "Editar estudiante"),
                     '<button data-accion="dar-de-baja" title="Dar de baja" '
                     'aria-label="Dar de baja a %s">%s</button>' % (nom, ico("trash", 16))),
            ],
        })
    cuerpo = callout("Los perfiles de estudiante se editan desde su cuenta. El "
                     "administrador solo puede cambiar el estado de acceso (Activo, "
                     "Limitado o Inactivo).", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("users", "Docentes", str(len(DOCENTES)), "", 45, "+1"),
        ("users", "Estudiantes", str(len(ESTUDIANTES)), "", 92, "+11"),
        ("alerta", "Cuentas inactivas", "4", "", 12, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "docentes", "Docentes",
        ["Código", "Nombre", "Correo institucional", "Área", "Carga semanal",
         "Emprendimientos", "Estado", "@ACC"], filas_doc,
        sub="Docentes registrados en el programa y su carga asignada.",
        caption="Docentes registrados en el programa",
        filtros=(_adm_filtro("docentes", "Todas las áreas",
                             ["Todas las áreas", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("docentes", "Todos los estados",
                               ["Todos los estados", "Activo", "Limitado", "Inactivo"], 6)),
        acciones=_nuevo_link("usuario-nuevo.html?tipo=docente", "Nuevo docente"))
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "estudiantes", "Estudiantes",
        ["ID de estudiante", "Nombre", "Correo institucional", "Sector",
         "Emprendimiento", "Etapa", "Avance", "Estado", "@ACC"], filas_est,
        sub="Estudiantes vinculados a un emprendimiento del programa.",
        caption="Estudiantes registrados en el programa",
        filtros=(_adm_filtro("estudiantes", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("estudiantes", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 5)
                 + _adm_filtro("estudiantes", "Todos los estados",
                               ["Todos los estados", "Activo", "Limitado", "Inactivo"], 7)),
        acciones=_nuevo_link("usuario-nuevo.html?tipo=estudiante", "Nuevo estudiante"))
    cuerpo = formulario("perfiles", cuerpo)
    return shell(R, "usuarios", "Gestión de perfiles", cuerpo,
                 migas=["Inicio", "Gestión de perfiles"],
                 sub="Altas, edición y estado de acceso de docentes y estudiantes.",
                 extra_head=ADMIN_CSS)


# --- 35. Vistas de usuario: detalle, edición y alta --------------------------
def usuario_detalle():
    """Ficha completa de un docente o estudiante (usuario-detalle.html?cod=)."""
    cuerpo = metricas([
        ("users", "Rol", '<span data-campo="tipo">docente</span>', "", 60,
         "Perfil del programa"),
        ("check", "Estado", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="estado">Activo</span></span>', "", 100,
         "Acceso al sistema"),
        ("reloj", "Último acceso", '<span data-campo="ultimo_acceso">Hoy, 07:42</span>',
         "", 60, '<span data-campo="registro">12 mar 2024</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos personales", lista_def([
        ("Código", '<b data-campo="codigo">DOC-014</b>'),
        ("Nombre completo", '<b data-campo="nombre">Carlos Mendoza</b>'),
        ("Correo institucional", '<span data-campo="correo">carlos.mendoza@sgemd.edu.co</span>'),
        ("Teléfono", '<span data-campo="telefono">+57 300 555 0142</span>'),
        ("Fecha de registro", '<span data-campo="registro">12 mar 2024</span>'),
        ("Último acceso", '<span data-campo="ultimo_acceso">Hoy, 07:42</span>'),
    ]))
    cuerpo += card("Información del programa", lista_def([
        ("Tipo de perfil", '<span data-campo="tipo">docente</span>'),
        ("Área o sector", '<span data-campo="area_txt">Alimentos</span>'),
        ("Carga o etapa", '<span data-campo="carga_txt">3 h</span>'),
        ("Emprendimiento(s)", '<span data-campo="emp_txt">8</span>'),
        ("Avance", '<span data-campo="avance_txt">—</span>'),
        ("Sede", '<span data-campo="sede_txt">—</span>'),
    ]))
    cuerpo += card("Nota del administrador",
                   '<p class="suave" data-campo="nota">Docente de acompañamiento '
                   'del programa.</p>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" data-enlace="editar_url" '
                   'href="usuario-docente.html">%s Editar perfil</a>'
                   '<a class="btn btn-secundario" href="usuarios.html">%s Volver a '
                   'gestión de perfiles</a>'
                   '<button class="btn btn-secundario" data-accion="dar-de-baja">'
                   '%s Dar de baja</button></div>'
                   % (ico("edit", 16), ico("izq", 16), ico("trash", 16)))
    cuerpo += card("Trazabilidad", lista_def([
        ("Creado por", "Administración del programa"),
        ("Cambios recientes", "Actualización de estado de acceso"),
        ("Notificaciones", "Correo institucional"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(USUARIOS_DET, "cod", "DOC-014")
    return shell(R, "usuarios", "Detalle del usuario", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Detalle del usuario"],
                 sub="Consulta la ficha completa del docente o estudiante.",
                 acciones=_volver("usuarios.html", "Volver"))


def _usuario_form(tipo):
    """Formulario editable de docente o estudiante, con los datos precargados."""
    es_doc = tipo == "docente"
    cuerpo = callout(
        ("El docente recibe un correo de activación en su cuenta institucional."
         if es_doc else
         "El estudiante edita sus datos personales. El administrador gestiona "
         "el estado de acceso y la información académica."), "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del %s" % tipo,
                   campo("Código", name="codigo",
                         bloqueo="Código asignado por el sistema")
                   + campo("Nombres", req=True, name="nombres")
                   + campo("Apellidos", req=True, name="apellidos")
                   + campo("Correo institucional", tipo="email", req=True,
                           name="correo",
                           ayuda="Debe ser una cuenta @sgemd.edu.co")
                   + campo("Teléfono", tipo="tel", name="telefono"))
    if es_doc:
        cuerpo += card("Área y carga",
                       select("Área de conocimiento",
                              ["Alimentos", "Moda", "Ambiental", "Tecnología",
                               "Muebles"], req=True, name="area")
                       + campo("Horas de asesoría por semana", tipo="number",
                               name="carga", ph="De 1 a 20")
                       + campo("Emprendimientos asignados", tipo="number",
                               name="emprendimientos",
                               bloqueo="Se actualiza desde Asignaciones"))
    else:
        cuerpo += card("Emprendimiento y etapa",
                       campo("Emprendimiento", name="emprendimiento")
                       + select("Sector", ["Alimentos", "Moda", "Ambiental",
                                           "Tecnología", "Muebles"], req=True,
                                name="sector")
                       + select("Etapa", ETAPAS, req=True, name="etapa"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso",
                   select("Estado de la cuenta", ["Activo", "Limitado", "Inactivo"],
                          req=True, name="estado")
                   + '<div class="ayuda">%s Limitado deja la cuenta creada pero '
                     'sin acceso hasta que la habilites.</div>' % ico("alerta", 13))
    cuerpo += card("Actividad", lista_def([
        ("Último acceso", '<span data-campo="ultimo_acceso">Hoy, 07:42</span>'),
        ("Fecha de registro", '<span data-campo="registro">12 mar 2024</span>'),
        ("Sede", '<span data-campo="sede_txt">Sede Norte</span>'),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-perfil">'
                   '%s Guardar cambios</button>'
                   '<a class="btn btn-secundario" href="usuario-detalle.html?cod=">'
                   '%s Ver ficha</a>'
                   '<a class="btn btn-secundario" href="usuarios.html">%s Cancelar</a>'
                   '</div>' % (ico("check", 16), ico("eye", 16), ico("x", 16)))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(USUARIOS_DET, "cod",
                             "DOC-014" if es_doc else "912646")
    return cuerpo


def usuario_docente():
    cuerpo = _usuario_form("docente")
    return shell(R, "usuarios", "Editar docente", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Editar docente"],
                 sub="Actualiza los datos y la carga del docente.",
                 acciones=_volver("usuarios.html", "Volver"))


def usuario_estudiante():
    cuerpo = _usuario_form("estudiante")
    return shell(R, "usuarios", "Editar estudiante", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Editar estudiante"],
                 sub="Actualiza el estado de acceso y los datos académicos.",
                 acciones=_volver("usuarios.html", "Volver"))


def usuario_nuevo():
    """Alta de docente o estudiante (usuario-nuevo.html?tipo=docente|estudiante)."""
    cuerpo = callout("El nuevo usuario recibirá un correo de activación en su "
                     "cuenta institucional para definir su contraseña.", "mail")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del nuevo usuario",
                   campo("Nombres", req=True, name="nombres")
                   + campo("Apellidos", req=True, name="apellidos")
                   + campo("Correo institucional", tipo="email", req=True,
                           name="correo",
                           ayuda="Debe ser una cuenta @sgemd.edu.co")
                   + campo("Teléfono", tipo="tel", name="telefono"))
    cuerpo += card("Perfil y programa",
                   select("Tipo de perfil", ["Docente", "Estudiante"], req=True,
                          valor="Docente")
                   + select("Sector o área", ["Alimentos", "Moda", "Ambiental",
                                              "Tecnología", "Muebles"], req=True,
                            valor="Alimentos")
                   + campo("Nombre del emprendimiento", ph="Ej.: Sabor y Sabe")
                   + select("Etapa", ETAPAS, req=True, valor="FASE 1 - Ideación"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado del acceso",
                   select("Estado de la cuenta", ["Activo", "Limitado"],
                          req=True, valor="Activo")
                   + '<div class="ayuda">%s Limitado deja la cuenta creada pero '
                     'sin acceso hasta que la habilites.</div>' % ico("alerta", 13))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-perfil">'
                   '%s Crear usuario</button>'
                   '<a class="btn btn-secundario" href="usuarios.html">%s Cancelar</a>'
                   '</div>' % (ico("check", 16), ico("x", 16)))
    cuerpo += "</div></div>"
    return cuerpo


def usuario_nuevo_vista():
    cuerpo = usuario_nuevo()
    return shell(R, "usuarios", "Nuevo usuario", cuerpo,
                 migas=["Inicio", "Gestión de perfiles", "Nuevo usuario"],
                 sub="Registra un docente o estudiante en el programa.",
                 acciones=_volver("usuarios.html", "Volver"))


# --- 35. Solicitudes pendientes (bandeja del Admin) --------------------------
def _cuerpo_desb():
    filas = []
    for i, (c, n, r, m, f) in enumerate(SOLIC_DESBLOQUEOS, 1):
        filas.append({
            "attrs": {"sol-id": c, "sol-nombre": n, "sol-tipo": r,
                      "sol-detalle": m, "sol-fecha": f,
                      "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % c, "<b>%s</b>" % n, badge(r, "b-linea"), m, f,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle",
                              "solicitud-detalle.html?clave=SOL-D%02d" % i))],
        })
    return _tabla_adm(
        "desbloqueos", "Desbloqueos de cuenta",
        ["Código", "Nombre", "Rol", "Motivo de la solicitud", "Fecha", "@ACC"],
        filas, sub="Cuentas bloqueadas o inactivas que esperan una decisión.",
        caption="Solicitudes de desbloqueo de cuenta",
        por_pagina=5)


def _cuerpo_par():
    filas = []
    for i, (c, n, emp, nu, s, f) in enumerate(SOLIC_PARALELOS, 1):
        filas.append({
            "attrs": {"sol-id": c, "sol-nombre": n, "sol-tipo": "Emprendimiento paralelo",
                      "sol-detalle": "Pasa de %s a %s (sector %s)." % (emp, nu, s),
                      "sol-fecha": f, "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % c, "<b>%s</b>" % n, emp, "<b>%s</b>" % nu, s, f,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle",
                              "solicitud-detalle.html?clave=SOL-P%02d" % i))],
        })
    return _tabla_adm(
        "paralelos", "Emprendimientos en paralelo",
        ["ID de estudiante", "Estudiante", "Emprendimiento actual",
         "Nuevo emprendimiento", "Sector", "Fecha", "@ACC"], filas,
        sub="Estudiantes que quieren registrar un segundo emprendimiento.",
        caption="Solicitudes de emprendimiento en paralelo",
        por_pagina=5)


def _cuerpo_cit():
    filas = []
    for i, (n, e, d, f, m) in enumerate(SOLIC_CITAS, 1):
        cid = _id_estudiante(n)
        filas.append({
            "attrs": {"sol-id": cid, "sol-nombre": n,
                      "sol-tipo": "Cita de asesoria",
                      "sol-detalle": "%s, docente sugerido: %s." % (m, d),
                      "sol-fecha": f, "sol-correo": CORREOS_EST.get(n, "")},
            "celdas": [
                "<b>%s</b>" % cid, "<b>%s</b>" % n, e, d, f, m,
                _acc(_solic("solicitud-aprobar", "check", "Aprobar"),
                     _solic("solicitud-rechazar", "x", "Rechazar"),
                     _detalle("solicitud", "Ver detalle",
                              "solicitud-detalle.html?clave=SOL-C%02d" % i))],
        })
    return _tabla_adm(
        "citas", "Citas de asesoria",
        ["ID de estudiante", "Estudiante", "Emprendimiento", "Docente sugerido",
         "Fecha propuesta", "Motivo", "@ACC"], filas,
        sub="Citas de asesoria propuestas por los estudiantes.",
        caption="Solicitudes de cita de asesoria",
        por_pagina=5)


def solicitudes():
    """Bandeja unica del Admin: desbloqueos de cuenta, paralelos y citas.

    Cada bandeja es una tabla propia del admin (buscador, filtros y
    paginacion) y el boton de detalle abre el panel con la descripcion
    completa de la solicitud."""
    paneles = [
        ("Desbloqueos (%d)" % len(SOLIC_DESBLOQUEOS), "tab-desb", _cuerpo_desb()),
        ("Paralelos (%d)" % len(SOLIC_PARALELOS), "tab-par", _cuerpo_par()),
        ("Citas (%d)" % len(SOLIC_CITAS), "tab-cit", _cuerpo_cit()),
    ]
    cuerpo = callout(
        "Aprueba o rechaza las solicitudes pendientes. Al aprobar, el sistema aplica "
        "el cambio y notifica al solicitante; al rechazar, se solicita un motivo.",
        "checklist")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("lock", "Desbloqueos", str(len(SOLIC_DESBLOQUEOS)), "", 35, None),
        ("maleta", "Paralelos", str(len(SOLIC_PARALELOS)), "", 25, None),
        ("calendar", "Citas de asesoria", str(len(SOLIC_CITAS)), "", 20, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += tabs_paneles([(n, pid) for n, pid, _ in paneles])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += "".join(
        '<div data-panel-nombre="%s"%s>%s</div>' % (pid, "" if i == 0 else " hidden", b)
        for i, (_, pid, b) in enumerate(paneles)
    )
    cuerpo = formulario("solicitudes", cuerpo)
    return shell(R, "solicitudes", "Solicitudes pendientes", cuerpo,
                 migas=["Inicio", "Solicitudes pendientes"],
                 sub="Bandeja de desbloqueos de cuenta, solicitudes de paralelo y citas de asesoria.",
                 extra_head=ADMIN_CSS)


def solicitud_detalle():
    """Vista propia de una solicitud (solicitud-detalle.html?clave=SOL-D01)."""
    cuerpo = steps(["Solicitud recibida", "Revisión del administrador",
                    "Decisión", "Notificación"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += metricas([
        ("doc", "Tipo", '<span data-campo="tipo">Desbloqueo de cuenta</span>', "", 60,
         "Solicitud del programa"),
        ("calendar", "Fecha", '<span data-campo="fecha">05 nov 2024</span>', "", 60,
         '<span data-campo="rol">Estudiante</span>'),
        ("users", "Solicitante", '<span data-campo="solicitante">Andres Felipe</span>',
         "", 100, '<span data-campo="correo">andres.felipe@sgemd.edu.co</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la solicitud", lista_def([
        ("Código de la solicitud", '<b data-campo="id">SOL-D01</b>'),
        ("Tipo", '<span data-campo="tipo">Desbloqueo de cuenta</span>'),
        ("Código del solicitante", '<span data-campo="codigo">912650</span>'),
        ("Solicitante", '<b data-campo="solicitante">Andres Felipe</b>'),
        ("Rol", '<span data-campo="rol">Estudiante</span>'),
        ("Correo institucional", '<span data-campo="correo">andres.felipe@sgemd.edu.co</span>'),
        ("Fecha de la solicitud", '<span data-campo="fecha">05 nov 2024</span>'),
        ("Estado", '<span class="badge b-amarillo">Pendiente</span>'),
    ]))
    cuerpo += card("Motivo y contexto",
                   '<div class="def-row"><dt>Motivo</dt><dd><b data-campo="motivo">'
                   'Cuenta inactiva por 90 días sin acceso</b></dd></div>'
                   '<div class="divisor"></div>'
                   '<p class="suave" data-campo="detalle">La cuenta está bloqueada o '
                   'inactiva. Al aprobar, el sistema restablece el acceso con el '
                   'estado Activo y registra la decisión en la bitácora.</p>')
    cuerpo += card("Decisión sugerida",
                   '<div class="callout">%s<div data-campo="accion">Reactivar la '
                   'cuenta y notificar al solicitante.</div></div>'
                   % ico("bombilla", 18))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones", '<div class="acciones-col">'
                   '<button class="btn btn-primario" data-accion="solicitud-aprobar">'
                   '%s Aprobar solicitud</button>'
                   '<button class="btn btn-secundario" data-accion="solicitud-rechazar">'
                   '%s Rechazar con motivo</button>'
                   '<a class="btn btn-secundario" href="solicitudes.html">%s Volver a '
                   'solicitudes</a></div>'
                   % (ico("check", 16), ico("x", 16), ico("izq", 16)))
    cuerpo += card("Trazabilidad", lista_def([
        ("Solicitud registrada", "05 nov 2024, 08:14"),
        ("Última actualización", "05 nov 2024, 08:14"),
        ("Canal", "Portal del estudiante"),
        ("Responsable", "Administración del programa"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(SOLICITUDES_DET, "clave", "SOL-D01")
    return shell(R, "solicitudes", "Detalle de la solicitud", cuerpo,
                 migas=["Inicio", "Solicitudes pendientes", "Detalle de la solicitud"],
                 sub="Revisa el contexto completo antes de tomar una decisión.",
                 acciones=_volver("solicitudes.html", "Volver"))


# --- 37. Emprendimientos -----------------------------------------------------
def emprendimientos():
    """Registro maestro del admin: la tabla canonica, con buscador, filtros
    por columna, paginacion propia y ficha de cada entrepreneurial."""
    cuerpo = callout("Como administrador tu ves <b>todos</b> los emprendimientos, "
                     "tengan o no docente asignado.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += metricas([
        ("maleta", "Total", str(len(EMPRENDIMIENTOS)), "", 72, "+5"),
        ("trend", "En fase 3 o 4", "18", "", 62, None),
        ("alerta", "Sin docente", str(sum(1 for e in EMPRENDIMIENTOS
                                          if e[8] == "Sin asignar")), "", 18, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    filas = []
    for cod, emp, estu, correo_est, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS:
        est_id = _id_estudiante(estu)
        filas.append({
            "attrs": {"cod": cod, "emp": emp, "estu": estu,
                      "emp-id": cod, "emp-cod": cod, "emp-nombre": emp, "emp-est-id": est_id,
                      "emp-est-nombre": estu, "emp-est-correo": correo_est,
                      "emp-sector": sector, "emp-tipo": tipo, "emp-etapa": etapa,
                      "emp-avance": "%d%%" % avance, "emp-sede": sede,
                      "emp-docente": docente},
            "celdas": [
                "<b>%s</b>" % emp, cod, est_id, estu, correo_est,
                badge(sector, "b-azul" if sector == "Alimentos" else
                      ("b-linea" if sector == "Ambiental" else "b-neutra")),
                tipo, badge(etapa, "b-linea"), _barra(avance), sede,
                docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
                _acc(_ficha("emprendimiento"),
                     _ver_link("emprendimiento-detalle.html?cod=%s" % cod),
                     _editar_link("emprendimiento-editar.html?cod=%s" % cod,
                                  "Editar emprendimiento")),
            ],
        })
    cuerpo += _tabla_adm(
        "emprendimientos", "Emprendimientos",
        ["Emprendimiento", "Código", "ID de estudiante", "Estudiante",
         "Correo institucional", "Sector", "Tipo", "Etapa", "Avance", "Sede",
         "Docente asignado", "@ACC"], filas,
        sub="Registro maestro de emprendimientos del programa.",
        caption="Emprendimientos registrados en el programa",
        filtros=(_adm_filtro("emprendimientos", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 5)
                 + _adm_filtro("emprendimientos", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 7)
                 + _adm_filtro("emprendimientos", "Todas las sedes",
                               ["Todas las sedes"] + SEDES, 9)))
    cuerpo = formulario("emprendimientos", cuerpo)
    return shell(R, "emprendimientos", "Emprendimientos", cuerpo,
                 migas=["Inicio", "Emprendimientos"],
                 sub="Todos los emprendimientos registrados en el programa.",
                 extra_head=ADMIN_CSS,
                 acciones=_btn("sliders", "Asignar docente",
                               "asignacion-form.html", "btn btn-secundario"))


# --- 37b. Detalle del emprendimiento -----------------------------------------
def emprendimiento_detalle():
    """Ficha completa del emprendimiento (emprendimiento-detalle.html?cod=)."""
    cuerpo = metricas([
        ("trend", "Avance", '<span data-campo="avance">62</span>%', "", 62,
         '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("users", "Docente", '<span data-campo="docente_txt">Carlos Mendoza</span>',
         "", 100, '<span data-campo="correo_doc">carlos.mendoza@sgemd.edu.co</span>'),
        ("maleta", "Sede", '<span data-campo="sede">Sede Norte</span>', "", 60,
         '<span data-campo="sector">Alimentos</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += steps(["Ideación", "Prototipo", "Validación", "Crecimiento"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Código", '<b data-campo="codigo">EMP-041</b>'),
        ("Nombre", '<b data-campo="nombre">Sabor y Sabe</b>'),
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("ID del estudiante", '<span data-campo="est_id">912646</span>'),
        ("Correo del estudiante", '<span data-campo="correo">mariana.lopez@sgemd.edu.co</span>'),
        ("Sector", '<span data-campo="sector">Alimentos</span>'),
        ("Tipo", '<span data-campo="tipo">Comercio</span>'),
        ("Etapa", '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("Sede", '<span data-campo="sede">Sede Norte</span>'),
    ]))
    cuerpo += card("Descripción",
                   '<p class="suave" data-campo="descripcion">Emprendimiento del '
                   'sector Alimentos en la etapa FASE 2 - Prototipo. Acompañado '
                   'por el programa SGEMD.</p>')
    cuerpo += card("Estado del acompañamiento", lista_def([
        ("Docente asignado", '<span data-campo="docente_txt">Carlos Mendoza</span>'),
        ("Correo del docente", '<span data-campo="correo_doc">carlos.mendoza@sgemd.edu.co</span>'),
        ("Estado", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="estado">Al día</span></span>'),
        ("Avance registrado", '<span data-campo="avance">62</span>%'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" data-enlace="editar_url" '
                   'href="emprendimiento-editar.html">%s Editar emprendimiento</a>'
                   '<a class="btn btn-secundario" data-enlace="seguimiento_url" '
                   'href="seguimiento-detalle.html">%s Ver seguimiento</a>'
                   '<a class="btn btn-secundario" data-enlace="avance_url" '
                   'href="avance-form.html">%s Registrar avance</a>'
                   '<a class="btn btn-secundario" data-enlace="asignar_url" '
                   'href="asignacion-form.html">%s Asignar docente</a>'
                   '<a class="btn btn-secundario" data-enlace="diagnostico_url" '
                   'href="diagnostico-detalle.html">%s Ver diagnóstico</a>'
                   '<a class="btn btn-secundario" href="emprendimientos.html">'
                   '%s Volver</a></div>'
                   % (ico("edit", 16), ico("trend", 16), ico("checklist", 16),
                      ico("sliders", 16), ico("clipboard", 16), ico("izq", 16)))
    cuerpo += card("Hitos recientes", linea_tiempo([
        ("12", "nov", "Cierre de prototipo", "Control de calidad del producto",
         '<div class="mt-10">' + badge("En curso", "b-amarillo", "reloj") + "</div>"),
        ("05", "nov", "Revisión con el docente", "Ajustes al modelo de negocio",
         '<div class="mt-10">' + badge("Completado", "b-azul", "check") + "</div>"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EMP_DET, "cod", "EMP-041")
    return shell(R, "emprendimientos", "Detalle del emprendimiento", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Detalle del emprendimiento"],
                 sub="Información completa del emprendimiento y su acompañamiento.",
                 acciones=_volver("emprendimientos.html", "Volver"))


# --- 37c. Editar emprendimiento ----------------------------------------------
def emprendimiento_editar():
    cuerpo = callout("Como administrador puedes actualizar la ficha del "
                     "emprendimiento; el avance y las tareas los registra el "
                     "docente.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del emprendimiento",
                   campo("Emprendimiento", req=True, name="nombre")
                   + campo("Código", name="codigo",
                           bloqueo="Código asignado por el sistema")
                   + campo("Estudiante", name="estudiante",
                           bloqueo="Se cambia desde Gestión de perfiles")
                   + campo("Descripción", alto=True, name="descripcion"))
    cuerpo += card("Clasificación",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + select("Sector", ["Alimentos", "Moda", "Ambiental",
                                       "Tecnología", "Muebles"], req=True,
                            name="sector")
                   + select("Tipo", ["Comercio", "Moda", "Industrial",
                                     "Alimentos", "Artesanal"], req=True,
                            name="tipo")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + select("Etapa", ETAPAS, req=True, name="etapa")
                   + campo("Avance (%)", tipo="number", name="avance")
                   + "</div>"
                   + select("Sede", SEDES, name="sede"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Docente asignado",
                   select("Docente", [d[1] for d in DOCENTES] + ["Sin asignar"],
                          name="docente")
                   + '<p class="nota-foot">La asignación definitiva se gestiona '
                     "desde Asignaciones.</p>")
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-perfil">'
                   '%s Guardar cambios</button>'
                   '<a class="btn btn-secundario" data-enlace="detalle_url" '
                   'href="emprendimiento-detalle.html">%s Ver ficha</a>'
                   '<a class="btn btn-secundario" href="emprendimientos.html">'
                   '%s Cancelar</a></div>'
                   % (ico("check", 16), ico("eye", 16), ico("x", 16)))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EMP_DET, "cod", "EMP-041")
    return shell(R, "emprendimientos", "Editar emprendimiento", cuerpo,
                 migas=["Inicio", "Emprendimientos", "Editar emprendimiento"],
                 sub="Actualiza la ficha y la clasificación del emprendimiento.",
                 acciones=_volver("emprendimientos.html", "Volver"))


def _sem(avance):
    """Semáforo de estado del emprendimiento a partir de su % de avance."""
    if avance == 0:
        return badge("Sin avance", "b-amarillo", "alerta")
    if avance < 60:
        return badge("En riesgo", "b-amarillo", "alerta")
    return badge("Al día", "b-azul", "check")


def seguimiento():
    """Seguimiento de todos los emprendimientos (tabla única del rol admin)."""
    filas = []
    for cod, emp, estu, correo_est, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS:
        est_id = _id_estudiante(estu)
        filas.append({
            "attrs": {"cod": cod, "emp": emp, "estu": estu, "etapa": etapa,
                      "avance": str(avance),
                      "emp-id": cod, "emp-cod": cod, "emp-nombre": emp, "emp-est-id": est_id,
                      "emp-est-nombre": estu, "emp-est-correo": correo_est,
                      "emp-sector": sector, "emp-tipo": tipo, "emp-etapa": etapa,
                      "emp-avance": "%d%%" % avance, "emp-sede": sede,
                      "emp-docente": docente},
            "celdas": [
                cod, "<b>%s</b>" % emp, estu,
                badge(sector, "b-azul" if sector == "Alimentos" else "b-neutra"),
                badge(etapa, "b-linea"),
                docente if docente != "Sin asignar" else badge("Sin asignar", "b-amarillo"),
                _barra(avance), _sem(avance),
                _acc(_ficha("emprendimiento"),
                     _ver_link("seguimiento-detalle.html?cod=%s" % cod),
                     _editar_link("avance-form.html?cod=%s" % cod,
                                  "Registrar avance")),
            ],
        })
    cuerpo = metricas([
        ("trend", "Avance promedio",
         str(round(sum(e[7] for e in EMPRENDIMIENTOS) / float(len(EMPRENDIMIENTOS)))),
         "%", 62, "Promedio del programa"),
        ("check", "Al día", str(sum(1 for e in EMPRENDIMIENTOS if e[7] >= 60)),
         "", 62, "Avance ≥ 60%"),
        ("alerta", "En riesgo",
         str(sum(1 for e in EMPRENDIMIENTOS if e[7] < 60)), "", 30,
         "Avance < 60%"),
        ("users", "Sin docente",
         str(sum(1 for e in EMPRENDIMIENTOS if e[8] == "Sin asignar")), "", 18,
         "Requieren asignación"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += callout("Como administrador ves el <b>seguimiento de todos los "
                      "emprendimientos</b>. Puedes consultar la ficha, el detalle "
                      "completo y registrar un avance.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "seguimiento", "Seguimiento de emprendimientos",
        ["Código", "Emprendimiento", "Estudiante", "Sector", "Etapa",
         "Docente", "Avance", "Estado", "@ACC"], filas,
        sub="Estado y avance de los %d emprendimientos del programa."
            % len(EMPRENDIMIENTOS),
        caption="Seguimiento de emprendimientos",
        filtros=(_adm_filtro("seguimiento", "Todos los sectores",
                             ["Todos los sectores", "Alimentos", "Moda", "Ambiental",
                              "Muebles", "Tecnología"], 3)
                 + _adm_filtro("seguimiento", "Todas las etapas",
                               ["Todas las etapas"] + ETAPAS, 4)
                 + _adm_filtro("seguimiento", "Todos los docentes",
                               ["Todos los docentes"] + [d[1] for d in DOCENTES]
                               + ["Sin asignar"], 5)
                 + _adm_filtro("seguimiento", "Todo el estado",
                               ["Todo el estado", "Al día", "En riesgo", "Sin avance"], 7)),
        acciones=_exportar("Exportar seguimiento"))
    cuerpo = formulario("seguimiento", cuerpo)
    return shell(R, "seguimiento", "Seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento"],
                 sub="Estado y avance de los %d emprendimientos del programa."
                     % len(EMPRENDIMIENTOS),
                 extra_head=ADMIN_CSS,
                 acciones=_btn("grid", "Registrar avance", "avance-form.html",
                               "btn btn-secundario"))


def seguimiento_detalle():
    """Detalle del seguimiento de un emprendimiento (seguimiento-detalle.html?cod=)."""
    cuerpo = metricas([
        ("trend", "Avance", '<span data-campo="avance">62</span>%', "", 62,
         '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("check", "Estado", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="estado">Al día</span></span>', "", 100,
         "Semáforo del programa"),
        ("users", "Docente", '<span data-campo="docente_txt">Carlos Mendoza</span>',
         "", 100, '<span data-campo="correo_doc">carlos.mendoza@sgemd.edu.co</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Plan de trabajo por fase", tabla(
        ["Fase", "Tareas", "Completadas", "Avance", "Estado"],
        [[badge(ETAPAS[0], "b-linea"), "3", "3", "100%", badge("Finalizada", "b-azul")],
         [badge(ETAPAS[1], "b-linea"), "5", "4", "80%", badge("En curso", "b-amarillo")],
         [badge(ETAPAS[2], "b-linea"), "4", "1", "25%", badge("Pendiente", "b-neutra")],
         [badge(ETAPAS[3], "b-linea"), "2", "0", "0%", badge("No iniciada", "b-neutra")]]))
    cuerpo += card("Historial de avances", linea_tiempo([
        ("12", "nov", "Avance al 62%", "Prototipo de empaque validado",
         '<div class="mt-10">' + badge("Registrado", "b-azul", "check") + "</div>"),
        ("05", "nov", "Avance al 55%", "Ajustes al modelo de negocio",
         '<div class="mt-10">' + badge("Registrado", "b-azul", "check") + "</div>"),
        ("28", "oct", "Avance al 41%", "Primer prototipo terminado",
         '<div class="mt-10">' + badge("Registrado", "b-azul", "check") + "</div>"),
    ]))
    cuerpo += card("Datos del emprendimiento", lista_def([
        ("Código", '<b data-campo="codigo">EMP-041</b>'),
        ("Emprendimiento", '<b data-campo="nombre">Sabor y Sabe</b>'),
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("Sector", '<span data-campo="sector">Alimentos</span>'),
        ("Sede", '<span data-campo="sede">Sede Norte</span>'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" data-enlace="avance_url" '
                   'href="avance-form.html">%s Registrar avance</a>'
                   '<a class="btn btn-secundario" data-enlace="detalle_url" '
                   'href="emprendimiento-detalle.html">%s Ver ficha completa</a>'
                   '<a class="btn btn-secundario" href="seguimiento.html">'
                   '%s Volver a seguimiento</a></div>'
                   % (ico("checklist", 16), ico("eye", 16), ico("izq", 16)))
    cuerpo += card("Alertas", lista_def([
        ("Días sin avance", "6"),
        ("Tareas vencidas", "1"),
        ("Última asesoría", "12 nov 2024"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EMP_DET, "cod", "EMP-041")
    return shell(R, "seguimiento", "Detalle del seguimiento", cuerpo,
                 migas=["Inicio", "Seguimiento", "Detalle del seguimiento"],
                 sub="Historial y estado del avance del emprendimiento.",
                 acciones=_volver("seguimiento.html", "Volver"))


def avance_form():
    """Registrar avance de un emprendimiento (avance-form.html?cod=)."""
    cuerpo = steps(["Seleccionar emprendimiento", "Registrar avance",
                    "Notificar al docente"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Emprendimiento",
                   campo("Emprendimiento", name="nombre", bloqueo="No editable")
                   + campo("Estudiante", name="estudiante", bloqueo="No editable")
                   + campo("Docente asignado", name="docente_txt", bloqueo="No editable"))
    cuerpo += card("Nuevo avance",
                   select("Fase", ETAPAS, req=True, name="etapa")
                   + campo("Avance (%)", tipo="number", req=True, name="avance")
                   + campo("Notas del avance", tipo="textarea", name="notas",
                           valor="Prototipo de empaque validado con el grupo focal."))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado actual", lista_def([
        ("Avance registrado", '<span data-campo="avance">62</span>%'),
        ("Etapa", '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("Semáforo", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="estado">Al día</span></span>'),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-avance">'
                   '%s Guardar avance</button>'
                   '<a class="btn btn-secundario" data-enlace="seguimiento_url" '
                   'href="seguimiento-detalle.html">%s Ver seguimiento</a>'
                   '<a class="btn btn-secundario" href="seguimiento.html">'
                   '%s Cancelar</a></div>'
                   % (ico("check", 16), ico("trend", 16), ico("x", 16)))
    cuerpo += card("Nota", '<p class="suave">El avance actualiza el semáforo de '
                   'estado y notifica al docente responsable.</p>')
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EMP_DET, "cod", "EMP-041")
    return shell(R, "seguimiento", "Registrar avance", cuerpo,
                 migas=["Inicio", "Seguimiento", "Registrar avance"],
                 sub="Actualiza el porcentaje de avance y la fase del emprendimiento.",
                 acciones=_volver("seguimiento.html", "Volver"))


# --- 41. Asignar / reasignar docente -----------------------------------------
def asignacion_form():
    """Asignar o reasignar docente a un emprendimiento.

    Se abre desde el botón superior de Asignaciones (alta) o desde la fila
    (reasignación) con ?cod=EMP-...; ambos casos usan la misma vista."""
    cuerpo = steps(["Seleccionar emprendimiento", "Elegir docente",
                    "Confirmar asignación"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Emprendimiento",
                   campo("Emprendimiento", name="nombre", bloqueo="No editable")
                   + campo("Estudiante", name="estudiante", bloqueo="No editable")
                   + campo("Código", name="codigo", bloqueo="No editable")
                   + campo("Sector", name="sector", bloqueo="No editable"))
    cuerpo += card("Docente y carga",
                   select("Docente", [d[1] + " - " + d[3] for d in DOCENTES]
                          + ["Sin asignar"], req=True, name="docente")
                   + campo("Horas semanales", tipo="number", valor="2", req=True,
                           name="horas", ph="De 1 a 20")
                   + campo("Fecha de inicio", tipo="date", name="inicio"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Asignación actual", lista_def([
        ("Docente", '<span data-campo="docente_txt">Sin docente asignado</span>'),
        ("Correo del docente", '<span data-campo="correo_doc">—</span>'),
        ("Etapa", '<span data-campo="etapa">FASE 1 - Ideación</span>'),
        ("Avance", '<span data-campo="avance">15</span>%'),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" '
                   'data-accion="guardar-asignacion-docente">%s Confirmar '
                   'asignación</button>'
                   '<a class="btn btn-secundario" href="asignaciones.html">'
                   '%s Cancelar</a></div>'
                   % (ico("check", 16), ico("x", 16)))
    cuerpo += card("Regla de asignación",
                   '<p class="suave">Verifica que el acta de confidencialidad '
                   'esté aceptada antes de confirmar. Un docente puede tener '
                   'hasta <b>12 emprendimientos</b>.</p>')
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EMP_DET, "cod", "EMP-038")
    return shell(R, "asignaciones", "Asignar docente", cuerpo,
                 migas=["Inicio", "Asignaciones", "Asignar docente"],
                 sub="Asigna o cambia el docente responsable del emprendimiento.",
                 acciones=_volver("asignaciones.html", "Volver"))


# --- 42. Asesorías: dashboard único ------------------------------------------
def asesorias():
    """Dashboard único de asesorías con métricas, gráficos y programación."""
    filas = []
    for c, e, d, f, h, t, m, es in ASESORIAS:
        filas.append([
            "<b>%s</b>" % c, "<b>%s</b>" % e, d,
            "{f} · {h}".format(f=_fmt_fecha(f), h=h), t, m,
            badge(es, BADGE.get(es.lower(), "b-neutra")),
            _acc(_asesoria("ver", "eye", "Ver"),
                 _ver_link("asesoria-detalle.html?cod=%s" % c),
                 _editar_link("asesoria-form.html?cod=%s" % c,
                              "Editar asesoría")),
        ])
    cuerpo = metricas([
        ("chat", "Asesorías este mes", str(len(ASESORIAS)), "", 84, "+9"),
        ("reloj", "Promedio de respuesta", "4.2", " h", 42, "-0.6"),
        ("checklist", "Asesorías finalizadas",
         str(sum(1 for a in ASESORIAS if a[7] == "Finalizada")), "", 82, None),
        ("alerta", "Sin confirmar",
         str(sum(1 for a in ASESORIAS if a[7] == "Programada")), "", 22, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Asesorías por mes", barras(
        "", "", ["Jul", "Ago", "Sep", "Oct", "Nov"], [18, 24, 29, 33, 38],
        unidad=" asesorías"))
    cuerpo += card("Asesorías por sector", barras_h(
        "", "", ["Alimentos", "Moda", "Ambiental", "Muebles", "Tecnología"],
        [16, 10, 7, 3, 2], color=AMAR))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Estado de las asesorías", donut(
        "", "", [("Finalizadas", 31, AZUL), ("Confirmadas", 7, AMAR),
                 ("Sin confirmar", 5, GRIS), ("Canceladas", 3, GRIS)],
        "asesorías"))
    cuerpo += card("Docentes con mejor respuesta", lista_def([
        ("Hector Vargas", "1.8 h promedio"),
        ("Paula Andrea Rios", "2.4 h promedio"),
        ("Carlos Mendoza", "3.1 h promedio"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += card("Programación de asesorías", tabla(
        ["Código", "Estudiante", "Docente", "Fecha y hora", "Tema", "Modalidad",
         "Estado", "@ACC"], filas, caption="Programación de asesorías"),
        accion=_nuevo_link("asesoria-form.html", "Nueva asesoría"),
        sin_pad=True)
    cuerpo = formulario("asesorias", cuerpo)
    return shell(R, "asesorias", "Asesorías", cuerpo,
                 migas=["Inicio", "Asesorías"],
                 sub="Indicadores de uso, respuesta y programación del servicio de "
                     "asesorías.",
                 acciones=_nuevo_link("asesoria-form.html", "Nueva asesoría"))


def asesoria_detalle():
    """Vista propia de una asesoría (asesoria-detalle.html?cod=ASE-012)."""
    cuerpo = steps(["Solicitud", "Confirmación", "Sesión", "Acta"], 2)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += metricas([
        ("calendar", "Fecha", '<span data-campo="fecha">2024-11-12</span>', "", 60,
         '<span data-campo="hora">10:00</span>'),
        ("chat", "Modalidad", '<span data-campo="modalidad">Virtual</span>', "", 60,
         '<span data-campo="lugar">meet.sgemd.edu.co</span>'),
        ("users", "Docente", '<span data-campo="docente">Carlos Mendoza</span>',
         "", 100, '<span data-campo="estudiante">Mariana López</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la asesoría", lista_def([
        ("Código", '<b data-campo="codigo">ASE-012</b>'),
        ("Estudiante", '<b data-campo="estudiante">Mariana López</b>'),
        ("Emprendimiento", '<span data-campo="emprendimiento">Sabor y Sabe</span>'),
        ("Docente", '<span data-campo="docente">Carlos Mendoza</span>'),
        ("Fecha", '<span data-campo="fecha">2024-11-12</span>'),
        ("Hora", '<span data-campo="hora">10:00</span>'),
        ("Modalidad", '<span data-campo="modalidad">Virtual</span>'),
        ("Lugar o enlace", '<span data-campo="lugar">meet.sgemd.edu.co/ases-012</span>'),
        ("Estado", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="estado">Programada</span></span>'),
    ]))
    cuerpo += card("Tema de la asesoría",
                   '<p class="suave"><b data-campo="tema">Revisión del prototipo '
                   'de empaque</b></p><div class="divisor"></div>'
                   '<p class="suave" data-campo="nota">Sesión de acompañamiento '
                   'del programa.</p>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" data-enlace="editar_url" '
                   'href="asesoria-form.html">%s Editar asesoría</a>'
                   '<button class="btn btn-secundario" data-accion="cancelar-asesoria">'
                   '%s Cancelar asesoría</button>'
                   '<a class="btn btn-secundario" href="asesorias.html">'
                   '%s Volver a asesorías</a></div>'
                   % (ico("edit", 16), ico("x", 16), ico("izq", 16)))
    cuerpo += card("Participantes", lista_def([
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("Docente", '<span data-campo="docente">Carlos Mendoza</span>'),
        ("Modalidad", '<span data-campo="modalidad">Virtual</span>'),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(ASES_DET, "cod", "ASE-012")
    return shell(R, "asesorias", "Detalle de asesoría", cuerpo,
                 migas=["Inicio", "Asesorías", "Detalle de asesoría"],
                 sub="Información completa de la asesoría y sus participantes.",
                 acciones=_volver("asesorias.html", "Volver"))


def asesoria_form():
    """Crear o editar asesoría con calendario y horas disponibles."""
    horas = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    cuerpo = callout("Selecciona la fecha en el calendario y una hora disponible. "
                     "El docente y el estudiante reciben la notificación.", "calendar")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la asesoría",
                   select("Estudiante", [e[1] for e in ESTUDIANTES], req=True,
                          name="estudiante")
                   + select("Docente asignado", [d[1] for d in DOCENTES], req=True,
                            name="docente")
                   + campo("Tema", name="tema", req=True,
                           ph="P. ej. Plan financiero del emprendimiento"))
    cuerpo += card("Fecha y hora",
                   '<div data-vacio-lista>'
                   + calendario_interactivo("noviembre", 2024, {12: "Día sugerido"},
                                            hoy=12, vacio="Sin asesorías")
                   + "</div>"
                   + '<div class="sep sep-16"></div>'
                   + campo("Fecha", tipo="date", req=True, name="fecha")
                   + select("Hora disponible", ["- Elegir hora -"] + horas,
                            req=True, name="hora")
                   + select("Modalidad", ["Virtual", "Presencial"], valor="Virtual",
                            name="modalidad")
                   + select("Estado", ["Programada", "Confirmada", "En curso",
                                       "Finalizada", "Cancelada"],
                            valor="Programada", name="estado"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Resumen", lista_def([
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("Docente", '<span data-campo="docente">Carlos Mendoza</span>'),
        ("Tema", '<span data-campo="tema">Revisión del prototipo de empaque</span>'),
        ("Fecha", '<span data-campo="fecha">2024-11-12</span>'),
        ("Hora", '<span data-campo="hora">10:00</span>'),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-perfil">'
                   '%s Guardar asesoría</button>'
                   '<a class="btn btn-secundario" href="asesorias.html">'
                   '%s Cancelar</a></div>'
                   % (ico("check", 16), ico("x", 16)))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(ASES_DET, "cod", "ASE-012")
    return shell(R, "asesorias", "Asesoría", cuerpo,
                 migas=["Inicio", "Asesorías", "Asesoría"],
                 sub="Crea o actualiza la programación de una asesoría.",
                 acciones=_volver("asesorias.html", "Volver"))


def _instrumento():
    """Resumen de solo lectura del instrumento del diagnóstico (A16): se
    desplega en un modal desde diagnosticos() para poder consultar las
    preguntas del cuestionario de 5 secciones / 22 preguntas."""
    secciones = [
        ("Perfil del emprendimiento", [
            "¿Cuál es el nombre de tu emprendimiento?",
            "¿Qué tipo de emprendimiento es?",
            "¿A qué sector productivo pertenece?",
            "¿Qué producto o servicio ofreces?",
            "¿En qué etapa del programa está tu emprendimiento?"]),
        ("Problema o necesidad", [
            "¿Qué problema concreto resuelve tu producto o servicio?",
            "¿A quién le ocurre ese problema?",
            "¿Cómo lo resuelven hoy (sin tu producto)?",
            "¿Qué tan urgente es el problema para tu cliente?"]),
        ("Propuesta de valor", [
            "¿Cuál es tu propuesta de valor en una frase?",
            "¿Qué beneficio concreto entrega al cliente?",
            "¿Qué te diferencia de la competencia?",
            "¿Qué necesidad principal cubre?"]),
        ("Mercado objetivo", [
            "¿Quién es tu cliente ideal (perfil)?",
            "¿Cuántos clientes potenciales estimas?",
            "¿Cuál es tu estrategia de precio?",
            "¿Qué canales usarás para llegarles?"]),
        ("Capacidad operativa y financiera", [
            "¿Con cuántas personas cuenta el equipo?",
            "¿Cuál es tu capacidad de producción actual?",
            "¿Llevas registro de costos y ventas?",
            "¿Qué inversión necesitas para crecer?",
            "¿Cuál es tu meta de ventas del próximo mes?"]),
    ]
    uls = []
    for i, (tit, preguntas) in enumerate(secciones, 1):
        items = "".join("<li>%s</li>" % p for p in preguntas)
        uls.append('<p><b>Sección %d · %s</b></p><ul style="margin:0 0 12px">%s</ul>'
                   % (i, tit, items))
    return ('<div class="suave">Cuestionario de 5 secciones y 22 preguntas que '
            "responde el estudiante al iniciar su plan.</div>" + "".join(uls))


# --- 44. Eventos -------------------------------------------------------------
def _ev_grad(i):
    return "g%d" % (i % 5)


def _evento_card(ev, i):
    return (
        '<article class="ev-card">'
        '<div class="ev-img %s">%s</div>'
        '<div class="ev-body">'
        '<div><span class="badge %s">%s</span></div>'
        '<h3>%s</h3>'
        '<div class="ev-meta"><span>%s %s · %s</span>'
        '<span>%s %s</span></div>'
        '<p class="suave" style="margin:0">%s</p>'
        '<div class="ev-foot">'
        '<a class="btn btn-sm btn-primario" href="evento-detalle.html?ev=%s">'
        '%s Ver evento</a>'
        '<a class="btn btn-sm btn-secundario" href="evento-form.html?ev=%s">%s</a>'
        '<span class="badge b-neutra">%s</span>'
        "</div></div></article>"
        % (_ev_grad(i), ico("calendar", 44), ev["clase"], ev["estado"],
           ev["titulo"], ico("calendar", 13), ev["fecha"], ev["hora"],
           ico("users", 13), ev["formato"], ev["descripcion"],
           ev["ev"], ev["titulo"].split(":")[0], ev["ev"], ico("edit", 13),
           ev["cupos"]))


def eventos():
    """Pipeline editorial con calendario y tarjetas con imagen."""
    lista = list(EVENTOS_DET.values())
    cuerpo = metricas([
        ("calendar", "Eventos publicados",
         str(sum(1 for e in lista if e["estado"] == "Publicado")), "", 40, None),
        ("reloj", "Por aprobar",
         str(sum(1 for e in lista if e["estado"] == "Por aprobar")), "", 20, None),
        ("doc", "Borradores",
         str(sum(1 for e in lista if e["estado"] == "Borrador")), "", 20, None),
        ("users", "Confirmaciones", "141", "", 88, "+37"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Próximos eventos",
                   agenda([
                       ("18 nov 2024", [
                           ("09:00", "Taller de costos y precios",
                            "Auditorio A · 32 de 40 cupos",
                            badge("Publicado", "b-azul", "check")),
                       ]),
                       ("22 nov 2024", [
                           ("14:00", "Feria de emprendedores",
                            "Plaza central · 86 de 120 cupos",
                            badge("Publicado", "b-azul", "check")),
                       ]),
                       ("25 nov 2024", [
                           ("08:30", "Jornada de mentoría",
                            "Sala 2 · 14 confirmados",
                            badge("Por aprobar", "b-amarillo", "reloj")),
                       ]),
                   ]))
    cuerpo += card("Calendario de noviembre",
                   '<div data-vacio-lista>'
                   + calendario_interactivo("noviembre", 2024, EVENTOS_CAL,
                                            hoy=12, vacio="Sin eventos")
                   + "</div>")
    cuerpo += "</div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="card-head"><div><h3>Tarjetas de eventos</h3>'
    cuerpo += '<p class="sub">Todos los eventos del programa con su imagen, '
    cuerpo += 'estado y cupos.</p></div>'
    cuerpo += _nuevo_link("evento-form.html", "Crear evento") + "</div>"
    cuerpo += '<div class="sep sep-16"></div>'
    cuerpo += '<div class="ev-grid">'
    cuerpo += "".join(_evento_card(ev, i) for i, ev in enumerate(lista))
    cuerpo += "</div>"
    cuerpo += ('<p class="nota-foot">Publicar un evento notifica a los estudiantes '
               'del sector correspondiente.</p>')
    cuerpo = formulario("eventos", cuerpo)
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Aprueba y publica eventos del programa.",
                 acciones=_btn("plus", "Crear evento", "evento-form.html"))


def evento_detalle():
    """Vista atractiva de un evento (evento-detalle.html?ev=...)."""
    cuerpo = ('<div class="ev-hero g0" data-campo-clase="ev">%s</div>'
              % ico("calendar", 64))
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Descripción del evento",
                   '<h2 style="margin:0 0 8px" data-campo="titulo">Taller de costos '
                   'y precios</h2>'
                   '<p class="suave" data-campo="descripcion">Taller práctico para '
                   'calcular el costo de insumos y definir el punto de equilibrio '
                   'de un emprendimiento.</p>')
    cuerpo += card("Detalles", lista_def([
        ("Fecha", '<span data-campo="fecha">18 nov 2024</span>'),
        ("Hora", '<span data-campo="hora">09:00 - 11:00</span>'),
        ("Formato", '<span class="badge b-azul" data-badge="clase">'
         '<span data-campo="formato">Presencial</span></span>'),
        ("Dirigido a", '<span data-campo="dirigido">Todos los estudiantes</span>'),
        ("Cupos", '<span data-campo="cupos">32 de 40 cupos</span>'),
        ("Recordatorio", '<span data-campo="recordatorio">Un día antes</span>'),
    ]))
    cuerpo += card("Ubicación y conexión",
                   '<dl class="lista-def">'
                   '<div class="def-row" data-si-vacio="lugar"><dt>'
                   '<span data-campo="lugar_etiqueta">Ubicación</span></dt>'
                   '<dd><span data-campo="lugar">Auditorio A</span></dd></div>'
                   '<div class="def-row" data-si-vacio="enlace"><dt>Enlace</dt>'
                   '<dd><span data-campo="enlace">—</span></dd></div></dl>'
                   '<p class="nota-foot">El lugar aplica a eventos presenciales o '
                   'mixtos; el enlace, a virtuales o mixtos.</p>')
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" data-enlace="editar_url" '
                   'href="evento-form.html">%s Editar evento</a>'
                   '<button class="btn btn-secundario" data-accion="publicar-evento">'
                   '%s Publicar</button>'
                   '<button class="btn btn-secundario" data-accion="guardar-borrador">'
                   '%s Guardar borrador</button>'
                   '<a class="btn btn-secundario" href="eventos.html">%s Volver a '
                   'eventos</a></div>'
                   % (ico("edit", 16), ico("enviar", 16), ico("doc", 16),
                      ico("izq", 16)))
    cuerpo += card("Estado", lista_def([
        ("Publicación", '<span data-campo="estado">Publicado</span>'),
        ("Formato", '<span data-campo="formato">Presencial</span>'),
        ("Cupos", '<span data-campo="cupos">32 de 40 cupos</span>'),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EVENTOS_DET, "ev", "taller-costos")
    cuerpo += ('<script>(function(){var d=window.__DET[(new URLSearchParams('
               "location.search)).get('ev')]||window.__DET['taller-costos'];"
               "var hero=document.querySelector('.ev-hero');"
               "var orden=Object.keys(window.__DET);"
               "hero.className='ev-hero g'+(orden.indexOf(d.ev)%5);})();</script>")
    return shell(R, "eventos", "Detalle del evento", cuerpo,
                 migas=["Inicio", "Eventos", "Detalle del evento"],
                 sub="Toda la información del evento y su formato.",
                 acciones=_volver("eventos.html", "Volver"))


def evento_form():
    """Crear o editar un evento (evento-form.html o ?ev=...).

    Incluye sección de imagen, guardar borrador y publicar."""
    cuerpo = steps(["Datos del evento", "Fecha, formato y lugar", "Publicar"], 1)
    cuerpo += '<div class="sep sep-22"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del evento",
                   campo("Título del evento", req=True, name="titulo")
                   + select("Dirigido a", ["Todos los estudiantes",
                                           "Solo Alimentos", "Solo Moda",
                                           "Solo Ambiental", "Solo Muebles"],
                            req=True, name="dirigido")
                   + campo("Descripción", alto=True, name="descripcion",
                           ph="De qué tratará el evento")
                   + campo("Cupo máximo", tipo="number", name="cupos",
                           ph="Número de asistentes"))
    cuerpo += card("Fecha y formato",
                   campo("Fecha", tipo="date", req=True, name="fecha")
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Hora de inicio", tipo="time", req=True, name="hora")
                   + campo("Hora de cierre", tipo="time", name="hora_fin")
                   + "</div>"
                   + select("Formato", ["Presencial", "Virtual", "Mixto"],
                            req=True, name="formato")
                   + '<div data-campo-formato="presencial">'
                   + campo("Ubicación", name="lugar", ph="Ej.: Auditorio A")
                   + "</div>"
                   + '<div data-campo-formato="virtual">'
                   + campo("Enlace de conexión", name="enlace",
                           ph="Ej.: meet.sgemd.edu.co/evento")
                   + "</div>"
                   + select("Recordatorio", ["Un día antes", "Dos días antes",
                                             "La misma mañana"], name="recordatorio"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Imagen del evento",
                   '<div class="ev-preview" id="ev-preview">%s</div>' % ico("doc", 44)
                   + '<p class="suave">Sube una imagen horizontal (mínimo 1200×600). '
                     "Se muestra en las tarjetas y en la vista del evento.</p>"
                   + _drop())
    cuerpo += card("Publicación",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="guardar-borrador">'
                   '%s Guardar borrador</button>'
                   '<button class="btn btn-secundario" data-accion="publicar-evento">'
                   '%s Publicar evento</button>'
                   '<a class="btn btn-secundario" href="eventos.html">%s Cancelar</a>'
                   '</div>' % (ico("doc", 16), ico("enviar", 16), ico("x", 16)))
    cuerpo += card("Visibilidad", lista_def([
        ("Visibilidad", '<span data-campo="dirigido">Todos los estudiantes</span>'),
        ("Estado", '<span data-campo="estado">Borrador</span>'),
        ("Confirmaciones", '<span data-campo="cupos">0 de 40 cupos</span>'),
    ]))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(EVENTOS_DET, "ev", "marco-legal")
    cuerpo += ("<script>(function(){var f=document.querySelector("
               "'select[name=formato]');if(!f)return;"
               "function pintar(){var v=f.value.toLowerCase();"
               "var pre=document.querySelector('[data-campo-formato=presencial]');"
               "var vir=document.querySelector('[data-campo-formato=virtual]');"
               "if(pre)pre.style.display=(v==='presencial'||v==='mixto')?'':'none';"
               "if(vir)vir.style.display=(v==='virtual'||v==='mixto')?'':'none';}"
               "f.addEventListener('change',pintar);pintar();})();</script>")
    return shell(R, "eventos", "Evento", cuerpo,
                 migas=["Inicio", "Eventos", "Evento"],
                 sub="Datos, formato, imagen y publicación del evento.",
                 acciones='<button class="btn btn-primario" '
                          'data-accion="guardar-borrador">%s Guardar</button>'
                          % ico("check", 16))


# --- 46. Asignaciones --------------------------------------------------------
def asignaciones():
    """Asignaciones de docente a emprendimiento (tabla única del admin)."""
    filas = []
    for cod, emp, estu, correo, sector, tipo, etapa, avance, docente, correo_doc, sede in EMPRENDIMIENTOS[:5]:
        est_id = _id_estudiante(estu)
        sin_doc = docente == "Sin asignar"
        estado = (badge("Sin asignar", "b-neutra", "alerta") if sin_doc
                  else badge("Asignado", "b-azul", "check"))
        etiqueta = "Asignar docente" if sin_doc else "Reasignar docente"
        filas.append({
            "attrs": {"correo": correo, "proyecto": emp, "estudiante": estu,
                      "docente": docente, "cod": cod, "col-docente": 3},
            "celdas": [
                "<b>%s</b><small class=\"nota-foot\">%s</small>" % (emp, cod),
                "<b>%s</b><small class=\"nota-foot\">%s</small><small class=\"nota-foot\">%s</small>"
                % (estu, est_id, correo),
                sector,
                docente if not sin_doc else "Sin docente asignado",
                estado,
                _acc(_editar_link("asignacion-form.html?cod=%s" % cod, etiqueta,
                                  "sliders")),
            ],
        })
    cab = "".join(th(c) for c in ["Proyecto", "Estudiante", "Sector",
                                  "Docente asignado", "Estado", "@ACC"])
    eti = [_etiqueta(c) for c in ["Proyecto", "Estudiante", "Sector",
                                  "Docente asignado", "Estado", "@ACC"]]
    body = ""
    for fila in filas:
        attrs = "".join(' data-%s="%s"' % (k, v)
                        for k, v in fila["attrs"].items() if v)
        celdas = ""
        for e, x in zip(eti, fila["celdas"]):
            if e == "Acciones":
                celdas += '<td class="acc" data-label="%s">%s</td>' % (e, x)
            else:
                celdas += '<td data-label="%s">%s</td>' % (e, x)
        body += "<tr%s>%s</tr>" % (attrs, celdas)
    cuerpo = callout(
        "<b>Regla de asignación:</b> verifica que el acta de confidencialidad esté "
        "aceptada antes de confirmar una asignación definitiva. Un docente puede "
        "tener hasta <b>12 emprendimientos</b>.", "alerta")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-4">'
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Asignaciones vigentes</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra"><span style="width:%d%%"></span></div></div>'
               % (ico("check", 18), 4, 80))
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Sin docente</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra amarilla"><span style="width:%d%%"></span></div></div>'
               % (ico("alerta", 18), 1, 20))
    cuerpo += ('<div class="card metrica"><div class="metrica-top">'
               '<span class="metrica-ico">%s</span><div><div class="metrica-lbl">'
               'Docentes registrados</div><div class="metrica-val">%d</div></div></div>'
               '<div class="barra"><span style="width:%d%%"></span></div></div>'
               % (ico("users", 18), len(DOCENTES), 62))
    cuerpo += "</div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="card" data-tabla-zona="adm-asignaciones">'
    cuerpo += ('<div class="card-head"><div><h3>Estudiantes y emprendimientos</h3>'
               '<p class="sub">Busca por correo institucional o nombre del proyecto.</p>'
               '</div><span class="hint" data-resultados>%d resultados</span></div>'
               % len(filas))
    cuerpo += '<div class="toolbar">'
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-correo">'
               'Correo del estudiante</label><input id="filtro-correo" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="1" '
               'type="text" placeholder="estudiante@sgemd.edu.co" autocomplete="off">'
               '</div>')
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-proyecto">'
               'Nombre del proyecto</label><input id="filtro-proyecto" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="0" '
               'type="text" placeholder="Ej. Sabor y Sabe" autocomplete="off"></div>')
    cuerpo += ('<div class="campo toolbar-field"><label for="filtro-docente">'
               'Estado de asignación</label><select id="filtro-docente" class="filtro" '
               'data-filtro="off" data-filtro-adm="asignaciones" data-col="4">'
               '<option value="">Todos</option><option value="asignado">Con docente</option>'
               '<option value="sin asignar">Sin docente</option></select></div>')
    cuerpo += "</div>"
    cuerpo += '<div class="tabla-scroll"><table class="tabla"><thead><tr>%s</tr></thead>' \
              "<tbody>%s</tbody></table></div>" % (cab, body)
    cuerpo += ('<div data-vacio hidden>%s</div>'
               % estado_vacio("Sin resultados",
                              "No hay estudiantes que coincidan con los filtros actuales.",
                              "", "alerta"))
    cuerpo += "</div>"
    cuerpo = formulario("asignaciones", cuerpo)
    return shell(R, "asignaciones", "Asignaciones", cuerpo,
                 migas=["Inicio", "Asignaciones"],
                 sub="Asigna docentes registrados a los emprendimientos y consulta "
                     "el estado actual del vínculo.",
                 extra_head=ADMIN_CSS,
                 acciones=_btn("plus", "Asignar docente", "asignacion-form.html"))


# --- 47. Diagnósticos: dashboard único ---------------------------------------
DIAG_DET = {}
for _cod, _emp, _estu, _correo, _sector, _tipo, _etapa, _av, _doc, _cdoc, _sede in EMPRENDIMIENTOS[:6]:
    DIAG_DET[_cod] = {
        "codigo": _cod, "emprendimiento": _emp, "estudiante": _estu,
        "docente_txt": _doc if _doc != "Sin asignar" else "Sin docente asignado",
        "sector": _sector, "etapa": _etapa,
        "puntaje": str(60 + (_av % 40)),
        "fecha": "02 nov 2024", "estado": "Sin revisión",
        "clase": "b-amarillo",
        "resumen": ("El estudiante respondió las 5 secciones del instrumento. "
                    "La propuesta de valor y el mercado objetivo están bien "
                    "definidos; falta profundizar en costos y proyección de ventas."),
        "detalle_url": "emprendimiento-detalle.html?cod=%s" % _cod,
        "editar_url": "diagnostico-detalle.html?cod=%s" % _cod,
    }


def diagnosticos():
    """Dashboard único de diagnósticos: resultados y pendientes en una vista."""
    filas = []
    for cod, d in DIAG_DET.items():
        filas.append({
            "attrs": {"cod": cod, "emp": d["emprendimiento"],
                      "estu": d["estudiante"]},
            "celdas": [
                "<b>%s</b>" % d["emprendimiento"],
                d["estudiante"], d["docente_txt"], d["puntaje"],
                d["fecha"], badge(d["estado"], "b-amarillo", "reloj"),
                _acc(_ver_link("diagnostico-detalle.html?cod=%s" % cod,
                               "Revisar diagnóstico", "check"),
                     _ver_link("emprendimiento-detalle.html?cod=%s" % cod,
                               "Ver emprendimiento", "maleta")),
            ],
        })
    cuerpo = metricas([
        ("clipboard", "Respondidos", "94", "", 88, "+8"),
        ("reloj", "Sin revisión", str(len(DIAG_DET)), "", 22, "Requieren acción"),
        ("medalla", "Promedio", "74", "", 74, "+2"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Puntaje por emprendimiento", barras_h(
        "", "Último diagnóstico registrado",
        ["EcoPack", "Sabor y Sabe", "Aromas del Sur", "Krea Textil",
         "Muebles Origen"], [91, 78, 64, 71, 70], maximo=100))
    cuerpo += card("Pendientes de revisión",
                   '<p class="suave">Cada pendiente abre la ficha del proyecto, '
                   'donde puedes quitar el pendiente, dar puntaje o corregir.</p>',
                   accion=_exportar("Exportar pendientes"))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Rendimiento del grupo", distribucion([
        ("90 - 100", "12", 26), ("70 - 89", "45", 48),
        ("50 - 69", "28", 30), ("Menos de 50", "9", 19)]))
    cuerpo += card("Acciones", '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-secundario" data-accion="ver-instrumento">'
                   '%s Ver instrumento</button>'
                   '<a class="btn btn-secundario" href="reportes.html">%s Exportar '
                   'resultados</a></div>' % (ico("doc", 16), ico("download", 16)))
    cuerpo += "</div></div>"
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "diagnosticos", "Diagnósticos por emprendimiento",
        ["Emprendimiento", "Estudiante", "Docente", "Puntaje", "Fecha", "Estado",
         "@ACC"], filas,
        sub="Resultados del diagnóstico de los estudiantes y su estado de revisión.",
        caption="Diagnósticos por emprendimiento")
    cuerpo += '<div id="contenido-instrumento" hidden>' + _instrumento() + "</div>"
    cuerpo = formulario("diagnosticos", cuerpo)
    return shell(R, "diagnosticos", "Diagnósticos", cuerpo,
                 migas=["Inicio", "Diagnósticos"],
                 sub="Resultados del diagnóstico y pendientes de revisión.")


def diagnostico_detalle():
    """Ficha de revisión de un diagnóstico (diagnostico-detalle.html?cod=)."""
    cuerpo = metricas([
        ("medalla", "Puntaje", '<span data-campo="puntaje">78</span>', "", 78,
         "Sobre 100"),
        ("clipboard", "Secciones", "5 de 5", "", 100, "Instrumento completo"),
        ("reloj", "Estado", '<span class="badge b-amarillo" data-badge="clase">'
         '<span data-campo="estado">Sin revisión</span></span>', "", 40,
         '<span data-campo="fecha">02 nov 2024</span>'),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos del diagnóstico", lista_def([
        ("Emprendimiento", '<b data-campo="emprendimiento">Sabor y Sabe</b>'),
        ("Código", '<span data-campo="codigo">EMP-041</span>'),
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("Docente", '<span data-campo="docente_txt">Carlos Mendoza</span>'),
        ("Sector", '<span data-campo="sector">Alimentos</span>'),
        ("Etapa", '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("Fecha de respuesta", '<span data-campo="fecha">02 nov 2024</span>'),
    ]))
    cuerpo += card("Resumen de respuestas",
                   '<p class="suave" data-campo="resumen">El estudiante respondió '
                   'las 5 secciones del instrumento.</p>')
    cuerpo += card("Revisión del administrador",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Puntaje (0 a 100)", tipo="number", valor="78",
                           name="puntaje")
                   + select("Estado de revisión", ["Sin revisión", "En revisión",
                                                   "Revisado"], name="estado")
                   + "</div>"
                   + campo("Correcciones u observaciones", alto=True,
                           name="observaciones",
                           valor="Ajustar la proyección de ventas y el costo unitario.")
                   + '<div class="fila" style="margin-top:8px">'
                   + '<button class="btn btn-primario" data-accion="guardar-perfil">'
                     "%s Guardar puntaje</button>" % ico("check", 16)
                   + '<button class="btn btn-secundario" data-accion="quitar-pendiente">'
                     "%s Quitar pendiente</button>" % ico("x", 16)
                   + "</div>")
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="quitar-pendiente">'
                   '%s Quitar pendiente</button>'
                   '<a class="btn btn-secundario" data-enlace="detalle_url" '
                   'href="emprendimiento-detalle.html">%s Ver emprendimiento</a>'
                   '<a class="btn btn-secundario" href="diagnosticos.html">'
                   '%s Volver a diagnósticos</a></div>'
                   % (ico("check", 16), ico("maleta", 16), ico("izq", 16)))
    cuerpo += card("Instrumento", lista_def([
        ("Secciones", "5"),
        ("Preguntas", "22"),
        ("Última actualización", "01 oct 2024"),
    ]) + '<div class="form-acciones">'
         '<button class="btn btn-secundario btn-sm" data-accion="ver-instrumento">'
         "%s Ver instrumento</button></div>" % ico("doc", 14))
    cuerpo += "</div></div>"
    cuerpo += _aplicar_datos(DIAG_DET, "cod", "EMP-041")
    return shell(R, "diagnosticos", "Revisión del diagnóstico", cuerpo,
                 migas=["Inicio", "Diagnósticos", "Revisión del diagnóstico"],
                 sub="Califica, corrige o quita el pendiente del diagnóstico.",
                 acciones=_volver("diagnosticos.html", "Volver"))


def reportes():
    cuerpo = card("Tipo de reporte", tabla(
        ["Reporte", "Descripción", "Formato", "Última generación", "@ACC"],
        [[badge("Seguimiento", "b-linea"), "Avances y calificación por emprendimiento",
          "CSV y PDF", "12 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Asesorías", "b-linea"), "Uso y respuesta del servicio de asesorías",
          "CSV y PDF", "11 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Emprendimientos", "b-linea"), "Inventario completo con sector y etapa",
          "CSV y PDF", "10 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))],
         [badge("Diagnosticos", "b-linea"), "Puntajes del diagnóstico por estudiante",
          "CSV y PDF", "08 nov 2024", _acc(_b("download", "Descargar"), _b("eye", "Vista previa"))]]),
        sin_pad=True)
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += card("Filtros del reporte", select("Formato", ["CSV", "PDF", "XLSX"], req=True,
                                                 valor="CSV")
                   + select("Periodo", ["Últimos 30 días", "Últimos 3 meses",
                                        "Todo el periodo"], req=True,
                            valor="Últimos 3 meses")
                   + select("Docente", ["Todos los docentes", "Carlos Mendoza",
                                        "Paula Andrea Rios", "Hector Vargas"], req=True,
                            valor="Todos los docentes")
                   + campo("Enviar por correo", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co"))
    cuerpo += card("Resumen de la exportación",
                   lista_def([
                       ("Emprendimientos incluidos", "46"),
                       ("Estudiantes incluidos", "110"),
                       ("Estimación de filas", "1.284"),
                       ("Último archivo generado", "12 nov 2024, 09:20"),
                   ]))
    cuerpo += card("Acciones",
                   '<div class="fila-col">'
                   + '<button class="btn btn-primario" data-accion="generar-reporte">'
                     '%s Generar reporte</button>' % ico("download", 16)
                   + '<button class="btn btn-secundario" data-accion="descargar-plantilla">'
                     '%s Descargar plantilla</button>' % ico("doc", 16)
                   + "</div>")
    cuerpo += "</div>"
    cuerpo = formulario("reportes", cuerpo)
    return shell(R, "reportes", "Exportar reportes", cuerpo,
                 migas=["Inicio", "Reportes"],
                 sub="Genera y descarga reportes institucionales en CSV, PDF o XLSX.",
                 acciones='<button class="btn btn-primario" data-accion="generar-reporte">'
                          '%s Generar</button>' % ico("check", 16))


# --- 52. Tareas (consulta, alta y baja) --------------------------------------
# Vista completa aprobada en la auditoria V3: el admin revisa el tablero de
# tareas por emprendimiento y puede añadir (modal con insercion real de fila)
# o eliminar (confirmacion + baja de la fila). Calificar sigue siendo del
# docente; aqui solo se gestiona la asignacion.
TAREAS_ADM = [
    ("Evidencia fotográfica del punto de venta", "Sabor y Sabe", "Mariana López",
     "Alta", "12 nov 2024", "En revisión"),
    ("Presupuesto de insumos", "Sabor y Sabe", "Mariana López",
     "Media", "15 nov 2024", "Completada"),
    ("Perfil en redes sociales", "Krea Textil", "Jhon Ospina",
     "Baja", "16 nov 2024", "Pendiente"),
    ("Prototipo de empaque", "EcoPack", "Lucía Fernández",
     "Alta", "14 nov 2024", "En revisión"),
    ("Análisis de competencia", "Aromas del Sur", "Sofía Ramírez",
     "Media", "18 nov 2024", "Pendiente"),
    ("Plan de marketing", "TechNova", "Camilo Rojas",
     "Alta", "20 nov 2024", "Pendiente"),
    ("Estudio de costos", "Aura Design", "Valentina Ortega",
     "Media", "21 nov 2024", "Completada"),
    ("Prototipo funcional", "BioEco", "Laura Martínez",
     "Alta", "22 nov 2024", "En revisión"),
    ("Menú y precios", "Gourmet Fresh", "Sebastián Torres",
     "Media", "23 nov 2024", "Pendiente"),
    ("MVP aplicación", "SmartApp", "Ana Restrepo",
     "Alta", "24 nov 2024", "Pendiente"),
    ("Validación mercado", "Urban Style", "Mateo Gómez",
     "Media", "25 nov 2024", "Pendiente"),
    ("Control de inventario", "WoodCraft", "Diego Peralta",
     "Baja", "26 nov 2024", "Pendiente"),
]

PRIO_ADM = {"Alta": "b-amarillo", "Media": "b-azul", "Baja": "b-linea"}
ESTADO_TAREA_ADM = {"En revisión": "b-amarillo", "Completada": "b-azul",
                    "Pendiente": "b-neutra", "Devuelta": "b-neutra"}


def _cuerpo_tarea_adm():
    """Formulario de alta/edición de tarea; vive oculto y lo abre el modal
    (case 'nueva-tarea' / 'editar-tarea' en lib_js)."""
    emps = ["Sabor y Sabe", "Krea Textil", "EcoPack", "Aromas del Sur"]
    ests = ["Mariana López", "Jhon Ospina", "Lucía Fernández", "Sofía Ramírez"]
    return ('<div class="grid g-2 g-col">'
            + campo("Título de la tarea", ph="Ej.: Presentación de pitch", req=True)
            + select("Emprendimiento", ["- Elegir -"] + emps)
            + select("Estudiante", ["- Elegir -"] + ests)
            + select("Prioridad", ["Baja", "Media", "Alta"], valor="Media")
            + campo("Vence el", tipo="date")
            + campo("Puntos", tipo="number", valor="100")
            + "</div>"
            + campo("Descripción (opcional)", alto=True,
                    ph="Detalla qué debe entregar el estudiante"))


def tareas():
    """Tareas del admin: dos tablas propias (emprendimientos con tareas y
    tareas asignadas), cada una con buscador, filtros y paginacion."""
    filas_t = []
    for i, (t, emp, estu, prio, vence, est) in enumerate(TAREAS_ADM, 1):
        est_id = _id_estudiante(estu)
        filas_t.append({
            "attrs": {"est-id": est_id, "est-nombre": estu,
                      "est-correo": CORREOS_EST.get(estu, ""), "est-emp": emp,
                      "tarea-titulo": t, "tarea-prioridad": prio,
                      "tarea-vence": vence, "tarea-estado": est},
            "celdas": [
                "<b>%s</b>" % t, emp, estu, badge(prio, PRIO_ADM[prio]), vence,
                badge(est, ESTADO_TAREA_ADM[est]),
                _acc(_ficha("estudiante"),
                     _ver_link("tarea-detalle.html?clave=TAR-%02d" % i),
                     _b("edit", "Editar", "editar-tarea"),
                     _b("trash", "Eliminar", "eliminar-tarea"))],
        })
    filas_emp = []
    for cod, emp, estu, etapa, n_tareas in (
            ("EMP-041", "Sabor y Sabe", "Mariana López", "FASE 2 - Prototipo", "2"),
            ("EMP-040", "Krea Textil", "Jhon Ospina", "FASE 1 - Ideación", "1"),
            ("EMP-039", "EcoPack", "Lucía Fernández", "FASE 3 - Validación", "1"),
            ("EMP-038", "Aromas del Sur", "Sofía Ramírez", "FASE 1 - Ideación", "1")):
        filas_emp.append({
            "attrs": {"emp-id": cod, "emp-cod": cod, "emp-nombre": emp,
                      "emp-est-id": _id_estudiante(estu), "emp-est-nombre": estu,
                      "emp-est-correo": CORREOS_EST.get(estu, ""),
                      "emp-etapa": etapa},
            "celdas": [
                cod, "<b>%s</b>" % emp, estu, badge(etapa, "b-linea"), n_tareas,
                _acc(_ficha("emprendimiento"),
                     _ver_link("tarea-detalle.html?cod=%s" % cod,
                               "Ver detalle"),
                     _b("eye", "Ver tareas", "ver-tareas"))],
        })
    cuerpo = callout("Como administrador puedes <b>consultar, añadir y eliminar</b> "
                     "tareas de cualquier emprendimiento. La calificación de las "
                     "entregas la realiza el docente.", "bombilla")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "emprendimientos-tareas", "Emprendimientos con tareas",
        ["Código", "Emprendimiento", "Estudiante", "Etapa", "Tareas", "@ACC"],
        filas_emp,
        sub="Emprendimientos del programa con tareas activas.",
        caption="Emprendimientos con tareas asignadas",
        filtros=_adm_filtro("emprendimientos-tareas", "Todas las etapas",
                             ["Todas las etapas"] + ETAPAS, 3))
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += _tabla_adm(
        "tareas", "Tareas asignadas a estudiantes",
        ["Tarea", "Emprendimiento", "Estudiante", "Prioridad", "Vence",
         "Estado", "@ACC"], filas_t,
        sub="Tareas creadas por los docentes para sus estudiantes.",
        caption="Tareas asignadas a estudiantes",
        filtros=(_adm_filtro("tareas", "Todos los estados",
                             ["Todos los estados", "Pendiente", "En revisión",
                              "Completada", "Devuelta"], 5)
                 + _adm_filtro("tareas", "Toda la prioridad",
                               ["Toda la prioridad", "Alta", "Media", "Baja"], 3)),
        acciones=_nuevo("nueva-tarea", "Nueva tarea"))
    cuerpo += '<div id="form-tarea" hidden>' + _cuerpo_tarea_adm() + "</div>"
    cuerpo = formulario("tareas", cuerpo)
    return shell(R, "tareas", "Tareas", cuerpo,
                 migas=["Inicio", "Tareas"],
                 sub="Consulta, alta y baja de tareas por emprendimiento.",
                 extra_head=ADMIN_CSS,
                 acciones=_nuevo("nueva-tarea", "Nueva tarea"))


# --- 52b. Detalle de tarea ----------------------------------------------------
TAREAS_DET = {}
for _i, (_t, _emp, _estu, _prio, _vence, _est) in enumerate(TAREAS_ADM, 1):
    TAREAS_DET["TAR-%02d" % _i] = {
        "clave": "TAR-%02d" % _i, "titulo": _t,
        "emprendimiento": _emp, "estudiante": _estu,
        "prioridad": _prio, "vence": _vence, "estado": _est,
        "clase_prio": PRIO_ADM[_prio],
        "clase_estado": ESTADO_TAREA_ADM[_est],
        "est_id": _id_estudiante(_estu),
        "correo": CORREOS_EST.get(_estu, ""),
        "descripcion": "Tarea asignada por el programa. El estudiante debe "
                       "entregarla antes de la fecha límite y el docente "
                       "califica el resultado.",
        "puntos": "100",
    }

# Detalle por emprendimiento: se resuelve con el código del emprendimiento.
TAREAS_POR_EMP = {}
for _cod, _emp, _estu, _etapa, _n in (
        ("EMP-041", "Sabor y Sabe", "Mariana López", "FASE 2 - Prototipo", "2"),
        ("EMP-040", "Krea Textil", "Jhon Ospina", "FASE 1 - Ideación", "1"),
        ("EMP-039", "EcoPack", "Lucía Fernández", "FASE 3 - Validación", "1"),
        ("EMP-038", "Aromas del Sur", "Sofía Ramírez", "FASE 1 - Ideación", "1")):
    TAREAS_POR_EMP[_cod] = {
        "codigo": _cod, "emprendimiento": _emp, "estudiante": _estu,
        "etapa": _etapa, "num_tareas": _n,
        "tareas": [t for t in TAREAS_ADM if t[1] == _emp],
        "clase": "b-azul",
    }


def tarea_detalle():
    """Vista propia de una tarea o de las tareas de un emprendimiento.

    Acepta ?clave=TAR-01 (tarea) o ?cod=EMP-041 (emprendimiento)."""
    cuerpo = metricas([
        ("checklist", "Tareas activas", str(len(TAREAS_ADM)), "", 60, None),
        ("reloj", "Vencen esta semana", "3", "", 30, None),
        ("medalla", "Completadas",
         str(sum(1 for t in TAREAS_ADM if t[5] == "Completada")), "", 17, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos de la tarea", lista_def([
        ("Código", '<b data-campo="clave">TAR-01</b>'),
        ("Título", '<b data-campo="titulo">Evidencia fotográfica del punto de venta</b>'),
        ("Emprendimiento", '<span data-campo="emprendimiento">Sabor y Sabe</span>'),
        ("Estudiante", '<span data-campo="estudiante">Mariana López</span>'),
        ("ID del estudiante", '<span data-campo="est_id">912646</span>'),
        ("Prioridad", '<span class="badge b-amarillo" data-badge="clase_prio">'
         '<span data-campo="prioridad">Alta</span></span>'),
        ("Vence", '<span data-campo="vence">12 nov 2024</span>'),
        ("Estado", '<span class="badge b-amarillo" data-badge="clase_estado">'
         '<span data-campo="estado">En revisión</span></span>'),
        ("Puntos", '<span data-campo="puntos">100</span>'),
    ]))
    cuerpo += card("Descripción",
                   '<p class="suave" data-campo="descripcion">Tarea asignada por el '
                   'programa.</p>')
    cuerpo += card("Emprendimiento asociado", lista_def([
        ("Código", '<span data-campo="codigo">EMP-041</span>'),
        ("Nombre", '<span data-campo="emprendimiento">Sabor y Sabe</span>'),
        ("Etapa", '<span data-campo="etapa">FASE 2 - Prototipo</span>'),
        ("Tareas activas", '<span data-campo="num_tareas">2</span>'),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<button class="btn btn-primario" data-accion="editar-tarea">'
                   '%s Editar tarea</button>'
                   '<button class="btn btn-secundario" data-accion="eliminar-tarea">'
                   '%s Eliminar tarea</button>'
                   '<a class="btn btn-secundario" href="tareas.html">%s Volver a '
                   'tareas</a></div>'
                   % (ico("edit", 16), ico("trash", 16), ico("izq", 16)))
    cuerpo += card("Trazabilidad", lista_def([
        ("Creada por", "Administración del programa"),
        ("Asignada a", '<span data-campo="estudiante">Mariana López</span>'),
        ("Calificación", "Pendiente del docente"),
    ]))
    cuerpo += "</div></div>"
    # Pintar datos de la tarea (si viene por clave) o del emprendimiento.
    cuerpo += _aplicar_datos(TAREAS_DET, "clave", "TAR-01")
    cuerpo += _aplicar_datos(TAREAS_POR_EMP, "cod", "EMP-041")
    return shell(R, "tareas", "Detalle de tarea", cuerpo,
                 migas=["Inicio", "Tareas", "Detalle de tarea"],
                 sub="Información completa de la tarea y su emprendimiento.",
                 acciones=_volver("tareas.html", "Volver"))

# --- 49. Mi perfil -----------------------------------------------------------

def perfil():
    """Perfil del administrador: solo visualización.

    La edición se hace en Configuración; el botón superior derecho lleva a la
    sección Información General de esa vista."""
    cuerpo = metricas([
        ("users", "Usuarios gestionados", "128", "", 84, "+12"),
        ("medalla", "Reportes generados", "24", "", 62, "+4"),
        ("alerta", "Decisiones pendientes", "12", "", 20, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Datos personales", lista_def([
        ("Nombres", "Ana"),
        ("Apellidos", "Restrepo"),
        ("Correo institucional", "ana.restrepo@sgemd.edu.co"),
        ("Teléfono", "+57 301 555 0199"),
        ("Cargo", "Administradora del programa"),
        ("Sede principal", "Sede Norte"),
        ("Zona horaria", "America/Bogota"),
    ]))
    cuerpo += card("Actividad", lista_def([
        ("Último acceso", "Hoy, 07:15"),
        ("Contraseña", "Actualizada hace 2 meses"),
        ("Verificación en dos pasos", "Activada"),
    ]))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Seguridad", lista_def([
        ("Contraseña", "Actualizada hace 2 meses"),
        ("Verificación en dos pasos", "Activada"),
        ("Último acceso", "Hoy, 07:15"),
    ]))
    cuerpo += card("Acciones",
                   '<div class="acciones-col acc-vertical">'
                   '<a class="btn btn-primario" href="configuracion.html#general">'
                   '%s Editar perfil</a>'
                   '<a class="btn btn-secundario" href="configuracion.html">'
                   '%s Ir a configuración</a></div>'
                   % (ico("edit", 16), ico("engranaje", 16)))
    cuerpo += "</div></div>"
    cuerpo = formulario("perfil", cuerpo)
    return shell(R, "perfil", "Mi perfil", cuerpo,
                 migas=["Inicio", "Mi perfil"],
                 sub="Consulta tus datos personales y de seguridad.",
                 acciones='<a class="btn btn-primario" href="configuracion.html#general">'
                          '%s Editar perfil</a>' % ico("edit", 16))


# --- 51. Configuracion del administrador --------------------------------------


def configuracion():
    """Configuración del admin con navegación por secciones."""
    sin_doc = sum(1 for e in EMPRENDIMIENTOS if e[8] == "Sin asignar")
    cuerpo = callout(
        "Los cambios de esta pantalla aplican a todo el programa: sedes, etapas, "
        "cupos y reglas de asignación.", "escudo")
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<nav class="cfg-nav" aria-label="Secciones de configuración">'
    for ancla, etiqueta in [("general", "Información General"),
                            ("seguridad", "Seguridad"),
                            ("notificaciones", "Notificaciones"),
                            ("parametros", "Parámetros del programa"),
                            ("bitacora", "Bitácora de decisiones")]:
        cuerpo += ('<a class="cfg-nav-item" href="#%s">%s</a>' % (ancla, etiqueta))
    cuerpo += "</nav>"
    cuerpo += '<div class="sep sep-16"></div>'

    # Seccion: Informacion General
    cuerpo += '<section id="general" class="cfg-seccion">'
    cuerpo += '<h2 class="cfg-titulo">Información General</h2>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += card("Cuenta del administrador",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Nombres", valor="Ana", req=True)
                   + campo("Apellidos", valor="Restrepo", req=True)
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Correo institucional", tipo="email",
                           valor="ana.restrepo@sgemd.edu.co",
                           bloqueo="El correo institucional no se puede editar")
                   + campo("Teléfono", tipo="tel", valor="+57 301 555 0199")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Cargo", valor="Administradora del programa",
                           bloqueo="El cargo lo asigna la institución")
                   + campo("Sede principal", valor="Sede Norte")
                   + "</div>"
                   + '<div class="fila-fin">'
                   + '<button class="btn btn-secundario" data-accion="cancelar-perfil">'
                     "Cancelar</button>"
                   + '<button class="btn btn-primario" data-accion="guardar-perfil">%s '
                     "Guardar cambios</button></div>" % ico("check", 16))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Sedes del programa", tabla(
        ["Sede", "Emprendimientos", "Estudiantes", "Estado"],
        [[s,
          str(sum(1 for e in EMPRENDIMIENTOS if e[10] == s)),
          str(sum(1 for e in ESTUDIANTES
                  if any(x[10] == s for x in EMPRENDIMIENTOS
                         if x[2] == e[1]))),
          badge("Activa", "b-azul")] for s in SEDES],
        caption="Sedes del programa"))
    cuerpo += "</div></div></section>"

    # Seccion: Seguridad
    cuerpo += '<section id="seguridad" class="cfg-seccion">'
    cuerpo += '<h2 class="cfg-titulo">Seguridad</h2>'
    cuerpo += card("Cambiar contraseña",
                   '<div class="grid g-3 g-col">'
                   + campo("Contraseña actual", tipo="password", ph="••••••••")
                   + campo("Nueva contraseña", tipo="password", ph="Mínimo 8 caracteres")
                   + campo("Repetir nueva contraseña", tipo="password", ph="••••••••")
                   + "</div>"
                   '<div style="display:flex;justify-content:flex-end">'
                   + '<button class="btn btn-secundario" data-accion="actualizar-contrasena">'
                     "%s Actualizar contraseña</button></div>" % ico("lock", 16))
    cuerpo += card("Estado de la cuenta", lista_def([
        ("Último acceso", "Hoy, 07:15"),
        ("Verificación en dos pasos", "Activada"),
        ("Sesiones activas", "1"),
    ]))
    cuerpo += "</section>"

    # Seccion: Notificaciones
    cuerpo += '<section id="notificaciones" class="cfg-seccion">'
    cuerpo += '<h2 class="cfg-titulo">Notificaciones</h2>'
    cuerpo += card("Notificaciones automáticas",
                   '<div class="fila-col">'
                   + _check("Aviso de solicitud de desbloqueo", True)
                   + _check("Aviso de emprendimiento en paralelo", True)
                   + _check("Aviso de tarea vencida", True)
                   + _check("Resumen semanal al equipo docente", False)
                   + "</div>"
                   + '<p class="nota-foot">Los avisos se envían al correo '
                     "institucional de cada docente y estudiante.</p>")
    cuerpo += "</section>"

    # Seccion: Parametros
    cuerpo += '<section id="parametros" class="cfg-seccion">'
    cuerpo += '<h2 class="cfg-titulo">Parámetros del programa</h2>'
    cuerpo += card("Parámetros del programa",
                   '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Carga máxima por docente (horas)", tipo="number", valor="12")
                   + campo("Emprendimientos máximos por docente", tipo="number", valor="12")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + select("Sede por defecto", SEDES, valor="Sede Norte")
                   + select("Etapa inicial del programa", ETAPAS,
                            valor="FASE 1 - Ideación")
                   + "</div>"
                   + '<div class="grid g-2" style="gap:0 16px">'
                   + campo("Fecha de cierre de admisiones", tipo="date",
                           valor="2024-12-15")
                   + campo("Cupos por sede", tipo="number", valor="40")
                   + "</div>"
                   + '<p class="nota-foot">Hoy hay %d emprendimientos sin docente '
                     'asignado: la cola se resuelve desde Asignaciones.</p>' % sin_doc)
    cuerpo += "</section>"

    # Seccion: Bitacora
    cuerpo += '<section id="bitacora" class="cfg-seccion">'
    cuerpo += '<h2 class="cfg-titulo">Bitácora de decisiones</h2>'
    cuerpo += card("Bitácora de decisiones",
                   lista_def([
                       ("Aprobación de desbloqueo de cuenta",
                        "05 nov 2024 · 912651 · Camilo.rojas@sgemd.edu.co"),
                       ("Cambio de docente asignado",
                        "04 nov 2024 · EMP-039 · EcoPack · Paula Andrea Rios → Hector Vargas"),
                       ("Reactivación de cuenta inactiva",
                        "02 nov 2024 · DOC-011 · Ninafq Beltran"),
                   ]) + _vacio(".def-row", "Sin decisiones registradas",
                               "Las aprobaciones, rechazos y cambios de docente "
                               "quedan registrados aquí.", "checklist"))
    cuerpo += "</section>"

    cuerpo = formulario("configuracion", cuerpo)
    return shell(R, "configuracion", "Configuración", cuerpo,
                 migas=["Inicio", "Configuración"],
                 sub="Parámetros del programa, sedes, notificaciones y bitácora.",
                 extra_head=ADMIN_CSS)


# --- 50. Notificaciones ------------------------------------------------------
# --- 50. Notificaciones ------------------------------------------------------
def notificaciones():
    """Bandeja del administrador: items .notif + chips de filtro (NO2/NO3).

    Replica la bandeja de estudiante y docente (avisos enlazados a la vista
    donde se resuelven, chip de tipo con filtrado y contador "sin leer" que
    persiste en localStorage) y conserva la agenda agrupada por fecha como
    sección secundaria de trazabilidad (90 días).
    """
    no_leidas = sum(1 for n in NOTIFS_ADMIN if not n[0])
    dias = [
        ("Hoy, 12 de noviembre", [
            ("08:15", "1 emprendimiento sigue sin docente",
             "Asignaciones · Sin docente asignado",
             '<a class="btn btn-sm btn-primario" href="asignaciones.html">'
             'Asignar</a>'),
            ("09:40", "5 diagnosticos sin revisión",
             "Diagnosticos · Enviados por estudiantes",
             '<a class="btn btn-sm btn-primario" href="diagnosticos.html">'
             'Revisar</a>'),
        ]),
        ("Ayer, 11 de noviembre", [
            ("16:40", "Evento por aprobar: Jornada de mentoria",
             "Eventos · Creado por docente tutor",
             '<a class="btn btn-sm btn-secundario" href="eventos.html">'
             'Aprobar</a>'),
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
        ("bell", "Sin leer", str(no_leidas), "", 18, None),
        ("check", "Aprobaciones del mes", "24", "", 62, None),
        ("users", "Docentes activos", "8", "", 88, None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div class="grid g-2-1">'
    cuerpo += '<div class="grid">'
    cuerpo += ('<div class="card"><div class="card-head">'
               '<h3>Bandeja de notificaciones</h3>'
               '<span class="hint" id="contador-no-leidas" aria-live="polite">%d sin leer</span></div>'
               '<div class="card-body sin-pad">' % no_leidas)
    cuerpo += "".join(
        '<a class="notif%s" href="%s" data-tipo="%s" data-i="%d">'
        '<span class="notif-ico">%s</span>'
        '<div class="notif-cuerpo"><h3>%s</h3><p>%s</p><time>%s</time></div>'
        '<span class="notif-flecha">%s</span>%s</a>'
        % (" no-leida" if not leer else "", href, tipo, i, ico(ic, 17),
           t, txt, f, ico("der", 16),
           '<span class="notif-dot"></span>' if not leer else "")
        for i, (leer, t, txt, f, ic, tipo, href) in enumerate(NOTIFS_ADMIN)
    )
    cuerpo += _vacio(".notif", "Sin notificaciones",
                      "Cuando haya asignaciones, diagnósticos, eventos o "
                      "reportes nuevos, se avisará aquí.", "bell")
    cuerpo += "</div></div>"
    cuerpo += card("Actividad reciente", agenda(dias))
    cuerpo += "</div>"
    cuerpo += '<div class="grid">'
    cuerpo += card("Filtros", '<div style="display:flex;flex-direction:column;'
                              'gap:8px">'
                    + "".join('<span class="chip%s" data-chip="%s">%s</span>'
                              % (" on" if i == 0 else "", val, etiqueta)
                              for i, (val, etiqueta) in enumerate(
                                  [("todas", "Todas"), ("sin-leer", "Sin leer"),
                                   ("asignacion", "Asignaciones"),
                                   ("diagnostico", "Diagnósticos"),
                                   ("evento", "Eventos"),
                                   ("reporte", "Reportes")]))
                    + "</div>")
    cuerpo += card("Retención", lista_def([
        ("Registro de decisiones", "90 días"),
        ("Exportación", "CSV desde Reportes"),
        ("Archivado automático", "Al resolverse"),
    ]))
    cuerpo += "</div></div>"
    cuerpo += ('<p class="nota-foot">El registro conserva 90 días y se puede '
               'exportar desde Reportes.</p>')
    cuerpo = formulario("notificaciones", cuerpo)
    return shell(R, "notificaciones", "Notificaciones", cuerpo,
                 migas=["Inicio", "Notificaciones"],
                 sub="Registro de aprobaciones y decisiones del equipo.",
                 acciones='<button class="btn btn-secundario" data-accion='
                          '"marcar-todas-como-leidas">%s Marcar todo como leído</button>'
                          % ico("check", 16))# --- 51. Respaldos ----------------------------------------------------------
def respaldos():
    cuerpo = metricas([
        ("carpeta","Respaldos realizados","12","",80,"+3"),
        ("reloj","Último respaldo","12 nov 2024","",100,None),
        ("download","Tamaño ocupado","84"," MB",75,None),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    filas=[["BKP-20241112-0915","Completo","12 nov 2024, 09:15","84 MB","Exitosa", _acc(_b("download","Descargar"), _b("eye","Ver detalle"))],["BKP-20241111-0910","Parcial","11 nov 2024, 09:10","41 MB","Exitosa", _acc(_b("download","Descargar"))],["BKP-20241110-0912","Completo","10 nov 2024, 09:12","83 MB","Fallida", _acc(_b("download","Descargar"))]]
    cuerpo += card("Historial de respaldos", tabla(["Código","Tipo","Fecha y hora","Tamaño","Estado","@ACC"],filas, caption="Historial de respaldos"), accion='<button class="btn btn-primario" data-accion="crear-respaldo">%s Crear respaldo</button>'%ico("download",16), sin_pad=True)
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += card("Configuración de respaldo", lista_def([("Frecuencia","Diaria a las 09:00"),("Destino","Almacenamiento institucional"),("Retención","30 días"),("Notificación","ana.restrepo@sgemd.edu.co")]))
    cuerpo = formulario("respaldos", cuerpo)
    return shell(R,"respaldos","Respaldos y recuperación", cuerpo, migas=["Inicio","Respaldos"], sub="Gestión de respaldos y verificación de integridad.")


def registrar(reg):
    paginas_adm = [
        ("dashboard.html", "01 Admin - Inicio (dashboard)", dashboard),
        ("usuarios.html", "02 Admin - Gestión de perfiles", usuarios),
        ("usuario-detalle.html", "02b Admin - Detalle de usuario", usuario_detalle),
        ("usuario-docente.html", "02c Admin - Editar docente", usuario_docente),
        ("usuario-estudiante.html", "02d Admin - Editar estudiante", usuario_estudiante),
        ("usuario-nuevo.html", "02e Admin - Nuevo usuario", usuario_nuevo_vista),
        ("solicitudes.html", "03 Admin - Solicitudes pendientes", solicitudes),
        ("solicitud-detalle.html", "03b Admin - Detalle de solicitud", solicitud_detalle),
        ("emprendimientos.html", "04 Admin - Emprendimientos", emprendimientos),
        ("emprendimiento-detalle.html", "04b Admin - Detalle de emprendimiento",
         emprendimiento_detalle),
        ("emprendimiento-editar.html", "04c Admin - Editar emprendimiento",
         emprendimiento_editar),
        ("seguimiento.html", "07 Admin - Seguimiento", seguimiento),
        ("seguimiento-detalle.html", "07b Admin - Detalle de seguimiento",
         seguimiento_detalle),
        ("avance-form.html", "07c Admin - Registrar avance", avance_form),
        ("asesorias.html", "11 Admin - Asesorías", asesorias),
        ("asesoria-detalle.html", "11b Admin - Detalle de asesoría", asesoria_detalle),
        ("asesoria-form.html", "11c Admin - Formulario de asesoría", asesoria_form),
        ("eventos.html", "12 Admin - Eventos", eventos),
        ("evento-detalle.html", "12b Admin - Detalle de evento", evento_detalle),
        ("evento-form.html", "12c Admin - Formulario de evento", evento_form),
        ("asignaciones.html", "14 Admin - Asignaciones", asignaciones),
        ("asignacion-form.html", "14b Admin - Asignar docente", asignacion_form),
        ("diagnosticos.html", "15 Admin - Diagnósticos", diagnosticos),
        ("diagnostico-detalle.html", "15b Admin - Revisión de diagnóstico",
         diagnostico_detalle),
        ("reportes.html", "16 Admin - Reportes", reportes),
        ("tareas.html", "17 Admin - Tareas", tareas),
        ("tarea-detalle.html", "17b Admin - Detalle de tarea", tarea_detalle),
        ("perfil.html", "18 Admin - Mi perfil", perfil),
        ("notificaciones.html", "19 Admin - Notificaciones", notificaciones),
        ("respaldos.html", "20 Admin - Respaldos y recuperación", respaldos),
        ("configuracion.html", "21 Admin - Configuración", configuracion),
    ]
    for i, (arch, tit, fn) in enumerate(paginas_adm):
        reg("admin", arch, tit, _envolver(fn), i)
