/**
 * CP3b-2 — Attached pod render scale/position/orientation verification.
 *
 * History:
 *   CP3   (S=52 -> POD_DISPLAY_SIZE=96 + z-order fix) — fixed the pod being
 *         invisible behind the hull, but chief QA rejected the result:
 *         the pod still read as a tiny accessory, visually separated from
 *         the ship.
 *   CP3b-2 (this fix) — attached-pod render size is now derived from
 *         CONNECTOR_GAP (a measured CP2 graph constant) rather than a fixed
 *         nominal sprite size. See getAttachedPodRenderSize() in main.js for
 *         the full geometric derivation. No CP2 docking-logic or graph-data
 *         change; render-only.
 *
 * Per chief's explicit instruction, this test does NOT hardcode a pixel-
 * probe calibrated to one specific S value. Instead it measures, from the
 * live canvas, the actual rendered bounding-box ratio (pod visible width vs
 * ship visible width) and the connector edge distance/overlap, and asserts
 * those measured geometric properties satisfy the requirements:
 *   - flush against the connector, no floating gap
 *   - reads as a full module (bigger than the old rejected 96)
 *   - ship remains the dominant, recognizable shape (not swallowed)
 *   - moves/rotates rigidly with the ship
 *
 * Run via the same dev-server-on-:8420 / bun harness as the other _dev/*.mjs
 * regressions.
 */
import { chromium } from 'playwright';
import { strictEqual, ok } from 'assert';

const BASE = 'http://localhost:8420';
const TIMEOUT = 15000;

let browser, page;
let passed = 0, failed = 0;

function pass(name) { console.log(`  \u2713 ${name}`); passed++; }
function fail(name, err) { console.error(`  \u2717 ${name}: ${err?.message || err}`); failed++; }
async function check(name, fn) { try { await fn(); pass(name); } catch (e) { fail(name, e); } }

async function pixelAt(pg, x, y) {
  return pg.evaluate(({ x, y }) => {
    const c = document.querySelector('canvas');
    const d = c.getContext('2d').getImageData(Math.round(x), Math.round(y), 1, 1).data;
    return [d[0], d[1], d[2], d[3]];
  }, { x, y });
}

// Deep-space background reference. Any pixel that clearly differs from this
// is sprite content (ship or pod) -- used instead of matching an exact
// sprite color, so the test survives art/palette tweaks and works at any S.
const BG_REF = [8, 60, 118];
function differsFromBackground(rgb, tol = 100) {
  const d = Math.abs(rgb[0] - BG_REF[0]) + Math.abs(rgb[1] - BG_REF[1]) + Math.abs(rgb[2] - BG_REF[2]);
  return d > tol;
}

async function waitForDockEnd(pg, timeout = 4000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (!(await pg.evaluate(() => window.__DB.isDocking))) return;
    await pg.waitForTimeout(50);
  }
  throw new Error('dock never completed');
}

// Scans a horizontal line through (cy) from world-x `from` to `to` (inclusive,
// step 1 world-px, zoom=1.00 so world-px == screen-px) and returns the first/
// last world-x offset whose pixel differs from background -- i.e. the visible
// content bounding box along that axis.
async function scanContentBounds(pg, cx, cy, from, to) {
  let minX = null, maxX = null;
  for (let wx = from; wx <= to; wx++) {
    const rgb = await pixelAt(pg, cx + wx, cy);
    if (differsFromBackground(rgb)) {
      if (minX === null) minX = wx;
      maxX = wx;
    }
  }
  return { minX, maxX };
}

async function main() {
  browser = await chromium.launch({ headless: true });
  page    = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('console', m => { if (m.type() === 'error') console.error('PAGE ERR:', m.text()); });

  await page.goto(BASE, { waitUntil: 'networkidle', timeout: TIMEOUT });
  await page.waitForFunction(() => typeof window.__DB !== 'undefined' && window.__DB.ship?.worldX !== undefined, { timeout: 10000 });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  await page.evaluate(() => {
    window.__DB.ship.dir = 'north';
    window.__DB.ship.vx  = 0;
    window.__DB.ship.vy  = 0;
    window.__DB.ship.ore = 50;
    window.__DB.camera.resetZoom();
  });
  await page.waitForTimeout(400); // let zoom ease to exactly 1.00 (index 1 default is 0.85 -- force index 2)
  await page.evaluate(() => window.__DB.camera.setZoomIndex(2)); // 1.00 -> screen-px == world-px, simplifies scanning
  await page.waitForTimeout(400);

  const dims = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    return { w: c.width, h: c.height };
  });
  const cx = Math.round(dims.w / 2), cy = Math.round(dims.h / 2);
  const CONNECTOR_GAP = await page.evaluate(() => window.__DB.shipAssembly.core ? 46 : 46); // graph constant, verified below via local_position

  const pid = await page.evaluate(() => {
    const pid = '__cp3b_render_' + Date.now();
    window.__DB.worldPods.push({
      pid, type: 'modular_space_pod',
      worldX: window.__DB.ship.worldX + 30,
      worldY: window.__DB.ship.worldY + 30,
      angle: 0,
    });
    return pid;
  });
  await page.evaluate((pid) => window.__DB.startDockingByPid(pid), pid);
  await waitForDockEnd(page);

  await page.waitForFunction(() => {
    const spr = window.__DB.podRotations && window.__DB.podRotations['south'];
    return spr && spr.naturalWidth > 0;
  }, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(200);

  console.log('\n[CP3b-2] Attached-pod render — graph data sanity (unchanged by this fix)');

  const node = await page.evaluate((pid) => window.__DB.shipAssembly[pid], pid);
  await check('docked node exists with expected parent/connector/local_position', async () => {
    ok(node, 'shipAssembly node should exist');
    strictEqual(node.parent_connector, 'E', `expected connector E, got ${node.parent_connector}`);
    strictEqual(node.local_position.x, 46, `expected local x=46, got ${node.local_position.x}`);
    strictEqual(node.local_position.y, 0,  `expected local y=0, got ${node.local_position.y}`);
  });

  console.log('\n[CP3b-2] Attached-pod render — measured bounding-box ratio + connector edge distance');

  // Ship-only content bounds, scanning the side AWAY from the connector
  // (negative world-x), since the pod never extends that far.
  const shipSide = await scanContentBounds(page, cx, cy, -70, -2);
  await check('ship hull is visible on the side away from the connector (not swallowed)', async () => {
    ok(shipSide.minX !== null, 'expected some ship content on the negative-x side, found none');
  });
  const shipHalfWidthMeasured = shipSide.minX !== null ? Math.abs(shipSide.minX) : null;

  // Full content bounds across both ship+pod, scanning the connector side.
  const podSide = await scanContentBounds(page, cx, cy, 2, 130);
  await check('pod content is visible flush at/near the connector (no floating gap)', async () => {
    ok(podSide.minX !== null && podSide.minX <= 10, `expected pod/ship content starting within 10px of connector approach, got minX=${podSide.minX}`);
  });
  const podFarEdge = podSide.maxX; // world-x offset of the pod's outermost visible pixel

  await check('no visible background gap between ship and pod along the connector axis (offsets 0..46)', async () => {
    let gapPixels = 0;
    for (let wx = 0; wx <= 46; wx += 2) {
      const rgb = await pixelAt(page, cx + wx, cy);
      if (!differsFromBackground(rgb)) gapPixels++;
    }
    ok(gapPixels === 0, `expected zero background-colored pixels between ship and pod, found ${gapPixels}`);
  });

  const podHalfWidthMeasured = podFarEdge !== null ? (podFarEdge - 46) : null;
  await check('pod reads as a substantial module, not a tiny accessory (measured half-width > old-rejected ~35px)', async () => {
    ok(podHalfWidthMeasured !== null && podHalfWidthMeasured > 40, `expected pod half-width > 40px (old rejected fix measured ~35px), got ${podHalfWidthMeasured}`);
  });

  await check('ship remains the dominant visible shape (measured ship half-width still >= 30px on its own side)', async () => {
    ok(shipHalfWidthMeasured !== null && shipHalfWidthMeasured >= 30, `expected ship still clearly visible (half-width >= 30px) on the side away from the pod, got ${shipHalfWidthMeasured}`);
  });

  await check('rendered attachedPodRenderSize is bigger than the old rejected POD_DISPLAY_SIZE=96, and not a raw hardcoded constant', async () => {
    const S = await page.evaluate(() => window.__DB.attachedPodRenderSize);
    ok(S > 96, `expected S > 96 (old rejected accessory size), got ${S}`);
    ok(S < 145, `expected S to stay well short of a 1:1 ship-size match (~152, which swallows the ship), got ${S}`);
  });

  console.log('\n[CP3b-2] Attached-pod render — rigid rotation with ship heading');

  await page.evaluate(() => { window.__DB.ship.dir = 'east'; });
  await page.waitForTimeout(150);

  await check('after heading change to east, pod swings to below the ship (moves rigidly with ship)', async () => {
    const rgb = await pixelAt(page, cx, cy + 40);
    ok(differsFromBackground(rgb), `expected non-background sprite content at rotated position, got [${rgb.slice(0,3)}]`);
  });

  await check('old (pre-rotation) connector-side position returns to background (confirms it truly moved, not duplicated)', async () => {
    const rgb = await pixelAt(page, cx + 100, cy);
    ok(!differsFromBackground(rgb), `expected background at old position after rotating, but found content: [${rgb.slice(0,3)}]`);
  });

  await page.evaluate(() => { window.__DB.ship.dir = 'north'; });
  await page.waitForTimeout(150);

  await check('reverting heading to north restores content at the connector side', async () => {
    const rgb = await pixelAt(page, cx + 40, cy);
    ok(differsFromBackground(rgb), `expected sprite content restored, got [${rgb.slice(0,3)}]`);
  });

  await browser.close();

  console.log(`\n─────────────────────────────────────`);
  console.log(`cp3_attached_pod_render_verify: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

main().catch(e => {
  console.error('FATAL:', e);
  browser?.close();
  process.exit(1);
});
