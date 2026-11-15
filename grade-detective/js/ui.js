/* Title screen, how-to panel and sound toggle. */
(()=>{const $=id=>document.getElementById(id),t=$('title'),m=$('mute'),h=$('how'),hb=$('howbtn');
const sync=()=>{m.textContent='Sound: '+(SFX.isMuted()?'off':'on');m.setAttribute('aria-pressed',SFX.isMuted())};
$('bestline').textContent=BEST>30?'Best score: '+BEST+' pts':'';sync();
$('start').onclick=()=>{t.hidden=true;document.getElementById('app').focus()};
hb.onclick=()=>{h.hidden=!h.hidden;hb.setAttribute('aria-expanded',!h.hidden)};
m.onclick=()=>{SFX.toggle();sync();SFX.ok()};
document.addEventListener('click',e=>{if(e.target.closest('button')&&e.target.id!='mute')SFX.click()});
window.openTitle=()=>{$('bestline').textContent=BEST>30?'Best score: '+BEST+' pts':'';t.hidden=false};
const hud=$('hud'),addMenu=()=>{if(!hud.querySelector('#menu')){const b=document.createElement('button');b.id='menu';b.className='n';b.textContent='☰ Menu';b.onclick=openTitle;hud.appendChild(b)}};addMenu();new MutationObserver(addMenu).observe(hud,{childList:true});
})();
