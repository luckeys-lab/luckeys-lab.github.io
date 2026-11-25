import json,re
O=json.load(open('/home/claude/edmap/objs.json'))
BAND=2240
ZN={1:'미야코시',2:'마녀 왕국 풀크라',3:'그렐론',4:'아발론',5:'요미',6:'프로비던스',7:'정션'}
BOSS={'EME_GATEBOSS_SPIRITBEAST':'스피릿 비스트','EME_GATEBOSS_DRAGON':'어스 드래곤','EME_GATEBOSS_FINALEMPEROR':'최종 황제','EME_GATEBOSS_IRONMAIDEN':'아이언 메이든','EME_GATEBOSS_SPECTER':'이와나가히메의 유령','EME_GATEBOSS_LIVINGANGUISH':'살아있는 고뇌','EME_SUSPICIOUS_OGRE':'수상한 오우거'}
CH={'EME_RAPIERDUAL':'츠나노리 미도','EME_SWORDBITE':'시그나스'}
pins=[];seen=set()
for o in sorted(O,key=lambda o:float(o.get('m_Y',0))):
    if 'm_X' not in o:continue
    x,y=float(o['m_X']),float(o['m_Y']);p=o.get('p') or {};nm=o.get('name','');t=o.get('m_Type','')
    band=int(y//BAND)+1;px,py=x/8,(y-(band-1)*BAND)/8;xm=int(p.get('xMultiplier') or 0)
    if nm.startswith('BossSpawn'):k=('boss',p.get('enemyType'))
    elif nm.startswith('CFF'):k=('coffin',p.get('cffCharacterType'))
    elif nm.startswith('Weapon'):k=('item',t)
    elif nm.startswith('Yellow'):k=('item',t)
    elif nm.startswith('TELEPORT'):
        key=p.get('teleportKey','');d=p.get('destinationBiome','')
        if d=='isDestination':continue   # 도착 지점은 빼고 출발 포탈만
        k=('portal',key)
    else:continue
    if k in seen:continue   # 요미 유령 줄 같은 반복은 한 번만
    seen.add(k)
    pins.append(dict(kind=k[0],id=k[1],zone=band,x=round(px,1),y=round(py,1),xm=xm,
      label=BOSS.get(k[1]) if k[0]=='boss' else CH.get(k[1]) if k[0]=='coffin' else k[1]))
json.dump({'zones':ZN,'pins':pins},open('/home/claude/work/edpins.json','w'),ensure_ascii=False,indent=0)
for p in pins:print(p['zone'],p['kind'],p['label'],p['x'],p['y'],'x칸',p['xm'])
