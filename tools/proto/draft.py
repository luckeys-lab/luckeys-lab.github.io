import json,sys,struct,UnityPy
from PIL import Image,ImageDraw,ImageFont
sys.argv=['x'];exec(open('/home/claude/map/so.py').read().split('env=UnityPy')[0])
R='/home/claude/luckeys-lab.github.io'
items=json.load(open(R+'/data/vs/items.json'))
objs={o['n']+'|'+str(o['xy']):o for o in json.load(open('/tmp/forest_objs.json'))}
env=UnityPy.load(B+'vs_local_assets_forest.bundle',B+'9157bd7583fd8f3cacf1afb11d5c32e5_monoscripts.bundle')
typ={}
for o in env.objects:
  if o.type.name!='MonoBehaviour':continue
  x=o.read()
  try:
    if x.m_Script.read().m_ClassName!='SuperObject':continue
  except Exception:continue
  s=strs(x.object_reader.get_raw_data());typ[x.m_GameObject.m_PathID]=s[1] if len(s)>1 else s[0]
# 게임오브젝트 pathid로 다시 매칭
L=[]
for o in env.objects:
  if o.type.name!='GameObject':continue
  g=o.read()
  if o.path_id not in typ:continue
  tr=None
  for c in g.m_Components:
    x=c.read()
    if x.object_reader.type.name=='Transform':tr=x
  wx=wy=0;t=tr
  while t:
    wx+=t.m_LocalPosition.x;wy+=t.m_LocalPosition.y;t=t.m_Father.read() if t.m_Father and t.m_Father.m_PathID else None
  par=tr.m_Father.read().m_GameObject.read().m_Name
  if par.startswith('ADV'):continue
  pr=next((v for k,v in objs.items() if v['n']==g.m_Name and abs(v['xy'][0]-wx)<.01 and abs(v['xy'][1]-wy)<.01),{'p':[]})['p']
  d=dict(zip(pr[0::3],pr[2::3]))
  L.append({'n':g.m_Name,'t':typ[o.path_id],'px':wx*100,'py':-wy*100,'xm':int(d.get('xMultiplier',0)),'ym':int(d.get('yMultiplier',0)),'ch':d.get('chance'),'g':d.get('guards')})
json.dump(L,open('/tmp/forest_L.json','w'),ensure_ascii=False,indent=0)
M=Image.open('/tmp/forest.png').convert('RGBA');D=ImageDraw.Draw(M)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
for o in L:
  x,y=o['px'],o['py'];k=o['t'];it=items.get(k)
  if o['n']=='PlayerStart':D.ellipse((x-30,y-30,x+30,y+30),outline=(255,215,0),width=8);D.text((x+34,y-18),'START',fill=(255,215,0),font=f);continue
  if it and it.get('i'):
    ic=Image.open(R+it['i']).convert('RGBA').resize((64,64),Image.NEAREST);M.alpha_composite(ic,(int(x-32),int(y-32)))
  else:D.rectangle((x-24,y-24,x+24,y+24),outline=(255,80,80),width=6);D.text((x-20,y-18),k[:3],fill=(255,255,255),font=f)
  lab=f"{'→' if o['xm']>0 else '←' if o['xm']<0 else ''}{abs(o['xm']) or ''} {'↑' if o['ym']>0 else '↓' if o['ym']<0 else ''}{abs(o['ym']) or ''}"
  D.text((x+34,y-18),lab,fill=(255,255,255),font=f,stroke_width=3,stroke_fill=(0,0,0))
M.resize((1024,1024),Image.LANCZOS).save('/home/claude/map/forest_draft.png')
for o in L:print(o['n'],o['t'],o['xm'],o['ym'],o['ch'],o['g'])
