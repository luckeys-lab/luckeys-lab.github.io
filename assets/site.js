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
    var ob=document.getElementById('ordBtn');
    if(ob){var om='rec';try{om=localStorage.getItem('ll_order')||'rec'}catch(e){}
      var reord=function(){[].forEach.call(list.querySelectorAll('.sec'),function(sec){var rs=[].slice.call(sec.querySelectorAll(':scope > .ul[data-gi]'));if(!rs.length)return;
          rs.sort(function(a,b){return om==='game'?(a.dataset.gi-b.dataset.gi):(a.dataset.ord-b.dataset.ord)});var anchor=rs[0].previousElementSibling;rs.forEach(function(r){sec.appendChild(r)})});
        ob.textContent=om==='game'?'📜 게임 순서':'🧭 추천 순서';ob.classList.toggle('on',om==='rec')};
      ob.addEventListener('click',function(){om=om==='game'?'rec':'game';try{localStorage.setItem('ll_order',om)}catch(e){}reord()});reord()}
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
        var r={nb:0,tb:0,ne:0,te:0,ns:0,ts:SK.length,name:o.saveName||''};
        Object.keys(K).forEach(function(a){var k=K[a],ok=!!AL[a.toLowerCase()];if(k.charAt(0)==='b'){r.tb++;if(ok)r.nb++}else{r.te++;if(ok)r.ne++}if(ok)S[k]=1;else delete S[k]});
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
    var show=function(r){msg.innerHTML='✅ '+(r.name?'「'+esc(r.name)+'」 ':'')+'세이브를 읽어 체크했어요'+(r.mod?' · 게임 저장 '+hhmm(r.mod):'')+'<br>🔓 <a href="/vs/unlocks.html">본편 해금 '+r.nb+' / '+r.tb+'</a> · 💎 <a href="/vs/unlocks.html#sec-ed">디오라마 해금 '+r.ne+' / '+r.te+'</a> · 🤫 <a href="/vs/secrets.html">비밀 '+r.ns+' / '+r.ts+'</a>'};
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
  var loadFile=function(f){if(!f)return;sflash('⏳');f.text().then(SAVE.apply).then(function(r){sflash('✅ 세이브 로드 · 💎 '+r.ne+'/'+r.te+' · 본편 '+r.nb+'/'+r.tb)}).catch(function(){sflash('⚠ 세이브 파일이 아니에요')})};
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
    var HAS=false,TIER=[['쉬움','🟢',2,3,false],['보통','🟡',4,8,true],['지옥','🔥',6,99,true]],RB=null,RC=null,bar=null,curT=0,mode='min',openRow=null;
    var first=false;try{mode=localStorage.getItem('ll_rbar');if(!mode){mode='min';first=true}if(mode==='off')mode='min';curT=+(localStorage.getItem('ll_rtier')||0)}catch(e){}
    var getS=function(){try{return JSON.parse(localStorage.getItem('ll_chk')||'{}')}catch(e){return {}}};
    function calc(){var S=getS(),has=function(k){return !!S[k]},inv=[].concat(RC.inv).every(has),T=TIER[curT],res=[];
      var vis=Object.keys(RB).filter(function(k){return !S[k]&&RB[k].need.every(function(g){return g.some(has)})&&RC.rows[k]});
      RC.opts.forEach(function(o){if(!o.need.every(has))return;[0,1].forEach(function(md){if(md&&!inv)return;var L=[];
        vis.forEach(function(id){var R=RC.rows[id];if(R.inv&&!md)return;if(R.ch.length&&R.ch.indexOf(o.c)<0)return;
          var sc=R.sc,lk=false,st=false;if(R.f){if(R.f===o.w)st=true;else{if(RC.wun[R.f]&&!has(RC.wun[R.f]))return;lk=true;sc+=1}}
          L.push({id:id,sc:sc,lk:lk,st:st,sp:(R.ch.length||R.inv||R.k==='coffin'||R.k==='boss')?0:1})});
        L.sort(function(a,b){return (b.st-a.st)||(a.sp-b.sp)||(a.sc-b.sc)});var pk=[],tot=0;
        L.forEach(function(x){if(pk.length>=T[2]||tot+x.sc>T[3]||(x.lk&&!T[4]))return;pk.push(x);tot+=x.sc});
        if(pk.length)res.push({o:o,md:md,pk:pk,tot:tot,ns:pk.filter(function(x){return x.st}).length})})});
      res.sort(function(a,b){return (b.pk.length-a.pk.length)||(b.ns-a.ns)||(a.tot-b.tot)});var seen={},top=[];
      res.forEach(function(r){if(seen[r.o.c]||top.length>=2)return;seen[r.o.c]=1;top.push(r)});return {top:top,S:S}}
    function head(r){var o=r.o;return '<b>'+esc(o.cn)+'</b>'+(o.c==='ANY'?'':' · '+esc(o.sk))+' · '+(r.md?'<span class="binv">🔄 인버스 모드</span>':'🌍 일반')}
    function draw(){if(!bar)return;var c=calc(),top=c.top,S=c.S;
      var one=top.length?head(top[0])+' → '+top[0].pk.map(function(x){return '💎'+RB[x.id].n}).join(' · '):'추천할 판이 없어요',cnt=top.length?top[0].pk.length:0;
      // 접힘 = 왼쪽 아래 둥근 버튼 (11/26 제이: 화면엔 페이지 내용만)
      if(mode!=='open'){bar.className='rbar fab'+(first?' hint':'');bar.innerHTML='<button type="button" class="rfab" data-m="open" title="추천 해금">🧭<span class="rlab">추천 해금</span>'+(cnt?'<i class="rcnt">'+cnt+'</i>':'')+'</button>';return}
      var h='<div class="rl"><span class="rtag">🧭 추천 해금</span><span class="rone">다음 판: '+one+'</span>'+(HAS?'<button type="button" class="rs" title="연결된 세이브를 다시 읽기">🔄 세이브</button>':'')+'<button type="button" class="rx" data-m="min">닫기 ✕</button></div>';
      if(mode==='open'){h+='<div class="rbody"><p class="rintro">체크한 해금을 보고, <b>다음 판에 한 번에 노릴 수 있는 해금</b>을 골라 줘요. 줄을 누르면 공략과 ☑ 체크가 펼쳐져요.</p><div class="rtabs">'+TIER.map(function(t,i){return '<button type="button" data-t="'+i+'" class="'+(i===curT?'on':'')+'">'+t[1]+' '+t[0]+'</button>'}).join('')+'</div>';
        if(!top.length)h+='<p class="rn">지금 체크 상태로는 추천할 판이 없어요.</p>';
        top.forEach(function(r){var o=r.o;h+='<div class="rc">'+(o.ci?'<img class="sp" src="'+o.ci+'" alt="">':'')+'<div class="rcb"><div class="rh2">'+head(r)+'</div>'+(o.c==='ANY'?'<div class="rw">본편 캐릭터도 OK</div>':'<div class="rw">'+(o.wi?'<img class="ic" src="'+o.wi+'" alt="">':'🗡️ ')+'시작 스킬 '+esc(o.wn)+'</div>')+'<ul>'+
          r.pk.map(function(x){var it=RB[x.id],op=openRow===x.id;return '<li><a class="ri" data-r="'+x.id+'">💎'+it.n+' '+(it.th||esc(it.t))+'</a>'+(x.st?' <em class="st">🗡️ 시작 스킬</em>':'')+(x.lk?' <em class="lk">🎲 상자 운</em>':'')+
            (op?'<div class="rdet"><label class="rck"><input type="checkbox" data-c="'+x.id+'"'+(S[x.id]?' checked':'')+'> 해금 완료</label><p class="rw2">🎁 보상 → '+esc(it.rw)+'</p>'+it.g+'<a class="go" href="/vs/unlocks.html#'+x.id+'">목록에서 보기 →</a></div>':'')+'</li>'}).join('')+'</ul></div></div>'});
        h+='</div>'}
      bar.className='rbar '+mode;bar.innerHTML=h}
    Promise.all([fetch('/data/vs/ed/rbar.json?v='+VER).then(function(r){return r.json()}),fetch('/data/vs/ed/reco.json?v='+VER).then(function(r){return r.json()})]).then(function(j){RB=j[0];RC=j[1];
      bar=document.createElement('div');(document.getElementById('dkReco')||document.body).appendChild(bar);
      bar.addEventListener('click',function(e){var m=e.target.closest('[data-m]'),t=e.target.closest('[data-t]'),ri=e.target.closest('.ri'),ck=e.target.closest('[data-c]');
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
      document.addEventListener('llchk',function(e){if(e.detail==='list'||e.detail==='save')draw()});
      SAVE.getH().then(function(h){HAS=!!h;draw()});draw()})}
  // 💾 세이브 연동 표시: 컬렉션(data-col) · 우화집 처치 수(data-kill) · 캐릭터(data-ch)
  var showExtra=function(){var X=null;try{X=JSON.parse(localStorage.getItem('ll_extra')||'null')}catch(e){}if(!X)return;
    var cw={};X.cw.forEach(function(k){cw[k]=1});var uc={},bc={};X.uc.forEach(function(k){uc[k]=1});X.bc.forEach(function(k){bc[k]=1});
    var nc=0,tc=0;[].forEach.call(document.querySelectorAll('[data-col]'),function(el){tc++;var ok=!!cw[el.dataset.col];if(ok)nc++;el.classList.toggle('got',ok);el.classList.toggle('miss',!ok)});
    var nk=0,tk=0;[].forEach.call(document.querySelectorAll('[data-kill]'),function(el){tk++;var n=X.kc[el.dataset.kill]||0;if(n)nk++;el.classList.toggle('miss',!n);var b=el.querySelector('.bkill');if(b)b.textContent=n?'처치 '+n.toLocaleString():'아직 못 잡음'});
    [].forEach.call(document.querySelectorAll('[data-ch]'),function(el){var id=el.dataset.ch;el.classList.toggle('locked',!uc[id]);el.classList.toggle('unbought',!!uc[id]&&!bc[id])});
    [].forEach.call(document.querySelectorAll('.savestat'),function(el){var k=el.dataset.kind;el.innerHTML=k==='col'?'💾 세이브 기준 모은 것 <b>'+nc+' / '+tc+'</b>':'💾 세이브 기준 잡은 몹 <b>'+nk+' / '+tk+'</b>';el.classList.add('on')})};
  showExtra();document.addEventListener('llchk',function(e){if(e.detail==='save')showExtra()});
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
