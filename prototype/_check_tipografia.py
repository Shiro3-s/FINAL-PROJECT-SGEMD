"""Comprueba que la tipografia este dentro de la escala aprobada.

Falla si aparece un tamano fuera de la escala de 8 pasos o por debajo de 13px, y
si queda un interlineado mas cerrado que 1.15.
"""

import glob
import io
import re
import sys

ESCALA = {"32", "28", "24", "20", "18", "16", "14", "13"}
MINIMO = 13
INTERLINEADO_MINIMO = 1.15

RE_FONT = re.compile(r"font-size:\s*([0-9]+(?:\.[0-9]+)?)px")
RE_FONT_STYLE = re.compile(r'style="[^"]*?font-size:\s*([0-9]+(?:\.[0-9]+)?)px')
RE_LINE = re.compile(r"line-height:\s*([0-9]+(?:\.[0-9]+)?)")


def main():
    malos = 0
    for ruta in sorted(glob.glob("*/*.html")) + sorted(glob.glob("*.html")):
        html = io.open(ruta, encoding="utf-8").read()
        for valor in set(RE_FONT.findall(html)) | set(RE_FONT_STYLE.findall(html)):
            if valor not in ESCALA:
                print("%s  font-size:%spx fuera de la escala" % (ruta, valor))
                malos += 1
            elif float(valor) < MINIMO:
                print("%s  font-size:%spx por debajo del minimo %d" % (ruta, valor, MINIMO))
                malos += 1
        for valor in set(RE_LINE.findall(html)):
            if float(valor) < INTERLINEADO_MINIMO:
                print("%s  line-height:%s mas cerrado de lo permitido" % (ruta, valor))
                malos += 1
    print("%d problema(s) de tipografia." % malos)
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())