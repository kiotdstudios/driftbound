// MAP INPUT SUPPRESSION REGRESSION
// Proves that when the regional map is open, no direction key produces
// ship acceleration. Closing the map immediately restores input.
//
// Run: node _dev/map_input_suppression_verify.mjs  (dev server on :8420)
import { chromium } from 'playwright';
const URL = 'http://localhost:8420/index.html';
const b = await chromium.launch({ headless: true });
const p = await b.newPage();
const con = [];
p.on('console', m => { if (m.type() === 'error') con.push('ERR: ' + m.text()); });
p.on('pageerror', e => con.push('PAGEERROR: ' + e.message));
await p.goto(URL, { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(1500);
await p.click('text=PLAY SOLO');
await p.waitForTimeout(800);

let PASS = 0, FAIL = 0;
const chk = (name, cond, detail = '') => {
  if (cond) { PASS++; console.log(`  PASS  ${name}`); }
  else       { FAIL++; console.log(`  FAIL  ${name}  ${detail}`); }
};

// Helper: zero velocity, clear map state, ensure flight mode
async function reset() {
  await p.evaluate(() => {
    const DB = window.__DB;
    DB.ship.vx = 0; DB.ship.vy = 0;
    DB.ship.mineCooldown = 0;
    DB.mapOpen = false;
    DB.interiorMode = false; DB.interiorFadeDir = 0;
  });
  await p.waitForTimeout(100);
}

// Helper: hold a key for N ms, return {vx, vy, ax, ay, thrusting} after
async function holdKey(code, ms) {
  await p.keyboard.down(code);
  await p.waitForTimeout(ms);
  const s = await p.evaluate(() => ({
    vx: window.__DB.ship.vx,
    vy: window.__DB.ship.vy,
    ax: window.__DB.dbgAX,
    ay: window.__DB.dbgAY,
    thrusting: window.__DB.thrusting,
  }));
  await p.keyboard.up(code);
  return s;
}

// ── [1] Map CLOSED: W key produces forward acceleration ──────────────────────
console.log('\n[1] Map closed + W → acceleration (baseline)');
con.length = 0;
await reset();
const s1 = await holdKey('KeyW', 300);
chk('vy became negative (forward thrust)', s1.vy < -0.01, `vy=${s1.vy.toFixed(4)}`);
chk('thrusting flag is true', s1.thrusting === true, String(s1.thrusting));
chk('0 console errors', con.length === 0, con.join(' | '));

// ── [2] Map CLOSED: S key produces reverse acceleration ──────────────────────
console.log('\n[2] Map closed + S → reverse acceleration');
con.length = 0;
await reset();
const s2 = await holdKey('KeyS', 300);
chk('vy became positive (reverse thrust)', s2.vy > 0.01, `vy=${s2.vy.toFixed(4)}`);

// ── [3] Map CLOSED: D key produces strafe ───────────────────────────────────
console.log('\n[3] Map closed + D → strafe right');
con.length = 0;
await reset();
const s3 = await holdKey('KeyD', 300);
chk('vx became positive (strafe right)', s3.vx > 0.01, `vx=${s3.vx.toFixed(4)}`);

// ── [4] Map OPEN: W key → NO acceleration ────────────────────────────────────
console.log('\n[4] Map open + W → no acceleration');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
const s4 = await holdKey('KeyW', 300);
chk('vy stays at zero (no forward thrust)', Math.abs(s4.vy) < 0.02, `vy=${s4.vy.toFixed(4)}`);
chk('thrusting flag is false', s4.thrusting === false, String(s4.thrusting));
chk('0 console errors while map open', con.length === 0, con.join(' | '));

// ── [5] Map OPEN: S key → NO acceleration ────────────────────────────────────
console.log('\n[5] Map open + S → no acceleration');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
const s5 = await holdKey('KeyS', 300);
chk('vy stays at zero (no reverse thrust)', Math.abs(s5.vy) < 0.02, `vy=${s5.vy.toFixed(4)}`);

// ── [6] Map OPEN: D key → NO strafe ──────────────────────────────────────────
console.log('\n[6] Map open + D → no strafe (the pre-fix bug direction)');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
const s6 = await holdKey('KeyD', 300);
chk('vx stays at zero (no strafe right)', Math.abs(s6.vx) < 0.02, `vx=${s6.vx.toFixed(4)}`);

// ── [7] Map OPEN: A key → NO strafe ──────────────────────────────────────────
console.log('\n[7] Map open + A → no strafe (was already guarded, confirm still ok)');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
const s7 = await holdKey('KeyA', 300);
chk('vx stays at zero (no strafe left)', Math.abs(s7.vx) < 0.02, `vx=${s7.vx.toFixed(4)}`);

// ── [8] Map OPEN: velocity still decays (coast logic preserved) ───────────────
console.log('\n[8] Map open: existing velocity decays (coast logic preserved)');
con.length = 0;
await p.evaluate(() => {
  window.__DB.ship.vx = 2.0;
  window.__DB.ship.vy = 2.0;
  window.__DB.mapOpen = true;
});
await p.waitForTimeout(500);
const s8 = await p.evaluate(() => ({ vx: window.__DB.ship.vx, vy: window.__DB.ship.vy }));
chk('vx decayed from 2.0 (not frozen, not persisted)', s8.vx < 1.8 && s8.vx >= 0, `vx=${s8.vx.toFixed(4)}`);
chk('vy decayed from 2.0', s8.vy < 1.8 && s8.vy >= 0, `vy=${s8.vy.toFixed(4)}`);

// ── [9] Map CLOSE → controls restore immediately ─────────────────────────────
console.log('\n[9] Map close → W key works again');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
await p.evaluate(() => { window.__DB.mapOpen = false; });
await p.waitForTimeout(50);
const s9 = await holdKey('KeyW', 300);
chk('vy became negative after map closed', s9.vy < -0.01, `vy=${s9.vy.toFixed(4)}`);
chk('thrusting resumes after close', s9.thrusting === true, String(s9.thrusting));
chk('0 console errors after close', con.length === 0, con.join(' | '));

// ── [10] Boost suppressed while map open ─────────────────────────────────────
console.log('\n[10] Map open: boost (Shift+W) still suppressed');
con.length = 0;
await reset();
await p.evaluate(() => { window.__DB.ship.fuel = 100; window.__DB.mapOpen = true; });
await p.waitForTimeout(50);
await p.keyboard.down('ShiftLeft');
const s10 = await holdKey('KeyW', 300);
await p.keyboard.up('ShiftLeft');
chk('no acceleration with Shift+W while map open', Math.abs(s10.vy) < 0.02, `vy=${s10.vy.toFixed(4)}`);
chk('boosting flag false while map open', await p.evaluate(() => window.__DB?.boosting !== true));

console.log(`\n===== ${FAIL === 0 ? 'ALL PASS' : 'FAIL'}  ${PASS} passed, ${FAIL} failed =====`);
await b.close();
process.exit(FAIL === 0 ? 0 : 1);
