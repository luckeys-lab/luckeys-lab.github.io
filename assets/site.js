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
  function load(){if(ITEMS)return Promise.resolve(ITEMS);if(!loading)loading=fetch('/data/vs/items.json').then(function(r){return r.json()}).then(function(j){ITEMS=j;return j});return loading}
  function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  // 미리보기
  var box=document.createElement('div');box.id='popbox';document.body.appendChild(box);var cur=null;
  function card(it){
    var h='<span class="ty">'+esc(it.t)+'</span><b>'+esc(it.n)+'</b>'+esc(it.d);
    if(it.p)h+='<div class="tip">'+esc(it.p)+'</div>';
    if(it.s)h+='<div class="ev">🗡️ 시작 스킬: '+esc(it.s)+'</div>';
    if(it.e)h+='<div class="ev">✨ 진화: '+esc(it.e)+'</div>';
    if(it.f)h+='<div class="ev">⬅ 재료: '+it.f.map(esc).join(' / ')+'</div>';
    if(it.u)h+='<div class="ev">🔗 이걸로 진화: '+it.u.map(esc).join(' · ')+'</div>';
    if(it.sk&&it.sk.length)h+='<div class="ev">👕 스킨: '+it.sk.map(esc).join(' · ')+'</div>';
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
    var rows=[].slice.call(list.querySelectorAll('.ul'));var fT='',fS='',only=false;
    function apply(){var n=0;rows.forEach(function(r){var d=!!S[r.dataset.id];if(d)n++;r.classList.toggle('done',d);
        var h=(fT&&r.dataset.type!==fT)||(fS&&r.dataset.scope!==fS)||(only&&d);r.classList.toggle('hide',h)});
      var pt=document.getElementById('ptxt'),pb=document.getElementById('pbar');if(pt)pt.textContent=n+' / '+rows.length;if(pb)pb.style.width=(n/rows.length*100)+'%'}
    rows.forEach(function(r){var c=r.querySelector('summary input');c.checked=!!S[r.dataset.id];
      c.addEventListener('click',function(e){e.stopPropagation()});
      c.addEventListener('change',function(){if(c.checked)S[r.dataset.id]=1;else delete S[r.dataset.id];try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}apply()})});
    function bar(id,attr,set){var b=document.getElementById(id);if(!b)return;b.addEventListener('click',function(e){var t=e.target.closest('button');if(!t)return;
      [].forEach.call(b.querySelectorAll('button'),function(x){x.classList.toggle('on',x===t)});set(t.dataset[attr]);apply()})}
    bar('fType','f',function(v){fT=v});bar('fScope','s',function(v){fS=v});
    var o=document.getElementById('onlyLeft');if(o){try{o.checked=localStorage.getItem('ll_only')==='1'}catch(e){}only=o.checked;
      o.addEventListener('change',function(){only=o.checked;try{localStorage.setItem('ll_only',only?'1':'0')}catch(e){}apply()})}
    apply();
    var h=location.hash.replace('#','');if(h){var t=document.querySelector('[data-id="'+h+'"]');if(t){t.open=true;t.scrollIntoView({block:'center'})}}
  }
  // 검색
  var q=document.getElementById('sq'),res=document.getElementById('sres');
  var PAGES=[['본편 해금 213개','/vs/base/unlocks.html'],['디오라마 캐릭터','/vs/ed/chars.html'],['에메랄드 디오라마 해금 41개','/vs/ed/'],['본편 진화 조합','/vs/evo.html'],['뱀파이어 서바이벌','/vs/'],['전체 글','/all.html']];
  var sb=document.getElementById('searchBtn');if(sb&&q)sb.addEventListener('click',function(){setTimeout(function(){q.focus()},150)});
  if(q)q.addEventListener('input',function(){var v=q.value.trim().replace(/\s/g,'');if(!v){res.innerHTML='';return}
    load().then(function(I){var out=[];PAGES.forEach(function(p){if(p[0].replace(/\s/g,'').indexOf(v)>=0)out.push('<a href="'+p[1]+'">📄 '+esc(p[0])+'</a>')});
      Object.keys(I).forEach(function(k){var it=I[k];if(out.length<30&&it.n.replace(/\s/g,'').indexOf(v)>=0)out.push('<span class="pop" data-pop="'+k+'">'+esc(it.n)+'<small>'+esc(it.t)+'</small></span>')});
      res.innerHTML=out.join('')||'<span>찾는 게 없어요</span>'})});
})();
