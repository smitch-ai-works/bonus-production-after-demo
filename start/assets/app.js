
(() => {
  'use strict';
  const data=JSON.parse(document.getElementById('copy-data').textContent);
  const status=document.getElementById('copy-status');
  const controls=[...document.querySelectorAll('[data-route]')];
  let selected=matchMedia('(max-width:650px)').matches?'phone':'pc';
  function select(route,scroll=false){
    selected=route;
    for(const key of ['pc','phone']){
      const panel=document.getElementById(key);panel.hidden=key!==route;
      if(panel.hidden)panel.querySelectorAll('video').forEach(v=>v.pause());
    }
    controls.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));
    if(scroll) document.getElementById(route).scrollIntoView({block:'start'});
  }
  document.getElementById('install-text').textContent=data.install;
  document.querySelectorAll('.start-text').forEach(el=>el.textContent=data.start);
  document.getElementById('answer-text').textContent=data.answer;
  document.getElementById('mobile-full').value=data.mobile;
  controls.forEach(b=>b.addEventListener('click',()=>select(b.dataset.route,true)));
  document.querySelectorAll('[data-select]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.select)));
  document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
    const key=button.dataset.copy,text=data[key];
    try{
      if(!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(text);
      status.textContent=key==='mobile'?'全文をコピーしました。ChatGPTの新しいチャットへ貼り付けて送ってください。':'コピーしました。AIへ貼り付けて使えます。';
      const old=button.textContent;button.textContent='コピーしました';
      setTimeout(()=>{button.textContent=old},2600);
    }catch{
      if(key==='mobile'){
        select('phone');const details=document.getElementById('prompt-details');details.open=true;
        const field=document.getElementById('mobile-full');field.focus();field.select();
        details.scrollIntoView({block:'start'});
        status.textContent='下の全文欄を長押しして「すべて選択」→「コピー」してください。';
      }else{
        const field=document.createElement('textarea');field.value=text;field.readOnly=true;field.setAttribute('aria-label','選択してコピーする文章');button.insertAdjacentElement('beforebegin',field);field.focus();field.select();
        status.textContent='文章を選択しました。「コピー」で保存してください。';
      }
    }
  }));
  document.getElementById('download-skill').addEventListener('click',()=>{status.textContent='ダウンロード後は、下の手順に沿ってZIPを展開してください。';});
  const osButtons=[...document.querySelectorAll('[data-os]')];
  function selectOS(os){
    for(const key of ['windows','mac']){
      const box=document.getElementById(key+'-video');
      if(key!==os)box.querySelector('video').pause();
      box.hidden=key!==os;
    }
    osButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.os===os)));
  }
  osButtons.forEach(b=>b.addEventListener('click',()=>selectOS(b.dataset.os)));
  selectOS(/Mac|iPhone|iPad/.test(navigator.platform)?'mac':'windows');

  const pcChapterButtons=[...document.querySelectorAll('[data-pc-chapter]')];
  const pcGuideStatus=document.getElementById('pc-guide-status');
  function activePCGuide(){return document.getElementById('mac-video').hidden?document.getElementById('pc-guide'):document.getElementById('mac-guide');}
  function pcChapterTime(button,video){return Number(video.id==='mac-guide'?button.dataset.macTime:button.dataset.windowsTime);}
  function refreshPCChapters(video=activePCGuide()){
    if(video!==activePCGuide())return;
    let active=0;pcChapterButtons.forEach((b,i)=>{if(video.currentTime>=pcChapterTime(b,video))active=i;});
    pcChapterButtons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===active)));
  }
  for(const video of [document.getElementById('pc-guide'),document.getElementById('mac-guide')]){
    video.addEventListener('timeupdate',()=>refreshPCChapters(video));
    video.addEventListener('loadedmetadata',()=>refreshPCChapters(video));
  }
  document.querySelectorAll('[data-os]').forEach(button=>button.addEventListener('click',()=>{pcGuideStatus.textContent='';refreshPCChapters();}));
  pcChapterButtons.forEach(button=>button.addEventListener('click',async()=>{
    const video=activePCGuide(),time=pcChapterTime(button,video);pcGuideStatus.textContent='';
    if(video.readyState===0){video.load();await new Promise(resolve=>{video.addEventListener('loadedmetadata',resolve,{once:true});video.addEventListener('error',resolve,{once:true});});}
    try{await video.play();}catch{pcGuideStatus.textContent='場面を移動しました。動画の再生ボタンを押してください。';}
    video.currentTime=time;refreshPCChapters(video);video.scrollIntoView({block:'start'});
  }));
  document.querySelector('.pc-fullscreen').addEventListener('click',async()=>{
    const video=activePCGuide(),time=video.currentTime;pcGuideStatus.textContent='';
    try{
      if(video.requestFullscreen)await video.requestFullscreen();
      else if(video.webkitEnterFullscreen)video.webkitEnterFullscreen();
      else throw new Error('Fullscreen unavailable');
      await video.play();
      video.currentTime=time;
    }catch{
      pcGuideStatus.replaceChildren();
      const link=document.createElement('a');link.href=(video.currentSrc||video.querySelector('source').src)+'#t='+time.toFixed(1);link.textContent='動画だけの画面を開く';link.target='_blank';link.rel='noopener';pcGuideStatus.append(link);
      pcGuideStatus.scrollIntoView({block:'nearest'});
    }
  });
  refreshPCChapters();
  select(selected);
})();
