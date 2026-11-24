#!/usr/bin/env python3
"""LucKey's Lab 페이지 찍어내기 (PHP include 대신)
_src/경로.html 맨 위 두 줄:  title: 제목 / desc: 설명  → 나머지는 본문
틀(위쪽 줄·메뉴·꼬리말)을 끼워서 같은 경로에 완성 HTML을 씀."""
import pathlib,re
R=pathlib.Path(__file__).resolve().parent.parent
HEAD=(R/'tools/head.html').read_text(encoding='utf-8')
FOOT=(R/'tools/foot.html').read_text(encoding='utf-8')
for src in sorted((R/'_src').rglob('*.html')):
    rel=src.relative_to(R/'_src'); t=src.read_text(encoding='utf-8')
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
    if rel=='404.html':continue
    urls.append(BASE+(rel[:-10] if rel.endswith('index.html') else rel))
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls)+'</urlset>\n'
(R/'sitemap.xml').write_text(sm,encoding='utf-8')
(R/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n',encoding='utf-8')
print('사이트맵',len(urls))
