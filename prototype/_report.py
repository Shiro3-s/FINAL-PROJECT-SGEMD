base = 'C:\\Users\\User\\Documents\\SGEMD-Rueda\\FINAL-PROJECT-SGEMD\\prototype'
# maps
ui_lines = {}
with open(base + '\\lib_ui.py', encoding='utf-8') as f:
    for i,l in enumerate(f,1):
        if l.startswith('def '):
            name = l.split('(')[0].replace('def ','').strip()
            ui_lines[name] = i
css_map = {}
with open(base + '\\lib_css.py', encoding='utf-8') as f:
    for i,l in enumerate(f,1):
        if '.' in l and '{' in l:
            tok = l.split('{')[0].strip()
            if tok and tok[0]=='.':
                parts = tok.split()[0]
                cname = parts[1:]
                if cname not in css_map:
                    css_map[cname] = i
