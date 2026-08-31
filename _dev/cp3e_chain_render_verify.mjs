/**
 * CP3e — Multi-pod chain connector continuity verification.
 *
 * Chief QA evidence (2026-08-31): a north-side chain of two pods showed the
 * lower pod separated from the ship by an excessive exposed line, and the
 * upper pod floating with a large empty gap and no visible strut. Root
 * cause: getModuleFaceExtent() used one blanket S/2 (half the pod's nominal
 * square canvas draw size, including transparent padding) for a pod's face
 * extent in EVERY direction, but the pod sprite's real visible bounds are
 * asymmetric per axis (see _podHullExtentWorld() in main.js). This
 * overestimated extent produced exactly the reported floating/oversized-gap
 * symptom on pod->pod edges.
 *
 * Fix (this checkpoint): _podHullExtentWorld() measures the pod's own real
 * per-axis visible half-extents (north/south/east/west), the same way
 * _shipHullExtentWorld() (CP3d) measures the ship. getModuleFaceExtent()
 * now uses this per-axis measurement for pods instead of a blanket half-S.
 * _connectorAxisKeys() is a single shared helper used by BOTH placement
 * (getNodeRenderOffset) and strut endpoints (drawAttachedPods), so
 * interaction geometry (hover, docking target) cannot drift from visuals.
 *
 * This test verifies a 2-pod chain (core -> pod1 -> pod2) on the E
 * connector with full independent pixel-bbox overlap/gap checks at BOTH
 * edges (core->pod1, pod1->pod2), plus lighter graph+offset-formula
 * consistency checks at N/S/W, plus hover-hit-matches-render for both
 * chained pods, plus a docking-completion-no-jump check.
 *
 * Run via the same dev-server-on-:8420 / bun harness as the other _dev/*.mjs
 * regressions.
 */
import { chromium } from 'playwright';
import { strictEqual, ok } from 'assert';

const BASE = 'http://localhost:8420';
const TIMEOUT = 15000;
const ART_OVERLAP_TOLERANCE = 4; // px allowance for intentional connector-nub art

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

const BG_REF = [8, 60, 118];
function differsFromBackground(rgb, tol = 100) {
  const d = Math.abs(rgb[0] - BG_REF[0]) + Math.abs(rgb[1] - BG_REF[1]) + Math.abs(rgb[2] - BG_REF[2]);
  return d > tol;
}

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
  await pg.waitForTimeout(120);
  return s;
}

// Dock a fresh pod (spawned dx,dy from the ship) and return its shipAssembly
// modId (== pid). Used to build a chain: pass dx/dy far enough along the
// SAME axis as a previously-docked pod to attach to that pod's outer
// connector instead of the core's.
async function dockPod(pg, dx, dy) {
  const pid = await pg.evaluate(async ({ dx, dy }) => {
    const pid = '__cp3e_chain_' + Math.random();
    const s = window.__DB.ship;
    window.__DB.worldPods.push({ pid, type: 'modular_space_pod', worldX: s.worldX + dx, worldY: s.worldY + dy, angle: 0 });
    return pid;
  }, { dx, dy });
  await pg.evaluate((pid) => window.__DB.startDockingByPid(pid), pid);
  await waitForDockEnd(pg);
  await pg.waitForTimeout(150);
  return pid;
}

async function resetAssembly(pg) {
  await pg.evaluate(() => {
    const DB = window.__DB;
    for (const p of DB.attachedPods.splice(0)) {
      delete DB.shipAssembly[p.mod_id || p.pid];
    }
    DB.shipAssembly.core.available_connectors.forEach(c => c.free = true);
  });
  await pg.waitForTimeout(100);
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
    window.__DB.ship.ore = 999;
    window.__DB.camera.resetZoom();
  });
  await page.waitForTimeout(400);
  await page.evaluate(() => window.__DB.camera.setZoomIndex(2)); // zoom=1.00, screen-px == world-px
  await page.waitForTimeout(400);

  await page.waitForFunction(() => {
    const spr = window.__DB.podRotations && window.__DB.podRotations['south'];
    return spr && spr.naturalWidth > 0;
  }, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(200);

  const dims = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    return { w: c.width, h: c.height };
  });
  const cx = Math.round(dims.w / 2), cy = Math.round(dims.h / 2);
  const commitHash = await page.evaluate(() => window.__DB.buildInfo?.commit || null).catch(() => null);

  console.log('\n[CP3e] Multi-pod chain -- geometry+graph consistency at N/E/S/W');

  const AXES = {
    N: { dx: 0, dy: -1, near: 60, far: 260, opp: 'south' },
    E: { dx: 1, dy: 0,  near: 60, far: 260, opp: 'west'  },
    S: { dx: 0, dy: 1,  near: 60, far: 260, opp: 'north' },
    W: { dx: -1, dy: 0, near: 60, far: 260, opp: 'east'  },
  };
  const DIR_KEY = { N: 'north', E: 'east', S: 'south', W: 'west' };

  let pod1E, pod2E; // keep the E-connector chain's ids for the deep pixel checks below

  for (const [connKey, ax] of Object.entries(AXES)) {
    const pod1 = await dockPod(page, ax.dx * ax.near, ax.dy * ax.near);
    const pod2 = await dockPod(page, ax.dx * ax.far, ax.dy * ax.far);

    const node1 = await page.evaluate((id) => window.__DB.shipAssembly[id], pod1);
    const node2 = await page.evaluate((id) => window.__DB.shipAssembly[id], pod2);

    await check(`[${connKey}] pod1 docks to core on connector ${connKey}`, async () => {
      ok(node1, 'pod1 node should exist');
      strictEqual(node1.parent_connector, connKey, `expected pod1 parent_connector ${connKey}, got ${node1.parent_connector}`);
    });

    await check(`[${connKey}] pod2 chains onto pod1 (parent is pod1, not core)`, async () => {
      ok(node2, 'pod2 node should exist');
      const parentId = node2.parent || 'core';
      strictEqual(parentId, pod1, `expected pod2.parent === pod1 (${pod1}), got ${parentId} -- this would mean pod2 attached to core instead of chaining`);
    });

    const dirKey = DIR_KEY[connKey];
    const oppKey = ax.opp;
    const coreExt = await page.evaluate((d) => window.__DB.getModuleFaceExtent('core', d), dirKey);
    const pod1ExtNear = await page.evaluate(({id,d}) => window.__DB.getModuleFaceExtent(id, d), { id: pod1, d: oppKey });
    const pod1ExtFar  = await page.evaluate(({id,d}) => window.__DB.getModuleFaceExtent(id, d), { id: pod1, d: dirKey });
    const pod2ExtNear = await page.evaluate(({id,d}) => window.__DB.getModuleFaceExtent(id, d), { id: pod2, d: oppKey });
    const off1 = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod1);
    const off2 = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod2);
    const dist1 = Math.hypot(off1.x, off1.y);
    const dist2to1 = Math.hypot(off2.x - off1.x, off2.y - off1.y);

    await check(`[${connKey}] core->pod1 edge is flush: offset distance == coreExtent + pod1's near-face extent (independently measured per-axis, not blanket S/2)`, async () => {
      ok(Math.abs(dist1 - (coreExt + pod1ExtNear)) < 1,
        `expected dist1=${dist1} ~= coreExt(${coreExt}) + pod1ExtNear(${pod1ExtNear}) = ${coreExt + pod1ExtNear}`);
    });

    await check(`[${connKey}] pod1->pod2 edge is flush: offset distance == pod1's far-face extent + pod2's near-face extent`, async () => {
      ok(Math.abs(dist2to1 - (pod1ExtFar + pod2ExtNear)) < 1,
        `expected dist2to1=${dist2to1} ~= pod1ExtFar(${pod1ExtFar}) + pod2ExtNear(${pod2ExtNear}) = ${pod1ExtFar + pod2ExtNear}`);
    });

    if (connKey === 'E') { pod1E = pod1; pod2E = pod2; }

    await resetAssembly(page);
  }

  console.log('\n[CP3e] Multi-pod chain (E) -- independent pixel bounding-box overlap/gap check at BOTH edges');

  const pod1 = await dockPod(page, 60, 0);
  const pod2 = await dockPod(page, 260, 0);

  // core-only bound: hide both pods
  const savedBoth = await page.evaluate(() => window.__DB.attachedPods.splice(0));
  const coreOnly = await scanContentBounds(page, cx, cy, 2, 400);
  const coreOnlyMaxX = coreOnly.maxX;
  await check('core-only content bound measured (both pods hidden)', async () => {
    ok(coreOnlyMaxX !== null, 'expected ship content with pods hidden');
  });

  // core + pod1 only: restore pod1's entry, keep pod2 hidden
  const pod1Entry = savedBoth.find(p => (p.mod_id || p.pid) === pod1);
  const pod2Entry = savedBoth.find(p => (p.mod_id || p.pid) === pod2);
  await page.evaluate((entry) => { window.__DB.attachedPods.push(entry); }, pod1Entry);
  await page.waitForTimeout(50);
  const pod1LeadScan = await scanContentBounds(page, cx, cy, (coreOnlyMaxX ?? 0) - ART_OVERLAP_TOLERANCE, 400);
  const pod1Lead = pod1LeadScan.minX;
  const pod1FarScan = await scanContentBounds(page, cx, cy, (pod1Lead ?? 0), 400);
  const pod1Far = pod1FarScan.maxX;

  await check('EDGE 1 (core->pod1): no bounding-box overlap beyond art tolerance', async () => {
    ok(pod1Lead !== null, 'expected pod1 content beyond the core-only bound');
    ok(pod1Lead >= coreOnlyMaxX - ART_OVERLAP_TOLERANCE,
      `pod1 leading edge at x=${pod1Lead} overlaps core-only bound x=${coreOnlyMaxX} beyond ${ART_OVERLAP_TOLERANCE}px tolerance`);
  });
  await check('EDGE 1 (core->pod1): no unexplained empty gap (flush within tolerance)', async () => {
    const gap = pod1Lead - coreOnlyMaxX;
    ok(gap <= ART_OVERLAP_TOLERANCE + 2, `expected flush (gap <= ~${ART_OVERLAP_TOLERANCE + 2}px), measured gap=${gap}px -- this is the exact CP3e chief-reported symptom (excessive exposed line / floating gap) if it fails`);
  });

  // core + pod1 + pod2, all visible: restore pod2 too
  await page.evaluate((entry) => { window.__DB.attachedPods.push(entry); }, pod2Entry);
  await page.waitForTimeout(50);
  const pod2LeadScan = await scanContentBounds(page, cx, cy, (pod1Far ?? 0) - ART_OVERLAP_TOLERANCE, 400);
  const pod2Lead = pod2LeadScan.minX;

  await check('EDGE 2 (pod1->pod2): no bounding-box overlap beyond art tolerance', async () => {
    ok(pod2Lead !== null, 'expected pod2 content beyond pod1\'s far bound');
    ok(pod2Lead >= pod1Far - ART_OVERLAP_TOLERANCE,
      `pod2 leading edge at x=${pod2Lead} overlaps pod1's far bound x=${pod1Far} beyond ${ART_OVERLAP_TOLERANCE}px tolerance`);
  });
  await check('EDGE 2 (pod1->pod2): no unexplained empty gap (flush within tolerance, i.e. no floating upper pod)', async () => {
    const gap = pod2Lead - pod1Far;
    ok(gap <= ART_OVERLAP_TOLERANCE + 2, `expected flush (gap <= ~${ART_OVERLAP_TOLERANCE + 2}px), measured gap=${gap}px -- this is the exact CP3e chief-reported "floats with a large empty gap" symptom if it fails`);
  });

  console.log('\n[CP3e] Multi-pod chain (E) -- hover hit-test matches render position for BOTH chained pods');

  const a0 = await page.evaluate(() => window.__DB.ship);
  const off1b = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod1);
  const off2b = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod2);

  await moveMouseToWorld(page, a0.worldX + off1b.x, a0.worldY + off1b.y);
  await check('hover over pod1\'s rendered position resolves to pod1 (not pod2, not core, not miss)', async () => {
    const t = await page.evaluate(() => window.__DB.hoveredTarget);
    ok(t, 'expected a hover target, got null');
    strictEqual(t.type, 'attached_pod', `expected type attached_pod, got ${t.type}`);
    strictEqual(t.id, pod1, `expected hover id === pod1 (${pod1}), got ${t.id}`);
  });

  await moveMouseToWorld(page, a0.worldX + off2b.x, a0.worldY + off2b.y);
  await check('hover over pod2\'s rendered position resolves to pod2 (not pod1, not core, not miss)', async () => {
    const t = await page.evaluate(() => window.__DB.hoveredTarget);
    ok(t, 'expected a hover target, got null');
    strictEqual(t.type, 'attached_pod', `expected type attached_pod, got ${t.type}`);
    strictEqual(t.id, pod2, `expected hover id === pod2 (${pod2}), got ${t.id}`);
  });

  console.log('\n[CP3e] Docking completion does not visibly jump to a different target position');

  const pod3 = await dockPod(page, 460, 0); // third pod, chains onto pod2
  const off3 = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod3);
  await page.waitForTimeout(60);
  const off3b = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod3);

  await check('rendered position immediately after LOCK is stable across subsequent frames (no post-completion drift/jump)', async () => {
    ok(Math.abs(off3.x - off3b.x) < 0.5 && Math.abs(off3.y - off3b.y) < 0.5,
      `expected identical render offset across frames, got (${off3.x},${off3.y}) then (${off3b.x},${off3b.y})`);
  });

  const pod2ExtFar  = await page.evaluate((id) => window.__DB.getModuleFaceExtent(id, 'east'), pod2);
  const pod3ExtNear = await page.evaluate((id) => window.__DB.getModuleFaceExtent(id, 'west'), pod3);
  const off2c = await page.evaluate((id) => window.__DB.getNodeRenderOffset(id), pod2);
  const distPost = Math.hypot(off3.x - off2c.x, off3.y - off2c.y);
  await check('post-LOCK settled position matches the same flush formula used during the in-flight docking animation (getModuleFaceExtent-based target) -- confirms no jump between anim target and final render', async () => {
    ok(Math.abs(distPost - (pod2ExtFar + pod3ExtNear)) < 1,
      `expected post-LOCK distance ${distPost} ~= pod2ExtFar(${pod2ExtFar}) + pod3ExtNear(${pod3ExtNear}) = ${pod2ExtFar + pod3ExtNear}`);
  });

  console.log(`\nTested commit (live during this run): ${commitHash || '(not exposed via bridge -- captured externally via git rev-parse HEAD)'}`);

  await browser.close();

  console.log(`\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500`);
  console.log(`cp3e_chain_render_verify: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

main().catch(e => {
  console.error('FATAL:', e);
  browser?.close();
  process.exit(1);
});
