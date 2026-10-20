with open('paginas_admin.py','r',encoding='utf-8') as f: 
    lines = f.readlines()

# Insert the modal before the formulario call (after line 1095 'cuerpo += "</div></div>"')
# Line 1095 is at index 1094 (0-based). I want to insert after it, at index 1095, 
# pushing the formulario line down.
modal = '''\n    # Modal para asignar docente por fila
    cuerpo += '<div id="form-asignar-docente" hidden>' + '</div>' + \"\"\"
    cuerpo += '<div class="grid">'
    cuerpo += campo("Estudiante", bloqueo="No editable", name="estudiante")
    cuerpo += campo("Emprendimiento", bloqueo="No editable", name="emprendimiento")
    cuerpo += campo("Correo", bloqueo="No editable", name="correo")
    cuerpo += "</div>"
    cuerpo += '<div class="grid g-2">'
    cuerpo += select("Docente", [d[1] + \" - \" + d[3] for d in DOCENTES] + [\"Sin asignar\"], req=True, name="docente")
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

# Insert after line 1095 (1-based) = index 1095 (0-based), which is the formulario line
# Actually line 1095 (1-based) = index 1094 (0-based). The formulario line is at 1096 (1-based) = index 1095.
# I want to insert BEFORE the formulario line, so at index 1095 (0-based).
insert_idx = 1095  # 0-based index, after the 1095th line (which is '</div></div>')
new_lines = lines[:insert_idx] + [modal] + lines[insert_idx:]
with open('paginas_admin.py','w',encoding='utf-8') as f:
    f.writelines(new_lines)
print('Added #form-asignar-docente modal at index', insert_idx)