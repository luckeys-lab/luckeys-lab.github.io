# 본편 스테이지 번들 → 타일 렌더 + 오브젝트 목록 (python3 -I rend.py <bundle이름> <출력>)
import UnityPy,sys,json
from PIL import Image
B='/mnt/user-data/uploads/C:--vs_rip/AssetRipper_export_20261127_110646/ExportedProject/Assets/StreamingAssets/aa/StandaloneWindows64/'
name,out=sys.argv[1],sys.argv[2]
env=UnityPy.load(B+'vs_local_assets_'+name+'.bundle')
ORDER=['Floor','FloorOverlay','Decals','Overlay1','Obstacle','FakeWalls','Walls']
tms={}
cache={}
for o in env.objects:
  if o.type.name=='Tilemap':
    t=o.read_typetree();go=o.read().m_GameObject.read().m_Name;tms[go]=(o,t)
xs=[];ys=[]
def ent(t):
  for e in t['m_Tiles']:
    pos,d=(e['first'],e['second']) if isinstance(e,dict) else e
    yield pos,d
for g,(o,t) in tms.items():
  for pos,d in ent(t):xs.append(pos['x']);ys.append(pos['y'])
x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys);P=32
img=Image.new('RGBA',((x1-x0+1)*P,(y1-y0+1)*P),(0,0,0,255))
def spr(o,t,i):
  k=(id(t),i)
  if k in cache:return cache[k]
  ref=t['m_TileSpriteArray'][i]['m_Data']
  im=None
  try:
    s=o.assets_file.objects[ref['m_PathID']].read();im=s.image
  except Exception as e:pass
  cache[k]=im;return im
for g in ORDER:
  if g not in tms:continue
  o,t=tms[g];mats=t.get('m_TileMatrixArray',[])
  for pos,d in ent(t):
    im=spr(o,t,d['m_TileSpriteIndex'])
    if im is None:continue
    m=mats[d['m_TileMatrixIndex']]['m_Data'] if mats else None
    if m:
      if m['e00']<0:im=im.transpose(Image.FLIP_LEFT_RIGHT)
      if m['e11']<0:im=im.transpose(Image.FLIP_TOP_BOTTOM)
    px=(pos['x']-x0)*P;py=(y1-pos['y'])*P+P-im.height
    img.alpha_composite(im.convert('RGBA'),(px,py))
img.save(out)
print('size',img.size,'origin',x0,y1,'layers',list(tms))
