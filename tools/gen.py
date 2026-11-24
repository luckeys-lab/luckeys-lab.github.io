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
    return f'<span class="pop" data-pop="{k}">{esc(name)}</span>' if k else esc(name)

def link_names(text):
    out=esc(text)
    for n in sorted(name2id,key=len,reverse=True):
        if len(n)>=2 and n in text:
            out=out.replace(esc(n),f'<span class="pop" data-pop="{name2id[n]}">{esc(n)}</span>',1)
    return out

# ---------- 디오라마 해금 ----------
U=json.loads((D/'ed/unlocks.json').read_text(encoding='utf-8'))
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
    cbadge=' · '.join(f"{esc(c)} 🗡️{esc(CH.get(c,'?'))}" for c in chars)
    badge=f'<span class="bd bd-own">전용 · {cbadge}</span>' if chars else '<span class="bd">공통</span>'
    mp=u.get('map','');mp=mp.replace('둘다','일반·인버스').replace('❓','')
    z=u.get('zone');zt=ZONE.get(z,'') if z not in (None,'❓') else ''
    loc=' · '.join(x for x in [mp,zt] if x)
    q=f'<q>{esc(raw)}</q>'
    if fixed!=raw: q+=f'<div class="fix">바른 표기: {esc(fixed)}</div>'
    title=re.sub(r'^(캐릭터|무기|스킨|스테이지|하이퍼|유물) ','',u['reward'])
    rows.append(f'''<details class="ul" data-id="ed-{u['n']}" data-type="{t}" data-scope="{scope}">
<summary><input type="checkbox" aria-label="해금 체크"><span class="n">{u['n']}</span><span class="tt">{esc(title)}</span><span class="k">{ICON.get(t,'')} {t}</span></summary>
<div class="bdy">{q}<p>보상 → {link_names(u['reward'])}</p><p>{badge}{(' · 📍 '+esc(loc)) if loc else ''}</p></div></details>''')
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
<div id="ulist" data-group="ed">
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
