# 11/27 · DLC 7개 해금 + 비밀 카드 → data/vs/dlc/unlocks.json · secrets.json(그룹 추가) · ach_keys.json(DLC 업적 ID → 체크 키)
# 입력: PC yuhwa\vs_cards.zip 풀어 둔 /tmp/cards/cards · I2Languages.asset (비밀 수수께끼 한국어)
import json,collections,re,sys
C='/tmp/cards/cards/';R='/home/claude/luckeys-lab.github.io/data/vs/'
I2P='/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/Resources/I2Languages.asset'
TAB=[('ms','moonspell','🌙 문스펠'),('fs','foscari','🌊 포스카리'),('em','chalcedony','🚀 긴급회의'),('og','firstblood','🔫 작전 총기'),('cv','thosepeople','🦇 캐슬바니아'),('ac','lemon','🏛️ 안테 챔버'),('bm','bloodmoon','🌕 블러드문')]
SRC=['base','emeralds']+[c for _,c,_ in TAB]
J=lambda p:json.load(open(C+p)) if __import__('os').path.exists(C+p) else {}
# 이름 (ko)
names={}
for s in SRC:
    for k,v in J(s+'/character.json').items():names[('C',k)]=' '.join(x for x in (v.get('ko',{}).get('charName'),v.get('ko',{}).get('surname')) if x) or k
    for f in ('weapon','item'):
        for k,v in J(f'{s}/{f}.json').items():names[('I',k)]=v.get('ko',{}).get('name') or v.get('raw',{}).get('name') or k
    for k,v in J(s+'/stage.json').items():names[('S',k)]=v.get('ko',{}).get('stageName') or k
for k,v in J('base/stage_names.json').items():names[('S',k)]=v['ko'].get('stageName') or k
for k,v in J('base/arcana.json').items():names[('A',str(k))]=v.get('ko',{}).get('name') or str(k)
nm=lambda t,x:names.get((t,x),x)
def reward(v):
    out=[]
    if v.get('characterToUnlock'):out.append('캐릭터 '+nm('C',v['characterToUnlock']))
    if v.get('arcanaToUnlock') is not None:out.append('아르카나 '+nm('A',str(v['arcanaToUnlock'])))
    if v.get('relicToUnlock'):out.append('유물 '+nm('I',v['relicToUnlock']))
    if v.get('weaponToUnlock'):out.append('스킬 '+nm('I',v['weaponToUnlock']))
    for w in v.get('weaponListToUnlock') or []:out.append('스킬 '+nm('I',w))
    if v.get('stageToUnlock'):out.append('스테이지 '+nm('S',v['stageToUnlock']))
    if v.get('hyperToUnlock'):out.append('하이퍼 '+nm('S',v['hyperToUnlock']))
    if v.get('skinsToUnlock'):out.append(f"스킨 {len(v['skinsToUnlock'])}개")
    if v.get('goldPrize'):out.append(f"골드 {v['goldPrize']:,}")
    if v.get('isModifier'):out.append('게임 효과(모드)')
    return out or ['(보상 확인 중)']
def cat(v):
    ts=[u.get('AchievementUnlockType') or '' for u in v.get('UnlockConditions',[])]
    if any('Kill' in t for t in ts):return 'kill'
    if any(t=='SurviveXSeconds' or 'ReachedXLevel' in t for t in ts):return 'survive'
    if any('HaveLeveledWeapon' in t for t in ts):return 'skill'
    if any(t.startswith('Find') or 'Coffin' in t or t=='CollectedWeapons' for t in ts):return 'find'
    return 'special'
def chars(v):
    out=[]
    for u in v.get('UnlockConditions',[]):
        for f in ('RequiredCharacterType','RequiredCharacter'):
            x=u.get(f)
            for y in (x if isinstance(x,list) else [x] if x else []):
                if u.get('AchievementUnlockType')!='HaveOpenedCoffinForXCharacter':out.append(nm('C',y))
    return list(dict.fromkeys(out))
# 키
BU=json.load(open(R+'base_unlocks.json'));EU=json.load(open(R+'ed/unlocks.json'))['unlocks']
edn={u['id']:u['n'] for u in EU}
ACH={'base':J('base/achievement.json'),'emeralds':J('emeralds/achievement.json')}
for t,c,_ in TAB:ACH[c]=J(c+'/achievement.json')
def key(src,i):
    if src=='base':return 'b-'+i
    if src=='emeralds':return 'ed-%d'%edn[i]
    return next(t for t,c,_ in TAB if c==src)+'-'+i
L=lambda x:[] if not x else [y if isinstance(y,str) else (y.get('skin') or '') for y in (x if isinstance(x,list) else [x])]
prov=collections.defaultdict(set)
for src,a in ACH.items():
    for i,v in a.items():
        r=v['raw']
        for f,t in [('characterToUnlock','C'),('stageToUnlock','S'),('relicToUnlock','I'),('weaponToUnlock','I'),('arcanaToUnlock','I'),('powerUpToUnlock','I'),('weaponListToUnlock','I')]:
            for x in L(r.get(f)):prov[(t,x)].add(key(src,i))
def need(src,i,r):
    me=key(src,i);g=[]
    for f,t in [('requiresChar','C'),('requiresStage','S'),('requiresItem','I'),('requiresWeapon','I'),('requiresRelic','I')]:
        for x in L(r.get(f)):
            p=sorted(prov.get((t,x),set())-{me})
            if p:g.append(p)
    return g
out={};ak=json.load(open(R+'ach_keys.json'))
for t,c,name in TAB:
    rows=[]
    for n,(i,v) in enumerate(ACH[c].items(),1):
        r=v['raw'];tx=(v.get('ko') or {}).get('description') or r.get('description') or i
        rows.append({'id':i,'n':n,'k':f'{t}-{i}','text':tx.replace('\\n',' ').strip(),'rw':reward(r),'need':need(c,i,r),'cat':cat(r),'char':chars(r)})
        ak[i]=f'{t}-{i}'
    out[t]={'name':name,'rows':rows}
json.dump(out,open(R+'dlc/unlocks.json','w'),ensure_ascii=False,indent=0)
json.dump(ak,open(R+'ach_keys.json','w'),ensure_ascii=False)
# 비밀
I2={};cur=None;inl=False
for line in open(I2P,encoding='utf-8'):
    if line.startswith('    - Term: '):cur=line[12:].strip();I2[cur]=[];inl=False;continue
    if cur is None:continue
    if line.startswith('      Languages:'):inl=True;continue
    if inl:
        if line.startswith('      - '):
            s=line[8:].rstrip('\n')
            if len(s)>1 and s[0]==s[-1] and s[0] in "'\"":s=s[1:-1].replace("''","'")
            I2[cur].append(s)
        else:inl=False
I2L={k.lower():v for k,v in I2.items()}
def ko(term):
    v=I2.get(term) or I2L.get(term.lower());return (v[11] if v and len(v)>11 and v[11] else None)
SEC=json.load(open(R+'secrets.json'));have={g['key'] for g in SEC}
for t,c,name in TAB:
    if t in have:continue
    rows=[]
    for i,v in J(c+'/secret.json').items():
        r=v['raw'];d=ko(f'secretLang/{{{i}}}description') or (r.get('description') or '').strip()
        kind='riddle' if not r.get('isSpell') else ('mod' if r.get('isModifier') else 'spell')
        rows.append({'id':i,'kind':kind,'d':d.replace('\\n',' ').strip(),'rw':reward(r) if reward(r)!=['(보상 확인 중)'] else [],'spell':r.get('spell') or ''})
    SEC.append({'key':t,'name':name,'rows':rows})
json.dump(SEC,open(R+'secrets.json','w'),ensure_ascii=False,indent=0)
for t in out:print(t,out[t]['name'],len(out[t]['rows']),sum(1 for r in out[t]['rows'] if r['need']),collections.Counter(r['cat'] for r in out[t]['rows']).most_common(3))
for g in SEC:print(g['key'],len(g['rows']),sum(1 for r in g['rows'] if r['kind']=='riddle' and not r['d']),'빈 수수께끼')
print(out['ms']['rows'][0]);print(out['cv']['rows'][2])
