import { chromium } from 'playwright';
const URL = 'http://localhost:8420/index.html';
const errors = [];
const b = await chromium.launch({ headless: true, args:[
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows','--disable-features=CalculateNativeWinOcclusion'] });
const pg = await b.newPage();
pg.on('pageerror', e => errors.push('PAGEERROR: '+e.message));
await pg.goto(URL, { waitUntil:'domcontentloaded' });
await pg.evaluate(()=> localStorage.removeItem('driftbound_save_v1'));
await pg.reload({ waitUntil:'domcontentloaded' });
await pg.waitForTimeout(3000);
await pg.click('text=PLAY SOLO').catch(()=>{});
await pg.waitForTimeout(800);
await pg.keyboard.press('KeyR'); await pg.waitForTimeout(100);
const oreSet = await pg.evaluate(()=> window.__DB.ship.ore);
// active loop: keep thrusting so rAF stays unthrottled; ~45s wall, poll save
let saved=false, waited=0;
while(waited < 70000){
  await pg.keyboard.down('ArrowUp'); await pg.waitForTimeout(400); await pg.keyboard.up('ArrowUp');
  await pg.keyboard.down('ArrowDown'); await pg.waitForTimeout(400); await pg.keyboard.up('ArrowDown');
  waited += 800;
  const s = await pg.evaluate(()=> localStorage.getItem('driftbound_save_v1'));
  if(s){ saved=true; break; }
}
console.log('save fired after ~'+(waited/1000)+'s active play:', saved);
const saved_ore = await pg.evaluate(()=>{ try{return JSON.parse(localStorage.getItem('driftbound_save_v1')).ore;}catch(e){return null;} });
await pg.reload({ waitUntil:'domcontentloaded' });
await pg.waitForTimeout(3500);
const oreAfter = await pg.evaluate(()=> window.__DB.ship.ore);
await b.close();
const R={ ore_before:oreSet, save_fired:saved, saved_ore, ore_after_reload:oreAfter, load_restored: oreAfter>=oreSet };
console.log(JSON.stringify(R,null,2));
console.log('ERRORS:', errors.length); errors.forEach(e=>console.log('  '+e));
const pass = R.save_fired && R.load_restored && errors.length===0;
console.log(pass?'SAVE/LOAD ROUNDTRIP: PASS':'SAVE/LOAD ROUNDTRIP: FAIL');
if(!pass) process.exit(1);
