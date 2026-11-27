# 본편 지도 데이터 → data/vs/base_map.json · assets/vs/map/b/*.png · 줍는 것 아이콘 assets/vs/i/ (python3 -I)
import json,os,UnityPy
from PIL import Image
R='/home/claude/luckeys-lab.github.io';S=json.load(open('/home/claude/map/out/summary.json'))
items=json.load(open(R+'/data/vs/items.json'));card=json.load(open('/tmp/cards/cards/base/item.json'))
SRC='/mnt/user-data/uploads/Vampire Survivors/VampireSurvivors_Data/resources.assets'
idx={}
for o in UnityPy.load(SRC).objects:
  if o.type.name=='Sprite':
    s=o.read();idx.setdefault(s.m_Name,s)
EXTRA={'CFF':'관','Coffin':'관','COFFIN_LYCA':'관','Piano':'피아노','DISK_MRC':'디스크 상인','MRC_BIGTROUBLER':'상인','ARCANACHEST':'아르카나 상자','Darkasso':'다르카소','EX_17COLOSSUS_BURIED':'묻힌 거상','ASTRALSTAIR_PIZZA':'피자','Pizza':'피자','PIZZA_CRAB':'피자','PIZZA_SALMON':'피자','PIZZA_SEAL':'피자','PIZZA_TRITON':'피자','UNO':'❓','GIOCARE':'❓','ROSARYX':'묵주','StartLeft':'시작(왼쪽)','StartRight':'시작(오른쪽)'}
def info(t):
  if t in items:return items[t]['n'],items[t].get('i')
  c=card.get(t)
  if c:
    n=c.get('ko',{}).get('name') or t;fr=(c.get('raw',{}).get('frameName') or '').replace('.png','');p=None
    if fr and fr in idx:
      p=f'/assets/vs/i/{fr}.png'
      if not os.path.exists(R+p):
        im=idx[fr].image;bb=im.getbbox();(im.crop(bb) if bb else im).save(R+p,optimize=True)
    return n,p
  return EXTRA.get(t,t),None
out=[]
for k,v in S.items():
  if v=='FAIL':continue
  im=Image.open(f'/home/claude/map/out/{k}.png').convert('RGB');s=min(1,1000/max(im.size))
  if s<1:im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
  im.quantize(256,method=Image.Quantize.MEDIANCUT).save(f'{R}/assets/vs/map/b/{k.lower()}.png',optimize=True)
  ob=[]
  for o in v['objs']:
    n,i=info(o['t']);ob.append({'t':o['t'],'n':n,'i':i,'xm':o['xm'],'ym':o['ym'],'ch':float(o['ch']) if o['ch'] else None,'pos':[round(o['pos'][0]*100,1),round(o['pos'][1]*100,1)] if o.get('pos') else None})
  out.append({'k':k,'n':v['n'],'tiled':v['tiled'],'img':f'/assets/vs/map/b/{k.lower()}.png','w':im.width,'h':im.height,'o':ob,'far':[{'t':t,'n':info(t)[0],'xm':x,'ym':y} for t,x,y in v.get('far',[])]})
json.dump(out,open(R+'/data/vs/base_map.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(out),sum(len(x['o']) for x in out),[ (o['t']) for x in out for o in x['o'] if o['n']==o['t']][:20])
