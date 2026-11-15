/* Canvas scatter plots (evidence + prediction charts). */
function scat(id,pts,xl,yl,dg){const c=document.getElementById(id);if(!c)return;const g=c.getContext('2d'),W=c.width,H=c.height,P=44,xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);
let x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);if(dg){x0=y0=Math.min(x0,y0);x1=y1=Math.max(x1,y1)}
const X=v=>P+(v-x0)/((x1-x0)||1)*(W-P-12),Y=v=>H-P-(v-y0)/((y1-y0)||1)*(H-P-12),disc=!dg&&new Set(xs).size<=8;g.clearRect(0,0,W,H);
g.strokeStyle='#8a6a2f';g.strokeRect(P,10,W-P-12,H-P-10);g.fillStyle='#d9c9a3';g.font='13px sans-serif';g.fillText(xl+'  ('+(+x0.toFixed(1))+' → '+(+x1.toFixed(1))+')',P,H-10);g.save();g.rotate(-Math.PI/2);g.fillText(yl,-H/2-30,14);g.restore();
if(dg){g.strokeStyle='#f0b84a';g.beginPath();g.moveTo(X(x0),Y(y0));g.lineTo(X(x1),Y(y1));g.stroke()}
g.fillStyle='rgba(94,196,182,.75)';pts.forEach(([x,y],i)=>{const j=disc?(((i*37)%11)-5)*.012*(x1-x0):0;g.beginPath();g.arc(X(x+j),Y(y),3.5,0,7);g.fill()})}
