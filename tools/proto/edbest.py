# 디오라마 우화집 카드 + 몹 그림 → data/vs/ed/bestiary.json · assets/vs/ed/e/*.png
import json5,json,os
from PIL import Image
D='/home/claude/edspr3/';OUT='/home/claude/luckeys-lab.github.io/'
E=json5.load(open('/tmp/edj/enemyData_Emeralds.json'))
I2={};cur=None;inl=False
for line in open('/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/Resources/I2Languages.asset',encoding='utf-8'):
    if line.startswith('    - Term: '):cur=line[12:].strip();I2[cur]=[];inl=False;continue
    if cur is None:continue
    if line.startswith('      Languages:'):inl=True;continue
    if inl:
        if line.startswith('      - '):
            v=line[8:].rstrip('\n')
            if len(v)>1 and v[0]==v[-1] and v[0] in "'\"":v=v[1:-1].replace("''","'")
            I2[cur].append(v)
        else:inl=False
I2L={k.lower():v for k,v in I2.items()}
def ko(t,l=11):v=I2.get(t) or I2L.get(t.lower());return v[l] if v and len(v)>l and v[l] else ''
AT=Image.open(D+'emeralds.png').convert('RGBA');H=AT.size[1]
low={x.lower():x for x in os.listdir(D)}
def sprite(frame,key):
    j=low.get(frame[:-4].lower()+'.json') if frame.endswith('.png') else low.get(frame.lower()+'.json')
    if not j:return None
    r=json.load(open(D+j))['m_Rect'];c=AT.crop((r['m_X'],H-r['m_Y']-r['m_Height'],r['m_X']+r['m_Width'],H-r['m_Y']))
    if not c.getbbox():return None
    c=c.crop(c.getbbox());n=max(1,min(4,96//max(c.size)));c=c.resize((c.size[0]*n,c.size[1]*n),Image.NEAREST)
    fn=f'assets/vs/ed/e/{key.lower()}.png';c.save(OUT+fn);return '/'+fn
out=[]
for k,v in E.items():
    v=v[0] if isinstance(v,list) else v
    if not v.get('bInclude'):continue
    fr=(v.get('frameNames') or [''])[0]
    out.append({'id':k,'i':sprite(fr,k),'n':ko(f'enemiesLang/{{{k}}}bName') or v.get('bName') or k,'en':ko(f'enemiesLang/{{{k}}}bName',0),
      'd':ko(f'enemiesLang/{{{k}}}bDesc').replace('\\n',' ').strip(),'hp':v.get('maxHp'),'pw':v.get('power'),'sp':v.get('speed'),'xp':v.get('xp'),
      'boss':'GATEBOSS' in k or 'BOSS' in k,'hpxlv':'HP_x_Level' in (v.get('skills') or []),'idx':v.get('bIndex',999),
      'res':{x[4:]:v[x] for x in ('res_Freeze','res_Rosary','res_Debuffs','res_Defang') if v.get(x)}})
out.sort(key=lambda x:(x['idx'] if isinstance(x['idx'],(int,float)) else 999))
json.dump(out,open(OUT+'data/vs/ed/bestiary.json','w'),ensure_ascii=False,indent=0)
print(len(out),sum(1 for x in out if x['i']),[x['n'] for x in out][:23])
