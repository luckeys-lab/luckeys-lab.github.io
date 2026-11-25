/* LucKey's Lab · 공통 기능 (메뉴 레이어 · 위로 가기 · 광고 설정) */
(function(){
  var root=document.documentElement;
  // ☰ 메뉴
  var mb=document.getElementById('menuBtn');
  function close(){root.classList.remove('menu-open');if(mb)mb.setAttribute('aria-expanded','false')}
  if(mb){
    mb.addEventListener('click',function(){
      var o=root.classList.toggle('menu-open');mb.setAttribute('aria-expanded',o?'true':'false');
    });
  }
  var dim=document.querySelector('.dim');if(dim)dim.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
  // 메뉴 묶음 펼치기
  document.querySelectorAll('.grp>button').forEach(function(b){
    b.addEventListener('click',function(){b.parentNode.classList.toggle('open')});
  });
  // 🔍 (2차에서 검색 붙임)
  var sb=document.getElementById('searchBtn');
  if(sb)sb.addEventListener('click',function(){root.classList.add('menu-open');});
  // 위로 가기
  var t=document.createElement('button');t.className='totop';t.type='button';t.setAttribute('aria-label','맨 위로');t.textContent='▲';
  document.body.appendChild(t);
  t.addEventListener('click',function(){scrollTo({top:0,behavior:'smooth'})});
  addEventListener('scroll',function(){t.classList.toggle('show',scrollY>500)},{passive:true});
  // 광고 설정 표 (data/ads.json) · 꺼져 있으면 아무것도 안 함
  fetch('/data/ads.json',{cache:'no-cache'}).then(function(r){return r.ok?r.json():null}).then(function(c){
    if(!c||!c.enabled)return;
    document.querySelectorAll('.ad[data-slot]').forEach(function(el){
      var code=c.slots&&c.slots[el.dataset.slot];
      if(code){el.innerHTML=code;el.classList.add('on')}
    });
  }).catch(function(){});
})();

/* ---- 2차: 미리보기 · 해금 체크 · 거르기 · 검색 ---- */
(function(){
  var ITEMS=null,loading=null;
  var VER=(function(){var c=document.querySelector('script[src*="site.js?v="]');return c?c.src.split('v=')[1]:''})();
  function load(){if(ITEMS)return Promise.resolve(ITEMS);if(!loading)loading=fetch('/data/vs/items.json?v='+VER).then(function(r){return r.json()}).then(function(j){ITEMS=j;mkrx(j);return j});return loading}
  function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  // 미리보기
  var box=document.createElement('div');box.id='popbox';document.body.appendChild(box);var cur=null;
  // 카드 안 이름 자동 링크 (3글자 이상 · 자기 자신 제외)
  var NRX=null,NMAP={};
  function mkrx(I){Object.keys(I).forEach(function(k){var n=I[k].n;if(!n||n.length<3||NMAP[n]||n.charAt(0)==='⚰')return;NMAP[n]=k});
    var a=Object.keys(NMAP).sort(function(x,y){return y.length-x.length}).map(function(n){return esc(n).replace(/[.*+?^${}()|[\]\\]/g,'\\$&')});NRX=a.length?new RegExp(a.join('|'),'g'):null}
  function lk(t,self){t=esc(t);if(!NRX)return t;return t.replace(NRX,function(w){var k=NMAP[w];return (k&&k!==self)?'<span class="pop in" data-pop="'+k+'">'+w+'</span>':w})}
  function card(it,self){
    var h='<span class="ty">'+esc(it.t)+'</span><b>'+(it.i?'<img class="ic big" src="'+it.i+'" alt="">':'')+esc(it.n)+'</b>'+lk(it.d,self);
    if(it.p)h+='<div class="tip">'+lk(it.p,self)+'</div>';
    if(it.s)h+='<div class="ev">'+(it.si?'<img class="ic" src="'+it.si+'" alt="">':'🗡️ ')+'시작 스킬: '+lk(it.s,self)+'</div>';
    if(it.e)h+='<div class="ev">✨ 진화: '+lk(it.e,self)+'</div>';
    if(it.f)h+='<div class="ev">⬅ 재료: '+it.f.map(function(x){return lk(x,self)}).join(' / ')+'</div>';
    if(it.u)h+='<div class="ev">🔗 이걸로 진화: '+it.u.map(function(x){return lk(x,self)}).join(' · ')+'</div>';
    if(it.sk&&it.sk.length)h+='<div class="ev">👕 스킨: '+it.sk.map(esc).join(' · ')+'</div>';
    if(it.x)it.x.forEach(function(t){h+='<div class="ev">'+esc(t)+'</div>'});
    if(it.ul&&it.ul.length)h+='<div class="uls">'+it.ul.map(function(u){return '<a href="'+u[1]+'">🔓 '+esc(u[0])+'</a>'}).join('')+'</div>';
    if(it.l)h+='<a class="go" href="'+it.l+'">자세히 →</a>';
    return h}
  // 여러 카드(가까운 핀 묶음) + 우화집 옆 카드 · PC는 나란히, 폰은 위아래(우화집 접힘)
  var hover=matchMedia('(hover:hover)').matches,tShow=null,tHide=null;
  function side(it){return it.bd?'<div class="side"><span class="ty">📖 우화집</span><b>'+esc(it.bn||it.n)+'</b>'+esc(it.bd)+'</div>':''}
  function show(el,keys){var inBox=box.contains(el),keep=inBox?{l:box.style.left,t:box.style.top}:null;load().then(function(I){var ks=keys.split(','),main='',sd='';
      ks.forEach(function(k,i){var it=I[k];if(!it)return;main+=(main?'<hr>':'')+card(it,k);sd+=side(it)});
      if(!main)return;var wide=hover&&innerWidth>=640&&sd;
      box.className=wide?'two':'';
      box.innerHTML=wide?'<div class="col">'+main+'</div><div class="col sidecol">'+sd+'</div>':main+(sd?'<details class="bdx"><summary>📖 우화집 보기</summary>'+sd+'</details>':'');
      box.style.display='flex';
      if(keep){box.style.left=keep.l;box.style.top=keep.t;cur=box;return}
      var r=el.getBoundingClientRect(),w=box.offsetWidth,h=box.offsetHeight,x,y,pin=el.classList.contains('pin');
      if(pin){x=r.right+10;if(x+w>innerWidth-8)x=r.left-w-10;if(x<8){x=Math.max(8,Math.min(r.left,innerWidth-w-8));y=r.bottom+22}else y=r.top+r.height/2-h/2}
      else{x=Math.max(8,Math.min(r.left,innerWidth-w-8));y=r.bottom+6;if(y+h>innerHeight-8)y=r.top-h-6}
      y=Math.max(8,Math.min(y,innerHeight-h-8));box.style.left=x+'px';box.style.top=y+'px';cur=el})}
  function hide(){clearTimeout(tShow);box.style.display='none';cur=null}
  document.addEventListener('click',function(e){var el=e.target.closest('[data-pop]');
    if(el){e.preventDefault();e.stopPropagation();if(cur===el)hide();else show(el,el.dataset.pop);return}
    if(!box.contains(e.target))hide()});
  if(hover){
    document.addEventListener('mouseover',function(e){var el=e.target.closest('[data-pop]');
      if(box.contains(e.target)){clearTimeout(tHide);return}
      if(!el)return;clearTimeout(tHide);if(el===cur)return;clearTimeout(tShow);tShow=setTimeout(function(){show(el,el.dataset.pop)},150)});
    document.addEventListener('mouseout',function(e){var to=e.relatedTarget;
      if(to&&(box.contains(to)||(cur&&cur.contains(to))))return;
      var el=e.target.closest('[data-pop]');if(el&&!cur){clearTimeout(tShow);return}
      if(el||box.contains(e.target)){clearTimeout(tHide);tHide=setTimeout(function(){if(!box.matches(':hover')&&!(cur&&cur.matches(':hover')))hide()},220)}});}
  addEventListener('scroll',hide,{passive:true});
  // 해금 체크 + 진행률 + 거르기
  var list=document.getElementById('ulist');
  if(list){
    var KEY='ll_chk',S={};try{S=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
    var rows=[].slice.call(list.querySelectorAll('.ul'));var fT='',fS='',only=false,LOCK=list.dataset.lock==='1',showL=false,lb=null;
    if(LOCK){lb=document.createElement('button');lb.type='button';lb.className='lockbtn';list.parentNode.insertBefore(lb,list.nextSibling);
      lb.addEventListener('click',function(){showL=!showL;apply()})}
    // 게임처럼: 먼저 필요한 해금(캐릭터·스테이지·유물)이 체크돼야 줄이 보임 · need = "a|b;c" (|는 또는, ;는 그리고)
    function locked(r){var nd=r.dataset.need;if(!LOCK||!nd)return false;return nd.split(';').some(function(g){return !g.split('|').some(function(k){return S[k]})})}
    function apply(){var n=0,nl=0;rows.forEach(function(r){var d=!!S[r.dataset.id];if(d)n++;r.classList.toggle('done',d);
        var lk=locked(r)&&!d;if(lk)nl++;r.classList.toggle('lock',lk);
        var h=(fT&&r.dataset.type!==fT)||(fS&&r.dataset.scope!==fS)||(only&&d)||(lk&&!showL);r.classList.toggle('hide',h)});
      [].forEach.call(list.querySelectorAll('.sec'),function(sec){var a=0,b=0;[].forEach.call(sec.querySelectorAll('.ul'),function(r){if(!r.classList.contains('lock'))b++;if(r.classList.contains('done'))a++});
        var sc=sec.querySelector('.sc');if(sc)sc.textContent=a+' / '+b});
      if(typeof doReco==='function')setTimeout(doReco,0);
      if(lb){lb.style.display=nl?'':'none';lb.textContent=showL?'🔓 숨은 해금 다시 접기':'🔒 아직 숨은 해금 '+nl+'개 · 게임처럼 먼저 필요한 해금을 체크하면 나타나요 (눌러서 미리 보기)'}
      var pt=document.getElementById('ptxt'),pb=document.getElementById('pbar');if(pt)pt.textContent=n+' / '+rows.length;if(pb)pb.style.width=(n/rows.length*100)+'%';
      var y=document.getElementById('yay');if(!y&&pb){y=document.createElement('div');y.id='yay';y.className='yay';y.innerHTML='<img src="/assets/mascot_yay.svg" alt=""><div><b>전부 해금! 🎉</b><br>축하합니다. 다음 열쇠도 같이 찾아봐요.</div>';var pr=pb.closest('.prog');pr.parentNode.insertBefore(y,pr)}
      if(y)y.classList.toggle('show',rows.length>0&&n===rows.length)}
    rows.forEach(function(r){var c=r.querySelector('summary input');c.checked=!!S[r.dataset.id];
      c.addEventListener('click',function(e){e.stopPropagation()});
      c.addEventListener('change',function(){if(c.checked)S[r.dataset.id]=1;else delete S[r.dataset.id];try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}apply()})});
    function bar(id,attr,set){var b=document.getElementById(id);if(!b)return;b.addEventListener('click',function(e){var t=e.target.closest('button');if(!t)return;
      [].forEach.call(b.querySelectorAll('button'),function(x){x.classList.toggle('on',x===t)});set(t.dataset[attr]);apply()})}
    bar('fType','f',function(v){fT=v});bar('fScope','s',function(v){fS=v});
    var o=document.getElementById('onlyLeft');if(o){try{o.checked=localStorage.getItem('ll_only')==='1'}catch(e){}only=o.checked;
      o.addEventListener('change',function(){only=o.checked;try{localStorage.setItem('ll_only',only?'1':'0')}catch(e){}apply()})}
    apply();
    // 💾 세이브 파일 → 자동 체크 (PC · 파일은 이 브라우저 안에서만 읽음)
    if(LOCK){var sv=document.createElement('div');sv.className='savebox';
      sv.innerHTML='<b>💾 PC 세이브로 자동 체크</b> 세이브 파일을 여기로 끌어다 놓거나 <label>📂 파일 고르기<input type="file" hidden></label><div class="path">스팀: C:\\Program Files (x86)\\Steam\\userdata\\(내 번호)\\1794680\\remote\\SaveData1~5 · 파일은 서버로 안 올라가요</div><div class="msg"></div>';
      var pg0=document.querySelector('.prog');pg0.parentNode.insertBefore(sv,pg0);
      var rd=function(f){if(!f)return;var r=new FileReader();r.onload=function(){var msg=sv.querySelector('.msg');
        try{var o=JSON.parse(r.result),A=o.Achievements||[];fetch('/data/vs/ach_keys.json?v='+VER).then(function(x){return x.json()}).then(function(K){
          var keys={};A.forEach(function(a){if(K[a])keys[K[a]]=1});
          Object.keys(K).forEach(function(a){var k=K[a];if(keys[k])S[k]=1;else delete S[k]});
          try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}
          rows.forEach(function(rw){rw.querySelector('summary input').checked=!!S[rw.dataset.id]});apply();
          msg.textContent='✅ '+(o.saveName?'「'+o.saveName+'」 ':'')+'세이브에서 해금 '+Object.keys(keys).length+'개를 읽어 체크했어요 (본편 + 디오라마 같이 반영)'})}
        catch(e){msg.textContent='⚠ 세이브 파일을 못 읽었어요. SaveData 파일이 맞는지 확인해 주세요.'}};r.readAsText(f)};
      sv.querySelector('input').addEventListener('change',function(e){rd(e.target.files[0])});
      sv.addEventListener('dragover',function(e){e.preventDefault();sv.classList.add('over')});
      sv.addEventListener('dragleave',function(){sv.classList.remove('over')});
      sv.addEventListener('drop',function(e){e.preventDefault();sv.classList.remove('over');rd(e.dataTransfer.files[0])})}
    // 🧭 꼼꼼 추천 (디오라마) · data/vs/ed/reco.json · 체크 상태로 계산
    var RECO=null,TIER=[['쉬움','🟢',2,3,false],['보통','🟡',4,8,true],['지옥','🔥',6,99,true]],curT=0,rbox=null;
    if(LOCK&&list.dataset.group==='ed'){fetch('/data/vs/ed/reco.json?v='+VER).then(function(r){return r.json()}).then(function(j){RECO=j;
      rbox=document.createElement('div');rbox.className='reco';var pg=document.querySelector('.prog');pg.parentNode.insertBefore(rbox,pg.nextSibling);
      rbox.addEventListener('click',function(e){var b=e.target.closest('[data-t]');if(b){curT=+b.dataset.t;doReco();return}
        var a=e.target.closest('[data-go]');if(a){location.hash='';location.hash=a.dataset.go}});doReco()})}
    function doReco(){if(!RECO||!rbox)return;var has=function(k){return !!S[k]},inv=has(RECO.inv),T=TIER[curT],res=[];
      var vis=rows.filter(function(r){return !S[r.dataset.id]&&!r.classList.contains('lock')&&RECO.rows[r.dataset.id]});
      RECO.opts.forEach(function(o){if(!o.need.every(has))return;[0,1].forEach(function(md){if(md&&!inv)return;var L=[];
        vis.forEach(function(r){var id=r.dataset.id,R=RECO.rows[id];if(R.inv&&!md)return;if(R.ch.length&&R.ch.indexOf(o.c)<0)return;
          var sc=R.sc,lk=false,st=false;if(R.f){if(R.f===o.w)st=true;else{if(RECO.wun[R.f]&&!has(RECO.wun[R.f]))return;lk=true;sc+=1}}
          L.push({id:id,sc:sc,lk:lk,st:st,sp:(R.ch.length||R.inv||R.k==='coffin'||R.k==='boss')?0:1,t:r.querySelector('.tt').textContent,n:r.querySelector('.n').textContent})});
        L.sort(function(a,b){return (b.st-a.st)||(a.sp-b.sp)||(a.sc-b.sc)});var pk=[],tot=0;
        L.forEach(function(x){if(pk.length>=T[2]||tot+x.sc>T[3]||(x.lk&&!T[4]))return;pk.push(x);tot+=x.sc});
        if(pk.length)res.push({o:o,md:md,pk:pk,tot:tot,ns:pk.filter(function(x){return x.st}).length})})});
      res.sort(function(a,b){return (b.pk.length-a.pk.length)||(b.ns-a.ns)||(a.tot-b.tot)});var seen={},top=[];
      res.forEach(function(r){var k=r.o.c;if(seen[k]||top.length>=2)return;seen[k]=1;top.push(r)});
      var h='<div class="rh"><b>🧭 다음 판 추천</b><span>'+TIER.map(function(t,i){return '<button type="button" data-t="'+i+'" class="'+(i===curT?'on':'')+'">'+t[1]+' '+t[0]+'</button>'}).join('')+'</span></div>';
      if(!top.length)h+='<p class="rn">지금 체크 상태로는 추천할 판이 없어요. 위에서부터 해금을 체크해 보세요.</p>';
      top.forEach(function(r){var o=r.o;h+='<div class="rc">'+(o.ci?'<img class="sp" src="'+o.ci+'" alt="">':'')+'<div>'+'<div class="rt"><b>'+esc(o.cn)+'</b>'+(o.c==='ANY'?' (본편 캐릭터도 OK)':' · 스킨 '+esc(o.sk))+' · '+(r.md?'🔁 인버스':'일반')+'</div>'+(o.c==='ANY'?'':'<div class="rw">'+(o.wi?'<img class="ic" src="'+o.wi+'" alt="">':'🗡️ ')+'시작 스킬 '+esc(o.wn)+'</div>')+'<ul>'+
        r.pk.map(function(x){return '<li><a data-go="'+x.id+'">#'+x.n+' '+esc(x.t)+'</a>'+(x.st?' <em class="st">🗡️ 시작 스킬</em>':'')+(x.lk?' <em class="lk">🎲 상자 운</em>':'')+'</li>'}).join('')+'</ul></div></div>'});
      rbox.innerHTML=h}
    function goHash(){var h=location.hash.replace('#','');if(!h)return;var t=document.querySelector('[data-id="'+h+'"]');if(!t)return;
      if(t.classList.contains('hide')){showL=true;fT='';fS='';only=false;apply()}t.open=true;var sc=t.closest('.sec');if(sc)sc.open=true;t.scrollIntoView({block:'center'})}
    goHash();window.addEventListener('hashchange',goHash);
  }
  // 지도 크게 보기 (⛶ 또는 빈 곳 탭)
  [].forEach.call(document.querySelectorAll('.map'),function(m){
    function tog(on){m.classList.toggle('full',on);document.body.classList.toggle('noscroll',on)}
    m.querySelector('.mfull').addEventListener('click',function(e){e.stopPropagation();tog(!m.classList.contains('full'))});
    m.addEventListener('click',function(e){if(e.target.closest('.pin'))return;if(m.classList.contains('full')&&!e.target.closest('.mi'))tog(false);else if(!m.classList.contains('full')&&e.target.tagName==='IMG')tog(true)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')tog(false)});
    m.querySelectorAll('a.pin').forEach(function(a){a.addEventListener('click',function(){tog(false)})});
  });
  // 검색
  var q=document.getElementById('sq'),res=document.getElementById('sres');
  var PAGES=[['본편 해금 213개','/vs/base/unlocks.html'],['디오라마 캐릭터','/vs/ed/chars.html'],['에메랄드 디오라마 해금 41개','/vs/ed/'],['에메랄드 디오라마 지도','/vs/ed/map.html'],['본편 진화 조합','/vs/evo.html'],['뱀파이어 서바이벌','/vs/'],['전체 글','/all.html']];
  var sb=document.getElementById('searchBtn');if(sb&&q)sb.addEventListener('click',function(){setTimeout(function(){q.focus()},150)});
  if(q)q.addEventListener('input',function(){var v=q.value.trim().replace(/\s/g,'');if(!v){res.innerHTML='';return}
    load().then(function(I){var out=[];PAGES.forEach(function(p){if(p[0].replace(/\s/g,'').indexOf(v)>=0)out.push('<a href="'+p[1]+'">📄 '+esc(p[0])+'</a>')});
      Object.keys(I).forEach(function(k){var it=I[k];if(out.length<30&&it.n.replace(/\s/g,'').indexOf(v)>=0)out.push('<span class="pop" data-pop="'+k+'">'+(it.i?'<img class="ic" src="'+it.i+'" alt="">':'')+esc(it.n)+'<small>'+esc(it.t)+'</small></span>')});
      res.innerHTML=out.join('')||'<span>찾는 게 없어요</span>'})});
})();
