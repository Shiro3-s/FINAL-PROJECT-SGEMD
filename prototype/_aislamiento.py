# -*- coding: utf-8 -*-
"""Huella de las pantallas que NO deben cambiar: estudiante, docente y acceso.

lib_ui.py, lib_js.py y lib_css.py son compartidas por los tres roles, asi que
cualquier cambio de comportamiento por defecto se nota en las 32 pantallas de
estudiante, docente y acceso. Este script imprime un hash por pantalla para
comparar antes y despues de un lote:

    python _aislamiento.py _aislamiento_antes.txt   # antes de tocar nada
    ... lote de cambios ...
    python generar.py
    python _aislamiento.py _aislamiento_despues.txt # despues
    Compare-Object (Get-Content _aislamiento_antes.txt) (Get-Content _aislamiento_despues.txt)

Que se hashea y por que: lo unico que produce el modulo de cada rol es el
contenido de <main>. El <style> y el <script> van embebidos en todas las
pantallas, asi que cambian en cuanto se toca una libreria compartida aunque el
resultado sea el mismo; ademas el JS lleva literales <style> y <body> que
confunden cualquier limpieza por expresion regular. Por eso la huella se saca de
<main>...</main> y de nada mas. Un hash distinto ahi si es un cambio real.

Un diff vacio es la prueba de que nada se movio fuera del administrador.

Uso:  python _aislamiento.py [salida.txt]
"""
import hashlib
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
AJENAS = ("compartido", "estudiante", "docente")
CUERPO = re.compile(r"<(main|body)\b", re.I)
FIN = re.compile(r"<(script|style)\b", re.I)


def huella(texto):
    """Hash del contenido propio de la pagina: lo que emite su modulo.

    Se toma desde <main> (o <body> en las pantallas de acceso, que no usan el
    shell de rol) hasta el primer <script> o <style>. Asi el CSS y el JS
    compartidos quedan fuera y solo se ve lo que cambia de verdad."""
    m = CUERPO.search(texto)
    if not m:
        return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:12]
    fin = FIN.search(texto, m.end())
    propio = texto[m.start():fin.start() if fin else len(texto)]
    return hashlib.sha1(propio.encode("utf-8")).hexdigest()[:12]


def huellas():
    """(carpeta/nombre, sha1 corto) de cada pantalla ajena al administrador."""
    out = []
    for carpeta in AJENAS:
        d = os.path.join(BASE, carpeta)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if not n.endswith(".html"):
                continue
            with io.open(os.path.join(d, n), encoding="utf-8") as f:
                h = huella(f.read())
            out.append(("%s/%s" % (carpeta, n), h))
    return out


def main():
    filas = huellas()
    lineas = ["%s  %s" % (h, ruta) for ruta, h in filas]
    if len(sys.argv) > 1:
        destino = sys.argv[1]
        # Al comparar dos archivos se omiten las líneas de resumen, que llevan la
        # fecha y siempre diferirían.
        with io.open(os.path.join(BASE, destino), "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
        print("escrito: %s (%d pantallas)" % (destino, len(lineas)))
    else:
        print("\n".join(lineas))
    admin = len([n for n in os.listdir(os.path.join(BASE, "admin"))
                 if n.endswith(".html")])
    print("# %d pantallas ajenas · %d pantallas de administrador" % (len(lineas), admin))
    return 0


if __name__ == "__main__":
    sys.exit(main())