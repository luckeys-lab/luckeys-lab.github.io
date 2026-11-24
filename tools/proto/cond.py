# 해금 조건 카드 뽑기 (본편) → data/vs/base_cond.json
import json5,json,re,collections
T='/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/'
A=json5.load(open(T+'TextAsset/ACHIEVEMENT_DATA.json'))
C=json5.load(open(T+'TextAsset/CHARACTER_DATA.json'))
# I2: term -> [언어들]  (en=0, ko=11)
I2={};cur=None;inl=False
for line in open(T+'Resources/I2Languages.asset',encoding='utf-8'):
    if line.startswith('    - Term: '):cur=line[12:].strip();I2[cur]=[];inl=False;continue
    if cur is None:continue
    if line.startswith('      Languages:'):inl=True;continue
    if inl:
        if line.startswith('      - '):
            v=line[8:].rstrip('\n')
            if len(v)>1 and v[0]==v[-1] and v[0] in "'\"":v=v[1:-1]
            I2[cur].append(v)
        else:inl=False
def tr(term,lang=11):
    v=I2.get(term);return v[lang] if v and len(v)>lang else None
def L(x):return [] if x is None else (x if isinstance(x,list) else [x])
RUN={'SurviveXSeconds','ReachedXLevel','ReachedXLevelAsCharacter','PlayInStage','HaveLeveledWeaponToSpecificLevelOrEvolved','HaveLeveledWeaponToSpecificLevel','FindWeapons','FindItems','HaveModifiers','KillXNumberOfEnemiesInRun','PlayXCharacter','HaveOpenedCoffinForXCharacter'}
CUM={'KillXNumberOfEnemiesOfTypes','KillXNumberOfEnemies','FindXNumberOfItems','FindXNumberOfAnyItems'}
out={};kinds=collections.Counter()
for i,v in A.items():
    cs=v.get('UnlockConditions') or [];c={'chars':[],'stage':[],'sec':0,'lvl':0,'weap':[],'evo':[],'items':[],'mods':[],'kill':0}
    ts={u.get('AchievementUnlockType') for u in cs}
    for u in cs:
        t=u.get('AchievementUnlockType') or ''
        c['chars']+=L(u.get('RequiredCharacterType'));c['stage']+=L(u.get('RequiredStageType'))
        c['sec']=max(c['sec'],u.get('RequiredSurvivedSeconds') or 0)
        if t in('ReachedXLevel','ReachedXLevelAsCharacter'):c['lvl']=max(c['lvl'],u.get('RequiredLevel') or 0)
        if t.startswith('HaveLeveledWeapon'):c['weap']+=[[w,u.get('RequiredLevel') or 0] for w in L(u.get('RequiredWeapons'))];c['evo']+=L(u.get('RequiredEvolvedWeapons'))
        if t=='FindWeapons':c['items']+=L(u.get('RequiredWeapons'))
        if t=='FindItems':c['items']+=L(u.get('RequiredItems'))
        if t=='HaveModifiers':c['mods']+=L(u.get('RequiredMofiers'))
        if t and t.startswith('Kill'):c['kill']=u.get('RequiredNumEnemiesKilled') or 0
    if v.get('mistery'):kind='비밀'
    elif not cs or ts=={None}:kind='특수'   # 조건 칸이 없음 → 손으로 정함
    elif ts&CUM:kind='누적'
    else:kind='한판'
    kinds[kind]+=1
    c={k:x for k,x in c.items() if x};c['kind']=kind;out[i]=c
start={k:L(v[0].get('startingWeapon') if isinstance(v,list) else v.get('startingWeapon')) for k,v in C.items()}
stn={k[len('stageLang/{'):-len('}stageName')]:v[11] for k,v in I2.items() if k.startswith('stageLang/{') and k.endswith('}stageName') and len(v)>11}
json.dump({'cond':out,'start':start,'stn':stn},open('/home/claude/work/base_cond.json','w'),ensure_ascii=False)
print(kinds);print(out['Survive15MinutesWithGatti'],out['GetHolyBookToLevel4'],out['ReachLV80InverseForest'],out['Defeat100kWithSigma'])
print('stage ko',tr('stageLang/{FOREST}stageName'),tr('stageLang/{FOREST}stageName',0),'| start',list(start.items())[:3])
sp=[i for i,c in out.items() if c['kind']=='특수'];print(len(sp),sp)
