// E-KEY INTERACTION REGRESSION TEST
// Verifies the single interaction resolver + edge-trigger + interior state machine.
// Run: node _dev/e_interaction_regression.mjs   (dev server must be on :8420)
// MIGRATED (Test Harness Migration checkpoint): targets modular index.html via window.__DB
// bridge instead of legacy bare globals (interiorMode/attachedPods/worldPods/mineTarget/
// ship/frameCount/ctx/podSecured/DOOR_COL/iPlayerX/etc. no longer exist on window under
// ES module scope). Assertions/intent unchanged from legacy version.
import { chromium } from 'playwright';
const URL='http://localhost:8420/index.html';
const b=await chromium.launch({headless:true}); const p=await b.newPage();
const con=[]; p.on('console',m=>{const t=m.type();if(t==='error')con.push('ERR: '+m.text());}); p.on('pageerror',e=>con.push('PAGEERROR: '+e.message));
await p.goto(URL,{waitUntil:'domcontentloaded'}); await p.waitForTimeout(1500);
await p.click('text=PLAY SOLO'); await p.waitForTimeout(800);

let PASS=0, FAIL=0;
// CP2: wait for docking sequence to complete (replaces old instant-attach behavior)
async function waitForDock(timeout=3000){const t0=Date.now();while(Date.now()-t0<timeout){const d=await p.evaluate(()=>window.__DB.isDocking);if(!d)return;await p.waitForTimeout(50);}throw new Error('waitForDock timed out');}
const chk=(name,cond,detail='')=>{ if(cond){PASS++;console.log(`  PASS  ${name}`);} else {FAIL++;console.log(`  FAIL  ${name}  ${detail}`);} };
const fc=()=>p.evaluate(()=>window.__DB.frameCount);
// getContext('2d') on an already-2d canvas returns the same live context instance the
// module uses internally — no bridge property needed to read the transform.
const tmLeak=async()=>p.evaluate(()=>{const t=document.getElementById('game').getContext('2d').getTransform();return Math.abs(t.a-1)>0.01||Math.abs(t.d-1)>0.01||Math.abs(t.b)>0.01||Math.abs(t.c)>0.01;});
async function reset(){ await p.evaluate(()=>{ const DB=window.__DB;
  DB.interiorMode=false; DB.interiorFadeDir=0; DB.interiorFade=0; DB.interiorPodIdx=-1;
  DB.attachedPods.length=0; DB.worldPods.length=0; DB.ship.mineCooldown=0; DB.ship.vx=0; DB.ship.vy=0;
  // mineTarget/mineDist are recomputed at the top of updateMining() every frame — no manual reset needed.
}); }
async function loopDelta(ms){const a=await fc();await p.waitForTimeout(ms);return (await fc())-a;}

// ---- 1. nothing nearby ----
console.log('\n[1] E with nothing nearby'); con.length=0; await reset(); await p.waitForTimeout(150);
await p.keyboard.press('KeyE'); await p.waitForTimeout(300);
let s=await p.evaluate(()=>({im:window.__DB.interiorMode,fd:window.__DB.interiorFadeDir}));
chk('interiorMode stays false', s.im===false, JSON.stringify(s));
chk('no fade started', s.fd===0);
chk('no transform leak', !(await tmLeak()));
chk('0 console errors', con.length===0, con.join(' | '));

// ---- 2. asteroid only -> mines ----
console.log('\n[2] E near asteroid only (should mine)'); con.length=0; await reset();
await p.evaluate(()=>{ const DB=window.__DB; const a=DB.asteroids.find(x=>x.hp>0); a.worldX=DB.ship.worldX+20; a.worldY=DB.ship.worldY;
  window.__hp0=a.hp; window.__aid=a.aid; });
await p.waitForTimeout(150); await p.keyboard.down('KeyE'); await p.waitForTimeout(500); await p.keyboard.up('KeyE');
s=await p.evaluate(()=>{ const a=window.__DB.asteroids.find(x=>x.aid===window.__aid); return {hp:a?a.hp:0,hp0:window.__hp0,im:window.__DB.interiorMode}; });
chk('asteroid hp decreased (mined)', s.hp<s.hp0, JSON.stringify(s));
chk('interiorMode stays false', s.im===false);
chk('no transform leak', !(await tmLeak()));
chk('0 console errors', con.length===0, con.join(' | '));

// ---- 3. attached pod WITHOUT interior -> nothing ----
console.log('\n[3] E near attached pod (no interior) -> safe no-op'); con.length=0; await reset();
await p.evaluate(()=>{ window.__DB.attachedPods.push({label:'CARGO POD',color:'#38bdf8',cargoBonus:20,pid:'t1'}); });
await p.waitForTimeout(150); await p.keyboard.press('KeyE'); await p.waitForTimeout(300);
s=await p.evaluate(()=>({im:window.__DB.interiorMode,fd:window.__DB.interiorFadeDir}));
chk('interiorMode stays false', s.im===false, JSON.stringify(s));
chk('no fade started', s.fd===0);
chk('0 console errors', con.length===0, con.join(' | '));

// ---- 4. world pod in range -> claim (edge) ----
console.log('\n[4] E near world pod -> attaches'); con.length=0; await reset();
await p.evaluate(()=>{ const DB=window.__DB; DB.ship.ore=999; DB.worldPods.push({type:'modular_space_pod',pid:'wp1',worldX:DB.ship.worldX+10,worldY:DB.ship.worldY}); window.__wp=DB.worldPods.length; window.__ap=DB.attachedPods.length; });
await p.waitForTimeout(150); await p.keyboard.press('KeyE'); await waitForDock();
s=await p.evaluate(()=>({wp:window.__DB.worldPods.length,ap:window.__DB.attachedPods.length,wp0:window.__wp,ap0:window.__ap}));
chk('world pod consumed', s.wp<s.wp0, JSON.stringify(s));
chk('attached pod added', s.ap>s.ap0, JSON.stringify(s));
chk('0 console errors', con.length===0, con.join(' | '));

// ---- 5. one action per press: world pod + asteroid, single E -> only pod ----
console.log('\n[5] E with pod AND asteroid in range -> pod only (one action)'); con.length=0; await reset();
await p.evaluate(()=>{ const DB=window.__DB; DB.ship.ore=999;
  DB.worldPods.push({type:'modular_space_pod',pid:'wp2',worldX:DB.ship.worldX+10,worldY:DB.ship.worldY});
  const a=DB.asteroids.find(x=>x.hp>0); a.worldX=DB.ship.worldX+20; a.worldY=DB.ship.worldY; window.__hp0=a.hp; window.__aid=a.aid; window.__wp=DB.worldPods.length; });
await p.waitForTimeout(150); await p.keyboard.press('KeyE'); await waitForDock();
s=await p.evaluate(()=>{ const DB=window.__DB; const a=DB.asteroids.find(x=>x.aid===window.__aid); return {wp:DB.worldPods.length,wp0:window.__wp,hp:a?a.hp:0,hp0:window.__hp0}; });
chk('pod claimed', s.wp<s.wp0, JSON.stringify(s));
chk('asteroid NOT mined on same press', s.hp===s.hp0, JSON.stringify(s));
chk('0 console errors', con.length===0, con.join(' | '));

// ---- 6. interior enter -> render -> exit (the P0 crash path) ----
console.log('\n[6] E into pod interior: enter, render, exit'); con.length=0; await reset();
await p.evaluate(()=>{ window.__DB.attachedPods.push({label:'CARGO POD',color:'#38bdf8',hasInterior:true,pid:'ip1'}); });
await p.waitForTimeout(100);
const fBefore=await fc();
await p.keyboard.press('KeyE');
await p.waitForTimeout(1200); // allow fade-in to complete
s=await p.evaluate(()=>({im:window.__DB.interiorMode,fd:window.__DB.interiorFadeDir,fade:+window.__DB.interiorFade.toFixed(2)}));
chk('interiorMode became true', s.im===true, JSON.stringify(s));
chk('fade completed to 1', s.fade>=0.99, JSON.stringify(s));
chk('no transform leak in interior', !(await tmLeak()));
await p.evaluate(()=>{ window.__rafN=0; const _o=window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame=cb=>{ window.__rafN++; return _o(cb); }; });
await p.waitForTimeout(500);
const rafN=await p.evaluate(()=>window.__rafN);
chk('no rAF runaway in interior (single rAF/frame)', rafN>=15 && rafN<=90, 'rAF/500ms='+rafN);
chk('0 console errors during interior', con.length===0, con.join(' | '));
// exit via door
con.length=0;
await p.evaluate(()=>{ const DB=window.__DB; DB.podSecured=true; const dc=DB.DOOR_COL, dr=DB.DOOR_ROW; if(dc!==undefined){ DB.iPlayerX=dc+0.5; DB.iPlayerY=dr+0.5; } });
const canExit=await p.evaluate(()=>window.__DB.DOOR_COL!==undefined);
if(canExit){
  await p.keyboard.press('KeyE'); await p.waitForTimeout(1200);
  s=await p.evaluate(()=>({im:window.__DB.interiorMode,fd:window.__DB.interiorFadeDir}));
  chk('exited interior (back to flight)', s.im===false, JSON.stringify(s));
  chk('no transform leak after exit', !(await tmLeak()));
  chk('0 console errors during exit', con.length===0, con.join(' | '));
} else {
  console.log('  (skip exit: DOOR_COL not in __DB bridge)');
}

console.log(`\n===== ${FAIL===0?'ALL PASS':'FAIL'}  ${PASS} passed, ${FAIL} failed =====`);
await b.close();
process.exit(FAIL===0?0:1);
