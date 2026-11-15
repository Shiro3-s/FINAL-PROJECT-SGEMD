import os
BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, 'paginas_admin.py'), 'r', encoding='utf-8') as f:
    pa = f.read()
with open(os.path.join(BASE, 'lib_ui.py'), 'r', encoding='utf-8') as f:
    lu = f.read()
with open(os.path.join(BASE, 'lib_js.py'), 'r', encoding='utf-8') as f:
    lj = f.read()

checks = [
    ('registrar function in admin', 'def registrar(' in pa),
    ('EVENTOS_CAL defined', 'EVENTOS_CAL' in pa),
    ('CORREOS_EST defined', 'CORREOS_EST' in pa),
    ('calendario_interactivo imported', 'calendario_interactivo' in lu),
    ('NAV sin Asignar docente', 'Asignar docente' not in lu),
    ('case registrar-avance in lib_js', 'case "registrar-avance"' in lj),
    ('case asignar-docente in lib_js', 'case "asignar-docente"' in lj),
    ('calendario_interactivo call in eventos', 'calendario_interactivo' in pa),
    ('usuario-detalle page registered', 'usuario-detalle.html' in pa),
    ('solicitud-detalle page registered', 'solicitud-detalle.html' in pa),
    ('emprendimiento-detalle page registered', 'emprendimiento-detalle.html' in pa),
    ('seguimiento-detalle page registered', 'seguimiento-detalle.html' in pa),
    ('asesoria-detalle page registered', 'asesoria-detalle.html' in pa),
    ('evento-detalle page registered', 'evento-detalle.html' in pa),
    ('diagnostico-detalle page registered', 'diagnostico-detalle.html' in pa),
    ('tarea-detalle page registered', 'tarea-detalle.html' in pa),
    ('asignacion-form page registered', 'asignacion-form.html' in pa),
]

for name, result in checks:
    status = 'OK' if result else 'FALTANTE'
    print(f'  {status}: {name}')
