# -*- coding: utf-8 -*-
"""Auditoria del HTML generado: placeholders, %% sin expandir, hex fuera de paleta,
texto corrupto y tablas anidadas en tarjetas."""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PALETA = {"ffd300", "ffffff", "162644", "051533", "004a93", "bbbbbb"}
NO_ASCII_OK = set("\u00b7\u2014\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00c1\u00c9\u00cd\u00d3\u00da"
                  "\u00d1\u00dc\u00fc\u00bf\u00a1\u2026\u00a0\u2192\u2022")


def rgba_ok(h):
    m = re.match(r"rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([\d.]+)\s*\)", h)
    if not m:
        return False
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    return ("%02x%02x%02x" % (r, g, b)).lower() in PALETA


# Bloques que definen como se ve una pantalla. Dos paginas del mismo rol con
# la misma secuencia son clones, aunque cambien los textos.
BLOQUES = [
    ("tabla", r"<table\b"),
    ("kanban", r'class="kanban"'),
    ("linea", r'class="linea"'),
    ("agenda", r'class="agenda"'),
    ("tarjetas", r'class="emp-card"'),
    ("dist", r'class="dist"'),
    ("avisos", r'class="avisos"'),
    ("metricas", r'class="metricas"'),
    ("callout", r'class="callout'),
    ("tabs", r'class="tabs"'),
    ("steps", r'class="steps"'),
    ("form", r"<form\b"),
    ("chart", r'class="chart'),
]


def esqueleto(h):
    """Firma de bloques visibles del contenido, sin texto ni CSS."""
    cuerpo = h
    m = re.search(r"<main\b.*?</main>", h, re.S)
    if m:
        cuerpo = m.group(0)
    found = [n for n, rx in BLOQUES if re.search(rx, cuerpo)]
    return "+".join(found) if len(found) >= 3 else ""


def main():
    total = 0
    firmas = {}
    for carpeta in ("compartido", "estudiante", "docente", "admin"):
        d = os.path.join(BASE, carpeta)
        if not os.path.isdir(d):
            continue
        for nom in sorted(os.listdir(d)):
            if not nom.endswith(".html"):
                continue
            h = io.open(os.path.join(d, nom), encoding="utf-8").read()
            malos = []

            # --- clon real: dos pantallas del mismo rol con el mismo esqueleto
            firma = esqueleto(h)
            if firma:
                firmas.setdefault((carpeta, firma), []).append(nom)

            for ph in set(re.findall(r"__[A-Z_]+__", h)):
                malos.append("placeholder sin resolver %s" % ph)

            n = h.count("%%")
            if n:
                malos.append("%% sin expandir x%d" % n)

            for c in sorted(set(re.findall(r"#([0-9a-fA-F]{6})\b", h))):
                if c.lower() not in PALETA:
                    malos.append("hex fuera de paleta #%s" % c)

            for c in sorted(set(re.findall(r"rgba\([^)]*\)", h))):
                if not rgba_ok(c):
                    malos.append("rgba no derivado %s" % c)

            for ch in sorted(set(h)):
                if ord(ch) > 127 and ch not in NO_ASCII_OK:
                    malos.append("caracter raro U+%04X" % ord(ch))

            n = len(re.findall(r'class="card"[^>]*>(?:(?!</div>).)*?class="card tabla-envoltura"',
                               h, re.S))
            if n:
                malos.append("tabla dentro de card x%d" % n)

            if not h.startswith("<!DOCTYPE html>"):
                malos.append("sin DOCTYPE")
            if h.count("<html") != 1 or h.count("</html>") != 1:
                malos.append("html desbalanceado")

            if malos:
                print("%s/%s" % (carpeta, nom))
                for x in malos:
                    print("   -", x)
                total += len(malos)

    for (carpeta, firma), noms in sorted(firmas.items()):
        if len(noms) < 2:
            continue
        print("%s/  CLONES (%d pantallas)" % (carpeta, len(noms)))
        print("   - mismo esqueleto: %s" % firma)
        for n in noms:
            print("     *", n)
        total += len(noms) - 1

    print("\n%d problema(s) total." % total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main() else 0)