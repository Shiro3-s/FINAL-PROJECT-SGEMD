with open('paginas_admin.py','r',encoding='utf-8') as f: 
    lines = f.readlines()

# Fix line 1098 (0-based index 1097): replace the triple-quote string concatenation
# Original problematic line (after my insertion):
#     cuerpo += '<div id="form-asignar-docente" hidden>' + '</div>' + """
# 
# Replace with regular string concatenation using empty string:
#     cuerpo += '<div id="form-asignar-docente" hidden>' + '</div>' + ''
#
lines[1097] = '    cuerpo += \'<div id="form-asignar-docente" hidden>\' + \'</div>\' + \"\"\n'

with open('paginas_admin.py','w',encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed line 1097')