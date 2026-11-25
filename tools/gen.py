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


# 이름 강조: 보스(빨강) · 캐릭터(파랑) · 관(금색)
BOSSN=['스피릿 비스트','어스 드래곤','최종 황제의 악마 형태','최종 황제','아이언 메이든','이와나가히메의 유령','살아있는 고뇌','숨은 오우거','모든 보스']
CHARN=sorted(['츠나노리 미도','보니 블레어','포미나 프랭클린','디바 5번','아메야 아이슬링','시그나스','츠나노리','보니','포미나','아메야','디바'],key=len,reverse=True)
_hlre=re.compile('('+'|'.join(map(re.escape,BOSSN+CHARN))+r'|(?<=번째 )관)')
def hl(t):
    def f(m):
        w=m.group(0);c='hb' if w in BOSSN else 'hf' if w=='관' else 'hc'
        return f'<b class="{c}">{w}</b>'
    return _hlre.sub(f,t)

FIXT={'시우그나스':'시그나스','디바 5호':'디바 5번'}
CH=U['chars']
FULL={'츠나노리':'츠나노리 미도','보니':'보니 블레어','포미나':'포미나 프랭클린','디바 5번':'디바 5번','아메야':'아메야 아이슬링','시그나스':'시그나스'}
ZONE={1:'1 미야코시',2:'2 마녀 왕국 풀크라',3:'3 그렐론',4:'4 아발론',5:'5 요미',6:'6 프로비던스','hub':'숨은 구역 (오우거)','전부':'모든 구역'}
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
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">{u['n']}</span><span class="tt">{hl(esc(title))}</span><span class="k">{ICON.get(t,'')} {t}</span></summary>
<div class="bdy"><p class="rw">🎁 보상 → {link_names(u['reward'])}</p>{q}<p>{badge}{(' · 📍 '+esc(loc)) if loc else ''}</p>{need_note(u,'/vs/ed/')}</div></details>''')
types=sorted({ty(u['type']) for u in U['unlocks']},key=lambda t:(t=='기타',-sum(1 for u in U['unlocks'] if ty(u['type'])==t)))
fb=''.join(f'<button type="button" data-f="{t}">{ICON.get(t,"")} {t} {sum(1 for u in U["unlocks"] if ty(u["type"])==t)}</button>' for t in types)
(R/'_src/vs/ed').mkdir(parents=True,exist_ok=True)
(R/'_src/vs/ed/index.html').write_text(f'''title: 에메랄드 디오라마 해금 41개
desc: 뱀파이어 서바이벌 에메랄드 디오라마 해금 조건 41개 전체. 게임 데이터 기준 · 필요 캐릭터와 시작 스킬 · 해금 체크.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › 에메랄드 디오라마</div>
<h1>💎 에메랄드 디오라마 · 해금</h1>
<p class="sub">무료 DLC · 해금 {len(U['unlocks'])}개 · 게임 데이터 기준 · 지도와 캐릭터 페이지 있음</p>
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
    t=t.replace('<div class="prog">','<a class="btn-line" href="/vs/ed/chars.html">🧛 디오라마 캐릭터 보기</a> <a class="btn-line" href="/vs/ed/map.html">🗺️ 디오라마 지도 보기</a>\n<div class="prog">',1);p.write_text(t,encoding='utf-8')
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
<details class="sec" open><summary>1.0 버전 <span class="sc"></span></summary>
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

# ── 디오라마 지도 (/vs/ed/map.html) · 핀 = data/vs/ed/map.json (게임 맵 오브젝트 · tools/proto/edmap.py) · 보스 = data/vs/ed/bosses.json ──
MP=json.load(open(R/'data/vs/ed/map.json'))
BS=json.load(open(R/'data/vs/ed/bosses.json'))
ZNAME={int(k):v for k,v in MP['zones'].items()}
rowby={re.search(r'data-id="(ed-\d+)"',r).group(1):r for r in rows}
UN={u['n']:u for u in U['unlocks']}
def side(n):return '포탈 도착 화면' if n==0 else (f'오른쪽으로 {n}칸' if n>0 else f'왼쪽으로 {-n}칸')
def ufix(t):
    for a,b in FIXT.items():t=t.replace(a,b)
    return t
def ulines(ns):return [[f'#{n} {ufix(UN[n]["text"])} → 🎁 {UN[n]["reward"]}','/vs/ed/map.html#ed-%d'%n] for n in ns]
# 보스 · 관 미리보기 카드 (items.json에 EB_ · EC_ 로 넣음)
for p in MP['pins']:
    z=p['zone'];zn=ZNAME.get(z,'숨은 구역')
    if p['kind']=='boss':
        b=BS.get(p['id'],{});nm=p['label']
        ns=[u['n'] for u in U['unlocks'] if nm.split(' ')[0] in u['text']]+([38,39] if p['id']!='EME_SUSPICIOUS_OGRE' else [])
        st=f"❤️ 체력 {b.get('hp')}{' × 플레이어 레벨' if b.get('hpxlv') else ''} · ⚔️ 공격력 {b.get('power')} · 👟 속도 {b.get('speed')}"
        alt=f"📖 우화집 이름: {b['ko']}" if b.get('ko') and b['ko']!=nm else ''
        items['EB_'+p['id']]={'n':nm,'t':f'보스 · {zn}','d':re.sub(r'\s+',' ',(b.get('d') or '').replace('\\n',' ')).strip(),'p':st,'x':[alt] if alt else [],'ul':ulines(sorted(set(ns)))}
    if p['kind']=='coffin':
        ch=items.get('CH_'+p['id'],{});cn={'EME_RAPIERDUAL':2,'EME_SWORDBITE':25}.get(p['id'])
        items['EC_'+p['id']]={'n':'⚰️ '+p['label'],'t':f'관 · {zn} · {side(p["xm"])}','d':ch.get('d',''),'s':ch.get('s'),'si':ch.get('si'),'ul':ulines([cn]) if cn else [],'l':ch.get('l')}
(D/'items.json').write_text(json.dumps(items,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def pin_html(p,hub=False):
    st=f'left:{p["x"]/256*100:.2f}%;top:{p["y"]/280*100:.2f}%'
    xm=(f'<b>{"→" if p["xm"]>0 else "←"}{abs(p["xm"])}</b>' if p['xm'] else '')
    if p['kind']=='portal':
        z=int(re.search(r'biome(\d)',p['id']).group(1))
        if hub:return f'<a class="pin k-portal" style="{st}" href="#z{z}" title="{esc(ZNAME[z])}">{z}</a>'
        return f'<a class="pin k-portal" style="{st}" href="#z7" title="정션으로">🌀</a>'
    if p['kind']=='item':
        it=items.get(p['id'],{});ic=f'<img src="{it["i"]}" alt="">' if it.get('i') else '💍'
        return f'<span class="pin k-item" style="{st}" data-pop="{p["id"]}">{ic}{xm}</span>'
    if p['kind']=='coffin':return f'<span class="pin k-coffin" style="{st}" data-pop="EC_{p["id"]}">⚰️{xm}<i class="lbl">{esc(p["label"])}</i></span>'
    return f'<span class="pin k-boss" style="{st}" data-pop="EB_{p["id"]}">👹{xm}<i class="lbl">{esc(p["label"])}</i></span>'
def pin_li(p):
    if p['kind']=='portal':return f'<li>🌀 정션으로 가는 포탈 · {side(p["xm"])}</li>'
    if p['kind']=='item':return f'<li>{pop(items[p["id"]]["n"]) if p["id"] in items else esc(p["id"])} · {side(p["xm"])}</li>'
    if p['kind']=='coffin':return f'<li>⚰️ <b class="hf">관</b> · <span class="pop" data-pop="EC_{p["id"]}"><b class="hc">{esc(p["label"])}</b></span> · {side(p["xm"])}</li>'
    return f'<li>👹 보스 · <span class="pop" data-pop="EB_{p["id"]}"><b class="hb">{esc(p["label"])}</b></span> · {side(p["xm"])}</li>'
KO=['coffin','boss','portal','item']
def mapbox(z,ps,hub=False):
    return f'''<div class="map" data-z="{z}"><div class="mi"><img src="/assets/vs/ed/map/z{z}.png" alt="{esc(ZNAME[z])} 지도" loading="lazy">{''.join(pin_html(p,hub) for p in ps)}</div><button type="button" class="mfull" aria-label="크게 보기">⛶</button></div>'''
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
(R/'_src/vs/ed/map.html').write_text(f'''title: 에메랄드 디오라마 지도
desc: 뱀파이어 서바이벌 에메랄드 디오라마 지도. 관 2개 위치와 정션(허브) · 구역 6곳의 보스 · 패시브 위치를 게임 데이터로 표시.
<div class="crumb"><a href="/">홈</a> › <a href="/vs/">뱀파이어 서바이벌</a> › <a href="/vs/ed/">에메랄드 디오라마</a> › 지도</div>
<h1>🗺️ 에메랄드 디오라마 · 지도</h1>
<div class="coffins"><h2>⚰️ 관 위치</h2><ul>{cofbox}</ul></div>
<p class="sub">게임 데이터 기준 · 정션에서 포탈 번호를 누르면 그 구역으로 · 아이콘·이름을 누르면 설명 · ⛶ 누르면 크게</p>
<div class="howto"><b>칸</b> = 지도 그림 한 장. 구역은 옆으로 같은 무늬가 계속 반복됩니다. <b>→2</b> 표시는 포탈로 도착한 화면에서 <b>오른쪽으로 2장</b> 더 가면 있다는 뜻입니다.</div>
<div id="ulist" data-group="ed">
<section class="zone" id="z7"><h2>🌀 정션 (허브)</h2>
{mapbox(7,hubp,True)}
<ul class="pins">{''.join(f'<li><a href="#z{z}">{z} · {esc(ZNAME[z])}</a></li>' for z in range(1,7))}</ul>
<h3>모든 구역 해금</h3>
{chr(10).join(allr)}
</section>
{chr(10).join(zs)}
<section class="zone" id="z9"><h2>❓ 숨은 구역 · <b class="hb">숨은 오우거</b></h2>
<p>게임 데이터상 <b>정션보다 훨씬 아래쪽</b>에 숨은 오우거 자리가 따로 있습니다. 가는 법은 확인 중입니다. <span class="pop" data-pop="EB_EME_SUSPICIOUS_OGRE">👹 능력치 보기</span></p>
{chr(10).join(ogr)}
</section>
</div>
<div class="ad" data-slot="end"></div>
''',encoding='utf-8')
print('ed map',len(MP['pins']))
