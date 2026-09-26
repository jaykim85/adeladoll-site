// 언어 메뉴: 고른 언어를 기억 (홈 첫 방문 시 자동 전환에 사용). 메뉴 밖을 누르면 닫힘
(function(){
  var menu=document.querySelector('details.lang'); if(!menu) return;
  menu.addEventListener('click',function(ev){
    var a=ev.target.closest('a[data-lang]'); if(!a) return;
    try{ localStorage.setItem('adela_lang', a.getAttribute('data-lang')); }catch(e){}
  });
  document.addEventListener('click',function(ev){ if(menu.open && !menu.contains(ev.target)) menu.open=false; });
  document.addEventListener('keydown',function(ev){ if(ev.key==='Escape') menu.open=false; });
})();
// 컬렉션 필터: #g=0,1 형태의 주소로 특정 그룹만 표시
(function(){
  var grid=document.getElementById('grid'); if(!grid) return;
  var chips=[].slice.call(document.querySelectorAll('.chip'));
  var cards=[].slice.call(grid.querySelectorAll('.card'));
  function apply(groups){
    chips.forEach(function(c){
      var g=c.getAttribute('data-g');
      c.setAttribute('aria-pressed', (groups===null ? g==='all' : groups.indexOf(g)>-1) ? 'true':'false');
    });
    cards.forEach(function(el){ el.hidden = groups!==null && groups.indexOf(el.getAttribute('data-group'))<0; });
  }
  function fromHash(){
    var m=location.hash.match(/g=([\d,]+)/); apply(m ? m[1].split(',') : null);
  }
  chips.forEach(function(c){
    c.addEventListener('click',function(){
      var g=c.getAttribute('data-g');
      if(g==='all'){ history.replaceState(null,'',location.pathname); apply(null); }
      else { history.replaceState(null,'','#g='+g); apply([g]); }
    });
  });
  window.addEventListener('hashchange',fromHash); fromHash();
})();
