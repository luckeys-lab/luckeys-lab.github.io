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
  var lx=document.querySelector('.layer .lx');if(lx)lx.addEventListener('click',close);
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
  var dk=document.getElementById('dock');(dk||document.body).appendChild(t);   // 오른쪽 아래 한 곳: ☰ → 🧭 → (빈 칸) → ▲
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
      if(!main)return;var wide=hover&&innerWidth>=640&&sd;main='<button type="button" class="pbx" aria-label="닫기">✕</button>'+main;
      box.className=wide?'two':'';
      box.innerHTML=wide?'<div class="col">'+main+'</div><div class="col sidecol">'+sd+'</div>':main+(sd?'<details class="bdx"><summary>📖 우화집 보기</summary>'+sd+'</details>':'');
      box.style.display='flex';
      if(keep){box.style.left=keep.l;box.style.top=keep.t;cur=box;return}
      var r=el.getBoundingClientRect(),w=box.offsetWidth,h=box.offsetHeight,x,y,pin=el.classList.contains('pin');
      if(pin){x=r.right+10;if(x+w>innerWidth-8)x=r.left-w-10;if(x<8){x=Math.max(8,Math.min(r.left,innerWidth-w-8));y=r.bottom+22}else y=r.top+r.height/2-h/2}
      else{x=Math.max(8,Math.min(r.left,innerWidth-w-8));y=r.bottom+6;if(y+h>innerHeight-8)y=r.top-h-6}
      y=Math.max(8,Math.min(y,innerHeight-h-8));box.style.left=x+'px';box.style.top=y+'px';cur=el})}
  function hide(){clearTimeout(tShow);box.style.display='none';cur=null}
  document.addEventListener('keydown',function(e){if(e.key==='Escape')hide()});
  box.addEventListener('click',function(e){if(e.target.closest('.pbx')){e.stopPropagation();hide()}});
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
  // 🎁 이번주 무료게임: 지금 시각으로 지금/곧/지난 분류 + 남은 시간 (11/26)
  var KST=function(d){return new Date(d).toLocaleString('ko-KR',{timeZone:'Asia/Seoul',month:'numeric',day:'numeric',weekday:'short',hour:'numeric',minute:'2-digit'})};
  var left=function(ms){var m=Math.max(0,Math.floor(ms/60000)),d=Math.floor(m/1440),h=Math.floor(m%1440/60),mi=m%60;return d?d+'일 '+h+'시간':h?h+'시간 '+mi+'분':mi+'분'};
  var fb=document.getElementById('freebox');
  if(fb){var put=function(){var now=Date.now(),L={};['now','next','past'].forEach(function(k){L[k]=fb.querySelector('.fgl[data-k="'+k+'"]')});
      [].forEach.call(fb.querySelectorAll('.fg'),function(c){var s=Date.parse(c.dataset.start),e=Date.parse(c.dataset.end),k=now<s?'next':now<e?'now':'past';L[k].appendChild(c);
        c.className='fg '+k;var t=c.querySelector('.fgt'),d=c.querySelector('.fgd');
        if(k==='now'){t.textContent='⏰ '+left(e-now)+' 남음';d.innerHTML='🟢 <b>'+KST(e)+'</b>까지 무료'}
        else if(k==='next'){t.textContent='⏳ '+left(s-now)+' 뒤 시작';d.innerHTML='⏳ <b>'+KST(s)+'</b>부터 <b>'+KST(e)+'</b>까지'}
        else{t.textContent='종료';d.textContent='📜 '+KST(s)+' ~ '+KST(e)}});
      ['now','next'].forEach(function(k){var h=fb.querySelector('.fh[data-k="'+k+'"]');if(h)h.style.display=L[k].children.length?'':'none'});
      var p=fb.querySelector('.fpast');if(p)p.style.display=L.past.children.length?'':'none'};
    put();setInterval(put,60000);var u=document.querySelector('.fupd');if(u)u.textContent=KST(u.dataset.t)}
  var f1=document.getElementById('freeone');
  if(f1)fetch('/data/free.json?v='+VER).then(function(r){return r.json()}).then(function(j){var now=Date.now(),g=j.games.filter(function(x){return Date.parse(x.start)<=now&&now<Date.parse(x.end)});
    if(g.length)f1.textContent=g[0].title+(g.length>1?' 외 '+(g.length-1)+'개':'')+' · '+left(Date.parse(g[0].end)-now)+' 남음'}).catch(function(){});
  // 🧭 추천 범위 ON/OFF (11/27) · ll_rgrp · 처음엔 본편만
  var GRPN={base:'🧛 본편',extra:'➕ 추가',ed:'💎 디오라마'};
  var getG=function(){try{var g=JSON.parse(localStorage.getItem('ll_rgrp')||'null');if(g)return g}catch(e){}return {base:1}};
  var setG=function(g){try{localStorage.setItem('ll_rgrp',JSON.stringify(g))}catch(e){}try{document.dispatchEvent(new CustomEvent('llchk',{detail:'grp'}))}catch(e){}};
  var swDraw=function(){var G=getG();[].forEach.call(document.querySelectorAll('.rsw[data-grp]'),function(r){var on=!!G[r.dataset.grp];r.classList.toggle('on',on);var b=r.querySelector('.sw');b.setAttribute('aria-checked',on?'true':'false')})};
  document.addEventListener('click',function(e){var b=e.target.closest('.rsw .sw');if(!b)return;var k=b.closest('.rsw').dataset.grp,G=getG();if(G[k])delete G[k];else G[k]=1;setG(G);swDraw()});
  swDraw();document.addEventListener('llchk',function(e){if(e.detail==='grp'||e.detail==='save')swDraw()});
  // 🗂 콘텐츠 틀: 왼쪽 DLC 탭 (11/26) · #base #ed … · 다른 콘텐츠로 가도 같은 탭(ll_tab)
  var CP=document.querySelector('.cp');
  function cpCount(){if(!CP)return;var X=null,C=false;try{X=JSON.parse(localStorage.getItem('ll_extra')||'null');C=localStorage.getItem('ll_chk')&&localStorage.getItem('ll_chk')!=='{}'}catch(e){}
    [].forEach.call(CP.querySelectorAll('.cpt'),function(p){var b=CP.querySelector('.cpt-b[data-tab="'+p.dataset.tab+'"] .cn'),t='',its=p.querySelectorAll('[data-col],[data-kill],[data-ch],[data-evo]');
      if(its.length){var kl=p.querySelector('[data-kill]');t=(X||(C&&!kl))?p.querySelectorAll('.sok').length+' / '+its.length:''+its.length}
      else{var a=0,n=0;[].forEach.call(p.querySelectorAll('.ul'),function(r){if(r.classList.contains('lock'))return;n++;if(r.classList.contains('done'))a++});if(n)t=a+' / '+n}
      if(b)b.textContent=t;if(p.classList.contains('on')){var c=CP.querySelector('.cpc');if(c)c.textContent=t}})}
  if(CP){var tabs=[].slice.call(CP.querySelectorAll('.cpt-b[data-tab]')),pans=[].slice.call(CP.querySelectorAll('.cpt'));
    var act=function(k,save){var b=tabs.filter(function(x){return x.dataset.tab===k})[0];if(!b)return false;
      tabs.forEach(function(x){x.classList.toggle('on',x===b)});pans.forEach(function(p){p.classList.toggle('on',p.dataset.tab===k)});
      var p=CP.querySelector('.cpt[data-tab="'+k+'"]');CP.querySelector('.cpn').textContent=p?'· '+p.dataset.lb:'';CP.style.setProperty('--tc',b.style.getPropertyValue('--tc'));
      var sd=b.parentNode;if(sd.scrollWidth>sd.clientWidth)sd.scrollLeft=b.offsetLeft-sd.clientWidth/2+b.offsetWidth/2;
      if(save){try{localStorage.setItem('ll_tab',k)}catch(e){}}cpCount();return true};
    var fromHash=function(){var h=decodeURIComponent(location.hash.slice(1)).replace(/^sec-/,'');if(!h)return false;if(act(h,true))return true;
      var el=document.getElementById(h)||document.querySelector('[data-id="'+h+'"]'),p=el&&el.closest('.cpt');if(p){act(p.dataset.tab,true);return true}return false};
    if(!fromHash()){var st=null;try{st=localStorage.getItem('ll_tab')}catch(e){}if(!(st&&act(st)))act(tabs[0].dataset.tab)}
    addEventListener('hashchange',fromHash);
    tabs.forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();act(b.dataset.tab,true);try{history.replaceState(null,'','#'+b.dataset.tab)}catch(x){}
      var r=CP.getBoundingClientRect();if(r.top<0)scrollTo({top:scrollY+r.top-56})})});
    document.addEventListener('llchk',function(){setTimeout(cpCount,0)})}
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
        var sc=sec.querySelector('.sc');if(sc)sc.textContent=a+' / '+b});cpCount();
      try{document.dispatchEvent(new CustomEvent('llchk',{detail:'list'}))}catch(e){}
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
    document.addEventListener('llchk',function(e){if(e.detail!=='bar'&&e.detail!=='save')return;try{S=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(x){}
      rows.forEach(function(rw){rw.querySelector('summary input').checked=!!S[rw.dataset.id]});apply()});
    // 🧭 추천 순서 ↔ 📜 게임 순서 (본편 줄만 · 번호는 게임 순서 그대로)
    // 정렬: 🎮 게임 순서(기본) / 🧭 추천 순서 · 칸마다 추천 스위치 바로 아래 (11/27 제이)
    var om='game';try{om=localStorage.getItem('ll_order')||'game'}catch(e){}
    var reord=function(){[].forEach.call(list.querySelectorAll('.sec'),function(sec){var rs=[].slice.call(sec.querySelectorAll(':scope > .ul[data-gi]'));if(!rs.length)return;
        rs.sort(function(a,b){return om==='game'?(a.dataset.gi-b.dataset.gi):(a.dataset.ord-b.dataset.ord)});rs.forEach(function(r){sec.appendChild(r)})});
      [].forEach.call(document.querySelectorAll('.lord [data-o]'),function(b){b.classList.toggle('on',b.dataset.o===om)})};
    document.addEventListener('click',function(e){var b=e.target.closest('.lord [data-o]');if(!b)return;om=b.dataset.o;try{localStorage.setItem('ll_order',om)}catch(x){}reord()});
    if(document.querySelector('.lord'))reord();
    // 🧭 지금 추천 줄을 그 칸 맨 위로 (11/27 제이: 추천이랑 목록 정렬 맞추기)
    rows.forEach(function(r,i){r.dataset.oi=i});
    document.addEventListener('llreco',function(e){[].forEach.call(list.querySelectorAll('.rpinh'),function(x){x.remove()});[].forEach.call(list.querySelectorAll('.ul.rpin'),function(x){x.classList.remove('rpin')});
      [].forEach.call(list.querySelectorAll('.sec'),function(sec){[].slice.call(sec.querySelectorAll(':scope > .ul')).sort(function(a,b){return a.dataset.oi-b.dataset.oi}).forEach(function(r){sec.appendChild(r)})});reord();
      e.detail.slice().reverse().forEach(function(g){var by={};g.ids.forEach(function(id){var r=list.querySelector('.ul[data-id="'+id+'"]');if(!r)return;var sec=r.closest('.sec');(by[sec.id]=by[sec.id]||{sec:sec,rows:[]}).rows.push(r)});
        Object.keys(by).forEach(function(k){var sec=by[k].sec,anc=sec.querySelector('.lctl');anc=anc?anc.nextSibling:sec.firstChild;var h=document.createElement('div');h.className='rpinh';h.innerHTML='🧭 지금 추천 · <b>'+esc(g.lb)+'</b>';
          sec.insertBefore(h,anc);var at=h.nextSibling;by[k].rows.forEach(function(r){r.classList.add('rpin');sec.insertBefore(r,at)})})})});
    // 🔍 번호·이름으로 찾기 (그 칸 안에서) · 숫자면 번호 그대로, 글자면 이름에 들어간 줄
    document.addEventListener('input',function(e){var q=e.target.closest('.lfind');if(!q)return;var sec=q.closest('.sec'),v=q.value.trim().replace(/^[#💎]+/,'');
      [].forEach.call(sec.querySelectorAll('.ul'),function(r){var hit=!v||(/^\d+$/.test(v)?(r.querySelector('.n')||{}).textContent.replace(/\D/g,'')===v:r.textContent.indexOf(v)>=0);r.classList.toggle('qhide',!hit);if(v&&hit)r.classList.remove('hide')});
      if(!v)apply()});
    function goHash(){var h=location.hash.replace('#','');if(!h)return;var t=document.querySelector('[data-id="'+h+'"]');if(!t)return;
      if(t.classList.contains('hide')){showL=true;fT='';fS='';only=false;apply()}t.open=true;var sc=t.closest('.sec');if(sc)sc.open=true;t.scrollIntoView({block:'center'})}
    goHash();window.addEventListener('hashchange',goHash);
  }
  // 💾 세이브 → 체크 (공통) · 파일 핸들 연결(크롬·엣지)이면 다시 고르지 않고 최신 세이브를 다시 읽음
  var SAVE={
    apply:function(txt){var o=JSON.parse(txt),A=o.Achievements||[];
      return Promise.all([fetch('/data/vs/ach_keys.json?v='+VER).then(function(x){return x.json()}),fetch('/data/vs/secret_keys.json?v='+VER).then(function(x){return x.json()})]).then(function(KK){
        var K=KK[0],SK=KK[1],AL={},SL={};A.forEach(function(a){AL[String(a).toLowerCase()]=1});(o.Secrets||[]).forEach(function(a){SL[String(a).toLowerCase()]=1});   // 대소문자 무시 (GetMagiStoneToLevel7)
        var S={};try{S=JSON.parse(localStorage.getItem('ll_chk')||'{}')}catch(e){}
        var r={nb:0,tb:0,ne:0,te:0,nd:0,td:0,ns:0,ts:SK.length,name:o.saveName||''};
        Object.keys(K).forEach(function(a){var k=K[a],ok=!!AL[a.toLowerCase()];if(/^b-/.test(k)){r.tb++;if(ok)r.nb++}else if(/^ed-/.test(k)){r.te++;if(ok)r.ne++}else{r.td++;if(ok)r.nd++}if(ok)S[k]=1;else delete S[k]});
        SK.forEach(function(id){if(SL[id.toLowerCase()]){S['s-'+id]=1;r.ns++}else delete S['s-'+id]});
        try{localStorage.setItem('ll_chk',JSON.stringify(S));localStorage.setItem('ll_saveinfo',JSON.stringify({t:Date.now(),name:r.name}))}catch(e){}
        var X={cw:(o.CollectedWeapons||[]).concat(o.CollectedItems||[]),kc:{},uc:o.UnlockedCharacters||[],bc:o.BoughtCharacters||[]};
        var KC=o.KillCount||{};Object.keys(KC).forEach(function(k){if(/^EME_/.test(k))X.kc[k]=KC[k]});   // 지금은 디오라마 몹만 (본편은 우화집 만들 때)
        try{localStorage.setItem('ll_extra',JSON.stringify(X))}catch(e){}
        try{document.dispatchEvent(new CustomEvent('llchk',{detail:'save'}))}catch(e){}return r})},
    db:function(){return new Promise(function(ok,no){if(!window.indexedDB)return no();var q=indexedDB.open('ll',1);q.onupgradeneeded=function(){q.result.createObjectStore('h')};q.onsuccess=function(){ok(q.result)};q.onerror=no})},
    getH:function(){return SAVE.db().then(function(d){return new Promise(function(ok){var t=d.transaction('h').objectStore('h').get('save');t.onsuccess=function(){ok(t.result||null)};t.onerror=function(){ok(null)}})}).catch(function(){return null})},
    setH:function(h){return SAVE.db().then(function(d){d.transaction('h','readwrite').objectStore('h').put(h,'save')})},
    // ask=true면 권한을 물어봄(버튼 클릭 때만) · last보다 새 파일일 때만 반영(force면 항상)
    reread:function(ask,force){return SAVE.getH().then(function(h){if(!h)return null;
      var go=function(){return h.getFile().then(function(f){var last=+(localStorage.getItem('ll_savemod')||0);if(!force&&f.lastModified<=last)return {same:true};
        return f.text().then(SAVE.apply).then(function(r){try{localStorage.setItem('ll_savemod',f.lastModified)}catch(e){}r.mod=f.lastModified;return r})})};
      return h.queryPermission({mode:'read'}).then(function(p){if(p==='granted')return go();if(!ask)return {need:true};
        return h.requestPermission({mode:'read'}).then(function(p2){return p2==='granted'?go():{need:true}})})})}};
  var hhmm=function(t){var d=new Date(t);return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)};
  var stool=document.getElementById('savetool');
  if(stool){var msg=stool.querySelector('.msg');
    var show=function(r){msg.innerHTML='✅ '+(r.name?'「'+esc(r.name)+'」 ':'')+'세이브를 읽어 체크했어요'+(r.mod?' · 게임 저장 '+hhmm(r.mod):'')+'<br>🔓 <a href="/vs/unlocks.html">본편 해금 '+r.nb+' / '+r.tb+'</a> · 💎 <a href="/vs/unlocks.html#sec-ed">디오라마 해금 '+r.ne+' / '+r.te+'</a> · 🌙 <a href="/vs/unlocks.html#ms">다른 DLC 해금 '+r.nd+' / '+r.td+'</a> · 🤫 <a href="/vs/secrets.html">비밀 '+r.ns+' / '+r.ts+'</a><br><button type="button" class="tqr fgbtn">🔖 저장 · 폰으로 보내기</button> <small>링크·QR로 저장 · 폰 카메라로 찍으면 폰에서도 같은 체크</small>'};
    var fail=function(){msg.textContent='⚠ 세이브 파일을 못 읽었어요. SaveData 파일이 맞는지 확인해 주세요.'};
    var rd=function(f){if(!f)return;f.text().then(SAVE.apply).then(show).catch(fail)};
    stool.querySelector('input').addEventListener('change',function(e){rd(e.target.files[0]);e.target.value=''});   // 같은 파일을 다시 골라도 읽히게
    stool.addEventListener('dragover',function(e){e.preventDefault();stool.classList.add('over')});
    stool.addEventListener('dragleave',function(){stool.classList.remove('over')});
    stool.addEventListener('drop',function(e){e.preventDefault();stool.classList.remove('over');rd(e.dataTransfer.files[0])});
    var cb=document.getElementById('saveconn');
    if(cb){if(!window.showOpenFilePicker){cb.disabled=true;cb.textContent='📌 연결은 크롬·엣지(PC)에서만 돼요'}
      cb.addEventListener('click',function(){window.showOpenFilePicker({multiple:false}).then(function(hs){var h=hs[0];return SAVE.setH(h).then(function(){return h.getFile()})})
        .then(function(f){return f.text().then(SAVE.apply).then(function(r){try{localStorage.setItem('ll_savemod',f.lastModified)}catch(e){}r.mod=f.lastModified;show(r);msg.innerHTML+='<br>📌 연결했어요. 이제 위쪽 띠의 🔄 버튼이나, 사이트로 돌아올 때 자동으로 최신 세이브를 읽어요.'})}).catch(function(e){if(e&&e.name!=='AbortError')fail()})});
      SAVE.getH().then(function(h){if(h){var i=document.getElementById('saveinfo');if(i)i.textContent='📌 연결된 세이브: '+h.name}})}}
  // 사이트로 돌아올 때(탭 다시 보기) 연결된 세이브가 바뀌었으면 자동으로 다시 읽기
  // 🔄 세이브 버튼 (버튼 모음 빈 칸) · 연결된 세이브가 있을 때만 · 크롬이 다시 허락을 원하면 "!" 표시
  var sbtn=null,gap=document.querySelector('.dock .dk-gap');
  var sflash=function(t){if(!sbtn)return;sbtn.querySelector('i').textContent=t;sbtn.classList.add('msg');clearTimeout(sbtn._t);sbtn._t=setTimeout(function(){sbtn.classList.remove('msg')},3500)};
  var loadFile=function(f){if(!f)return;sflash('⏳');f.text().then(SAVE.apply).then(function(r){sflash('✅ 세이브 로드 · 본편 '+r.nb+'/'+r.tb+' · 💎 '+r.ne+'/'+r.te+' · 다른 DLC '+r.nd+'/'+r.td);toast('✅ 세이브 로드 완료 · <button type="button" class="tqr">🔖 저장 · 폰으로 보내기</button>')}).catch(function(){sflash('⚠ 세이브 파일이 아니에요')})};
  var isPC=matchMedia('(hover:hover) and (pointer:fine)').matches;   // 폰·태블릿엔 세이브 로드 안 보이게 (11/26 제이)
  if(gap&&isPC&&/^\/vs\//.test(location.pathname)){
    sbtn=document.createElement('button');sbtn.type='button';sbtn.className='dk dk-save';sbtn.title='💾 세이브 파일 로드';sbtn.innerHTML='💾<i></i><input type="file" hidden>';gap.parentNode.replaceChild(sbtn,gap);
    var fin=sbtn.querySelector('input');fin.addEventListener('change',function(e){loadFile(e.target.files[0]);e.target.value=''});
    // 처음 💾 누를 때만 사용 방법 안내 (💾 옆 ? 로 다시 보기)
    var PATH='C:\\Program Files (x86)\\Steam\\userdata';
    var guide=function(){var g=document.createElement('div');g.className='sguide';
      g.innerHTML='<div class="sgc"><button type="button" class="sgx" aria-label="닫기">✕</button><h3>💾 세이브 파일 로드</h3><p>게임 세이브를 넣으면 해금 체크가 한 번에 채워져요.</p>'+
        '<h4>① 세이브 위치</h4><p><code>'+PATH+'</code> <button type="button" class="sgcp">📋 복사</button><br>→ 숫자 폴더 → <b>1794680</b> → <b>remote</b> → <b>SaveData</b> (슬롯 번호: SaveData, SaveData2 …)</p>'+
        '<h4>② 빠르게 가기</h4><p>파일 열기 창 아래 <b>"파일 이름"</b> 칸에 붙여넣고 <b>엔터</b>를 치면 그 폴더로 바로 가요.</p>'+
        '<h4>③ 알아두기</h4><p>· 지금 체크는 <b>세이브 기준으로 바뀌어요</b><br>· 다음부터는 창이 마지막 폴더를 기억해서 더 빨라요<br>· 파일은 이 브라우저 안에서만 읽어요</p>'+
        '<button type="button" class="sggo">📂 파일 고르기</button></div>';
      document.body.appendChild(g);var cl=function(){g.remove()};
      g.addEventListener('click',function(e){if(e.target===g||e.target.closest('.sgx'))cl();
        if(e.target.closest('.sgcp')){var b=e.target.closest('.sgcp');(navigator.clipboard?navigator.clipboard.writeText(PATH):Promise.reject()).then(function(){b.textContent='✅ 복사됨'}).catch(function(){b.textContent='복사 실패 · 직접 선택'})}
        if(e.target.closest('.sggo')){cl();fin.click()}});
      try{localStorage.setItem('ll_saveguide','1')}catch(e){}};
    var q=document.createElement('span');q.className='sq';q.textContent='?';q.title='사용 방법';sbtn.appendChild(q);
    sbtn.addEventListener('click',function(e){if(e.target===fin)return;if(e.target.closest('.sq')){guide();return}
      if(sbtn.classList.contains('linked')){sflash('⏳');SAVE.reread(true,true).then(function(r){sbtn.classList.remove('need');sflash(r&&r.need?'🔒 허락 필요':'✅ '+(r&&r.mod?hhmm(r.mod)+' 저장분 반영':'반영'))}).catch(function(){sflash('⚠ 못 읽음')});return}
      var seen=false;try{seen=localStorage.getItem('ll_saveguide')==='1'}catch(x){}if(!seen){guide();return}
      fin.click()});
    SAVE.getH().then(function(h){if(h){sbtn.classList.add('linked');sbtn.firstChild.textContent='🔄';sbtn.title='연결된 세이브 다시 읽기'}});
    // 페이지 아무 데나 끌어다 놓기
    var dz=document.createElement('div');dz.className='dropzone';dz.textContent='💾 여기에 놓으면 세이브 파일 로드';document.body.appendChild(dz);
    var dc=0;document.addEventListener('dragenter',function(e){if(e.dataTransfer&&[].indexOf.call(e.dataTransfer.types||[],'Files')>=0){dc++;dz.classList.add('on')}});
    document.addEventListener('dragleave',function(){if(--dc<=0){dc=0;dz.classList.remove('on')}});
    document.addEventListener('dragover',function(e){if(dz.classList.contains('on'))e.preventDefault()});
    document.addEventListener('drop',function(e){if(!dz.classList.contains('on'))return;e.preventDefault();dc=0;dz.classList.remove('on');loadFile(e.dataTransfer.files[0])})}
  var autoRe=function(){if(document.visibilityState!=='visible')return;SAVE.reread(false,false).then(function(r){if(r&&r.need&&sbtn)sbtn.classList.add('need');else if(r&&r.mod)sflash('✅ '+hhmm(r.mod)+' 저장분 반영')}).catch(function(){})};
  document.addEventListener('visibilitychange',autoRe);window.addEventListener('focus',autoRe);setTimeout(autoRe,800);
  document.addEventListener('click',function(e){var sp=e.target.closest('.spoil');if(sp){e.preventDefault();sp.classList.add('show')}});
  // 📌 상단 고정 추천 띠 · ll_chk로 계산 · 띠 안에서 펼치기/체크
  if(/^\/vs\//.test(location.pathname)){
    var HAS=false,BR=null,PEND={},TIER=[['쉬움','🟢',2,3,false],['보통','🟡',4,8,true],['지옥','🔥',6,99,true]],RB=null,RC=null,bar=null,curT=0,mode='min',openRow=null;
    var first=false;try{mode=localStorage.getItem('ll_rbar');if(!mode){mode='min';first=true}if(mode==='off')mode='min';curT=+(localStorage.getItem('ll_rtier')||0)}catch(e){}
    var getS=function(){try{return JSON.parse(localStorage.getItem('ll_chk')||'{}')}catch(e){return {}}};
    function calcEd(S){var has=function(k){return !!S[k]},inv=[].concat(RC.inv).every(has),T=TIER[curT],res=[];
      var vis=Object.keys(RB).filter(function(k){return !S[k]&&RB[k].need.every(function(g){return g.some(has)})&&RC.rows[k]});
      RC.opts.forEach(function(o){if(!o.need.every(has))return;[0,1].forEach(function(md){if(md&&!inv)return;var L=[];
        vis.forEach(function(id){var R=RC.rows[id];if(R.inv&&!md)return;if(R.ch.length&&R.ch.indexOf(o.c)<0)return;
          var sc=R.sc,lk=false,st=false;if(R.f){if(R.f===o.w)st=true;else{if(RC.wun[R.f]&&!has(RC.wun[R.f]))return;lk=true;sc+=1}}
          L.push({id:id,sc:sc,lk:lk,st:st,sp:(R.ch.length||R.inv||R.k==='coffin'||R.k==='boss')?0:1})});
        L.sort(function(a,b){return (b.st-a.st)||(a.sp-b.sp)||(a.sc-b.sc)});var pk=[],tot=0;
        L.forEach(function(x){if(pk.length>=T[2]||tot+x.sc>T[3]||(x.lk&&!T[4]))return;pk.push(x);tot+=x.sc});
        if(pk.length)res.push({o:o,md:md,pk:pk,tot:tot,ns:pk.filter(function(x){return x.st}).length})})});
      return res}
    // 🧛 본편 v1: 캐릭터 1 + 스테이지 1 조합마다 한 판에 되는 해금 묶기 (11/27)
    function calcBase(S,G){var has=function(k){return !!S[k]},T=TIER[curT],res=[],B=BR,ok=function(nd){return !nd.length||nd.some(has)};
      var n=Object.keys(S).length,early=n<40;
      var vis=Object.keys(B.rows).filter(function(k){var R=B.rows[k];return G[R.g]&&!S[k]&&RB[k]&&RB[k].need.every(function(g){return g.some(has)})});
      var CH=B.chars.filter(function(c){return ok(c.need)}),ST=B.stages.filter(function(x){return ok(x.need)}),inv=has(B.invk);
      CH.forEach(function(c){ST.forEach(function(st){var L=[];
        vis.forEach(function(id){var R=B.rows[id];if(R.nl)return;if(R.ch.length&&R.ch.indexOf(c.c)<0)return;if(R.st.length&&R.st.indexOf(st.s)<0)return;if(R.inv&&!inv)return;
          var sc=R.sc+(early&&R.sec>=1800?2:0),lk=false,stt=false,bad=false;
          R.w.forEach(function(w){if(c.w.indexOf(w)>=0)stt=true;else{var l=B.lock[w];if(l&&!l.some(has))bad=true;lk=true;sc+=1}});
          R.it.forEach(function(w){var l=B.lock[w];if(l&&l.indexOf(id)<0&&!l.some(has))bad=true});if(bad)return;
          L.push({id:id,sc:sc,lk:lk,st:stt,sp:(R.ch.length||R.st.length)?0:1})});
        L.sort(function(a,b){return (b.st-a.st)||(a.sp-b.sp)||(a.sc-b.sc)});var pk=[],tot=0;
        L.forEach(function(x){if(pk.length>=T[2]||tot+x.sc>T[3]||(x.lk&&!T[4]))return;pk.push(x);tot+=x.sc});
        if(pk.length)res.push({o:{c:'B_'+c.c,cn:c.cn,sk:'📍 '+st.sn,wn:c.wn,ci:c.ci,wi:c.wi,ms:c.ms||1},md:0,pk:pk,tot:tot,ns:pk.filter(function(x){return x.st}).length,b:1})})});
      return res}
    function calc(){var S=getS(),G=getG(),parts=[];
      if(G.ed)parts.push(calcEd(S));if((G.base||G.extra)&&BR)parts.push(calcBase(S,G));
      var srt=function(a,b){return (b.pk.length-a.pk.length)||(b.ns-a.ns)||(a.tot-b.tot)||((b.o.ms||1)-(a.o.ms||1))},seen={},top=[];
      parts.forEach(function(p){p.sort(srt)});
      parts.forEach(function(p){for(var i=0;i<p.length;i++){if(!seen[p[i].o.c]){seen[p[i].o.c]=1;top.push(p[i]);break}}});   // 켠 칸마다 1장씩
      parts.forEach(function(p){p.forEach(function(r){if(top.length>=3||seen[r.o.c])return;seen[r.o.c]=1;top.push(r)})});
      return {top:top,S:S}}
    function head(r){var o=r.o;return '<b>'+esc(o.cn)+'</b>'+(o.ms>1?' <em class="spd">👟 +'+Math.round((o.ms-1)*100)+'%</em>':'')+(o.c==='ANY'?'':' · '+esc(o.sk))+' · '+(r.md?'<span class="binv">🔄 인버스 모드</span>':'🌍 일반')}
    function draw(){if(!bar)return;var c=calc(),top=c.top,S=c.S;pinRec(top);
      var one=top.length?head(top[0])+' → '+top[0].pk.map(function(x){return (x.id.charAt(0)==='b'?'#':'💎')+RB[x.id].n}).join(' · '):'추천할 판이 없어요',cnt=top.length?top[0].pk.length:0;
      // 접힘 = 왼쪽 아래 둥근 버튼 (11/26 제이: 화면엔 페이지 내용만)
      if(mode!=='open'){bar.className='rbar fab'+(first?' hint':'');bar.innerHTML='<button type="button" class="rfab" data-m="open" title="추천 해금">🧭<span class="rlab">추천 해금</span>'+(cnt?'<i class="rcnt">'+cnt+'</i>':'')+'</button>';return}
      var h='<div class="rl"><span class="rtag">🧭 추천 해금</span><span class="rone">다음 판: '+one+'</span>'+(HAS?'<button type="button" class="rs" title="연결된 세이브를 다시 읽기">🔄 세이브</button>':'')+'<a class="rhelp" href="/vs/howto.html">❓ 사용법</a><button type="button" class="rx" data-m="min">닫기 ✕</button></div>';
      if(mode==='open'){h+='<div class="rbody"><p class="rintro">체크한 해금을 보고, <b>다음 판에 한 번에 노릴 수 있는 해금</b>을 골라 줘요. 줄을 누르면 공략과 ☑ 체크가 펼쳐져요.</p><div class="rtabs">'+TIER.map(function(t,i){return '<button type="button" data-t="'+i+'" class="'+(i===curT?'on':'')+'">'+t[1]+' '+t[0]+'</button>'}).join('')+'</div>';
        var G=getG(),gl=Object.keys(GRPN).filter(function(k){return G[k]});
        h+='<p class="rscope">추천 범위: '+(gl.length?gl.map(function(k){return '<b>'+GRPN[k]+'</b>'}).join(' · '):'<b>없음</b>')+' · <a href="/vs/unlocks.html">해금 페이지 맨 위에서 켜기/끄기</a></p>';
        if((G.base||G.extra)&&BR){var nc=BR.cum.filter(function(k){return !S[k]&&RB[k]&&RB[k].need.every(function(g){return g.some(function(x){return S[x]})})}).length;var nlc=Object.keys(BR.rows).filter(function(k){var R=BR.rows[k];return R.nl&&G[R.g]&&!S[k]&&RB[k]&&RB[k].need.every(function(g){return g.some(function(x){return S[x]})})}).length;if(nc)h+='<p class="rn">🔁 아무 판에서나 쌓이는 해금 '+nc+'개는 따로 · <a href="/vs/unlocks.html#base">해금 목록</a> · 🧛 본편 추천은 v1이라 같이 다듬는 중</p>';if(nlc)h+='<p class="rn">📍 위치를 알아야 하는 유물 찾기 '+nlc+'개는 위치 공략을 채우는 중이라 추천에서 뺐어요</p>'}
        if(!top.length&&gl.length)h+='<p class="rn">지금 체크 상태로는 추천할 판이 없어요.</p>';
        if(!gl.length)h+='<p class="rn">켜진 칸이 없어요 · 해금 페이지 각 칸 맨 위 🧭 스위치를 켜 주세요</p>';
        top.forEach(function(r){var o=r.o;h+='<div class="rc">'+(o.ci?'<img class="sp" src="'+o.ci+'" alt="">':'')+'<div class="rcb"><div class="rh2">'+head(r)+'</div>'+(o.c==='ANY'?'<div class="rw">본편 캐릭터도 OK</div>':'<div class="rw">'+(o.wi?'<img class="ic" src="'+o.wi+'" alt="">':'🗡️ ')+'시작 스킬 '+esc(o.wn)+'</div>')+'<ul>'+
          r.pk.map(function(x){var it=RB[x.id],op=openRow===x.id;return '<li><input type="checkbox" class="rq" data-q="'+x.id+'"'+(PEND[x.id]?' checked':'')+' aria-label="이번 판에 해냄"><a class="ri" data-r="'+x.id+'">'+(x.id.charAt(0)==='b'?'#':'💎')+it.n+' '+(it.th||esc(it.t))+'</a>'+(x.st?' <em class="st">🗡️ 시작 스킬</em>':'')+(x.lk?' <em class="lk">🎲 상자 운</em>':'')+
            (op?'<div class="rdet"><label class="rck"><input type="checkbox" data-c="'+x.id+'"'+(S[x.id]?' checked':'')+'> 해금 완료</label><p class="rw2">🎁 보상 → '+esc(it.rw)+'</p>'+it.g+'<a class="go" href="/vs/unlocks.html#'+x.id+'">목록에서 보기 →</a></div>':'')+'</li>'}).join('')+'</ul></div></div>'});
        var np=Object.keys(PEND).length;if(top.length)h+='<div class="rqbar">'+(np?'<button type="button" class="rqgo">✅ 체크한 '+np+'개 해금 완료</button>':'<small>판 끝나고 해낸 줄 앞 ☐ 를 눌러 모아 두고, 한 번에 완료할 수 있어요</small>')+'</div>';
        h+='</div>'}
      bar.className='rbar '+mode;bar.innerHTML=h}
    var _rp='';function pinRec(top){var sig=top.map(function(r){return r.o.c+':'+r.pk.map(function(x){return x.id}).join(',')}).join('|');if(sig===_rp)return;_rp=sig;try{document.dispatchEvent(new CustomEvent('llreco',{detail:top.map(function(r){return {lb:r.o.cn+(r.o.c==='ANY'?'':' · '+r.o.sk),ids:r.pk.map(function(x){return x.id})}})}))}catch(e){}}
    Promise.all([fetch('/data/vs/ed/rbar.json?v='+VER).then(function(r){return r.json()}),fetch('/data/vs/ed/reco.json?v='+VER).then(function(r){return r.json()}),fetch('/data/vs/breco.json?v='+VER).then(function(r){return r.json()}).catch(function(){return null})]).then(function(j){RB=j[0];RC=j[1];BR=j[2];
      bar=document.createElement('div');(document.getElementById('dkReco')||document.body).appendChild(bar);
      bar.addEventListener('click',function(e){var q=e.target.closest('.rq');if(q){if(q.checked)PEND[q.dataset.q]=1;else delete PEND[q.dataset.q];draw();return}
        if(e.target.closest('.rqgo')){var S2=getS();Object.keys(PEND).forEach(function(k){S2[k]=1});PEND={};try{localStorage.setItem('ll_chk',JSON.stringify(S2))}catch(x){}draw();try{document.dispatchEvent(new CustomEvent('llchk',{detail:'bar'}))}catch(x){}return}
        var m=e.target.closest('[data-m]'),t=e.target.closest('[data-t]'),ri=e.target.closest('.ri'),ck=e.target.closest('[data-c]');
        if(e.target.closest('.rs')){var b=e.target.closest('.rs');b.textContent='⏳';SAVE.reread(true,true).then(function(r){b.textContent=r&&r.need?'🔒 허락 필요':'✅ '+(r&&r.mod?hhmm(r.mod):'');setTimeout(draw,1500)}).catch(function(){b.textContent='⚠'});return}
        if(m){mode=m.dataset.m;try{localStorage.setItem('ll_rbar',mode)}catch(x){}draw();return}
        if(t){curT=+t.dataset.t;try{localStorage.setItem('ll_rtier',curT)}catch(x){}draw();return}
        if(ri){openRow=openRow===ri.dataset.r?null:ri.dataset.r;draw();return}
        if(ck){var S=getS();if(ck.checked)S[ck.dataset.c]=1;else delete S[ck.dataset.c];try{localStorage.setItem('ll_chk',JSON.stringify(S))}catch(x){}
          if(ck.checked)openRow=null;draw();try{document.dispatchEvent(new CustomEvent('llchk',{detail:'bar'}))}catch(x){}}});
      if(first){try{localStorage.setItem('ll_rbar','min')}catch(x){}setTimeout(function(){first=false;draw()},6000)}
      // 띠 밖을 누르거나 ESC → 접기 (펼친 채 남아 화면을 가리지 않게)
      document.addEventListener('click',function(e){if(!e.target.isConnected)return;   // 띠를 다시 그리면서 사라진 버튼 클릭 = 띠 안 클릭
        if(mode==='open'&&!bar.contains(e.target)&&!e.target.closest('#popbox')){mode='min';try{localStorage.setItem('ll_rbar',mode)}catch(x){}draw()}});
      document.addEventListener('keydown',function(e){if(e.key==='Escape'&&mode==='open'){mode='min';try{localStorage.setItem('ll_rbar',mode)}catch(x){}draw()}});
      // 카드 머리(캐릭터 이름·그림)를 눌러도 접기
      bar.addEventListener('click',function(e){if(e.target.closest('.rh2')||e.target.closest('.rc img.sp')){mode='min';try{localStorage.setItem('ll_rbar',mode)}catch(x){}draw()}});
      document.addEventListener('llchk',function(e){if(e.detail==='list'||e.detail==='save'||e.detail==='grp')draw()});
      SAVE.getH().then(function(h){HAS=!!h;draw()});draw()})}
  // 🔒 해금 표시 (11/26): ☑ 체크(모바일 OK) → 해금/미해금 · 💾 세이브 → 모음(금테)/아직(흐림) · 아무것도 없으면 전부 원래 색
  var LM=null,LMing=false;
  var showExtra=function(){var X=null,S={};try{X=JSON.parse(localStorage.getItem('ll_extra')||'null');S=JSON.parse(localStorage.getItem('ll_chk')||'{}')}catch(e){}
    var C=Object.keys(S).length>0,els=document.querySelectorAll('[data-col],[data-kill],[data-ch],[data-evo],[data-ek]');if(!els.length)return;
    if(C&&!LM){if(!LMing){LMing=true;fetch('/data/vs/lockmap.json?v='+VER).then(function(r){return r.json()}).then(function(j){LM=j;showExtra()}).catch(function(){})}if(!X)return}
    var U=function(k){return String(k).toUpperCase().replace(/^ED_/,'')},cw={},uc={},bc={};
    if(X){X.cw.forEach(function(k){cw[U(k)]=1});X.uc.forEach(function(k){uc[k]=1});X.bc.forEach(function(k){bc[k]=1})}
    var lk=function(k){var a=C&&LM&&LM[k];return !!a&&!a.some(function(x){return S[x]})};
    var T=function(el,c,v){el.classList.toggle(c,!!v)};
    [].forEach.call(document.querySelectorAll('[data-col]'),function(el){var L=lk(el.dataset.lk||('ED_'+el.dataset.col)),g=X&&cw[U(el.dataset.col)];T(el,'locked',L&&!g);T(el,'got',g);T(el,'miss',X&&!g&&!L);T(el,'sok',X?g:!L)});
    [].forEach.call(document.querySelectorAll('[data-kill]'),function(el){var n=X?(X.kc[el.dataset.kill]||0):0;T(el,'miss',X&&!n);T(el,'sok',n);var b=el.querySelector('.bkill');if(b)b.textContent=!X?'':n>0?'처치 '+n.toLocaleString():n<0?'처치함':'아직 못 잡음'});
    [].forEach.call(document.querySelectorAll('[data-ch]'),function(el){var id=el.dataset.ch,L=lk('CH_'+id)||(X&&!uc[id]);T(el,'locked',L);T(el,'unbought',X&&!L&&!bc[id]);T(el,'sok',(X||C)&&!L)});
    [].forEach.call(document.querySelectorAll('[data-ek]'),function(el){T(el,'locked',lk(el.dataset.ek))});
    [].forEach.call(document.querySelectorAll('[data-evo]'),function(el){var g=X&&cw[U(el.dataset.evo)],L=!g&&el.dataset.parts.split(',').some(function(p){return lk(p)||(X&&!cw[U(p)])});
      T(el,'got',g);T(el,'locked',L);T(el,'miss',X&&!g&&!L);T(el,'sok',X?g:!L)});
    cpCount()};
  showExtra();document.addEventListener('llchk',function(){setTimeout(showExtra,0)});
  // 📲 폰으로 보내기 (11/26): PC 체크·세이브 표시를 QR/코드 한 줄로 → 폰 카메라로 찍으면 사이트가 열리며 그대로 들어감 (게임 진행을 옮기는 게 아님)
  var SYNC={
    keys:function(){return SYNC._k||(SYNC._k=fetch('/data/vs/sync_keys.json?v='+VER).then(function(r){return r.json()}))},
    b64:function(u8){var s='';u8.forEach(function(b){s+=String.fromCharCode(b)});return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')},
    unb64:function(t){t=t.replace(/-/g,'+').replace(/_/g,'/');var s=atob(t),u=new Uint8Array(s.length);for(var i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u},
    make:function(){return SYNC.keys().then(function(K){var S={},X=null;try{S=JSON.parse(localStorage.getItem('ll_chk')||'{}');X=JSON.parse(localStorage.getItem('ll_extra')||'null')}catch(e){}
      var U=function(k){return String(k).toUpperCase().replace(/^ED_/,'')},cw={},uc={},bc={};if(X){X.cw.forEach(function(k){cw[U(k)]=1});X.uc.forEach(function(k){uc[k]=1});X.bc.forEach(function(k){bc[k]=1})}
      var u8=new Uint8Array(Math.ceil(K.length/8)),n=0;
      K.forEach(function(k,i){var v=false,p=k.indexOf(':'),t=p>0?k.slice(0,p):'',id=p>0?k.slice(p+1):k;
        if(!t)v=!!S[k];else if(t==='rg')v=!!getG()[id];else if(X){if(t==='cw')v=!!cw[U(id)];else if(t==='uc')v=!!uc[id];else if(t==='bc')v=!!bc[id];else if(t==='kc')v=!!X.kc[id]}
        if(v){u8[i>>3]|=1<<(i&7);n++}});
      var end=u8.length;while(end>0&&!u8[end-1])end--;return {code:(X?'2':'1')+SYNC.b64(u8.slice(0,end)),n:n}})},
    take:function(code){code=String(code).trim();var m=code.match(/[#&]s=([A-Za-z0-9_-]+)/);if(m)code=m[1];
      return SYNC.keys().then(function(K){var hx=code.charAt(0)==='2',u8=SYNC.unb64(code.slice(1)),S={},RG={},X=hx?{cw:[],kc:{},uc:[],bc:[]}:null,nb=0;
        K.forEach(function(k,i){if(!(u8[i>>3]&(1<<(i&7))))return;var p=k.indexOf(':'),t=p>0?k.slice(0,p):'',id=p>0?k.slice(p+1):k;
          if(!t){S[k]=1;nb++}else if(t==='rg')RG[id]=1;else if(X){if(t==='cw')X.cw.push(id.replace(/^ED_/,''));else if(t==='uc')X.uc.push(id);else if(t==='bc')X.bc.push(id);else if(t==='kc')X.kc[id]=-1}});
        try{localStorage.setItem('ll_chk',JSON.stringify(S));if(Object.keys(RG).length)localStorage.setItem('ll_rgrp',JSON.stringify(RG));if(X)localStorage.setItem('ll_extra',JSON.stringify(X));localStorage.setItem('ll_sync',String(Date.now()))}catch(e){}
        try{document.dispatchEvent(new CustomEvent('llchk',{detail:'save'}))}catch(e){}return nb})}};
  var modal=function(html){var g=document.createElement('div');g.className='sguide';g.innerHTML='<div class="sgc"><button type="button" class="sgx" aria-label="닫기">✕</button>'+html+'</div>';document.body.appendChild(g);
    g.addEventListener('click',function(e){if(e.target===g||e.target.closest('.sgx'))g.remove()});return g};
  var toast=function(t){var d=document.createElement('div');d.className='lltoast';d.innerHTML=t;document.body.appendChild(d);setTimeout(function(){d.classList.add('out')},3800);setTimeout(function(){d.remove()},4400)};
  document.addEventListener('click',function(e){if(e.target.closest('.tqr')){e.preventDefault();sendQR()}});
  // 🔖 독 버튼 (뱀서 페이지 · PC·폰 모두) · 저장 뒤로 체크가 바뀌면 작은 숫자로 "다시 저장" 알림
  var bkb=null,bkBadge=function(){if(!bkb)return;var n=nChk(),bk=null;try{bk=JSON.parse(localStorage.getItem('ll_bk')||'null')}catch(e){}
    var d=bk?n-bk.n:(n>=10?n:0),i=bkb.querySelector('b');i.textContent=d?(d>0?'+'+d:d):'';bkb.title=d?'🔖 저장한 뒤로 체크가 바뀌었어요 · 다시 저장':'🔖 내 체크 저장 · 불러오기'};
  var rs=document.getElementById('dkReco');
  if(rs&&/^\/vs\//.test(location.pathname)){bkb=document.createElement('button');bkb.type='button';bkb.className='dk dk-bk';bkb.innerHTML='🔖<b></b>';rs.parentNode.insertBefore(bkb,rs.nextSibling);
    bkb.addEventListener('click',function(){bookmark()});setTimeout(bkBadge,0);document.addEventListener('llchk',function(){setTimeout(bkBadge,0)})}
  // 📱 폰: 스크롤하는 동안 독을 흐리게 (글자 가림 줄이기 · 11/27 제이)
  if(matchMedia('(max-width:720px)').matches){var dsT=null;addEventListener('scroll',function(){document.documentElement.classList.add('dscroll');clearTimeout(dsT);dsT=setTimeout(function(){document.documentElement.classList.remove('dscroll')},700)},{passive:true})}
  // 🎁 이번주 무료게임 독 버튼 (11/27 · 사이트 전체 · 새 게임을 아직 안 봤으면 빨간 점 · 누르면 작은 창)
  var mb2=document.getElementById('menuBtn');
  if(mb2&&!document.getElementById('freebox')){var fbB=document.createElement('button');fbB.type='button';fbB.className='dk dk-free';fbB.title='🎁 이번주 무료게임';fbB.innerHTML='🎁<b></b>';mb2.parentNode.insertBefore(fbB,mb2.nextSibling);
    var FJ=null,fload=function(){return FJ?Promise.resolve(FJ):fetch('/data/free.json?v='+VER).then(function(r){return r.json()}).then(function(j){FJ=j;return j})};
    var fstate=function(j){var now=Date.now(),cur=j.games.filter(function(g){return Date.parse(g.start)<=now&&now<Date.parse(g.end)}),nx=j.games.filter(function(g){return now<Date.parse(g.start)});return {now:now,cur:cur,nx:nx}};
    var fdot=function(){fload().then(function(j){var st=fstate(j),seen=+(localStorage.getItem('ll_freeseen')||0),nw=st.cur.some(function(g){return Date.parse(g.start)>seen});fbB.classList.toggle('new',nw)}).catch(function(){})};
    fdot();
    fbB.addEventListener('click',function(){fload().then(function(j){var st=fstate(j);
      var card=function(g,k){var t=k==='cur'?'⏰ '+left(Date.parse(g.end)-st.now)+' 남음':'⏳ '+KST(g.start)+'부터';
        return '<a class="fmini" href="'+g.url+'" target="_blank" rel="noopener"><img src="'+g.img+'" alt="" referrerpolicy="no-referrer"><span><b>'+esc(g.title)+'</b><small>'+t+'</small></span><i>받기 ›</i></a>'};
      modal('<h3>🎁 이번주 무료게임</h3>'+(st.cur.length?'<p class="fmh">🟢 지금 무료 · 받으면 계속 내 것</p>'+st.cur.map(function(g){return card(g,'cur')}).join(''):'<p>지금 무료인 게임이 없어요</p>')+
        (st.nx.length?'<p class="fmh">⏳ 곧 무료</p>'+st.nx.map(function(g){return card(g,'nx')}).join(''):'')+'<p><a class="fgbtn" href="/review/free.html">전체 보기 ›</a></p>');
      try{localStorage.setItem('ll_freeseen',String(Date.now()))}catch(e){}fbB.classList.remove('new')})})}
  // 받는 쪽: 주소에 #s=코드 → 바로 반영 후 주소에서 지움
  if(/[#&]s=/.test(location.hash)){var hc=location.hash;try{history.replaceState(null,'',location.pathname+location.search)}catch(e){}
    SYNC.take(hc).then(function(n){toast('📥 저장한 체크를 불러왔어요 · ☑ '+n+'개')}).catch(function(){toast('⚠ 코드가 잘못됐어요')})}
  // 🔖 내 체크 저장 · 불러오기 (11/26 제이: 모바일 유저가 링크·QR 이미지로 백업 → 링크 누르기 / QR 사진 고르기 / 코드 붙여넣기로 복구)
  var nChk=function(){try{return Object.keys(JSON.parse(localStorage.getItem('ll_chk')||'{}')).length}catch(e){return 0}};
  var loadJS=function(src,name){return window[name]?Promise.resolve(window[name]):new Promise(function(ok,no){var sc=document.createElement('script');sc.src=src+'?v='+VER;sc.onload=function(){ok(window[name])};sc.onerror=no;document.head.appendChild(sc)})};
  var bookmark=function(tab){
    var g=modal('<h3>🔖 내 체크 저장 · 불러오기</h3><div class="bktabs"><button type="button" data-bt="save">💾 저장</button><button type="button" data-bt="load">📥 불러오기</button></div><div class="bkp" data-bt="save"></div><div class="bkp" data-bt="load"></div>');
    var ps=g.querySelector('.bkp[data-bt="save"]'),pl=g.querySelector('.bkp[data-bt="load"]');
    var show=function(t){[].forEach.call(g.querySelectorAll('[data-bt]'),function(e){e.classList.toggle('on',e.dataset.bt===t)})};
    g.querySelector('.bktabs').addEventListener('click',function(e){var b=e.target.closest('[data-bt]');if(b)show(b.dataset.bt)});
    var n=nChk(),bk=null;try{bk=JSON.parse(localStorage.getItem('ll_bk')||'null')}catch(e){}
    if(!n){ps.innerHTML='<p>아직 ☑ 체크한 게 없어요. <a href="/vs/unlocks.html">🔓 해금</a>에서 체크하고 오세요.</p>'}
    else SYNC.make().then(function(r){var url=location.origin+'/vs/unlocks.html#s='+r.code;
      var share=!isPC&&!!navigator.share;
      var qrb='<div class="qrbox"><img alt="체크 저장 QR"></div><div class="bkbtn"><button type="button" class="fgbtn bkcp">🔗 링크 복사</button><button type="button" class="fgbtn bkimg">🖼️ QR 이미지 저장</button></div><p class="note">아이폰은 QR 그림을 꾹 눌러 <b>사진에 저장</b> · 이미지는 다운로드 폴더(갤러리)에 저장돼요</p><details><summary>코드만 보기</summary><p><code class="sccode"></code></p></details>';
      ps.innerHTML='<p>지금 체크 <b>☑ '+r.n+'개</b>를 저장해요. 폰을 바꾸거나 기록을 지워도 이걸로 되살려요.</p>'+
        (share?'<button type="button" class="bkshare">📤 링크 보내기 <small>카톡 → 나와의 채팅 추천</small></button><p class="note">나중에 그 링크를 <b>누르기만</b> 하면 불러와져요 · 체크를 더 하면 다시 보내 주세요</p><details class="bkmore"><summary>다른 방법 ▾ (QR · 이미지 · 코드)</summary>'+qrb+'</details>'
          :qrb.replace('<div class="bkbtn">','<p class="note">링크를 복사해서 카톡 <b>나와의 채팅</b>에 붙여 두면, 나중에 누르기만 하면 불러와져요 · PC 화면의 QR은 폰 기본 카메라로 찍어도 돼요</p><div class="bkbtn">'));
      if(share)ps.querySelector('.bkshare').onclick=function(){navigator.share({title:"LucKey's Lab 체크 저장",text:"🔖 뱀서 체크 저장 ("+KST(Date.now())+" · ☑ "+r.n+"개) · 누르면 불러와져요",url:url}).then(function(){done();toast('📤 보냈어요')}).catch(function(){})};
      ps.querySelector('.sccode').textContent=r.code;
      var done=function(){try{localStorage.setItem('ll_bk',JSON.stringify({t:Date.now(),n:r.n}))}catch(e){}bkBadge()};
      loadJS('/assets/qrcode.min.js','qrcode').then(function(qrcode){var q=qrcode(0,'M');q.addData(url);q.make();
        var im=new Image();im.onload=function(){var c=document.createElement('canvas'),W=im.width+40,H=im.height+112,dn=new Date(),ds=dn.getFullYear()+'. '+(dn.getMonth()+1)+'. '+dn.getDate()+'.',fn='luckeys-lab-check-'+dn.getFullYear()+'-'+('0'+(dn.getMonth()+1)).slice(-2)+'-'+('0'+dn.getDate()).slice(-2)+'.png';c.width=W;c.height=H;var x=c.getContext('2d');
          x.fillStyle='#fff';x.fillRect(0,0,W,H);x.fillStyle='#1E2346';x.fillRect(0,0,W,46);x.fillStyle='#E6B84F';x.font='bold 17px sans-serif';x.textAlign='center';x.fillText("🔖 LucKey's Lab 체크 저장",W/2,29);
          x.drawImage(im,20,56);x.fillStyle='#1E2346';x.font='bold 22px sans-serif';x.fillText('📅 '+ds,W/2,H-36);x.font='14px sans-serif';x.fillText(KST(Date.now())+' · ☑ '+r.n+'개',W/2,H-12);
          var png=c.toDataURL('image/png');ps.querySelector('.qrbox img').src=png;
          ps.querySelector('.bkimg').onclick=function(){c.toBlob(function(bl){var f=new File([bl],fn,{type:'image/png'});
            var a=document.createElement('a');a.href=URL.createObjectURL(bl);a.download=fn;document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(a.href)},4000);done();toast('🖼️ '+fn+' 저장')})}};
        im.src=q.createDataURL(6,2)});
      ps.querySelector('.bkcp').onclick=function(e){var b=e.target;(navigator.clipboard?navigator.clipboard.writeText(url):Promise.reject()).then(function(){b.textContent='✅ 복사됨 · 카톡 나에게 붙여넣기';done()}).catch(function(){b.textContent='길게 눌러 코드 복사';ps.querySelector('details').open=true})}});
    var last=+(localStorage.getItem('ll_sync')||0);
    pl.innerHTML='<p>저장해 둔 걸 불러와요. <b>지금 체크는 불러온 걸로 바뀌어요.</b></p><ol class="bkol"><li><b>🔗 링크</b>를 저장했으면 → 그 링크를 누르면 끝</li><li><b>🖼️ QR 이미지</b>를 저장했으면 → <label class="fgbtn bkpick">QR 사진 고르기<input type="file" accept="image/*" hidden></label><br><small>갤러리에서 저장한 QR 사진을 고르면 돼요 · 카메라는 안 써요</small></li><li><b>⌨️ 코드</b>면 → <input class="scin" placeholder="코드 또는 링크 붙여넣기" autocomplete="off"> <button type="button" class="fgbtn scgo">불러오기</button></li></ol>'+
      '<p class="note">'+(last?'마지막으로 불러온 때: '+KST(last):'아직 불러온 적 없어요')+(bk?' · 마지막 저장: '+KST(bk.t)+' (☑ '+bk.n+'개)':'')+'</p><p class="bkmsg"></p>'+'<div class="bkrst"><button type="button" class="bkrb">🗑️ 내 체크 초기화</button><small>체크 · 세이브 표시 · 추천 범위를 처음 상태로 · 지우기 전에 💾 저장 탭에서 링크를 보내 두면 되살릴 수 있어요</small></div>';
    var msg=pl.querySelector('.bkmsg'),take=function(v){SYNC.take(v).then(function(n){g.remove();toast('📥 불러왔어요 · ☑ '+n+'개');bkBadge()}).catch(function(){msg.textContent='⚠ 코드를 못 읽었어요'})};
    pl.querySelector('.scgo').onclick=function(){var v=pl.querySelector('.scin').value;if(v)take(v)};
    var rb=pl.querySelector('.bkrb');rb.onclick=function(){if(!rb.classList.contains('arm')){rb.classList.add('arm');rb.textContent='⚠ 정말 지울까요? 한 번 더 누르면 지워져요';setTimeout(function(){if(rb.isConnected){rb.classList.remove('arm');rb.textContent='🗑️ 내 체크 초기화'}},5000);return}
      ['ll_chk','ll_extra','ll_bk','ll_sync','ll_saveinfo','ll_savemod','ll_rgrp'].forEach(function(k){try{localStorage.removeItem(k)}catch(e){}});
      g.remove();toast('🗑️ 초기화했어요 · 처음 상태예요');try{document.dispatchEvent(new CustomEvent('llchk',{detail:'save'}))}catch(e){}setTimeout(function(){location.reload()},900)};
    pl.querySelector('.bkpick input').onchange=function(e){var f=e.target.files[0];e.target.value='';if(!f)return;msg.textContent='⏳ 사진 읽는 중…';
      loadJS('/assets/jsqr.min.js','jsQR').then(function(jsQR){var im=new Image();im.onload=function(){var sc=Math.min(1,1600/Math.max(im.width,im.height)),c=document.createElement('canvas');c.width=im.width*sc;c.height=im.height*sc;
        var x=c.getContext('2d');x.drawImage(im,0,0,c.width,c.height);var d=x.getImageData(0,0,c.width,c.height),q=jsQR(d.data,c.width,c.height);URL.revokeObjectURL(im.src);
        if(q&&/[#&]s=/.test(q.data))take(q.data);else msg.textContent='⚠ 이 사진에서 저장 QR을 못 찾았어요'};im.src=URL.createObjectURL(f)}).catch(function(){msg.textContent='⚠ 읽기 실패'})};
    show(tab||(n?'save':'load'))};
  var sendQR=function(){bookmark('save')};
  // 🔄 지도 일반/인버스 토글 (인버스 = 180° 회전) · ?inv=1 로 들어오면 인버스로
  var isw=document.querySelector('.invsw');
  if(isw){var setInv=function(v){document.documentElement.classList.toggle('inv',v);[].forEach.call(isw.querySelectorAll('[data-inv]'),function(b){b.classList.toggle('on',(b.dataset.inv==='1')===v)});try{localStorage.setItem('ll_inv',v?'1':'0')}catch(e){}};
    var q=/[?&]inv=1/.test(location.search),st=false;try{st=localStorage.getItem('ll_inv')==='1'}catch(e){}
    setInv(q||st);isw.addEventListener('click',function(e){var b=e.target.closest('[data-inv]');if(b)setInv(b.dataset.inv==='1')})}
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
  var PAGES=[['해금 (본편 + DLC)','/vs/unlocks.html'],['비밀 (본편 + DLC)','/vs/secrets.html'],['디오라마 캐릭터','/vs/ed/chars.html'],['에메랄드 디오라마','/vs/ed/'],['에메랄드 디오라마 지도','/vs/ed/map.html'],['본편 진화 조합','/vs/evo.html'],['뱀파이어 서바이벌','/vs/'],['전체 글','/all.html']];
  var sb=document.getElementById('searchBtn');if(sb&&q)sb.addEventListener('click',function(){setTimeout(function(){q.focus()},150)});
  if(q)q.addEventListener('input',function(){var v=q.value.trim().replace(/\s/g,'');if(!v){res.innerHTML='';return}
    load().then(function(I){var out=[];PAGES.forEach(function(p){if(p[0].replace(/\s/g,'').indexOf(v)>=0)out.push('<a href="'+p[1]+'">📄 '+esc(p[0])+'</a>')});
      Object.keys(I).forEach(function(k){var it=I[k];if(out.length<30&&it.n.replace(/\s/g,'').indexOf(v)>=0)out.push('<span class="pop" data-pop="'+k+'">'+(it.i?'<img class="ic" src="'+it.i+'" alt="">':'')+esc(it.n)+'<small>'+esc(it.t)+'</small></span>')});
      res.innerHTML=out.join('')||'<span>찾는 게 없어요</span>'})});
})();
