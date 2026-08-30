import { chromium } from 'playwright';
const URL='http://localhost:8420/index.html';
const errs=[];
const b=await chromium.launch({headless:true,args:['--disable-background-timer-throttling','--disable-renderer-backgrounding']});
const pg=await b.newPage();
pg.on('pageerror',e=>errs.push('PAGEERR '+e.message));
pg.on('console',m=>{const t=m.text(); if(m.type()==='error')errs.push('CONSOLE '+t);});
await pg.goto(URL,{waitUntil:'domcontentloaded'});
await pg.waitForTimeout(3500);
await pg.click('text=PLAY SOLO');
await pg.waitForTimeout(1200);

const R={};
// wait for RUNTIME READY log (fires ~800ms after loop)
await pg.waitForTimeout(1500);
R.runtimeLog = await pg.evaluate(()=>{
  const L=window.__DB.DevLog; const all=(L&&L.entries?L.entries:[]).map(e=>JSON.stringify(e));
  return all.filter(s=>s.includes('RUNTIME READY')).join(' | ') || '(none found)';
});
R.critCount = await pg.evaluate(()=>{
  const L=window.__DB.DevLog; const es=(L&&L.entries)?L.entries:[];
  return es.filter(e=>(e.level==='CRITICAL'||e.level==='ERROR')&&e.system==='RuntimeError').length;
});

// X brake test: build up speed then brake with X
await pg.keyboard.down('ArrowUp'); await pg.waitForTimeout(900); await pg.keyboard.up('ArrowUp');
const sp1=await pg.evaluate(()=>Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
await pg.keyboard.down('KeyX'); await pg.waitForTimeout(900); await pg.keyboard.up('KeyX');
const sp2=await pg.evaluate(()=>Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
R.xBrakes = sp2 < sp1*0.6;
R.xSpeeds=[sp1.toFixed(3),sp2.toFixed(3)];

// Space no longer brakes: build speed, hold Space, speed should NOT drop like brake
await pg.keyboard.down('ArrowUp'); await pg.waitForTimeout(900); await pg.keyboard.up('ArrowUp');
const sp3=await pg.evaluate(()=>Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
await pg.keyboard.down('Space'); await pg.waitForTimeout(900); await pg.keyboard.up('Space');
const sp4=await pg.evaluate(()=>Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
// with no thrust, natural friction decays slowly; brake would slash hard. Space should decay much less than X did.
R.spaceNoBrake = sp4 > sp3*0.6;  // not a hard brake
R.spaceSpeeds=[sp3.toFixed(3),sp4.toFixed(3)];

// F3 dev panel toggles the devControls flag (read via a probe we inject)
R.devInit = await pg.evaluate(()=>window.__DB.devControls);
await pg.keyboard.press('F3'); await pg.waitForTimeout(150);
R.devAfterToggle = await pg.evaluate(()=>window.__DB.devControls);
await pg.keyboard.press('F3'); await pg.waitForTimeout(150); // toggle back on

// Pod ambient drift: sample the beacon-independent visual — sprite uses rotate; verify pod render loop doesn't crash & pod exists
R.podCount = await pg.evaluate(()=>window.__DB.worldPods.length);

// zoom + map still crash-free
await pg.keyboard.press('Minus'); await pg.keyboard.press('Equal'); await pg.keyboard.press('Digit0');
await pg.keyboard.press('KeyM'); await pg.waitForTimeout(200); await pg.keyboard.press('KeyM');
await pg.waitForTimeout(300);

R.errsFinal=errs.slice(0,20);
console.log(JSON.stringify(R,null,2));
await b.close();
