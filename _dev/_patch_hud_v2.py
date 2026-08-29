import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. drawAttachedPods — draw pod physically tethered behind ship
#    + keep save indicator
# ══════════════════════════════════════════════════════════════════
OLD_ATTACHED = re.compile(
    r'function drawAttachedPods\(cx, cy\) \{.*?\}',
    re.DOTALL
)

NEW_ATTACHED = r'''function drawAttachedPods(cx, cy) {

  // ── Physical pod(s) tethered behind the ship ──────────────────
  if (attachedPods.length) {
    const now   = Date.now();
    const t     = now * 0.001;

    // Offset pod behind ship based on facing direction
    const DIR_OFFSETS = {
      north:      { ox:  0,   oy:  38 },
      northeast:  { ox: -27,  oy:  27 },
      east:       { ox: -38,  oy:  0  },
      southeast:  { ox: -27,  oy: -27 },
      south:      { ox:  0,   oy: -38 },
      southwest:  { ox:  27,  oy: -27 },
      west:       { ox:  38,  oy:  0  },
      northwest:  { ox:  27,  oy:  27 },
    };
    const off = DIR_OFFSETS[ship.dir] || { ox: 0, oy: 38 };

    attachedPods.forEach((pod, idx) => {
      // Stack multiple pods further back
      const dist  = 42 + idx * 36;
      const ratio = dist / 38;
      const px    = cx + off.ox * ratio;
      const py    = cy + off.oy * ratio;

      // Tether line
      ctx.save();
      ctx.strokeStyle = '#38bdf866';
      ctx.lineWidth   = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(px, py);
      ctx.stroke();
      ctx.setLineDash([]);

      // Pod sprite or fallback hex
      const podSize  = 44;
      const bobY     = Math.sin(t * 1.8 + idx * 1.2) * 2;
      const podFrame = podRotations['south'];

      ctx.translate(px, py + bobY);
      ctx.shadowColor = pod.color || '#38bdf8';
      ctx.shadowBlur  = 10;
      if (podFrame) {
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(podFrame, -podSize/2, -podSize/2, podSize, podSize);
      } else {
        // Hex fallback
        ctx.fillStyle = (pod.color || '#38bdf8') + 'cc';
        ctx.beginPath();
        for (let k = 0; k < 6; k++) {
          const a = (k/6)*Math.PI*2 - Math.PI/6;
          k === 0 ? ctx.moveTo(Math.cos(a)*14, Math.sin(a)*14)
                  : ctx.lineTo(Math.cos(a)*14, Math.sin(a)*14);
        }
        ctx.closePath(); ctx.fill();
      }
      ctx.shadowBlur = 0;
      ctx.restore();
    });
  }

  // ── Save flash indicator (top-right) ──────────────────────────
  const saveFlash = _autoSaveTimer > 1780;
  if (saveFlash) {
    ctx.save();
    ctx.textAlign = 'right';
    ctx.font      = '11px Courier New';
    ctx.fillStyle = '#22c55e';
    ctx.fillText('\u25cf SAVING...', canvas.width - 14, 16);
    ctx.restore();
  }
}'''

if OLD_ATTACHED.search(d):
    d = OLD_ATTACHED.sub(NEW_ATTACHED, d)
    fixes.append('drawAttachedPods — physical pod behind ship')
else:
    fixes.append('drawAttachedPods: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. Full HUD redesign — replace entire drawHUD function
# ══════════════════════════════════════════════════════════════════
OLD_HUD = re.compile(r'function drawHUD\(speed\) \{.*?\n\}', re.DOTALL)

NEW_HUD = r'''function drawHUD(speed) {
  const L      = 18;       // left margin
  const PW     = 310;      // panel width
  const LINE   = 22;       // standard line height
  const SML    = '13px Courier New';
  const MED    = '15px Courier New';
  const BIG    = 'bold 15px Courier New';
  const DIM    = '#4a6070';
  const TEAL   = '#4FC3C3';
  const ORANGE = '#D9541E';
  const WHITE  = '#c8d8e8';

  // Helper: section divider bar
  function sectionBar(y, label, col) {
    col = col || TEAL;
    ctx.fillStyle = col + '33';
    ctx.fillRect(10, y - 14, PW, 18);
    ctx.fillStyle = col;
    ctx.fillRect(10, y - 14, 3, 18);
    ctx.font = 'bold 11px Courier New';
    ctx.fillStyle = col;
    ctx.fillText(label, L + 6, y);
  }

  // Helper: horizontal key/value line
  function kv(key, val, x, y, valCol) {
    ctx.font = SML; ctx.fillStyle = DIM;
    ctx.fillText(key, x, y);
    ctx.font = MED; ctx.fillStyle = valCol || WHITE;
    ctx.fillText(val, x + 68, y);
  }

  // Helper: filled bar
  function bar(x, y, w, h, pct, col1, col2) {
    ctx.fillStyle = '#0d1520';
    ctx.fillRect(x - 1, y - 1, w + 2, h + 2);
    const g = ctx.createLinearGradient(x, 0, x + w, 0);
    g.addColorStop(0, col1); g.addColorStop(1, col2 || col1);
    ctx.fillStyle = g;
    ctx.fillRect(x, y, w * Math.min(pct, 1), h);
    ctx.strokeStyle = '#ffffff14'; ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);
  }

  // ── Measure panel height dynamically ──
  const resCount = (ship.ore > 0 ? 1 : 0) + (ship.mineral > 0 ? 1 : 0) + (ship.armalcolite > 0 ? 1 : 0);
  const panelH   = 310 + resCount * LINE + (attachedPods.length ? LINE : 0);

  // ── Panel background ──
  ctx.fillStyle   = '#000000e0';
  ctx.fillRect(10, 10, PW, panelH);
  ctx.strokeStyle = TEAL + '30';
  ctx.lineWidth   = 1;
  ctx.strokeRect(10, 10, PW, panelH);
  // Left accent stripe
  ctx.fillStyle = TEAL + '60';
  ctx.fillRect(10, 10, 3, panelH);

  let y = 30;

  // ══ SECTION: NAVIGATION ═══════════════════════════════════════
  sectionBar(y, 'NAVIGATION', TEAL);
  y += LINE + 2;
  kv('SPD', speed.toFixed(2),                                          L, y);
  y += LINE;
  kv('DIR', ship.dir.replace('-', ' ').toUpperCase(),                  L, y);
  y += LINE;
  kv('POS', Math.floor(ship.worldX) + ' / ' + Math.floor(ship.worldY), L, y);
  y += LINE + 4;

  // ══ SECTION: SHIP ═════════════════════════════════════════════
  sectionBar(y, 'SHIP  ' + ship.shipType.name, TEAL);
  y += LINE + 2;

  // THRUST bar
  ctx.font = SML; ctx.fillStyle = DIM; ctx.fillText('THRUST', L, y);
  y += 4;
  bar(L, y, PW - 28, 8, speed / BOOST_MAX, '#4FC3C3', '#ff2222');
  y += 18;

  // HULL bar
  const hpPct = ship.hp / SHIP_MAX_HP;
  const hpCol = hpPct < 0.25 ? '#ff4444' : hpPct < 0.5 ? '#ffcc00' : '#22bb55';
  ctx.font = SML; ctx.fillStyle = DIM; ctx.fillText('HULL', L, y);
  ctx.font = SML; ctx.fillStyle = hpPct < 0.25 ? '#ff4444' : WHITE;
  ctx.fillText(ship.hp + ' / ' + SHIP_MAX_HP, L + 68, y);
  y += 4;
  bar(L, y, PW - 28, 8, hpPct,
    hpPct > 0.5 ? '#22bb55' : hpPct > 0.25 ? '#aa6600' : '#880000',
    hpPct > 0.5 ? '#44ff88' : hpPct > 0.25 ? '#ffcc00' : '#ff2222');
  y += 18;

  // FUEL segments
  const fuelPct   = ship.fuel / FUEL_CAPACITY;
  const segCount  = 10;
  const segW      = Math.floor((PW - 28) / segCount) - 2;
  const filledSegs = Math.ceil(fuelPct * segCount);
  ctx.font = SML; ctx.fillStyle = DIM; ctx.fillText('FUEL', L, y);
  ctx.font = SML; ctx.fillStyle = fuelPct < 0.25 ? ORANGE : WHITE;
  ctx.fillText(ship.fuel.toFixed(1) + ' gal', L + 68, y);
  y += 4;
  for (let i = 0; i < segCount; i++) {
    const lit  = i < filledSegs;
    const fcol = !lit ? '#0d1520'
      : fuelPct > 0.5  ? '#3db87a'
      : fuelPct > 0.25 ? '#e6c040'
      : (fuelPct < 0.1 && Math.floor(Date.now()/300)%2===0) ? '#ff2222' : ORANGE;
    ctx.fillStyle = fcol;
    ctx.fillRect(L + i*(segW+2), y, segW, 10);
    ctx.strokeStyle = '#4FC3C318'; ctx.lineWidth = 0.5;
    ctx.strokeRect(L + i*(segW+2), y, segW, 10);
  }
  y += 18;
  if (ship.fuel <= 0) {
    ctx.font = SML; ctx.fillStyle = '#ff4444';
    ctx.fillText('\u2715 FUEL EMPTY \u2014 COASTING', L, y); y += LINE;
  } else if (fuelPct < 0.2 && Math.floor(Date.now()/500)%2===0) {
    ctx.font = SML; ctx.fillStyle = ORANGE;
    ctx.fillText('\u26a0 LOW FUEL', L, y); y += LINE;
  }

  // Hull-destroyed overlay
  if (ship.hp <= 0) {
    if (!ship.destroyed) {
      ship.destroyed = true; ship.destroyedAt = Date.now();
      for (let i = 0; i < 60; i++) {
        const ang = Math.random()*Math.PI*2, spd = 1+Math.random()*5;
        particles.push({x:canvas.width/2,y:canvas.height/2,
          vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
          life:80+Math.random()*60,maxLife:140,
          color:['#ff4444','#ff8800','#ffcc00','#ffffff'][Math.floor(Math.random()*4)],
          size:2+Math.random()*4});
      }
    }
    const elapsed   = Date.now() - (ship.destroyedAt||Date.now());
    const remaining = Math.ceil((4000-elapsed)/1000);
    ctx.fillStyle='#000000bb'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.textAlign='center';
    ctx.font='bold 32px Courier New'; ctx.fillStyle='#ff2222';
    ctx.fillText('\u2715  SHIP DESTROYED',canvas.width/2,canvas.height/2-30);
    ctx.font='20px Courier New'; ctx.fillStyle='#ff8800';
    ctx.fillText('RESPAWNING IN '+Math.max(0,remaining)+'...',canvas.width/2,canvas.height/2+14);
    ctx.textAlign='left';
    if (elapsed>=4000) {
      if (ship.ore > 0 || ship.mineral > 0 || ship.armalcolite > 0) {
        worldPods.push({
          pid:'wreck_'+Date.now(), type:'_wreck',
          worldX:ship.worldX+(Math.random()-0.5)*40,
          worldY:ship.worldY+(Math.random()-0.5)*40,
          angle:Math.random()*Math.PI*2,
          cargo:{ore:ship.ore,mineral:ship.mineral,armalcolite:ship.armalcolite},
          label:'WRECK',
        });
      }
      ship.ore=0; ship.mineral=0; ship.armalcolite=0;
      ship.hp=SHIP_MAX_HP;
      ship.worldX=(Math.random()-0.5)*300; ship.worldY=(Math.random()-0.5)*300;
      ship.vx=0; ship.vy=0; ship.destroyed=false;
      saveGame();
      showToast('RESPAWNED \u2014 cargo lost. Find your wreck.','#f97316');
    }
    return;
  }

  // ══ SECTION: CARGO ════════════════════════════════════════════
  sectionBar(y, 'CARGO', '#f59e0b');
  y += LINE + 2;

  const cUsed = cargoUsed();
  const cMax  = ship.shipType.cargoLimit || CARGO_LIMIT;
  const cPct  = Math.min(cUsed / cMax, 1);
  const cFull = cUsed >= cMax;

  // Cargo bar
  bar(L, y, PW - 28, 6, cPct,
    cPct < 0.7 ? '#4FC3C3' : cPct < 0.95 ? ORANGE : '#ff2222',
    cPct < 0.7 ? '#22aacc' : cPct < 0.95 ? '#ffaa44' : '#ff6666');
  ctx.font = SML;
  ctx.fillStyle = cFull ? '#ef4444' : WHITE;
  ctx.fillText(cUsed + ' / ' + cMax + (cFull ? '  FULL' : ''), L + (PW - 28) + 6, y + 6);
  y += 14;

  // Resource rows — only when held
  if (ship.ore > 0) {
    ctx.font = 'bold 14px monospace'; ctx.fillStyle = '#FFD700';
    ctx.fillText('\u25c6', L + 4, y);
    ctx.font = MED; ctx.fillStyle = '#FFD700';
    ctx.fillText(ship.ore + '  NEBULITE', L + 18, y);
    y += LINE;
  }
  if (ship.mineral > 0) {
    ctx.font = 'bold 14px monospace'; ctx.fillStyle = '#a78bfa';
    ctx.fillText('\u2666', L + 4, y);
    ctx.font = MED; ctx.fillStyle = '#c4b5fd';
    ctx.fillText(ship.mineral + '  MINERAL', L + 18, y);
    y += LINE;
  }
  if (ship.armalcolite > 0) {
    ctx.font = 'bold 14px monospace'; ctx.fillStyle = '#34d399';
    ctx.fillText('\u25c8', L + 4, y);
    ctx.font = MED; ctx.fillStyle = '#6ee7b7';
    ctx.fillText(ship.armalcolite + '  ARMALCOLITE', L + 18, y);
    y += LINE;
  }
  if (cUsed === 0) {
    ctx.font = SML; ctx.fillStyle = DIM;
    ctx.fillText('empty hold', L + 4, y); y += LINE;
  }

  // ══ SECTION: MODULES ══════════════════════════════════════════
  if (attachedPods.length) {
    sectionBar(y, 'MODULES', '#38bdf8');
    y += LINE + 2;
    attachedPods.forEach(p => {
      ctx.font = 'bold 13px monospace'; ctx.fillStyle = p.color || '#38bdf8';
      ctx.fillText('\u29BF', L + 4, y);
      ctx.font = SML; ctx.fillStyle = p.color || '#38bdf8';
      ctx.fillText(p.label, L + 18, y);
      if (p.cargoBonus) {
        ctx.fillStyle = DIM;
        ctx.fillText('+' + p.cargoBonus + ' cargo', L + 18 + 110, y);
      }
      y += LINE;
    });
  }

  // ══ SECTION: ACTIONS ══════════════════════════════════════════
  sectionBar(y, 'ACTIONS', '#64748b');
  y += LINE + 2;

  const canCraft = ship.armalcolite > 0;
  ctx.font = SML;
  ctx.fillStyle = canCraft ? '#FFD700' : DIM;
  ctx.fillText('[C]', L, y);
  ctx.fillStyle = canCraft ? WHITE : DIM;
  ctx.fillText('REFINE  1 ARM \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', L + 26, y);
  y += LINE;

  ctx.fillStyle = mineTarget ? TEAL : DIM;
  ctx.fillText('[E]', L, y);
  ctx.fillStyle = mineTarget ? WHITE : DIM;
  ctx.fillText('MINE' + (mineTarget ? '  ' + Math.round(mineDist) + 'px' : ''), L + 26, y);
  y += LINE;

  // ══ SECTION: NETWORK ══════════════════════════════════════════
  if (typeof multiMode !== 'undefined' && multiMode) {
    sectionBar(y, 'NETWORK', '#38bdf8');
    y += LINE + 2;
    ctx.font = SML; ctx.fillStyle = '#38bdf8';
    ctx.fillText('\u25a0  ' + (Object.keys(remotePlayers).length + 1) + ' pilots online', L, y);
    y += LINE;
  }

  // ── Mini compass (top-right of panel, fixed pos) ──
  const cx2 = 10 + PW - 36, cy2 = 58, r = 22;
  ctx.strokeStyle = '#1a2a3a'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(cx2, cy2, r, 0, Math.PI*2); ctx.stroke();
  const dirIdx = DIRS.indexOf(ship.dir);
  if (dirIdx >= 0) {
    const a = DIR_ANGLES_DEG[dirIdx] * (Math.PI / 180);
    ctx.strokeStyle = TEAL; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx2, cy2);
    ctx.lineTo(cx2 + Math.cos(a)*(r-4), cy2 + Math.sin(a)*(r-4)); ctx.stroke();
    ctx.fillStyle = TEAL;
    ctx.beginPath(); ctx.arc(cx2+Math.cos(a)*(r-4), cy2+Math.sin(a)*(r-4), 3, 0, Math.PI*2); ctx.fill();
  }
  ctx.fillStyle = '#1a2a3a88';
  ctx.beginPath(); ctx.arc(cx2, cy2, 3, 0, Math.PI*2); ctx.fill();

  // ── Map zone flash ──
  if (bgFlash && bgFlash.timer > 0) {
    const alpha = Math.min(1, bgFlash.timer / 30);
    ctx.globalAlpha = alpha; ctx.fillStyle = TEAL;
    ctx.font = '18px Courier New'; ctx.textAlign = 'center';
    ctx.fillText('MAP: ' + bgFlash.name.replace('_',' ').toUpperCase(), canvas.width/2, canvas.height - 30);
    ctx.textAlign = 'left'; ctx.globalAlpha = 1;
    bgFlash.timer--;
  }
}'''

if OLD_HUD.search(d):
    d = OLD_HUD.sub(NEW_HUD, d)
    fixes.append('drawHUD fully redesigned with section bars')
else:
    fixes.append('drawHUD: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
