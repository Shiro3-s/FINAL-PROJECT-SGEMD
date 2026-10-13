# -*- coding: utf-8 -*-
"""Normaliza acentos y enie del texto visible del prototipo (T9).

Correccion de una sola pasada, reejecutable e idempotente. Trabaja sobre los
.py que generan el HTML, no sobre el HTML (asi el cambio queda en la fuente y
se regenera solo).

Seguridad de la transformacion:
  - Se tokeniza el codigo (tokenize) y SOLO se tocan literales de string. Nunca
    identificadores, comentarios, nombres de archivo ni claves de diccionario.
  - Dentro de cada string se protege todo lo que va entre '<' y '>' (markup y
    valores de atributos: href, id, class, data-*, style...). Asi un
    href="diagnostico.html" jamas se acentua.
  - Los segmentos que parecen ruta/identificador (sin espacios y con . / : # _
    o todo en minusculas) se dejan intactos.

Se apoya en Mapa de palabras (abajo). Es intencionalmente conservador: prefiere
dejar una palabra sin acentuar antes que romper un valor de codigo.
"""

import io
import os
import re
import tokenize

ARCHIVOS = (
    "lib_ui.py",
    "lib_charts.py",
    "paginas_auth.py",
    "paginas_estudiante.py",
    "paginas_docente.py",
    "paginas_admin.py",
)

# lib_js.py NO se incluye a proposito: su JS vive dentro de un unico string de
# Python, asi que tokenizar no distingue codigo de texto visible y se acentuan
# identificadores y valores maquina (data-accion, #id, sgemd:sesion...). Ese
# archivo ya viene con los acentos puestos solo en el texto visible.

MAPA = {
    # n -> ñ
    "contrasena": "contraseña", "Contrasena": "Contraseña",
    "contrasenas": "contraseñas", "Contrasenas": "Contraseñas",
    # terminacion -cion / -sion
    "descripcion": "descripción", "Descripcion": "Descripción",
    "informacion": "información", "Informacion": "Información",
    "configuracion": "configuración", "Configuracion": "Configuración",
    "creacion": "creación", "Creacion": "Creación",
    "aprobacion": "aprobación", "Aprobacion": "Aprobación",
    "confirmacion": "confirmación", "Confirmacion": "Confirmación",
    "asignacion": "asignación", "Asignacion": "Asignación",
    "validacion": "validación", "Validacion": "Validación",
    "calificacion": "calificación", "Calificacion": "Calificación",
    "ejecucion": "ejecución", "Ejecucion": "Ejecución",
    "ideacion": "ideación", "Ideacion": "Ideación",
    "consolidacion": "consolidación", "Consolidacion": "Consolidación",
    "formacion": "formación", "Formacion": "Formación",
    "capacitacion": "capacitación", "Capacitacion": "Capacitación",
    "inscripcion": "inscripción", "Inscripcion": "Inscripción",
    "revision": "revisión", "Revision": "Revisión",
    "version": "versión", "Version": "Versión",
    "decision": "decisión", "Decision": "Decisión",
    "opcion": "opción", "Opcion": "Opción",
    "poblacion": "población", "Poblacion": "Población",
    "ubicacion": "ubicación", "Ubicacion": "Ubicación",
    "direccion": "dirección", "Direccion": "Dirección",
    "vinculacion": "vinculación", "Vinculacion": "Vinculación",
    "promocion": "promoción", "Promocion": "Promoción",
    "caracterizacion": "caracterización", "Caracterizacion": "Caracterización",
    "valoracion": "valoración", "Valoracion": "Valoración",
    "autenticacion": "autenticación", "Autenticacion": "Autenticación",
    "puntuacion": "puntuación", "Puntuacion": "Puntuación",
    "duracion": "duración", "Duracion": "Duración",
    "seccion": "sección", "Seccion": "Sección",
    "evaluacion": "evaluación", "Evaluacion": "Evaluación",
    "observacion": "observación", "Observacion": "Observación",
    "recomendacion": "recomendación", "Recomendacion": "Recomendación",
    "notificacion": "notificación", "Notificacion": "Notificación",
    "relacion": "relación", "Relacion": "Relación",
    "aplicacion": "aplicación", "Aplicacion": "Aplicación",
    "integracion": "integración", "Integracion": "Integración",
    "organizacion": "organización", "Organizacion": "Organización",
    "participacion": "participación", "Participacion": "Participación",
    "administracion": "administración", "Administracion": "Administración",
    "institucion": "institución", "Institucion": "Institución",
    "educacion": "educación", "Educacion": "Educación",
    "extension": "extensión", "Extension": "Extensión",
    "conclusion": "conclusión", "Conclusion": "Conclusión",
    "gestion": "gestión", "Gestion": "Gestión",
    "mision": "misión", "Mision": "Misión",
    "vision": "visión", "Vision": "Visión",
    "ocasion": "ocasión", "Ocasion": "Ocasión",
    "suscripcion": "suscripción", "Suscripcion": "Suscripción",
    "atencion": "atención", "Atencion": "Atención",
    "satisfaccion": "satisfacción", "Satisfaccion": "Satisfacción",
    "auditoria": "auditoría", "Auditoria": "Auditoría",
    # acentos frecuentes
    "diagnostico": "diagnóstico", "Diagnostico": "Diagnóstico",
    "asesoria": "asesoría", "Asesoria": "Asesoría",
    "asesorias": "asesorías", "Asesorias": "Asesorías",
    "sesion": "sesión", "Sesion": "Sesión",
    "codigo": "código", "Codigo": "Código",
    "telefono": "teléfono", "Telefono": "Teléfono",
    "numero": "número", "Numero": "Número",
    "numeros": "números", "Numeros": "Números",
    "dia": "día", "Dia": "Día", "dias": "días", "Dias": "Días",
    "proximo": "próximo", "Proximo": "Próximo",
    "proximos": "próximos", "Proximos": "Próximos",
    "proxima": "próxima", "Proxima": "Próxima",
    "proximas": "próximas", "Proximas": "Próximas",
    "ultimo": "último", "Ultimo": "Último",
    "ultima": "última", "Ultima": "Última",
    "ultimos": "últimos", "Ultimos": "Últimos",
    "ultimas": "últimas", "Ultimas": "Últimas",
    "metrica": "métrica", "Metrica": "Métrica",
    "metricas": "métricas", "Metricas": "Métricas",
    "pagina": "página", "Pagina": "Página",
    "paginas": "páginas", "Paginas": "Páginas",
    "aqui": "aquí", "Aqui": "Aquí",
    "tambien": "también", "Tambien": "También",
    "ademas": "además", "Ademas": "Además",
    "despues": "después", "Despues": "Después",
    "atras": "atrás", "Atras": "Atrás",
    "metodologia": "metodología", "Metodologia": "Metodología",
    "tecnologia": "tecnología", "Tecnologia": "Tecnología",
    "categoria": "categoría", "Categoria": "Categoría",
    "categorias": "categorías", "Categorias": "Categorías",
    "area": "área", "Area": "Área", "areas": "áreas", "Areas": "Áreas",
    "academico": "académico", "Academico": "Académico",
    "academica": "académica", "Academica": "Académica",
    "practica": "práctica", "Practica": "Práctica",
    "practicas": "prácticas", "Practicas": "Prácticas",
    "analisis": "análisis", "Analisis": "Análisis",
    "estadistica": "estadística", "Estadistica": "Estadística",
    "estadisticas": "estadísticas", "Estadisticas": "Estadísticas",
    "economia": "economía", "Economia": "Economía",
    "historico": "histórico", "Historico": "Histórico",
    "historica": "histórica", "Historica": "Histórica",
    "basico": "básico", "Basico": "Básico",
    "basicos": "básicos", "Basicos": "Básicos",
    "basica": "básica", "Basica": "Básica",
    "basicas": "básicas", "Basicas": "Básicas",
    "publico": "público", "Publico": "Público",
    "unico": "único", "Unico": "Único", "unica": "única", "Unica": "Única",
    "grafico": "gráfico", "Grafico": "Gráfico",
    "graficos": "gráficos", "Graficos": "Gráficos",
    "grafica": "gráfica", "Grafica": "Gráfica",
    "graficas": "gráficas", "Graficas": "Gráficas",
    "linea": "línea", "Linea": "Línea", "lineas": "líneas", "Lineas": "Líneas",
    "limite": "límite", "Limite": "Límite",
    "minimo": "mínimo", "Minimo": "Mínimo", "maximo": "máximo", "Maximo": "Máximo",
    "titulo": "título", "Titulo": "Título",
    "articulo": "artículo", "Articulo": "Artículo",
    "guia": "guía", "Guia": "Guía",
    "envio": "envío", "Envio": "Envío",
    "parrafo": "párrafo", "Parrafo": "Párrafo",
    "credito": "crédito", "Credito": "Crédito",
    "creditos": "créditos", "Creditos": "Créditos",
    "resumenes": "resúmenes", "Resumenes": "Resúmenes",
    "almacen": "almacén", "Almacen": "Almacén",
    # --- segunda pasada (T9): sustantivos -cion/-sion que faltaban -----------
    "actualizacion": "actualización", "Actualizacion": "Actualización",
    "constitucion": "constitución", "Constitucion": "Constitución",
    "coordinacion": "coordinación", "Coordinacion": "Coordinación",
    "definicion": "definición", "Definicion": "Definición",
    "demostracion": "demostración", "Demostracion": "Demostración",
    "dimension": "dimensión", "Dimension": "Dimensión",
    "distribucion": "distribución", "Distribucion": "Distribución",
    "edicion": "edición", "Edicion": "Edición",
    "estimacion": "estimación", "Estimacion": "Estimación",
    "estructuracion": "estructuración", "Estructuracion": "Estructuración",
    "exportacion": "exportación", "Exportacion": "Exportación",
    "formalizacion": "formalización", "Formalizacion": "Formalización",
    "generacion": "generación", "Generacion": "Generación",
    "inversion": "inversión", "Inversion": "Inversión",
    "moderacion": "moderación", "Moderacion": "Moderación",
    "operacion": "operación", "Operacion": "Operación",
    "planificacion": "planificación", "Planificacion": "Planificación",
    "postulacion": "postulación", "Postulacion": "Postulación",
    "precision": "precisión", "Precision": "Precisión",
    "priorizacion": "priorización", "Priorizacion": "Priorización",
    "produccion": "producción", "Produccion": "Producción",
    "recuperacion": "recuperación", "Recuperacion": "Recuperación",
    "segmentacion": "segmentación", "Segmentacion": "Segmentación",
    "solucion": "solución", "Solucion": "Solución",
    "verificacion": "verificación", "Verificacion": "Verificación",
    # --- segunda pasada (T9): enie y acentos frecuentes ----------------------
    "cercania": "cercanía", "Cercania": "Cercanía",
    "manana": "mañana", "Manana": "Mañana",
    "acompanana": "acompaña", "Acompanana": "Acompaña",
    "acompana": "acompaña", "Acompana": "Acompaña",
    "acompanar": "acompañar", "Acompanar": "Acompañar",
    "mas": "más", "Mas": "Más",
    "boton": "botón", "Boton": "Botón",
    "aun": "aún", "Aun": "Aún",
    "todavia": "todavía", "Todavia": "Todavía",
    "envia": "envía", "Envia": "Envía",
    "leidas": "leídas", "Leidas": "Leídas",
    "leidos": "leídos", "Leidos": "Leídos",
    "leida": "leída", "Leida": "Leída",
    "leido": "leído", "Leido": "Leído",
}

# Frases dependientes de contexto (interrogativos, verbos con tilde diacritica)
# que no se pueden resolver palabra por palabra. Se aplican al texto visible.
FRASES = (
    ("Cual es el nombre", "Cuál es el nombre"),
    ("Que tipo de emprendimiento es?", "Qué tipo de emprendimiento es?"),
    ("A que sector productivo pertenece?", "A qué sector productivo pertenece?"),
    ("Que producto o servicio ofreces?", "Qué producto o servicio ofreces?"),
    ("En que etapa del programa esta tu emprendimiento?",
     "En qué etapa del programa está tu emprendimiento?"),
    ("Que problema concreto resuelve", "Qué problema concreto resuelve"),
    ("Como lo resuelven hoy", "Cómo lo resuelven hoy"),
    ("Que tan urgente es el problema", "Qué tan urgente es el problema"),
    ("Que beneficio concreto entrega", "Qué beneficio concreto entrega"),
    ("Que te diferencia de la competencia?", "Qué te diferencia de la competencia?"),
    ("Que necesidad principal cubre?", "Qué necesidad principal cubre?"),
    ("Que canales usaras para llegarles?", "Qué canales usarás para llegarles?"),
    ("Que inversion necesitas para crecer?", "Qué inversión necesitas para crecer?"),
    ("Cual es tu propuesta de valor", "Cuál es tu propuesta de valor"),
    ("Cual es tu estrategia de precio?", "Cuál es tu estrategia de precio?"),
    ("Cual es tu capacidad de produccion actual?",
     "Cuál es tu capacidad de producción actual?"),
    ("Cual es tu meta de ventas", "Cuál es tu meta de ventas"),
    ("Cuantos clientes potenciales estimas?", "Cuántos clientes potenciales estimas?"),
    ("Con cuantas personas cuenta el equipo?", "Con cuántas personas cuenta el equipo?"),
    ("Quien es tu cliente ideal", "Quién es tu cliente ideal"),
    ("A quien le ocurre ese problema?", "A quién le ocurre ese problema?"),
    ("Mas de 5", "Más de 5"),
    ("Como va el cuestionario", "Cómo va el cuestionario"),
    ("Como funciona", "Cómo funciona"),
    ("Como inscribirte", "Cómo inscribirte"),
    ("ves cuanto has avanzado y que te falta", "ves cuánto has avanzado y qué te falta"),
    ("Se detecto que", "Se detectó que"),
    ("Tu evidencia esta en validación", "Tu evidencia está en validación"),
    ("Tu cuenta esta en estado", "Tu cuenta está en estado"),
    ("archivos apareceran", "archivos aparecerán"),
    ("que veras en las otras", "que verás en las otras"),
    ("Para que sirve", "Para qué sirve"),
    ("que el estudiante solicito", "que el estudiante solicitó"),
    ("Como docente tu confirmas", "Como docente tú confirmas"),
    ("Capacidad deDecision", "Capacidad de decisión"),
)

# Literal completo: prefijo de cadena + delimitador (simple, doble o triple).
RE_LITERAL = re.compile(r'^([rRbBuUfF]*)(\"\"\"|\'\'\'|"|\')(.*)(\2)$', re.S | re.M)
RE_TAG = re.compile(r"(<[^>]*>)")
# Placeholders de formato: %(k)s, %s, %%, {...}. No se acentuan por dentro.
RE_PLACEHOLDER = re.compile(r"(%%|%\([^)]*\)[a-zA-Z]|%[sdifgrexXoc]|\{[^{}]*\})")
RE_PALABRA = re.compile(r"\b(\w+)\b", re.UNICODE)
# Heuristica de bloque de codigo (JS/CSS embebido en un string de Python).
RE_BLOQUE = re.compile(
    r"\b(function|addEventListener|document\.|querySelector|localStorage|"
    r"sessionStorage|getElementById|=>)\b"
)


def _es_bloque_codigo(contenido):
    return bool(RE_BLOQUE.search(contenido)) and (";" in contenido or "{" in contenido)



def _parece_codigo(segmento):
    """True si el segmento NO debe acentuarse (ruta, id, clase, css, url...)."""
    s = segmento.strip()
    if not s:
        return False
    if re.search(r"[^\W\d_]", s, re.UNICODE) is None:   # sin letras
        return True
    if re.search(r"\s", s):                              # con espacios -> prosa
        return bool(re.search(r"^(https?://|www\.|/|\.\.?/)", s))
    if re.search(r"[./:#_=<>{}]", s):                    # sin espacios y con estos
        return True
    if s.islower():                                      # todo minusculas -> clave/id
        return True
    return False


def _palabras(texto):
    if _parece_codigo(texto):
        return texto
    # Los placeholders de formato se preservan literales (no se acentuan).
    partes = RE_PLACEHOLDER.split(texto)
    for i in range(0, len(partes), 2):
        seg = partes[i]
        for viejo, nuevo in FRASES:
            if viejo in seg:
                seg = seg.replace(viejo, nuevo)
        partes[i] = RE_PALABRA.sub(lambda m: MAPA.get(m.group(1), m.group(0)), seg)
    return "".join(partes)


def _prosa(contenido):
    """Acentua solo el texto que va fuera de las etiquetas <...>."""
    partes = RE_TAG.split(contenido)
    for i in range(0, len(partes), 2):
        partes[i] = _palabras(partes[i])
    return "".join(partes)


def _transformar_literal(token):
    m = RE_LITERAL.match(token)
    if not m:
        return None
    prefijo, comilla, contenido = m.group(1), m.group(2), m.group(3)
    if _es_bloque_codigo(contenido):
        return None
    nuevo = _prosa(contenido)
    if nuevo == contenido:
        return None
    return prefijo + comilla + nuevo + comilla


def _procesar(nombre):
    crudo = io.open(nombre, encoding="utf-8", newline="").read()
    texto = crudo.replace("\r\n", "\n")
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(texto).readline))
    except Exception as e:  # noqa: BLE001
        print("  ! %s no tokeniza: %s" % (nombre, e))
        return 0

    inicio = [0]
    for linea in texto.splitlines(keepends=True):
        inicio.append(inicio[-1] + len(linea))

    def offset(fila, col):
        return inicio[fila - 1] + col

    cambios = []
    for tok in tokens:
        if tok.type != tokenize.STRING:
            continue
        nuevo = _transformar_literal(tok.string)
        if nuevo is not None:
            cambios.append((offset(*tok.start), offset(*tok.end), nuevo))

    if not cambios:
        return 0
    for a, b, nuevo in sorted(cambios, reverse=True):
        texto = texto[:a] + nuevo + texto[b:]
    io.open(nombre, "w", encoding="utf-8", newline="").write(texto.replace("\n", "\r\n"))
    return len(cambios)


def main():
    total = 0
    for nombre in ARCHIVOS:
        if not os.path.exists(nombre):
            print("FALTA %s" % nombre)
            continue
        n = _procesar(nombre)
        total += n
        print("%-26s %d literales ajustados" % (nombre, n))
    print("total: %d literales con acentos normalizados" % total)


if __name__ == "__main__":
    main()
