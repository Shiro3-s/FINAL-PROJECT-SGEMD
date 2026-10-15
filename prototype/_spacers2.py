import re

base = '.'
for fname in ['paginas_estudiante.py','paginas_admin.py']:
    path = fname
    defs=[]
    with open(path,encoding='utf-8') as f:
        for i,l in enumerate(f,1):
            if l.startswith('def '):
                name=l.split('(')[0].replace('def ','').strip()
                defs.append((i,name))
    dmap={}
    for j,(ln,name) in enumerate(defs):
        end=defs[j+1][0]-1 if j+1<len(defs) else 999999
        dmap[name]=(ln,end)
    def fn(i):
        for name,(ln,end) in dmap.items():
            if ln<=i<=end: return name
        return ''
    pat = re.compile(r'<div[^>]*style="([^"]*height:[^"]*)"')
    with open(path,encoding='utf-8') as f:
        for i,l in enumerate(f,1):
            for m in pat.finditer(l):
                print(fname + chr(9) + str(i) + chr(9) + fn(i) + chr(9) + '"' + m.group(1) + '"')
