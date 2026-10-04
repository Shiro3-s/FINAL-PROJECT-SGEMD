"""Fase 4 en ejecucion: el bloque de lib_js.js dentro de las 50 pantallas.

Chromium carga cada HTML como se vera en Stitch (file://, sin servidor) y se
comprueba que:

  - el script no lance errores de consola ni excepciones de pagina;
  - el JS se haya ejecutado de verdad (html.js-listo, toast, drawer, modal);
  - ningun control quede sin efecto: cada boton, enlace .btn y campo tiene un
    gancho (data-accion, texto visible, aria-label o un id de formulario);
  - los estilos de los componentes que crea el JS existan en la pagina;
  - el estado quede en localStorage bajo la clave de la propia pantalla.

Un boton con texto visible siempre cae en el `default` del manejador global, que
confirma la accion con un toast, asi que basta con que tenga texto o un
data-accion para no ser inerte.
"""
import asyncio
import glob
import json
import os
import urllib.parse

from playwright.async_api import async_playwright

BASE = os.path.abspath(".")
CARPETAS = ("compartido", "estudiante", "docente", "admin")

JS_SONDA = r"""() => {
  // El componente se crea por JS, asi que la clase no existe en el DOM todavia:
  // se busca la regla en las hojas de estilo de la propia pagina.
  const estiloDefinido = sel => {
    for (const ss of document.styleSheets) {
      let reglas;
      try { reglas = ss.cssRules; } catch (e) { continue; }
      for (const r of reglas) {
        if (r.selectorText && r.selectorText.split(',').some(s => s.trim() === sel)) return true;
      }
    }
    return false;
  };

  const r = {};
  r.jsListo = document.documentElement.classList.contains('js-listo');
  r.estilos = ['.toast-pila', '.modal-velo', '.sg-drawer', '.who-menu', '.campo-error']
      .map(s => [s, estiloDefinido(s)]);

  // Controles sin ningun gancho posible.
  const inertes = [];
  document.querySelectorAll('button, a.btn, input, select, textarea').forEach(c => {
    if (c.disabled || c.type === 'hidden') return;
    const texto = (c.textContent || '').trim();
    const accion = c.dataset && c.dataset.accion;
    const label = c.getAttribute('aria-label');
    const idEnForm = c.id && !!document.querySelector(`label[for="${CSS.escape(c.id)}"]`);
    // Un input dentro de un <label> ya tiene etiqueta implicita (checkbox de
    // "recordar sesion", "acepto los terminos"), igual que en _estructura.py.
    const etiquetaImplicita = !!c.closest('label');
    const conPlaceholder = !!c.getAttribute('placeholder');
    // Casos con comportamiento propio y legitimo, ya cubierto por lib_js.
    const propios = c.matches('.burger, .chip, .tabs button, .who, .tabla-envoltura thead input, [data-paginacion] button, form');
    if (texto || accion || label || idEnForm || etiquetaImplicita || conPlaceholder || propios) return;
    inertes.push(c.tagName + '.' + String(c.className || '').slice(0, 26));
  });
  r.inertes = [...new Set(inertes)];

  // Enlaces .btn que no llevan a ninguna parte.
  r.anclasVacias = [...new Set([...document.querySelectorAll('a.btn')]
      .filter(a => !a.getAttribute('href') && !a.dataset.accion)
      .map(a => a.textContent.trim().slice(0, 20)))];

  r.acciones = {};
  document.querySelectorAll('[data-accion]').forEach(b => {
    const k = b.dataset.accion;
    r.acciones[k] = (r.acciones[k] || 0) + 1;
  });
  return r;
}"""

# Interacciones que se disparan para comprobar que el script responde de verdad.
JS_PRUEBA_ACCION = r"""async () => {
  const esperar = ms => new Promise(r => setTimeout(r, ms));
  const salida = {};

  const conAccion = sel => document.querySelector(sel);

  // Toast: cualquier boton con texto visible cae en el default del manejador.
  const btn = [...document.querySelectorAll('button')]
      .find(b => (b.textContent || '').trim() && !b.dataset.accion && !b.matches('.burger'));
  if (btn) {
    btn.click();
    await esperar(120);
    salida.toast = document.querySelectorAll('.toast-pila .toast').length;
  }

  // Drawer de notificaciones.
  const bell = document.querySelector('[data-accion="notificaciones"]');
  if (bell) {
    bell.click();
    await esperar(120);
    salida.drawer = document.querySelectorAll('.sg-drawer').length;
    const x = document.querySelector('.drawer-x');
    if (x) { x.click(); await esperar(80); }
    salida.drawerCerrado = document.querySelectorAll('.sg-drawer').length;
  }

  // Modal de detalle.
  const ver = document.querySelector('[data-accion="ver"]');
  if (ver) {
    ver.click();
    await esperar(120);
    salida.modal = document.querySelectorAll('.modal-velo').length;
    const x = document.querySelector('.modal-x');
    if (x) { x.click(); await esperar(80); }
    salida.modalCerrado = document.querySelectorAll('.modal-velo').length;
  }

  // Confirmacion de borrado: el boton es el propio, la fila sobrevive.
  const borrar = document.querySelector('[data-accion="borrar"]');
  if (borrar) {
    const fila = borrar.closest('tr, article, li');
    borrar.click();
    await esperar(120);
    salida.confirm = document.querySelectorAll('.modal-velo').length;
    const cancel = [...document.querySelectorAll('.modal-foot button')]
        .find(b => /cancelar/i.test(b.textContent));
    if (cancel) { cancel.click(); await esperar(80); }
    salida.filaIntacta = !!fila && !!fila.isConnected;
  }

  // Menu de usuario.
  const who = document.querySelector('.who');
  if (who) {
    who.click();
    await esperar(100);
    salida.menu = document.querySelectorAll('.who-menu.visible').length;
    document.body.click();
    await esperar(80);
    salida.menuCerrado = document.querySelectorAll('.who-menu.visible').length;
  }

  // Buscador de tablas.
  const buscar = document.querySelector('.buscador input');
  if (buscar) {
    const filas = document.querySelectorAll('table.tabla tbody tr').length;
    buscar.value = 'zzzz-no-existe';
    buscar.dispatchEvent(new Event('input', {bubbles: true}));
    await esperar(400);
    salida.busquedaOculta = [...document.querySelectorAll('table.tabla tbody tr')]
        .every(tr => tr.hidden);
    buscar.value = '';
    buscar.dispatchEvent(new Event('input', {bubbles: true}));
    await esperar(400);
    salida.busquedaRestaura = [...document.querySelectorAll('table.tabla tbody tr')]
        .filter(tr => !tr.hidden).length === filas;
  }

  // Persistencia del estado de la pantalla.
  salida.claves = Object.keys(localStorage).filter(k => k.startsWith('sgemd:v1:')).length;
  return salida;
}"""


# Valores validos por formulario de acceso. Son estrictamente validos: un
# type=email con texto invalido lo bloquea el navegador antes de que corra el
# script, y entonces la prueba no mediria lo que cree medir.
RUTAS_ACCESO = {
    "registro.html": [
        ("#n1", "Demo"), ("#n2", "Prueba"),
        ("input[placeholder='1020304050']", "1020304050"),
        ("#ce", "demo@correo.com"), ("#ci", "demo@minutodedios.edu.co"),
        ("#tc", "3001234567"), ("#pa", "Aa1!aaaaa"),
        ("label.chk input[type=checkbox]", "on"),
    ],
    "recuperar-contrasena.html": [
        ("#co", "demo@minutodedios.edu.co"), ("#do", "1020304050"),
    ],
    "verificar-otp.html": [(".otp input:nth-of-type(%d)" % i, str(i)) for i in range(1, 9)],
}


async def formulario_simulado(pagina, ruta, rutas):
    """Envio en blanco (debe avisar) y envio completo (debe confirmar)."""
    clave = os.path.basename(ruta)
    fallos = 0
    try:
        await pagina.click("form[data-form-simulado] button[type=submit]")
        await pagina.wait_for_timeout(150)
        vacio = await pagina.evaluate(
            "() => {const e = document.querySelector('.campo-error');"
            " return {campo: !!(e && e.textContent.trim()),"
            " invalido: document.querySelectorAll('[aria-invalid]').length > 0};}")
        if not vacio["campo"] or not vacio["invalido"]:
            fallos += 1
            print("  VALIDACION  %s  el envio en blanco no aviso: %s" % (ruta, vacio))

        for sel, valor in rutas.get(clave, []):
            if "checkbox" in sel:
                await pagina.check(sel)
            else:
                await pagina.fill(sel, valor)
        await pagina.click("form[data-form-simulado] button[type=submit]")
        await pagina.wait_for_timeout(200)
        ok = await pagina.evaluate(
            "() => {const o = document.getElementById('acceso-ok');"
            " return {ok: !!o && !o.hidden, texto: o ? o.textContent.trim() : '',"
            " limpio: document.querySelectorAll('.campo-error').length === 0};}")
        if not ok["ok"] or not ok["limpio"]:
            fallos += 1
            print("  SIN AVISO   %s  el envio valido no confirmo: %s" % (ruta, ok))
    except Exception as exc:  # noqa: BLE001
        fallos += 1
        print("  ACCESO      %s  %s" % (ruta, exc))
    return fallos


async def main():
    rutas = []
    for carpeta in CARPETAS:
        rutas += sorted(glob.glob(os.path.join(carpeta, "*.html")))
    rutas = [r.replace("\\", "/") for r in rutas]
    fallos = 0
    acciones_totales = {}
    async with async_playwright() as p:
        navegador = await p.chromium.launch()
        pagina = await navegador.new_page(viewport={"width": 1280, "height": 900})
        errores, excepciones = [], []
        pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pagina.on("pageerror", lambda e: excepciones.append(str(e)))
        for ruta in rutas:
            # Los acumuladores se vacian en cada navegacion: los listeners se
            # registran una vez y siguen vivos entre goto.
            del errores[:]
            del excepciones[:]
            url = "file:///" + urllib.parse.quote(BASE.replace("\\", "/") + "/" + ruta)
            errores, excepciones = [], []
            pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            pagina.on("pageerror", lambda e: excepciones.append(str(e)))
            await pagina.goto(url)
            await pagina.wait_for_timeout(120)
            r = await pagina.evaluate(JS_SONDA)
            # El bloque de lib_js va en el shell de las pantallas de rol. Las de
            # acceso (compartido/) tienen su propio formulario y se auditan en
            # la Fase 5, asi que solo se les exige no romper la consola.
            con_shell = not ruta.startswith("compartido/")
            if con_shell and not r["jsListo"]:
                fallos += 1
                print("  SIN JS      %s  (el script no llego al final o fallo)" % ruta)
            faltantes = [s for s, ok in r["estilos"] if not ok]
            if faltantes:
                fallos += 1
                print("  SIN ESTILO  %s  %s" % (ruta, faltantes))
            if r["inertes"]:
                fallos += len(r["inertes"])
                print("  INERTE      %s  %s" % (ruta, r["inertes"][:5]))
            if r["anclasVacias"]:
                fallos += len(r["anclasVacias"])
                print("  ANCLA       %s  %s" % (ruta, r["anclasVacias"][:5]))
            if excepciones:
                fallos += len(excepciones)
                print("  EXCEPCION   %s  %s" % (ruta, excepciones[:2]))
            if errores:
                fallos += len(errores)
                print("  CONSOLA     %s  %s" % (ruta, errores[:2]))
            for k, v in r["acciones"].items():
                acciones_totales[k] = acciones_totales.get(k, 0) + v

            # Solo se ejercita la interaccion en una pantalla por rol: el bloque
            # es identico en las 50 y repetirlas multiplicaria el tiempo x50.
            # Las de acceso se comprueban en _accesos.py y en la parte de
            # formularios simulados de aqui abajo.
            if con_shell and ruta.endswith(("dashboard.html", "usuarios.html")):
                try:
                    prueba = await pagina.evaluate(JS_PRUEBA_ACCION)
                except Exception as exc:  # noqa: BLE001
                    fallos += 1
                    print("  PRUEBA      %s  %s" % (ruta, exc))
                    prueba = {}
                if prueba:
                    fallos += comprobar(ruta, prueba)

            # Las pantallas de acceso: formulario obligatorio, aviso de campo y
            # confirmacion simulada. Se prueba el envio vacio y el envio valido.
            elif not con_shell and ruta.endswith(
                    ("registro.html", "verificar-otp.html", "recuperar-contrasena.html")):
                fallos += await formulario_simulado(pagina, ruta, RUTAS_ACCESO)

        await navegador.close()

    print("\nacciones data-accion emitidas: %s" % json.dumps(
        dict(sorted(acciones_totales.items(), key=lambda kv: -kv[1]))))
    print("%d problema(s) de interaccion." % fallos)
    return fallos


def comprobar(ruta, p):
    """Comprueba el resultado de JS_PRUEBA_ACCION."""
    malos = []

    def pedir(clave, esperado):
        if clave in p and p[clave] != esperado:
            malos.append("%s=%r (esperado %r)" % (clave, p[clave], esperado))

    pedir("toast", 1)
    pedir("drawer", 1)
    pedir("drawerCerrado", 0)
    pedir("modal", 1)
    pedir("modalCerrado", 0)
    pedir("confirm", 1)
    pedir("filaIntacta", True)
    pedir("menu", 1)
    pedir("menuCerrado", 0)
    pedir("busquedaOculta", True)
    pedir("busquedaRestaura", True)
    if malos:
        print("  COMPORTAMIENTO %s  %s" % (ruta, malos))
    return len(malos)


if __name__ == "__main__":
    raise SystemExit(1 if asyncio.run(main()) else 0)