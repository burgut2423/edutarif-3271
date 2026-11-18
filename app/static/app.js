(function(){
  const path=window.location.pathname;
  document.querySelectorAll('.nav-stack .nav-link').forEach(link=>{
    const href=link.getAttribute('href');
    if(href==='/' ? path==='/' : (path===href||path.startsWith(href+'/')))link.classList.add('active');
  });
  document.addEventListener('click',e=>{const s=document.getElementById('sidebar');if(s&&s.classList.contains('shown')&&!e.target.closest('.sidebar')&&!e.target.closest('.menu-toggle'))s.classList.remove('shown')});
})();
