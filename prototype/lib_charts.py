# -*- coding: utf-8 -*-
"""Graficos SVG del prototipo SGEMD. Solo paleta. Valores siempre visibles."""

AZUL = "#004a93"
PROF = "#162644"
NOCHE = "#051533"
GRIS = "#bbbbbb"
AMAR = "#ffd300"


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _wrap(svg, titulo, sub, leyenda="", alto_extra=0):
    cab = ""
    if titulo:
        cab += '<div class="chart-titulo">%s</div>' % _esc(titulo)
    if sub:
        cab += '<div class="chart-sub">%s</div>' % _esc(sub)
    return '<div>%s%s%s</div>' % (cab, svg, leyenda)


def barras(titulo, sub, etiquetas, valores, maximo=None, unidad="", alto=180, color=AZUL):
    """Barras verticales con rejilla, etiqueta de eje Y y valor sobre cada barra."""
    mx = maximo or (max(valores) * 1.2 or 1)
    W, H = 520, alto
    pad_l, pad_b, pad_t = 44, 30, 16
    pw, ph = W - pad_l - 12, H - pad_b - pad_t
    s = ['<svg viewBox="0 0 %d %d" width="100%%" height="%d" role="img" '
         'aria-label="%s" style="display:block">' % (W, H, H, _esc(titulo or "Grafico de barras"))]
    # rejilla + eje Y con valores
    for i in range(5):
        y = pad_t + ph - i * ph / 4
        v = mx * i / 4
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (pad_l, y, W - 12, y, GRIS))
        s.append('<text x="%d" y="%.1f" font-size="10" fill="%s" text-anchor="end" '
                 'font-family="Inter,sans-serif">%s</text>'
                 % (pad_l - 8, y + 3, PROF, _esc(("%.0f" % v) if v >= 10 else ("%.1f" % v))))
    n = len(valores)
    paso = pw / max(n, 1)
    ancho = min(46, paso * 0.56)
    for i, (et, v) in enumerate(zip(etiquetas, valores)):
        h = max(2, ph * (v / mx))
        x = pad_l + paso * i + (paso - ancho) / 2
        y = pad_t + ph - h
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>'
                 % (x, y, ancho, h, color))
        s.append('<text x="%.1f" y="%.1f" font-size="11" font-weight="700" fill="%s" '
                 'text-anchor="middle" font-family="Inter,sans-serif">%s</text>'
                 % (x + ancho / 2, y - 6, NOCHE, _esc("%g%s" % (v, unidad))))
        s.append('<text x="%.1f" y="%d" font-size="10" fill="%s" text-anchor="middle" '
                 'font-family="Inter,sans-serif">%s</text>'
                 % (x + ancho / 2, H - 10, PROF, _esc(et)))
    s.append("</svg>")
    return _wrap("".join(s), titulo, sub)


def barras_h(titulo, sub, etiquetas, valores, maximo=None, unidad="", color=AZUL):
    """Barras horizontales: ideal para rankings y estados por estudiante."""
    mx = maximo or (max(valores) * 1.2 or 1)
    filas = len(valores)
    alto = filas * 34 + 8
    W = 520
    s = ['<svg viewBox="0 0 %d %d" width="100%%" height="%d" role="img" aria-label="%s" '
         'style="display:block">' % (W, alto, alto, _esc(titulo or "Grafico"))]
    pad_l, pad_r = 150, 54
    pw = W - pad_l - pad_r
    for i, (et, v) in enumerate(zip(etiquetas, valores)):
        y = i * 34 + 6
        s.append('<text x="%d" y="%d" font-size="11.5" fill="%s" text-anchor="end" '
                 'font-family="Inter,sans-serif">%s</text>' % (pad_l - 10, y + 16, PROF, _esc(et)))
        s.append('<rect x="%d" y="%d" width="%.1f" height="18" rx="3" fill="rgba(0,74,147,.15)"/>'
                 % (pad_l, y, pw))
        s.append('<rect x="%d" y="%d" width="%.1f" height="18" rx="3" fill="%s"/>'
                 % (pad_l, y, pw * min(v / mx, 1), color))
        s.append('<text x="%d" y="%d" font-size="11.5" font-weight="700" fill="%s" '
                 'text-anchor="end" font-family="Inter,sans-serif">%s</text>'
                 % (W - 6, y + 14, NOCHE, _esc("%g%s" % (v, unidad))))
    s.append("</svg>")
    return _wrap("".join(s), titulo, sub)


def lineas(titulo, sub, etiquetas, series, maximo=None, unidad="", alto=200):
    """series: lista de (nombre, valores, color). Ejes y valores visibles."""
    todos = [v for _, vs, _ in series for v in vs]
    mx = maximo or (max(todos) * 1.2 or 1)
    W, H = 520, alto
    pad_l, pad_b, pad_t = 44, 32, 20
    pw, ph = W - pad_l - 12, H - pad_b - pad_t
    s = ['<svg viewBox="0 0 %d %d" width="100%%" height="%d" role="img" aria-label="%s" '
         'style="display:block">' % (W, H, H, _esc(titulo or "Grafico de lineas"))]
    for i in range(5):
        y = pad_t + ph - i * ph / 4
        v = mx * i / 4
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (pad_l, y, W - 12, y, GRIS))
        s.append('<text x="%d" y="%.1f" font-size="10" fill="%s" text-anchor="end" '
                 'font-family="Inter,sans-serif">%s</text>'
                 % (pad_l - 8, y + 3, PROF, _esc("%.0f" % v)))
    n = len(etiquetas)
    px = lambda i: pad_l + (pw * i / max(n - 1, 1))
    for i, et in enumerate(etiquetas):
        s.append('<text x="%.1f" y="%d" font-size="10" fill="%s" text-anchor="middle" '
                 'font-family="Inter,sans-serif">%s</text>' % (px(i), H - 10, PROF, _esc(et)))
    for nombre, vs, color in series:
        pts = [(px(i), pad_t + ph - ph * (v / mx)) for i, v in enumerate(vs)]
        d = " ".join("%.1f,%.1f" % p for p in pts)
        area = "%s %.1f,%.1f %.1f,%.1f %s" % ("M", pts[0][0], pad_t + ph, pts[-1][0], pad_t + ph, d)
        s.append('<path d="%s" fill="rgba(0,74,147,.12)" stroke="none"/>' % area)
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color))
        for (x, y), v in zip(pts, vs):
            s.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s" stroke="%s" stroke-width="2"/>'
                     % (x, y, GRIS, color))
            s.append('<text x="%.1f" y="%.1f" font-size="10.5" font-weight="700" fill="%s" '
                     'text-anchor="middle" font-family="Inter,sans-serif">%s</text>'
                     % (x, y - 10, NOCHE, _esc("%g%s" % (v, unidad))))
    s.append("</svg>")
    lg = '<div class="leyenda">%s</div>' % "".join(
        '<span><i style="background:%s"></i>%s</span>' % (c, _esc(nm)) for nm, _, c in series)
    return _wrap("".join(s), titulo, sub, lg)


def donut(titulo, sub, segmentos, unidad=""):
    """segmentos: lista de (nombre, valor, color). Centro con total."""
    total = sum(s[1] for s in segmentos) or 1
    R, r, cx, cy = 78, 50, 92, 92
    s = ['<svg viewBox="0 0 184 184" width="184" height="184" role="img" aria-label="%s">'
         % _esc(titulo or "Distribucion")]
    ang = -90.0
    for nombre, v, color in segmentos:
        frac = v / total
        a2 = ang + frac * 360
        if frac >= 0.9999:
            s.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d"/>'
                     % (cx, cy, (R + r) / 2, color, R - r))
        else:
            x1 = cx + R * __import__("math").cos(__import__("math").radians(ang))
            y1 = cy + R * __import__("math").sin(__import__("math").radians(ang))
            x2 = cx + R * __import__("math").cos(__import__("math").radians(a2))
            y2 = cy + R * __import__("math").sin(__import__("math").radians(a2))
            x3 = cx + r * __import__("math").cos(__import__("math").radians(a2))
            y3 = cy + r * __import__("math").sin(__import__("math").radians(a2))
            x4 = cx + r * __import__("math").cos(__import__("math").radians(ang))
            y4 = cy + r * __import__("math").sin(__import__("math").radians(ang))
            lg = 1 if frac > 0.5 else 0
            s.append('<path d="M%.2f %.2f A%d %d 0 %d 1 %.2f %.2f L%.2f %.2f A%d %d 0 %d 0 %.2f %.2f Z" '
                     'fill="%s" stroke="#ffffff" stroke-width="2"/>'
                     % (x1, y1, R, R, lg, x2, y2, x3, y3, r, r, lg, x4, y4, color))
        ang = a2
    s.append('<text x="%d" y="%d" font-size="26" font-weight="700" fill="%s" text-anchor="middle" '
             'font-family="Inter,sans-serif">%d</text>' % (cx, cy + 2, NOCHE, total))
    s.append('<text x="%d" y="%d" font-size="11" fill="%s" text-anchor="middle" '
             'font-family="Inter,sans-serif">%s</text>' % (cx, cy + 18, PROF, _esc(unidad or "total")))
    s.append("</svg>")
    lg = '<div class="leyenda" style="flex-direction:column;gap:8px">%s</div>' % "".join(
        '<span><i style="background:%s"></i>%s <b style="color:#051533">%d</b></span>' % (c, _esc(n), v)
        for n, v, c in segmentos)
    return ('<div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">'
            '<div>%s</div><div style="flex:1;min-width:180px">%s</div></div>'
            % ("".join(s), lg))


def circular(pct, etiqueta, sub="", tam=132, color=AZUL):
    """Anillo de progreso con porcentaje visible."""
    import math
    R, w = tam / 2 - 9, 10
    c = 2 * math.pi * R
    v = max(0, min(100, pct))
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
         % (tam, tam, tam, tam, _esc(etiqueta))]
    s.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="rgba(0,74,147,.15)" stroke-width="%d"/>'
             % (tam / 2, tam / 2, R, w))
    s.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%d" '
             'stroke-linecap="round" stroke-dasharray="%.2f" '
             'transform="rotate(-90 %s %s)"/>'
             % (tam / 2, tam / 2, R, color, w, c * v / 100, tam / 2, tam / 2))
    s.append('<text x="%s" y="%s" font-size="22" font-weight="700" fill="%s" text-anchor="middle" '
             'font-family="Inter,sans-serif">%d%%</text>' % (tam / 2, tam / 2 + 3, NOCHE, round(v)))
    s.append('<text x="%s" y="%s" font-size="10.5" fill="%s" text-anchor="middle" '
             'font-family="Inter,sans-serif">%s</text>' % (tam / 2, tam / 2 + 18, PROF, _esc(etiqueta)))
    s.append("</svg>")
    h = ""
    if sub:
        h = '<div style="font-size:13px;color:#162644;margin-top:6px;text-align:center">%s</div>' % _esc(sub)
    return '<div style="text-align:center">%s%s</div>' % ("".join(s), h)


def progreso_fases(fases):
    """fases: lista de (nombre, pct, color). Barra apilada + tabla de avance."""
    h = '<div style="display:flex;height:22px;border-radius:999px;overflow:hidden;border:1px solid %s">' % GRIS
    for nombre, pct, color in fases:
        if pct > 0:
            h += '<div style="width:%d%%;background:%s" title="%s %d%%"></div>' % (pct, color, nombre, pct)
    h += "</div>"
    filas = ""
    for nombre, pct, color in fases:
        filas += ('<div style="display:flex;align-items:center;gap:10px;padding:7px 0;'
                  'font-size:13px">'
                  '<i style="width:10px;height:10px;border-radius:2px;background:%s;flex:0 0 10px"></i>'
                  '<span style="flex:1;color:#162644">%s</span>'
                  '<b style="color:#051533">%d%%</b></div>' % (color, _esc(nombre), pct))
    return h + '<div style="margin-top:12px">%s</div>' % filas


def stacked_tareas(grupos, unidad="tareas"):
    """grupos: lista de (prioridad, valor, color)."""
    total = sum(g[1] for g in grupos) or 1
    h = '<div style="display:flex;height:22px;border-radius:999px;overflow:hidden;border:1px solid %s">' % GRIS
    for nombre, v, color in grupos:
        h += '<div style="width:%.1f%%;background:%s"></div>' % (v / total * 100, color)
    h += "</div>"
    filas = "".join(
        '<div style="display:flex;align-items:center;gap:10px;padding:6px 0;font-size:13px">'
        '<i style="width:10px;height:10px;border-radius:2px;background:%s;flex:0 0 10px"></i>'
        '<span style="flex:1;color:#162644">Prioridad %s</span>'
        '<b style="color:#051533">%d %s</b></div>' % (c, _esc(n.lower()), v, unidad)
        for n, v, c in grupos)
    return h + '<div style="margin-top:12px">%s</div>' % filas


def velocidad(pct, etiqueta, sub=""):
    """'Velocimetro' horizontal usado en metricas de asesorias."""
    h = ('<div style="font-size:13px;color:#162644;font-weight:500;margin-bottom:6px">%s</div>'
         % _esc(etiqueta))
    h += '<div style="display:flex;align-items:center;gap:10px">'
    h += ('<div style="flex:1;height:8px;background:rgba(0,74,147,.15);border-radius:999px;'
          'overflow:hidden"><div style="width:%d%%;height:100%%;background:%s;border-radius:999px"></div></div>'
          % (pct, AZUL))
    h += '<b style="font-size:14px;color:#051533">%d%%</b></div>' % pct
    if sub:
        h += '<div style="font-size:13px;color:#162644;margin-top:4px">%s</div>' % _esc(sub)
    return h