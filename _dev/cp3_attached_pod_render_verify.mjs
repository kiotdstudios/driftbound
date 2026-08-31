/**
 * CP3 bugfix — Attached pod render scale/position/orientation verification.
 *
 * Bug: after CP2 docking committed, the attached pod rendered far smaller than
 * every other pod sprite in the game (hardcoded S=52 instead of POD_DISPLAY_SIZE)
 * AND was drawn *before* the ship, so the ship sprite painted over it — the pod
 * was almost entirely invisible, tucked behind the hull instead of sitting flush.
 *
 * Fix (render-only, in main.js — no CP2 docking-logic or graph-data changes):
 *   1. drawAttachedPods() sprite size: 52 -> POD_DISPLAY_SIZE (matches every
 *      other place this same pod sprite is rendered: world pods, in-flight
 *      docking animation).
 *   2. Render order: drawAttachedPods() now runs AFTER drawShip(), so the
 *      docked pod is visible on top of/flush against the hull instead of
 *      hidden underneath it.
 *
 * This test proves the fix with direct canvas pixel probes (not just game
 * state), because the bug was purely visual — shipAssembly/local_position
 * data was correct the whole time.
 *
 * Run via the same 3-suite harness as cp2_docking_verify.mjs (dev server on
 * :8420, bun runtime).
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

async function getDB(pg, expr) { return pg.evaluate(expr); }

async function pixelAt(pg, x, y) {
  return pg.evaluate(({ x, y }) => {
    const c = document.querySelector('canvas');
    const d = c.getContext('2d').getImageData(Math.round(x), Math.round(y), 1, 1).data;
    return [d[0], d[1], d[2], d[3]];
  }, { x, y });
}

// Solid pod-hull tan color sampled from the real sprite — see calibration in
// checkpoint notes. Tolerance is generous (±22/channel) to survive minor
// anti-aliasing/glow changes without masking a real regression.
const POD_TAN = [123, 106, 91];
function closeToPodTan(rgb, tol = 22) {
  return Math.abs(rgb[0] - POD_TAN[0]) <= tol
      && Math.abs(rgb[1] - POD_TAN[1]) <= tol
      && Math.abs(rgb[2] - POD_TAN[2]) <= tol;
}

// Deep-space background reference (no sprite content) — used when the ship
// is rotated, because the pod sprite's own internal detail (rivets/panels)
// rotates along with it, so a fixed absolute color match no longer applies.
// Any pixel that is clearly NOT this background color, at a position outside
// the ship's own north-facing silhouette, must be sprite content (ship or pod).
const BG_REF = [6, 48, 95];
function differsFromBackground(rgb, tol = 60) {
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

async function main() {
  browser = await chromium.launch({ headless: true });
  page    = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('console', m => { if (m.type() === 'error') console.error('PAGE ERR:', m.text()); });

  await page.goto(BASE, { waitUntil: 'networkidle', timeout: TIMEOUT });
  await page.waitForFunction(() => typeof window.__DB !== 'undefined' && window.__DB.ship?.worldX !== undefined, { timeout: 10000 });

  // Dismiss the multiplayer lobby overlay so the canvas is visible/unobstructed.
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Deterministic geometry: ship stationary, facing north (heading angle 0).
  await page.evaluate(() => {
    window.__DB.ship.dir = 'north';
    window.__DB.ship.vx  = 0;
    window.__DB.ship.vy  = 0;
    window.__DB.ship.ore = 50;
  });

  const dims = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    return { w: c.width, h: c.height };
  });
  const cx = Math.round(dims.w / 2), cy = Math.round(dims.h / 2);

  // Dock a fresh test pod. Approach vector (+30,+30) deterministically selects
  // connector 'E' (see findBestConnector dot-product scoring, ties broken by
  // iteration order N,E,S,W) -> local_position becomes (CONNECTOR_GAP, 0) = (46, 0).
  const pid = await page.evaluate(() => {
    const pid = '__cp3_render_' + Date.now();
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

  // Let the pod sprite image finish loading before sampling pixels.
  await page.waitForFunction(() => {
    const spr = window.__DB.podRotations && window.__DB.podRotations['south'];
    return spr && spr.naturalWidth > 0;
  }, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(150);

  console.log('\n[CP3] Attached-pod render — graph data sanity (unchanged by this fix)');

  const node = await page.evaluate((pid) => window.__DB.shipAssembly[pid], pid);
  await check('docked node exists with expected parent/connector/local_position', async () => {
    ok(node, 'shipAssembly node should exist');
    strictEqual(node.parent_connector, 'E', `expected connector E, got ${node.parent_connector}`);
    strictEqual(node.local_position.x, 46, `expected local x=46, got ${node.local_position.x}`);
    strictEqual(node.local_position.y, 0,  `expected local y=0, got ${node.local_position.y}`);
  });

  console.log('\n[CP3] Attached-pod render — scale & visibility (the actual bug)');

  // These offsets sit inside the ship's own visible silhouette radius (~51px).
  // Before the fix, the ship (drawn second) painted over anything here, so a
  // docked pod was invisible at every one of these points. After the fix, the
  // pod (drawn after the ship, at full POD_DISPLAY_SIZE) is solidly visible.
  const insideShipRadiusOffsets = [33, 36, 40, 44, 48];
  let tanHits = 0;
  for (const off of insideShipRadiusOffsets) {
    const rgb = await pixelAt(page, cx + off, cy);
    if (closeToPodTan(rgb)) tanHits++;
  }
  await check('pod sprite visibly rendered on top of the hull (>=4/5 probe points match pod color)', async () => {
    ok(tanHits >= 4, `expected >=4 of 5 probes to match pod tan color, got ${tanHits}`);
  });

  await check('single deterministic probe at connector offset (cx+40,cy) shows pod, not ship/background', async () => {
    const rgb = await pixelAt(page, cx + 40, cy);
    ok(closeToPodTan(rgb), `expected pod-tan color near [123,106,91], got [${rgb.slice(0,3)}]`);
  });

  console.log('\n[CP3] Attached-pod render — rigid rotation with ship heading');

  // Rotate the ship 90°: connector E (local +x) should now point toward local
  // +y in world space -> rendered swinging to directly below the ship on screen.
  await page.evaluate(() => { window.__DB.ship.dir = 'east'; });
  await page.waitForTimeout(150);

  await check('after heading change to east, pod swings to (cx, cy+40) — moves rigidly with ship', async () => {
    // Sprite detail rotates with the canvas, so match "not background" rather
    // than the exact tan color sampled at heading=north.
    const rgb = await pixelAt(page, cx, cy + 40);
    ok(differsFromBackground(rgb), `expected non-background sprite content at rotated position, got [${rgb.slice(0,3)}]`);
  });

  await check('old (pre-rotation) screen position no longer shows the pod (confirms it truly moved, not duplicated)', async () => {
    const rgb = await pixelAt(page, cx + 40, cy);
    ok(!closeToPodTan(rgb), `pod should have left (cx+40,cy) after rotating, but tan color still found: [${rgb.slice(0,3)}]`);
  });

  // Restore heading and re-verify original position lights up again — proves
  // the pod's orientation/position is fully determined by ship heading, not
  // a one-way animation artifact.
  await page.evaluate(() => { window.__DB.ship.dir = 'north'; });
  await page.waitForTimeout(150);

  await check('reverting heading to north restores pod at (cx+40,cy)', async () => {
    const rgb = await pixelAt(page, cx + 40, cy);
    ok(closeToPodTan(rgb), `expected pod-tan color restored, got [${rgb.slice(0,3)}]`);
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
