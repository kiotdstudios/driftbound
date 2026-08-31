// ═══════════════════════════════════════════════════════════════════════════
// DRIFTBOUND — REGIONAL MAP OVERLAY
// Extracted verbatim (behavior-preserving) from src/main.js's drawRegionalMap()
// + the mapMode state variable, per the World/UI workstream ownership split
// (see OWNERSHIP.md). Press M to open/close (the M-key gate that checks
// interior/fade state stays in main.js — this module never reads interior
// state). Shows local sector: player, pods, asteroids, ore. MVP — no fog of
// war, full range shown. Suspends movement while open — but the movement
// mutation itself stays in main.js's update(); this module only exposes
// isOpen()/toggle() so gameplay code can react to it explicitly.
//
// This module owns rendering + its own open/closed state ONLY. It must not
// and does not mutate ship assembly, docking state, mining state, movement,
// or save schema — render() only reads the world-state object it's given.
// ═══════════════════════════════════════════════════════════════════════════

// Local copies of the direction constants (presentation-only; duplicated
// here rather than imported from main.js to avoid a circular module
// dependency — main.js imports this module, not the other way around).
const DIRS = [
  'north', 'north-east', 'east', 'south-east',
  'south', 'south-west', 'west', 'north-west'
];
const DIR_ANGLES_DEG = [-90, -45, 0, 45, 90, 135, 180, -135];

// Local rounded-rect helper (same duplication rationale as above).
function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r, y);
  ctx.lineTo(x+w-r, y);
  ctx.quadraticCurveTo(x+w, y, x+w, y+r);
  ctx.lineTo(x+w, y+h-r);
  ctx.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
  ctx.lineTo(x+r, y+h);
  ctx.quadraticCurveTo(x, y+h, x, y+h-r);
  ctx.lineTo(x, y+r);
  ctx.quadraticCurveTo(x, y, x+r, y);
  ctx.closePath();
}

export function createRegionalMap(ctx, canvas) {
  let mapMode = false;   // true while regional map overlay is open (M key)

  function isOpen() { return mapMode; }
  function toggle() { mapMode = !mapMode; return mapMode; }
  function open()  { mapMode = true;  return mapMode; }
  function close() { mapMode = false; return mapMode; }

  // render(state) — state = {
  //   ship:       live ship object (reads worldX/worldY/dir/shipType only),
  //   asteroids:  array (read-only; each { worldX, worldY, type:{w} }),
  //   orePickups: array (read-only; each { worldX, worldY }),
  //   worldPods:  array (read-only; each { worldX, worldY, type }),
  //   podTypes:   { [typeId]: { label, color } },  // POD_TYPES lookup table
  // }
  // No mutation of any field on `state` — presentation only.
  function render(state) {
    const { ship, asteroids = [], orePickups = [], worldPods = [], podTypes = {} } = state;
    const W = canvas.width, H = canvas.height;
    const t = Date.now();

    // ── Full-screen dim ──
    ctx.fillStyle = 'rgba(0,4,12,0.92)';
    ctx.fillRect(0, 0, W, H);

    // ── Map panel ──
    const MPW = Math.min(900, W - 80);   // map panel width
    const MPH = Math.min(680, H - 80);   // map panel height
    const MPX = (W - MPW) / 2;
    const MPY = (H - MPH) / 2;

    // Panel background + border
    ctx.fillStyle = 'rgba(2,8,18,0.96)';
    roundRect(ctx, MPX, MPY, MPW, MPH, 6);
    ctx.fill();
    ctx.strokeStyle = '#4FC3C3';
    ctx.lineWidth = 1.5;
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 10;
    roundRect(ctx, MPX, MPY, MPW, MPH, 6);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Title
    ctx.save();
    ctx.font = 'bold 14px "Courier New", monospace';
    ctx.fillStyle = '#4FC3C3';
    ctx.textAlign = 'center';
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 8;
    ctx.fillText('◈  SECTOR MAP', W/2, MPY + 24);
    ctx.shadowBlur = 0;

    // Ship name + coords subtitle
    ctx.font = '11px "Courier New", monospace';
    ctx.fillStyle = '#3a5060';
    ctx.fillText(
      (ship.shipType ? ship.shipType.name : 'SHIP') +
      '  ·  ' + Math.floor(ship.worldX) + ' / ' + Math.floor(ship.worldY),
      W/2, MPY + 42
    );
    ctx.restore();

    // ── Map drawing area (inside panel, with margin) ──
    const MX = MPX + 40,  MY = MPY + 60;   // draw area origin
    const MW = MPW - 80,  MH = MPH - 100;  // draw area size
    const MCX = MX + MW/2, MCY = MY + MH/2; // center of map

    // Draw area clip + background
    ctx.save();
    ctx.beginPath();
    ctx.rect(MX, MY, MW, MH);
    ctx.clip();

    ctx.fillStyle = 'rgba(0,4,14,0.98)';
    ctx.fillRect(MX, MY, MW, MH);

    // Grid lines
    const RANGE = 3500;   // world units visible from center to edge
    const SCALE = Math.min(MW, MH) / 2 / RANGE;

    const gridStep = 500;   // world units per grid line
    ctx.strokeStyle = '#4FC3C310'; ctx.lineWidth = 0.5;
    for (let wx = -RANGE; wx <= RANGE; wx += gridStep) {
      const sx = MCX + wx * SCALE;
      ctx.beginPath(); ctx.moveTo(sx, MY); ctx.lineTo(sx, MY+MH); ctx.stroke();
    }
    for (let wy = -RANGE; wy <= RANGE; wy += gridStep) {
      const sy = MCY + wy * SCALE;
      ctx.beginPath(); ctx.moveTo(MX, sy); ctx.lineTo(MX+MW, sy); ctx.stroke();
    }

    // Cross-hairs at player center
    ctx.strokeStyle = '#4FC3C322'; ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.moveTo(MCX, MY); ctx.lineTo(MCX, MY+MH); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(MX, MCY); ctx.lineTo(MX+MW, MCY); ctx.stroke();

    // ── Asteroids — orange dots ──
    for (const ast of asteroids) {
      const dx = (ast.worldX - ship.worldX) * SCALE;
      const dy = (ast.worldY - ship.worldY) * SCALE;
      if (Math.abs(dx) > MW/2 + 10 || Math.abs(dy) > MH/2 + 10) continue;
      const r = Math.max(2, (ast.type ? ast.type.w / 14 : 3));
      ctx.fillStyle = '#f97316';
      ctx.shadowColor = '#f97316'; ctx.shadowBlur = 4;
      ctx.beginPath(); ctx.arc(MCX+dx, MCY+dy, r, 0, Math.PI*2); ctx.fill();
      ctx.shadowBlur = 0;
      // Type label on hover is MVP-deferred; show size hint with opacity
    }

    // ── Ore pickups — green blips ──
    for (const o of orePickups) {
      const dx = (o.worldX - ship.worldX) * SCALE;
      const dy = (o.worldY - ship.worldY) * SCALE;
      if (Math.abs(dx) > MW/2 + 4 || Math.abs(dy) > MH/2 + 4) continue;
      ctx.fillStyle = '#22c55e';
      ctx.shadowColor = '#22c55e'; ctx.shadowBlur = 5;
      ctx.beginPath(); ctx.arc(MCX+dx, MCY+dy, 3, 0, Math.PI*2); ctx.fill();
      ctx.shadowBlur = 0;
    }

    // ── World pods — cyan diamonds ──
    const podBlink = 0.6 + 0.4 * Math.sin(t * 0.003);
    for (const pod of worldPods) {
      const dx = (pod.worldX - ship.worldX) * SCALE;
      const dy = (pod.worldY - ship.worldY) * SCALE;
      if (Math.abs(dx) > MW/2 + 10 || Math.abs(dy) > MH/2 + 10) continue;
      const pCol = (podTypes[pod.type]||{}).color || '#38bdf8';
      const px = MCX+dx, py = MCY+dy;
      ctx.save();
      ctx.globalAlpha = podBlink;
      ctx.translate(px, py); ctx.rotate(Math.PI/4);
      ctx.fillStyle = pCol;
      ctx.shadowColor = pCol; ctx.shadowBlur = 8;
      ctx.fillRect(-5, -5, 10, 10);
      ctx.shadowBlur = 0;
      ctx.restore();
      // Label
      ctx.font = '10px "Courier New", monospace';
      ctx.fillStyle = pCol + 'cc';
      ctx.textAlign = 'center';
      ctx.fillText((podTypes[pod.type]||{label:'POD'}).label, MCX+dx, MCY+dy - 11);
    }

    // ── Home marker (first worldPod or origin) ──
    const homeX = worldPods.length > 0 ? worldPods[0].worldX : 0;
    const homeY = worldPods.length > 0 ? worldPods[0].worldY : 0;
    const hdx = (homeX - ship.worldX) * SCALE;
    const hdy = (homeY - ship.worldY) * SCALE;
    if (Math.abs(hdx) <= MW/2 && Math.abs(hdy) <= MH/2) {
      ctx.fillStyle = '#FFD700';
      ctx.shadowColor = '#FFD700'; ctx.shadowBlur = 12;
      ctx.font = '14px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('⌂', MCX+hdx, MCY+hdy + 5);
      ctx.shadowBlur = 0;
    }

    // ── Player dot (center) ──
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.arc(MCX, MCY, 5, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;

    // Direction arrow from player
    const dIdx = DIRS.indexOf(ship.dir);
    if (dIdx >= 0) {
      const da = DIR_ANGLES_DEG[dIdx] * Math.PI / 180;
      ctx.strokeStyle = '#4FC3C3'; ctx.lineWidth = 2;
      ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 5;
      ctx.beginPath();
      ctx.moveTo(MCX + Math.cos(da)*7, MCY + Math.sin(da)*7);
      ctx.lineTo(MCX + Math.cos(da)*18, MCY + Math.sin(da)*18);
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    ctx.restore();  // end clip

    // ── Map border ──
    ctx.strokeStyle = '#4FC3C330'; ctx.lineWidth = 1;
    ctx.strokeRect(MX, MY, MW, MH);

    // ── Scale bar ──
    const scalePx = 500 * SCALE;  // 500 world units
    const sbX = MPX + MPW - 120, sbY = MPY + MPH - 24;
    ctx.strokeStyle = '#4FC3C3'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(sbX, sbY); ctx.lineTo(sbX + scalePx, sbY); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(sbX, sbY-4); ctx.lineTo(sbX, sbY+4); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(sbX+scalePx, sbY-4); ctx.lineTo(sbX+scalePx, sbY+4); ctx.stroke();
    ctx.font = '9px "Courier New", monospace';
    ctx.fillStyle = '#4FC3C3';
    ctx.textAlign = 'center';
    ctx.fillText('500u', sbX + scalePx/2, sbY + 12);

    // ── Legend ──
    const lx = MPX + 16, ly = MPY + MPH - 72;
    ctx.font = '10px "Courier New", monospace';
    ctx.textAlign = 'left';
    const legend = [
      { col:'#ffffff', label:'YOU'      },
      { col:'#f97316', label:'ASTEROID' },
      { col:'#38bdf8', label:'POD'      },
      { col:'#22c55e', label:'ORE'      },
      { col:'#FFD700', label:'HOME'     },
    ];
    legend.forEach((item, i) => {
      ctx.fillStyle = item.col;
      ctx.beginPath(); ctx.arc(lx+6, ly + i*16 + 4, 4, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = item.col + 'aa';
      ctx.fillText(item.label, lx+16, ly + i*16 + 8);
    });

    // ── Close hint ──
    ctx.save();
    ctx.font = '11px "Courier New", monospace';
    ctx.fillStyle = '#2a4050';
    ctx.textAlign = 'center';
    ctx.fillText('[M]  CLOSE MAP', W/2, MPY + MPH - 10);
    ctx.restore();
  }

  return { isOpen, toggle, open, close, render };
}
