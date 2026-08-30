// HUD readability / collision pass regression.
// Verifies: zero vertical row overlap + zero horizontal label/gauge/value overlap,
// across HUD states x resolutions. Screenshots each state for visual confirmation.
import { chromium } from 'playwright';
const URL = 'http://localhost:8420/driftbound_flight_test.html';
const DEV = String.raw`C:\Users\diepowel\Documents\DRIFTBOUND\_dev`;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE_ERR: ' + m.text()); });

await page.goto(URL, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
await page.click('text=PLAY SOLO');
await page.waitForTimeout(1000);
// enable bounds capture + collision boxes
await page.evaluate(() => { _hudBounds = []; diagMode = true; });

const STATES = {
  full_fuel:      () => { ship.fuel = FUEL_CAPACITY; ship.ore = 0; ship.mineral = 0; ship.armalcolite = 0; attachedPods.length = 0; mineTarget = null; },
  low_fuel:       () => { ship.fuel = FUEL_CAPACITY * 0.1; },
  empty_fuel:     () => { ship.fuel = 0; },
  empty_cargo:    () => { ship.fuel = FUEL_CAPACITY; ship.ore = 0; ship.mineral = 0; ship.armalcolite = 0; },
  multi_resource: () => { ship.ore = 25; ship.mineral = 10; ship.armalcolite = 5; },
  attached_pod:   () => { attachedPods.push({ label: 'CARGO POD', color: '#38bdf8', cargoBonus: 20 }); },
  mining_prompt:  () => { const a = asteroids.find(x => x.hp > 0); if (a) { mineTarget = a; mineDist = 42; } },
  refine_prompt:  () => { ship.armalcolite = 5; mineTarget = null; },
  max_rows:       () => { ship.fuel = FUEL_CAPACITY * 0.1; ship.ore = 25; ship.mineral = 10; ship.armalcolite = 5;
                          if (!attachedPods.length) attachedPods.push({ label: 'CARGO POD', color: '#38bdf8', cargoBonus: 20 });
                          const a = asteroids.find(x => x.hp > 0); if (a) { mineTarget = a; mineDist = 42; } },
};
const VIEWPORTS = [[1366,768],[1920,1080],[2560,1440]];

// horizontal-overlap probe: reads live layout columns + measures actual text widths for the
// worst-case rows (SPD/HULL bars carry both a gauge and a right-aligned value).
async function horizontalReport() {
  return await page.evaluate(() => {
    const PAD_X=10, PW=240, PX=14, VALUE_W=60, GAP=8;
    const L = PX+PAD_X, R = PX+PW-PAD_X, LV = L+44, BW = (R-VALUE_W-GAP)-LV;
    ctx.font = '11px "Courier New",monospace';
    const rows = [
      ['SPD', ctx.measureText('SPD').width, ctx.measureText(BOOST_MAX.toFixed(2)).width],
      ['HULL', ctx.measureText('HULL').width, ctx.measureText(ship.hp+' / '+SHIP_MAX_HP).width],
      ['FUEL', ctx.measureText('FUEL').width, ctx.measureText(FUEL_CAPACITY.toFixed(1)+' gal').width],
    ];
    const gaugeRight = LV + BW;
    return rows.map(([name, lw, vw]) => {
      const labelRight = L + lw;
      const valueLeft = R - vw;
      return { name,
        labelClear: labelRight <= LV,       // label ends before gauge starts
        valueClear: valueLeft >= gaugeRight, // value starts after gauge ends
        labelRight:+labelRight.toFixed(1), gaugeStart:LV, gaugeRight:+gaugeRight.toFixed(1), valueLeft:+valueLeft.toFixed(1) };
    });
  });
}

let fail = 0;
for (const [vw, vh] of VIEWPORTS) {
  await page.setViewportSize({ width: vw, height: vh });
  for (const [name, setup] of Object.entries(STATES)) {
    await page.evaluate(setup);
    await page.waitForTimeout(120); // a few frames so _hudBounds repopulates
    const bounds = await page.evaluate(() => _hudBounds.slice());
    // vertical overlap check (allow shared edges; flag interior overlap > 0.5px)
    let vOverlap = [];
    for (let i = 1; i < bounds.length; i++) {
      const prev = bounds[i-1], cur = bounds[i];
      if (cur.y0 < prev.y1 - 0.5) vOverlap.push({ i, prevY1:+prev.y1.toFixed(1), curY0:+cur.y0.toFixed(1) });
    }
    const hz = await horizontalReport();
    const hBad = hz.filter(r => !r.labelClear || !r.valueClear);
    const ok = vOverlap.length === 0 && hBad.length === 0;
    if (!ok) fail++;
    if (vw === 1920) await page.screenshot({ path: `${DEV}\\hud_${name}.png` });
    console.log(`[${vw}x${vh}] ${name.padEnd(15)} rows=${bounds.length} vOverlap=${vOverlap.length} hBad=${hBad.length} ${ok?'OK':'FAIL'}`);
    if (vOverlap.length) console.log('     vertical:', JSON.stringify(vOverlap));
    if (hBad.length) console.log('     horizontal:', JSON.stringify(hBad));
  }
}
console.log('\nERRORS:', errors.length); errors.forEach(e => console.log('  ', e));
console.log(fail === 0 && errors.length === 0 ? 'RESULT: PASS' : `RESULT: FAIL (${fail} bad states)`);
await browser.close();
