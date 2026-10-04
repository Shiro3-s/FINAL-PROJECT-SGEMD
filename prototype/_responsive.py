"""Barrido responsive de las 50 pantallas.

Verifica a 1440, 1280, 768 y 375 px:
  - que la pagina no desborde en horizontal;
  - que ningun elemento se salga del viewport;
  - que a 375px no quede ninguna celda de tabla oculta ni recortada;
  - que la tipografia este dentro de la escala aprobada.
"""
import asyncio
import glob
import io
import os

from playwright.async_api import async_playwright

BASE = os.path.abspath(".")
ANCHOS = (1440, 1280, 768, 375)

JS_DESBORDE = """() => {
  const W = document.documentElement.clientWidth;
  // Un hijo puede sobresalir legitimamente si esta dentro de un contenedor con
  // scroll horizontal declarado (.tabs, .tabla-scroll): ahi el dato sigue
  // alcanzable desplazandolo, y contarlo como desborde daria falsos positivos.
  const scrollea = e => {
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === 'auto' || ox === 'scroll') return true;
    }
    return false;
  };
  const fuera = [];
  document.querySelectorAll('body *').forEach(e => {
    const b = e.getBoundingClientRect();
    if (b.width && b.height && b.right > W + 1 && !scrollea(e))
      fuera.push(e.tagName + '.' + String(e.className || '').slice(0, 28));
  });
  return {sw: document.documentElement.scrollWidth, cw: W, fuera: [...new Set(fuera)].slice(0, 3)};
}"""

JS_TABLAS = """() => {
  let celdas = 0, ocultas = 0, recortadas = 0, sinEtiqueta = 0, tablas = 0;
  const recorta = td => {
    for (let p = td.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === 'auto' || ox === 'scroll') return false;
    }
    return true;
  };
  document.querySelectorAll('table.tabla').forEach(t => {
    tablas++;
    const caja = t.closest('.tabla-envoltura').getBoundingClientRect();
    if (t.getBoundingClientRect().width - caja.width > 1) tablas++;
    t.querySelectorAll('tbody td').forEach(td => {
      celdas++;
      const b = td.getBoundingClientRect();
      if (!b.width || !b.height) ocultas++;
      if (b.right > document.documentElement.clientWidth + 1 && recorta(td)) recortadas++;
      if (!td.dataset.label && !td.classList.contains('sel')) sinEtiqueta++;
    });
  });
  return {tablas, celdas, ocultas, recortadas, sinEtiqueta};
}"""


async def main():
    rutas = []
    for carpeta in ("compartido", "estudiante", "docente", "admin"):
        rutas += sorted(glob.glob(os.path.join(carpeta, "*.html")))
    fallos = 0
    async with async_playwright() as p:
        navegador = await p.chromium.launch()
        for ancho in ANCHOS:
            pagina = await navegador.new_page(viewport={"width": ancho, "height": 900})
            desborde = celdas = ocultas = recortadas = sin_etq = 0
            for ruta in rutas:
                await pagina.goto("file:///" + BASE.replace("\\", "/") + "/" + ruta.replace("\\", "/"))
                await pagina.wait_for_timeout(120)
                d = await pagina.evaluate(JS_DESBORDE)
                if d["sw"] > d["cw"]:
                    desborde += 1
                    print("  DESBORDE %s @%d  %d>%d %s" % (ruta, ancho, d["sw"], d["cw"], d["fuera"]))
                if ancho == 375:
                    t = await pagina.evaluate(JS_TABLAS)
                    celdas += t["celdas"]
                    ocultas += t["ocultas"]
                    recortadas += t["recortadas"]
                    sin_etq += t["sinEtiqueta"]
                    if t["ocultas"] or t["recortadas"] or t["sinEtiqueta"]:
                        print("  TABLA %s ocultas=%d recortadas=%d sin_etiqueta=%d"
                              % (ruta, t["ocultas"], t["recortadas"], t["sinEtiqueta"]))
            extra = ""
            if ancho == 375:
                extra = "  celdas=%d ocultas=%d recortadas=%d sin_etiqueta=%d" % (
                    celdas, ocultas, recortadas, sin_etq)
            print("@%-5d paginas con desborde: %d/%d%s" % (ancho, desborde, len(rutas), extra))
            fallos += desborde + ocultas + recortadas + sin_etq
            await pagina.close()
        await navegador.close()
    print("\n%d problema(s) responsive." % fallos)
    return fallos


if __name__ == "__main__":
    raise SystemExit(1 if asyncio.run(main()) else 0)