# 11/27 · 본편 캐릭터 카드: vs_cards base/character.json(이름·능력치·시작 스킬·스킨) + 블로그 캐릭터 글 순서·해금 문구(game_ref_base 005~006) + 블로그 그림(luckeys-img vs/char/CH_NNN)
import json,shutil,os,re
C=json.load(open('/tmp/cards/cards/base/character.json'));B=json.load(open('/tmp/bc/blog_chars.json'))
IMG='/home/claude/arangvsf-alt/luckeys-img/vs/char/';R='/home/claude/luckeys-lab.github.io/'
os.makedirs(R+'assets/vs/c',exist_ok=True)
nm={k:' '.join(x for x in (v['ko'].get('charName'),v['ko'].get('surname')) if x) for k,v in C.items()}
used=set();out=[]
for i,o in enumerate(B):
    n=o['name'];cand=[k for k,v in nm.items() if v==n] or [k for k,v in nm.items() if v and (v in n or n in v)]
    cand=[k for k in cand if k not in used] or (['SCOREJ'] if n=='스코레지오니' else [])
    if not cand:print('??',n);continue
    k=cand[0];used.add(k);r=C[k]['raw']
    src=IMG+'CH_%03d.png'%(i+2);img=None
    if os.path.exists(src):shutil.copy(src,R+f'assets/vs/c/{k.lower()}.png');img=f'/assets/vs/c/{k.lower()}.png'
    st={f:r[f] for f in ('maxHp','armor','regen','moveSpeed','power','area','speed','duration','amount','cooldown','luck','growth','greed','curse','magnet','revivals','rerolls','skips','banish') if f in r}
    sk=[]
    for s in r.get('skins') or []:
        sn=(C[k].get('ko') or {}).get('skins',{}) if False else None
        sk.append(s.get('name') or s.get('skinType'))
    out.append({'id':k,'ko':nm[k] or n,'blog':n,'grp':'extra' if r.get('contentGroup')=='EXTRA' else 'base','desc':(C[k].get('ko') or {}).get('description') or '','start':r.get('startingWeapon'),'stats':st,'price':r.get('price'),'skins':sk,'img':img,'un':o['un'],'tip':o['tip'],'secret':o['un'].startswith('🔒')})
json.dump(out,open(R+'data/vs/base_chars.json','w'),ensure_ascii=False,indent=0)
print(len(out),sum(1 for o in out if o['img']),sum(o['grp']=='extra' for o in out),sum(o['secret'] for o in out))
print(out[0])
