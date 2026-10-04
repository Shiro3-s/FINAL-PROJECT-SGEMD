# -*- coding: utf-8 -*-
"""Generador del prototipo SGEMD.

Emite HTML autocontenido (CSS embebido, sin dependencias locales) en:

    prototype/compartido/   pantallas globales de acceso
    prototype/estudiante/   rol ESTUDIANTE
    prototype/docente/       rol DOCENTE
    prototype/admin/         rol ADMINISTRADOR

Uso:  python generar.py
"""

import io
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

SALIDAS = {}


def registrar(carpeta, nombre, titulo, fn, orden):
    SALIDAS.setdefault(carpeta, []).append(
        {"archivo": nombre, "titulo": titulo, "fn": fn, "orden": orden}
    )


def _cargar(modulo, carpeta, items):
    try:
        m = __import__(modulo)
    except ImportError as e:
        print("  (sin modulo %s: %s)" % (modulo, e))
        return
    for i, (nombre, titulo, fn) in enumerate(items):
        registrar(carpeta, nombre, titulo, getattr(m, fn), i)


# --- 1. Pantallas globales de acceso -----------------------------------------
_cargar(
    "paginas_auth",
    "compartido",
    [
        ("login.html", "01 Acceso - Login (global)", "login"),
        ("registro.html", "02 Acceso - Registro (global)", "registro"),
        ("verificar-otp.html", "03 Acceso - Verificar OTP (global)", "verificar_otp"),
        ("recuperar-contrasena.html", "04 Acceso - Recuperar contrasena (global)", "recuperar_contrasena"),
    ],
)

# --- 2. Rol Estudiante -------------------------------------------------------
try:
    import paginas_estudiante as pe

    pe.registrar(registrar)
except ImportError:
    pass

# --- 3. Rol Docente ----------------------------------------------------------
try:
    import paginas_docente as pd

    pd.registrar(registrar)
except ImportError:
    pass

# --- 4. Rol Administrador ----------------------------------------------------
try:
    import paginas_admin as pa

    pa.registrar(registrar)
except ImportError:
    pass


def main():
    total = 0
    indice = []
    for carpeta in ["compartido", "estudiante", "docente", "admin"]:
        items = SALIDAS.get(carpeta, [])
        if not items:
            continue
        d = os.path.join(BASE, carpeta)
        os.makedirs(d, exist_ok=True)
        for it in sorted(items, key=lambda x: x["orden"]):
            html = it["fn"]()
            ruta = os.path.join(d, it["archivo"])
            with io.open(ruta, "w", encoding="utf-8") as f:
                f.write(html)
            total += 1
            indice.append((carpeta, it["archivo"], it["titulo"]))
            print("  ok  %-12s %s" % (carpeta, it["archivo"]))
    print("\n%d pantallas generadas." % total)

    # indice de navegacion
    def _ind():
        h = ['<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             "<title>SGEMD - Indice del prototipo</title>",
             '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
             "<style>body{font-family:Inter,sans-serif;margin:0;background:#ffffff;color:#051533;",
             "font-size:14px}header{background:#051533;color:#ffffff;padding:32px 40px}",
             "h1{margin:0;font-size:28px}p.o{opacity:.78;margin-top:6px}",
             ".wrap{padding:32px 40px;max-width:1100px}",
             "h2{font-size:18px;margin:32px 0 12px;padding-bottom:8px;border-bottom:1px solid #bbbbbb}",
             "a.row{display:flex;align-items:center;gap:14px;padding:12px 16px;border:1px solid #bbbbbb;",
             "border-radius:8px;margin-bottom:8px;text-decoration:none;color:#051533}",
             "a.row:hover{border-color:#004a93;background:rgba(0,74,147,.06)}",
             ".n{font-size:13px;color:#162644;background:rgba(0,74,147,.08);padding:2px 8px;",
             "border-radius:999px;font-weight:600}",".d{margin-left:auto;font-size:13px;color:#162644}",
             "</style></head><body><header><h1>SGEMD</h1>",
             "<p class=\"o\">Indice del prototipo &middot; 3 roles + acceso global</p></header>",
             '<div class="wrap">']
        etiquetas = {
            "compartido": "Acceso global (los 3 roles)",
            "estudiante": "Rol ESTUDIANTE",
            "docente": "Rol DOCENTE",
            "admin": "Rol ADMINISTRADOR",
        }
        for carpeta in ["compartido", "estudiante", "docente", "admin"]:
            filas = [x for x in indice if x[0] == carpeta]
            if not filas:
                continue
            h.append("<h2>%s &middot; %d pantallas</h2>" % (etiquetas[carpeta], len(filas)))
            for _, arch, tit in filas:
                h.append(
                    '<a class="row" href="%s/%s"><span class="n">%s</span><b>%s</b>'
                    '<span class="d">%s</span></a>'
                    % (carpeta, arch, arch.replace(".html", ""), tit, carpeta)
                )
        h.append("</div></body></html>")
        with io.open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
            f.write("\n".join(h))

    _ind()
    print("Indice: prototype/index.html")


if __name__ == "__main__":
    main()