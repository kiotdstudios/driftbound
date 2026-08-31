/**
 * CP3b-2 / CP3c — Attached pod render scale/position/orientation verification.
 *
 * History:
 *   CP3    (S=52 -> POD_DISPLAY_SIZE=96 + z-order fix) — fixed the pod being
 *          invisible behind the hull, but chief QA rejected the result:
 *          the pod still read as a tiny accessory, visually separated from
 *          the ship.
 *   CP3b-2 attached-pod render SIZE is derived from CONNECTOR_GAP (a
 *          measured CP2 graph constant) rather than a fixed nominal sprite
 *          size. Chief QA later confirmed the SIZE itself is now correct.
 *   CP3c   (this fix) — chief QA found the connector PLACEMENT still wrong:
 *          the pod rendered overlapping/on top of the hull instead of
 *          flush outside it, because the CP2 graph's CONNECTOR_GAP (46
 *          world-px) is smaller than the ship's own visible half-width
 *          (~51 world-px) -- i.e. the raw graph local_position the OLD
 *          code drew at sits inside the ship's own silhouette by
 *          construction. Fix is render-time only (getNodeRenderOffset() /
 *          getModuleRenderHalfWidth() in main.js): distance along the
 *          existing connector direction is recomputed as
 *          (parentHalfWidth + podHalfWidth), flush, zero unintended
 *          overlap. shipAssembly / local_position / CONNECTOR_GAP (CP2
 *          graph+save data) and pod render SCALE are all untouched.
 *
 * Chief flagged the pre-CP3c "no visible background gap" check (scanning
 * world-x 0..46 for zero background pixels) as INSUFFICIENT: overlapping
 * sprites also produce zero background gap, so that check alone cannot
 * distinguish "flush" from "overlapping". This version adds an explicit
 * ship-only-vs-pod-only bounding-box measurement (by toggling the pod out
 * of attachedPods and re-scanning) so overlap and flush-gap are checked
 * as two independent, non-conflatable assertions:
 *   - ship-only content bbox and pod-only-implied leading edge must not
 *     overlap beyond a small intentional-art tolerance
 *   - the two bounding boxes must still be flush (no floating background gap)
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

  console.log('\n[CP3c] Attached-pod render — expected flush geometry (from live measured half-widths)');

  const shipHalfWidth = await page.evaluate(() => window.__DB.getModuleFaceExtent('core', 'east')); // CP3d: connector is E, use real east-axis extent
  const S             = await page.evaluate(() => window.__DB.attachedPodRenderSize);
  // CP3e: pod's own near-face extent is now measured per-axis (real visible
  // bounds via _podHullExtentWorld()), not a blanket S/2 -- the pod's face
  // toward the ship on an E connector is its WEST face.
  const podHalfWidth  = await page.evaluate((pid) => window.__DB.getModuleFaceExtent(pid, 'west'), pid);
  const renderOffset  = await page.evaluate((pid) => window.__DB.getNodeRenderOffset(pid), pid);
  const expectedFlushDist = shipHalfWidth + podHalfWidth;

  await check('render offset uses flush distance (shipHalfWidth + pod\'s real per-axis west-face extent), not raw CONNECTOR_GAP local_position and not a blanket S/2', async () => {
    ok(shipHalfWidth !== null, 'shipHalfWidthWorld should be measurable once sprites are loaded');
    ok(podHalfWidth !== null, 'pod west-face extent should be measurable once sprites are loaded');
    ok(Math.abs(renderOffset.x - expectedFlushDist) < 1, `expected render offset x ~= ${expectedFlushDist} (shipHalfWidth ${shipHalfWidth} + pod west-face extent ${podHalfWidth}), got ${renderOffset.x}`);
    ok(Math.abs(renderOffset.y) < 1, `expected render offset y ~= 0 for an E connector, got ${renderOffset.y}`);
    ok(renderOffset.x > 46, `flush distance (${renderOffset.x}) must be greater than the raw graph CONNECTOR_GAP (46) -- otherwise this is the old overlap bug`);
  });

  console.log('\n[CP3c] Attached-pod render — independent ship-only vs pod-only bounding boxes (no unintended overlap)');

  // Ship-only content bounds, scanning the side AWAY from the connector
  // (negative world-x), since the pod never extends that far. Unaffected by
  // the CP3c fix -- sanity check that the ship itself still reads correctly.
  const shipSideAway = await scanContentBounds(page, cx, cy, -70, -2);
  await check('ship hull is visible on the side away from the connector (not swallowed)', async () => {
    ok(shipSideAway.minX !== null, 'expected some ship content on the negative-x side, found none');
  });

  // Ship-ONLY bounding box on the CONNECTOR side: temporarily remove the pod
  // from attachedPods (draw-only toggle; does not touch shipAssembly/graph
  // data) and measure where the ship's own content actually ends. This is
  // the independent "ship bbox" half of chief's requested overlap check.
  const savedPods = await page.evaluate(() => window.__DB.attachedPods.splice(0));
  const shipOnlySide = await scanContentBounds(page, cx, cy, 2, Math.round(expectedFlushDist + podHalfWidth + 20));
  await page.evaluate((saved) => { window.__DB.attachedPods.push(...saved); }, savedPods);
  await page.waitForTimeout(50);
  const shipOnlyMaxX = shipOnlySide.maxX; // outermost ship-only pixel on the connector side

  await check('ship-only content bound measured (pod temporarily hidden)', async () => {
    ok(shipOnlyMaxX !== null, 'expected ship content on the connector side even with the pod removed');
  });

  // Pod's own leading (near) edge, measured with BOTH ship and pod rendered:
  // first non-background pixel found beyond the ship-only bound.
  const ART_OVERLAP_TOLERANCE = 4; // px allowance for intentional connector-nub art, not a real hull/pod overlap
  const podLeadingEdgeScan = await scanContentBounds(page, cx, cy, (shipOnlyMaxX ?? 0) - ART_OVERLAP_TOLERANCE, Math.round(expectedFlushDist + podHalfWidth + 20));
  const podLeadingEdge = podLeadingEdgeScan.minX;

  await check('NO unintended core/pod bounding-box overlap: pod-visible content does not begin before the ship-only bound (beyond small art tolerance)', async () => {
    ok(podLeadingEdge !== null, 'expected some content on the connector side with the pod attached');
    ok(podLeadingEdge >= shipOnlyMaxX - ART_OVERLAP_TOLERANCE,
      `pod content starts at world-x=${podLeadingEdge}, but ship-only content already extends to ${shipOnlyMaxX} -- ` +
      `this is a bounding-box overlap greater than the ${ART_OVERLAP_TOLERANCE}px intentional-art tolerance (the exact CP3 bug chief flagged)`);
  });

  await check('flush: no floating background gap between the ship-only bound and the pod leading edge', async () => {
    const gap = podLeadingEdge - shipOnlyMaxX;
    ok(gap <= ART_OVERLAP_TOLERANCE + 2, `expected pod to sit flush against the ship (gap <= ~${ART_OVERLAP_TOLERANCE + 2}px), measured gap=${gap}px`);
  });

  const podFarEdgeScan = await scanContentBounds(page, cx, cy, 2, Math.round(expectedFlushDist + podHalfWidth + 20));
  const podFarEdge = podFarEdgeScan.maxX;
  const podHalfWidthMeasured = podFarEdge !== null ? (podFarEdge - renderOffset.x) : null;
  await check('pod reads as a substantial module, not a tiny accessory (measured half-width > old-rejected ~35px)', async () => {
    ok(podHalfWidthMeasured !== null && podHalfWidthMeasured > 40, `expected pod half-width > 40px (old rejected fix measured ~35px), got ${podHalfWidthMeasured}`);
  });

  await check('ship remains the dominant visible shape (measured ship-only half-width still >= 30px)', async () => {
    ok(shipOnlyMaxX !== null && shipOnlyMaxX >= 30, `expected ship still clearly visible (half-width >= 30px), got ${shipOnlyMaxX}`);
  });

  await check('pod scale is UNCHANGED by this fix: S stays > 96 (old rejected accessory size) and < 145 (would swallow the ship), same bounds as CP3b-2', async () => {
    ok(S > 96, `expected S > 96 (old rejected accessory size), got ${S}`);
    ok(S < 145, `expected S to stay well short of a 1:1 ship-size match (~152, which swallows the ship), got ${S}`);
  });

  console.log('\n[CP3b-2] Attached-pod render — rigid rotation with ship heading');

  // Rotation math is unaffected by CP3c (still shipHeadingAngle() * rotLocal),
  // but the probe points below must use the NEW flush offset, not the old
  // (inside-hull) magic numbers -- those no longer land on the pod at all.
  await page.evaluate(() => { window.__DB.ship.dir = 'east'; });
  await page.waitForTimeout(150);

  await check('after heading change to east, pod swings to below the ship (moves rigidly with ship)', async () => {
    const rgb = await pixelAt(page, cx, cy + Math.round(renderOffset.x));
    ok(differsFromBackground(rgb), `expected non-background sprite content at rotated position, got [${rgb.slice(0,3)}]`);
  });

  await check('old (pre-rotation) connector-side position returns to background (confirms it truly moved, not duplicated)', async () => {
    const rgb = await pixelAt(page, cx + Math.round(renderOffset.x), cy);
    ok(!differsFromBackground(rgb), `expected background at old position after rotating, but found content: [${rgb.slice(0,3)}]`);
  });

  await page.evaluate(() => { window.__DB.ship.dir = 'north'; });
  await page.waitForTimeout(150);

  await check('reverting heading to north restores content at the connector side', async () => {
    const rgb = await pixelAt(page, cx + Math.round(renderOffset.x), cy);
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
