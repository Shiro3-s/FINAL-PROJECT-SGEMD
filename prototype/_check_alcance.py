# -*- coding: utf-8 -*-
"""Auditoria de alcance del panel: pantallas huerfanas y listados sin CRUD.

Dos preguntas que los otros validadores no responden:

  1. ¿Se puede llegar a cada pantalla? Una pantalla que nadie enlaza (ni el
     indice, ni el menú, ni un boton de otra pantalla) es codigo muerto: se
     genera en cada `generar.py` y no lo encuentra nadie.
  2. ¿Cada listado del administrador se puede administrar de verdad? Un listado
     sin forma de crear, editar, eliminar ni ver es una foto: se ve, no se
     opera.

Las subpantillas son legitimas siempre que la pantalla madre las enlace, asi
que el criterio de la primera pregunta es alcanzabilidad, no "tiene entrada en
el menu". Las excepciones de la segunda estan declaradas abajo con su motivo:
sin ellas, el validador gritaria sobre decisiones ya tomadas.

Uso: python _check_alcance.py
"""
import io
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETAS = ("compartido", "estudiante", "docente", "admin")
ATRIBUTO = re.compile(r'[\s<]href\s*=\s*"([^"]+)"')

# Las cuatro operaciones de un listado administrable. Se pide "al menos una de",
# porque cada pantalla elige el boton que le corresponde.
OPERACIONES = {
    "crear": ("nuevo-fila", "nuevo-usuario", "nuevo-emprendimiento", "crear",
              "crear-emprendimiento", "nuevo"),
    "editar": ("editar-fila", "editar", "editar-docente", "editar-estudiante",
               "gestion-usuario", "registrar-avance", "alternar-estado"),
    "eliminar": ("borrar-fila", "borrar", "retirar-emprendimiento"),
    "ver": ("ver-fila", "ver", "ver-detalle", "ver-usuario", "detalle"),
}

# Decisiones ya tomadas: que operacion se cubre con otra cosa y por que.
SUSTITUIDO = {
    # El candado desactiva el acceso: es el "eliminar" del perfil de usuario,
    # porque un usuario con historia pedagogica no se borra, se suspende.
    "eliminar": ("usuarios.html", "alternar-estado (desactivar acceso)"),
}

# Pantallas cuya tabla es de solo lectura por diseno. La lista es explicita
# para que anadir una tabla nueva no se lleve por delante la exencion.
SOLO_LECTURA = {
    "dashboard.html": "bitacora de actividad: refleja lo que paso, no se edita",
    "reportes.html": "vista previa de la exportacion: el origen son los datos",
    "sedes-carreras.html": "oferta academica: la fuente es el catalogo",
}


def pantallas():
    """(ruta, nombre, carpeta) de cada HTML generado."""
    out = [os.path.join(BASE, "index.html")]
    for carpeta in CARPETAS:
        d = os.path.join(BASE, carpeta)
        if os.path.isdir(d):
            out += [os.path.join(d, n) for n in sorted(os.listdir(d))
                    if n.endswith(".html")]
    return [p for p in out if os.path.isfile(p)]


def referencias():
    """Cuenta a quien apunta cada enlace del prototipo (nombre -> enlaces)."""
    ref = Counter()
    for p in pantallas():
        h = io.open(p, encoding="utf-8").read()
        for r in ATRIBUTO.findall(h):
            ref[os.path.basename(r.split("#")[0].split("?")[0])] += 1
    return ref


def huerfanas(ref):
    """Pantallas de rol a las que no llega ningun enlace."""
    out = []
    for p in pantallas():
        base = os.path.basename(p)
        if base == "index.html":
            continue
        if not ref[base]:
            out.append(p)
    return out


def sin_crud(nombre, h):
    """Operaciones que le faltan a un listado administrable, o None.

    Solo se miran los controles visibles: el bloque <script> lleva las plantillas
    del generador y ahi aparecen acciones que el usuario nunca ve.
    """
    cuerpo = re.sub(r"<script\b.*?</script>", "", h, flags=re.S)
    if "<table" not in cuerpo:
        return None  # no es un listado
    if nombre in SOLO_LECTURA:
        return None  # tabla de solo lectura, por decision documentada
    acciones = set(re.findall(r'data-accion="([a-z0-9-]+)"', cuerpo))
    faltan = []
    for op, alias in sorted(OPERACIONES.items()):
        if any(a in acciones for a in alias):
            continue
        sustituto = SUSTITUIDO.get(op)
        if sustituto and sustituto[0] == nombre:
            continue  # cubierto por decision documentada
        faltan.append(op)
    return faltan or None


def main():
    ref = referencias()
    total = 0

    huerf = huerfanas(ref)
    if huerf:
        print("PANTALLAS HUERFANAS (%d): ninguna pantalla las enlaza" % len(huerf))
        for p in huerf:
            print("   - %s" % p.replace(BASE, ".").replace("\\", "/"))
        total += len(huerf)
    else:
        print("pantallas huerfanas: 0")

    admin = os.path.join(BASE, "admin")
    if os.path.isdir(admin):
        sin = []
        for n in sorted(os.listdir(admin)):
            if not n.endswith(".html"):
                continue
            h = io.open(os.path.join(admin, n), encoding="utf-8").read()
            faltan = sin_crud(n, h)
            if faltan:
                sin.append((n, faltan))
        if sin:
            print("\nLISTADOS SIN ADMINISTRAR (%d): tienen tabla pero no se "
                  "pueden crear, editar, eliminar ni ver" % len(sin))
            for n, faltan in sin:
                print("   - %s  falta: %s" % (n, ", ".join(faltan)))
            total += len(sin)
        else:
            print("listados sin administrar: 0")

    print("\n%d problema(s) de alcance." % total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main() else 0)