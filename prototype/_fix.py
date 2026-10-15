import re

base = 'C:\\Users\\User\\Documents\\SGEMD-Rueda\\FINAL-PROJECT-SGEMD\\prototype'
ui_lines={}
with open(base + '\\lib_ui.py',encoding='utf-8') as f:
  for i,l in enumerate(f,1):
    if l.startswith('def '):
      name=l.split('(')[0].replace('def ','').strip()
      ui_lines[name]=i
css_map={}
with open(base + '\\lib_css.py',encoding='utf-8') as f:
  for i,l in enumerate(f,1):
    if '.' in l and '{' in l:
      tok=l.split('{')[0].strip()
      if tok and tok[0]=='.':
        cname=tok.split()[0][1:]
        if cname and cname not in css_map: css_map[cname]=i

def load_defs(path):
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
  return dmap

def find_fn(dmap,line):
  for name,(ln,end) in dmap.items():
    if ln<=line<=end: return name
  return ''

def classify(s, orig_line=''):
  repl=[]
  sl = s.lower()
  if 'display:flex;gap:24px;align-items:center;flex-wrap:wrap' in s and 'toolbar' in ui_lines:
    repl.append(('toolbar (lib_ui)', ui_lines['toolbar']))
  if ('grid' in s and 'g-4' in s) or 'metrica' in sl:
    if 'metricas' in ui_lines: repl.append(('metricas (lib_ui)', ui_lines['metricas']))
  if 'card' in sl:
    if 'card' in ui_lines: repl.append(('card (lib_ui)', ui_lines['card']))
  if 'avatar' in sl or 'avatar' in orig_line.lower():
    if 'avatar' in css_map: repl.append(('avatar (css)', css_map['avatar']))
  if 'badge' in sl and 'badge' in ui_lines: repl.append(('badge (lib_ui)', ui_lines['badge']))
  if 'btn' in sl:
    if 'boton' in ui_lines: repl.append(('boton (lib_ui)', ui_lines['boton']))
    if 'btn' in css_map: repl.append(('btn (css)', css_map['btn']))
  for cname in ['campo','select','callout','steps','tabs','kanban','linea_tiempo','agenda','lista_def','paginas','migas']:
    if cname in ui_lines: 
      # avoid flooding; only add if somewhat relevant? keep as requested
      repl.append((cname+' (lib_ui)', ui_lines[cname]))
  seen=set(); out=[]
  for r in repl:
    if r[0] not in seen:
      seen.add(r[0]); out.append(r)
    if len(out)>=5: pass  # cap a bit for readability? but user wants matches
  if len(out)==0: return 'UNICO',[]
  return 'REEMPLAZABLE', out

pat=re.compile(r'style="([^"]*)"')
results=[]
for fname in ['paginas_estudiante.py','paginas_admin.py']:
  path=base+'\\'+fname
  dmap=load_defs(path)
  with open(path,encoding='utf-8') as f:
    for i,l in enumerate(f,1):
      for m in pat.finditer(l):
        style=m.group(1)
        fn=find_fn(dmap,i)
        cls,hits=classify(style,l)
        hstr='; '.join(h[0]+':L'+str(h[1]) for h in hits)
        results.append((fname,i,fn,style,cls,hstr))
with open(base + '\\report_final_v2.txt','w',encoding='utf-8') as f:
  for r in results:
    f.write(r[0]+'\t'+str(r[1])+'\t'+r[2]+'\t"'+r[3]+'"\t'+r[4]+'\t'+r[5]+'\n')
print(len(results))
