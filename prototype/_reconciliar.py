# -*- coding: utf-8 -*-
"""Reconcilia _subidas.json con el proyecto real y lista las pantallas duplicadas.

Stitch no expone DELETE para pantallas, asi que las sobrantes se borran desde la UI.
Este script dice exactamente cuales conservar y cuales eliminar.
"""
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
INFORME = os.path.join(BASE, "_duplicados.md")
CONTEXTO = ssl.create_default_context()


def listar():
    url = "%s/v1/projects/%s/screens?pageSize=200" % (API, PROYECTO)
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": os.environ["STITCH_API_KEY"]})
    with urllib.request.urlopen(req, timeout=120, context=CONTEXTO) as r:
        d = json.loads(r.read().decode("utf-8"))
    return d.get("screens") or []


def main():
    pantallas = listar()

    sys.path.insert(0, BASE)
    import generar
    esperados = {}
    for carpeta, items in generar.SALIDAS.items():
        for it in items:
            esperados[it["titulo"]] = "%s/%s" % (carpeta, it["archivo"])
    esperados["SGEMD - Logo institucional"] = "_marca/logo-color-1200.png"

    por_titulo = {}
    for s in pantallas:
        por_titulo.setdefault(s.get("title") or "(sin titulo)", []).append(s)

    # conservar por titulo la pantalla mas antigua; registrar en carpeta/archivo
    nuevo = {}
    for titulo, grupo in por_titulo.items():
        orden = sorted(grupo, key=lambda s: int(s["name"].rsplit("/", 1)[-1]))
        clave = esperados.get(titulo)
        if clave is None or titulo not in esperados:
            continue
        s0 = orden[0]
        inst = nuevo.setdefault(clave, {"estado": "ok", "titulo": titulo,
                                        "pantalla": s0["name"]})
        inst["ancho"] = s0.get("width")
        inst["alto"] = s0.get("height")
        inst["duplicadas"] = len(grupo) - 1
    estado = nuevo
    falantes = sorted(set(esperados.values()) - set(nuevo))
    for k in falantes:
        estado[k] = {"estado": "pendiente", "titulo": k.split("/")[-1]}
        print("  PENDIENTE %s" % k)

    with io.open(ESTADO, "w", encoding="utf-8") as f:
        f.write(json.dumps(estado, indent=2, ensure_ascii=False, sort_keys=True))

    lineas = ["# Pantallas duplicadas en Stitch",
              "",
              "Proyecto: `projects/%s`" % PROYECTO,
              "",
              "Stitch no permite borrar pantallas por API (DELETE devuelve 404).",
              "Borra desde la UI de Stitch las pantallas marcadas como **ELIMINAR**.",
              "",
              "Total de pantallas ahora: **%d**" % len(pantallas),
              ""]
    borrar = []
    for titulo in sorted(por_titulo):
        grupo = sorted(por_titulo[titulo], key=lambda s: int(s["name"].rsplit("/", 1)[-1]))
        if titulo not in esperados:
            # pantalla obsoleta de una prueba anterior: se elimina todas
            lineas.append("## %s  — obsoleta, eliminar todas" % titulo)
            lineas.append("")
            for s in grupo:
                lineas.append("- ELIMINAR   `%s`" % s["name"].rsplit("/", 1)[-1])
                borrar.append(s["name"].rsplit("/", 1)[-1])
            lineas.append("")
            continue
        conservar = grupo[0]["name"]
        extras = [s for s in grupo if s["name"] != conservar]
        if not extras:
            continue
        lineas.append("## %s" % titulo)
        lineas.append("")
        lineas.append("- CONSERVAR  `%s`" % conservar.rsplit("/", 1)[-1])
        for s in extras:
            lineas.append("- ELIMINAR   `%s`  (duplicada)"
                          % s["name"].rsplit("/", 1)[-1])
            borrar.append(s["name"].rsplit("/", 1)[-1])
        lineas.append("")

    lineas.append("## Resumen")
    lineas.append("")
    lineas.append("- A eliminar: **%d**" % len(borrar))
    lineas.append("")
    lineas.append("```")
    lineas.extend(borrar)
    lineas.append("```")

    with io.open(INFORME, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    print("\n".join(lineas[:6]))
    print("...")
    print("pantallas: %d | a eliminar: %d | informe: %s"
          % (len(pantallas), len(borrar), os.path.basename(INFORME)))


if __name__ == "__main__":
    sys.exit(main())