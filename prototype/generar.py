# -*- coding: utf-8 -*-
"""Generador del prototipo SGEMD.

Emite HTML autocontenido (CSS embebido, sin dependencias locales) en:

    prototype/compartido/   pantallas globales de acceso
    prototype/estudiante/   rol ESTUDIANTE
    prototype/docente/       rol DOCENTE
    prototype/admin/         rol ADMINISTRADOR
    prototype/superadmin/    rol SUPER ADMIN (gestión de perfiles)

Uso:
    python generar.py                              # todas las pantallas
    python generar.py --rol admin                  # solo el rol administrador
    python generar.py --rol superadmin             # solo el módulo Super Admin
    python generar.py --rol estudiante --vista perfil.html --vista configuracion.html
    python generar.py --vista dashboard.html       # ese archivo en todos los roles

`--rol` y `--vista` acotan lo que se reescribe: el resto de archivos queda
byte-identico en disco. `index.html` se regenera siempre (es el indice de
navegacion y depende del registro completo de pantallas).
"""

import argparse
import io
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

SALIDAS = {}

ROLES = ["compartido", "estudiante", "docente", "admin", "superadmin"]


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

# --- 5. Rol Super Admin ------------------------------------------------------
try:
    import paginas_superadmin as ps

    ps.registrar(registrar)
except ImportError:
    pass


def main():
    ap = argparse.ArgumentParser(
        description="Genera el prototipo SGEMD (HTML autocontenido por rol).")
    ap.add_argument("--rol", action="append", choices=ROLES, default=None,
                    help="Genera solo ese rol (repetible). Por defecto, todos.")
    ap.add_argument("--vista", action="append", default=None,
                    help="Genera solo ese archivo (repetible). Por defecto, todos.")
    args = ap.parse_args()

    roles = args.rol or ROLES
    vistas = set(args.vista) if args.vista else None

    total = 0
    indice = []
    for carpeta in ROLES:
        items = SALIDAS.get(carpeta, [])
        if not items:
            continue
        d = os.path.join(BASE, carpeta)
        os.makedirs(d, exist_ok=True)
        for it in sorted(items, key=lambda x: x["orden"]):
            # El indice de navegacion necesita TODAS las pantallas, aunque
            # en esta corrida solo se reescriban algunas.
            indice.append((carpeta, it["archivo"], it["titulo"]))
            if carpeta not in roles:
                continue
            if vistas is not None and it["archivo"] not in vistas:
                continue
            html = it["fn"]()
            ruta = os.path.join(d, it["archivo"])
            with io.open(ruta, "w", encoding="utf-8") as f:
                f.write(html)
            total += 1
            print("  ok  %-12s %s" % (carpeta, it["archivo"]))
    print("\n%d pantallas generadas." % total)

    # indice de navegacion
    def _ind():
        etiquetas = {
            "compartido": "Acceso global (los 4 roles)",
            "estudiante": "Rol ESTUDIANTE",
            "docente": "Rol DOCENTE",
            "admin": "Rol ADMINISTRADOR",
            "superadmin": "Rol SUPER ADMIN",
        }
        nombres_cortos = {
            "compartido": "Acceso global",
            "estudiante": "Estudiante",
            "docente": "Docente",
            "admin": "Administrador",
            "superadmin": "Super Admin",
        }
        total_pantallas = len(indice)
        chips = ['<button type="button" class="ind-chip activo" data-rol="todos">Todos (%d)</button>' % total_pantallas]
        for carpeta in ROLES:
            cnt = sum(1 for x in indice if x[0] == carpeta)
            if cnt:
                chips.append(
                    '<button type="button" class="ind-chip" data-rol="%s">%s (%d)</button>'
                    % (carpeta, nombres_cortos[carpeta], cnt)
                )
        h = [
            '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>SGEMD — Índice del prototipo</title>",
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
            "<style>",
            "*{box-sizing:border-box}",
            "body{font-family:Inter,sans-serif;margin:0;background:#ffffff;color:#051533;font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}",
            "header{background:#051533;color:#ffffff;padding:32px 40px;border-bottom:4px solid #ffd300}",
            ".head-inner{max-width:1440px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}",
            "h1{margin:0;font-size:28px;font-weight:800;letter-spacing:-.02em}",
            "p.o{color:#ffffff;opacity:.82;margin:6px 0 0;font-size:14px}",
            ".head-cta{display:flex;gap:10px;flex-wrap:wrap}",
            ".btn-inicio{display:inline-flex;align-items:center;justify-content:center;height:40px;padding:0 18px;border-radius:6px;background:#ffd300;color:#051533;font-weight:700;font-size:14px;text-decoration:none}",
            ".btn-inicio:hover{background:#004a93;color:#ffffff}",
            ".wrap{padding:32px 40px 56px;max-width:1440px;margin:0 auto}",
            ".ind-bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:24px;padding:16px;border:1px solid #bbbbbb;border-radius:10px;background:rgba(5,21,51,.03)}",
            ".ind-search{flex:1 1 260px;min-width:0;height:40px;padding:0 14px;border:1px solid #bbbbbb;border-radius:6px;font-family:Inter,sans-serif;font-size:14px;color:#051533;background:#ffffff}",
            ".ind-search:focus{outline:none;border-color:#004a93;box-shadow:0 0 0 3px rgba(0,74,147,.12)}",
            ".ind-chips{display:flex;gap:8px;flex-wrap:wrap}",
            ".ind-chip{height:36px;padding:0 14px;border-radius:999px;border:1px solid #bbbbbb;background:#ffffff;color:#162644;font-family:Inter,sans-serif;font-size:13px;font-weight:600;cursor:pointer}",
            ".ind-chip:hover{border-color:#004a93;color:#004a93}",
            ".ind-chip.activo{background:#004a93;border-color:#004a93;color:#ffffff}",
            ".ind-sec{margin-bottom:32px}",
            ".ind-sec[hidden]{display:none!important}",
            "h2{font-size:18px;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid #bbbbbb;color:#051533;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}",
            ".ind-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}",
            "a.row{display:flex;align-items:center;gap:12px;padding:12px 16px;border:1px solid #bbbbbb;border-radius:8px;text-decoration:none;color:#051533;background:#ffffff;min-width:0;flex-wrap:wrap}",
            "a.row[hidden]{display:none!important}",
            "a.row:hover{border-color:#004a93;background:rgba(0,74,147,.06)}",
            "a.row b{flex:1;min-width:140px;font-size:14px;font-weight:600;overflow-wrap:anywhere}",
            ".n{font-size:13px;color:#004a93;background:rgba(0,74,147,.08);padding:2px 10px;border-radius:999px;font-weight:600;max-width:100%;overflow-wrap:anywhere}",
            ".d{margin-left:auto;font-size:13px;color:#162644;font-weight:500}",
            "@media (min-width:1600px){.head-inner,.wrap{max-width:1760px}.ind-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}",
            "@media (min-width:2560px){html{font-size:18px}body{font-size:16px}.head-inner,.wrap{max-width:2320px}.ind-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}",
            "@media (max-width:1023px){header{padding:24px 20px}.wrap{padding:24px 20px 44px}.ind-grid{grid-template-columns:minmax(0,1fr)}}",
            "@media (max-width:639px){header{padding:20px 16px}h1{font-size:24px}.head-cta,.btn-inicio{width:100%}.wrap{padding:16px 12px 36px}.ind-bar{padding:12px}.ind-search{flex:1 1 100%;width:100%}.ind-chips{width:100%}.ind-chip{flex:1 1 auto;text-align:center}a.row{padding:12px}a.row b{flex:1 1 100%;order:2}.d{margin-left:auto}}",
            "</style></head><body>",
            '<header><div class="head-inner"><div><h1>SGEMD</h1>',
            '<p class="o">Índice general del prototipo &middot; 4 roles + acceso global (%d pantallas)</p></div>' % total_pantallas,
            '<div class="head-cta"><a class="btn-inicio" href="compartido/login.html">Iniciar sesión en el prototipo</a></div>',
            "</div></header>",
            '<main class="wrap">',
            '<div class="ind-bar">',
            '<input type="search" class="ind-search" id="ind-q" placeholder="Filtrar vista por nombre o archivo..." aria-label="Filtrar vista por nombre o archivo">',
            '<div class="ind-chips" role="tablist" aria-label="Filtrar por rol">%s</div>' % "".join(chips),
            "</div>",
        ]
        for carpeta in ROLES:
            filas = [x for x in indice if x[0] == carpeta]
            if not filas:
                continue
            h.append('<section class="ind-sec" data-sec="%s">' % carpeta)
            h.append("<h2><span>%s</span><span class=\"d\">%d pantallas</span></h2>" % (etiquetas[carpeta], len(filas)))
            h.append('<div class="ind-grid">')
            for _, arch, tit in filas:
                clave = arch.replace(".html", "")
                h.append(
                    '<a class="row" href="%s/%s" data-txt="%s %s %s"><span class="n">%s</span><b>%s</b>'
                    '<span class="d">%s</span></a>'
                    % (carpeta, arch, clave.lower(), tit.lower(), carpeta.lower(), clave, tit, carpeta)
                )
            h.append("</div></section>")
        h.append(
            "<script>"
            "(function(){"
            "var q=document.getElementById('ind-q');"
            "var chips=Array.prototype.slice.call(document.querySelectorAll('.ind-chip'));"
            "var secs=Array.prototype.slice.call(document.querySelectorAll('.ind-sec'));"
            "var rol='todos';"
            "function filtrar(){"
            "var txt=(q&&q.value||'').toLowerCase().trim();"
            "secs.forEach(function(s){"
            "var r=s.getAttribute('data-sec');"
            "if(rol!=='todos'&&r!==rol){s.hidden=true;return;}"
            "var rows=Array.prototype.slice.call(s.querySelectorAll('a.row'));"
            "var vis=0;"
            "rows.forEach(function(a){"
            "var ok=!txt||a.getAttribute('data-txt').indexOf(txt)>=0;"
            "a.hidden=!ok;if(ok)vis++;"
            "});"
            "s.hidden=(vis===0);"
            "});"
            "}"
            "if(q)q.addEventListener('input',filtrar);"
            "chips.forEach(function(c){c.addEventListener('click',function(){"
            "chips.forEach(function(b){b.classList.remove('activo');});"
            "c.classList.add('activo');rol=c.getAttribute('data-rol');filtrar();"
            "});});"
            "})();"
            "</script></main></body></html>"
        )
        with io.open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
            f.write("\n".join(h))

    _ind()
    print("Indice: prototype/index.html")


if __name__ == "__main__":
    main()