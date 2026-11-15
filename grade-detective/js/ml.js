/* ML engine: seeded split (237 train / 79 validation / 79 sealed test), metrics, ridge, kNN, cross-validation. */
const rng=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const RN=rng(42),ix=[...ALL.keys()];for(let i=ix.length-1;i>0;i--){const j=Math.floor(RN()*(i+1));[ix[i],ix[j]]=[ix[j],ix[i]]}
const TR=ix.slice(0,237).map(i=>ALL[i]),VA=ix.slice(237,316).map(i=>ALL[i]),TE=ix.slice(316).map(i=>ALL[i]);
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(x=>(x-m)**2)))||1};
const qt=(a,p)=>{const s=[...a].sort((x,y)=>x-y),i=(s.length-1)*p,l=Math.floor(i);return s[l]+(s[Math.ceil(i)]-s[l])*(i-l)};
const rmse=(y,p)=>Math.sqrt(mean(y.map((v,i)=>(v-p[i])**2))),mae=(y,p)=>mean(y.map((v,i)=>Math.abs(v-p[i]))),r2=(y,p)=>1-y.reduce((s,v,i)=>s+(v-p[i])**2,0)/y.reduce((s,v)=>s+(v-mean(y))**2,0);
const corr=(a,b)=>{const ma=mean(a),mb=mean(b);let n=0;a.forEach((x,i)=>n+=(x-ma)*(b[i]-mb));return n/(a.length*sd(a)*sd(b))};
const ab=TR.map(r=>r.absences),FEN=qt(ab,.75)+1.5*(qt(ab,.75)-qt(ab,.25));

const view=r=>S.o.abs=='cap'?r.map(x=>({...x,absences:Math.min(x.absences,FEN)})):r;
const cleanTrain=r=>{let v=view(r);if(S.o.abs=='drop')v=v.filter(x=>x.absences<=FEN);if(S.o.zero=='drop')v=v.filter(x=>x.G3>0);return v};
function predict(c,tr,ev){const y=tr.map(r=>r.G3),m=mean(y);if(c.model=='base'||!c.f.length)return ev.map(()=>m);
const mu=c.f.map(k=>mean(tr.map(r=>r[k]))),s=c.f.map(k=>sd(tr.map(r=>r[k]))),t=r=>c.f.map((k,j)=>(r[k]-mu[j])/s[j]),X=tr.map(t),E=ev.map(t);
if(c.model=='knn')return E.map(e=>mean(X.map((x,i)=>[x.reduce((a,v,j)=>a+(v-e[j])**2,0),y[i]]).sort((a,b)=>a[0]-b[0]).slice(0,c.p).map(z=>z[1])));
const p=c.f.length,A=Array.from({length:p},(_,i)=>Array.from({length:p+1},(_,j)=>j==p?X.reduce((a,x,n)=>a+x[i]*(y[n]-m),0):X.reduce((a,x)=>a+x[i]*x[j],0)+(i==j?c.p:0)));
for(let i=0;i<p;i++){let mx=i;for(let r=i+1;r<p;r++)if(Math.abs(A[r][i])>Math.abs(A[mx][i]))mx=r;[A[i],A[mx]]=[A[mx],A[i]];for(let r=0;r<p;r++)if(r!=i){const f=A[r][i]/A[i][i];for(let q=i;q<=p;q++)A[r][q]-=f*A[i][q]}}
const w=A.map((row,i)=>row[p]/row[i]);return E.map(e=>m+e.reduce((a,v,j)=>a+v*w[j],0))}
const cv=(c,tr)=>mean([0,1,2,3,4].map(f=>{const te=tr.filter((_,i)=>i%5==f);return rmse(te.map(r=>r.G3),predict(c,tr.filter((_,i)=>i%5!=f),te))}));
