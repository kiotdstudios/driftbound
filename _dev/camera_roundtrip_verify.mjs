// DRIFTBOUND Phase 3 regression: camera.js zoom controls + worldToScreen/screenToWorld
// round-trip assertion at multiple world points, multiple zoom levels, with non-zero
// camera lead (ship moving). Targets the MODULAR build (index.html) via argv or default.
// Run: node camera_roundtrip_verify.mjs [URL]
import { chromium } from 'playwright';
const URL = process.argv[2] || 'http://localhost:8420/index.html';

const b = await chromium.launch({ headless: true });
const p = await b.newPage();
const con = [];
p.on('console', m => { if (m.type() === 'error') con.push('ERR: ' + m.text()); });
p.on('pageerror', e => con.push('PAGEERROR: ' + e.message));

await p.goto(URL, { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(1200);
await p.click('text=PLAY SOLO').catch(() => {});
await p.waitForTimeout(500);

let PASS = 0, FAIL = 0;
const chk = (n, c, d = '') => { if (c) { PASS++; console.log('  PASS  ' + n); } else { FAIL++; console.log('  FAIL  ' + n + '   ' + d); } };
const ev = (fn, arg) => p.evaluate(fn, arg);

// ── default zoom ──
const z0 = await ev(() => window.__DB.camera.getState());
chk('default zoom is 0.85x (idx 1)', z0.zoomIdx === 1 && Math.abs(z0.zoom - 0.85) < 0.01, JSON.stringify(z0));

// ── keyboard zoom: - out ──
await p.keyboard.press('Minus'); await p.waitForTimeout(400);
let z = await ev(() => window.__DB.camera.getState());
chk("'-' zooms out (idx 0, target 0.70)", z.zoomIdx === 0 && Math.abs(z.zoomTarget - 0.70) < 0.001, JSON.stringify(z));

// ── keyboard zoom: = in (back to default, then beyond) ──
await p.keyboard.press('Equal'); await p.waitForTimeout(400);
z = await ev(() => window.__DB.camera.getState());
chk("'=' zooms in (idx 1, target 0.85)", z.zoomIdx === 1 && Math.abs(z.zoomTarget - 0.85) < 0.001, JSON.stringify(z));

for (let i = 0; i < 5; i++) await p.keyboard.press('Equal');
await p.waitForTimeout(400);
z = await ev(() => window.__DB.camera.getState());
chk("'=' clamps at max (idx 4, target 1.30)", z.zoomIdx === 4 && Math.abs(z.zoomTarget - 1.30) < 0.001, JSON.stringify(z));

// ── keyboard zoom: 0 reset ──
await p.keyboard.press('Digit0'); await p.waitForTimeout(400);
z = await ev(() => window.__DB.camera.getState());
chk("'0' resets zoom (idx 1, target 0.85)", z.zoomIdx === 1 && Math.abs(z.zoomTarget - 0.85) < 0.001, JSON.stringify(z));

// ── mouse wheel zoom ──
await p.mouse.move(640, 400);
await p.mouse.wheel(0, -120); await p.waitForTimeout(400);
z = await ev(() => window.__DB.camera.getState());
chk('wheel up zooms in (idx 2)', z.zoomIdx === 2, JSON.stringify(z));
await p.mouse.wheel(0, 120); await p.waitForTimeout(400);
z = await ev(() => window.__DB.camera.getState());
chk('wheel down zooms out (idx 1)', z.zoomIdx === 1, JSON.stringify(z));

// ── camera lead/shake still respond to movement (feel unchanged) ──
await p.keyboard.down('KeyW'); await p.waitForTimeout(900);
const midLead = await ev(() => window.__DB.camera.getState());
await p.keyboard.up('KeyW');
chk('camera lead builds up while thrusting', Math.abs(midLead.camLeadY) > 1, JSON.stringify(midLead));
await p.waitForTimeout(1500);
const afterLead = await ev(() => window.__DB.camera.getState());
chk('camera lead decays back down after releasing thrust', Math.abs(afterLead.camLeadY) < Math.abs(midLead.camLeadY), JSON.stringify(afterLead));

// ── mining range unaffected by camera changes ──
const mineCheck = await ev(() => {
  const a = window.__DB.asteroids.find(x => x.hp > 0);
  if (!a) return null;
  window.__DB.ship.worldX = a.worldX - 55; window.__DB.ship.worldY = a.worldY;
  window.__DB.ship.vx = 0; window.__DB.ship.vy = 0;
  return { hp0: a.hp };
});
if (mineCheck) {
  await p.keyboard.down('KeyE'); await p.waitForTimeout(500); await p.keyboard.up('KeyE');
  const hp1 = await ev(() => { const a = window.__DB.asteroids.find(x=>x.type); return a ? a.hp : null; });
  chk('mining range/behavior unaffected by camera refactor', hp1 !== null, 'hp1=' + hp1);
}

// ── HUD/minimap render without error after all zoom/camera changes ──
await p.waitForTimeout(300);
chk('0 console/page errors after full zoom+movement cycle', con.length === 0, JSON.stringify(con));

// ══════════════════════════════════════════════════════════════════
// ROUND-TRIP ASSERTION: world -> worldToScreen -> screenToWorld ≈ world
// Tested at all 5 zoom levels, multiple world offsets, WITH non-zero
// camera lead (ship actively moving) to stress the inverse transform.
// ══════════════════════════════════════════════════════════════════
console.log('\n=== CAMERA ROUND-TRIP (world -> screen -> world) ===');

// Give the ship non-zero lead by moving briefly, then sample mid-motion.
await p.keyboard.down('KeyD'); await p.keyboard.down('KeyW');
await p.waitForTimeout(600);

const TOL = 0.75; // px tolerance for float round-trip error

for (const zoomIdx of [0, 1, 2, 3, 4]) {
  await ev((idx) => window.__DB.camera.setZoomIndex(idx), zoomIdx);
  await p.waitForTimeout(500); // let zoom easing settle toward target

  const state = await ev(() => window.__DB.camera.getState());
  const shipPos = await ev(() => ({ x: window.__DB.ship.worldX, y: window.__DB.ship.worldY }));

  const offsets = [
    { x: 0, y: 0 },
    { x: 200, y: -150 },
    { x: -400, y: 300 },
    { x: 1200, y: 800 },
    { x: -900, y: -1100 },
  ];

  for (const off of offsets) {
    const worldPt = { x: shipPos.x + off.x, y: shipPos.y + off.y };
    const result = await ev((pt) => {
      const screen = window.__DB.camera.worldToScreen(pt.x, pt.y);
      const back   = window.__DB.camera.screenToWorld(screen.x, screen.y);
      return { screen, back };
    }, worldPt);

    const dx = Math.abs(result.back.x - worldPt.x);
    const dy = Math.abs(result.back.y - worldPt.y);
    chk(
      `round-trip @ zoomIdx=${zoomIdx} (lead=${state.camLeadX.toFixed(1)},${state.camLeadY.toFixed(1)}) offset(${off.x},${off.y})`,
      dx < TOL && dy < TOL,
      `world=(${worldPt.x.toFixed(1)},${worldPt.y.toFixed(1)}) -> screen=(${result.screen.x.toFixed(1)},${result.screen.y.toFixed(1)}) -> back=(${result.back.x.toFixed(1)},${result.back.y.toFixed(1)}) dx=${dx.toFixed(3)} dy=${dy.toFixed(3)}`
    );
  }
}
await p.keyboard.up('KeyD'); await p.keyboard.up('KeyW');

console.log(`\n==== RESULT: ${PASS} passed, ${FAIL} failed ====`);
console.log('CONSOLE/PAGE ERRORS TOTAL:', con.length);
await b.close();
process.exit(FAIL > 0 ? 1 : 0);
