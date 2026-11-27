# 스테이지 번들 → 오브젝트(이름·월드좌표·Tiled 커스텀 속성) json
import UnityPy,sys,json,struct,re
B='/mnt/user-data/uploads/C:--vs_rip/AssetRipper_export_20261127_110646/ExportedProject/Assets/StreamingAssets/aa/StandaloneWindows64/'
env=UnityPy.load(B+'vs_local_assets_'+sys.argv[1]+'.bundle',B+'9157bd7583fd8f3cacf1afb11d5c32e5_monoscripts.bundle')
def strs(raw):
  out=[];i=0
  while i+4<=len(raw):
    n=struct.unpack_from('<i',raw,i)[0]
    if 0<n<200 and i+4+n<=len(raw):
      s=raw[i+4:i+4+n]
      try:
        t=s.decode('utf-8')
        if t.isprintable():out.append(t);i+=4+n;i=(i+3)&~3;continue
      except Exception:pass
    i+=4
  return out
def world(tr):
  x=y=0
  while tr:
    p=tr.m_LocalPosition;x+=p.x;y+=p.y
    tr=tr.m_Father.read() if tr.m_Father and tr.m_Father.m_PathID else None
  return round(x,3),round(y,3)
res=[]
for o in env.objects:
  if o.type.name!='GameObject':continue
  g=o.read();tr=None;props=None
  for c in g.m_Components:
    try:
      x=c.read();tn=x.object_reader.type.name
      if tn=='Transform':tr=x
      elif tn=='MonoBehaviour' and x.m_Script.read().m_ClassName=='SuperCustomProperties':
        props=strs(x.object_reader.get_raw_data())
    except Exception:pass
  if props is None or not tr:continue
  par=tr.m_Father.read().m_GameObject.read().m_Name if tr.m_Father and tr.m_Father.m_PathID else ''
  res.append({'n':g.m_Name,'par':par,'xy':world(tr),'p':props})
json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
for r in res:
  if not r['par'].startswith('ADV'):print(r['n'],r['xy'],r['p'][:12])
