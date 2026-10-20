with open('paginas_admin.py','r',encoding='utf-8') as f: 
    lines = f.readlines()

# Insert the modal before the formulario call (after line 1095 which is '</div></div>')
# Line 1095 is at index 1094, we want to insert after it, at index 1095
modal = '''\n    # Modal para asignar docente por fila
    cuerpo += '<div id="form-asignar-docente" hidden>' + '</div>' + \"\"\"
    cuerpo += '<div class="grid">'
    cuerpo += campo("Estudiante", bloqueo="No editable", name="estudiante")
    cuerpo += campo("Emprendimiento", bloqueo="No editable", name="emprendimiento")
    cuerpo += campo("Correo", bloqueo="No editable", name="correo")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Docente", [d[1] + " - " + d[3] for d in DOCENTES] + ["Sin asignar"], req=True, name="docente")
    cuerpo += campo("Horas semanales", tipo="number", valor="2", req=True, name="horas")
    cuerpo += "</div>"
    cuerpo += '<div class="fila" style="margin-top:16px">'
    cuerpo += '<button class="btn btn-primario" data-accion="guardar-asignacion-docente">'
    cuerpo += '%s Guardar asignaci\u00f3n</button>' % ico("check", 16)
    cuerpo += '<a class="btn btn-secundario" href="asignaciones.html">'
    cuerpo += '%s Volver</a>' % ico("izq", 16)
    cuerpo += "</div>"
    cuerpo += '<div class="nota-foot">El docente y el estudiante reciben una '
    cuerpo += "notificaci\u00f3n con la asignaci\u00f3n.</div>"
    cuerpo += "</div>"
'''

# Insert after line 1095 (index 1094), which is the last line before formulario
# The line 1095 is '    cuerpo = formulario("asignar", cuerpo)\n'
# I want to insert before that, after the '</div></div>' at line 1095
# Actually let me find the exact index of the formulario line
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if i == 1094 and 'formulario("asignar"' in line:
        # Insert the modal before this line
        new_lines.append(modal)
        break

with open('paginas_admin.py','w',encoding='utf-8') as f:
    f.writelines(new_lines)
print('Added #form-asignar-docente modal')