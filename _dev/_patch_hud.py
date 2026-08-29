import shutil, os
src = 'driftbound_flight_test.html'
shutil.copy(src, src + '.bak')
lines = open(src, 'r', encoding='utf-8').readlines()

# Find HUD_FONT const line and drawDebug line
hud_start = next(i for i,l in enumerate(lines) if 'const HUD_FONT' in l and 'Courier' in l)
debug_start = next(i for i,l in enumerate(lines) if 'function drawDebug(speed)' in l)
print(f'Replacing lines {hud_start+1} to {debug_start} (HUD block)')

NEW_HUD = r"""const HUD_FONT    = '13px Courier New';
const HUD_FONT_SM = '11px Courier New';
const HUD_COLOR = '#4FC3C3';
const HUD_DIM   = '#4FC3C380';

function hLine(label, value, x, y) {
  ctx.font      = HUD_FONT;
  ctx.fillStyle = HUD_DIM;
  ctx.fillText(label, x, y);
  ctx.fillStyle = HUD_COLOR;
  ctx.fillText(value, x + 54, y);
}

function drawHUD(speed) {
  const LEFT  = 22;
  const TOP   = 28;
  const PW    = 245;
  const LH    = 17;

  const statsTop = TOP + 14;
  const thrustY  = statsTop + LH * 3 + 12;
  const hullY    = thrustY + 24;
  const fuelY    = hullY  + 30;
  const oreY     = fuelY  + 46;
  const minY     = oreY   + LH + 4;
  const armY     = minY   + LH + 2;
  const pilotY   = armY   + LH + 6;
  const hintY    = pilotY + LH + 8;
  const panelH   = hintY  + LH * 2 + 16;

  ctx.fillStyle = '#000000d0';
  ctx.fillRect(10, 10, PW, panelH);
  ctx.strokeStyle = '#4FC3C344';
  ctx.lineWidth = 1;
  ctx.strokeRect(10, 10, PW, panelH);

  // STATS
  hLine('SPD', speed.toFixed(2),                                           LEFT, statsTop);
  hLine('DIR', ship.dir.replace('-', ' ').toUpperCase(),                   LEFT, statsTop + LH);
  hLine('POS', Math.floor(ship.worldX) + ' / ' + Math.floor(ship.worldY), LEFT, statsTop + LH * 2);

  // THRUST bar
  const bx = LEFT, by = thrustY, bw = PW - 34, bh = 5;
  ctx.font = HUD_FONT_SM; ctx.fillStyle = HUD_DIM;
  ctx.fillText('THRUST', bx, by - 5);
  ctx.fillStyle = '#0d1520';
  ctx.fillRect(bx-1, by-1, bw+2, bh+2);
  const grad = ctx.createLinearGradient(bx, 0, bx+bw, 0);
  grad.addColorStop(0,'#4FC3C3'); grad.addColorStop(0.6,'#D9541E'); grad.addColorStop(1,'#ff2222');
  ctx.fillStyle = grad;
  ctx.fillRect(bx, by, (speed / BOOST_MAX) * bw, bh);
  ctx.strokeStyle = '#4FC3C340'; ctx.lineWidth = 1;
  ctx.strokeRect(bx, by, bw, bh);

  // HULL bar
  const hbx = LEFT, hby = hullY, hbw = PW - 34, hbh = 5;
  const hpPct = ship.hp / SHIP_MAX_HP;
  ctx.font = HUD_FONT_SM; ctx.fillStyle = HUD_DIM;
  ctx.fillText('HULL', hbx, hby - 4);
  ctx.fillStyle = hpPct < 0.25 ? '#ff4444' : HUD_COLOR;
  ctx.fillText(ship.hp + ' / ' + SHIP_MAX_HP, hbx + hbw - 52, hby - 4);
  ctx.fillStyle = '#0d1520';
  ctx.fillRect(hbx-1, hby-1, hbw+2, hbh+2);
  const hGrad = ctx.createLinearGradient(hbx, 0, hbx+hbw, 0);
  if (hpPct > 0.5)       { hGrad.addColorStop(0,'#22bb55'); hGrad.addColorStop(1,'#44ff88'); }
  else if (hpPct > 0.25) { hGrad.addColorStop(0,'#aa6600'); hGrad.addColorStop(1,'#ffcc00'); }
  else                   { hGrad.addColorStop(0,'#880000'); hGrad.addColorStop(1,'#ff2222'); }
  ctx.fillStyle = hGrad;
  ctx.fillRect(hbx, hby, hbw * hpPct, hbh);
  ctx.strokeStyle = '#ffffff18'; ctx.lineWidth = 1;
  ctx.strokeRect(hbx, hby, hbw, hbh);
  if (ship.hp <= 0 && Math.floor(Date.now()/400)%2===0) {
    ctx.fillStyle = '#ff2222'; ctx.font = 'bold 14px Courier New'; ctx.textAlign = 'center';
    ctx.fillText('\u2715 HULL BREACH \u2014 CRITICAL', canvas.width/2, canvas.height/2 - 20);
    ctx.textAlign = 'left';
  }

  // FUEL segments
  const fx = LEFT, fy = fuelY;
  const segCount = 10, segW = Math.floor((PW - 36) / 10) - 1, segH = 12, segGap = 2;
  const fuelPct = ship.fuel / FUEL_CAPACITY;
  const filledSegs = Math.ceil(fuelPct * segCount);
  ctx.font = HUD_FONT_SM; ctx.fillStyle = HUD_DIM;
  ctx.fillText('FUEL', fx, fy - 5);
  for (let i = 0; i < segCount; i++) {
    const lit = i < filledSegs;
    let fill = !lit ? '#0d1520'
      : fuelPct > 0.5  ? '#3db87a'
      : fuelPct > 0.25 ? '#e6c040'
      : (fuelPct < 0.1 && Math.floor(Date.now()/300)%2===0) ? '#ff2222' : '#D9541E';
    ctx.fillStyle = fill;
    ctx.fillRect(fx + i*(segW+segGap), fy, segW, segH);
    ctx.strokeStyle = '#4FC3C318'; ctx.lineWidth = 0.5;
    ctx.strokeRect(fx + i*(segW+segGap), fy, segW, segH);
  }
  ctx.fillStyle = fuelPct < 0.25 ? '#D9541E' : HUD_COLOR;
  ctx.font = HUD_FONT_SM;
  ctx.fillText(ship.fuel.toFixed(1) + ' GAL  \u00b7  ' + ship.mpg + ' MPG', fx, fy + segH + 14);
  if (ship.fuel <= 0) {
    ctx.fillStyle = '#ff4444';
    ctx.fillText('\u2715 FUEL EMPTY \u2014 COASTING', fx, fy + segH + 27);
  } else if (fuelPct < 0.2 && Math.floor(Date.now()/500)%2===0) {
    ctx.fillStyle = '#D9541E';
    ctx.fillText('\u26a0 LOW FUEL', fx, fy + segH + 27);
  }

  // CARGO
  ctx.font = HUD_FONT_SM; ctx.fillStyle = HUD_DIM;
  ctx.fillText('CARGO', LEFT, oreY);
  ctx.fillStyle = ship.ore > 0 ? '#FFD700' : '#FFD70040';
  ctx.fillText(ship.ore + ' NEBULITE', LEFT + 56, oreY);

  ctx.font = 'bold 12px monospace';
  ctx.fillStyle = ship.mineral > 0 ? '#a78bfa' : '#a78bfa40';
  ctx.fillText('\u2666', LEFT + 14, minY);
  ctx.font = HUD_FONT_SM;
  ctx.fillStyle = ship.mineral > 0 ? '#c4b5fd' : '#c4b5fd50';
  ctx.fillText(ship.mineral + ' MINERAL', LEFT + 30, minY);

  ctx.font = 'bold 12px monospace';
  ctx.fillStyle = ship.armalcolite > 0 ? '#34d399' : '#34d39940';
  ctx.fillText('\u25c8', LEFT + 14, armY);
  ctx.font = HUD_FONT_SM;
  ctx.fillStyle = ship.armalcolite > 0 ? '#6ee7b7' : '#6ee7b750';
  ctx.fillText(ship.armalcolite + ' ARMALCOLITE', LEFT + 30, armY);

  // PILOTS ONLINE
  if (typeof multiMode !== 'undefined' && multiMode) {
    ctx.font = 'bold 12px monospace'; ctx.fillStyle = '#38bdf8';
    ctx.fillText('\u25a0', LEFT + 14, pilotY);
    ctx.font = HUD_FONT_SM; ctx.fillStyle = '#38bdf8';
    ctx.fillText((Object.keys(remotePlayers).length + 1) + ' PILOTS ONLINE', LEFT + 30, pilotY);
  }

  // ACTION HINTS
  const canCraft = ship.armalcolite > 0;
  ctx.font = HUD_FONT_SM;
  ctx.fillStyle = canCraft ? '#FFD700' : '#3a3010';
  ctx.fillText('[C] REFINE', LEFT, hintY);
  ctx.fillStyle = canCraft ? HUD_COLOR : '#2a3040';
  ctx.fillText(ORE_PER_FUEL + ' ORE \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', LEFT + 84, hintY);

  ctx.fillStyle = mineTarget ? '#4FC3C3' : '#2a3a4a';
  ctx.fillText('[E] MINE', LEFT, hintY + LH);
  if (mineTarget) {
    ctx.fillStyle = '#4FC3C380';
    ctx.fillText(Math.round(mineDist) + 'px', LEFT + 72, hintY + LH);
  }

  // MINI COMPASS
  const cx2 = canvas.width - 52, cy2 = 124, r = 26;
  ctx.strokeStyle = '#1a2a3a'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(cx2, cy2, r, 0, Math.PI*2); ctx.stroke();
  const dirIdx = DIRS.indexOf(ship.dir);
  if (dirIdx >= 0) {
    const a = DIR_ANGLES_DEG[dirIdx] * (Math.PI / 180);
    ctx.strokeStyle = '#4FC3C3'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx2, cy2);
    ctx.lineTo(cx2 + Math.cos(a)*(r-4), cy2 + Math.sin(a)*(r-4)); ctx.stroke();
    ctx.fillStyle = '#4FC3C3';
    ctx.beginPath(); ctx.arc(cx2+Math.cos(a)*(r-4), cy2+Math.sin(a)*(r-4), 3, 0, Math.PI*2); ctx.fill();
  }
  ctx.fillStyle = '#1a2a3a88';
  ctx.beginPath(); ctx.arc(cx2, cy2, 3, 0, Math.PI*2); ctx.fill();

  // MAP FLASH
  if (bgFlash && bgFlash.timer > 0) {
    const alpha = Math.min(1, bgFlash.timer / 30);
    ctx.globalAlpha = alpha; ctx.fillStyle = '#4FC3C3';
    ctx.font = HUD_FONT; ctx.textAlign = 'center';
    ctx.fillText('MAP: ' + bgFlash.name.replace('_',' ').toUpperCase(), canvas.width/2, canvas.height - 30);
    ctx.textAlign = 'left'; ctx.globalAlpha = 1;
    bgFlash.timer--;
  }
}

"""

new_lines = lines[:hud_start] + [NEW_HUD] + lines[debug_start:]
open(src, 'w', encoding='utf-8').write(''.join(new_lines))
new_size = os.path.getsize(src)
print(f'Done. New size: {new_size} bytes. Lines replaced: {debug_start - hud_start}')
