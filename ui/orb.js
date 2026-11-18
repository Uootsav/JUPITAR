/* Original JUPITAR orbital renderer. Functional UI, no film assets. */
class JupiterOrb {
 constructor(canvas){this.c=canvas;this.ctx=canvas.getContext('2d');this.level=0;this.state='idle';this.motion=!matchMedia('(prefers-reduced-motion: reduce)').matches;this.phase=0;this.last=0;this.visible=true;this.ro=new ResizeObserver(()=>this.resize());this.ro.observe(canvas);document.addEventListener('visibilitychange',()=>{this.visible=!document.hidden});this.resize();requestAnimationFrame(t=>this.frame(t));}
 resize(){const b=this.c.getBoundingClientRect();this.dpr=Math.min(devicePixelRatio||1,2);this.w=b.width;this.h=b.height;this.c.width=b.width*this.dpr;this.c.height=b.height*this.dpr;}
 frame(t){requestAnimationFrame(x=>this.frame(x));if(!this.visible||t-this.last<33)return;this.last=t;if(this.motion)this.phase+=.009;this.draw();}
 draw(){let c=this.ctx,w=this.w,h=this.h;if(!w||!h)return;c.setTransform(this.dpr,0,0,this.dpr,0,0);c.clearRect(0,0,w,h);c.save();c.translate(w/2,h/2);const R=Math.min(w,h)*.36,t=this.phase,active=this.state==='thinking'||this.state==='speaking';let glow=c.createRadialGradient(0,0,R*.04,0,0,R*1.4);glow.addColorStop(0,'#5ff6ff35');glow.addColorStop(.5,'#22bde01c');glow.addColorStop(1,'#00b5ff00');c.fillStyle=glow;c.fillRect(-w/2,-h/2,w,h);
 const ring=(radius,start,end,color,width)=>{c.beginPath();c.strokeStyle=color;c.lineWidth=width;c.arc(0,0,radius,start,end);c.stroke()};
 ring(R*1.1,0,Math.PI*2,'#62d9ff18',1);ring(R*.94,0,Math.PI*2,'#62d9ff35',1);
 for(let i=0;i<96;i++){let a=i*Math.PI/48;c.strokeStyle=i%8===0?'#9bf5ff99':'#61d7ff35';c.lineWidth=1;c.beginPath();c.moveTo(Math.cos(a)*R*1.04,Math.sin(a)*R*1.04);c.lineTo(Math.cos(a)*R*(i%8===0?1.09:1.06),Math.sin(a)*R*(i%8===0?1.09:1.06));c.stroke()}
 for(let k=0;k<3;k++){c.save();c.rotate(t*(k%2?-1:1)+k*1.1);for(let i=0;i<3;i++)ring(R*(.78+k*.075),i*2.094,i*2.094+1.1,k===1?'#a7faff':'#30b6e5',k===1?2:1);c.restore()}
 // Tilted orbital paths, independently rotating satellites.
 for(let k=0;k<3;k++){c.save();c.rotate(k*1.02+t*.18);c.scale(1,.38+k*.055);ring(R*.88,0,Math.PI*2,'#66dfff55',1.3);let a=t*(1.3+k*.3)+k*2;c.fillStyle='#d4ffff';c.shadowBlur=14;c.shadowColor='#38d9ff';c.beginPath();c.arc(Math.cos(a)*R*.88,Math.sin(a)*R*.88,2.7,0,Math.PI*2);c.fill();c.restore()}
 // Latitude/longitude mesh gives the core depth without an external 3D library.
 let sphere=R*(.55+(active?.018:0)+this.level*.035);c.save();c.rotate(t*.15);c.strokeStyle='#59dfff55';c.lineWidth=.65;for(let i=-3;i<=3;i++){let y=i*sphere/4;let rx=Math.sqrt(Math.max(0,sphere*sphere-y*y));c.beginPath();c.ellipse(0,y,rx,rx*.22,0,0,Math.PI*2);c.stroke()}for(let i=0;i<7;i++){c.beginPath();c.ellipse(0,0,sphere*Math.abs(Math.cos(t*.5+i*Math.PI/7)),sphere,0,0,Math.PI*2);c.stroke()}c.restore();
 let core=c.createRadialGradient(-sphere*.2,-sphere*.2,0,0,0,sphere);core.addColorStop(0,'#e0ffffdd');core.addColorStop(.12,'#77f7ff99');core.addColorStop(.42,'#2fd3ef35');core.addColorStop(1,'#003c7510');c.fillStyle=core;c.beginPath();c.arc(0,0,sphere,0,Math.PI*2);c.fill();
 for(let i=0;i<32;i++){let a=i*2.39996+t*.25,rr=sphere*Math.sqrt((i+.5)/32);c.fillStyle=i%3?'#88eeff88':'#ffffff';c.beginPath();c.arc(Math.cos(a)*rr,Math.sin(a)*rr,.9+(i%4===0?.5:0),0,Math.PI*2);c.fill()}
 ring(sphere*.13,0,Math.PI*2,'#caffff',1);c.restore();}
}
window.JupiterOrb=JupiterOrb;
