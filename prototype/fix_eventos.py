with open('paginas_admin.py','r',encoding='utf-8') as f:
    lines = f.readlines()
# Insert after line 139 (1-based) = index 138 (the "# Se pinta con calendario_interactivo" comment)
cal_block = [
    '\n',
    'EVENTOS_CAL = {\n',
    '    18: "<b>Taller de costos y precios</b><br/>Auditorio A \u00b7 32 de 40 cupos \u00b7 Publicado",\n',
    '    22: "<b>Feria de emprendedores</b><br/>Plaza central \u00b7 86 de 120 cupos \u00b7 Publicado",\n',
    '    25: "<b>Jornada de mentoria</b><br/>Sala 2 \u00b7 14 confirmados \u00b7 Por aproximado",\n',
    '}\n',
]
new_lines = lines[:139] + cal_block + lines[139:]
with open('paginas_admin.py','w',encoding='utf-8') as f:
    f.writelines(new_lines)
print('Inserted EVENTOS_CAL')