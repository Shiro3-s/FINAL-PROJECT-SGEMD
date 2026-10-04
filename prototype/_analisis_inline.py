"""Analiza los estilos inline del HTML generado para decidir que extraer a clases."""
import collections
import glob
import io
import re

cuerpo_sin_css = re.compile(r"<style>.*?</style>", re.S)

distintos = collections.Counter()
por_prop = collections.Counter()
inline = re.compile(r'style="([^"]*)"')

total = 0
for ruta in sorted(glob.glob("*/*.html")):
    html = io.open(ruta, encoding="utf-8").read()
    cuerpo = cuerpo_sin_css.sub("", html)
    for bruto in inline.findall(cuerpo):
        total += 1
        limpio = ";".join(x.strip() for x in bruto.split(";") if x.strip())
        distintos[limpio] += 1
        for decl in limpio.split(";"):
            if ":" in decl:
                por_prop[decl.split(":")[0].strip()] += 1

print("estilos inline: %d usos, %d combinaciones distintas" % (total, len(distintos)))
print()
print("=== las 34 combinaciones mas repetidas ===")
for k, v in distintos.most_common(34):
    print("%5d  %s" % (v, k[:100]))
acumulado = sum(v for _, v in distintos.most_common(34))
print()
print("esas 34 cubren %d usos (%.0f%% del total)" % (acumulado, 100.0 * acumulado / total))
print()
print("=== propiedades ===")
for k, v in por_prop.most_common(28):
    print("%5d  %s" % (v, k))