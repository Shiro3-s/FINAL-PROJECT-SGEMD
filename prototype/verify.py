with open('paginas_admin.py','r',encoding='utf-8') as f: 
    pa = f.read()
with open('lib_ui.py','r',encoding='utf-8') as f: 
    lu = f.read()
with open('lib_js.py','r',encoding='utf-8') as f: 
    lj = f.read()

checks = [
    ('registrar function in admin', 'def registrar(' in pa),
    ('EVENTOS_CAL defined', 'EVENTOS_CAL' in pa),
    ('CORREOS_EST defined', 'CORREOS_EST' in pa),
    ('calendario_interactivo imported', 'calendario_interactivo' in lu),
    ('NAV item Asignar docente', 'Asignar docente' in lu),
    ('case registrar-avance in lib_js', 'case "registrar-avance"' in lj),
    ('case asignar-docente in lib_js', 'case "asignar-docente"' in lj),
    ('#form-avance in admin', '#form-avance' in pa),
    ('#form-asignar-docente in admin', '#form-asignar-docente' in pa),
    ('calendario_interactivo call in eventos', 'calendario_interactivo' in pa),
]

for name, result in checks:
    status = 'OK' if result else 'FALTANTE'
    print(f'  {status}: {name}')