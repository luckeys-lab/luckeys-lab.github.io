# 본편 우화집 → data/vs/base_bestiary.json · assets/vs/e/*.png (python3 -I · 게임 ENEMY_DATA + enemies*.bundle + I2)
import json5,json,UnityPy,glob
from PIL import Image
X='/mnt/user-data/uploads/C:--vs_rip/AssetRipper_export_20261127_110646/ExportedProject/Assets/'
OUT='/home/claude/luckeys-lab.github.io/'
E=json5.load(open(X+'TextAsset/ENEMY_DATA.json'))
I2={};cur=None;inl=False
for line in open(X+'Resources/I2Languages.asset',encoding='utf-8'):
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
SP={}
for b in glob.glob(X+'StreamingAssets/aa/StandaloneWindows64/vs_local_assets_enemies*.bundle'):
    for o in UnityPy.load(b).objects:
        if o.type.name=='Sprite':
            s=o.read();SP.setdefault(s.m_Name.lower(),s)
def sprite(fr,key):
    s=SP.get(fr.replace('.png','').lower())
    if not s:return None
    c=s.image;bb=c.getbbox()
    if not bb:return None
    c=c.crop(bb);n=max(1,min(4,96//max(c.size)));c=c.resize((c.size[0]*n,c.size[1]*n),Image.NEAREST)
    fn=f'assets/vs/e/{key.lower()}.png';c.save(OUT+fn,optimize=True);return '/'+fn
out=[];noimg=[]
for k,v in E.items():
    v=v[0] if isinstance(v,list) else v
    if not v.get('bInclude'):continue
    fr=(v.get('frameNames') or [''])[0];im=sprite(fr,k)
    if not im:noimg.append((k,fr))
    out.append({'id':k,'i':im,'n':ko(f'enemiesLang/{{{k}}}bName') or v.get('bName') or k,'en':ko(f'enemiesLang/{{{k}}}bName',0) or v.get('bName',''),
      'd':ko(f'enemiesLang/{{{k}}}bDesc').replace('\\n',' ').strip(),'hp':v.get('maxHp'),'pw':v.get('power'),'sp':v.get('speed'),'xp':v.get('xp'),
      'boss':'BOSS' in k,'hpxlv':'HP_x_Level' in (v.get('skills') or []),'idx':v.get('bIndex',999),
      'res':{x[4:]:v[x] for x in ('res_Freeze','res_Rosary','res_Debuffs','res_Defang') if v.get(x)}})
out.sort(key=lambda x:(x['idx'] if isinstance(x['idx'],(int,float)) else 999))
json.dump(out,open(OUT+'data/vs/base_bestiary.json','w'),ensure_ascii=False,indent=0)
print(len(out),'img',sum(1 for x in out if x['i']),'noimg',noimg[:20]);print([ (x['idx'],x['n']) for x in out][:12])
print('noko',[x['id'] for x in out if x['n']==x['en']][:10])
