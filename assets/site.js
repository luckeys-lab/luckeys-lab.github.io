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
  function load(){if(ITEMS)return Promise.resolve(ITEMS);if(!loading)loading=fetch('/data/vs/items.json?v='+VER).then(function(r){return r.json()}).then(function(j){ITEMS=j;return j});return loading}
  function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  // 미리보기
  var box=document.createElement('div');box.id='popbox';document.body.appendChild(box);var cur=null;
  function card(it){
    var h='<span class="ty">'+esc(it.t)+'</span><b>'+(it.i?'<img class="ic big" src="'+it.i+'" alt="">':'')+esc(it.n)+'</b>'+esc(it.d);
    if(it.p)h+='<div class="tip">'+esc(it.p)+'</div>';
    if(it.s)h+='<div class="ev">'+(it.si?'<img class="ic" src="'+it.si+'" alt="">':'🗡️ ')+'시작 스킬: '+esc(it.s)+'</div>';
    if(it.e)h+='<div class="ev">✨ 진화: '+esc(it.e)+'</div>';
    if(it.f)h+='<div class="ev">⬅ 재료: '+it.f.map(esc).join(' / ')+'</div>';
    if(it.u)h+='<div class="ev">🔗 이걸로 진화: '+it.u.map(esc).join(' · ')+'</div>';
    if(it.sk&&it.sk.length)h+='<div class="ev">👕 스킨: '+it.sk.map(esc).join(' · ')+'</div>';
    if(it.x)it.x.forEach(function(t){h+='<div class="ev">'+esc(t)+'</div>'});
    if(it.ul&&it.ul.length)h+='<div class="uls">'+it.ul.map(function(u){return '<a href="'+u[1]+'">🔓 '+esc(u[0])+'</a>'}).join('')+'</div>';
    if(it.l)h+='<a class="go" href="'+it.l+'">자세히 →</a>';
    return h}
  function show(el,key){load().then(function(I){var it=I[key];if(!it)return;box.innerHTML=card(it);box.style.display='block';
    var r=el.getBoundingClientRect(),w=box.offsetWidth,h=box.offsetHeight;var x=Math.max(8,Math.min(r.left,innerWidth-w-8));var y=r.bottom+6;if(y+h>innerHeight-8)y=Math.max(8,r.top-h-6);
    box.style.left=x+'px';box.style.top=y+'px';cur=el})}
  function hide(){box.style.display='none';cur=null}
  var hover=matchMedia('(hover:hover)').matches;
  document.addEventListener('click',function(e){var el=e.target.closest('[data-pop]');
    if(el){e.preventDefault();e.stopPropagation();if(cur===el)hide();else show(el,el.dataset.pop);return}
    if(!box.contains(e.target))hide()});
  if(hover){document.addEventListener('mouseover',function(e){var el=e.target.closest('[data-pop]');if(el&&el!==cur)show(el,el.dataset.pop)});
    document.addEventListener('mouseout',function(e){var el=e.target.closest('[data-pop]');if(el&&!(e.relatedTarget&&(box.contains(e.relatedTarget)||el.contains(e.relatedTarget))))setTimeout(function(){if(!box.matches(':hover'))hide()},120)});}
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
