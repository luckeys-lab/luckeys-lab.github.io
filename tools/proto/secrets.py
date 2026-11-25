# 비밀 카드: 본편 SECRET_DATA + DLC secretData → data/vs/secrets.json (칸별)
import json5,json,re
T='/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/'
I2={};cur=None;inl=False
for line in open(T+'Resources/I2Languages.asset',encoding='utf-8'):
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
def ko(term):
    v=I2.get(term) or I2L.get(term.lower());return (v[11] if v and len(v)>11 and v[11] else None)
C='/home/claude/cards/'
names={}
for src in ('base','emeralds'):
    for k,v in json.load(open(C+src+'/character.json')).items():names[('C',k)]=' '.join(x for x in (v['ko'].get('charName'),v['ko'].get('surname')) if x) or k
    for f in ('weapon','item'):
        for k,v in json.load(open(C+src+f'/{f}.json'.replace(src+'/',src+'/'))).items() if False else json.load(open(f'{C}{src}/{f}.json')).items():names[('I',k)]=v['ko'].get('name') or k
for k,v in json.load(open(C+'base/stage_names.json')).items():names[('S',k)]=v['ko'].get('stageName') or k
for k,v in json.load(open(C+'base/arcana.json')).items():names[('A',int(k))]=v.get('ko',{}).get('name') or k
def reward(v):
    out=[]
    if v.get('characterToUnlock'):out.append('캐릭터 '+names.get(('C',v['characterToUnlock']),v['characterToUnlock']))
    if v.get('arcanaToUnlock') is not None:out.append('아르카나 '+str(names.get(('A',v['arcanaToUnlock']),v['arcanaToUnlock'])))
    for f in ('relicToUnlock','weaponToUnlock'):
        if v.get(f):out.append(('유물 ' if f[0]=='r' else '스킬 ')+names.get(('I',v[f]),v[f]))
    for w in v.get('weaponListToUnlock') or []:out.append('스킬 '+names.get(('I',w),w))
    if v.get('stageToUnlock'):out.append('스테이지 '+names.get(('S',v['stageToUnlock']),v['stageToUnlock']))
    if v.get('hyperToUnlock'):out.append('하이퍼 '+names.get(('S',v['hyperToUnlock']),v['hyperToUnlock']))
    if v.get('skinsToUnlock'):out.append(f"스킨 {len(v['skinsToUnlock'])}개")
    if v.get('isModifier'):out.append('게임 효과(모드)')
    return out
def build(data):
    rows=[]
    for k,v in data.items():
        d=ko(f'secretLang/{{{k}}}description') or v.get('description') or ''
        kind='riddle' if not v.get('isSpell') else ('mod' if v.get('isModifier') else 'spell')
        rows.append({'id':k,'kind':kind,'d':d.replace('\\n',' ').strip(),'rw':reward(v),'spell':v.get('spell') or ''})
    return rows
out=[{'key':'base','name':'본편','rows':build(json5.load(open(T+'TextAsset/SECRET_DATA.json')))},
     {'key':'ed','name':'💎 에메랄드 디오라마','rows':build(json5.load(open('/home/claude/src/dlc/emeralds/secretData_Emeralds.json')))}]
json.dump(out,open('/home/claude/luckeys-lab.github.io/data/vs/secrets.json','w'),ensure_ascii=False,indent=0)
for s in out:
    import collections;print(s['name'],len(s['rows']),collections.Counter(r['kind'] for r in s['rows']))
print(out[0]['rows'][0]);print(out[1]['rows'][-3])
