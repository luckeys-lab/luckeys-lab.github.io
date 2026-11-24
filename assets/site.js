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
