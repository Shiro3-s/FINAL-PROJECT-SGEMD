path = 'paginas_admin.py'
defs = []
with open(path, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if line.startswith('def '):
            name = line.split('(')[0].replace('def ', '').strip()
            defs.append((i, name))
dmap = {}
for j, (ln, name) in enumerate(defs):
    end = defs[j+1][0]-1 if j+1 < len(defs) else 999999
    dmap[name] = (ln, end)
import re
pat = re.compile(r'style="([^"]*)"')
with open(path, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        for m in pat.finditer(line):
            s = m.group(1)
            fn = None
            for name, (ln, end) in dmap.items():
                if ln <= i <= end:
                    fn = name; break
            print(str(i) + '\t' + (fn or '') + '\t' + s)
