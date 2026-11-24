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
