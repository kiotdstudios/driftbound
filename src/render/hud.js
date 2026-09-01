// ─── HUD MODULE (World/UI ownership — see OWNERSHIP.md) ─────────────────────
// Extracted verbatim (behavior-preserving move, W2 directive) from drawHUD()
// in src/main.js. Owns presentation/rendering for: Navigation, Ship, Hull,
// Fuel, Cargo/resources, pod information, context/action prompts, warnings.
//
// Consumes gameplay information ONLY through the explicit render(state)
// argument — no closures back into main.js. Screen-space only; drawn after
// applyWorldTransform()/restoreWorldTransform() has already returned to
// identity, so it is inherently independent of camera zoom (unchanged from
// the original call site in loop(): drawHUD -> minimap.render -> drawDevControls,
// preserved by the caller).
//
// Local duplicate constants (DIRS/DIR_ANGLES_DEG) mirror the same
// circular-import-avoidance rationale already established in map.js /
// minimap.js. Gameplay-tunable balance numbers (fuel capacity, hull max,
// base cargo limit, boost cap, fuel-per-craft) are NOT duplicated here —
// they are Core-Gameplay-owned (OWNERSHIP.md / SHIP_BALANCE-adjacent) and
// are passed in via state each frame to avoid any drift risk if Aki tunes
// them later.

const DIRS = [
  'north', 'north-east', 'east', 'south-east',
  'south', 'south-west', 'west', 'north-west'
];
const DIR_ANGLES_DEG = [-90, -45, 0, 45, 90, 135, 180, -135];

// Helper: rounded rect path (local duplicate of main.js's roundRect — same
// reasoning as above; main.js keeps its own copy for drawDiagnostics, which
// stays in main.js under this directive).
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

export function createHUD(ctx, canvas) {

  function render(state) {
    const {
      ship, speed, attachedPods, mineTarget, mineDist, boosting,
      hudBounds, debugBoxes,
      fuelCapacity, shipMaxHp, cargoLimitBase, boostMax, fuelPerCraft,
    } = state;

    // In-place clear (not reassignment) so the caller's array reference
    // (main.js's _hudBounds, exposed via window.__DB.hudBounds for the test
    // harness) stays valid across frames — identical observable behavior to
    // the original `_hudBounds = []` reset, without breaking the reference
    // the test bridge is holding.
    if (hudBounds) hudBounds.length = 0;

    const W = canvas.width, H = canvas.height;
    const t = Date.now();

    // ── Palette ──
    const TEAL   = '#4FC3C3';
    const ORANGE = '#e07b30';
    const WHT    = '#d0e4f0';
    const DIM    = '#3a5060';
    const ACC    = '#38bdf8';
    const ERR    = '#ef4444';

    // ── Layout constants — all drawing uses these, nothing else ──
    const PAD_X  = 10;   // left/right interior padding
    const PAD_Y  = 10;   // top/bottom interior padding
    const PW     = 240;  // panel width
    const PX     = 14;   // panel left edge from screen
    const PY_TOP = 14;   // panel top edge from screen
    const R_H    = 19;   // standard row height (a touch taller — breathing room)
    const B_H    =  4;   // bar fill height
    const B_OFF  =  5;   // bar top from row top (so bar is vertically centered)
    const TXT    = 13;   // text baseline offset from row top (consistent across all rows)
    const DIV_A  =  7;   // space above divider line (consistent divider padding)
    const DIV_B  =  7;   // space below divider line
    const SEC_B  =  5;   // space below section label

    // ── Derived values ──
    const fuelPct    = ship.fuel / fuelCapacity;
    const hpPct      = ship.hp / shipMaxHp;
    const cUsed      = ship.ore + ship.armalcolite;
    const cMax       = (ship.shipType ? ship.shipType.cargoLimit : cargoLimitBase) +
                       attachedPods.reduce((s, p) => s + (p.cargoBonus || 0), 0);
    const cFull      = cUsed >= cMax;
    const boostOn    = boosting && ship.fuel > 0;
    const fuelLow    = fuelPct < 0.2;
    const fuelEmpty  = ship.fuel <= 0;
    const resRows    = (ship.ore > 0 ? 1 : 0) + (ship.mineral > 0 ? 1 : 0) + (ship.armalcolite > 0 ? 1 : 0);
    const emptyHold  = resRows === 0;

    // ── Pre-calculate panel height ──
    // Every block below adds the same amount it will draw.
    // Formula is the single source of truth — drawing code MUST match it.
    const DIV = DIV_A + 1 + DIV_B;   // 11px per divider
    const SEC = R_H + SEC_B;         // 22px per section label row

    let PH = PAD_Y;
    // Header
    PH += R_H + 4;                             // ship name (slightly taller)
    // ─ NAVIGATION ─
    PH += DIV;                                  // divider
    PH += SEC;                                  // section label
    PH += R_H;                                  // speed bar row
    PH += R_H;                                  // direction row
    PH += R_H;                                  // position row
    // ─ SHIP ─
    PH += DIV;
    PH += SEC;
    PH += R_H;                                  // hull bar
    PH += R_H;                                  // fuel bar
    if (fuelEmpty || fuelLow)  PH += R_H;       // optional fuel warning
    // ─ CARGO ─
    PH += DIV;
    PH += SEC;
    PH += R_H;                                  // hold label+count
    PH += B_OFF + B_H + 5;                      // cargo bar  (B_OFF + bar + gap)
    PH += (emptyHold ? 1 : resRows) * R_H;      // resource rows (or empty-hold text)
    // ─ Pods (optional) ─
    if (attachedPods.length > 0) {
      PH += DIV;
      PH += attachedPods.length * R_H;
    }
    // ─ CONTEXT ─
    PH += DIV;
    PH += SEC;
    PH += R_H;  // [C]
    PH += R_H;  // [E]
    // Footer
    PH += DIV_A + 1 + DIV_B;                   // thin divider above coords
    PH += R_H;                                  // coordinate row
    PH += PAD_Y;

    // ── Panel background ──
    ctx.save();
    ctx.fillStyle = 'rgba(2,6,14,0.86)';
    roundRect(ctx, PX, PY_TOP, PW, PH, 4);
    ctx.fill();
    ctx.strokeStyle = TEAL + '28';
    ctx.lineWidth = 1;
    roundRect(ctx, PX, PY_TOP, PW, PH, 4);
    ctx.stroke();
    ctx.fillStyle = TEAL;
    ctx.fillRect(PX, PY_TOP, 2, PH);            // left accent bar
    ctx.restore();

    // ── Content layout columns (fixed; nothing positions by text width) ──
    //   Row grid:  [labelX ..]  [gaugeX .. gaugeX+gaugeW]   GAP   [.. valueX]
    //   The gauge and the value occupy separate X ranges and can never overlap.
    const L       = PX + PAD_X;               // labelX — left text start
    const R       = PX + PW - PAD_X;          // valueX — right-aligned value column edge
    const VALUE_W = 60;                       // reserved width for the value column
    const GAP     = 8;                        // gap between gauge and value column
    const LV      = L + 44;                   // gaugeX — bar left edge
    const BW      = (R - VALUE_W - GAP) - LV; // gaugeW — bar width (value column stays clear)

    let y = PY_TOP + PAD_Y;

    const F_SML = '11px "Courier New",monospace';
    const F_MED = '12px "Courier New",monospace';
    const F_HDR = 'bold 13px "Courier New",monospace';
    const F_SEC = '10px "Courier New",monospace';
    const F_XSM = '10px "Courier New",monospace';

    // ── DEV: collision-box overlay (F2). Boxes each layout row so overlaps are obvious. ──
    const HDBG = !!debugBoxes;
    function hbox(y0) {
      if (hudBounds) hudBounds.push({ y0, y1: y });
      if (!HDBG) return;
      ctx.save();
      ctx.strokeStyle = '#ff00ff'; ctx.lineWidth = 0.5;
      ctx.strokeRect(PX + 1.5, y0 + 0.5, PW - 3, (y - y0) - 1);
      ctx.restore();
    }

    // ── helper: bar row (label + fill bar + right-aligned value) ──
    function barRow(label, pct, c0, c1, valStr, valCol) {
      const _y0 = y;
      ctx.font = F_SML; ctx.fillStyle = DIM; ctx.textAlign = 'left';
      ctx.fillText(label, L, y + TXT);
      const bx = LV, by = y + B_OFF;
      ctx.fillStyle = '#08111e';
      ctx.fillRect(bx, by, BW, B_H);
      const bg = ctx.createLinearGradient(bx, 0, bx + BW, 0);
      bg.addColorStop(0, c0); bg.addColorStop(1, c1 || c0);
      ctx.fillStyle = bg;
      ctx.fillRect(bx, by, BW * Math.min(Math.max(pct, 0), 1), B_H);
      ctx.strokeStyle = '#ffffff0c'; ctx.lineWidth = 0.5;
      ctx.strokeRect(bx, by, BW, B_H);
      if (valStr !== undefined) {
        ctx.font = F_SML; ctx.fillStyle = valCol || WHT; ctx.textAlign = 'right';
        ctx.fillText(valStr, R, y + TXT);
        ctx.textAlign = 'left';
      }
      y += R_H;
      hbox(_y0);
    }

    // ── helper: plain text row (left label + optional right value) ──
    function txtRow(label, val, lCol, vCol) {
      const _y0 = y;
      ctx.font = F_SML; ctx.fillStyle = lCol || DIM; ctx.textAlign = 'left';
      ctx.fillText(label, L, y + TXT);
      if (val !== undefined) {
        ctx.font = F_SML; ctx.fillStyle = vCol || WHT; ctx.textAlign = 'right';
        ctx.fillText(val, R, y + TXT);
        ctx.textAlign = 'left';
      }
      y += R_H;
      hbox(_y0);
    }

    // ── helper: section divider + label ──
    function section(label) {
      const _y0 = y;
      y += DIV_A;
      ctx.strokeStyle = TEAL + '20'; ctx.lineWidth = 0.75;
      ctx.beginPath(); ctx.moveTo(PX + 4, y + 0.5); ctx.lineTo(PX + PW - 4, y + 0.5); ctx.stroke();
      y += 1 + DIV_B;
      ctx.font = F_SEC; ctx.fillStyle = TEAL + '99'; ctx.textAlign = 'left';
      ctx.fillText(label, L, y + TXT - 1);
      y += R_H + SEC_B;
      hbox(_y0);
    }

    // ════════════════════════════════════════════
    // HEADER — ship name + inline compass
    // ════════════════════════════════════════════
    ctx.save();
    ctx.font = F_HDR; ctx.fillStyle = TEAL;
    ctx.shadowColor = TEAL; ctx.shadowBlur = 5; ctx.textAlign = 'left';
    ctx.fillText('◈  ' + (ship.shipType ? ship.shipType.name.toUpperCase() : 'SHIP'), L, y + TXT + 1);
    ctx.shadowBlur = 0;
    // Compass
    const cpX = PX + PW - PAD_X - 11, cpY = y + 9, cpR = 10;
    ctx.strokeStyle = DIM; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cpX, cpY, cpR, 0, Math.PI * 2); ctx.stroke();
    const dIdx = DIRS.indexOf(ship.dir);
    if (dIdx >= 0) {
      const da = DIR_ANGLES_DEG[dIdx] * Math.PI / 180;
      ctx.strokeStyle = TEAL; ctx.lineWidth = 1.8;
      ctx.shadowColor = TEAL; ctx.shadowBlur = 4;
      ctx.beginPath(); ctx.moveTo(cpX, cpY);
      ctx.lineTo(cpX + Math.cos(da) * (cpR - 1), cpY + Math.sin(da) * (cpR - 1));
      ctx.stroke(); ctx.shadowBlur = 0;
    }
    ctx.restore();
    y += R_H + 4;

    // ════════════════════════════════════════════
    // NAVIGATION
    // ════════════════════════════════════════════
    section('NAVIGATION');

    // Speed bar
    barRow('SPD',
      speed / boostMax,
      '#1e5a7a', boostOn ? '#ff6b35' : TEAL,
      speed.toFixed(2),
      boostOn ? '#ff9055' : WHT);

    // Direction
    txtRow('DIR', ship.dir.toUpperCase().replace('-', '  '));

    // Position
    txtRow('POS', Math.floor(ship.worldX) + '  ·  ' + Math.floor(ship.worldY));

    // ════════════════════════════════════════════
    // SHIP
    // ════════════════════════════════════════════
    section('SHIP');

    // Hull bar
    barRow('HULL',
      hpPct,
      hpPct > 0.5 ? '#1d5e38' : hpPct > 0.25 ? '#7a5500' : '#6b1000',
      hpPct > 0.5 ? '#36e878' : hpPct > 0.25 ? '#ffbb00' : '#ff3333',
      ship.hp + ' / ' + shipMaxHp,
      hpPct < 0.25 ? ERR : WHT);

    // Fuel — segmented bar (custom renderer)
    const _yFuel = y;
    ctx.font = F_SML; ctx.textAlign = 'left';
    if (boostOn) { ctx.shadowColor = '#ff8800'; ctx.shadowBlur = 5; ctx.fillStyle = '#ffcc55'; }
    else         { ctx.shadowBlur = 0; ctx.fillStyle = fuelLow ? ORANGE : DIM; }
    ctx.fillText('FUEL', L, y + TXT);
    ctx.shadowBlur = 0;

    const segN  = 10, segGap = 2;
    const segBW = Math.floor((BW - segGap * (segN - 1)) / segN);
    const fBy   = y + B_OFF;
    for (let i = 0; i < segN; i++) {
      const lit = i < Math.ceil(fuelPct * segN);
      let sc;
      if (!lit) { sc = '#08111e'; }
      else if (boostOn) {
        const flk = 0.55 + 0.45 * Math.sin(t * 0.018 + i * 0.9);
        sc = `rgb(255,${Math.round(80 + 120 * flk)},${Math.round(10 + 30 * flk)})`;
      } else {
        sc = fuelPct > 0.5 ? '#2a9e5a' : fuelPct > 0.25 ? '#c8a020' : ORANGE;
      }
      if (boostOn && lit) { ctx.shadowColor = '#ff6600'; ctx.shadowBlur = 3 + 2 * Math.sin(t * 0.02 + i); }
      ctx.fillStyle = sc;
      ctx.fillRect(LV + i * (segBW + segGap), fBy, segBW, B_H);
      ctx.shadowBlur = 0;
      ctx.strokeStyle = TEAL + '14'; ctx.lineWidth = 0.5;
      ctx.strokeRect(LV + i * (segBW + segGap), fBy, segBW, B_H);
    }
    ctx.font = F_SML; ctx.fillStyle = fuelLow ? ORANGE : WHT; ctx.textAlign = 'right';
    ctx.fillText(ship.fuel.toFixed(1) + ' gal', R, y + TXT);
    ctx.textAlign = 'left';
    y += R_H;
    hbox(_yFuel);

    // Fuel warning (only when applicable — height already reserved in PH)
    if (fuelEmpty) {
      const _yw = y;
      ctx.font = F_SML; ctx.fillStyle = ERR; ctx.textAlign = 'left';
      ctx.fillText('✕  FUEL EMPTY — ADRIFT', L, y + TXT);
      y += R_H;
      hbox(_yw);
    } else if (fuelLow) {
      const _yw = y;
      const blink = Math.floor(t / 500) % 2 === 0;
      ctx.font = F_SML; ctx.fillStyle = blink ? '#ffaa00' : ORANGE; ctx.textAlign = 'left';
      ctx.fillText('⚠  LOW FUEL', L, y + TXT);
      y += R_H;
      hbox(_yw);
    }

    // ════════════════════════════════════════════
    // CARGO
    // ════════════════════════════════════════════
    section('CARGO');

    // Hold header row
    const _yHold = y;
    ctx.font = F_SML; ctx.fillStyle = cFull ? ERR : DIM; ctx.textAlign = 'left';
    ctx.fillText('HOLD', L, y + TXT);
    ctx.font = F_SML; ctx.fillStyle = cFull ? ERR : WHT; ctx.textAlign = 'right';
    ctx.fillText(cUsed + ' / ' + cMax + (cFull ? '  ●FULL' : ''), R, y + TXT);
    ctx.textAlign = 'left';
    y += R_H;
    hbox(_yHold);

    // Cargo fill bar (thin, full panel width)
    const _yBar = y;
    const cbx = L, cby = y + B_OFF, cbw = PW - PAD_X * 2, cbh = B_H;
    ctx.fillStyle = '#08111e'; ctx.fillRect(cbx, cby, cbw, cbh);
    const cg = ctx.createLinearGradient(cbx, 0, cbx + cbw, 0);
    cg.addColorStop(0, '#1e5a7a'); cg.addColorStop(1, cFull ? ERR : ACC);
    ctx.fillStyle = cg;
    // Chief QA fix: clamp fill ratio to [0,1] so the bar never draws outside
    // its own bounds regardless of data (e.g. dev cheats or any future path
    // that lets cUsed exceed cMax). Same clamp pattern already used by
    // barRow() above. The numeric "cUsed / cMax" label above is untouched --
    // it stays truthful even when the bar itself is visually capped.
    const cargoFillRatio = Math.min(Math.max(cUsed / Math.max(cMax, 1), 0), 1);
    ctx.fillRect(cbx, cby, cbw * cargoFillRatio, cbh);
    ctx.strokeStyle = '#ffffff0c'; ctx.lineWidth = 0.5;
    ctx.strokeRect(cbx, cby, cbw, cbh);
    y += B_OFF + B_H + 5;
    hbox(_yBar);

    // Resource rows
    if (emptyHold) {
      const _yr = y;
      ctx.font = F_SML; ctx.fillStyle = DIM; ctx.textAlign = 'left';
      ctx.fillText('— empty hold —', L + 6, y + TXT);
      y += R_H;
      hbox(_yr);
    } else {
      if (ship.ore > 0) {
        const _yr = y;
        ctx.font = F_MED; ctx.fillStyle = '#FFD700'; ctx.textAlign = 'left';
        ctx.fillText('◆  ' + ship.ore + '  NEBULITE', L + 4, y + TXT);
        y += R_H;
        hbox(_yr);
      }
      if (ship.mineral > 0) {
        const _yr = y;
        ctx.font = F_MED; ctx.fillStyle = '#c4b5fd'; ctx.textAlign = 'left';
        ctx.fillText('♦  ' + ship.mineral + '  MINERAL', L + 4, y + TXT);
        y += R_H;
        hbox(_yr);
      }
      if (ship.armalcolite > 0) {
        const _yr = y;
        ctx.font = F_MED; ctx.fillStyle = '#6ee7b7'; ctx.textAlign = 'left';
        ctx.fillText('◈  ' + ship.armalcolite + '  ARMALCOLITE', L + 4, y + TXT);
        y += R_H;
        hbox(_yr);
      }
    }

    // ─ Attached pods ─
    if (attachedPods.length > 0) {
      y += DIV_A;
      ctx.strokeStyle = ACC + '20'; ctx.lineWidth = 0.75;
      ctx.beginPath(); ctx.moveTo(PX + 4, y + 0.5); ctx.lineTo(PX + PW - 4, y + 0.5); ctx.stroke();
      y += 1 + DIV_B;
      attachedPods.forEach(p => {
        const _yp = y;
        ctx.font = F_MED; ctx.fillStyle = p.color || ACC; ctx.textAlign = 'left';
        ctx.fillText('⦿  ' + p.label + (p.cargoBonus ? '  +' + p.cargoBonus + ' cargo' : ''), L + 4, y + TXT);
        y += R_H;
        hbox(_yp);
      });
    }

    // ════════════════════════════════════════════
    // CONTEXT
    // ════════════════════════════════════════════
    section('CONTEXT');

    const canCraft = ship.armalcolite > 0;
    ctx.textAlign = 'left';

    // [C] Refine
    const _yC = y;
    ctx.font = F_SML; ctx.fillStyle = canCraft ? '#FFD700' : DIM;
    ctx.fillText('[C]', L, y + TXT);
    ctx.fillStyle = canCraft ? WHT : DIM;
    ctx.fillText(' REFINE  →  +' + fuelPerCraft.toFixed(1) + ' FUEL', L + 22, y + TXT);
    y += R_H;
    hbox(_yC);

    // [E] Mine
    const _yE = y;
    ctx.font = F_SML; ctx.fillStyle = mineTarget ? TEAL : DIM;
    ctx.fillText('[E]', L, y + TXT);
    ctx.fillStyle = mineTarget ? WHT : DIM;
    ctx.fillText(' MINE' + (mineTarget ? '  ' + Math.round(mineDist) + ' px' : ''), L + 22, y + TXT);
    y += R_H;
    hbox(_yE);

    // ════════════════════════════════════════════
    // FOOTER — coordinates
    // ════════════════════════════════════════════
    const _yF = y;
    y += DIV_A;
    ctx.strokeStyle = TEAL + '14'; ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.moveTo(PX + 4, y + 0.5); ctx.lineTo(PX + PW - 4, y + 0.5); ctx.stroke();
    y += 1 + DIV_B;
    ctx.font = F_XSM; ctx.fillStyle = DIM + 'cc'; ctx.textAlign = 'left';
    ctx.fillText(Math.floor(ship.worldX) + ' / ' + Math.floor(ship.worldY), L, y + TXT);
    y += R_H;
    hbox(_yF);
  }

  return { render };
}
