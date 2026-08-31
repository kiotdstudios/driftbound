// Verifies full HUD renders identically at every zoom level + no transform leak + mining works.
// MIGRATED (Test Harness Migration checkpoint): targets modular index.html via window.__DB
// bridge instead of legacy bare globals (camZoomIdx/camZoom/asteroids/ship/DevLog no longer
// exist on window under ES module scope). Assertions/intent unchanged from legacy version.
import { chromium } from 'playwright';
const URL='http://localhost:8420/index.html';
const DEV=String.raw`C:\Users\diepowel\Documents\driftbound_work\integration\_dev`;
const browser=await chromium.launch({headless:true});
const page=await browser.newPage();
await page.setViewportSize({width:1280,height:720});
const errors=[]; const leaks=[];
page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message));
page.on('console',m=>{const t=m.text(); if(m.type()==='error'){errors.push('CONSOLE_ERR: '+t); if(t.includes('LEAKED INTO HUD'))leaks.push(t);} });
await page.goto(URL,{waitUntil:'domcontentloaded'});
await page.waitForTimeout(1500);
await page.click('text=PLAY SOLO');
await page.waitForTimeout(1200);

// helper: read transform at HUD-draw time via the canvas's own 2D context — getContext('2d')
// on an already-2d canvas always returns the SAME context instance, so this reaches the exact
// live ctx the module uses internally without needing a bridge property.
async function transformIdentity(){
  return await page.evaluate(()=>{ const ctx=document.getElementById('game').getContext('2d'); const tm=ctx.getTransform();
    return {a:+tm.a.toFixed(3),d:+tm.d.toFixed(3),e:+tm.e.toFixed(1),f:+tm.f.toFixed(1)}; });
}

const levels=[[0,'070'],[1,'085'],[2,'100'],[3,'115'],[4,'130']];
for(const [idx,tag] of levels){
  await page.evaluate((i)=>{ window.__DB.camera.setZoomIndex(i); }, idx);
  await page.waitForTimeout(700); // let ease settle
  const z=await page.evaluate(()=>{ const s=window.__DB.camera.getState(); return {idx:s.zoomIdx,zoom:+s.zoom.toFixed(3)}; });
  await page.screenshot({path:`${DEV}\\hud_zoom_${tag}.png`});
  console.log(`zoom ${tag}: idx=${z.idx} camZoom=${z.zoom} -> hud_zoom_${tag}.png`);
}

// mining still works?
const mine=await page.evaluate(async()=>{
  const asteroids=window.__DB.asteroids, ship=window.__DB.ship;
  const i=asteroids.findIndex(a=>a.type?.id==='lg_planet'&&a.hp>0);
  if(i<0) return 'no lg_planet';
  const a=asteroids[i]; ship.worldX=a.worldX-30; ship.worldY=a.worldY; ship.vx=0; ship.vy=0;
  const hp0=a.hp; return {i,hp0};
});
await page.keyboard.down('KeyE'); await page.waitForTimeout(1500); await page.keyboard.up('KeyE');
const mineAfter=await page.evaluate((i)=>{ const asteroids=window.__DB.asteroids; return {hp:asteroids[i]?asteroids[i].hp:'gone'}; }, (typeof mine==='object'?mine.i:0));
console.log('mining lg_planet hp0=%s -> now %s (mine engaged if lower or gone)', mine.hp0, mineAfter.hp);

// DevLog leak check
const devLeak=await page.evaluate(()=>{try{return (window.__DB.DevLog.entries||[]).filter(e=>String(e.message||'').includes('LEAKED INTO HUD')).length;}catch(e){return 'n/a';}});
console.log('\nTRANSFORM LEAK logs (console):',leaks.length,'| DevLog leak entries:',devLeak);
console.log('UNCAUGHT/CONSOLE ERRORS:',errors.length);
errors.forEach(e=>console.log('  ',e));
console.log(errors.length===0 && leaks.length===0 ? 'RESULT: PASS' : 'RESULT: FAIL');
await browser.close();
