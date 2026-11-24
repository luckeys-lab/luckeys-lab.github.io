exec(open('reco.py').read().split('# 초반 흉내')[0])
S=json.load(open('S_early.json'))
GIVE={}
for i,v in A.items():
    for f in('characterToUnlock','stageToUnlock','relicToUnlock','weaponToUnlock','arcanaToUnlock','powerUpToUnlock','hyperToUnlock'):
        x=v.get(f)
        for y in (x if isinstance(x,list) else [x] if x else []):GIVE.setdefault(y,[]).append(i)
def cost1(i):
    c=dict(CO[i]);k=c['kind']
    if k=='특수':return GUESS.get(i,('',{},3,''))[2] or 3
    if k=='누적':return 3
    return score(i,c,True)
memo={}
def plan(i,seen=()):
    # i를 하려면 필요한 해금 집합(아직 안 한 것) + 비용
    if S.get(i):return (0,frozenset())
    if i in seen:return (99,frozenset())
    tot=cost1(i);need={i}
    for g in NEED[i]:
        if any(S.get(k[2:]) for k in g):continue
        best=min((plan(k[2:],seen+(i,)) for k in g),key=lambda p:p[0])
        tot+=best[0];need|=best[1]
    return (tot,frozenset(need))
def depth(i,need,d={}):
    ds=[depth(k[2:],need) for g in NEED[i] for k in g if k[2:] in need]
    return 1+max(ds,default=0)
def route(target):
    opts=[plan(i) for i in GIVE.get(target,[])]
    if not opts:return print('줄 없음',target)
    tot,need=min(opts,key=lambda p:p[0])
    lv={}
    for i in need:lv.setdefault(depth(i,need),[]).append(i)
    print(f'🎯 {nm(target) if target in I else CHN.get(target,target)} · 해금 {len(need)}개 · {len(lv)}단계')
    for d in sorted(lv):
        for i in lv[d]:
            c=CO[i];ws=[w for w,_ in c.get('weap',[])]+c.get('evo',[])
            tip=''
            for w in ws:
                who=[CHN.get(ch,ch) for ch,st in START.items() if w in st and opened('C',ch,S)]
                tip+=f' 🗡️{nm(w)}: '+(who[0]+'로 시작' if who else '상자 운🎲')
            print(f'  {d}단계 [{cost1(i)}] {TXT[i][:34]}{tip}')
for t in sys.argv[1:]:route(t)
