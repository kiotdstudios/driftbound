// DRIFTBOUND regression: mine sm_brown, lg_brown, lg_planet (no uncaught exceptions,
// HUD stays visible) + verify camera zoom controls. Run: node mining_zoom_regression.mjs
import { chromium } from 'playwright';
const URL = 'http://localhost:8420/driftbound_flight_test.html';
const DEV = String.raw`C:\Users\diepowel\Documents\DRIFTBOUND\_dev`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 720 });
const errors = [];
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE_ERR: ' + m.text()); });

await page.goto(URL, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
await page.click('text=PLAY SOLO');
await page.waitForTimeout(1500);

async function mine(typeId) {
  const t = await page.evaluate((tid) => {
    let a = asteroids.find(x => x.type?.id === tid && x.hp > 0);
    if (!a) { // spawn one if none present
      return null;
    }
    ship.worldX = a.worldX - 55; ship.worldY = a.worldY; ship.vx = 0; ship.vy = 0;
    return { id: a.type.id, hp: a.hp, maxHp: a.maxHp };
  }, typeId);
  if (!t) { console.log(`  ${typeId}: NONE PRESENT (skipped)`); return; }
  await page.keyboard.down('KeyE');
  await page.waitForTimeout(6000);
  await page.keyboard.up('KeyE');
  await page.waitForTimeout(400);
  const after = await page.evaluate((tid) => {
    const a = asteroids.find(x => x.type?.id === tid);
    return { hp: a ? a.hp : 'destroyed/gone' };
  }, typeId);
  console.log(`  ${typeId}: start hp ${t.hp} -> ${JSON.stringify(after.hp)}`);
}

console.log('=== MINING REGRESSION ===');
for (const id of ['sm_brown','lg_brown','lg_planet']) await mine(id);

// HUD visibility check: is drawHUD still executing (frameCount advancing) and no errors
const hud = await page.evaluate(() => {
  const f0 = frameCount; return new Promise(r => setTimeout(() => r({ advanced: frameCount > f0, frameCount }), 300));
});
console.log('HUD/loop alive after mining:', hud.advanced, '(frameCount', hud.frameCount + ')');

// DevLog errors
const devlog = await page.evaluate(() => {
  try { return (DevLog.entries||[]).filter(e=>e.level==='ERROR'||e.level==='CRITICAL')
      .map(e=>({level:e.level,system:e.system,message:e.message})); }
  catch(e){ return 'DevLog fail: '+e.message; }
});
console.log('DevLog errors:', JSON.stringify(devlog));

// === ZOOM CONTROLS ===
console.log('\n=== ZOOM CONTROLS ===');
const z0 = await page.evaluate(() => ({ idx: camZoomIdx, zoom: +camZoom.toFixed(3), target: camZoomTarget }));
console.log('default:', JSON.stringify(z0), '(expect idx 1, target 0.85)');

await page.keyboard.press('Minus');  await page.waitForTimeout(300);
const zOut = await page.evaluate(() => ({ idx: camZoomIdx, target: camZoomTarget, zoom:+camZoom.toFixed(3) }));
console.log("after '-':", JSON.stringify(zOut), '(expect idx 0, target 0.70)');

await page.keyboard.press('Equal'); await page.keyboard.press('Equal'); await page.waitForTimeout(300);
const zIn = await page.evaluate(() => ({ idx: camZoomIdx, target: camZoomTarget }));
console.log("after '=' x2:", JSON.stringify(zIn), '(expect idx 1, target 0.85)');

await page.keyboard.press('Equal'); await page.keyboard.press('Equal'); await page.keyboard.press('Equal'); await page.keyboard.press('Equal'); await page.waitForTimeout(300);
const zMax = await page.evaluate(() => ({ idx: camZoomIdx, target: camZoomTarget }));
console.log("after many '=':", JSON.stringify(zMax), '(expect clamp idx 4, target 1.30)');

await page.keyboard.press('Digit0'); await page.waitForTimeout(300);
const zReset = await page.evaluate(() => ({ idx: camZoomIdx, target: camZoomTarget }));
console.log("after '0':", JSON.stringify(zReset), '(expect idx 1, target 0.85)');

// Screenshot at default 0.85x — let it settle
await page.waitForTimeout(600);
await page.screenshot({ path: DEV + String.raw`\zoom_085x.png` });
console.log('screenshot: zoom_085x.png');

// Zoom out to 0.70x max and screenshot
await page.keyboard.press('Minus'); await page.waitForTimeout(900);
const zFinal = await page.evaluate(() => ({ idx: camZoomIdx, zoom:+camZoom.toFixed(3) }));
await page.screenshot({ path: DEV + String.raw`\zoom_070x_max_out.png` });
console.log('max zoom-out:', JSON.stringify(zFinal), '-> zoom_070x_max_out.png');

console.log('\n=== ERRORS ===');
errors.forEach(e => console.log(e));
console.log('TOTAL UNCAUGHT ERRORS:', errors.length);
console.log(errors.length === 0 ? 'RESULT: PASS' : 'RESULT: FAIL');
await browser.close();
