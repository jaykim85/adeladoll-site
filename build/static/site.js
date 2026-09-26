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
