with open('paginas_admin.py','r',encoding='utf-8') as f:
    content = f.read()

old = """# Se pinta con calendario_interactivo (data-cal-doc) y lo controla ADMIN_JS.
EVENTOS_CAL = {
    18: agenda([("09:00", "Taller de costos y precios",
                 "Auditorio A Ã© 32 de 40 cupos", badge("Publicado", "b-azul"))]),
    22: agenda([("14:00", "Feria de emprendedores",
                 "Plaza central Ã© 86 de 120 cupos", badge("Publicado", "b-azul"))]),
    25: agenda([("08:30", "Jornada de mentoria",
                 "Sala 2 Ã© 14 confirmados", badge("Por aprobar", "b-amarillo", "reloj"))]),
}"""

new = """# Se pinta con calendario_interactivo (data-cal-doc) y lo controla ADMIN_JS.
EVENTOS_CAL = {
    18: "<b>Taller de costos y precios</b><br/>Auditorio A · 32 de 40 cupos · Publicado",
    22: "<b>Feria de emprendedores</b><br/>Plaza central · 86 de 120 cupos · Publicado",
    25: "<b>Jornada de mentoria</b><br/>Sala 2 · 14 confirmados · Por aprobar",
}"""

if old in content:
    content = content.replace(old, new)
    with open('paginas_admin.py','w',encoding='utf-8') as f:
        f.write(content)
    print('REPLACED OK')
else:
    print('OLD NOT FOUND - searching for partial')
    if 'EVENTOS_CAL' in content:
        print('EVENTOS_CAL found but format different')
    if 'agenda' in content:
        print('agenda calls still present')