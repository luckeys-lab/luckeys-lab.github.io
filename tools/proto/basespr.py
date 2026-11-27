import UnityPy,json,glob,os,sys
from PIL import Image
R='/home/claude/luckeys-lab.github.io'
B='/mnt/user-data/uploads/C:--vs_rip/AssetRipper_export_20261127_110646/ExportedProject/Assets/StreamingAssets/aa/StandaloneWindows64/'
cards=json.load(open('/tmp/cards/cards/base/character.json'))
chars=json.load(open(R+'/data/vs/base_chars.json'))
cache={}
def sprites(tex):
  if tex in cache: return cache[tex]
  m={}
  env=UnityPy.load(B+'vs_local_assets_'+tex.lower()+'.bundle')
  for o in env.objects:
    if o.type.name=='Sprite':
      d=o.read(); m[d.m_Name]=d
  cache[tex]=m;return m
def up(im,k=3): 
  bb=im.getbbox(); im=im.crop(bb) if bb else im
  return im.resize((im.width*k,im.height*k),Image.NEAREST)
os.makedirs(R+'/assets/vs/c/s',exist_ok=True)
miss=[]
for c in chars:
  r=cards[c['id']]['raw']; slug=os.path.basename(c['img'] or ('/'+c['id'].lower()+'.png'))[:-4]
  sp=sprites(r['textureName']); n=r['spriteName'].replace('.png','')
  if n not in sp: miss.append((c['id'],n));continue
  up(sp[n].image).save(f'{R}/assets/vs/c/{slug}.png',optimize=True)
  c['img']=f'/assets/vs/c/{slug}.png'
  sk=[]
  for s in r.get('skins',[]):
    spp=sprites(s['textureName']); sn=s['spriteName'].replace('.png','')
    if sn not in spp: miss.append((c['id'],s['skinType'],sn));continue
    fn=f'{slug}_{s["skinType"].lower()}.png'
    up(spp[sn].image).save(f'{R}/assets/vs/c/s/{fn}',optimize=True)
    sk.append({'t':s['skinType'],'n':s.get('name'),'img':'/assets/vs/c/s/'+fn})
  c['skimg']=sk
json.dump(chars,open(R+'/data/vs/base_chars.json','w'),ensure_ascii=False,indent=1)
print('miss',miss)
