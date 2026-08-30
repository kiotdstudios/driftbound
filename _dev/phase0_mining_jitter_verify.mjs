// Regression guard for the asteroid shake-jitter render path (jx/jy locals in
// drawAsteroids). A prior extraction was reported to drop the jx declaration,
// producing "ReferenceError: jx is not defined" every frame an asteroid is
// visible. This forces flashTimer>0 + damage so the jitter translate, crack
// overlay, spark particles, and [E] MINE hint all execute, and asserts zero
// runtime errors. Run against the MODULAR build (index.html), hard-loaded.
import { chromium } from 'playwright';
const URL = process.env.DB_URL || 'http://localhost:8420/index.html';
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
const errs = [];
pg.on('pageerror', e => errs.push('PAGEERR: ' + e.message));
pg.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
await pg.goto(URL, { waitUntil: 'domcontentloaded' });
await pg.waitForTimeout(3500);
await pg.click('text=PLAY SOLO');
await pg.waitForTimeout(800);

// RUNTIME READY log (fires ~800ms after loop start)
await pg.waitForTimeout(1200);
const runtime = await pg.evaluate(() => {
  const es = (window.__DB.DevLog && window.__DB.DevLog.entries) || [];
  const r = es.find(e => String(e.message||'').includes('RUNTIME READY'));
  return r ? r.message : '(no RUNTIME READY log)';
});
const critCount = await pg.evaluate(() => {
  const es = (window.__DB.DevLog && window.__DB.DevLog.entries) || [];
  return es.filter(e => (e.level==='CRITICAL'||e.level==='ERROR') && e.system==='RuntimeError').length;
});

// Force the jitter render path on every asteroid near the ship
const forced = await pg.evaluate(() => {
  const a = window.__DB.asteroids;
  if (!a || !a.length) return { ok:false, msg:'no asteroids' };
  const f = a[0];
  window.__DB.ship.worldX = f.worldX; window.__DB.ship.worldY = f.worldY;
  let n = 0;
  for (const ast of a) {
    if (Math.hypot(ast.worldX-f.worldX, ast.worldY-f.worldY) < 1200) {
      ast.flashTimer = 8; ast.hp = ast.maxHp * 0.3; n++;
    }
  }
  return { ok:true, n };
});
await pg.waitForTimeout(1500); // ~90 frames rendered with flashTimer>0

const pass = errs.length === 0 && critCount === 0 && runtime.includes('PASS') && forced.ok && forced.n > 0;
console.log(JSON.stringify({ runtime, critCount, forced, errCount: errs.length, errs: errs.slice(0,8) }, null, 2));
console.log('PHASE0 MINING JITTER VERIFY: ' + (pass ? 'PASS' : 'FAIL'));
await b.close();
process.exit(pass ? 0 : 1);
