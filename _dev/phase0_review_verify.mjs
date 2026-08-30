import { chromium } from 'playwright';
const URL = 'http://localhost:8420/index.html';
const errors = [];
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
pg.on('console', m => { if (m.type()==='error') errors.push('CONSOLE: '+m.text()); });
pg.on('pageerror', e => errors.push('PAGEERROR: '+e.message));
const R = {};

await pg.goto(URL, { waitUntil: 'domcontentloaded' });
await pg.waitForTimeout(3000);

// --- inline-handler globals ---
R.lobbyConnect_fn = await pg.evaluate(()=> typeof window.lobbyConnect==='function');
R.showToast_fn    = await pg.evaluate(()=> typeof window.showToast==='function');
R.showToast_works = await pg.evaluate(()=>{ window.showToast('REVIEW_TEST','#fff'); return window.__DB.toastMsg==='REVIEW_TEST'; });
// lobby buttons carry the inline onclick wired to the now-global fn
R.launchBtn_onclick = await pg.evaluate(()=>{ const btns=[...document.querySelectorAll('button')]; const l=btns.find(x=>/LAUNCH/.test(x.textContent)); return l? l.getAttribute('onclick') : null; });
R.soloBtn_present   = await pg.evaluate(()=> [...document.querySelectorAll('button')].some(x=>/PLAY SOLO/.test(x.textContent)));
// lobby name input onkeydown references lobbyConnect
R.nameInput_onkeydown = await pg.evaluate(()=>{ const i=document.getElementById('lobby-name'); return i? i.getAttribute('onkeydown'): null; });

// --- __DB read/write bridge ---
R.bridge_read  = await pg.evaluate(()=> !!(window.__DB && window.__DB.ship && window.__DB.DevLog));
R.bridge_write = await pg.evaluate(()=>{ window.__DB.interiorMode=true; const v=window.__DB.interiorMode; window.__DB.interiorMode=false; return v===true && window.__DB.interiorMode===false; });

// --- PLAY SOLO hides lobby ---
await pg.click('text=PLAY SOLO').catch(()=>{});
await pg.waitForTimeout(1500);
R.solo_hidesLobby = await pg.evaluate(()=>{ const l=document.getElementById('lobby'); return !l||l.style.display==='none'; });

// --- keyboard handlers: movement / boost / braking ---
const p0 = await pg.evaluate(()=>({y:window.__DB.ship.worldY}));
await pg.keyboard.down('ArrowUp'); await pg.waitForTimeout(1000); await pg.keyboard.up('ArrowUp'); await pg.waitForTimeout(150);
const p1 = await pg.evaluate(()=>({y:window.__DB.ship.worldY, sp:Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy)}));
R.kbd_move = Math.abs(p1.y-p0.y) > 1;
await pg.keyboard.down('ArrowUp'); await pg.keyboard.down('ShiftLeft'); await pg.waitForTimeout(1200);
const spBoost = await pg.evaluate(()=> Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
await pg.keyboard.up('ShiftLeft'); await pg.keyboard.up('ArrowUp');
R.kbd_boost = spBoost > 1.0;
// braking: press Down (reverse/brake) and confirm speed drops from boost peak
await pg.keyboard.down('ArrowDown'); await pg.waitForTimeout(800); await pg.keyboard.up('ArrowDown');
const spBrake = await pg.evaluate(()=> Math.hypot(window.__DB.ship.vx,window.__DB.ship.vy));
R.kbd_brake = spBrake < spBoost;

// --- zoom / map keys do not crash ---
const errBeforeZoom = errors.length;
await pg.keyboard.press('Minus'); await pg.keyboard.press('Equal'); await pg.keyboard.press('Digit0');
await pg.keyboard.press('KeyM'); await pg.keyboard.press('KeyM'); await pg.keyboard.press('Tab');
await pg.waitForTimeout(200);
R.zoomMap_noError = errors.length === errBeforeZoom;

// --- dev cheats (Slash fuel / KeyR resources / KeyP spawn pod / KeyH hull) ---
const cheat0 = await pg.evaluate(()=>({fuel:window.__DB.ship.fuel, ore:window.__DB.ship.ore, pods:window.__DB.worldPods.length}));
await pg.keyboard.press('Slash'); await pg.waitForTimeout(80);
await pg.keyboard.press('KeyR');  await pg.waitForTimeout(80);
await pg.keyboard.press('KeyP');  await pg.waitForTimeout(80);
const cheat1 = await pg.evaluate(()=>({fuel:window.__DB.ship.fuel, ore:window.__DB.ship.ore, pods:window.__DB.worldPods.length}));
R.cheat_fuel = cheat1.fuel > cheat0.fuel;
R.cheat_resources = cheat1.ore >= cheat0.ore + 25;
R.cheat_spawnpod = cheat1.pods === cheat0.pods + 1;

// --- canvas shooting input handler (merged tail script) does not throw outside interior ---
const errBeforeShoot = errors.length;
await pg.evaluate(()=>{ const c=document.getElementById('game'); c.dispatchEvent(new MouseEvent('mousedown',{clientX:200,clientY:200,bubbles:true})); });
await pg.waitForTimeout(120);
R.canvasShoot_safe = errors.length === errBeforeShoot;

// --- save initialization ---
await pg.waitForTimeout(400);
R.save_key = await pg.evaluate(()=> Object.keys(localStorage).filter(k=>k.toLowerCase().includes('driftbound')));

// --- HARD REFRESH: ES-module reload must not break ---
const errBeforeReload = errors.length;
await pg.reload({ waitUntil: 'domcontentloaded' });
await pg.waitForTimeout(3000);
R.reload_bridge = await pg.evaluate(()=> !!(window.__DB && window.__DB.ship));
R.reload_binds  = await pg.evaluate(()=> typeof window.lobbyConnect==='function' && typeof window.showToast==='function');
R.reload_saveKept = await pg.evaluate(()=> Object.keys(localStorage).some(k=>k.toLowerCase().includes('driftbound')));
R.reload_noNewErr = errors.length === errBeforeReload;
// module script actually executed after reload (game booted)
R.reload_booted = await pg.evaluate(()=> !!(window.__DB && window.__DB.DevLog && window.__DB.DevLog.entries && window.__DB.DevLog.entries.length>0));

// --- DevLog CRITICAL/ERROR sweep ---
R.devlog_clean = await pg.evaluate(()=>{
  const d=window.__DB.DevLog; if(!d||!d.entries) return true;
  return d.entries.filter(e=>e.level==='CRITICAL'||e.level==='ERROR').length===0;
});

await b.close();

console.log(JSON.stringify(R,null,2));
console.log('CONSOLE/PAGE ERRORS:', errors.length);
errors.forEach(e=>console.log('  '+e));

const checks = {
 lobbyConnect_fn:R.lobbyConnect_fn, showToast_fn:R.showToast_fn, showToast_works:R.showToast_works,
 launchBtn_wired: !!R.launchBtn_onclick, soloBtn_present:R.soloBtn_present, nameInput_wired: !!R.nameInput_onkeydown,
 bridge_read:R.bridge_read, bridge_write:R.bridge_write, solo_hidesLobby:R.solo_hidesLobby,
 kbd_move:R.kbd_move, kbd_boost:R.kbd_boost, kbd_brake:R.kbd_brake, zoomMap_noError:R.zoomMap_noError,
 cheat_fuel:R.cheat_fuel, cheat_resources:R.cheat_resources, cheat_spawnpod:R.cheat_spawnpod,
 canvasShoot_safe:R.canvasShoot_safe, save_key:(R.save_key&&R.save_key.length>0),
 reload_bridge:R.reload_bridge, reload_binds:R.reload_binds, reload_saveKept:R.reload_saveKept,
 reload_noNewErr:R.reload_noNewErr, reload_booted:R.reload_booted, devlog_clean:R.devlog_clean,
 zero_errors: errors.length===0,
};
const failed = Object.entries(checks).filter(([k,v])=>!v).map(([k])=>k);
console.log('FAILED CHECKS:', failed.length? failed.join(', ') : 'NONE');
console.log(failed.length? 'PHASE0 REVIEW VERIFY: FAIL' : 'PHASE0 REVIEW VERIFY: PASS');
if(failed.length) process.exit(1);
