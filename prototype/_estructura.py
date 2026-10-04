# -*- coding: utf-8 -*-
"""Verificacion estructural del HTML: balance de etiquetas, landmarks por rol,
accesibilidad basica, coherencia de tablas y riesgo de desbordamiento."""
import glob
import io
import os
import re
import sys
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}
LANDMARKS = ("<main", "<nav", "<aside", "<header")
ROLES = {"estudiante": "ESTUDIANTE", "docente": "DOCENTE", "admin": "ADMINISTRADOR"}

# El logo debe existir UNA sola vez en el DOM. En <=1023px la sidebar sale de
# pantalla y el respaldo decorativo se pinta con `background`, no con un <img>
# mas, asi que un segundo <img> siempre seria un logo duplicado visible.
RE_IMG_LOGO = re.compile(r'<span class="(?:brand-tile|accede-logo)"><img\b', re.I)
RE_COMENTARIOS = re.compile(r'/\*.*?\*/|<!--.*?-->', re.S)


def sin_comentarios(h):
    return RE_COMENTARIOS.sub(" ", h)


class Revisor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila = []
        self.errores = []
        self.img_sin_alt = 0
        self.a_sin_href = 0
        self.campos_sin_label = 0
        self.ancho_fijo = []
        self.prof_label = 0
        self.ids = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids[a["id"]] = self.ids.get(a["id"], 0) + 1
        if tag == "img" and "alt" not in a:
            self.img_sin_alt += 1
        if tag == "a" and "href" not in a:
            self.a_sin_href += 1
        if tag == "label":
            self.prof_label += 1
        if tag in ("input", "select", "textarea"):
            # etiqueta implicita: el control esta dentro de un <label>
            if not (a.get("aria-label") or a.get("id") or a.get("placeholder")
                    or self.prof_label):
                self.campos_sin_label += 1
        if tag not in VACIOS:
            self.pila.append((tag, self.getpos()))
        for k, v in a.items():
            if k == "style" and v:
                m = re.search(r"(?:min-)?width:\s*(\d{3,})px", v)
                if m and int(m.group(1)) > 1180:
                    self.ancho_fijo.append(int(m.group(1)))

    def handle_endtag(self, tag):
        if tag == "label" and self.prof_label:
            self.prof_label -= 1
        if tag in VACIOS:
            return
        if not self.pila:
            self.errores.append("cierre </%s> sin apertura" % tag)
            return
        if self.pila[-1][0] == tag:
            self.pila.pop()
        else:
            for i in range(len(self.pila) - 1, -1, -1):
                if self.pila[i][0] == tag:
                    for j in range(len(self.pila) - 1, i - 1, -1):
                        t, pos = self.pila[j]
                        self.errores.append("<%s> sin cerrar (linea %d)" % (t, pos[0]))
                    del self.pila[i:]
                    return
            self.errores.append("cierre </%s> huerfano" % tag)


CUERPO = re.compile(r"<(style|script)\b.*?</\1>", re.S)


def revisar(archivo, carpeta):
    h = io.open(archivo, encoding="utf-8").read()
    # El documento completo se revisa tal cual porque hay comprobaciones que
    # miran dentro del <style>. Para contar etiquetas de bloque, en cambio, se
    # quita style y script: un comentario de CSS que mencione "<td>" Contaba
    # como celda y daba un falso positivo de desbalance en las 50 pantallas.
    sin_css = CUERPO.sub("", h)
    # El parser ve el documento sin style ni script: el JS embebido contiene
    # cadenas como '<label for="m-campo">' que el parser tomaba por etiquetas
    # reales y reportaba como label huerfano en las 46 pantallas con lib_js.
    r = Revisor()
    r.feed(sin_css)
    r.close()
    for t, pos in r.pila:
        r.errores.append("<%s> sin cerrar (linea %d)" % (t, pos[0]))

    malos = list(r.errores)
    if r.img_sin_alt:
        malos.append("img sin alt x%d" % r.img_sin_alt)
    if r.a_sin_href:
        malos.append("a sin href x%d" % r.a_sin_href)
    if r.campos_sin_label:
        malos.append("campos sin etiqueta x%d" % r.campos_sin_label)
    if r.ancho_fijo:
        malos.append("ancho fijo >1180px: %s" % sorted(set(r.ancho_fijo)))
    repes = sorted(k for k, v in r.ids.items() if v > 1)
    if repes:
        malos.append("id duplicado x%s" % repes[:6])
    huerfanos = sorted(set(re.findall(r'<label for="([^"]+)"', sin_css)) - set(r.ids))
    if huerfanos:
        malos.append("label for sin control: %s" % huerfanos[:6])
    if carpeta != "compartido" and not all(l in h for l in LANDMARKS):
        faltan = [l for l in LANDMARKS if l not in h]
        malos.append("faltan landmarks %s" % faltan)
    if sin_css.count("<tr") != sin_css.count("</tr>"):
        malos.append("tr desbalanceados %d/%d"
                     % (sin_css.count("<tr"), sin_css.count("</tr>")))
    if sin_css.count("<td") != sin_css.count("</td>"):
        malos.append("td desbalanceados %d/%d"
                     % (sin_css.count("<td"), sin_css.count("</td>")))

    rol = ROLES.get(carpeta)
    if rol and ('>%s<' % rol) not in h:
        malos.append("falta el badge de rol %s" % rol)

    # --- logo unico ---------------------------------------------------------
    limpio = sin_comentarios(h)
    n_logo = len(RE_IMG_LOGO.findall(limpio))
    if n_logo != 1:
        malos.append("logo en el DOM: %d <img> (se espera 1)" % n_logo)
    if carpeta != "compartido":
        # Las pantallas de acceso usan un lockup grande propio, no el shell.
        if limpio.count("class=\"topbar-mark\"") > 1:
            malos.append("topbar-mark repetido")
        if limpio.count(".shell:has(.sidebar.abierto) .topbar-mark") != 1:
            malos.append("falta la regla que oculta topbar-mark con el drawer abierto")
        if not re.search(r'\.brand-tile\{[^}]*width:180px', limpio):
            malos.append("el lockup de la sidebar no mide 180px")
    return malos


PRESUPUESTO_INLINE = 699
SIN_CSS = re.compile(r"<style>.*?</style>", re.S)
STYLE_ATTR = re.compile(r'style="([^"]*)"')
# Anchos fijos declarados en linea: son los que no pueden adaptarse a 375px y
# por eso se vigilan aparte, aunque el total de style= ya quepa en el presupuesto.
FIJOS = re.compile(r"(?:min-)?width:\s*[0-9]+px")


def revisar_inline():
    """Frena la deuda de estilos en linea.

    Quedan 699 usos, casi todos colores semanticos de estado y anchos en
    porcentaje que no estorban al responsive. No se extraen todos porque el
    beneficio es estetico y el riesgo de regresion sobre 50 pantallas es alto;
    lo que se garantiza es que la cifra no vuelva a crecer.
    """
    malos = []
    total = 0
    fijos = 0
    for carpeta in ("compartido", "estudiante", "docente", "admin"):
        d = os.path.join(BASE, carpeta)
        if not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, "*.html"))):
            html = io.open(f, encoding="utf-8").read()
            estilos = STYLE_ATTR.findall(SIN_CSS.sub("", html))
            total += len(estilos)
            fijos += sum(1 for e in estilos if FIJOS.search(e))
    if total > PRESUPUESTO_INLINE:
        malos.append("estilos inline: %d, supera el presupuesto de %d"
                     % (total, PRESUPUESTO_INLINE))
    print("estilos inline: %d / %d   anchos fijos en linea: %d"
          % (total, PRESUPUESTO_INLINE, fijos))
    return malos


def main():
    total = 0
    for carpeta in ("compartido", "estudiante", "docente", "admin"):
        d = os.path.join(BASE, carpeta)
        if not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, "*.html"))):
            malos = revisar(f, carpeta)
            if malos:
                print("%s/%s" % (carpeta, os.path.basename(f)))
                for x in sorted(set(malos)):
                    print("   -", x)
                total += len(set(malos))
    inline = revisar_inline()
    for x in inline:
        print("   -", x)
    total += len(inline)
    print("\n%d problema(s) estructural(es)." % total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main() else 0)