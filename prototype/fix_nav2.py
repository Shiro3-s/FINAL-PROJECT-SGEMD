with open('lib_ui.py','r',encoding='utf-8') as f: 
    lines = f.readlines()
# Insert after line 107 (1-based) which is the "Gesti\u00f3n de perfiles" item
# Line 107 is at index 106, we want after it, so insert at index 107
new_line = '            ("Asignar docente", "check", "asignar-emprendimiento"),\n'
new_lines = lines[:107] + [new_line] + lines[107:]
with open('lib_ui.py','w',encoding='utf-8') as f:
    f.writelines(new_lines)
print('Inserted NAV item')