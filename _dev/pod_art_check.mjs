import { chromium } from 'playwright';
// MIGRATED (Test Harness Migration checkpoint): targets modular index.html via window.__DB
// bridge instead of legacy bare globals. Assertions/intent unchanged.
const DEV=String.raw`C:\Users\diepowel\Documents\driftbound_work\integration\_dev`;
const b=await chromium.launch({headless:true}); const p=await b.newPage();
const errs=[]; p.on('console',m=>{if(m.type()==='error')errs.push(m.text());}); p.on('pageerror',e=>errs.push('PAGEERR: '+e.message));
await p.goto('http://localhost:8420/index.html',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(2500);
await p.click('text=PLAY SOLO'); await p.waitForTimeout(3500);
const sprite=await p.evaluate(()=>{
  const DB=window.__DB;
  const keys=Object.keys(DB.podRotations);
  const loaded=keys.filter(k=>DB.podRotations[k]&&DB.podRotations[k].naturalWidth>0);
  const s=DB.podRotations['south'];
  return { base:DB.POD_SPRITE_BASE, keys, loadedCount:loaded.length,
           south:s?{w:s.naturalWidth,h:s.naturalHeight,src:s.src.split('/').slice(-2).join('/')}:null };
});
// place ship near the world pod and attach one, screenshot both states
await p.evaluate(()=>{ const DB=window.__DB; const wp=DB.worldPods[0]; DB.ship.worldX=wp.worldX-70; DB.ship.worldY=wp.worldY; DB.ship.ore=999; });
await p.waitForTimeout(400);
await p.screenshot({path:`${DEV}\\podart_world.png`});
await p.keyboard.press('KeyE'); await p.waitForTimeout(500);
const attached=await p.evaluate(()=>window.__DB.attachedPods.length);
await p.screenshot({path:`${DEV}\\podart_attached.png`});
console.log('POD_SPRITE_BASE:', sprite.base);
console.log('rotations loaded:', sprite.loadedCount, '/', sprite.keys.length, sprite.keys.join(','));
console.log('south sprite:', JSON.stringify(sprite.south));
console.log('attached pods after E:', attached);
console.log('console errors:', errs.length); errs.slice(0,5).forEach(e=>console.log('  '+e));
console.log((sprite.loadedCount===8 && attached===1 && errs.length===0) ? 'POD ART: PASS' : 'POD ART: CHECK');
await b.close();
