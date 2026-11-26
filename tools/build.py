#!/usr/bin/env python3
"""LucKey's Lab 페이지 찍어내기 (PHP include 대신)
_src/경로.html 맨 위 두 줄:  title: 제목 / desc: 설명  → 나머지는 본문
틀(위쪽 줄·메뉴·꼬리말)을 끼워서 같은 경로에 완성 HTML을 씀."""
import pathlib,re
R=pathlib.Path(__file__).resolve().parent.parent
HEAD=(R/'tools/head.html').read_text(encoding='utf-8')
FOOT=(R/'tools/foot.html').read_text(encoding='utf-8')
# 캐시 번호 자동: css·js·items.json 내용이 바뀌면 ?v= 도 자동으로 바뀜 (손으로 안 올려도 됨)
import hashlib
V=hashlib.md5(b''.join((R/f).read_bytes() for f in ('assets/site.css','assets/site.js','data/vs/items.json','data/free.json','data/vs/breco.json','data/vs/ed/rbar.json'))).hexdigest()[:8]
HEAD=re.sub(r'site\.css\?v=\w+','site.css?v='+V,HEAD);FOOT=re.sub(r'site\.js\?v=\w+','site.js?v='+V,FOOT)
# [[이름]] 태그 → 카드 링크 (카드집 이름으로 찾음 · 캐릭터는 앞 이름만 써도 됨)
import json,html as _h
ITEMS=json.loads((R/'data/vs/items.json').read_text(encoding='utf-8'))
TAG={}
for k,it in ITEMS.items():TAG.setdefault(it['n'],k)
for k,it in ITEMS.items():
    if k.startswith('CH_'):
        f=it['n'].split(' ')[0]
        if f and sum(1 for x in ITEMS.values() if x['n'].split(' ')[0]==f)==1:TAG.setdefault(f,k)
TCLS=lambda t:'hb' if t.startswith('보스') else 'hc' if t.startswith('캐릭터') else 'hi'
MISS=set()
def tag(m):
    w=m.group(1).strip();k=TAG.get(w)
    if not k:MISS.add(w);return _h.escape(w)
    it=ITEMS[k];ic=f'<img class="ic" src="{it["i"]}" alt="">' if it.get('i') else ''
    return f'<span class="pop tg {TCLS(it.get("t",""))}" data-pop="{k}">{ic}{_h.escape(w)}</span>'
for src in sorted((R/'_src').rglob('*.html')):
    rel=src.relative_to(R/'_src'); t=src.read_text(encoding='utf-8')
    t=re.sub(r'\[\[([^\]]+)\]\]',tag,t)
    meta={};lines=t.split('\n')
    while lines and re.match(r'^(title|desc):',lines[0]):
        k,v=lines.pop(0).split(':',1);meta[k]=v.strip()
    title=meta.get('title',"LucKey's Lab");desc=meta.get('desc','게임 공략 연구소')
    full=f"{title} · LucKey's Lab" if title!="LucKey's Lab" else "LucKey's Lab · 게임 공략 연구소"
    out=HEAD.replace('{{TITLE}}',full).replace('{{DESC}}',desc)+'\n'.join(lines)+FOOT
    dst=R/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(out,encoding='utf-8');print('찍음',rel)

# 사이트맵 + robots.txt (검색엔진용, 404는 제외)
import datetime
BASE='https://luckeys-lab.github.io/';today=datetime.date.today().isoformat()
urls=[]
for src in sorted((R/'_src').rglob('*.html')):
    rel=src.relative_to(R/'_src').as_posix()
    if rel=='404.html' or rel.startswith('tools/'):continue   # 테스트 도구는 검색 등록 안 함
    urls.append(BASE+(rel[:-10] if rel.endswith('index.html') else rel))
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)+'</urlset>\n'
(R/'sitemap.xml').write_text(sm,encoding='utf-8')
(R/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n',encoding='utf-8')
print('사이트맵',len(urls))
if MISS:print('⚠ 못 찾은 이름:',', '.join(sorted(MISS)))
