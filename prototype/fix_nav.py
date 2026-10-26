with open('lib_ui.py','r',encoding='utf-8') as f:
    content = f.read()

old = '(("Gesti\u00f3n de perfiles", "users", "usuarios"),\n    ("Asignaciones", "sliders", "asignaciones"),)'
# The actual old string in the file (with actual Unicode)
old_actual = '("Gesti\u00f3n de perfiles", "users", "usuarios"),\n    ("Asignaciones", "sliders", "asignaciones"),'

new = '("Gesti\u00f3n de perfiles", "users", "usuarios"),\n    ("Asignar docente", "check", "asignar-emprendimiento"),\n    ("Asignaciones", "sliders", "asignaciones"),'

if old_actual in content:
    content = content.replace(old_actual, new)
    with open('lib_ui.py','w',encoding='utf-8') as f:
        f.write(content)
    print('NAV item inserted')
else:
    print('Old string not found')
    # Let's find what's actually there
    idx = content.find('Usuarios y asignaciones')
    if idx >= 0:
        print('Found at', idx)
        print(repr(content[idx:idx+100]))