# 디오라마 그림: 스킬 아이콘(본편 아틀라스) + 캐릭터/스킨 그림(캐릭터 시트)
import json,os
from PIL import Image
S='/mnt/user-data/uploads/vs_rip/Assets/Resources/spritesheets/';OUT='/home/claude/luckeys-lab.github.io/assets/vs/ed/'
AT=Image.open('/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/Texture2D/tps_lossless_icons.png').convert('RGBA');AH=AT.size[1]
def crop(im,r,H):return im.crop((r['m_X'],H-r['m_Y']-r['m_Height'],r['m_X']+r['m_Width'],H-r['m_Y']))
def up(c,n):return c.resize((c.size[0]*n,c.size[1]*n),Image.NEAREST)
C='/home/claude/cards/emeralds/';icons={};miss=[]
for f in ('weapon.json','item.json'):
    for k,v in json.load(open(C+f)).items():
        fr=v['raw'].get('frameName');p=S+(fr or 'x')[:-4]+'.json'
        if not fr or not os.path.exists(p):miss.append(k);continue
        r=json.load(open(p))['m_Rect'];c=crop(AT,r,AH)
        if not c.getbbox():miss.append(k);continue
        fn=fr[:-4].lstrip('-').replace('06-','')+'.png';up(c,3).save(OUT+'i/'+fn);icons[k]='/assets/vs/ed/i/'+fn
chars={};order={};D='/home/claude/edspr2/characters/'
TEX={}
def tex(n):
    if n not in TEX:
        p=D+n+'.png';TEX[n]=Image.open(p).convert('RGBA') if os.path.exists(p) else None
    return TEX[n]
LOW={x.lower():x for x in os.listdir(D)}
def portrait(texn,sprite):
    j=D+LOW.get((sprite[:-4]+'.json').lower(),'none')
    if not os.path.exists(j):return None
    r=json.load(open(j))['m_Rect']
    for t in [texn]+[x[:-4] for x in os.listdir(D) if x.endswith('.png')]:
        im=tex(t)
        if im is None:continue
        c=crop(im,r,im.size[1])
        if c.getbbox() and c.size[0]>4:
            c=c.crop(c.getbbox());return c
    return None
for k,v in json.load(open(C+'character.json')).items():
    if 'FOLLOWER' in k:continue
    r=v['raw'];out={};seq=[]
    for s in r.get('skins') or [{'skinType':'DEFAULT','textureName':r.get('textureName'),'spriteName':r.get('spriteName')}]:
        sp=s.get('spriteName') or r.get('spriteName');tx=s.get('textureName') or r.get('textureName')
        c=portrait(tx,sp)
        if c:
            fn=f"{k.lower()}_{s.get('skinType','DEFAULT').lower()}.png";up(c,3).save(OUT+'c/'+fn);out[s.get('skinType','DEFAULT')]='/assets/vs/ed/c/'+fn
        seq.append(out.get(s.get('skinType','DEFAULT')) if c else None)
    chars[k]=out;order[k]=seq
json.dump({'icons':icons,'chars':chars,'order':order},open('/home/claude/luckeys-lab.github.io/data/vs/ed/img.json','w'),ensure_ascii=False,indent=0)
print('icons',len(icons),'miss',miss);print('chars',{k:len(v) for k,v in chars.items()})
