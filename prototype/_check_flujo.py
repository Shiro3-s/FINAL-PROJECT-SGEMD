# -*- coding: utf-8 -*-
"""G8: validador del flujo de trabajo del administrador.

Los validadores anteriores miran el color, los enlaces, el desborde y que los
botones tengan un gancho. Este mira lo que el administrador tiene que poder
hacer, y cuatro reglas queemedicine costaron un bug cada una:

  1. Inmersion: ninguna pantalla del admin puede decir "prototipo".
  2. Obligatorios: un campo con el asterisco debe llevar `required`, o la
     validacion nunca dispara.
  3. Seguridad: todo boton de eliminar pasa por confirmacion.
  4. Descarga: toda tabla con datos debe poder bajarse.
  5. Formulario: cada boton de editar tiene que abrir un formulario real.

Uso: python _check_flujo.py
"""
import glob
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ADMIN = os.path.join(BASE, "admin")

# Frases que delatan que la pantalla no es el producto.
INMERSION = re.compile(
    r"(?i)(vista de prototipo|prototipo de interfaz|cuentas de demostraci|"
    r"el prototipo valida|sin servidor|en construcci|coming soon)")

CUERPO = re.compile(r"<(main)\b", re.I)
FUERA = re.compile(r"<(script|style)\b", re.I)


def cuerpo(h):
    """El contenido visible: sin el script que lo construye ni los estilos."""
    m = CUERPO.search(h)
    base = h[m.start():] if m else h
    f = FUERA.search(base)
    return base[:f.start()] if f else base


def revisar():
    fallos = 0
    total = 0
    for nombre in sorted(os.listdir(ADMIN)):
        if not nombre.endswith(".html"):
            continue
        total += 1
        ruta = os.path.join(ADMIN, nombre)
        h = io.open(ruta, encoding="utf-8").read()
        v = cuerpo(h)
        malos = []

        # 1. Inmersion
        for frase in INMERSION.finditer(v):
            malos.append("inmersion: %s" % frase.group(0))

        # 2. Campo obligatorio sin `required`. Se compara por formulario: si
        #    hay mas asteriscos que atributos required, hay campos marcados como
        #    obligatorios que el validador nunca va a revisar.
        for form in re.finditer(r"<form\b.*?</form>", v, re.S):
            bloque = form.group(0)
            marcados = bloque.count('class="req"')
            revisados = len(re.findall(r"\brequired\b", bloque))
            if marcados > revisados:
                malos.append("obligatorios sin required: %d de %d"
                             % (marcados - revisados, marcados))

        # 3. Borrar sin confirmacion.
        if re.search(r'data-accion="(borrar|borrar-fila|retirar-emprendimiento)"', v):
            if 'data-accion="confirmar"' not in h and "confirmar(" not in h:
                malos.append("borrar sin confirmacion")

        # 4. Tabla con datos sin forma de descargarla.
        if "<table" in v and "data-export" not in v and "data-crud-tbody" not in v:
            malos.append("tabla sin descarga")

        # 5. Editar que no abre formulario.
        if re.search(r'data-accion="(editar|editar-fila|editar-docente|'
                     r'editar-estudiante|gestion-usuario)"', v):
            if "abrirCrud" not in h and "editarPerfil" not in h and "abrirEditor" not in h:
                malos.append("editar sin formulario")

        if malos:
            print("admin/%s" % nombre)
            for m in malos:
                print("   - %s" % m)
            fallos += len(malos)

    print("\n%d pantalla(s) de administrador revisadas." % total)
    print("%d problema(s) de flujo." % fallos)
    return fallos


if __name__ == "__main__":
    sys.exit(1 if revisar() else 0)