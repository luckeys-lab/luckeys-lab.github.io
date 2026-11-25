# 디오라마 보스 카드 (우화집 문구 + 능력치) → data/vs/ed/bosses.json
import json5,json
T='/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/Resources/I2Languages.asset'
I2={};cur=None;inl=False
for line in open(T,encoding='utf-8'):
    if line.startswith('    - Term: '):cur=line[12:].strip();I2[cur]=[];inl=False;continue
    if cur is None:continue
    if line.startswith('      Languages:'):inl=True;continue
    if inl:
        if line.startswith('      - '):
            v=line[8:].rstrip('\n')
            if len(v)>1 and v[0]==v[-1] and v[0] in "'\"":v=v[1:-1].replace("''","'")
            I2[cur].append(v)
        else:inl=False
E=json5.load(open('/tmp/edj/enemyData_Emeralds.json'))
M=json.load(open('/home/claude/luckeys-lab.github.io/data/vs/ed/map.json'))
out={}
for b in sorted({p['id'] for p in M['pins'] if p['kind']=='boss'}|{'EME_BOSS_OGRE'}):
    v=E[b];v=v[0] if isinstance(v,list) else v
    g=lambda f,l:(I2.get(f'enemiesLang/{{{b}}}{f}') or ['']*12)[l]
    out[b]={'ko':g('bName',11),'en':g('bName',0),'d':g('bDesc',11),'d_en':g('bDesc',0),'hp':v.get('maxHp'),'power':v.get('power'),'speed':v.get('speed'),'hpxlv':'HP_x_Level' in (v.get('skills') or [])}
json.dump(out,open('/home/claude/luckeys-lab.github.io/data/vs/ed/bosses.json','w'),ensure_ascii=False,indent=1)
for k,v in out.items():print(k,v['ko'],'|',v['d'][:50],'|',v['hp'],v['power'],v['speed'],v['hpxlv'])
