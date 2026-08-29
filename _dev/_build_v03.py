with open('driftbound_flight_test.html','rb') as f:
    src = f.read().decode('utf-8')

# Normalize to LF for easy replacements
src = src.replace('\r\n', '\n')

# ── 1. Lock BG to toxic_01 (index 10) ────────────────────────────────────────
src = src.replace(
    "let currentBgIdx = 7;   // vapor_03 as default \u2014 purple/teal nebula",
    "let currentBgIdx = 10;  // toxic_01 \u2014 pink void, locked as main space BG"
)

# ── 2. Fix boost ramp constants ──────────────────────────────────────────────
src = src.replace(
    "const BOOST_RAMP_UP   = 0.08; // ramp to full boost: ~12 frames\nconst BOOST_RAMP_DOWN = 0.05; // ramp back to cruise: ~20 frames",
    "const BOOST_RAMP_UP   = 0.045; // ramp to full boost: ~22 frames\nconst BOOST_RAMP_DOWN = 0.012; // ramp back to cruise: ~83 frames \u2014 gradual coast"
)

# ── 3. Ship health constants after SPEED_THRESH ──────────────────────────────
src = src.replace(
    "const SPEED_THRESH = 0.12;",
    """const SPEED_THRESH = 0.12;

// \u2500\u2500\u2500 HEALTH / COLLISION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\nconst SHIP_MAX_HP      = 100;
const COLLISION_BOUNCE = 0.45;
const COLLISION_DAMAGE = 8;
const COLLISION_IFRAMES= 60;
const COLLISION_RADIUS = 28;"""
)

# ── 4. Add hp/iframes/hitFlash to ship state ─────────────────────────────────
src = src.replace(
    "  mineCooldown: 0, // frames until next mine hit\n  laserWx: null, laserWy: null, laserTimer: 0, // visual laser",
    """  mineCooldown: 0, // frames until next mine hit
  laserWx: null, laserWy: null, laserTimer: 0, // visual laser
  hp:       100,   // hull integrity
  iframes:  0,     // invincibility frames after collision
  hitFlash: 0,     // red screen flash"""
)

# ── 5. Add rotation + drift to spawnAsteroid ─────────────────────────────────
src = src.replace(
    """  asteroids.push({
    type,
    worldX:     ox + Math.cos(angle) * dist,
    worldY:     oy + Math.sin(angle) * dist,
    hp:         type.hp,
    maxHp:      type.hp,
    flashTimer: 0,
  });""",
    """  asteroids.push({
    type,
    worldX:     ox + Math.cos(angle) * dist,
    worldY:     oy + Math.sin(angle) * dist,
    hp:         type.hp,
    maxHp:      type.hp,
    flashTimer: 0,
    angle:      Math.random() * Math.PI * 2,
    rotSpeed:   (Math.random() - 0.5) * 0.008,
    driftVx:    (Math.random() - 0.5) * 0.18,
    driftVy:    (Math.random() - 0.5) * 0.18,
  });"""
)

# ── 6. Tick rotation + drift ─────────────────────────────────────────────────
src = src.replace(
    "  // Tick flash timers\n  for (const ast of asteroids) {\n    if (ast.flashTimer > 0) ast.flashTimer--;\n  }",
    """  // Tick flash timers, rotation, drift
  for (const ast of asteroids) {
    if (ast.flashTimer > 0) ast.flashTimer--;
    ast.angle  = (ast.angle  || 0) + (ast.rotSpeed || 0);
    ast.worldX += ast.driftVx || 0;
    ast.worldY += ast.driftVy || 0;
  }"""
)

# ── 7. Draw asteroids with rotation ──────────────────────────────────────────
src = src.replace(
    "    if (img) ctx.drawImage(img, sx - sw/2, sy - sh/2, sw, sh);",
    """    if (img) {
      const rot = ast.angle || 0;
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(rot);
      ctx.drawImage(img, -sw/2, -sh/2, sw, sh);
      ctx.restore();
    }"""
)

# ── 8. Collision detection — insert after speed cap check ────────────────────
collision_code = """
  // \u2500\u2500\u2500 COLLISION DETECTION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n  if (ship.iframes > 0) {
    ship.iframes--;
  } else {
    for (const ast of asteroids) {
      const dx   = ast.worldX - ship.worldX;
      const dy   = ast.worldY - ship.worldY;
      const astR = Math.max(ast.type.w, ast.type.h) * AST_SCALE * 0.38;
      const minD = COLLISION_RADIUS + astR;
      const dist = Math.hypot(dx, dy);
      if (dist < minD && dist > 0.001) {
        const nx = dx / dist, ny = dy / dist;
        const dot = ship.vx * nx + ship.vy * ny;
        ship.vx -= (1 + COLLISION_BOUNCE) * dot * nx;
        ship.vy -= (1 + COLLISION_BOUNCE) * dot * ny;
        ship.worldX -= nx * (minD - dist) * 0.6;
        ship.worldY -= ny * (minD - dist) * 0.6;
        ship.hp      = Math.max(0, ship.hp - COLLISION_DAMAGE);
        ship.iframes = COLLISION_IFRAMES;
        ship.hitFlash = 18;
        showToast('HULL DAMAGE  \u2502  ' + ship.hp + ' / ' + SHIP_MAX_HP);
        break;
      }
    }
  }
  if (ship.hitFlash > 0) ship.hitFlash--;
"""
src = src.replace(
    "  if (spd < 0.01) { ship.vx = 0; ship.vy = 0; }",
    "  if (spd < 0.01) { ship.vx = 0; ship.vy = 0; }" + collision_code
)

# ── 9. Hull bar in HUD — insert after thrust bar label line ──────────────────
health_hud = """
  // \u2500\u2500\u2500 HULL INTEGRITY \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  const hbx = LEFT, hby = TOP + 72;
  const hbw = 160,  hbh = 4;
  const hpPct = ship.hp / SHIP_MAX_HP;
  ctx.fillStyle = '#0d1520';
  ctx.fillRect(hbx - 1, hby - 1, hbw + 2, hbh + 2);
  const hGrad = ctx.createLinearGradient(hbx, 0, hbx + hbw, 0);
  if (hpPct > 0.5)       { hGrad.addColorStop(0,'#22bb55'); hGrad.addColorStop(1,'#44ff88'); }
  else if (hpPct > 0.25) { hGrad.addColorStop(0,'#aa6600'); hGrad.addColorStop(1,'#ffcc00'); }
  else                   { hGrad.addColorStop(0,'#880000'); hGrad.addColorStop(1,'#ff2222'); }
  ctx.fillStyle = hGrad;
  ctx.fillRect(hbx, hby, hbw * hpPct, hbh);
  ctx.strokeStyle = '#ffffff18';
  ctx.lineWidth = 1;
  ctx.strokeRect(hbx, hby, hbw, hbh);
  ctx.font = HUD_FONT;
  ctx.fillStyle = HUD_DIM;
  ctx.fillText('HULL', hbx, hby - 4);
  ctx.fillStyle = hpPct < 0.25 ? '#ff4444' : HUD_COLOR;
  ctx.fillText(ship.hp + ' / ' + SHIP_MAX_HP, hbx + 120, hby - 4);
  if (ship.hp <= 0 && Math.floor(Date.now()/400)%2===0) {
    ctx.fillStyle = '#ff2222';
    ctx.font = 'bold 13px Courier New';
    ctx.textAlign = 'center';
    ctx.fillText('\u2715 HULL BREACH \u2014 CRITICAL', canvas.width/2, canvas.height/2 - 20);
    ctx.textAlign = 'left';
  }
"""
src = src.replace(
    "  ctx.font = HUD_FONT;\n  ctx.fillStyle = HUD_DIM;\n  ctx.fillText('THRUST', bx, by - 5);",
    "  ctx.font = HUD_FONT;\n  ctx.fillStyle = HUD_DIM;\n  ctx.fillText('THRUST', bx, by - 5);\n" + health_hud
)

# ── 10. Expand HUD panel height ───────────────────────────────────────────────
src = src.replace(
    "  ctx.fillRect(12, 12, 200, 230);\n  ctx.strokeStyle = '#4FC3C344';\n  ctx.lineWidth = 1;\n  ctx.strokeRect(12, 12, 200, 230);",
    "  ctx.fillRect(12, 12, 200, 255);\n  ctx.strokeStyle = '#4FC3C344';\n  ctx.lineWidth = 1;\n  ctx.strokeRect(12, 12, 200, 255);"
)

# ── 11. Red hit flash overlay in loop ────────────────────────────────────────
src = src.replace(
    "  drawShip(cx, cy, now, speed);",
    """  // Hit flash
  if (ship.hitFlash > 0) {
    ctx.globalAlpha = (ship.hitFlash / 18) * 0.30;
    ctx.fillStyle = '#ff1010';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 1;
  }
  drawShip(cx, cy, now, speed);"""
)

# ── Write output ──────────────────────────────────────────────────────────────
with open('driftbound_flight_test_v03.html','w',encoding='utf-8') as f:
    f.write(src)

print('DONE:', len(src), 'chars')

checks = [
    ('BG toxic locked',    'currentBgIdx = 10'),
    ('Boost ramp fix',     'BOOST_RAMP_DOWN = 0.012'),
    ('Health constants',   'SHIP_MAX_HP      = 100'),
    ('Ship hp state',      'hp:       100'),
    ('Ast rotation spawn', 'rotSpeed:'),
    ('Ast drift spawn',    'driftVx:'),
    ('Rotation tick',      'ast.angle  = (ast.angle'),
    ('Drift tick',         'ast.worldX += ast.driftVx'),
    ('Rotate draw',        'ctx.rotate(rot)'),
    ('Collision detect',   'COLLISION DETECTION'),
    ('Hull bar HUD',       'HULL INTEGRITY'),
    ('Hit flash draw',     'Hit flash'),
]
all_ok = True
for label, tok in checks:
    found = tok in src
    status = 'OK' if found else 'MISSING'
    if not found: all_ok = False
    print(f'  [{status}] {label}')

if all_ok:
    print('\nALL CHECKS PASSED')
else:
    print('\nSOME CHECKS FAILED')
