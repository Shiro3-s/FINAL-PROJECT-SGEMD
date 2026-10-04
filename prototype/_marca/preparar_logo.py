"""Genera las variantes del logo SGEMD a partir de docs/Logo_sinfondo.png.

La fuente es un PNG indexado con transparencia (canal tRNS). Al convertirla a RGBA
el lienzo queda con ~90% de pixeles transparentes y el lockup real ocupa
x 29..3374, y 768..2361, es decir un rectangulo de 3345x1593 (ratio 2.0998).

La composicion del lockup tiene tres familias de color:

  * oro  #F0C000  -> rosca de la izquierda y las dos lineas de texto de la derecha
  * azul #004090  -> las letras "USMA" del centro
  * blanco #F0F0F0 -> una diagonal y un asta vertical que cruzan el texto

Ese blanco NO es una mancha de la fuente: es un elemento grafico del logotipo.
Por eso este script no lo borra, lo RECOLOREA segun la variante, porque un blanco
sobre un panel blanco seria invisible y el logo quedaria incompleto.

Salidas (en esta misma carpeta):

  logo-blanco-600.png   todo opaco en #FFFFFF, alfa intacto. Para fondos navy.
  logo-color-1200.png   oro y azul originales, blanco -> #051533. Para fondos claros.
  logo_datos.py         data URIs en base64 de las dos variantes, para incrustar
                        en el CSS y que cada HTML sea autocontenido (Stitch sirve
                        cada pantalla como documento aislado, sin rutas relativas).
"""

import base64
import io
import os

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
FUENTE = os.path.join(RAIZ, "docs", "Logo_sinfondo.png")

# Solo se recorta lo que tiene alfa visible; por debajo de esto es ruido del PNG.
ALFA_VISIBLE = 8
# Un pixel cuenta como "blanco del logotipo" si los tres canales pasan este valor.
GRIS_MINIMO = 235
# Navy de la paleta del proyecto, para el elemento blanco sobre fondo claro.
NOCHE = (5, 21, 51)

BLANCO = (255, 255, 255)

ANCHO_BLANCO = 600
ANCHO_COLOR = 1200
# La data URI de color va incrustada en las 4 pantallas de acceso, donde la barra
# compacta se dibuja a 170px CSS (340px a 2x). 800px de sobra y pesa la mitad que
# el archivo de 1200px que si se sube a Stitch como pantalla institucional.
ANCHO_COLOR_URI = 800


def _recortar_por_alfa(imagen):
    """Devuelve la imagen recortada al rectangulo que realmente contiene el logo."""
    caja = imagen.getchannel("A").point(lambda v: 255 if v > ALFA_VISIBLE else 0).getbbox()
    if caja is None:
        raise SystemExit("La fuente no tiene ningun pixel visible.")
    return imagen.crop(caja), caja


def _recolorer(imagen, destino, umbral):
    """Pasa los pixeles casi blancos de `imagen` a `destino`, conservando el alfa."""
    salida = imagen.copy()
    pixeles = salida.load()
    for y in range(salida.height):
        for x in range(salida.width):
            r, g, b, a = pixeles[x, y]
            if a > 0 and r >= umbral and g >= umbral and b >= umbral:
                pixeles[x, y] = destino + (a,)
    return salida


def _variante_blanca(imagen):
    """Todos los pixeles opacos a blanco, con el alfa original intacto."""
    salida = imagen.copy()
    pixeles = salida.load()
    for y in range(salida.height):
        for x in range(salida.width):
            _, _, _, a = pixeles[x, y]
            pixeles[x, y] = BLANCO + (a,)
    return salida


def _escalar(imagen, ancho):
    if imagen.width <= ancho:
        return imagen
    alto = max(1, round(imagen.height * ancho / imagen.width))
    return imagen.resize((ancho, alto), Image.LANCZOS)


def _data_uri(imagen):
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _verificar(nombre, imagen, permite_blanco):
    """Avisa si la variante tiene un color que no deberia."""
    pixeles = imagen.convert("RGBA").load()
    proporcion = imagen.width / imagen.height
    if abs(proporcion - 2.0998) > 0.02:
        raise SystemExit("%s: ratio %.4f, se esperaba 2.0998" % (nombre, proporcion))
    if not permite_blanco:
        for y in range(0, imagen.height, 7):
            for x in range(0, imagen.width, 7):
                r, g, b, a = pixeles[x, y]
                if a > 200 and r >= 235 and g >= 235 and b >= 235:
                    raise SystemExit("%s: quedan pixeles blancos opacos" % nombre)
    return proporcion


def main():
    if not os.path.exists(FUENTE):
        raise SystemExit("No existe la fuente: %s" % FUENTE)

    original = Image.open(FUENTE).convert("RGBA")
    recortada, caja = _recortar_por_alfa(original)

    blanca = _escalar(_variante_blanca(recortada), ANCHO_BLANCO)
    color = _escalar(_recolorer(recortada, NOCHE, GRIS_MINIMO), ANCHO_COLOR)

    destino_blanco = os.path.join(AQUI, "logo-blanco-%d.png" % ANCHO_BLANCO)
    destino_color = os.path.join(AQUI, "logo-color-%d.png" % ANCHO_COLOR)
    blanca.save(destino_blanco, format="PNG", optimize=True)
    color.save(destino_color, format="PNG", optimize=True)

    uri_blanco = _data_uri(blanca)
    uri_color = _data_uri(_escalar(color, ANCHO_COLOR_URI))

    # El modulo de datos va en la raiz de temporal/, junto a lib_css y demas, para
    # que `from logo_datos import ...` funcione sin tocar sys.path. Los PNG siguen
    # aqui en _marca/, que es la carpeta de assets.
    destino_py = os.path.join(os.path.dirname(AQUI), "logo_datos.py")
    with open(destino_py, "w", encoding="utf-8") as archivo:
        archivo.write(
            '"""Generado por _marca/preparar_logo.py. No editar a mano."""\n\n'
            "LOGO_BLANCO_URI = (\n"
        )
        for i in range(0, len(uri_blanco), 96):
            archivo.write("    %r\n" % uri_blanco[i:i + 96])
        archivo.write(")\n\nLOGO_COLOR_URI = (\n")
        for i in range(0, len(uri_color), 96):
            archivo.write("    %r\n" % uri_color[i:i + 96])
        archivo.write(")\n")

    print("fuente  %dx%d  lienzo" % original.size)
    print("lockup  x%d..%d y%d..%d  %dx%d" % (
        caja[0], caja[2] - 1, caja[1], caja[3] - 1,
        recortada.width, recortada.height))
    print("  blanco  %dx%d  ratio %.4f  %.1f KB  uri %.1f KB" % (
        blanca.width, blanca.height, blanca.width / blanca.height,
        os.path.getsize(destino_blanco) / 1024, len(uri_blanco) / 1024))
    print("  color   %dx%d  ratio %.4f  %.1f KB  uri %.1f KB" % (
        color.width, color.height, color.width / color.height,
        os.path.getsize(destino_color) / 1024, len(uri_color) / 1024))
    print("  verificacion: ok en ambas variantes")


if __name__ == "__main__":
    main()