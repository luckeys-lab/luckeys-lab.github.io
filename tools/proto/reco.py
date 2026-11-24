import json,itertools,sys
sys.path.insert(0,'/home/claude/work')
R='/home/claude/luckeys-lab.github.io/data/vs/'
D=json.load(open('/home/claude/work/base_cond.json'));CO=D['cond'];START=D['start'];STN=D['stn']
B=json.load(open(R+'base_unlocks.json'));I=json.load(open(R+'items.json'))
import json5
A=json5.load(open('/mnt/user-data/uploads/vs_unit/ExportedProject/Assets/TextAsset/ACHIEVEMENT_DATA.json'))
exec(open('/home/claude/work/i2.py').read()) if False else None
# 특수 38개: 유화 추정 (제이 확인용)
GUESS={'Survive20MinutesWithCurse':('한판',{'sec':1200},3,''),'Have6Evolutions':('한판',{},4,'🎲'),'Have6DifferentWeapons':('한판',{},1,''),
 'Recover1000HP':('누적',{},0,''),'Earn5000CoinsInASingleRun':('한판',{},2,''),'Destroy20Candles':('한판',{},1,''),'EvolvePenshin':('한판',{},2,''),
 'DefeatManyBats':('누적',{},0,''),'DefeatShootingEnemies':('누적',{},0,''),'DefeatBatDragons':('누적',{},0,''),'Banish10Items':('누적',{},0,''),'Banish20Items':('누적',{},0,''),'Banish40Items':('누적',{},0,''),'Banish80Items':('누적',{},0,'')}
def provmap():
    P={}
    for i,v in A.items():
        for f,t in [('characterToUnlock','C'),('stageToUnlock','S')]:
            x=v.get(f)
            for y in (x if isinstance(x,list) else [x] if x else []):P.setdefault((t,y),set()).add(i)
    return P
P=provmap()
def opened(t,x,S):p=P.get((t,x));return (not p) or any(S.get(j) for j in p)
NEED={u['id']:u.get('need',[]) for u in B}
def visible(i,S):return all(any(S.get(k[2:]) for k in g) for g in NEED[i])
def score(i,c,early):
    s=0;sec=c.get('sec',0);s+=0 if sec<=60 else 1 if sec<=600 else 2 if sec<=900 else 3 if sec<=1200 else 4
    if early and sec>=1800:s+=2
    l=c.get('lvl',0);s+=0 if not l else 1 if l<=40 else 2 if l<=60 else 3 if l<=80 else 4
    s+=2*len(c.get('mods',[]))+len(c.get('weap',[]))+2*len(c.get('evo',[]))+len(c.get('items',[]))+(4 if c.get('kill',0)>=50000 else 0)
    return max(s,1)
def rows(S):
    early=sum(1 for v in S.values() if v)<60;out=[]
    for u in B:
        i=u['id'];c=dict(CO[i]);k=c['kind'];luck=''
        if S.get(i) or not visible(i,S) or k in('비밀','누적'):continue
        if k=='특수':
            if i not in GUESS or GUESS[i][0]!='한판':continue
            c.update(GUESS[i][1]);sc=GUESS[i][2];luck=GUESS[i][3]
        else:sc=score(i,c,early)
        if len(c.get('evo',[]))+len(c.get('weap',[]))>=2:luck='🎲'
        out.append((i,c,sc,luck))
    return out
CHN={k[3:]:v['n'] for k,v in I.items() if k.startswith('CH_')}
def nm(x):return I.get(x,{}).get('n',x)
TIER={'쉬움':(2,3,False),'보통':(4,8,True),'지옥':(6,99,True)}
def reco(S,tier):
    mx,cap,luckok=TIER[tier];R=rows(S)
    chars=[c for c in START if opened('C',c,S)];stages=sorted({s for _,c,_,_ in R for s in c.get('stage',[])} )
    stages=[s for s in stages if opened('S',s,S)]+[None]
    res=[]
    for st in stages:
        for ch in chars+[None]:
            cand=[]
            for i,c,sc,lk in R:
                if c.get('chars') and ch not in c['chars']:continue
                if c.get('stage') and st not in c['stage']:continue
                if lk and not luckok:continue
                ws=[w for w,_ in c.get('weap',[])]+c.get('evo',[])
                own=ch and set(ws)&set(START.get(ch,[]))
                cand.append((0 if (c.get('chars') or c.get('stage')) else 1,sc-(1 if own else 0),i,sc,lk,ws))
            cand.sort();pick=[];tot=0;W=set(START.get(ch,[]) if ch else [])
            for spec,s2,i,sc,lk,ws in cand:
                if len(pick)>=mx or tot+s2>cap:continue
                if len(W|set(ws))>6:continue
                pick.append((i,lk));tot+=s2;W|=set(ws)
            nspec=sum(1 for i,_ in pick if CO[i].get('chars') or CO[i].get('stage'))
            if pick and (ch or not any(CO[i].get('chars') for i,_ in pick)):res.append((len(pick),nspec,-tot,ch,st,pick,tot))
    res.sort(key=lambda r:(-r[0],-r[1],-r[2]));seen=set();top=[]
    for r in res:
        key=r[4]
        if key in seen:continue
        seen.add(key);top.append(r)
        if len(top)==3:break
    return top
TXT={u['id']:u['text_fix'] for u in B}
def show(S,label):
    print('==',label,'체크',sum(1 for v in S.values() if v))
    for t in TIER:
        for n,_,_,ch,st,pick,tot in reco(S,t):
            print(f' [{t}] {CHN.get(ch,"아무 캐릭") if ch else "아무 캐릭"} · {STN.get(st,st) if st else "아무 맵"} → {n}개 (점수{tot}) :',' / '.join(TXT[i][:22]+lk for i,lk in pick))
# 초반 흉내: 쉬운 줄을 몇 번 체크
S={}
for _ in range(3):
    for i,c,sc,lk in rows(S):
        if sc<=1 and not c.get('chars') and not c.get('stage'):S[i]=1
show(S,'초반')
json.dump(S,open('/home/claude/work/S_early.json','w'))
