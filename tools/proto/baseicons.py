# 본편 컬렉션 아이콘: 게임 resources.assets에서 frameName 스프라이트를 잘라 assets/vs/i/ 에 저장 (python3 -I)
import UnityPy,json,os,sys
R='/home/claude/luckeys-lab.github.io';C='/tmp/cards/cards/base/'
SRC='/mnt/user-data/uploads/Vampire Survivors/VampireSurvivors_Data/resources.assets'
env=UnityPy.load(SRC);idx={}
for o in env.objects:
  if o.type.name!='Sprite':continue
  s=o.read()
  try:t=s.m_RD.texture.read().m_Name
  except Exception:t='?'
  idx[(t,s.m_Name)]=s
items=json.load(open(R+'/data/vs/items.json',encoding='utf-8'))
miss=[];new=0
for f in ['item','weapon','arcana']:
  for k,v in json.load(open(C+f+'.json')).items():
    r=v.get('raw',v);fr=(r.get('frameName') or '').replace('.png','');tx=r.get('texture')
    key='ARCANA_'+k if f=='arcana' else k
    if key not in items or not fr:continue
    s=idx.get((tx,fr))
    if not s:miss.append((key,tx,fr));continue
    fn=(('arc_'+fr) if f=='arcana' else fr)+'.png';p=f'{R}/assets/vs/i/{fn}'
    if not os.path.exists(p):
      im=s.image;bb=im.getbbox();(im.crop(bb) if bb else im).save(p,optimize=True);new+=1
    if not items[key].get('i'):items[key]['i']='/assets/vs/i/'+fn
json.dump(items,open(R+'/data/vs/items.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('new',new,'miss',miss)
