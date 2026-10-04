"""Fase 5: los tres accesos de demostracion, ejecutados en Chromium.

Cada cuenta se recorre como lo haria quien revisa el prototipo: pulsar la fila
del panel, enviar el formulario y comprobar a donde se llega y que quedo
guardado en localStorage. Se comprueba tambien el rechazo de una contrasena
equivocada y que el mensaje de error quede asociado al campo.

Cada HTML se sirve por file://, igual que en Stitch: sin servidor, sin rutas.
"""
import asyncio
import json
import os
import urllib.parse

from playwright.async_api import async_playwright

BASE = os.path.abspath(".")
LOGIN = "compartido/login.html"

CUENTAS = [
    ("estudiante", "../estudiante/dashboard.html"),
    ("profesor", "../docente/dashboard.html"),
    ("admi", "../admin/dashboard.html"),
]

JS_ENTRADA = r"""async (usuario) => {
  const esperar = ms => new Promise(r => setTimeout(r, ms));
  const salida = {};

  // 1) La fila del panel completa los dos campos.
  const fila = document.querySelector(`[data-demo="${usuario}"]`);
  salida.hayFila = !!fila;
  if (fila) fila.click();
  await esperar(60);
  salida.usuarioPuesto = document.getElementById('usuario').value;
  salida.clavePuesta = document.getElementById('clave').value.length > 0;

  // 2) Con la contrasena equivocada no debe pasar nada y debe avisar.
  document.getElementById('clave').value = 'no-es-la-clave';
  document.getElementById('acceso').requestSubmit();
  await esperar(120);
  salida.avisoError = (() => {
    const e = document.getElementById('acceso-error');
    return !e.hidden && /incorrect/i.test(e.textContent);
  })();
  salida.seQuedoEnLogin = location.pathname.endsWith('login.html');
  salida.marcoInvalido = document.getElementById('clave').getAttribute('aria-invalid') === 'true';
  salida.avisoAsociado = document.getElementById('clave').getAttribute('aria-describedby') === 'acceso-error';

  // 3) Con la credencial correcta se entra y se guarda la sesion.
  document.querySelector(`[data-demo="${usuario}"]`).click();
  await esperar(60);
  document.getElementById('acceso').requestSubmit();
  await esperar(120);
  salida.avisoOk = !document.getElementById('acceso-ok').hidden;
  salida.sesion = localStorage.getItem('sgemd:sesion');
  salida.destinoEsperado = "__DESTINO__";
  return salida;
}"""


async def main():
    fallos = 0
    async with async_playwright() as p:
        navegador = await p.chromium.launch()
        pagina = await navegador.new_page(viewport={"width": 1280, "height": 900})
        url = "file:///" + urllib.parse.quote(BASE.replace("\\", "/") + "/" + LOGIN)

        for usuario, destino in CUENTAS:
            errores = []
            pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            await pagina.goto(url)
            await pagina.wait_for_timeout(150)

            r = await pagina.evaluate(JS_ENTRADA.replace('"__DESTINO__"', json.dumps(destino)), usuario)
            # La redireccion es a un archivo real de la misma carpeta: en file://
            # el salto ocurre dentro del margen de la prueba.
            await pagina.wait_for_url("**/" + destino.split("/")[-1], timeout=4000)
            await pagina.wait_for_timeout(200)
            r["urlFinal"] = pagina.url
            r["llego"] = pagina.url.endswith(destino.split("/")[-1])

            malos = []
            for clave, valor in (
                ("hayFila", True),
                ("usuarioPuesto", usuario),
                ("clavePuesta", True),
                ("avisoError", True),
                ("seQuedoEnLogin", True),
                ("marcoInvalido", True),
                ("avisoAsociado", True),
                ("avisoOk", True),
                ("llego", True),
            ):
                if r.get(clave) != valor:
                    malos.append("%s=%r (esperado %r)" % (clave, r.get(clave), valor))
            try:
                sesion = json.loads(r["sesion"] or "{}")
            except ValueError:
                sesion = {}
            if sesion.get("usuario") != usuario or not sesion.get("rol"):
                malos.append("sesion=%r" % (r.get("sesion"),))
            if errores:
                malos.append("consola=%s" % errores[:2])

            if malos:
                fallos += 1
                print("  FALLA %-11s %s" % (usuario, malos))
            else:
                print("  ok    %-11s rol=%-14s -> %s" % (usuario, sesion.get("rol"), destino))

            await pagina.goto(url)
            await pagina.wait_for_timeout(100)
            await pagina.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

        # El buscador de la cabecera del shell y el resto de paginas de rol ya
        # se cubrieron en _interaccion.py; aqui solo el arranque en sesion.
        await navegador.close()
    print("\n%d fallo(s) de acceso." % fallos)
    return fallos


if __name__ == "__main__":
    raise SystemExit(1 if asyncio.run(main()) else 0)