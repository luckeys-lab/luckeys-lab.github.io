# python3 -I stage.py <bundle> : 오브젝트 목록(/tmp/<b>_L.json) · y는 화면 기준(위 +)
import json,sys,struct,UnityPy
b=sys.argv[1]
B='/mnt/user-data/uploads/C:--vs_rip/AssetRipper_export_20261127_110646/ExportedProject/Assets/StreamingAssets/aa/StandaloneWindows64/'
def strs(raw):
  out=[];i=0
  while i+4<=len(raw):
    n=struct.unpack_from('<i',raw,i)[0]
    if 0<n<200 and i+4+n<=len(raw):
      try:
        t=raw[i+4:i+4+n].decode('utf-8')
        if t.isprintable():out.append(t);i=(i+4+n+3)&~3;continue
      except Exception:pass
    i+=4
  return out
env=UnityPy.load(B+'vs_local_assets_'+b+'.bundle',B+'9157bd7583fd8f3cacf1afb11d5c32e5_monoscripts.bundle')
so={};cp={}
for o in env.objects:
  if o.type.name!='MonoBehaviour':continue
  x=o.read()
  try:cn=x.m_Script.read().m_ClassName
  except Exception:continue
  if cn=='SuperObject':so[x.m_GameObject.m_PathID]=strs(x.object_reader.get_raw_data())
  elif cn=='SuperCustomProperties':cp[x.m_GameObject.m_PathID]=strs(x.object_reader.get_raw_data())
L=[]
for o in env.objects:
  if o.type.name!='GameObject' or o.path_id not in so:continue
  g=o.read();tr=next((c.read() for c in g.m_Components if c.read().object_reader.type.name=='Transform'),None)
  wx=wy=0;t=tr;chain=[]
  while t:
    wx+=t.m_LocalPosition.x;wy+=t.m_LocalPosition.y;chain.append(t.m_GameObject.read().m_Name);t=t.m_Father.read() if t.m_Father and t.m_Father.m_PathID else None
  if any(c.startswith('ADV') for c in chain):continue
  s=so[o.path_id];pr=cp.get(o.path_id,[]);d=dict(zip(pr[0::3],pr[2::3]))
  L.append({'n':g.m_Name,'t':s[1] if len(s)>1 else s[0],'px':wx*100,'py':-wy*100,'xm':int(float(d.get('xMultiplier',0))),'ym':-int(float(d.get('yMultiplier',0))),'ch':d.get('chance'),'g':d.get('guards'),'all':d})
json.dump(L,open(f'/tmp/{b}_L.json','w'),ensure_ascii=False,indent=0)
for o in L:print(o['n'],o['t'],o['xm'],o['ym'],o['ch'] or '',o['g'] or '',{k:v for k,v in o['all'].items() if k not in('xMultiplier','yMultiplier','chance','guards')} or '')
