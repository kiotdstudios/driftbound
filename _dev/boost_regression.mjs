// Verifies: Shift release ends boost accel immediately; releasing movement stops accel;
// velocity coasts (never increases) with no input; blur clears held keys. + mining works.
import { chromium } from 'playwright';
const URL='http://localhost:8420/driftbound_flight_test.html';
const browser=await chromium.launch({headless:true});
const page=await browser.newPage();
await page.setViewportSize({width:1280,height:720});
const errors=[];
page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message));
page.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE_ERR: '+m.text());});
await page.goto(URL,{waitUntil:'domcontentloaded'});
await page.waitForTimeout(1500);
await page.click('text=PLAY SOLO');
await page.waitForTimeout(800);
await page.evaluate(()=>{ ship.fuel = FUEL_CAPACITY; }); // ensure boost available

const spd = ()=>page.evaluate(()=>Math.hypot(ship.vx,ship.vy));
const state = ()=>page.evaluate(()=>({spd:+Math.hypot(ship.vx,ship.vy).toFixed(4), boostRamp:+ship.boostRamp.toFixed(3), thr:_thrusting, boo:_boosting}));

console.log('=== PHASE 1: hold W + Shift (accelerate/boost) ===');
await page.keyboard.down('KeyW'); await page.keyboard.down('ShiftLeft');
for(let i=0;i<8;i++){ await page.waitForTimeout(200); }
const sBoost=await state(); console.log('after boost hold:', JSON.stringify(sBoost));

console.log('=== PHASE 2: release Shift, KEEP W held (boost must end immediately) ===');
await page.keyboard.up('ShiftLeft');
const samplesA=[];
for(let i=0;i<12;i++){ await page.waitForTimeout(200); samplesA.push(await spd()); }
const sAfterShift=await state();
console.log('boostRamp right after shift release samples first 3:', samplesA.slice(0,3).map(x=>x.toFixed(3)));
console.log('speed trajectory (shift released, W held):', samplesA.map(x=>x.toFixed(3)).join(' '));
const increasedAfterShift = samplesA.slice(1).some((v,i)=> v > samplesA[i] + 0.02);
console.log('boostRamp now:', sAfterShift.boostRamp, '| speed kept INCREASING?', increasedAfterShift);

console.log('=== PHASE 3: release ALL movement (should only coast down) ===');
await page.keyboard.up('KeyW');
const samplesB=[];
for(let i=0;i<25;i++){ await page.waitForTimeout(200); samplesB.push(await spd()); }
console.log('coast trajectory:', samplesB.filter((_,i)=>i%3===0).map(x=>x.toFixed(3)).join(' '));
const increasedCoast = samplesB.slice(1).some((v,i)=> v > samplesB[i] + 0.001);
console.log('speed increased while coasting?', increasedCoast, '| final speed', samplesB[samplesB.length-1].toFixed(4));

console.log('=== PHASE 4: focus loss clears stuck keys ===');
await page.keyboard.down('KeyW'); await page.keyboard.down('ShiftLeft');
await page.waitForTimeout(300);
await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
await page.waitForTimeout(200);
const afterBlur=await page.evaluate(()=>({anyKey:Object.values(keys).some(Boolean), boostRamp:+ship.boostRamp.toFixed(3), thr:_thrusting, boo:_boosting}));
console.log('after blur:', JSON.stringify(afterBlur));
// let it settle: speed must not climb with no input
await page.waitForTimeout(400);
const blurTraj=[]; for(let i=0;i<8;i++){ await page.waitForTimeout(150); blurTraj.push(await spd()); }
const climbedAfterBlur = blurTraj.slice(1).some((v,i)=>v>blurTraj[i]+0.01);
console.log('speed climbed after blur?', climbedAfterBlur);

console.log('=== PHASE 5: mining still works ===');
const mine=await page.evaluate(async()=>{
  const i=asteroids.findIndex(a=>a.type?.id==='lg_planet'&&a.hp>0); if(i<0)return null;
  const a=asteroids[i]; ship.worldX=a.worldX-30; ship.worldY=a.worldY; ship.vx=0; ship.vy=0; return {i,hp0:a.hp};
});
if(mine){ await page.keyboard.down('KeyE'); await page.waitForTimeout(1500); await page.keyboard.up('KeyE');
  const hp=await page.evaluate((i)=>asteroids[i]?asteroids[i].hp:'gone', mine.i);
  console.log(`mining lg_planet hp ${mine.hp0} -> ${hp}`); }

console.log('\n=== RESULTS ===');
console.log('ERRORS:', errors.length); errors.forEach(e=>console.log('  ',e));
const pass = !increasedAfterShift && !increasedCoast && !afterBlur.anyKey && !climbedAfterBlur && errors.length===0 && sAfterShift.boostRamp===0;
console.log(pass?'RESULT: PASS':'RESULT: FAIL',
  {increasedAfterShift, increasedCoast, stuckKeys:afterBlur.anyKey, climbedAfterBlur, boostRampAfterShift:sAfterShift.boostRamp, errors:errors.length});
await browser.close();
