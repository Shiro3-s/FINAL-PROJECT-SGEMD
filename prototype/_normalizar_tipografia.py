"""Normaliza la escala tipografica y los interlineados de los generadores.

Correccion de una sola pasada, reejecutable e idempotente: recorre los .py que
generan el HTML y reescribe cada `font-size:Npx` y `line-height:N` con el mapa de
abajo. Se aplica de una sola vez sobre la fuente, no sobre el HTML, para que el
cambio quede en el codigo y se regenere solo.

Escala objetivo: 8 pasos, todos en pixeles enteros y con 13px como minimo.

    32  28  24  20  18  16  14  13

Los 17 valores que existian antes incluian medios pixeles (14.5, 13.5, 12.5,
11.5) y cinco pasos por debajo de 13px, que a 375px de ancho no se leen. Los
sub-13 suben a 13: son etiquetas y badges, no texto corrido, y a 13px siguen
siendo legibles.

Interlineado: se elimina 1 y 1.1, que son demasiado cerrados para leer.
"""

import io
import os
import re

ARCHIVOS = (
    "lib_css.py",
    "lib_ui.py",
    "lib_charts.py",
    "paginas_auth.py",
    "paginas_estudiante.py",
    "paginas_docente.py",
    "paginas_admin.py",
    "generar.py",
)

# tamano -> tamano
TAMANOS = {
    "34": "32",
    "30": "28",
    "26": "28",
    "22": "20",
    "15": "14",
    "14.5": "14",
    "13.5": "13",
    "12.5": "13",
    "12": "13",
    "11.5": "13",
    "11": "13",
}

INTERLINEADOS = {
    "1": "1.4",
    "1.1": "1.4",
    "1.25": "1.3",
    "1.35": "1.4",
}

RE_FONT = re.compile(r"(font-size:\s*)([0-9]+(?:\.[0-9]+)?)(px)")
RE_LINE = re.compile(r"(line-height:\s*)([0-9]+(?:\.[0-9]+)?)")


def main():
    total_font = 0
    total_line = 0
    for nombre in ARCHIVOS:
        if not os.path.exists(nombre):
            print("FALTA %s" % nombre)
            continue
        texto = io.open(nombre, encoding="utf-8", newline="").read()

        cambios = [0]

        def sub_fuente(m):
            nuevo = TAMANOS.get(m.group(2))
            if nuevo and nuevo != m.group(2):
                cambios[0] += 1
                return m.group(1) + nuevo + "px"
            return m.group(0)

        def sub_linea(m):
            nuevo = INTERLINEADOS.get(m.group(2))
            if nuevo and nuevo != m.group(2):
                cambios[0] += 1
                return m.group(1) + nuevo
            return m.group(0)

        nuevo_texto = RE_LINE.sub(sub_linea, RE_FONT.sub(sub_fuente, texto))
        if nuevo_texto != texto:
            io.open(nombre, "w", encoding="utf-8", newline="").write(nuevo_texto)
        total_font += cambios[0]
        print("%-26s %d ajustes" % (nombre, cambios[0]))
    print("total: %d ajustes en fuente e interlineado" % (total_font + total_line))


if __name__ == "__main__":
    main()