# 게임 소스의 requires* 로 "먼저 필요한 해금"을 계산해서 카드에 need 필드로 넣음
import json5,json,collections,sys
SRC='/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/TextAsset/ACHIEVEMENT_DATA.json'
ED='/tmp/edj/achievementData_Emeralds.json'
R='/home/claude/luckeys-lab.github.io/data/vs/'
base=json5.load(open(SRC));ed=json5.load(open(ED))
BU=json.load(open(R+'base_unlocks.json'));EU=json.load(open(R+'ed/unlocks.json'))
edn={u['id']:u['n'] for u in EU['unlocks']}
key=lambda i:('b-'+i) if i in base else ('ed-%d'%edn[i])
def L(x):
    if not x:return []
    return [y if isinstance(y,str) else (y.get('skin') or '') for y in (x if isinstance(x,list) else [x])]
prov=collections.defaultdict(set)
for src in (base,ed):
    for i,v in src.items():
        for f,t in [('characterToUnlock','C'),('stageToUnlock','S'),('relicToUnlock','I'),('weaponToUnlock','I'),('arcanaToUnlock','I'),('powerUpToUnlock','I')]:
            for x in L(v.get(f)):prov[(t,x)].add(i)
def need(i,v):
    g=[]
    for f,t in [('requiresChar','C'),('requiresStage','S'),('requiresItem','I'),('requiresWeapon','I')]:
        for x in L(v.get(f)):
            p=sorted(prov.get((t,x),set())-{i})
            if p:g.append([key(j) for j in p])
    return g
# 이름 붙이기: 제공 줄의 보상에서 해당 종류 글자 찾기
brow={'b-'+u['id']:u for u in BU};erow={'ed-%d'%u['n']:u for u in EU['unlocks']}
def label(k):
    u=brow.get(k) or erow.get(k);rw=u['reward'] if isinstance(u['reward'],list) else [u['reward']]
    return rw
cnt=collections.Counter()
for u in BU:
    u['need']=need(u['id'],base[u['id']]);cnt['b']+=bool(u['need'])
for u in EU['unlocks']:
    u['need']=need(u['id'],ed[u['id']]);cnt['ed']+=bool(u['need'])
json.dump(BU,open(R+'base_unlocks.json','w'),ensure_ascii=False,indent=1)
json.dump(EU,open(R+'ed/unlocks.json','w'),ensure_ascii=False,indent=1)
print(cnt)
for u in BU[6:7]+BU[14:17]+EU['unlocks'][:3]+EU['unlocks'][29:31]:print(u.get('n',u['id']),u['need'],[label(k) for g in u['need'] for k in g])
mx=max(BU,key=lambda u:sum(len(g) for g in u['need']));print('max',mx['id'],mx['need'])
