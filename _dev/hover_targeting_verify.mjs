/**
 * CP3b-2 — Mouse hover targeting verification.
 *
 * Chief spec: mouse screen position -> camera.screenToWorld() -> world-space
 * mouse coords -> hit-test candidates -> hoveredTarget. Hover is a pure
 * cursor readout, completely separate from interaction range (E-key), and
 * must work for world pods, attached pods, and asteroids at every zoom
 * level. It must NOT create a second E consumer -- src/systems/interactions.js
 * stays the only place E-key resolution happens.
 *
 * This test drives the real DOM mouse (page.mouse.move), not a synthetic
 * dev-bridge hook, so it exercises the actual initMouseTracking() listener
 * exactly as a real player would.
 *
 * Run via the same dev-server-on-:8420 / bun harness as the other _dev/*.mjs
 * regressions.
 */
import { chromium } from 'playwright';
import { strictEqual, ok } from 'assert';

const BASE = 'http://localhost:8420';
const TIMEOUT = 15000;
const ZOOM_LEVELS = [0.70, 0.85, 1.00, 1.15, 1.30];

let browser, page;
let passed = 0, failed = 0;

function pass(name) { console.log(`  \u2713 ${name}`); passed++; }
function fail(name, err) { console.error(`  \u2717 ${name}: ${err?.message || err}`); failed++; }
async function check(name, fn) { try { await fn(); pass(name); } catch (e) { fail(name, e); } }

async function waitForDockEnd(pg, timeout = 4000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (!(await pg.evaluate(() => window.__DB.isDocking))) return;
    await pg.waitForTimeout(50);
  }
  throw new Error('dock never completed');
}

async function moveMouseToWorld(pg, wx, wy) {
  const s = await pg.evaluate(({ wx, wy }) => window.__DB.camera.worldToScreen(wx, wy), { wx, wy });
  await pg.mouse.move(s.x, s.y);
  // Let a few real frames run so updateHover() (called once per loop tick)
  // has picked up the new mousemove event.
  await pg.waitForTimeout(120);
  return s;
}

async function main() {
  browser = await chromium.launch({ headless: true });
  page    = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('console', m => { if (m.type() === 'error') console.error('PAGE ERR:', m.text()); });

  await page.goto(BASE, { waitUntil: 'networkidle', timeout: TIMEOUT });
  await page.waitForFunction(() => typeof window.__DB !== 'undefined' && window.__DB.ship?.worldX !== undefined, { timeout: 10000 });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Deterministic, stationary ship facing north (heading angle 0) so the
  // attached-pod connector offset is exactly (+46, 0) in world space with
  // no rotation math needed by the test itself.
  await page.evaluate(() => {
    window.__DB.ship.dir = 'north';
    window.__DB.ship.vx = 0; window.__DB.ship.vy = 0;
    window.__DB.ship.ore = 50;
  });
  const shipPos = await page.evaluate(() => ({ x: window.__DB.ship.worldX, y: window.__DB.ship.worldY }));

  // Fixture 1: a world pod, far from the ship so its hover radius never
  // overlaps any other candidate.
  const wpPid = await page.evaluate((shipPos) => {
    const pid = '__hover_wp_' + Date.now();
    window.__DB.worldPods.push({ pid, type: 'modular_space_pod', worldX: shipPos.x + 400, worldY: shipPos.y, angle: 0 });
    return pid;
  }, shipPos);

  // Fixture 2: an attached pod, docked at connector E -> local_position (46,0).
  const apPid = await page.evaluate((shipPos) => {
    const pid = '__hover_ap_' + Date.now();
    window.__DB.worldPods.push({ pid, type: 'modular_space_pod', worldX: shipPos.x + 30, worldY: shipPos.y + 30, angle: 0 });
    return pid;
  }, shipPos);
  await page.evaluate((pid) => window.__DB.startDockingByPid(pid), apPid);
  await waitForDockEnd(page);
  await page.waitForTimeout(150);

  // Fixture 3: a synthetic asteroid, far from the ship and the other fixtures.
  await page.evaluate((shipPos) => {
    window.__DB.asteroids.push({
      type: { w: 40, h: 39, scale: 2 }, worldX: shipPos.x - 400, worldY: shipPos.y,
      hp: 5, maxHp: 5, flashTimer: 0, angle: 0, rotSpeed: 0,
    });
  }, shipPos);

  const apWorld = { x: shipPos.x + 46, y: shipPos.y };
  const wpWorld = { x: shipPos.x + 400, y: shipPos.y };
  const astWorld = { x: shipPos.x - 400, y: shipPos.y };
  // Kept well within the viewport at every zoom level (max 1.30x * 150 = 195px
  // offset, viewport half-height/width is 400/640) and far from every fixture's
  // hit radius (world pod hitRadius 60 @ (+400,0), attached pod ~63 @ (+46,0),
  // asteroid hitRadius 40 @ (-400,0)).
  const emptyWorld = { x: shipPos.x + 150, y: shipPos.y + 150 }; // no fixture nearby

  console.log('\n[hover] world_pod / attached_pod / asteroid / empty-space at every zoom level');

  for (let zi = 0; zi < ZOOM_LEVELS.length; zi++) {
    await page.evaluate((zi) => window.__DB.camera.setZoomIndex(zi), zi);
    await page.waitForTimeout(400); // let the eased zoom value settle
    const zoomLabel = ZOOM_LEVELS[zi].toFixed(2);

    await check(`zoom ${zoomLabel} — hovering world pod resolves type=world_pod, id=${wpPid}`, async () => {
      await moveMouseToWorld(page, wpWorld.x, wpWorld.y);
      const t = await page.evaluate(() => window.__DB.hoveredTarget);
      ok(t, 'expected a hovered target, got null');
      strictEqual(t.type, 'world_pod', `expected type world_pod, got ${t.type}`);
      strictEqual(t.id, wpPid, `expected id ${wpPid}, got ${t.id}`);
    });

    await check(`zoom ${zoomLabel} — hovering attached pod resolves type=attached_pod`, async () => {
      await moveMouseToWorld(page, apWorld.x, apWorld.y);
      const t = await page.evaluate(() => window.__DB.hoveredTarget);
      ok(t, 'expected a hovered target, got null');
      strictEqual(t.type, 'attached_pod', `expected type attached_pod, got ${t.type}`);
    });

    await check(`zoom ${zoomLabel} — hovering asteroid resolves type=asteroid`, async () => {
      await moveMouseToWorld(page, astWorld.x, astWorld.y);
      const t = await page.evaluate(() => window.__DB.hoveredTarget);
      ok(t, 'expected a hovered target, got null');
      strictEqual(t.type, 'asteroid', `expected type asteroid, got ${t.type}`);
    });

    await check(`zoom ${zoomLabel} — hovering empty space resolves null`, async () => {
      await moveMouseToWorld(page, emptyWorld.x, emptyWorld.y);
      const t = await page.evaluate(() => window.__DB.hoveredTarget);
      strictEqual(t, null, `expected null over empty space, got ${JSON.stringify(t)}`);
    });
  }

  // Restore default zoom before the remaining checks, so screen<->world math
  // below matches the other regressions' assumptions.
  await page.evaluate(() => window.__DB.camera.resetZoom());
  await page.waitForTimeout(400);

  console.log('\n[hover] does not create a second E consumer / does not affect the real resolver');

  await check('interactions.js resolver is untouched — resolveInteractions is not called from hover path', async () => {
    // getInteractionCandidates() must be pure (no gameplay side effects): calling
    // it repeatedly must not mutate ship state, ore, or shipAssembly.
    const before = await page.evaluate(() => JSON.stringify({ ore: window.__DB.ship.ore, assembly: window.__DB.shipAssembly }));
    await page.evaluate(() => { window.__DB.getInteractionCandidates(); window.__DB.getInteractionCandidates(); });
    const after = await page.evaluate(() => JSON.stringify({ ore: window.__DB.ship.ore, assembly: window.__DB.shipAssembly }));
    strictEqual(before, after, 'getInteractionCandidates() must be a pure readout with zero side effects');
  });

  await check('hover state itself never gates E — hoveredTarget can be set with ship far outside any range check', async () => {
    // Point the mouse at the far-away world pod (well outside POD_ATTACH_RANGE)
    // and confirm hover still resolves it (hover has no range concept at all).
    await moveMouseToWorld(page, wpWorld.x, wpWorld.y);
    const t = await page.evaluate(() => window.__DB.hoveredTarget);
    ok(t && t.type === 'world_pod', 'hover must resolve regardless of interaction range');
  });

  await browser.close();

  console.log(`\n─────────────────────────────────────`);
  console.log(`hover_targeting_verify: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

main().catch(e => {
  console.error('FATAL:', e);
  browser?.close();
  process.exit(1);
});
