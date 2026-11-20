# -*- coding: utf-8 -*-
"""Sube las pantallas generadas al proyecto de Stitch (BatchCreateScreens).

Habla directo con la API para poder registrar el estado ANTES de cada llamada: si
algo falla a mitad, la entrada queda marcada como "pendiente" y no se reintenta a
ciegas (evita duplicados silenciosos).

Uso:
    python generar.py
    python subir.py                # sube lo que falte
    python subir.py --rol estudiante
    python subir.py --force --rol estudiante
    python subir.py --pendientes   # revisa entradas a medio subir
"""
import argparse
import base64
import io
import json
import os
import ssl
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
API = "https://stitch.googleapis.com"
PROYECTO = "3060781598377201049"
ESTADO = os.path.join(BASE, "_subidas.json")
TITULO_LOGO = "SGEMD - Logo institucional"
ORDEN = ["compartido", "estudiante", "docente", "admin"]
CONTEXTO = ssl.create_default_context()


def cargar_estado():
    if os.path.exists(ESTADO):
        with io.open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_estado(d):
    with io.open(ESTADO, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True))


def subir_html(ruta, titulo, mime="text/html"):
    with open(ruta, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    payload = {
        "parent": "projects/%s" % PROYECTO,
        "requests": [{
            "screen": {
                "htmlCode": {"fileContentBase64": b64, "mimeType": mime},
                "screenType": "DOCUMENT",
                "isCreatedByClient": True,
                "generatedBy": "UserUploadedHtml",
                "title": titulo,
            }
        }],
        "createScreenInstances": True,
    }
    req = urllib.request.Request(
        "%s/v1/projects/%s/screens:batchCreate" % (API, PROYECTO),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "X-Goog-Api-Key": os.environ["STITCH_API_KEY"]},
        method="POST")
    with urllib.request.urlopen(req, timeout=180, context=CONTEXTO) as r:
        d = json.loads(r.read().decode("utf-8"))
    res = (d.get("results") or [{}])[0]
    pant = (res.get("screen") or {}).get("name")
    inst = (res.get("screenInstances") or [{}])[0]
    if not pant:
        raise RuntimeError("respuesta sin screen: %s" % sorted(d.keys()))
    return {"pantalla": pant, "instancia": inst.get("id"),
            "ancho": inst.get("width"), "alto": inst.get("height")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--rol", choices=ORDEN)
    ap.add_argument("--pendientes", action="store_true")
    a = ap.parse_args()

    estado = cargar_estado()

    if a.pendientes:
        pend = {k: v for k, v in estado.items() if v.get("estado") != "ok"}
        if not pend:
            print("sin entradas pendientes.")
        for k, v in sorted(pend.items()):
            print("  %-42s %s" % (k, v.get("estado")))
        return 0

    import generar  # registra las pantallas disponibles

    nuevas = fallidas = 0
    for carpeta in ORDEN:
        if a.rol and carpeta != a.rol:
            continue
        for it in sorted(generar.SALIDAS.get(carpeta, []), key=lambda x: x["orden"]):
            clave = "%s/%s" % (carpeta, it["archivo"])
            ruta = os.path.join(BASE, carpeta, it["archivo"])
            if not os.path.exists(ruta):
                print("  FALTA  %s (ejecuta generar.py)" % clave)
                fallidas += 1
                continue
            previo = estado.get(clave)
            if previo and previo.get("estado") == "ok" and not a.force:
                print("  ya     %-42s %s" % (clave, previo["pantalla"].rsplit("/", 1)[-1]))
                continue
            if previo and previo.get("estado") == "pendiente" and not a.force:
                print("  REVISAR %-41sUpload sin confirmar; usa --force" % clave)
                continue
            # marcar ANTES de la llamada: si el proceso muere, queda pendiente
            estado[clave] = {"estado": "pendiente", "titulo": it["titulo"]}
            guardar_estado(estado)
            try:
                info = subir_html(ruta, it["titulo"])
            except Exception as e:  # noqa: BLE001
                estado[clave]["estado"] = "fallo"
                estado[clave]["error"] = str(e)[:200]
                guardar_estado(estado)
                print("  ERROR  %-42s %s" % (clave, e))
                fallidas += 1
                continue
            info["estado"] = "ok"
            info["titulo"] = it["titulo"]
            estado[clave] = info
            guardar_estado(estado)
            nuevas += 1
            print("  ok     %-42s %s" % (clave, info["instancia"] or info["pantalla"].rsplit("/", 1)[-1]))

    # Pantalla institucional: el lockup recortado, no el PNG cuadrado original.
    if not a.rol:
        clave = "_marca/logo-color-1200.png"
        ruta = os.path.join(BASE, clave)
        previo = estado.get(clave)
        if not os.path.exists(ruta):
            print("  FALTA  %s" % clave)
            fallidas += 1
        elif previo and previo.get("estado") == "ok" and not a.force:
            print("  ya     %-42s %s" % (clave, previo["pantalla"].rsplit("/", 1)[-1]))
        else:
            estado[clave] = {"estado": "pendiente", "titulo": TITULO_LOGO}
            guardar_estado(estado)
            try:
                info = subir_html(ruta, TITULO_LOGO, mime="image/png")
            except Exception as e:  # noqa: BLE001
                estado[clave]["estado"] = "fallo"
                estado[clave]["error"] = str(e)[:200]
                guardar_estado(estado)
                print("  ERROR  %-42s %s" % (clave, e))
                fallidas += 1
            else:
                info["estado"] = "ok"
                info["titulo"] = TITULO_LOGO
                estado[clave] = info
                guardar_estado(estado)
                nuevas += 1
                print("  ok     %-42s %s" % (clave, info["instancia"]
                                              or info["pantalla"].rsplit("/", 1)[-1]))

    print("\n%d nueva(s), %d fallo(s). Estado en _subidas.json" % (nuevas, fallidas))
    return 1 if fallidas else 0


if __name__ == "__main__":
    sys.exit(main())