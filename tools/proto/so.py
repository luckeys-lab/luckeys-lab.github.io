import UnityPy,struct
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
env=UnityPy.load(B+'vs_local_assets_forest.bundle',B+'9157bd7583fd8f3cacf1afb11d5c32e5_monoscripts.bundle')
for o in env.objects:
  if o.type.name!='MonoBehaviour':continue
  x=o.read()
  try:
    if x.m_Script.read().m_ClassName!='SuperObject':continue
  except Exception:continue
  g=x.m_GameObject.read().m_Name
  if g.startswith(('Weapon','CFF','Yellow')):
    raw=x.object_reader.get_raw_data();print(g,strs(raw)[:8],len(raw))
