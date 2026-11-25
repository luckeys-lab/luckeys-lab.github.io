# 본편 해금: 플레이 패턴 카테고리(cat) · 스킬 묶음(grp) · 추천 순서(ord) → data/vs/base_unlocks.json
import json,re
R='/home/claude/luckeys-lab.github.io/data/vs/'
B=json.load(open(R+'base_unlocks.json'));C=json.load(open(R+'base_cond.json'))['cond'];I=json.load(open(R+'items.json'))
nm2k={v['n']:k for k,v in I.items() if v.get('t')=='스킬'}
def base_of(w):   # 진화 스킬 → 첫 재료 스킬
    it=I.get(w,{})
    if it.get('t')=='스킬':return w
    for f in it.get('f') or []:
        a=f.split(' + ')[0].strip()
        if a in nm2k:return nm2k[a]
    return w
def cat(u,c):
    k=c['kind']
    if k=='비밀':return 'secret'
    ws=[w for w,_ in c.get('weap',[])]+c.get('evo',[])+[x for x in c.get('items',[]) if I.get(x,{}).get('t') in ('스킬','진화 스킬')]
    if ws:return 'skill'
    if c.get('kill'):return 'kill'
    if c.get('items') or 'Coffin' in u['id']:return 'find'
    if c.get('sec') or c.get('lvl'):return 'survive'
    return 'special'
def score(c):
    s=0;sec=c.get('sec',0);s+=0 if sec<=60 else 1 if sec<=600 else 2 if sec<=900 else 3 if sec<=1200 else 4
    l=c.get('lvl',0);s+=0 if not l else 1 if l<=40 else 2 if l<=60 else 3 if l<=80 else 4
    s+=2*len(c.get('mods',[]))+len(c.get('weap',[]))+len(c.get('items',[]))+(3 if c.get('kill',0)>=5000 else 1 if c.get('kill') else 0)
    if c['kind']=='특수':s+=3
    if c['kind']=='비밀':s+=6
    return s
import json5
RAW=json5.load(open('/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/TextAsset/ACHIEVEMENT_DATA.json'))
def rawc(i):return RAW[i].get('UnlockConditions') or []
_cat0=cat
def cat(u,c):
    t={x.get('AchievementUnlockType') for x in rawc(u['id'])}
    if c['kind']!='비밀' and ('FindXNumberOfItems' in t or 'FindXNumberOfAnyItems' in t):return 'find'
    return _cat0(u,c)
_score0=score
def score2(u,c):
    s=_score0(c)
    for x in rawc(u['id']):
        n=x.get('RequiredNumberOfItems')
        if n:s+=min(8,n//15 if x.get('AchievementUnlockType')=='FindXNumberOfAnyItems' else 1+n//50)
    return s
need={'b-'+u['id']:u.get('need',[]) for u in B}
memo={}
def depth(k,seen=()):
    if k in memo:return memo[k]
    if k in seen or k not in need:return 0
    d=0
    for g in need[k]:
        d=max(d,1+min(depth(x,seen+(k,)) for x in g))
    memo[k]=d;return d
for i,u in enumerate(B,1):
    c=C[u['id']];u['cat']=cat(u,c);u['gi']=i
    ws=[w for w,_ in c.get('weap',[])]+c.get('evo',[])+[x for x in c.get('items',[]) if I.get(x,{}).get('t') in ('스킬','진화 스킬')]
    if u['cat']=='skill' and ws:
        g=base_of(ws[0]);u['grp']=g;u['grpn']=I.get(g,{}).get('n',g)
        u['step']=0 if c.get('weap') and not any(I.get(x,{}).get('t')=='진화 스킬' for x in c.get('items',[])) else 1
    else:u.pop('grp',None);u.pop('grpn',None);u.pop('step',None)
    u['ord']=depth('b-'+u['id'])*100+score2(u,c)*10
# 스킬 묶음은 붙어 있게: 묶음 안 가장 이른 순서로 맞추고 레벨 → 진화
gmin={}
for u in B:
    if u.get('grp'):gmin[u['grp']]=min(gmin.get(u['grp'],9e9),u['ord'])
for u in B:
    if u.get('grp'):u['ord']=gmin[u['grp']]+u['step']+0.001*u['gi']
json.dump(B,open(R+'base_unlocks.json','w'),ensure_ascii=False,indent=1)
import collections;print(collections.Counter(u['cat'] for u in B));print(len(gmin),'skill groups')
for u in sorted(B,key=lambda u:u['ord'])[:12]:print(u['gi'],u['cat'],u.get('grpn',''),u['text_fix'][:30],round(u['ord'],1))
