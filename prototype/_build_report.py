import sys
base = 'C:\\Users\\User\\Documents\\SGEMD-Rueda\\FINAL-PROJECT-SGEMD\\prototype'

# lib_ui primitives/classes
ui_lines = {}
try:
    with open(base + '\\lib_ui.py', encoding='utf-8') as f:
        for i,l in enumerate(f,1):
            if 'def ' in l and l.startswith('def '):
                name = l.split('(')[0].replace('def ','').strip()
                ui_lines[name] = i
except Exception as e:
    pass

# lib_css classes
css_classes = []
try:
    with open(base + '\\lib_css.py', encoding='utf-8') as f:
        for i,l in enumerate(f,1):
            if '.' in l and '{' in l:
                # crude extract class name before { - first token
                tok = l.split('{')[0].strip()
                # take first class/thing
                if tok and tok[0]=='.':
                    cname = tok.split()[0][1:]  # first class
                    css_classes.append((cname,i,l))
except Exception as e:
    pass
css_set = {c[0] for c in css_classes}
css_map = {c[0]:(c[1], c[2]) for c in css_classes}

# helper to classify
def classify(style):
    s = style
    # common ui primitives
    # metricas/card/tabla/badge/campo/select/callout/lista_def/steps/tabs/kanban/linea_tiempo/agenda
    # check against known component class usage? maybe 'card' in style? not directly
    # look for patterns that map to components
    repl = []
    # card-like: padding/card borders
    if 'card' in s or 'border-radius:12px' in s or 'background:var(--blanco)' in s and 'box-shadow' in s:
        if 'card' in ui_lines:
            repl.append(('card', ui_lines['card']))
    if 'metrica' in s or ('grid' in s and 'g-4' in s):
        if 'metricas' in ui_lines:
            repl.append(('metricas', ui_lines['metricas']))
    if 'tabla' in s or 'data-label' in s or '<table' in s:  # not style but hint
        pass
    # check for specific class names appearing
    for c in css_set:
        if c in s:  # token
            linfo = css_map[c]
            repl.append((c, linfo[0]))
    if len(repl) == 0:
        return 'UNICO', []
    else:
        return 'REEMPLAZABLE', repl[:3]
