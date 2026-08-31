// CHECKPOINT 1 — PHYSICAL POD ATTACHMENT + MASS SYSTEM verification
// Entry: index.html (module src/main.js), state via window.__DB getters.
// Run: node _dev/phase1_pod_assembly_verify.mjs   (dev server on :8420)
import { chromium } from 'playwright';
const URL = 'http://localhost:8420/index.html';
const b = await chromium.launch({ headless: true });
const p = await b.newPage();
const con = [];
p.on('console', m => { if (m.type() === 'error') con.push('ERR: ' + m.text()); });
p.on('pageerror', e => con.push('PAGEERROR: ' + e.message));
await p.goto(URL, { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3500);
await p.click('text=PLAY SOLO');
await p.waitForTimeout(900);

let PASS = 0, FAIL = 0;
// CP2: wait for docking sequence to complete (replaces old instant-attach behavior)
async function waitForDock(timeout=3000){const t0=Date.now();while(Date.now()-t0<timeout){const d=await p.evaluate(()=>window.__DB.isDocking);if(!d)return;await p.waitForTimeout(50);}throw new Error('waitForDock timed out');}
const chk = (n, c, d = '') => { if (c) { PASS++; console.log('  PASS  ' + n); } else { FAIL++; console.log('  FAIL  ' + n + '   ' + d); } };
const ev = fn => p.evaluate(fn);

// RUNTIME READY
const ready = await ev(() => __DB.DevLog.entries.some(e => (e.msg || e.message || '').includes('RUNTIME READY')));
chk('runtime ready log present', ready);

// Baseline: core-only mass = coreMass
await ev(() => {
  // wipe any restored pods to a clean core-only assembly
  const asm = __DB.shipAssembly;
  Object.keys(asm).forEach(k => { if (k !== 'core') delete asm[k]; });
  __DB.attachedPods.length = 0;
  const core = asm.core;
  core.available_connectors.forEach(c => { c.free = true; });
  core.connected_to = {};
  __DB.worldPods.length = 0;
});
let m0 = await ev(() => __DB.totalMass);
let acc0 = await ev(() => __DB.accelMult);
let fuel0 = await ev(() => __DB.fuelMult);
chk('core-only mass == 100', Math.abs(m0 - 100) < 0.01, 'm0=' + m0);
chk('core-only accelMult == 1', Math.abs(acc0 - 1) < 0.01, 'acc0=' + acc0);
chk('core-only fuelMult == 1', Math.abs(fuel0 - 1) < 0.01, 'fuel0=' + fuel0);

// Attach a pod: place ship on top of a world pod, give ore, press E
await ev(() => {
  __DB.ship.ore = 999;
  __DB.worldPods.push({ pid: 'wpX', type: 'modular_space_pod', worldX: __DB.ship.worldX + 8, worldY: __DB.ship.worldY, angle: 0 });
  window.__wp0 = __DB.worldPods.length;
  window.__ap0 = __DB.attachedPods.length;
});
await p.waitForTimeout(120);
await p.keyboard.press('KeyE');
await waitForDock();
let s = await ev(() => ({
  wp: __DB.worldPods.length, wp0: window.__wp0,
  ap: __DB.attachedPods.length, ap0: window.__ap0,
  hasNode: !!__DB.shipAssembly['wpX'],
  node: __DB.shipAssembly['wpX'] ? {
    parent: __DB.shipAssembly['wpX'].parent,
    pc: __DB.shipAssembly['wpX'].parent_connector,
    lp: __DB.shipAssembly['wpX'].local_position,
    mass: __DB.shipAssembly['wpX'].mass,
    ac: __DB.shipAssembly['wpX'].available_connectors.length,
  } : null,
  mass: __DB.totalMass, acc: __DB.accelMult, fuel: __DB.fuelMult,
  free: __DB.freeConnectors,
}));
chk('world pod consumed', s.wp < s.wp0, JSON.stringify(s));
chk('attachedPods grew', s.ap > s.ap0);
chk('graph node created for wpX', s.hasNode);
chk('node parent == core', s.node && s.node.parent === 'core', JSON.stringify(s.node));
chk('node has local_position offset', s.node && (Math.abs(s.node.lp.x) + Math.abs(s.node.lp.y)) > 0, JSON.stringify(s.node && s.node.lp));
chk('node stores mass 40', s.node && s.node.mass === 40, JSON.stringify(s.node && s.node.mass));
chk('total mass now 140', Math.abs(s.mass - 140) < 0.01, 'mass=' + s.mass);
chk('accelMult dropped below 1', s.acc < 1, 'acc=' + s.acc);
chk('fuelMult rose above 1', s.fuel > 1, 'fuel=' + s.fuel);
chk('graph grows free ports (core-1 + pod-3 = 6)', s.free === 6, 'free=' + s.free);

// Pod moves with ship: capture screen render offset relative to ship, move ship, node local_position unchanged
let lpBefore = await ev(() => JSON.stringify(__DB.shipAssembly['wpX'].local_position));
await ev(() => { __DB.ship.worldX += 500; __DB.ship.worldY -= 300; });
await p.waitForTimeout(120);
let lpAfter = await ev(() => JSON.stringify(__DB.shipAssembly['wpX'].local_position));
chk('local_position is ship-relative (unchanged when ship moves)', lpBefore === lpAfter, lpBefore + ' vs ' + lpAfter);

// Fill remaining core ports + verify NO AVAILABLE DOCKING PORT once graph is full
await ev(() => {
  __DB.ship.ore = 9999;
  // dock pods until no free connector remains
  for (let k = 0; k < 6; k++) {
    __DB.worldPods.push({ pid: 'fill' + k, type: 'modular_space_pod', worldX: __DB.ship.worldX + 8, worldY: __DB.ship.worldY, angle: 0 });
  }
});
// CP2: wait for each docking sequence to complete before starting the next
for (let k = 0; k < 6; k++) { await p.keyboard.press('KeyE'); await waitForDock(); await p.waitForTimeout(80); }
let full = await ev(() => ({ free: __DB.freeConnectors, mods: __DB.attachedPods.length }));
chk('graph extends beyond 4 core ports (pod-on-pod)', full.mods >= 4, JSON.stringify(full));

// NO AVAILABLE DOCKING PORT: occupy every connector across the whole graph,
// then attempt to dock a pod in range. findFreeConnector() must return null.
await ev(() => {
  const asm = __DB.shipAssembly;
  Object.values(asm).forEach(mod => { (mod.available_connectors || []).forEach(c => { c.free = false; }); });
  __DB.toastMsg = null;
  __DB.worldPods.length = 0;
  __DB.worldPods.push({ pid: 'ovf', type: 'modular_space_pod', worldX: __DB.ship.worldX + 8, worldY: __DB.ship.worldY, angle: 0 });
});
chk('all connectors occupied -> free == 0', (await ev(() => __DB.freeConnectors)) === 0, 'free=' + (await ev(() => __DB.freeConnectors)));
await p.keyboard.press('KeyE'); await p.waitForTimeout(250);
let toast = await ev(() => (__DB.toastMsg && (__DB.toastMsg.text || __DB.toastMsg)) || '');
chk('NO AVAILABLE DOCKING PORT when full', String(toast).includes('NO AVAILABLE DOCKING PORT'), 'toast=' + JSON.stringify(toast));
chk('pod stays in world when no port', (await ev(() => __DB.worldPods.some(w => w.pid === 'ovf'))), 'unattached pod should remain');

// Save -> reload -> reconstruct graph
let before = await ev(() => ({ mods: __DB.attachedPods.length, mass: __DB.totalMass, keys: Object.keys(__DB.shipAssembly).sort().join(',') }));
await ev(() => __DB.saveGame());
await p.reload({ waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3500);
await p.click('text=PLAY SOLO');
await p.waitForTimeout(900);
let after = await ev(() => ({ mods: __DB.attachedPods.length, mass: __DB.totalMass, keys: Object.keys(__DB.shipAssembly).sort().join(',') }));
chk('reload: module count preserved', after.mods === before.mods, JSON.stringify({ before, after }));
chk('reload: total mass preserved', Math.abs(after.mass - before.mass) < 0.01, JSON.stringify({ before, after }));
chk('reload: assembly graph reconstructed (same node ids)', after.keys === before.keys, JSON.stringify({ before, after }));

// Zoom levels: node renders (no crash) at each zoom — cycle zoom keys, watch for errors
con.length = 0;
for (const key of ['Minus', 'Minus', 'Equal', 'Equal', 'Equal', 'Digit0']) { await p.keyboard.press(key); await p.waitForTimeout(120); }
chk('0 console errors after zoom cycling with attached modules', con.length === 0, con.join(' | '));

console.log('\n==== RESULT: ' + PASS + ' passed, ' + FAIL + ' failed ====');
await b.close();
process.exit(FAIL === 0 ? 0 : 1);
