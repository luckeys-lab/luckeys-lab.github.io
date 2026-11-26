#!/usr/bin/env python3
"""카드(JSON) → _src 페이지 만들기. 그다음 build.py가 틀을 끼워 완성.
   python3 tools/gen.py && python3 tools/build.py"""
import json,pathlib,html,re
R=pathlib.Path(__file__).resolve().parent.parent
D=R/'data/vs'
items=json.loads((D/'items.json').read_text(encoding='utf-8'))
# 디오라마 그림 (tools/proto/edimg.py → data/vs/ed/img.json)
IMG=json.loads((D/'ed/img.json').read_text(encoding='utf-8'))
for _k,_p in IMG['icons'].items():
    if 'ED_'+_k in items:items['ED_'+_k]['i']=_p
_byname={v['n']:v.get('i') for k,v in items.items() if k.startswith('ED_')}
for _k,_seq in IMG['order'].items():
    c=items.get('CH_'+_k)
    if not c:continue
    _f=next((x for x in _seq if x),None)
    if _f:c['i']=_f
    if c.get('s') and _byname.get(c['s']):c['si']=_byname[c['s']]
esc=html.escape
name2id={}
for k,v in items.items(): name2id.setdefault(v['n'],k)

def pop(name):
    """이름에 미리보기 걸기 (카드에 있으면)"""
    k=name2id.get(name)
    if not k: return esc(name)
    ic=items[k].get('i')
    img=f'<img class="ic" src="{ic}" alt="" loading="lazy">' if ic else ''
    return f'<span class="pop" data-pop="{k}">{img}{esc(name)}</span>'

# ── 🗂 콘텐츠 틀 (11/26 제이): 위 = 콘텐츠 아이콘 + 이름 · 왼쪽 = DLC 세로 탭 (모바일은 가로 줄) · 탭 주소 #base #ed … ──
TABS=[('base','🧛','본편','#E8B23C'),('extra','➕','추가','#E8B23C'),('ms','🌙','문스펠','#78C8FF'),('fs','🌊','포스카리','#28B4AA'),('em','🚀','긴급회의','#F06EAA'),('og','🔫','작전 총기','#F58C28'),('cv','🦇','캐슬바니아','#A064DC'),('ed','💎','디오라마','#46BE5A'),('ac','🏛️','안테 챔버','#9696A0'),('bm','🌕','블러드문','#C8283C')]
def cpage(icon,name,tabs,top='',wrap=''):
    side=[];body=[]
    for k,ic,lb,col in TABS:
        h=tabs.get(k)
        if h is None:
            side.append(f'<span class="cpt-b off" title="준비 중"><i>{ic}</i><b>{lb}</b><small>준비 중</small></span>');continue
        side.append(f'<a class="cpt-b" href="#{k}" data-tab="{k}" style="--tc:{col}"><i>{ic}</i><b>{lb}</b><small class="cn"></small></a>')
        body.append(f'<div class="sec cpt" id="t-{k}" data-tab="{k}" data-lb="{ic} {lb}" style="--tc:{col}">\n{h}\n</div>')
    return f'''<div class="cp"><div class="cphead"><span class="cpi">{icon}</span><h1>{name}</h1><span class="cpn"></span><span class="cpc"></span></div>
{top}
<div class="cpw"><nav class="cpside" aria-label="DLC">{''.join(side)}</nav><div class="cpbody"{(' '+wrap) if wrap else ''}>{''.join(body)}</div></div></div>'''
def redir(path,target,dh):
    """옛 주소 → 새 주소 (검색·링크 보존 · ?inv · #해시 그대로)"""
    f=R/'_src'/path
    if f.exists():f.unlink()
    o=R/path;o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>이동 중 · LucKey's Lab</title><link rel="canonical" href="https://luckeys-lab.github.io{target}">
<meta name="robots" content="noindex"><script>location.replace('{target}'+location.search+(location.hash||'{dh}'))</script><meta http-equiv="refresh" content="0;url={target}{dh}"></head><body><a href="{target}{dh}">새 페이지로 이동</a></body></html>''',encoding='utf-8')

def link_names(text):
    out=esc(text)
    for n in sorted(name2id,key=len,reverse=True):
        if len(n)>=2 and n in text:
            out=out.replace(esc(n),pop(n),1)
    return out

# ---------- 디오라마 해금 ----------
U=json.loads((D/'ed/unlocks.json').read_text(encoding='utf-8'))

# 먼저 필요한 해금 (게임처럼 숨기기) · need = [[OR 키들], ...] (AND)
def _needinfo():
    m={}
    for i,u in enumerate(json.load(open(R/'data/vs/base_unlocks.json')),1):m['b-'+u['id']]=(i,u['reward'] if isinstance(u['reward'],list) else [u['reward']])
    for u in json.load(open(R/'data/vs/ed/unlocks.json'))['unlocks']:m['ed-%d'%u['n']]=(('💎%d'%u['n']),[u['reward']])
    return m
NEEDI=_needinfo()
def need_attr(u):
    return ' data-need="'+';'.join('|'.join(g) for g in u.get('need',[]))+'"' if u.get('need') else ''
def need_note(u,here):
    if not u.get('need'):return ''
    def one(k):
        n,rw=NEEDI[k];pre='/vs/unlocks.html'
        href=('#' if pre==here else pre+'#')+k
        return f'<a href="{href}">#{n}</a> {esc(" · ".join(rw))}'
    return '<p class="need">🔒 먼저: '+' 그리고 '.join(' 또는 '.join(one(k) for k in g) for g in u['need'])+'</p>'


# 이름 강조: 보스(빨강) · 캐릭터(파랑) · 관(금색)
BOSSN=['스피릿 비스트','어스 드래곤','최종 황제의 악마 형태','최종 황제','아이언 메이든','이와나가히메의 유령','살아있는 고뇌','숨은 오우거','모든 보스']
CHARN=sorted(['츠나노리 미도','보니 블레어','포미나 프랭클린','디바 5번','아메야 아이슬링','시그나스','츠나노리','보니','포미나','아메야','디바'],key=len,reverse=True)
_hlre=re.compile('('+'|'.join(map(re.escape,BOSSN+CHARN))+r'|(?<=번째 )관)')
HLPOP={'스피릿 비스트':'EB_EME_GATEBOSS_SPIRITBEAST','어스 드래곤':'EB_EME_GATEBOSS_DRAGON','최종 황제의 악마 형태':'EB_EME_GATEBOSS_FINALEMPEROR','최종 황제':'EB_EME_GATEBOSS_FINALEMPEROR','아이언 메이든':'EB_EME_GATEBOSS_IRONMAIDEN','이와나가히메의 유령':'EB_EME_GATEBOSS_SPECTER','살아있는 고뇌':'EB_EME_GATEBOSS_LIVINGANGUISH','숨은 오우거':'EB_EME_BOSS_OGRE'}
for _k,_v in items.items():
    if _k.startswith('CH_EME_'):HLPOP[_v['n']]=_k
for _s,_f in {'츠나노리':'츠나노리 미도','보니':'보니 블레어','포미나':'포미나 프랭클린','아메야':'아메야 아이슬링','디바':'디바 5번'}.items():
    if _f in HLPOP:HLPOP[_s]=HLPOP[_f]
def hl(t):
    def f(m):
        w=m.group(0);c='hb' if w in BOSSN else 'hf' if w=='관' else 'hc'
        k=HLPOP.get(w)
        return f'<b class="{c} pop" data-pop="{k}">{w}</b>' if k else f'<b class="{c}">{w}</b>'
    return _hlre.sub(f,t)


# 💡 디오라마 해금 자동 공략 (데이터로): 시작 스킬 캐릭/스킨 · 진화 단계 · 위치 · 보스
RC=json.loads((D/'ed/reco.json').read_text(encoding='utf-8'))
_MP=json.loads((D/'ed/map.json').read_text(encoding='utf-8'));_BS=json.loads((D/'ed/bosses.json').read_text(encoding='utf-8'))
_ZN={int(k):v for k,v in _MP['zones'].items()}
_EW={k[3:]:v for k,v in items.items() if k.startswith('ED_')}
def _side(n):return '포탈 도착 화면' if n==0 else (f'오른쪽으로 {n}칸' if n>0 else f'왼쪽으로 {-n}칸')
def _arr(n):return f'{"→" if n>0 else "←"}{abs(n)}'
def dual(a,b):return a if a==b else f'<span class="nv">{a}</span><span class="iv">{b}</span>'   # 지도 🔄 토글: 일반/인버스 글자 (인버스 = 180° 회전, 11/26 제이 스샷)
INVM=lambda u:str(u.get('map','')).startswith('인버스')
def guide(u):
    r=RC['rows'].get('ed-%d'%u['n']);out=[];iv=INVM(u)
    if not r:return ''
    if iv:out.append('🔄 <b class="hinv">인버스(반전) 모드에서만</b> 해금돼요 · 일반 모드에서는 잡아도 안 쳐줘요 · 맵이 180° 돌아가 있어요')
    if r.get('f'):
        f=r['f'];who=[f"{o['cn']}{'' if o['sk'] in ('기본','') else ' ['+o['sk'].strip('()')+']'}" for o in RC['opts'] if o['w']==f]
        nm=_EW.get(f+'1',{}).get('n') or _EW.get(f,{}).get('n') or f
        if who:out.append(f"🗡️ 시작 스킬 <b>{esc(nm)}</b>로 시작하는 캐릭터: "+' · '.join(esc(x) for x in dict.fromkeys(who)))
        else:
            un=RC['wun'].get(f);out.append(f"🎲 {esc(nm)} 시작 캐릭터 없음 · 레벨업에서 골라야 합니다"+(f" (먼저 <a href=\"#{un}\">💎{un[3:]}</a>에서 스킬 해금)" if un else ''))
        if r['k']=='evo':
            line=[k for k in _EW if re.sub(r'\d+$','',k)==f and re.search(r'\d+$',k)];line.sort()
            if not line and f in _EW:line=[f,f+'2']
            steps=' → '.join(esc(_EW[k]['n']) for k in line if k in _EW)
            if steps:out.append('✨ 진화 단계: '+steps)
            for k in line[1:]:
                tp=(_EW.get(k,{}).get('p') or '').strip()
                if tp and tp not in ('-','.'):out.append(f"✨ {esc(_EW[k]['n'])}: {esc(tp)}")
    if r['k']=='coffin':
        pc=[x for x in _MP['pins'] if x['kind']=='coffin' and x['zone']==r['z']]
        if pc:out.append(f"📍 <a href=\"/vs/map.html#z{r['z']}\">{esc(_ZN[r['z']])}</a> · {_side(pc[0]['xm'])}"+(' (시작 화면 기준)' if r['z']==1 else ''))
    if r['k']=='boss':
        pb=[x for x in _MP['pins'] if x['kind']=='boss' and x['zone']==r['z']]
        b=_BS.get(pb[0]['id'],{}) if pb else {}
        out.append(f"📍 <a href=\"/vs/map.html#z{r['z']}\">{esc(_ZN[r['z']])}</a> 보스 · {(_side(-pb[0]['xm']) if iv else _side(pb[0]['xm'])) if pb else ''} · ❤️ {b.get('hp')}{'×레벨' if b.get('hpxlv') else ''}")
    if r['k']=='allboss':out.append('📍 <a href="/vs/map.html#z7">정션</a>에서 6구역 보스를 한 판에 전부 · 디바 5번 필수')
    if r['k']=='ogre':out.append('⏱ <b>21~25분쯤</b> 나오는 숨은 보스 (시간 확인 중) · 화면 가장자리 💀 표시를 따라가기 · 일반 <b>6시</b>(정션 아래쪽) · 인버스 <b>12시</b>')
    if r['k']=='disk':out.append('🛒 에메랄드 디스크를 찾아 구매')
    mm=''
    if r['k'] in ('coffin','boss'):
        z=r['z'];hit=[x for x in _MP['pins'] if x['zone']==z and x['kind']==r['k']][:1]
        def _mp(x,cls):
            ic={'coffin':'⚰️','boss':'👹','portal':'🌀','item':'💍'}[x['kind']];xm=(f'<b>{_arr(-x["xm"] if iv else x["xm"])}</b>' if x['xm'] else '')
            px,py=x["x"]/256*100,x["y"]/280*100
            if iv:px,py=100-px,100-py
            return f'<span class="mp {cls}" style="left:{px:.1f}%;top:{py:.1f}%">{ic}{xm if cls=="hit" else ""}</span>'
        others=''.join(_mp(x,'dim') for x in _MP['pins'] if x['zone']==z and x not in hit)
        mm=f'<a class="mmap{" inv" if iv else ""}" href="/vs/map.html{"?inv=1" if iv else ""}#z{z}" title="크게 보기"><img src="/assets/vs/ed/map/z{z}.png" alt="{esc(_ZN[z])} 지도" loading="lazy">{others}{"".join(_mp(x,"hit") for x in hit)}<i>🔍 {esc(_ZN[z])} 지도{" · 🔄 인버스" if iv else ""}</i></a>'
    return ''.join(f'<p class="guide">{x}</p>' for x in out)+mm

FIXT={'시우그나스':'시그나스','디바 5호':'디바 5번'}
CH=U['chars']
FULL={'츠나노리':'츠나노리 미도','보니':'보니 블레어','포미나':'포미나 프랭클린','디바 5번':'디바 5번','아메야':'아메야 아이슬링','시그나스':'시그나스'}
ZONE={1:'1 미야코시',2:'2 마녀 왕국 풀크라',3:'3 그렐론',4:'4 아발론',5:'5 요미',6:'6 프로비던스','hub':'숨은 구역 (오우거)','전부':'모든 구역'}
ICON={'성장·진화':'📈','성장':'📈','진화':'✨','찾아서진화':'🔍','사냥':'⚔️','발견':'⚰️','특수':'🎯','기타':'📦'}
cnt={}
for u in U['unlocks']: cnt[u['type']]=cnt.get(u['type'],0)+1
# 플레이 패턴 카테고리 (11/26 제이: 한 판에 같이 하는 것끼리) · 본편 cat = tools/proto/basecat.py
CATL={'skill':'스킬','survive':'버티기','find':'찾기','kill':'잡기','special':'특수','secret':'비밀'}
CATI={'스킬':'🗡️','버티기':'⏱','찾기':'⚰️','잡기':'👹','특수':'🎯','비밀':'🔒'}
EDMAP={'성장':'스킬','진화':'스킬','찾아서진화':'스킬','사냥':'잡기','발견':'찾기'}
def ty(t): return EDMAP.get(t,'특수')
rows=[]
for u in U['unlocks']:
    t=ty(u['type']);scope='전용' if u['char'] else '공통'
    raw=u['text'];fixed=raw
    for a,b in FIXT.items(): fixed=fixed.replace(a,b)
    chars=u['char'].split('|') if u['char'] else []
    cbadge=' · '.join(f"{pop(FULL.get(c,c)) if FULL.get(c,c) in name2id else esc(c)} 🗡️{pop(CH.get(c,'?'))}" for c in chars)
    badge=f'<span class="bd bd-own">전용 · {cbadge}</span>' if chars else '<span class="bd">공통</span>'
    mp=u.get('map','');mp=mp.replace('둘다','일반·인버스').replace('❓','')
    z=u.get('zone');zt=ZONE.get(z,'') if z not in (None,'❓') else ''
    loc=' · '.join(x for x in [mp,zt] if x)
    q=f'<div class="fix">게임 원문: {esc(raw)}</div>' if fixed!=raw else ''
    title=fixed
    rows.append(f'''<details class="ul" data-id="ed-{u['n']}" data-type="{t}" data-scope="{scope}"{need_attr(u)}>
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">💎{u['n']}</span><span class="tt">{'<span class="binv">🔄 인버스</span> ' if INVM(u) else ''}{hl(esc(title))}</span><span class="k">{CATI.get(t,'')} {t}</span></summary>
<div class="bdy"><p class="rw">🎁 보상 → {link_names(u['reward'])}</p>{q}<p>{badge}{(' · 📍 '+esc(loc)) if loc else ''}</p>{guide(u)}{need_note(u,'/vs/unlocks.html')}</div></details>''')
types=sorted({ty(u['type']) for u in U['unlocks']},key=lambda t:(t=='기타',-sum(1 for u in U['unlocks'] if ty(u['type'])==t)))
fb=''.join(f'<button type="button" data-f="{t}">{ICON.get(t,"")} {t} {sum(1 for u in U["unlocks"] if ty(u["type"])==t)}</button>' for t in types)
(R/'_src/vs/ed').mkdir(parents=True,exist_ok=True)
(R/'_src/vs/ed/index.html').write_text(f'''title: 에메랄드 디오라마
desc: 뱀파이어 서바이벌 무료 DLC 에메랄드 디오라마 공략 · 해금 {len(U['unlocks'])}개 · 지도 · 캐릭터 · 비밀.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 에메랄드 디오라마</div>
<h1>💎 에메랄드 디오라마</h1>
<p class="sub">무료 DLC · 해금 {len(U['unlocks'])}개 · 게임 데이터 기준</p>
<div class="tiles">
<a class="tile" href="/vs/unlocks.html#sec-ed"><b>🔓 해금</b><span>{len(U['unlocks'])}개 · 다음 판 추천</span></a>
<a class="tile" href="/vs/map.html#ed"><b>🗺️ 지도</b><span>관 · 보스 · 패시브 위치</span></a>
<a class="tile" href="/vs/chars.html#ed"><b>🧛 캐릭터</b><span>스킨별 시작 스킬</span></a>
<a class="tile" href="/vs/secrets.html#sec-ed"><b>🤫 비밀</b><span>수수께끼 · 주문</span></a>
<a class="tile" href="/vs/collection.html#ed"><b>📦 컬렉션</b><span>스킬 진화 단계별</span></a>
<a class="tile" href="/vs/bestiary.html#ed"><b>📖 우화집</b><span>몹 그림 · 능력치 · 이야기</span></a>
<a class="tile" href="/vs/evo.html#ed"><b>✨ 진화</b><span>진화 단계 · 요구 사항</span></a>
</div>
<script>if(/^#ed-/.test(location.hash))location.replace('/vs/unlocks.html'+location.hash)</script>
''',encoding='utf-8')

print('gen ok',len(rows))

# ---------- 디오라마 캐릭터 페이지 ----------
EC=json.loads((D/'ed/chars.json').read_text(encoding='utf-8'))
SHORT={v:k for k,v in FULL.items()}
MULT={'moveSpeed':'이동 속도','power':'피해량','area':'공격 범위','speed':'투사체 속도','duration':'지속시간','luck':'행운','growth':'성장','greed':'탐욕','curse':'저주','magnet':'자석','cooldown':'쿨타임'}
FLAT={'maxHp':'최대 체력','armor':'방어력','regen':'회복','amount':'투사체 수','revivals':'부활','rerolls':'새로고침','skips':'건너뛰기','banish':'지우기'}
def slug(i): return i.replace('EME_','').lower()
def stat_rows(st):
    out=[]
    for k,lab in list(FLAT.items())+list(MULT.items()):
        if k not in st: continue
        v=st[k]
        if k in MULT:
            if v==1: continue
            p=round((v-1)*100);txt=f"{p:+d}%";w=max(6,min(100,50+p))
        else:
            txt=str(v) if k=='maxHp' else f"+{v}";w=max(6,min(100,(v/2 if k=='maxHp' else v*12)))
        out.append(f'<div class="stat"><span>{lab}</span><div class="pb"><i style="width:{w}%"></i></div><em>{txt}</em></div>')
    return ''.join(out)
(R/'_src/vs/ed/c').mkdir(parents=True,exist_ok=True)
tiles=[]
for c in EC:
    sl=slug(c['id']);short=SHORT.get(c['ko'],c['ko'])
    need=[u for u in U['unlocks'] if u['char'] and short in u['char'].split('|')]
    how=[u for u in U['unlocks'] if c['ko'] in u['reward']]
    rws=[r for r in rows if any(f'data-id="ed-{u["n"]}"' in r for u in need)]
    seq=IMG['order'].get(c['id'],[])
    def _sim(i):
        p=seq[i] if i<len(seq) else None
        return f'<img class="sp" src="{p}" alt="" loading="lazy">' if p else ''
    def _sic(n):
        p=_byname.get(n);return f'<img class="ic" src="{p}" alt="">' if p else '🗡️ '
    sk=''.join(f'<div class="skin">{_sim(i)}<b>{esc(s["ko"])}</b><span>{_sic(s.get("start"))}{pop(s["start"]) if s.get("start") else "-"}</span></div>' for i,s in enumerate(c['skins']))
    hero=next((x for x in seq if x),None)
    howt=''.join(f'<li><a href="/vs/unlocks.html#ed-{u["n"]}">💎{u["n"]}번</a> · {esc(u["text"])}</li>' for u in how) or '<li>처음부터 또는 확인 중</li>'
    tiles.append(f'<a class="tile ctile" data-ch="{c['id']}" href="/vs/ed/c/{sl}.html">{f'<img class="sp" src="{hero}" alt="" loading="lazy">' if hero else ''}<b>{esc(c["ko"])}</b><span>{_sic(c.get("start"))}{esc(c["start"] or "-")}</span></a>')
    (R/f'_src/vs/ed/c/{sl}.html').write_text(f'''title: {c["ko"]} · 에메랄드 디오라마
desc: 뱀파이어 서바이벌 에메랄드 디오라마 캐릭터 {c["ko"]} · 시작 스킬 {c["start"]} · 스킨별 시작 스킬 · 해금 방법 · 이 캐릭터가 필요한 해금
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › <a href="/vs/ed/">에메랄드 디오라마</a> › <a href="/vs/chars.html">캐릭터</a></div>
<div class="chead">{f'<img class="sp big" src="{hero}" alt="{esc(c["ko"])}">' if hero else ''}<div><h1>{esc(c["ko"])}</h1>
<p class="sub">{_sic(c.get("start"))}시작 스킬 {pop(c["start"]) if c.get("start") else "-"}</p></div></div>
<div class="quote">{link_names(c["desc"] or "")}</div>
<h2>능력치</h2>{stat_rows(c.get("stats",{}))}
<h2>스킨 {len(c["skins"])}</h2><div class="skins">{sk}</div>
<p class="note">스킨마다 시작 스킬이 다릅니다. 스킨 이름 일부는 게임 번역 파일에 한글이 없어 영어로 적었습니다.</p>
<h2>해금 방법</h2><ul class="how">{howt}</ul>
<h2>{esc(c["ko"])}가 필요한 해금 {len(need)}</h2>
{('<div class="prog"><div class="pb"><i id="pbar"></i></div><span id="ptxt"></span></div><div id="ulist" data-group="ed">'+chr(10).join(rws)+'</div>') if rws else '<p class="note">이 캐릭터 전용 해금은 없습니다.</p>'}
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
    k='CH_'+c['id']
    if k in items: items[k]['l']=f'/vs/ed/c/{sl}.html'
(R/'_src/vs/chars.html').write_text(f'''title: 캐릭터 (본편 + DLC)
desc: 뱀파이어 서바이벌 캐릭터 · DLC별 탭 · 에메랄드 디오라마 {len(EC)}명 시작 스킬 · 스킨 · PC 세이브로 해금 표시.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 캐릭터</div>
{cpage('🧛','캐릭터',{'ed':f'<p class="sub">디오라마 {len(EC)}명 · 이름 아래는 기본 시작 스킬 · 들어가면 스킨별 시작 스킬과 해금 방법</p><div class="tiles">{"".join(tiles)}</div>'},top='<p class="sub">PC는 💾 세이브를 넣으면 아직 해금 안 된 캐릭터가 회색으로 보여요</p>')}
''',encoding='utf-8')
redir('vs/ed/chars.html','/vs/chars.html','#ed')
(D/'items.json').write_text(json.dumps(items,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# 해금 페이지 위에 캐릭터 링크
p=R/'_src/vs/ed/index.html';t=p.read_text(encoding='utf-8')
if False:
    t=t.replace('<div class="prog">','<a class="btn-line" href="/vs/chars.html">🧛 디오라마 캐릭터 보기</a> <a class="btn-line" href="/vs/map.html">🗺️ 디오라마 지도 보기</a>\n<div class="prog">',1);p.write_text(t,encoding='utf-8')
print('chars pages',len(EC))

# ---------- 본편 해금 ----------
BU=json.loads((D/'base_unlocks.json').read_text(encoding='utf-8'))
ICON2={'성장·진화':'📈','발견':'⚰️','특수':'🎯','레벨':'🆙','생존':'⏱','성장':'📈','처치 수':'💀','비밀':'🔒','진화':'✨','기타':'📦'}
bc={}
for u in BU: bc[u['type']]=bc.get(u['type'],0)+1
bty=lambda t:t
brows=[]
NMAIN=sum(1 for u in BU if u['group']!='추가')
for i,u in enumerate(BU,1):
    t=CATL[u['cat']];scope='전용' if u['char'] else '공통'
    gl=''
    if u.get('grp'):
        mates=[x for x in BU if x.get('grp')==u['grp']]
        ev=items.get(u['grp'],{}).get('e') or ''
        gl='<p class="guide">🔗 한 판에 같이: '+' · '.join(f'<a href="#b-{x["id"]}">#{x["gi"]}</a> {esc(x["text_fix"])}' for x in sorted(mates,key=lambda x:x['ord']))+'</p>'+(f'<p class="guide">✨ 진화: {link_names(ev)}</p>' if ev else '')
    q=(f'<div class="fix">게임 원문: {esc(u["text"])}</div>' if u['text_fix']!=u['text'] else '')
    rw=' · '.join(link_names(r) for r in u['reward'])
    badge=('<span class="bd bd-own">전용 · '+' · '.join(pop(c) for c in u['char'])+'</span>') if u['char'] else '<span class="bd">공통</span>'
    mode='<span class="bd">누적</span> ' if u['mode']=='누적' else ''
    title=u['text_fix']
    extra=''
    brows.append((u['group']!='추가',u['ord'],f'''<details class="ul" data-id="b-{u['id']}" data-type="{t}" data-scope="{scope}" data-gi="{i}" data-ord="{u['ord']}"{need_attr(u)}>
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">{i}</span><span class="tt">{esc(title)}{extra}</span><span class="k">{CATI.get(t,'')} {t}</span></summary>
<div class="bdy"><p class="rw">🎁 보상 → {rw}</p>{q}<p>{mode}{badge}</p>{gl}{need_note(u,'/vs/unlocks.html')}</div></details>'''))
_bm=[h for m,o,h in sorted([x for x in brows if x[0]],key=lambda x:x[1])];_be=[h for m,o,h in sorted([x for x in brows if not x[0]],key=lambda x:x[1])];brows=_bm+_be
btypes=sorted({bty(u['type']) for u in BU},key=lambda t:(t=='기타',-sum(1 for u in BU if bty(u['type'])==t)))
bfb=''.join(f'<button type="button" data-f="{t}">{ICON2.get(t,"")} {t} {sum(1 for u in BU if bty(u["type"])==t)}</button>' for t in btypes)
(R/'_src/vs/base').mkdir(parents=True,exist_ok=True)
# 📌 상단 추천 띠용 데이터: data/vs/ed/rbar.json
ZONEN=['마녀 왕국 풀크라','미야코시','풀크라','그렐론','아발론','요미','프로비던스','정션']
_hlre2=re.compile('('+'|'.join(map(re.escape,sorted(ZONEN+BOSSN,key=len,reverse=True)))+')')
_rb={}
for u in U['unlocks']:
    t=u['text']
    for a,b in FIXT.items():t=t.replace(a,b)
    _th=_hlre2.sub(lambda m:f'<span class="{"hz" if m.group(0) in ZONEN else "hbx"}">{m.group(0)}</span>',esc(t))   # 추천 창: 구역 노랑 · 보스 빨강 · 링크 없음 (11/26 제이)
    if INVM(u):_th='<span class="binv">🔄 인버스</span> '+_th
    _rb['ed-%d'%u['n']]={'n':u['n'],'t':t,'th':_th,'rw':u['reward'],'need':u.get('need',[]),'g':guide(u)}
(D/'ed/rbar.json').write_text(json.dumps(_rb,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# ── 통합 해금 페이지 /vs/unlocks.html (게임처럼 칸: 1.0 버전 · 추가 · DLC) ──
ALLT={}
for r in brows+rows:
    t=re.search(r'data-type="([^"]+)"',r).group(1);ALLT[t]=ALLT.get(t,0)+1
ICA=CATI
afb=''.join(f'<button type="button" data-f="{t}">{ICA.get(t,"")} {t} {n}</button>' for t,n in sorted(ALLT.items(),key=lambda x:(x[0]=='기타',-x[1])))
(R/'_src/vs/unlocks.html').write_text(f'''title: 해금 {len(BU)+len(U["unlocks"])}개 (본편 + DLC)
desc: 뱀파이어 서바이벌 해금 조건 전체. 게임처럼 1.0 버전 · 추가 · DLC 칸으로 나눔 · 먼저 필요한 해금을 체크해야 다음 해금이 보임 · 게임 데이터 기준.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 해금</div>
{cpage('🔓','해금',{'base':chr(10).join(brows[:NMAIN]),'extra':chr(10).join(brows[NMAIN:]),'ed':'<p class="secnav"><a href="/vs/map.html#ed">🗺️ 지도</a> · <a href="/vs/chars.html#ed">🧛 캐릭터</a></p>'+chr(10).join(rows)},top='''<p class="sub">게임 해금 화면처럼 칸으로 나눴습니다 · 기본은 <b>열리는 순서(추천 순서)</b> · 같은 스킬의 레벨·진화는 붙여 놨습니다(🔗 한 판에 같이) · 번호는 게임 순서</p>
<div class="prog"><div class="pb"><i id="pbar"></i></div><span id="ptxt"></span></div>
<div class="fbar" id="fType"><button type="button" class="on" data-f="">전체</button>{afb}</div>
<div class="fbar" id="fScope"><button type="button" class="on" data-s="">전체</button><button type="button" data-s="공통">공통</button><button type="button" data-s="전용">전용</button>
<label class="only"><input type="checkbox" id="onlyLeft"> 미해금만 보기</label> <button type="button" id="ordBtn" class="ordbtn">🧭 추천 순서</button></div>
''',wrap='id="ulist" data-group="all" data-lock="1"')}
<p class="note">☑ 체크는 이 기기(브라우저)에만 저장됩니다. PC는 🛠 도구 → 💾 세이브 자동 체크로 한 번에 채울 수 있습니다.</p>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
# 예전 주소 → 통합 페이지로 (검색·링크 보존)
REDIR='''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>이동 중 · LucKey's Lab</title><link rel="canonical" href="https://luckeys-lab.github.io/vs/unlocks.html{h}">
<meta name="robots" content="noindex"><script>location.replace('/vs/unlocks.html'+(location.hash||'{h}'))</script><meta http-equiv="refresh" content="0;url=/vs/unlocks.html{h}"></head><body><a href="/vs/unlocks.html{h}">해금 페이지로 이동</a></body></html>'''
(R/'vs/base').mkdir(parents=True,exist_ok=True);(R/'vs/base/unlocks.html').write_text(REDIR.replace('{h}',''),encoding='utf-8')
for f in [R/'_src/vs/base/unlocks.html']:
    if f.exists():f.unlink()
print('base unlocks',len(BU))

# ── 디오라마 지도 (/vs/map.html) · 핀 = data/vs/ed/map.json (게임 맵 오브젝트 · tools/proto/edmap.py) · 보스 = data/vs/ed/bosses.json ──
MP=json.load(open(R/'data/vs/ed/map.json'))
BS=json.load(open(R/'data/vs/ed/bosses.json'))
ZNAME={int(k):v for k,v in MP['zones'].items()}
rowby={re.search(r'data-id="(ed-\d+)"',r).group(1):r for r in rows}
UN={u['n']:u for u in U['unlocks']}
def side(n):return dual(_side(n),_side(-n))
def ufix(t):
    for a,b in FIXT.items():t=t.replace(a,b)
    return t
def ulines(ns):return [[f'#{n} {ufix(UN[n]["text"])} → 🎁 {UN[n]["reward"]}','/vs/map.html#ed-%d'%n] for n in ns]
# 보스 · 관 미리보기 카드 (items.json에 EB_ · EC_ 로 넣음)
for p in MP['pins']:
    z=p['zone'];zn=ZNAME.get(z,'숨은 구역')
    if p['kind']=='boss':
        b=BS.get(p['id'],{});nm=p['label']
        ns=[u['n'] for u in U['unlocks'] if nm.split(' ')[0] in u['text'] and u['zone']!='전부']
        st=f"❤️ {b.get('hp')}{'×레벨' if b.get('hpxlv') else ''} · ⚔️ {b.get('power')} · 👟 {b.get('speed')}"
        bd=re.sub(r'\s+',' ',(b.get('d') or '').replace('\\n',' ')).strip()
        items['EB_'+p['id']]={'n':nm,'t':f'보스 · {zn}','d':'','p':st,'ul':ulines(sorted(set(ns))),'bn':b.get('ko') or nm,'bd':bd}
    if p['kind']=='coffin':
        ch=items.get('CH_'+p['id'],{});cn={'EME_RAPIERDUAL':2,'EME_SWORDBITE':25}.get(p['id'])
        items['EC_'+p['id']]={'i':ch.get('i'),'n':'⚰️ '+p['label'],'t':f'관 · {zn} · {_side(p["xm"])}','d':ch.get('d',''),'s':ch.get('s'),'si':ch.get('si'),'ul':ulines([cn]) if cn else [],'l':ch.get('l')}
_b=BS['EME_BOSS_OGRE']
items['EB_EME_BOSS_OGRE']={'n':'숨은 오우거','t':'보스 · 21~25분쯤','d':'21~25분쯤 나타나요 (시간 확인 중). 화면 가장자리 💀 표시를 따라가면 돼요 · 일반 6시(정션 아래쪽) · 인버스 12시.','p':f"❤️ {_b['hp']}{'×레벨' if _b['hpxlv'] else ''} · ⚔️ {_b['power']} · 👟 {_b['speed']}",'ul':ulines([41]),'bn':'숨은 오우거','bd':''}
(D/'items.json').write_text(json.dumps(items,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def pin_html(p,hub=False):
    st=f'--x:{p["x"]/256*100:.2f}%;--y:{p["y"]/280*100:.2f}%'
    xm=(f'<b>{dual(_arr(p["xm"]),_arr(-p["xm"]))}</b>' if p['xm'] else '')
    if p['kind']=='portal':
        z=int(re.search(r'biome(\d)',p['id']).group(1))
        if hub:
            side='l' if p['x']<100 else 'r' if p['x']>156 else ('t' if p['y']<140 else 'b')
            bn=next((x['label'] for x in MP['pins'] if x['zone']==z and x['kind']=='boss'),'')
            return f'<a class="pin k-portal" style="{st}" href="#z{z}" title="{esc(ZNAME[z])}">{z}<i class="zl zl-{side}">{esc(ZNAME[z])}<small>👹 {esc(bn)}</small></i></a>'
        return f'<a class="pin k-portal" style="{st}" href="#z7" title="정션으로">🌀</a>'
    if p['kind']=='item':
        it=items.get(p['id'],{});ic=f'<img src="{it["i"]}" alt="">' if it.get('i') else '💍'
        return f'<span class="pin k-item" style="{st}" data-pop="{p["pk"]}">{ic}{xm}</span>'
    if p['kind']=='coffin':return f'<span class="pin k-coffin" style="{st}" data-pop="{p["pk"]}">⚰️{xm}<i class="lbl">{esc(p["label"])}</i></span>'
    return f'<span class="pin k-boss" style="{st}" data-pop="{p["pk"]}">👹{xm}<i class="lbl">{esc(p["label"])}</i></span>'
def pin_li(p):
    if p['kind']=='portal':return f'<li>🌀 정션으로 가는 포탈 · {side(p["xm"])}</li>'
    if p['kind']=='item':return f'<li>{pop(items[p["id"]]["n"]) if p["id"] in items else esc(p["id"])} · {side(p["xm"])}</li>'
    if p['kind']=='coffin':return f'<li>⚰️ <b class="hf">관</b> · <span class="pop" data-pop="EC_{p["id"]}"><b class="hc">{esc(p["label"])}</b></span> · {side(p["xm"])}</li>'
    return f'<li>👹 보스 · <span class="pop" data-pop="EB_{p["id"]}"><b class="hb">{esc(p["label"])}</b></span> · {side(p["xm"])}</li>'
KO=['coffin','boss','portal','item']
def popkey(p):return {'item':p['id'],'coffin':'EC_'+p['id'],'boss':'EB_'+p['id']}.get(p['kind'])
NEAR=10   # 지도 그림 픽셀(256 기준) · 이보다 가까우면 한 묶음
for z in set(p['zone'] for p in MP['pins']):
    ps=[p for p in MP['pins'] if p['zone']==z and popkey(p)]
    for p in ps:
        grp=[q for q in ps if abs(q['x']-p['x'])<NEAR and abs(q['y']-p['y'])<NEAR]
        grp.sort(key=lambda q:KO.index(q['kind']))
        p['pk']=','.join(popkey(q) for q in grp)
OGPIN='<span class="pin k-ogre" style="--x:54.69%;--y:96%" data-pop="EB_EME_BOSS_OGRE">💀<i class="lbl">숨은 오우거 {}<small>21~25분쯤</small></i></span>'.format(dual('⬇','⬆'))
def mapbox(z,ps,hub=False):
    return f'''<div class="map" data-z="{z}"><div class="mi"><img src="/assets/vs/ed/map/z{z}.png" alt="{esc(ZNAME[z])} 지도" loading="lazy">{''.join(pin_html(p,hub) for p in ps)}{OGPIN if hub else ''}</div><button type="button" class="mfull" aria-label="크게 보기">⛶</button></div>'''
zs=[]
for z in range(1,7):
    ps=[p for p in MP['pins'] if p['zone']==z];ps.sort(key=lambda p:KO.index(p['kind']))
    ur=[rowby[f'ed-{u["n"]}'] for u in U['unlocks'] if u.get('zone')==z]
    zs.append(f'''<section class="zone" id="z{z}"><h2>{z} · {esc(ZNAME[z])}</h2>
{mapbox(z,ps)}
<ul class="pins">{''.join(pin_li(p) for p in ps)}</ul>
{('<h3>이 구역 해금</h3>'+chr(10).join(ur)) if ur else ''}
<p class="back"><a href="#z7">↑ 정션 지도로</a></p></section>''')
hubp=[p for p in MP['pins'] if p['zone']==7]
allr=[rowby[f'ed-{u["n"]}'] for u in U['unlocks'] if u.get('zone')=='전부']
ogr=[rowby[f'ed-{u["n"]}'] for u in U['unlocks'] if u.get('zone')=='hub']
cof=[p for p in MP['pins'] if p['kind']=='coffin']
cofbox=''.join(f'<li><b class="hf">⚰️ {i}번 관</b> · <span class="pop" data-pop="EC_{p["id"]}"><b class="hc">{esc(p["label"])}</b></span> → <a href="#z{p["zone"]}">{p["zone"]} {esc(ZNAME[p["zone"]])}</a> · {side(p["xm"])}{" (시작 화면 기준)" if p["zone"]==1 else ""}</li>' for i,p in enumerate(sorted(cof,key=lambda p:p['zone']),1))
MAPED=f'''<div class="coffins"><h2>⚰️ 관 위치</h2><ul>{cofbox}</ul></div>
<p class="sub">게임 데이터 기준 · 정션에서 포탈 번호를 누르면 그 구역으로 · 아이콘·이름을 누르면 설명 · ⛶ 누르면 크게</p>
<div class="howto"><b>칸</b> = 지도 그림 한 장. 구역은 옆으로 같은 무늬가 계속 반복됩니다. <b>→2</b> 표시는 포탈로 도착한 화면에서 <b>오른쪽으로 2장</b> 더 가면 있다는 뜻입니다.</div>
<div class="invsw" role="group" aria-label="지도 모드"><button type="button" data-inv="0" class="on">🌍 일반</button><button type="button" data-inv="1">🔄 인버스</button><span>인버스 = 맵 전체가 <b>180°</b> 돌아가요 (좌우·위아래 모두)</span></div>
<div id="ulist" data-group="ed">
<section class="zone" id="z7"><h2>🌀 정션 (허브)</h2>
{mapbox(7,hubp,True)}
<h3>모든 구역 해금</h3>
{chr(10).join(allr)}
</section>
{chr(10).join(zs)}
<section class="zone" id="z9"><h2>💀 <b class="hb">숨은 오우거</b> · 21~25분쯤</h2>
<p>해금 조건은 <b class="hb pop" data-pop="EB_EME_BOSS_OGRE">숨은 오우거</b> 1마리 처치입니다. <b>21~25분쯤</b> 나타나요 (정확한 시간 확인 중).</p>
<p>나타나면 화면 가장자리에 <b>💀 해골 표시</b>가 방향을 알려줘요. 일반 모드는 <b>6시</b>(정션 아래쪽, 지도의 💀 핀), <b>인버스는 맵이 돌아가서 12시</b>예요. 위 🔄 버튼으로 바꿔 보세요.</p>
<p class="note">게임 데이터에도 정션 훨씬 아래에 <span class="pop" data-pop="EB_EME_SUSPICIOUS_OGRE">수상한 오우거</span> 자리가 있어요.</p>
{chr(10).join(ogr)}
</section>
</div>
'''
(R/'_src/vs/map.html').write_text(f'''title: 지도 (본편 + DLC)
desc: 뱀파이어 서바이벌 에메랄드 디오라마 지도. 관 2개 위치와 정션(허브) · 구역 6곳의 보스 · 패시브 위치를 게임 데이터로 표시.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 지도</div>
{cpage('🗺️','지도',{'ed':MAPED})}
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
redir('vs/ed/map.html','/vs/map.html','#ed')
print('ed map',len(MP['pins']))

# ── 🤫 비밀 페이지 /vs/secrets.html (칸: 본편 · DLC) · data/vs/secrets.json (tools/proto/secrets.py) ──
SEC=json.load(open(R/'data/vs/secrets.json'))
def srow(r):
    t={'riddle':'수수께끼','spell':'주문','mod':'모드'}[r['kind']]
    title=r['d'] if r['kind']=='riddle' else (' · '.join(r['rw']) or r['d'])
    sp=f'<p>🔑 주문: <span class="spoil" title="눌러서 보기">{esc(r["spell"])}</span></p>' if r['spell'] else ''
    ds=f'<p class="fix">{esc(r["d"])}</p>' if r['kind']!='riddle' and r['d'] else ''
    rw=' · '.join(link_names(x) for x in r['rw'])
    return f'''<details class="ul" data-id="s-{esc(r['id'])}" data-type="{t}" data-scope="공통">
<summary><input type="checkbox" aria-label="비밀 체크"><span class="tt">{esc(title)}</span><span class="k">{'🧩' if r['kind']=='riddle' else '🔑' if r['kind']=='spell' else '🎛️'} {t}</span></summary>
<div class="bdy">{('<p class="rw">🎁 보상 → '+rw+'</p>') if rw else ''}{ds}{sp}</div></details>'''
secs=[]
for g in SEC:
    rd=[r for r in g['rows'] if r['kind']=='riddle'];spl=[r for r in g['rows'] if r['kind']!='riddle']
    secs.append((g['key'],f'''<h3>🧩 수수께끼 {len(rd)}</h3>
{chr(10).join(srow(r) for r in rd)}
<details class="spells"><summary>🔑 주문 {len(spl)}개 · 스포일러 (눌러서 펼치기)</summary>
{chr(10).join(srow(r) for r in spl)}
</details>'''))
(R/'_src/vs/secrets.html').write_text(f'''title: 비밀 (본편 + DLC)
desc: 뱀파이어 서바이벌 비밀 전체. 수수께끼 문구 · 보상 · 비밀 주문(접어 둠) · 본편과 DLC 칸으로 나눔 · 게임 데이터 기준.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 비밀</div>
{cpage('🤫','비밀',dict(secs),top='''<p class="sub">수수께끼는 게임 문구 그대로 · 주문은 스포일러라 접어 뒀습니다 · 주문 글자는 눌러야 보입니다</p>
<div class="prog"><div class="pb"><i id="pbar"></i></div><span id="ptxt"></span></div>
<div class="fbar"><label class="only"><input type="checkbox" id="onlyLeft"> 못 푼 것만 보기</label></div>''',wrap='id="ulist" data-group="secret"')}
<p class="note">☑ 체크는 이 기기(브라우저)에만 저장됩니다. PC는 🛠 도구 → 💾 세이브 자동 체크로 한 번에 채울 수 있습니다.</p>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
json.dump([r['id'] for g in SEC for r in g['rows']],open(R/'data/vs/secret_keys.json','w'),ensure_ascii=False)
print('secrets',sum(len(g['rows']) for g in SEC))


# ── 디오라마 📦 컬렉션 · 📖 우화집 (11/26 · 세이브 연동: data-col / data-kill · site.js ll_extra) ──
SUBS={'EME_RING_FIRE','EME_RING_WATER','EME_RING_WOOD','EME_RING_EARTH','EME_RING_METAL','EME_RING_CHAOS','EME_MECH_RAVE','EME_MECH_BALLMISS','EME_AXE_HELLFURY','EME_BLOOD_BLOODRAGE','EME_SWORD_SWALLOW','EME_SWORD_GALE'}
cw=[k[3:] for k in items if k.startswith('ED_') and k[3:] not in SUBS]
fams={}
for k in cw:fams.setdefault(re.sub(r'\d+$','',k),[]).append(k)
tiles=[]
for f,ks in fams.items():
    ks.sort();cells=''.join(f'<span class="ct" data-col="{k}" data-pop="ED_{k}">{"<img src=%s alt=>"%items["ED_"+k]["i"] if items["ED_"+k].get("i") else ""}<b>{esc(items["ED_"+k]["n"])}</b></span>' for k in ks)
    tiles.append(f'<div class="cline">{cells}</div>')
(R/'_src/vs/collection.html').write_text(f'''title: 컬렉션 (본편 + DLC)
desc: 뱀파이어 서바이벌 컬렉션 · DLC별 탭 · 에메랄드 디오라마 {len(cw)}개 스킬 진화 단계별 · PC 세이브 파일로 모은 것 표시.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 컬렉션</div>
{cpage('📦','컬렉션',{'ed':f'<p class="sub">디오라마 {len(cw)}개 · 한 줄 = 한 스킬의 진화 단계 · 아이콘을 누르면 설명</p><div class="cgrid">{"".join(tiles)}</div>'},top='<p class="sub">PC는 💾 세이브를 넣으면 아직 못 모은 것이 회색으로 보여요</p>')}
''',encoding='utf-8')
redir('vs/ed/collection.html','/vs/collection.html','#ed')
BE=json.loads((D/'ed/bestiary.json').read_text(encoding='utf-8'))
def bcard(i,b):
    st=f"❤️ {b['hp']}{'×Lv' if b['hpxlv'] else ''} · ⚔️ {b['pw']} · 👟 {b['sp']} · ✨ XP {b['xp']}"
    res=''.join(f'<span class="rz">{ {"Freeze":"❄️ 빙결","Rosary":"📿 묵주","Debuffs":"🌀 약화","Defang":"🦷 무력화"}.get(k,k)} 저항</span>' for k in b['res'])
    return f'''<article class="bcard{' boss' if b['boss'] else ''}" data-kill="{b['id']}">
<div class="bimg"><span class="bno">No.{i:02d}</span>{'<span class="bboss">👑 보스</span>' if b['boss'] else ''}<img src="{b['i']}" alt="{esc(b['n'])}" loading="lazy"><span class="bkill"></span></div>
<div class="binfo"><h3>{esc(b['n'])}<small>{esc(b['en'])}</small></h3><p class="bst">{st}</p>{('<p class="brs">'+res+'</p>') if res else ''}
{('<details class="blore"><summary>📖 이야기</summary><p>'+esc(b['d'])+'</p></details>') if b['d'] else ''}</div></article>'''
(R/'_src/vs/bestiary.html').write_text(f'''title: 우화집 (본편 + DLC)
desc: 뱀파이어 서바이벌 우화집 · DLC별 탭 · 에메랄드 디오라마 {len(BE)}마리 몹 그림 · 능력치 · 저항 · 이야기 · PC 세이브로 처치 수 표시.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 우화집</div>
{cpage('📖','우화집',{'ed':f'<p class="sub">디오라마 {len(BE)}마리 · 게임 우화집 순서</p><div class="bgrid">{"".join(bcard(i,b) for i,b in enumerate(BE,1))}</div>'},top='<p class="sub">PC는 💾 세이브를 넣으면 처치 수가 붙고, 아직 못 잡은 몹은 회색으로 보여요</p>')}
''',encoding='utf-8')
redir('vs/ed/bestiary.html','/vs/bestiary.html','#ed')
print('ed collection',len(cw),'bestiary',len(BE))


# ── ✨ 진화 /vs/evo.html (11/26 · 탭: 본편 · 추가 · 💎 디오라마 · 세이브: data-evo 줄 got/miss/locked) ──
evo=json.loads((D/'evo_rows.json').read_text(encoding='utf-8'))
EVSKIP={'FOLLOWER_KNIFE2'}   # 혼돈의 룬 → 사악한 통치자: 해금 보상·그림 없음 · 제이도 처음 봄 → 안 쓰는 데이터로 보고 뺌 (11/26)
evo=[e for e in evo if e['to'] not in EVSKIP]
def evchip(k,cls=''):
    it=items.get(k,{});ic=f'<img src="{it["i"]}" alt="" loading="lazy">' if it.get('i') else ''
    return f'<span class="ec{cls}" data-pop="{k}" data-ek="{k}">{ic}<b>{esc(it.get("n",k))}</b></span>'
def evrow(parts,to):
    return f'<div class="evr" data-evo="{to}" data-parts="{",".join(parts)}">{"<i class=pl>+</i>".join(evchip(p) for p in parts)}<i class="ar">→</i>{evchip(to," to")}</div>'
def evchain(ks,eid):
    req=[]
    for k in ks[1:]:
        tp=(items.get(eid(k),{}).get('p') or '').strip()
        if tp and tp not in ('-','.'):req.append(f'<b>{esc(items[eid(k)]["n"])}</b> {esc(tp)}')
    return f'<div class="evr ch" data-evo="{eid(ks[-1])}" data-parts="{eid(ks[0])}">'+'<i class="ar">→</i>'.join(evchip(eid(k),' to' if k==ks[-1] else '') for k in ks)+(f'<p class="ereq">{" · ".join(req)}</p>' if req else '')+'</div>'
_n=lambda nm:name2id.get(nm)
UNI=[([_n('은 반지'),_n('시곗바늘'),_n('금 반지')],'CORRIDOR'),([_n('좌 메탈리오'),_n('월계수'),_n('우 메탈리오')],'SHROUD')]
UNI=[(p,t) for p,t in UNI if all(p) and t in items]
eb=[evrow(e['parts'],e['to']) for e in evo if e['g']=='BASE'];ex=[evrow(e['parts'],e['to']) for e in evo if e['g']!='BASE']
tri=[k for k in ('TRIASSO1','TRIASSO2','TRIASSO3') if k in items]
efam={}
for k in [k[3:] for k in items if k.startswith('ED_') and k[3:] not in SUBS]:efam.setdefault(re.sub(r'\d+$','',k),[]).append(k)
edl=[evchain(sorted(v),lambda k:'ED_'+k) for v in efam.values() if len(v)>1]
EVT={'base':f'<h3>기본 진화 {len(eb)}</h3><div class="evl">{"".join(eb)}</div>'+(f'<h3>합체 진화 {len(UNI)}</h3><p class="note">패시브 둘 + 하나를 모두 최고 레벨로 · 보물상자에서 합쳐집니다</p><div class="evl">{"".join(evrow(p,t) for p,t in UNI)}</div>' if UNI else ''),
     'extra':f'<h3>추가 진화 {len(ex)}</h3><div class="evl">{"".join(ex)}</div>'+(f'<h3>팔찌</h3><div class="evl">{evchain(tri,lambda k:k)}</div>' if len(tri)>1 else ''),
     'ed':f'<p class="sub">디오라마 {len(edl)}줄 · 디오라마는 패시브 대신 <b>요구 사항</b>(아이템 · "기술")을 갖추면 진화</p><div class="evl">{"".join(edl)}</div>'}
(R/'_src/vs/evo.html').write_text(f'''title: 진화 (본편 + DLC)
desc: 뱀파이어 서바이벌 진화 조합 전체 · 본편 기본 · 합체 · 추가 · 에메랄드 디오라마 진화 단계 · PC 세이브로 진화한 것 표시 · 게임 데이터 기준.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 진화</div>
{cpage('✨','진화',EVT,top='<p class="sub">게임 데이터 기준 · 아이콘을 누르면 설명 · 스킬을 최고 레벨로 올리고 재료를 가진 채 보물상자를 열면 진화 · PC는 💾 세이브를 넣으면 아직 안 한 진화가 회색, 재료부터 없는 건 🔒</p>')}
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
print('evo',len(eb),len(ex),len(UNI),len(edl))

# ── 🎁 이번주 무료게임 /review/free.html (11/26 · data/free.json · 예약 작업이 매주 금요일 갱신 · 분류는 페이지 JS가 지금 시각으로) ──
FR=json.loads((R/'data/free.json').read_text(encoding='utf-8'))
STORE={'epic':('에픽','#2a2a2a'),'gog':('GOG','#86328a'),'stove':('스토브','#ff5a1f'),'steam':('스팀','#1b2838'),'ea':('EA 앱','#ff4747'),'ubisoft':('유비소프트','#0070ff'),'prime':('프라임 게이밍','#00a8e1')}
def fcard(g):
    sn,sc=STORE.get(g['store'],(g['store'],'#555'))
    return f'''<article class="fg" data-start="{g['start']}" data-end="{g['end']}">
<a class="fgimg" href="{g['url']}" target="_blank" rel="noopener"><img src="{g['img']}" alt="{esc(g['title'])}" loading="lazy" referrerpolicy="no-referrer"><span class="fgst" style="background:{sc}">{sn}</span><span class="fgt"></span></a>
<div class="fgb"><h3>{esc(g['title'])}</h3><p class="fgg">{esc(g.get('genre',''))}</p><p>{esc(g['desc'])}</p>{('<p class="fgfit">👍 <b>이런 사람에게</b> · '+esc(g['fit'])+'</p>') if g.get('fit') else ''}
<p class="fgd"></p><a class="fgbtn" href="{g['url']}" target="_blank" rel="noopener">스토어에서 받기 ›</a></div></article>'''
(R/'_src/review').mkdir(parents=True,exist_ok=True)
(R/'_src/review/free.html').write_text(f'''title: 이번주 무료게임 (에픽 · GOG · 스토브)
desc: 이번주 에픽게임즈 무료게임 · 언제까지 무료인지 남은 시간 · 다음 주 무료게임 미리보기 · 매주 금요일 갱신 · 받으면 계속 내 것.
<div class="crumb"><a href="/">홈</a> › <a href="/review/">리뷰</a> › 이번주 무료게임</div>
<h1>🎁 이번주 무료게임</h1>
<p class="sub">기간 안에 받으면 <b>계속 내 것</b> · 시간은 한국 시간 · 에픽은 매주 <b>금요일 새벽 1시</b>에 바뀌어요 · 매주 금요일 아침 갱신</p>
<div id="freebox">
<h2 class="fh" data-k="now">🟢 지금 무료</h2><div class="fgl" data-k="now"></div>
<h2 class="fh" data-k="next">⏳ 곧 무료</h2><div class="fgl" data-k="next"></div>
<details class="fpast"><summary>📜 지난 무료게임</summary><div class="fgl" data-k="past"></div></details>
<div class="fgl" data-k="all">{''.join(fcard(g) for g in sorted(FR['games'],key=lambda g:g['start'],reverse=True))}</div>
</div>
<p class="note">GOG · 스토브 같은 다른 스토어는 무료 배포가 있을 때만 올라와요 · 무료 여부는 각 스토어 공식 정보 기준이고, 받기 전에 스토어에서 한 번 더 확인해 주세요 · 마지막 확인 <span class="fupd" data-t="{FR['updated']}"></span></p>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
(R/'_src/review/index.html').write_text('''title: 리뷰
desc: LucKey's Lab 게임 리뷰 · 이번주 무료게임.
<div class="crumb"><a href="/">홈</a> › 리뷰</div>
<h1>🎬 리뷰</h1>
<div class="tiles"><a class="tile on" href="/review/free.html"><b>🎁 이번주 무료게임</b><span>에픽 · 남은 시간 · 매주 금요일 갱신</span></a><div class="tile off"><b>게임 리뷰</b><span>준비 중</span></div></div>
''',encoding='utf-8')
print('free',len(FR['games']))

# ── 🔒 ☑ 체크 → 해금/미해금 (11/26 · 모바일 유저용) · data/vs/lockmap.json = {아이템키: [이걸 주는 해금 체크키…]} ──
# 해금 보상에 있는 스킬·패시브·캐릭터·무기 = 그 해금을 체크해야 "해금됨" · 맵에 없는 건 처음부터 있는 것
LMAP={}
_n2=lambda nm,pre:next((k for k,v in items.items() if v.get('n')==nm and any(k.startswith(p) for p in pre)),None)
for u in BU:
    for r in u['reward']:
        p,_,nm=r.partition(' ')
        if p in ('스킬','패시브','캐릭터'):
            k=_n2(nm,('CH_',) if p=='캐릭터' else ('',)) if p=='캐릭터' else name2id.get(nm)
            if k and not k.startswith(('ED_','EB_','EC_')):LMAP.setdefault(k,[]).append('b-'+u['id'])
for u in U['unlocks']:
    p,_,nm=u['reward'].partition(' ')
    if p in ('무기','캐릭터'):
        k=_n2(nm,('CH_EME_',) if p=='캐릭터' else ('ED_',))
        if k:LMAP.setdefault(k,[]).append('ed-%d'%u['n'])
(D/'lockmap.json').write_text(json.dumps(LMAP,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('lockmap',len(LMAP),sum(1 for k in LMAP if k.startswith('CH_')),'chars')

# ── 📲 폰으로 보내기 (QR) · data/vs/sync_keys.json = 비트 순서 (⚠ 뒤에 붙이기만 · 순서 바꾸면 예전 코드가 깨짐) ──
SKF=D/'sync_keys.json'
SKL=json.loads(SKF.read_text(encoding='utf-8')) if SKF.exists() else []
_have=set(SKL)
_new=[k for k in list(json.loads((D/'ach_keys.json').read_text(encoding='utf-8')).values())+['ed-%d'%u['n'] for u in U['unlocks']]+['s-'+x for x in json.loads((D/'secret_keys.json').read_text(encoding='utf-8'))]
      +['cw:'+k for k in sorted(items) if not k.startswith(('CH_','EB_','EC_','TP_'))]
      +['uc:'+k[3:] for k in sorted(items) if k.startswith('CH_')]+['bc:'+k[3:] for k in sorted(items) if k.startswith('CH_')]
      +['kc:'+b['id'] for b in BE] if k not in _have]
SKL+=list(dict.fromkeys(_new))
SKF.write_text(json.dumps(SKL,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('sync keys',len(SKL))

# ── 🧭 사용법 /vs/howto.html (11/26 · 혜택 먼저 → 따라 하기 · 진짜 화면 조각으로 "전/후") ──
def _demo(h):return re.sub(r' data-(evo|parts|ek|ch|col|kill)="[^"]*"','',h)
_ec=[c for c in EC][:3]
def _dt(c,cls=''):
    hero=next((x for x in IMG['order'].get(c['id'],[]) if x),None)
    return f'<span class="tile ctile{cls}">{f"<img class=sp src={hero} alt=>" if hero else ""}<b>{esc(c["ko"])}</b></span>'
_e1=[e for e in evo if e['g']=='BASE'][4]
_ev=lambda cls:_demo(evrow(_e1['parts'],_e1['to'])).replace('class="evr"',f'class="evr {cls}"')
HOW=f'''title: 🧭 사용법 · 체크하면 뭐가 좋나요?
desc: LucKey's Lab 뱀파이어 서바이벌 공략 사용법 · 해금 체크 하나로 추천 해금 · 캐릭터 · 진화 · 컬렉션이 내 진행에 맞춰 바뀝니다 · 모바일은 직접 체크 · PC 스팀판은 세이브 파일로 자동.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 사용법</div>
<h1>🧭 사용법</h1>
<p class="sub">해금을 <b>☑ 체크</b>하면 사이트 전체가 <b>내 진행 상황</b>에 맞춰 바뀌어요 · 체크는 이 기기 브라우저에만 저장돼요 (로그인 없음)</p>

<h2>✨ 체크하면 이렇게 돼요</h2>
<div class="howgrid">
<section class="howc"><h3>🧭 다음 판에 뭘 할지 골라 줘요</h3>
<div class="hdemo"><div class="hrc"><b>보니 블레어 · 기본 · 🌍 일반</b><span>🗡️ 시작 스킬 펀치</span><ul><li>💎7 펀치 레벨을 6에 맞추세요 <em class="st">🗡️ 시작 스킬</em></li><li>💎8 펀치를 완전히 진화시키세요 <em class="st">🗡️ 시작 스킬</em></li><li>💎33 <span class="binv">🔄 인버스</span> 아발론에서 아이언 메이든 처치</li></ul></div></div>
<p>체크한 걸 보고 <b>한 판에 같이 노릴 수 있는 해금</b>을 캐릭터 + 스킨으로 묶어 줘요. 왼쪽 아래 <b>🧭</b> 버튼.</p></section>
<section class="howc"><h3>🔓 게임처럼 다음 해금이 열려요</h3>
<div class="hdemo two"><div><small>체크 전</small><ul class="hul"><li>☐ 💎2 첫 번째 관을 찾아서 여세요</li><li class="hlk">🔒 아직 숨은 해금 12개</li></ul></div><div><small>체크 후</small><ul class="hul"><li class="hok">☑ 💎2 첫 번째 관을 찾아서 여세요</li><li>☐ 💎3 플뢰레 레벨을 6에 맞추세요</li><li>☐ 💎5 스플래셔 레벨을 6에…</li></ul></div></div>
<p>먼저 필요한 해금을 체크해야 다음 줄이 보여요. 스포일러 걱정 없이 게임 화면이랑 똑같이.</p></section>
<section class="howc"><h3>🧛 캐릭터 · ✨ 진화 · 📦 컬렉션이 회색으로 나뉘어요</h3>
<div class="hdemo two"><div><small>체크 전 (아직 미해금)</small><div class="htiles">{_dt(_ec[0])}{_dt(_ec[1],' locked')}{_dt(_ec[2],' locked')}</div></div><div><small>체크 후</small><div class="htiles">{_dt(_ec[0])}{_dt(_ec[1])}{_dt(_ec[2],' locked')}</div></div></div>
<div class="hdemo"><small>✨ 진화 줄</small>{_ev('locked')}{_ev('')}</div>
<p>해금 안 된 캐릭터 · 재료가 아직인 진화는 <b>회색 + 🔒</b>. 뭘 먼저 풀어야 하는지 한눈에 보여요. 체크를 하나도 안 했으면 전부 원래 색이에요.</p></section>
<section class="howc"><h3>💾 PC 스팀판은 세이브로 한 번에</h3>
<div class="hdemo"><small>세이브를 넣으면 실제로 진화한 것까지 금테</small>{_ev('got')}{_ev('miss')}</div>
<p>세이브 파일을 넣으면 해금 체크가 자동으로 채워지고, <b>진화한 것 · 모은 것 · 잡은 몹</b>까지 표시돼요.</p></section>
</div>

<h2>👣 따라 하기</h2>
<div class="howgrid">
<section class="howc"><h3>📱 모바일 게임으로 할 때</h3><p class="note">모바일 게임은 세이브 파일을 꺼낼 수 없어서 직접 체크해요</p><ol>
<li><a href="/vs/unlocks.html">🔓 해금</a>에서 게임 해금 화면을 보면서 끝낸 걸 <b>☑ 체크</b> (DLC는 왼쪽 탭에서)</li>
<li>왼쪽 아래 <b>🧭 추천 해금</b> → 🟢 쉬움 · 🟡 보통 · 🔥 지옥 중 고르기</li>
<li>추천 카드의 <b>캐릭터 + 스킨</b>으로 게임 시작 · 줄을 누르면 공략 · 미니 지도</li>
<li>판이 끝나면 해낸 걸 <b>☑</b> → 추천이 다음 판으로 바뀜</li>
<li>가끔 <b>🔖 저장</b> → 링크를 카톡 나에게 보내 두면 체크가 날아갈 걱정 없음</li></ol></section>
<section class="howc"><h3>🖥️ PC 스팀판으로 할 때</h3><ol>
<li>왼쪽 아래 <b>💾</b> → 세이브 파일 고르기 (처음엔 위치 안내가 떠요) · 화면 아무 데나 끌어다 놓아도 돼요</li>
<li>해금 체크 + 금테 표시가 한 번에 채워짐</li>
<li>폰으로 공략을 보고 싶으면 <b>🔖</b> → PC 화면의 QR을 폰 기본 카메라로 찍기 <span class="note">(사이트 체크만 옮겨요 · 게임 진행이 옮겨지는 건 아니에요)</span></li>
<li>게임을 하고 나면 💾 다시 → 최신으로</li></ol>
</section>
</div>

<h2>🔖 체크 저장 · 불러오기</h2>
<p class="sub">체크는 이 브라우저에만 있어서 <b>기록을 지우거나 폰을 바꾸면 사라져요</b> · 왼쪽 아래 <b>🔖</b>로 링크·QR에 저장해 두세요 · 숫자 배지(+5)가 뜨면 저장한 뒤로 체크가 늘었다는 뜻</p>
<div class="howgrid">
<section class="howc"><h3>💾 저장</h3><img class="hshot" src="/assets/howto/bk_save.png" alt="🔖 저장 화면" loading="lazy"><ol>
<li>왼쪽 아래 <b>🔖</b> 누르기</li><li><b>🔗 링크 복사</b> → 카톡 <b>나에게 보내기</b>에 붙여넣기 (추천)</li><li>또는 <b>🖼️ QR 이미지 저장</b> → 갤러리에 저장</li></ol></section>
<section class="howc"><h3>📥 불러오기</h3><img class="hshot" src="/assets/howto/bk_load.png" alt="🔖 불러오기 화면" loading="lazy"><ol>
<li><b>링크</b>로 저장했으면 → 카톡에서 그 링크를 <b>누르면 끝</b></li><li><b>QR 이미지</b>면 → 🔖 → 📥 불러오기 → <b>QR 사진 고르기</b> → 갤러리에서 그 사진 선택 (카메라 안 씀)</li><li><b>PC → 폰</b>: PC에서 🔖 → 폰 기본 카메라로 PC 화면 QR 찍기</li></ol>
<p class="note">불러오면 지금 체크는 불러온 걸로 바뀌어요</p></section>
</div>

<h2>🔍 표시 뜻</h2>
<table class="howt"><tr><td>🟢 🟡 🔥</td><td>추천 난이도 · 쉬움 / 보통 / 지옥 (한 판에 노리는 개수와 어려움)</td></tr>
<tr><td>🗡️ 시작 스킬</td><td>그 캐릭터 · 스킨이 처음부터 들고 있는 스킬이라 확실해요</td></tr>
<tr><td>🎲 상자 운</td><td>레벨업 · 상자에서 그 스킬이 나와 줘야 해요</td></tr>
<tr><td><span class="binv">🔄 인버스</span></td><td>인버스(반전) 모드에서만 해금 · 맵이 180° 돌아가 있어요</td></tr>
<tr><td>🔒 회색</td><td>아직 해금 안 됨 (☑ 체크 또는 💾 세이브 기준)</td></tr>
<tr><td>금테</td><td>💾 세이브 기준 진화함 · 모음 · 잡음</td></tr>
<tr><td>🔖 +5</td><td>저장한 뒤로 체크가 5개 늘었어요 · 🔖 눌러 다시 저장</td></tr>
<tr><td>💎7</td><td>에메랄드 디오라마 해금 7번 (게임 순서)</td></tr></table>

<h2>❔ 자주 묻는 것</h2>
<details class="faq"><summary>체크가 사라졌어요</summary><p>체크는 이 기기 브라우저에만 저장돼요. 브라우저 기록 · 사이트 데이터를 지우거나 다른 브라우저로 열면 비어 보여요. 🔖로 저장해 둔 링크·QR이 있으면 그걸로 되살릴 수 있어요.</p></details>
<details class="faq"><summary>PC 체크를 폰에서도 보고 싶어요</summary><p>PC에서 🔖 → 폰 기본 카메라로 PC 화면의 QR을 찍으면 돼요. 링크를 카톡으로 보내서 폰에서 눌러도 돼요.</p></details>
<details class="faq"><summary>모바일 게임 세이브는 못 넣나요?</summary><p>모바일 게임은 세이브 파일을 밖으로 꺼낼 수 없어서 ☑ 직접 체크해요. 체크만 해도 추천 · 🔒 표시는 똑같이 돼요.</p></details>
<details class="faq"><summary>DLC를 안 샀어요</summary><p>왼쪽 탭에서 본편 · 산 DLC만 보면 돼요. 추천은 체크한 것 기준이라 안 산 DLC는 신경 안 써도 돼요.</p></details>
<div class="ad" data-slot="end"></div>
'''
(R/'_src/vs/howto.html').write_text(HOW,encoding='utf-8')
print('howto ok')
