# 디오라마 꼼꼼 추천 데이터 → data/vs/ed/reco.json (화면 계산은 site.js)
import json,re
C=json.load(open('/home/claude/cards/emeralds/character.json'));A=json.load(open('/home/claude/cards/emeralds/achievement.json'))
R='/home/claude/luckeys-lab.github.io/data/vs/'
U=json.load(open(R+'ed/unlocks.json'))['unlocks'];N={x['id']:x['n'] for x in U}
CH=json.load(open(R+'ed/chars.json'));CHN={c['id']:c for c in (CH if isinstance(CH,list) else CH.values())}
I=json.load(open(R+'items.json'))
fam=lambda w:re.sub(r'\d+$','',w or '')
give={'C':{},'S':{},'W':{}}
for k,v in A.items():
    r=v['raw'];n=N[k]
    if r.get('characterToUnlock'):give['C'][r['characterToUnlock']]='ed-%d'%n
    if r.get('weaponToUnlock'):give['W'][fam(r['weaponToUnlock'])]='ed-%d'%n
    for s in r.get('skinsToUnlock') or []:give['S'][s['skin']]='ed-%d'%n
opts=[]
for cid,v in C.items():
    if 'FOLLOWER' in cid or cid not in give['C']:continue   # 비밀로만 여는 캐릭터는 빼기
    r=v['raw'];sk=r.get('skins') or [{'skinType':'DEFAULT'}];names=[s['ko'] for s in CHN.get(cid,{}).get('skins',[])]
    for i,s in enumerate(sk):
        w=s.get('startingWeapon') or r.get('startingWeapon')
        need=[give['C'][cid]]+([give['S'][s['skinType']]] if s.get('skinType') in give['S'] else [])
        if s.get('skinType') not in ('DEFAULT',None) and s['skinType'] not in give['S'] and i>0:continue  # 비밀 스킨 빼기
        wn=I.get('ED_'+w,{}).get('n',w)
        opts.append({'c':cid,'cn':CHN.get(cid,{}).get('ko',cid),'sk':names[i] if i<len(names) else '기본','w':fam(w),'wn':wn,'wi':I.get('ED_'+w,{}).get('i'),'ci':(json.load(open(R+'ed/img.json'))['order'].get(cid) or [None]*9)[i] if i<len((json.load(open(R+'ed/img.json'))['order'].get(cid) or [])) else None,'need':need})
opts.insert(0,{'c':'ANY','cn':'아무 캐릭터','sk':'','w':'','wn':'','wi':None,'ci':None,'need':[]})   # 본편 캐릭터로도 디오라마 가능
rows={}
ZB={'EME_GATEBOSS_SPIRITBEAST':1,'EME_GATEBOSS_DRAGON':2,'EME_GATEBOSS_FINALEMPEROR':3,'EME_GATEBOSS_IRONMAIDEN':4,'EME_GATEBOSS_SPECTER':5,'EME_GATEBOSS_LIVINGANGUISH':6}
for k,v in A.items():
    r=v['raw'];n=N[k];cs=r.get('UnlockConditions') or [];t={c['AchievementUnlockType'] for c in cs}
    inv='HaveModifiers' in t;play=[c.get('RequiredCharacterType') for c in cs if c['AchievementUnlockType']=='PlayXCharacter']
    o={'inv':1 if inv else 0,'ch':play}
    if 'HaveLeveledWeaponToSpecificLevel' in t and any(c.get('RequiredLevel')==6 for c in cs):o.update(k='lv',f=fam(cs[0]['RequiredWeapons'][0]),sc=1)
    elif 'FindWeapons' in t or ('HaveLeveledWeaponToSpecificLevel' in t):o.update(k='evo',f=fam(cs[0]['RequiredWeapons'][0]),sc=2)
    elif 'HaveOpenedCoffinForXCharacter' in t:o.update(k='coffin',sc=1,z=1 if n==2 else 6)
    elif 'FindItems' in t:o.update(k='disk',sc=1)
    elif 'KillBossTypesInRun' in t:
        bs=[b for c in cs for b in c.get('RequiredEnemyTypes') or []]
        if len(bs)>1:o.update(k='allboss',sc=6 if inv else 5)
        else:o.update(k='boss',sc=3 if ZB[bs[0]]>=4 else 2,z=ZB[bs[0]])
    elif 'KillXNumberOfEnemiesOfTypes' in t:o.update(k='ogre',sc=3)
    else:continue   # 조건 칸 없는 것(디바 스킨 2개)은 빼기
    rows['ed-%d'%n]=o
json.dump({'opts':opts,'rows':rows,'wun':give['W'],'inv':'b-ObtainGraciasMirror'},open(R+'ed/reco.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(opts),'options',len(rows),'rows');print(opts[1]);print({k:v for k,v in list(rows.items())[:4]})
