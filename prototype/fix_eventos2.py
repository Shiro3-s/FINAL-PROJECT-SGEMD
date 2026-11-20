with open('paginas_admin.py','r',encoding='utf-8') as f: 
    lines = f.readlines()

# Find the start of def eventos() and replace the whole function
# up to the next # --- section or def, but keeping the migas/shell return
# First, locate line numbers
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'def eventos():' in line:
        start_idx = i
    if start_idx is not None and i > start_idx:
        # Look for the next top-level def or # --- section
        if line.strip().startswith('def ') or (line.strip().startswith('# ---') and i > start_idx + 5):
            end_idx = i
            break

if start_idx is None:
    print('ERROR: def eventos() not found')
elif end_idx is None:
    print('ERROR: could not find end of eventos()')
else:
    # Replace lines[start_idx:end_idx] with new function
    nuevo = '''def eventos():
    """Pipeline editorial: el admin aprueba y publica, no solo lista."""
    cuerpo = metricas([
        ("calendar", "Eventos publicados", "2", "", 40, None),
        ("reloj", "Por aprobar", "1", "", 20, None),
        ("doc", "Borradores", "1", "", 20, None),
        ("users", "Confirmaciones", "141", "", 88, "+37"),
    ])
    cuerpo += '<div class="sep sep-20"></div>'
    cuerpo += '<div data-vacio-lista>' + calendario_interactivo("noviembre", 2024, EVENTOS_CAL, hoy=12, vacio="Sin eventos") + '</div>'
    cuerpo += ('<p class="nota-foot">Publicar un evento notifica a los estudiantes '
               'del sector correspondiente.</p>')
    cuerpo = formulario("eventos", cuerpo)
    return shell(R, "eventos", "Eventos", cuerpo,
                 migas=["Inicio", "Eventos"],
                 sub="Aprueba y publica eventos del programa.",
                 acciones=_btn("plus", "Crear evento", "evento-form.html"))
'''
    new_lines = lines[:start_idx] + [nuevo] + lines[end_idx:]
    with open('paginas_admin.py','w',encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Replaced eventos() function')