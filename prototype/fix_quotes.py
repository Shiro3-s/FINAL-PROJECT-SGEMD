with open('paginas_admin.py','r',encoding='utf-8') as f: 
    lines = f.readlines()

# Fix: replace the broken triple-quoted string with regular string concatenation
# Find and replace line 1098 which has the problematic """ 
for i in range(len(lines)):
    if i < len(lines) and '"""' in lines[i] and i > 1090 and i < 1105:
        # Replace the line with regular string concatenation
        lines[i] = lines[i].replace('+ """', '+ \"\"\"')  # Actually just use regular string
        # Better: find the specific line and fix it
        pass

# Let me just remove the """ and make it regular string
# Line 1098: '    cuerpo += \'<div id="form-asignar-docente" hidden>\' + \'</div>\' + """\n'
# Change to: '    cuerpo += \'<div id="form-asignar-docente" hidden>\' + \'</div>\' + \"\"\n'
# Actually, let me just replace the specific broken pattern

with open('paginas_admin.py','r',encoding='utf-8') as f: 
    content = f.read()

# Replace the broken triple-quote pattern
old = \"    cuerpo += '<div id=\"form-asignar-docente\" hidden>' + '</div>' + \"\"\"\"
new = \"    cuerpo += '<div id=\\\"form-asignar-docente\\\" hidden>' + '</div>' + ''\"\"

# Actually, let me just remove the """ and use empty string
old2 = \"    cuerpo += '<div id=\"form-asignar-docente\" hidden>' + '</div>' + \\\"\\\"\\\"\\\"\"
# This is getting messy. Let me just replace the specific line content.

# Simple approach: find the '''docstring''' issue and fix
# The problem is the + """ at line 1098. Let me just replace it.
content = content.replace(
    \"    cuerpo += '<div id=\"form-asignar-docente\" hidden>' + '</div>' + \\\"\\\"\\\"\\\"\",
    \"    cuerpo += '<div id=\"form-asignar-docente\" hidden>' + '</div>' + ''\"
)

with open('paginas_admin.py','w',encoding='utf-8') as f:
    f.write(content)
print('Fixed triple-quote issue')