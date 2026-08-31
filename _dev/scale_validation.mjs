import { chromium } from 'playwright';

// MIGRATED (Test Harness Migration checkpoint): targets modular index.html via window.__DB
// bridge instead of legacy bare globals. Assertions/intent unchanged.
// KNOWN STALE: the ship-smaller-than-lg_planet assertion is EXPECTED to read FAIL —
// asteroid scale was intentionally reverted per art direction after this test was written.
// This is a pre-existing, chief-acknowledged non-regression; do not "fix" by changing
// asteroid scale. Classify this file's result separately from the rest of the suite.

const browser = await chromium.launch({ headless: true });
const page    = await browser.newPage();
const errors  = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console',   m => { if (m.type()==='error') errors.push(m.text()); });

await page.setViewportSize({ width: 1920, height: 1080 });
await page.goto('http://localhost:8420/index.html', { waitUntil: 'load' });
await page.waitForTimeout(600);
const solo = page.locator('text=PLAY SOLO');
if (await solo.count() > 0) await solo.click();
await page.waitForTimeout(1800);

// ── Runtime checks ──
const result = await page.evaluate(() => {
  const DB = window.__DB;
  const devMode    = DB.DEV_MODE === true;
  const devCmds    = DB.DEV_COMMANDS ? Object.keys(DB.DEV_COMMANDS) : [];
  const astScale   = DB.ASTEROID_TYPES.map(t => ({ id: t.id, renderedW: t.w * t.scale, renderedH: t.h * t.scale }));
  const rr         = DB.DevLog.entries.find(e => e.message?.includes('RUNTIME READY'));
  const mineRangeOk = DB.MINE_RANGE === 140;
  // Check ship is not visually larger than lg_planet
  const shipW      = 68 * 2; // SPRITE_SIZE * DISPLAY_SCALE
  const lgPlanet   = DB.ASTEROID_TYPES.find(t => t.id === 'lg_planet');
  const planetRendW = lgPlanet ? lgPlanet.w * lgPlanet.scale : 0;
  return {
    devMode, devCmds, astScale, rr: rr?.message, mineRangeOk,
    shipW, planetRendW,
    shipSmallerThanPlanet: shipW < planetRendW,
  };
});

const shot = 'C:\\Users\\diepowel\\Documents\\driftbound_work\\integration\\_dev\\scale_final.png';
await page.screenshot({ path: shot });

// Press / to test fuel cheat
await page.keyboard.press('/');
await page.waitForTimeout(400);

// Press R to give resources
await page.keyboard.press('r');
await page.waitForTimeout(400);

// Open F2 diagnostics
await page.keyboard.press('F2');
await page.waitForTimeout(500);
const shotF2 = 'C:\\Users\\diepowel\\Documents\\driftbound_work\\integration\\_dev\\scale_diag_f2.png';
await page.screenshot({ path: shotF2 });

console.log('\n══════════════════════════════════════');
console.log('SCALE + DEV VALIDATION  (KNOWN STALE — see header)');
console.log('══════════════════════════════════════');
console.log(`[ ${errors.length===0?'✓':'✗'} ] Zero uncaught exceptions (${errors.length} found)`);
if (errors.length) errors.forEach(e=>console.log('  ✗',e));
console.log(`[ ${result.rr?.includes('PASS')?'✓':'?'} ] RUNTIME READY: ${result.rr}`);
console.log(`[ ${result.devMode?'✓':'✗'} ] DEV_MODE = true`);
console.log(`[ ${result.devCmds.length===5?'✓':'✗'} ] DEV_COMMANDS has 5 entries: ${result.devCmds.join(', ')}`);
console.log(`[ ${result.mineRangeOk?'✓':'✗'} ] MINE_RANGE = 140 (unchanged)`);
console.log(`[ ${result.shipSmallerThanPlanet?'✓':'✗ (KNOWN STALE — asteroid scale intentionally reverted)'} ] Ship (${result.shipW}px) < lg_planet (${result.planetRendW}px)`);
result.astScale.forEach(a => {
  const rel = a.renderedW > result.shipW ? 'LARGER' : 'smaller';
  console.log(`  asteroid ${a.id}: ${a.renderedW}×${a.renderedH}px → ${rel} than ship`);
});
console.log(`[ ✓ ] Screenshots: scale_final.png, scale_diag_f2.png`);
console.log('══════════════════════════════════════\n');

await browser.close();
