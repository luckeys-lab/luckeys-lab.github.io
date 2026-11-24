#!/usr/bin/env python3
"""카드(JSON) → _src 페이지 만들기. 그다음 build.py가 틀을 끼워 완성.
   python3 tools/gen.py && python3 tools/build.py"""
import json,pathlib,html,re
R=pathlib.Path(__file__).resolve().parent.parent
D=R/'data/vs'
items=json.loads((D/'items.json').read_text(encoding='utf-8'))
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
        n,rw=NEEDI[k];pre='/vs/base/unlocks.html' if k.startswith('b-') else '/vs/ed/'
        href=('#' if pre==here else pre+'#')+k
        return f'<a href="{href}">#{n}</a> {esc(" · ".join(rw))}'
    return '<p class="need">🔒 먼저: '+' 그리고 '.join(' 또는 '.join(one(k) for k in g) for g in u['need'])+'</p>'

FIXT={'시우그나스':'시그나스','디바 5호':'디바 5번'}
CH=U['chars']
FULL={'츠나노리':'츠나노리 미도','보니':'보니 블레어','포미나':'포미나 프랭클린','디바 5번':'디바 5번','아메야':'아메야 아이슬링','시그나스':'시그나스'}
ZONE={1:'1 미야코시',2:'2 풀크라',3:'3 그렐론',4:'4 아발론',5:'5 요미',6:'6 구역','hub':'아래 허브','전부':'모든 구역'}
ICON={'성장':'📈','진화':'✨','찾아서진화':'🔍','사냥':'⚔️','발견':'⚰️','특수':'🎯','기타':'📦'}
cnt={}
for u in U['unlocks']: cnt[u['type']]=cnt.get(u['type'],0)+1
def ty(t): return t if cnt.get(t,0)>=3 else '기타'
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
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">{u['n']}</span><span class="tt">{esc(title)}</span><span class="k">{ICON.get(t,'')} {t}</span></summary>
<div class="bdy"><p class="rw">🎁 보상 → {link_names(u['reward'])}</p>{q}<p>{badge}{(' · 📍 '+esc(loc)) if loc else ''}</p>{need_note(u,'/vs/ed/')}</div></details>''')
types=sorted({ty(u['type']) for u in U['unlocks']},key=lambda t:(t=='기타',-sum(1 for u in U['unlocks'] if ty(u['type'])==t)))
fb=''.join(f'<button type="button" data-f="{t}">{ICON.get(t,"")} {t} {sum(1 for u in U["unlocks"] if ty(u["type"])==t)}</button>' for t in types)
(R/'_src/vs/ed').mkdir(parents=True,exist_ok=True)
(R/'_src/vs/ed/index.html').write_text(f'''title: 에메랄드 디오라마 해금 41개
desc: 뱀파이어 서바이벌 에메랄드 디오라마 해금 조건 41개 전체. 게임 데이터 기준 · 필요 캐릭터와 시작 스킬 · 해금 체크.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 에메랄드 디오라마</div>
<h1>💎 에메랄드 디오라마 · 해금</h1>
<p class="sub">무료 DLC · 해금 {len(U['unlocks'])}개 · 게임 데이터 기준 · 지도와 캐릭터 페이지는 준비 중</p>
<div class="prog"><div class="pb"><i id="pbar"></i></div><span id="ptxt"></span></div>
<div class="fbar" id="fType"><button type="button" class="on" data-f="">전체</button>{fb}</div>
<div class="fbar" id="fScope"><button type="button" class="on" data-s="">전체</button><button type="button" data-s="공통">공통</button><button type="button" data-s="전용">전용</button>
<label class="only"><input type="checkbox" id="onlyLeft"> 미해금만 보기</label></div>
<div id="ulist" data-group="ed" data-lock="1">
{chr(10).join(rows)}
</div>
<p class="note">☑ 체크는 이 기기(브라우저)에만 저장됩니다. 줄을 누르면 펼쳐집니다.</p>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')

# ---------- 본편 진화 ----------
evo=json.loads((D/'evo_rows.json').read_text(encoding='utf-8')) if (D/'evo_rows.json').exists() else []
def row(e):
    parts=' + '.join(pop(items[p]['n']) if p in items else esc(p) for p in e['parts'])
    to=pop(items[e['to']]['n']) if e['to'] in items else esc(e['to'])
    return f'<tr><td>{parts}</td><td class="to">→ {to}</td></tr>'
base=[e for e in evo if e['g']=='BASE'];extra=[e for e in evo if e['g']!='BASE']
(R/'_src/vs/evo.html').write_text(f'''title: 본편 진화 조합표
desc: 뱀파이어 서바이벌 본편 진화 조합 전체 (게임 데이터 기준). 스킬 + 패시브 → 진화 스킬.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 진화</div>
<h1>✨ 본편 진화 조합</h1>
<p class="sub">게임 데이터 기준 · 이름을 누르면 설명이 보입니다 · 스킬을 최고 레벨로 올리고 패시브를 가진 채 보물상자를 열면 진화합니다</p>
<h2>기본 {len(base)}</h2><table class="evo">{''.join(row(e) for e in base)}</table>
<h2>추가 {len(extra)}</h2><table class="evo">{''.join(row(e) for e in extra)}</table>
<p class="note">시곗바늘·월계수 같은 다른 방식의 합체 진화는 정리 중입니다.</p>
''',encoding='utf-8')
print('gen ok',len(rows),len(evo))

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
    sk=''.join(f'<div class="skin"><b>{esc(s["ko"])}</b><span>🗡️ {pop(s["start"]) if s.get("start") else "-"}</span></div>' for s in c['skins'])
    howt=''.join(f'<li><a href="/vs/ed/#ed-{u["n"]}">{u["n"]}번</a> · {esc(u["text"])}</li>' for u in how) or '<li>처음부터 또는 확인 중</li>'
    tiles.append(f'<a class="tile" href="/vs/ed/c/{sl}.html"><b>{esc(c["ko"])}</b><span>🗡️ {esc(c["start"] or "-")}</span></a>')
    (R/f'_src/vs/ed/c/{sl}.html').write_text(f'''title: {c["ko"]} · 에메랄드 디오라마
desc: 뱀파이어 서바이벌 에메랄드 디오라마 캐릭터 {c["ko"]} · 시작 스킬 {c["start"]} · 스킨별 시작 스킬 · 해금 방법 · 이 캐릭터가 필요한 해금
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › <a href="/vs/ed/">에메랄드 디오라마</a> › <a href="/vs/ed/chars.html">캐릭터</a></div>
<h1>{esc(c["ko"])}</h1>
<p class="sub">🗡️ 시작 스킬 {pop(c["start"]) if c.get("start") else "-"}</p>
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
(R/'_src/vs/ed/chars.html').write_text(f'''title: 에메랄드 디오라마 캐릭터 {len(EC)}
desc: 뱀파이어 서바이벌 에메랄드 디오라마 캐릭터 {len(EC)}명 · 시작 스킬 · 스킨
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › <a href="/vs/ed/">에메랄드 디오라마</a> › 캐릭터</div>
<h1>🧛 디오라마 캐릭터 {len(EC)}</h1>
<p class="sub">이름 아래는 기본 시작 스킬 · 들어가면 스킨별 시작 스킬과 해금 방법</p>
<div class="tiles">{''.join(tiles)}</div>
''',encoding='utf-8')
(D/'items.json').write_text(json.dumps(items,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# 해금 페이지 위에 캐릭터 링크
p=R/'_src/vs/ed/index.html';t=p.read_text(encoding='utf-8')
if 'chars.html' not in t:
    t=t.replace('<div class="prog">','<a class="btn-line" href="/vs/ed/chars.html">🧛 디오라마 캐릭터 보기</a>\n<div class="prog">',1);p.write_text(t,encoding='utf-8')
print('chars pages',len(EC))

# ---------- 본편 해금 ----------
BU=json.loads((D/'base_unlocks.json').read_text(encoding='utf-8'))
ICON2={'발견':'⚰️','특수':'🎯','레벨':'🆙','생존':'⏱','성장':'📈','처치 수':'💀','비밀':'🔒','진화':'✨','기타':'📦'}
bc={}
for u in BU: bc[u['type']]=bc.get(u['type'],0)+1
bty=lambda t:t if bc.get(t,0)>=3 else '기타'
brows=[]
NMAIN=sum(1 for u in BU if u['group']!='추가')
for i,u in enumerate(BU,1):
    t=bty(u['type']);scope='전용' if u['char'] else '공통'
    q=(f'<div class="fix">게임 원문: {esc(u["text"])}</div>' if u['text_fix']!=u['text'] else '')
    rw=' · '.join(link_names(r) for r in u['reward'])
    badge=('<span class="bd bd-own">전용 · '+' · '.join(pop(c) for c in u['char'])+'</span>') if u['char'] else '<span class="bd">공통</span>'
    mode='<span class="bd">누적</span> ' if u['mode']=='누적' else ''
    title=u['text_fix']
    extra=''
    brows.append(f'''<details class="ul" data-id="b-{u['id']}" data-type="{t}" data-scope="{scope}"{need_attr(u)}>
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">{i}</span><span class="tt">{esc(title)}{extra}</span><span class="k">{ICON2.get(t,'')} {t}</span></summary>
<div class="bdy"><p class="rw">🎁 보상 → {rw}</p>{q}<p>{mode}{badge}</p>{need_note(u,'/vs/base/unlocks.html')}</div></details>''')
btypes=sorted({bty(u['type']) for u in BU},key=lambda t:(t=='기타',-sum(1 for u in BU if bty(u['type'])==t)))
bfb=''.join(f'<button type="button" data-f="{t}">{ICON2.get(t,"")} {t} {sum(1 for u in BU if bty(u["type"])==t)}</button>' for t in btypes)
(R/'_src/vs/base').mkdir(parents=True,exist_ok=True)
(R/'_src/vs/base/unlocks.html').write_text(f'''title: 본편 해금 {len(BU)}개
desc: 뱀파이어 서바이벌 본편 해금 조건 {len(BU)}개 전체 (1.0 + 추가). 게임 데이터 기준 · 보상 · 필요 캐릭터 · 해금 체크.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 본편 해금</div>
<h1>🔓 본편 해금 {len(BU)}</h1>
<p class="sub">1.0 + 무료 추가 업데이트 · 게임 데이터 기준 · 보상 이름을 누르면 설명이 보입니다</p>
<div class="prog"><div class="pb"><i id="pbar"></i></div><span id="ptxt"></span></div>
<div class="fbar" id="fType"><button type="button" class="on" data-f="">전체</button>{bfb}</div>
<div class="fbar" id="fScope"><button type="button" class="on" data-s="">전체</button><button type="button" data-s="공통">공통</button><button type="button" data-s="전용">전용</button>
<label class="only"><input type="checkbox" id="onlyLeft"> 미해금만 보기</label></div>
<div id="ulist" data-group="base" data-lock="1">
<details class="sec" open><summary>본편 <span class="sc"></span></summary>
{chr(10).join(brows[:NMAIN])}
</details>
<details class="sec" open><summary>추가 <span class="sc"></span></summary>
{chr(10).join(brows[NMAIN:])}
</details>
</div>
<p class="note">☑ 체크는 이 기기(브라우저)에만 저장됩니다. 순서는 게임 데이터 순서이고, 추천 순서는 준비 중입니다.</p>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
print('base unlocks',len(BU))
