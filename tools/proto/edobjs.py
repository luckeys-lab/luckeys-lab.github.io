import re,json,collections,sys
txt=open('Emeralds001.prefab',encoding='utf-8').read()
docs=re.split(r'\n--- !u!',txt)
G=collections.defaultdict(dict)
for d in docs:
    m=re.search(r'm_GameObject: \{fileID: (\d+)\}',d)
    if m:
        g=G[m.group(1)]
        for k in ('m_TiledName','m_Type','m_X','m_Y','m_Width','m_Height','m_TiledId'):
            mm=re.search(rf'\n  {k}: (.*)',d)
            if mm:g[k]=mm.group(1).strip()
        for n,v in re.findall(r'- m_Name: (\w+)\n\s+m_Type: \w+\n\s+m_Value: (.*)',d):g.setdefault('p',{})[n]=v.strip()
        mm=re.search(r'm_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+)',d)
        if mm and 'pos' not in g:g['pos']=(float(mm.group(1)),float(mm.group(2)))
        mm=re.search(r'm_Father: \{fileID: (\d+)\}',d)
        if mm:g['father_tr']=mm.group(1)
    m=re.match(r'1 &(\d+)\nGameObject:',d)
    if m:
        nm=re.search(r'\n  m_Name: (.*)',d);G[m.group(1)]['name']=nm.group(1).strip() if nm else ''
objs=[dict(id=k,**v) for k,v in G.items() if v.get('m_Type') or v.get('p')]
c=collections.Counter((o.get('m_Type') or o.get('name')) for o in objs);print(c.most_common(30))
json.dump(objs,open('objs.json','w'),ensure_ascii=False)
for t in ('TELEPORT','BossSpawn','Weapon','CFF','Yellow','PlayerStart'):
    ex=[o for o in objs if o.get('m_Type')==t or o.get('name')==t][:2]
    for o in ex:print(t,{k:o.get(k) for k in ('m_X','m_Y','p','name','m_TiledName')})
