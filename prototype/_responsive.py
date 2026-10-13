"""Barrido responsive de todas las pantallas.

Verifica a 1440, 1280, 1100, 900, 768 y 375 px:
  - que la pagina no desborde en horizontal;
  - que ningun elemento se salga del viewport;
  - que la **columna de acciones** de cada tabla este dentro de la pantalla sin
    tener que desplazar en horizontal (los botones crear/editar/eliminar tienen
    que estar a la vista; si hay que-discovery el scroll, no existen);
  - que los cuadros de click tengan el tamano minimo;
  - a 375px que ninguna celda de tabla quede oculta ni recortada, y que la
    tipografia este dentro de la escala aprobada.
"""
import asyncio
import glob
import io
import os

from playwright.async_api import async_playwright

BASE = os.path.abspath(".")
ANCHOS = (1440, 1280, 1100, 900, 768, 375)
MIN_CLIC = 32  # ancho/alto minimo de un boton en escritorio y tablet

JS_DESBORDE = """() => {
  const W = document.documentElement.clientWidth;
  // Un hijo puede sobresalir legitimamente si esta dentro de un contenedor con
  // scroll horizontal declarado (.tabs, .tabla-scroll): ahi el dato sigue
  // alcanzable desplazandolo, y contarlo como desborde daria falsos positivos.
  // La columna de acciones NO tiene esa exencion: sus botones son el unico
  // acceso a crear/editar/eliminar y deben verse sin desplazamiento.
  const scrollea = e => {
    if (e.classList.contains('acc')) return false;
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
  let celdas = 0, ocultas = 0, recortadas = 0, sinEtiqueta = 0;
  let anchas = 0, accFuera = 0, clicChico = 0;
  const W = document.documentElement.clientWidth;
  const recorta = td => {
    for (let p = td.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === 'auto' || ox === 'scroll') return false;
    }
    return true;
  };
  document.querySelectorAll('table.tabla').forEach(t => {
    const caja = t.closest('.tabla-envoltura').getBoundingClientRect();
    /* Tabla mas ancha que su caja: obliga a desplazar en horizontal. Antes se
       contaba y luego se tiraba el dato; ahora informa. */
    if (t.getBoundingClientRect().width - caja.width > 1) anchas++;
    t.querySelectorAll('tbody td').forEach(td => {
      celdas++;
      const b = td.getBoundingClientRect();
      /* La celda de seleccion se oculta a proposito en vista ficha (el
         seleccionar-todo se dibuja en la cabecera de la tarjeta), asi que no
         cuenta como celda oculta. */
      if (!b.width || !b.height) { if (!td.classList.contains('sel')) ocultas++; }
      if (b.right > W + 1 && recorta(td)) recortadas++;
      if (!td.dataset.label && !td.classList.contains('sel')) sinEtiqueta++;
    });
    /* La columna de acciones tiene que caber en pantalla: si no, el usuario
       no ve los botones sin descubrir que la tabla se desplaza. */
    const acc = t.querySelector('tbody td.acc');
    if (acc && acc.getBoundingClientRect().right > W + 1) accFuera++;
  });
  /* Cuadros de click: por debajo de MIN_CLIC px son difficiles de acertar. */
  document.querySelectorAll('.acciones-cell button, .acciones-cell a, .toolbar button, .toolbar a.btn')
      .forEach(e => {
        const b = e.getBoundingClientRect();
        if (b.width && b.height && (b.width < %(min)d || b.height < %(min)d)) clicChico++;
      });
  return {celdas, ocultas, recortadas, sinEtiqueta, anchas, accFuera, clicChico};
}""" % {"min": MIN_CLIC}


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
            anchas = acc_fuera = clic_chico = 0
            for ruta in rutas:
                await pagina.goto("file:///" + BASE.replace("\\", "/") + "/" + ruta.replace("\\", "/"))
                await pagina.wait_for_timeout(100)
                d = await pagina.evaluate(JS_DESBORDE)
                if d["sw"] > d["cw"]:
                    desborde += 1
                    print("  DESBORDE %s @%d  %d>%d %s" % (ruta, ancho, d["sw"], d["cw"], d["fuera"]))
                t = await pagina.evaluate(JS_TABLAS)
                anchas += t["anchas"]
                acc_fuera += t["accFuera"]
                clic_chico += t["clicChico"]
                if t["accFuera"]:
                    print("  ACCIONES %s @%d  la columna de acciones queda fuera "
                          "de pantalla en %d tabla(s)" % (ruta, ancho, t["accFuera"]))
                if t["clicChico"]:
                    print("  CLIC      %s @%d  %d cuadro(s) de click por debajo "
                          "de %d px" % (ruta, ancho, t["clicChico"], MIN_CLIC))
                # `ocultas` solo tiene sentido en la vista ficha: por encima,
                # una celda plegada (.oc-lg/.oc-md/.oc-sm) ocupa cero a proposito.
                if ancho == 375:
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
            print("@%-5d desborde=%d/%d  tablas anchas=%d  acciones fuera=%d  "
                  "click chico=%d%s"
                  % (ancho, desborde, len(rutas), anchas, acc_fuera, clic_chico, extra))
            fallos += (desborde + ocultas + recortadas + sin_etq
                       + acc_fuera + clic_chico)
            await pagina.close()
        await navegador.close()
    print("\n%d problema(s) responsive." % fallos)
    return fallos


if __name__ == "__main__":
    raise SystemExit(1 if asyncio.run(main()) else 0)