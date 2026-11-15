/* Tiny WebAudio sound effects – no audio files needed. */
const SFX=(()=>{let ctx,muted=false;try{muted=localStorage.getItem('gl2mute')=='1'}catch(e){}
const tone=(f,d,t='sine',v=.07,at=0)=>{if(muted)return;try{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();const o=ctx.createOscillator(),g=ctx.createGain(),s=ctx.currentTime+at;o.type=t;o.frequency.value=f;g.gain.setValueAtTime(v,s);g.gain.exponentialRampToValueAtTime(.0001,s+d);o.connect(g);g.connect(ctx.destination);o.start(s);o.stop(s+d)}catch(e){}};
return{click:()=>tone(520,.05,'square',.03),ok:()=>{tone(523,.12,'triangle');tone(784,.2,'triangle',.07,.1)},bad:()=>{tone(180,.25,'sawtooth',.06);tone(120,.3,'sawtooth',.06,.12)},
isMuted:()=>muted,toggle:()=>{muted=!muted;try{localStorage.setItem('gl2mute',muted?'1':'0')}catch(e){}return muted}}})();
