// ═══════════════════════════════════════════════════════════════════════════
// DRIFTBOUND — MINIMAP (bottom-right sector radar)
// Extracted verbatim (behavior-preserving) from src/main.js's drawMinimap(),
// per the World/UI workstream ownership split (see OWNERSHIP.md). Owns
// minimap rendering, minimap presentation constants (radius, scale, colors),
// and minimap-specific visual calculations (dot placement, direction tick,
// legend). Consumes world data only through the explicit render(state)
// argument — no closures back into main.js.
//
// This module owns rendering + its own presentation constants ONLY. It must
// not and does not mutate movement, map-open behavior, docking, ship
// assembly, mining, or save data — render() only reads the world-state
// object it's given.
// ═══════════════════════════════════════════════════════════════════════════

// Local copies of the direction constants (presentation-only; duplicated
// here rather than imported from main.js to avoid a circular module
// dependency — main.js imports this module, not the other way around).
// Same duplication rationale as src/render/map.js.
const DIRS = [
  'north', 'north-east', 'east', 'south-east',
  'south', 'south-west', 'west', 'north-west'
];
const DIR_ANGLES_DEG = [-90, -45, 0, 45, 90, 135, 180, -135];

export function createMinimap(ctx, canvas) {
  // render(state) — state = {
  //   ship:       live ship object (reads worldX/worldY/dir only),
  //   asteroids:  array (read-only; each { worldX, worldY, type:{w} }),
  //   orePickups: array (read-only; each { worldX, worldY }),
  //   worldPods:  array (read-only; each { worldX, worldY, type }),
  //   podTypes:   { [typeId]: { color } },  // POD_TYPES lookup table
  // }
  // No mutation of any field on `state` — presentation only.
  function render(state) {
    const { ship, asteroids = [], orePickups = [], worldPods = [], podTypes = {} } = state;
    const W = canvas.width, H = canvas.height;
    const MR = 72;                    // minimap radius px
    const MX = W - MR - 16;          // center x
    const MY = H - MR - 16;          // center y
    const SCALE = MR / 1400;         // world-px to minimap-px  (1400 world = 1 minimap radius)
    const t = Date.now();

    ctx.save();

    // Clip to circle
    ctx.beginPath(); ctx.arc(MX, MY, MR, 0, Math.PI*2); ctx.clip();

    // Background
    ctx.fillStyle = 'rgba(2,8,18,0.88)';
    ctx.fillRect(MX-MR, MY-MR, MR*2, MR*2);

    // Subtle grid rings
    ctx.strokeStyle = '#4FC3C310'; ctx.lineWidth = 0.5;
    for (let r = MR/3; r <= MR; r += MR/3) {
      ctx.beginPath(); ctx.arc(MX, MY, r, 0, Math.PI*2); ctx.stroke();
    }
    // Cross hairs
    ctx.beginPath(); ctx.moveTo(MX-MR, MY); ctx.lineTo(MX+MR, MY); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(MX, MY-MR); ctx.lineTo(MX, MY+MR); ctx.stroke();

    // ── Asteroids — orange dots ──
    for (const ast of asteroids) {
      const dx = (ast.worldX - ship.worldX) * SCALE;
      const dy = (ast.worldY - ship.worldY) * SCALE;
      if (dx*dx + dy*dy > MR*MR) continue;
      const sz = Math.max(1.5, (ast.type ? ast.type.w / 20 : 2));
      ctx.fillStyle = '#f97316';
      ctx.shadowColor = '#f97316'; ctx.shadowBlur = 3;
      ctx.beginPath(); ctx.arc(MX+dx, MY+dy, sz, 0, Math.PI*2); ctx.fill();
    }
    ctx.shadowBlur = 0;

    // ── Ore pickups — green dots ──
    if (orePickups) {
      for (const o of orePickups) {
        const dx = (o.worldX - ship.worldX) * SCALE;
        const dy = (o.worldY - ship.worldY) * SCALE;
        if (dx*dx + dy*dy > MR*MR) continue;
        ctx.fillStyle = '#22c55e';
        ctx.shadowColor = '#22c55e'; ctx.shadowBlur = 4;
        ctx.beginPath(); ctx.arc(MX+dx, MY+dy, 2, 0, Math.PI*2); ctx.fill();
      }
      ctx.shadowBlur = 0;
    }

    // ── World pods — cyan blips (pulsing) ──
    const blink = 0.6 + 0.4 * Math.sin(t * 0.004);
    for (const pod of worldPods) {
      const dx = (pod.worldX - ship.worldX) * SCALE;
      const dy = (pod.worldY - ship.worldY) * SCALE;
      if (dx*dx + dy*dy > MR*MR) continue;
      const pCol = (podTypes[pod.type]||{}).color || '#38bdf8';
      ctx.fillStyle = pCol;
      ctx.shadowColor = pCol; ctx.shadowBlur = 5 * blink;
      ctx.globalAlpha = blink;
      ctx.beginPath(); ctx.arc(MX+dx, MY+dy, 3, 0, Math.PI*2); ctx.fill();
      ctx.globalAlpha = 1;
    }
    ctx.shadowBlur = 0;

    // ── Player dot — white center ──
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 8;
    ctx.beginPath(); ctx.arc(MX, MY, 3.5, 0, Math.PI*2); ctx.fill();

    // Player direction tick
    const dIdx = DIRS.indexOf(ship.dir);
    if (dIdx >= 0) {
      const da = DIR_ANGLES_DEG[dIdx] * Math.PI / 180;
      ctx.strokeStyle = '#4FC3C3'; ctx.lineWidth = 1.5;
      ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 4;
      ctx.beginPath();
      ctx.moveTo(MX + Math.cos(da)*5, MY + Math.sin(da)*5);
      ctx.lineTo(MX + Math.cos(da)*10, MY + Math.sin(da)*10);
      ctx.stroke();
    }
    ctx.shadowBlur = 0;

    ctx.restore();  // end clip

    // ── Outer border ring ──
    ctx.strokeStyle = '#4FC3C3';
    ctx.lineWidth = 1.2;
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 6;
    ctx.beginPath(); ctx.arc(MX, MY, MR, 0, Math.PI*2); ctx.stroke();
    ctx.shadowBlur = 0;

    // Label
    ctx.save();
    ctx.font = '9px "Courier New", monospace';
    ctx.fillStyle = '#4FC3C388';
    ctx.textAlign = 'center';
    ctx.fillText('SECTOR MAP', MX, MY + MR + 12);
    ctx.restore();

    // Legend — tiny, bottom-right corner under ring
    const lx = MX - MR + 4, ly = MY + MR - 22;
    ctx.save(); ctx.font = '8px "Courier New", monospace';
    ctx.fillStyle = '#f97316'; ctx.beginPath(); ctx.arc(lx+4, ly, 2.5, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#f9731688'; ctx.fillText('AST', lx+10, ly+3);
    ctx.fillStyle = '#38bdf8'; ctx.beginPath(); ctx.arc(lx+4, ly+10, 2.5, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#38bdf888'; ctx.fillText('POD', lx+10, ly+13);
    ctx.fillStyle = '#22c55e'; ctx.beginPath(); ctx.arc(lx+4, ly+20, 2.5, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#22c55e88'; ctx.fillText('ORE', lx+10, ly+23);
    ctx.restore();
  }

  return { render };
}
