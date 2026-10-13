# -*- coding: utf-8 -*-
"""Auditoria de enlaces muertos del HTML generado.

Recorre todas las pantallas (y el indice) y verifica que cada href="/src"
relativo apunte a un archivo que exista. Ignora anclas (#...), esquemas
(http/mailto/tel/data/javascript) y data URI.

El atributo se exige precedido de espacio o de "<": sin eso el `location.href`
de un script inline (p. ej. `location.href = "actas.html"`) se tomaria por un
enlace de la pagina, aunque es codigo y no un destino.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ATRIBUTO = re.compile(r'[\s<](?:href|src)\s*=\s*"([^"]+)"')
SCRIPT = re.compile(r"<script\b.*?</script>", re.S)


def resolver(archivo_html, ruta):
    """Convierte una ruta relativa hacia el destino. Devuelve None si no aplica."""
    ruta = ruta.split("#")[0].split("?")[0].strip()
    if not ruta:
        return None
    if ruta.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "//")):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", ruta):
        return None
    base = os.path.dirname(archivo_html)
    destino = os.path.normpath(os.path.join(base, ruta))
    return destino


def main():
    total = 0
    carpetas = ["compartido", "estudiante", "docente", "admin"]
    archivos = [os.path.join(BASE, "index.html")]
    for carpeta in carpetas:
        d = os.path.join(BASE, carpeta)
        if os.path.isdir(d):
            archivos += [os.path.join(d, n) for n in sorted(os.listdir(d))
                         if n.endswith(".html")]
    for a in archivos:
        if not os.path.isfile(a):
            continue
        h = io.open(a, encoding="utf-8").read()
        # Los enlaces que el script arma en tiempo de ejecucion (el buscador de
        # pantallas construye sus <a> con a.getAttribute("href")) no son enlaces
        # de la pagina: apuntan a destinos que ya se comprueban alli donde estan.
        h = SCRIPT.sub("", h)
        refs = ATRIBUTO.findall(h)
        base = os.path.basename(a)
        for r in sorted(set(refs)):
            d = resolver(a, r)
            if d is None or os.path.basename(d) == base:
                continue
            if not os.path.isfile(d):
                print("%s -> %s  [no existe]" % (a.replace(BASE, ".").replace("\\", "/"), r))
                total += 1
    print("\n%d enlace(s) muerto(s)." % total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main() else 0)