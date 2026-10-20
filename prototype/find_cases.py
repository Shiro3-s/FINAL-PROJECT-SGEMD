with open('lib_js.py','r',encoding='utf-8') as f: 
    lines = f.readlines()
for i, l in enumerate(lines, 1):
    if 'case "registrar-avance"' in l or 'case "asignar-docente"' in l:
        print(i, l.rstrip())
    if 'case "confirmar-asignacion"' in l:
        print(i, 'FOUND confirmar-asignacion at', i)