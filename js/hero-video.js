(() => {
  const video=document.getElementById('heroVideo');
  const button=document.querySelector('.hero-video-toggle');
  if(!video||!button)return;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let manuallyPaused=false;
  function update(){button.textContent=video.paused?'Play video':'Pause video';button.setAttribute('aria-label',video.paused?'Play DJ hero video':'Pause DJ hero video');}
  async function play(){try{await video.play();}catch(_){update();}}
  button.onclick=()=>{if(video.paused){manuallyPaused=false;play();}else{manuallyPaused=true;video.pause();}};
  video.addEventListener('play',update);video.addEventListener('pause',update);
  reduced.addEventListener('change',()=>{if(reduced.matches)video.pause();});
  const observer=new IntersectionObserver(entries=>{
    if(!entries[0].isIntersecting)video.pause();
    else if(!reduced.matches&&!manuallyPaused&&!document.hidden)play();
  },{threshold:.1});
  observer.observe(video);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();});
  update();
})();
