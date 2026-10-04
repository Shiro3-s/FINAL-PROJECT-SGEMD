"""Cataloga los controles que hay que volver interactivos.

Agrupa botones, enlaces y campos por clase y atributos data-*, que es lo que
despues consume lib_js.py. Sirve para no inventar enlaces a ciegas.
"""
import collections
import glob
import io
import re

BUTTON = re.compile(r"<button\b([^>]*)>(.*?)</button>", re.S)
LINK = re.compile(r"<a\b([^>]*)>", re.S)
INPUT = re.compile(r"<(input|select|textarea)\b([^>]*)>", re.S)
TAGS = re.compile(r"<[^>]+>", re.S)


def clases(attr):
    m = re.search(r'class="([^"]*)"', attr)
    return m.group(1) if m else ""


def texto(html):
    t = TAGS.sub(" ", html)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:22]


def datos(attr):
    return ",".join(sorted(re.findall(r"(data-[\w-]+)(?:=|\s|>)", attr)))


def main():
    botones = collections.Counter()
    enlaces = collections.Counter()
    campos = collections.Counter()
    sin_accion = 0
    total_b = total_a = total_i = 0

    for ruta in sorted(glob.glob("*/*.html")):
        html = io.open(ruta, encoding="utf-8").read()
        cuerpo = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", html, flags=re.S)

        for attr, inside in BUTTON.findall(cuerpo):
            total_b += 1
            clave = "%s | data=%s" % (clases(attr) or "(sin clase)", datos(attr) or "-")
            botones[clave] += 1
            if not re.search(r"data-|type=\"(submit|reset)\"", attr):
                sin_accion += 1

        for attr in LINK.findall(cuerpo):
            total_a += 1
            if 'href="#"' in attr:
                enlaces["href=# | %s" % (clases(attr) or "(sin clase)")] += 1

        for tag, attr in INPUT.findall(cuerpo):
            total_i += 1
            tipo = re.search(r'type="([^"]*)"', attr)
            campos["%s/%s" % (tag, tipo.group(1) if tipo else "-")] += 1

    print("BOTONES: %d  (sin data-* ni type=submit: %d, con flavor de color: %d)"
          % (total_b, sin_accion, sum(v for k, v in botones.items()
                                       if re.search(r"btn-(acento|primario|peligro|fantasma)", k))))
    for k, v in botones.most_common(28):
        print("%5d  %s" % (v, k))
    print()
    print("ENLACES href=#: %d" % sum(enlaces.values()))
    for k, v in enlaces.most_common(10):
        print("%5d  %s" % (v, k))
    print()
    print("CAMPOS: %d" % total_i)
    for k, v in campos.most_common(12):
        print("%5d  %s" % (v, k))


if __name__ == "__main__":
    main()