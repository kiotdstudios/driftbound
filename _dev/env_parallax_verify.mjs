// DEEP-SPACE ENVIRONMENT / PARALLAX PASS verification
// Entry: index.html (module src/main.js + src/render/background.js), state via __DB.
// Run: node _dev/env_parallax_verify.mjs   (dev server on :8420)
import { chromium } from 'playwright';
const URL='http://localhost:8420/index.html';
const b=await chromium.launch({headless:true});
const p=await b.newPage();
const con=[];
p.on('console',m=>{ if(m.type()==='error') con.push('ERR: '+m.text()); });
p.on('pageerror',e=>con.push('PAGEERROR: '+e.message));
await p.goto(URL,{waitUntil:'domcontentloaded'});
await p.waitForTimeout(3800);
await p.click('text=PLAY SOLO');
await p.waitForTimeout(1200);

let PASS=0,FAIL=0;
const chk=(n,c,d='')=>{ if(c){PASS++;console.log('  PASS  '+n);} else {FAIL++;console.log('  FAIL  '+n+'   '+d);} };
const ev=fn=>p.evaluate(fn);

const sampleTL=()=>p.evaluate(()=>{
  const c=document.getElementById('game');
  const g=c.getContext('2d');
  const d=g.getImageData(20,20,64,64).data;
  return Array.from(d);
});
const diffCount=(a,b)=>{ let n=0; for(let i=0;i<a.length;i++) if(a[i]!==b[i]) n++; return n; };

const ready=await ev(()=>__DB.DevLog.entries.some(e=>(e.msg||e.message||'').includes('RUNTIME READY')));
chk('RUNTIME READY: PASS', ready);

let st=await ev(()=>__DB.envStats());
chk('all 7 layers loaded', st.layers===7, JSON.stringify(st));
chk('procedural stars present (>300)', st.stars>300, 'stars='+st.stars);
chk('procedural particles present (>90)', st.particles>90, 'particles='+st.particles);

let cfg=await ev(()=>({ starTiers:__DB.envConfig.stars.tiers.length, pTiers:__DB.envConfig.particles.tiers.length,
  layerKeys:Object.keys(__DB.envConfig.layers), rareGlow:__DB.envConfig.stars.tiers.filter(t=>t.glow).length,
  streak:__DB.envConfig.particles.tiers.filter(t=>t.streak).length }));
chk('4 star tiers (tiny/med/bright/rare)', cfg.starTiers===4, JSON.stringify(cfg));
chk('3 particle tiers', cfg.pTiers===3);
chk('7 named depth layers', cfg.layerKeys.length===7, cfg.layerKeys.join(','));
chk('rare-glow star tiers exist', cfg.rareGlow>=1);
chk('exactly one streaking (nearest) particle tier', cfg.streak===1, 'streak tiers='+cfg.streak);

await ev(()=>{ __DB.ship.vx=0; __DB.ship.vy=0; __DB.ship.worldX=0; __DB.ship.worldY=0; });
await p.waitForTimeout(200);
let s0=await sampleTL();
await p.waitForTimeout(1300);
let s1=await sampleTL();
const stationaryDiff=diffCount(s0,s1);
chk('stationary space still feels alive (bg changes at rest)', stationaryDiff>0, 'diff bytes='+stationaryDiff);

let s2=await sampleTL();
await ev(()=>{ __DB.ship.worldX=1200; __DB.ship.worldY=-600; });
await p.waitForTimeout(120);
let s3=await sampleTL();
const moveDiff=diffCount(s2,s3);
chk('parallax responds to camera movement', moveDiff>stationaryDiff, 'moveDiff='+moveDiff+' stationaryDiff='+stationaryDiff);

await ev(()=>{ __DB.ship.worldX=0; __DB.ship.worldY=0; });
async function setZoom(target){
  await p.keyboard.press('Digit0'); await p.waitForTimeout(250);
  if(target<0.85){ await p.keyboard.press('Minus'); }
  else if(target>1.0){ await p.keyboard.press('Equal'); await p.keyboard.press('Equal'); await p.keyboard.press('Equal'); }
  else { await p.keyboard.press('Equal'); }
  await p.waitForTimeout(400);
}
async function cornersOpaque(){
  return p.evaluate(()=>{
    const c=document.getElementById('game'); const g=c.getContext('2d');
    const pts=[[2,2],[c.width-3,2],[2,c.height-3],[c.width-3,c.height-3]];
    return pts.every(([x,y])=>{ const d=g.getImageData(x,y,1,1).data; return d[3]===255; });
  });
}
for(const z of [0.70,1.00,1.30]){ await setZoom(z); const ok=await cornersOpaque(); chk('no black/transparent edges @ zoom '+z, ok); }
await p.keyboard.press('Digit0'); await p.waitForTimeout(250);

con.length=0;
await ev(()=>{ __DB.ship.vx=3; __DB.ship.vy=1; __DB.ship.boostRamp=0.9; });
await p.waitForTimeout(500);
chk('boost streak path: 0 errors', con.length===0, con.join(' | '));

con.length=0;
await p.keyboard.press('F2'); await p.waitForTimeout(300);
await p.keyboard.press('F1'); await p.waitForTimeout(300);
await p.keyboard.press('KeyM'); await p.waitForTimeout(300); await p.keyboard.press('KeyM'); await p.waitForTimeout(200);
chk('HUD/minimap/diag overlays: 0 errors', con.length===0, con.join(' | '));

await p.waitForTimeout(500);
let alive=await ev(()=>{ const a=__DB.envStats(); return a && typeof a.camVel==='number'; });
chk('environment loop alive (stats responsive)', alive);

chk('zero uncaught exceptions overall', con.length===0, con.join(' | '));

console.log('\n==== ENV RESULT: '+PASS+' passed, '+FAIL+' failed ====');
await b.close();
process.exit(FAIL===0?0:1);
