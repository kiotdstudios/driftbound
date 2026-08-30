import { chromium } from 'playwright';
const DEV=String.raw`C:\Users\diepowel\Documents\DRIFTBOUND\_dev`;
const b=await chromium.launch({headless:true}); const p=await b.newPage();
const errs=[]; p.on('console',m=>{if(m.type()==='error')errs.push(m.text());}); p.on('pageerror',e=>errs.push('PAGEERR: '+e.message));
await p.goto('http://localhost:8420/driftbound_flight_test.html',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(2500);
await p.click('text=PLAY SOLO'); await p.waitForTimeout(3500);
const sprite=await p.evaluate(()=>{
  const keys=Object.keys(podRotations);
  const loaded=keys.filter(k=>podRotations[k]&&podRotations[k].naturalWidth>0);
  const s=podRotations['south'];
  return { base:POD_SPRITE_BASE, keys, loadedCount:loaded.length,
           south:s?{w:s.naturalWidth,h:s.naturalHeight,src:s.src.split('/').slice(-2).join('/')}:null };
});
// place ship near the world pod and attach one, screenshot both states
await p.evaluate(()=>{ const wp=worldPods[0]; ship.worldX=wp.worldX-70; ship.worldY=wp.worldY; ship.ore=999; });
await p.waitForTimeout(400);
await p.screenshot({path:`${DEV}\\podart_world.png`});
await p.keyboard.press('KeyE'); await p.waitForTimeout(500);
const attached=await p.evaluate(()=>attachedPods.length);
await p.screenshot({path:`${DEV}\\podart_attached.png`});
console.log('POD_SPRITE_BASE:', sprite.base);
console.log('rotations loaded:', sprite.loadedCount, '/', sprite.keys.length, sprite.keys.join(','));
console.log('south sprite:', JSON.stringify(sprite.south));
console.log('attached pods after E:', attached);
console.log('console errors:', errs.length); errs.slice(0,5).forEach(e=>console.log('  '+e));
console.log((sprite.loadedCount===8 && attached===1 && errs.length===0) ? 'POD ART: PASS' : 'POD ART: CHECK');
await b.close();
