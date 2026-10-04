# -*- coding: utf-8 -*-
"""Descarga el screenshot de una pantalla de Stitch para revision visual."""
import io
import json
import os
import sys
import urllib.request

BASE = "https://stitch.googleapis.com/v1"
CLAVE = os.environ["STITCH_API_KEY"]
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_capturas")


def pedir(url):
    r = urllib.request.Request(url, headers={"x-goog-api-key": CLAVE})
    with urllib.request.urlopen(r) as f:
        return json.loads(f.read().decode("utf-8"))


def main(proyecto, pantalla):
    d = pedir("%s/%s/screens/%s" % (BASE, proyecto, pantalla))
    print("claves:", sorted(d.keys()))
    ss = d.get("screenshot") or (d.get("proto", {}) or {}).get("screenshot")
    print("screenshot:", json.dumps(ss)[:300] if ss else None)
    return d


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])