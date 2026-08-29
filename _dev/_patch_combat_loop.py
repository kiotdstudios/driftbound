raw = open('driftbound_flight_test.html','rb').read()
d   = raw.decode('utf-8','replace')
ok  = []

# ══════════════════════════════════════════════════════════════════════
# PATCH 1 — Pod secured state + Armory weapon reward globals
# ══════════════════════════════════════════════════════════════════════
ANCHOR_GLOBALS = 'let interiorMode   = false;'
INSERT_GLOBALS  = '''\
// ── COMBAT & POD STATE ────────────────────────────────────────────────
// Pod secured state: 0=unknown, 1=hostile(drone inside), 2=secured
// For MVP the first attached pod starts as hostile until cleared
const POD_STATE_HOSTILE  = 1;
const POD_STATE_SECURED  = 2;
let   podSecured = false;   // true once drone is defeated

// ── DRONE (interior enemy) ────────────────────────────────────────────
let drone = null;   // null = not spawned
const DRONE_HP_MAX   = 40;
const DRONE_SPEED    = 0.045;
const DRONE_ATTACK_R = 0.9;     // tile distance to deal damage
const DRONE_DMG      = 8;       // damage per hit to player
const DRONE_FIRE_CD  = 90;      // frames between attacks
let   droneFireTimer = 0;
let   droneAlertFlash= 0;

// ── PLAYER COMBAT STATS ───────────────────────────────────────────────
let playerHP     = 100;
const PLAYER_HP_MAX = 100;
let   playerInvTimer = 0;   // invincibility frames after hit
const PLAYER_INV_DUR = 40;

// ── WEAPON (Armory reward) ────────────────────────────────────────────
// weapon = null (no weapon), or { type:'pulse_rifle', ammo:24, maxAmmo:24 }
let weapon = null;
const WEAPON_PICKUP_POS = {col:4, row:3};  // centre of room, near weapon rack
let   weaponPickedUp = false;
let   weaponGlow = 0;   // sine glow counter for pickup sprite

// ── PROJECTILES ───────────────────────────────────────────────────────
const projectiles = [];   // { x, y, vx, vy, owner:'player'|'drone', life }

// ── SHOOT COOLDOWN ────────────────────────────────────────────────────
let shootCooldown = 0;
const SHOOT_CD    = 18;   // frames between shots
const PROJ_SPEED  = 0.22;
const PROJ_LIFE   = 60;

let interiorMode   = false;'''

if ANCHOR_GLOBALS in d:
    d = d.replace(ANCHOR_GLOBALS, INSERT_GLOBALS, 1)
    ok.append('globals')
else:
    print('ERR globals anchor missing')

# ══════════════════════════════════════════════════════════════════════
# PATCH 2 — Replace drawInterior() with full combat-aware version
# ══════════════════════════════════════════════════════════════════════
# Find start/end of existing drawInterior
import re
m_start = re.search(r'// ── INTERIOR RENDERER ─+\nfunction drawInterior\(\) \{', d)
m_end   = re.search(r'\nfunction updateInteriorPlayer\(\)', d)

if m_start and m_end:
    old_draw = d[m_start.start():m_end.start()]
    new_draw = r'''// ── INTERIOR RENDERER ───────────────────────────────────────
function drawInterior() {
  const cols = ARMORY_MAP[0].length;
  const rows = ARMORY_MAP.length;
  const mapW  = cols * TILE;
  const mapH  = rows * TILE;
  const offX  = (canvas.width  - mapW) / 2;
  const offY  = (canvas.height - mapH) / 2;

  // background
  ctx.fillStyle = '#0a0e14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // ── TILES ─────────────────────────────────────────────────────
  const t_now = performance.now() / 1000;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const tx = offX + c * TILE, ty = offY + r * TILE;
      const t  = ARMORY_MAP[r][c];
      if (t === 0) continue;

      if (t === 1) {
        ctx.fillStyle = '#1a2230';
        ctx.fillRect(tx, ty, TILE, TILE);
        ctx.strokeStyle = '#2a3545'; ctx.lineWidth = 1;
        ctx.strokeRect(tx+1, ty+1, TILE-2, TILE-2);
      } else if (t === 2) {
        ctx.fillStyle = '#2c3a4a'; ctx.fillRect(tx, ty, TILE, TILE);
        ctx.fillStyle = '#3d4f63'; ctx.fillRect(tx+4, ty+4, TILE-8, TILE-8);
        ctx.fillStyle = '#1a2230'; ctx.fillRect(tx+8, ty+8, TILE-16, TILE-16);
      } else if (t === 3) {
        // door
        ctx.fillStyle = podSecured ? '#0d3340' : '#1a0d0d';
        ctx.fillRect(tx, ty, TILE, TILE);
        ctx.fillStyle = podSecured ? '#1a6070' : '#401010';
        ctx.fillRect(tx+6, ty+6, TILE-12, TILE-12);
        if (podSecured) {
          ctx.fillStyle = '#4FC3C3';
          ctx.fillRect(tx+10, ty+10, (TILE-20)/2-2, TILE-20);
          ctx.fillRect(tx+10+(TILE-20)/2+2, ty+10, (TILE-20)/2-2, TILE-20);
        } else {
          // locked — red X
          ctx.strokeStyle = '#ff3333'; ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(tx+14,ty+14); ctx.lineTo(tx+TILE-14,ty+TILE-14);
          ctx.moveTo(tx+TILE-14,ty+14); ctx.lineTo(tx+14,ty+TILE-14);
          ctx.stroke();
        }
        ctx.font = 'bold 9px Courier New'; ctx.textAlign = 'center';
        ctx.fillStyle = podSecured ? '#4FC3C3' : '#ff3333';
        ctx.fillText(podSecured ? 'EXIT' : 'LOCKED', tx+TILE/2, ty+TILE-8);
        ctx.textAlign = 'left';
      } else if (t === 4) {
        // crate
        ctx.fillStyle = '#3a2800'; ctx.fillRect(tx+8, ty+8, TILE-16, TILE-16);
        ctx.fillStyle = '#c47a1e'; ctx.fillRect(tx+10, ty+10, TILE-20, TILE-20);
        ctx.strokeStyle = '#8a5010'; ctx.lineWidth = 2;
        ctx.strokeRect(tx+10, ty+10, TILE-20, TILE-20);
        ctx.beginPath();
        ctx.moveTo(tx+10,ty+10); ctx.lineTo(tx+TILE-10,ty+TILE-10);
        ctx.moveTo(tx+TILE-10,ty+10); ctx.lineTo(tx+10,ty+TILE-10);
        ctx.stroke();
      } else if (t === 5) {
        // weapon rack
        ctx.fillStyle = '#1a1a2e'; ctx.fillRect(tx+6, ty+6, TILE-12, TILE-12);
        ctx.strokeStyle = '#D9541E'; ctx.lineWidth = 1.5;
        ctx.strokeRect(tx+8, ty+8, TILE-16, TILE-16);
        ctx.strokeStyle = '#ff7744'; ctx.lineWidth = 3;
        for (let i = 0; i < 3; i++) {
          const wy = ty + 16 + i*14;
          ctx.beginPath(); ctx.moveTo(tx+14, wy); ctx.lineTo(tx+TILE-14, wy); ctx.stroke();
        }
        ctx.font = 'bold 8px Courier New'; ctx.fillStyle = '#D9541E'; ctx.textAlign = 'center';
        ctx.fillText('ARMORY', tx+TILE/2, ty+TILE-8); ctx.textAlign = 'left';
      }
    }
  }

  // ── WEAPON PICKUP (if not yet collected) ──────────────────────
  if (!weaponPickedUp) {
    weaponGlow += 0.06;
    const wpx = offX + (WEAPON_PICKUP_POS.col + 0.5) * TILE;
    const wpy = offY + (WEAPON_PICKUP_POS.row + 0.5) * TILE;
    const gAlpha = 0.5 + 0.5 * Math.sin(weaponGlow);
    ctx.shadowColor = '#38bdf8'; ctx.shadowBlur = 12 + 8*gAlpha;
    ctx.fillStyle   = `rgba(56,189,248,${0.7+0.3*gAlpha})`;
    // draw a small rifle silhouette
    ctx.save();
    ctx.translate(wpx, wpy);
    ctx.rotate(-Math.PI/6);
    ctx.fillRect(-18, -4, 36, 8);
    ctx.fillRect(-4, -8, 8, 6);   // grip
    ctx.fillRect(12, -3, 8, 4);   // barrel extension
    ctx.restore();
    ctx.shadowBlur = 0;
    // label
    ctx.font = 'bold 9px Courier New'; ctx.fillStyle = '#38bdf8';
    ctx.textAlign = 'center';
    ctx.fillText('PULSE RIFLE', wpx, wpy + 28);
    ctx.fillText('[E] PICK UP', wpx, wpy + 40);
    ctx.textAlign = 'left';
  }

  // ── DRONE ─────────────────────────────────────────────────────
  if (drone && drone.hp > 0) {
    droneAlertFlash = Math.max(0, droneAlertFlash - 1);
    const dx = offX + drone.x * TILE, dy = offY + drone.y * TILE;
    const flash = droneAlertFlash > 0 && droneAlertFlash % 6 < 3;
    ctx.shadowColor = flash ? '#ff4444' : '#ff6600';
    ctx.shadowBlur  = flash ? 24 : 14;
    // body — hexagon
    ctx.fillStyle = flash ? '#ff3333' : '#cc3300';
    ctx.beginPath();
    for (let a = 0; a < 6; a++) {
      const angle = (Math.PI/3)*a - Math.PI/6;
      const r = 14;
      a===0 ? ctx.moveTo(dx+r*Math.cos(angle), dy+r*Math.sin(angle))
            : ctx.lineTo(dx+r*Math.cos(angle), dy+r*Math.sin(angle));
    }
    ctx.closePath(); ctx.fill();
    // eye
    ctx.fillStyle = '#ffff44'; ctx.shadowBlur = 8;
    ctx.beginPath(); ctx.arc(dx, dy, 5, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;
    // HP bar
    const hpBarW = 40, hpBarH = 5;
    ctx.fillStyle = '#300'; ctx.fillRect(dx - hpBarW/2, dy - 22, hpBarW, hpBarH);
    ctx.fillStyle = drone.hp/DRONE_HP_MAX > 0.5 ? '#ff6600' : '#ff2200';
    ctx.fillRect(dx - hpBarW/2, dy - 22, hpBarW * (drone.hp/DRONE_HP_MAX), hpBarH);
    ctx.strokeStyle = '#ff6600'; ctx.lineWidth = 1;
    ctx.strokeRect(dx - hpBarW/2, dy - 22, hpBarW, hpBarH);
  }

  // ── PROJECTILES ───────────────────────────────────────────────
  for (const p of projectiles) {
    const px2 = offX + p.x * TILE, py2 = offY + p.y * TILE;
    ctx.shadowColor = p.owner==='player' ? '#38bdf8' : '#ff4400';
    ctx.shadowBlur  = 8;
    ctx.fillStyle   = p.owner==='player' ? '#7de8ff' : '#ff6633';
    ctx.beginPath(); ctx.arc(px2, py2, 4, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;
  }

  // ── PLAYER ────────────────────────────────────────────────────
  const px = offX + iPlayerX * TILE, py = offY + iPlayerY * TILE;
  const invFlash = playerInvTimer > 0 && Math.floor(playerInvTimer/4) % 2 === 0;
  if (!invFlash) {
    ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 12;
    ctx.fillStyle = '#4FC3C3';
    ctx.beginPath(); ctx.arc(px, py, 12, 0, Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#0a1520';
    ctx.beginPath(); ctx.arc(px, py, 6, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#4FC3C3';
    ctx.beginPath(); ctx.arc(px, py, 3, 0, Math.PI*2); ctx.fill();
  }

  // ── HUD STRIP ─────────────────────────────────────────────────
  ctx.fillStyle = '#000000cc';
  ctx.fillRect(0, 0, canvas.width, 34);
  ctx.strokeStyle = '#4FC3C388'; ctx.lineWidth = 1;
  ctx.strokeRect(0, 0, canvas.width, 34);
  ctx.font = 'bold 13px Courier New'; ctx.fillStyle = '#4FC3C3';
  ctx.fillText(podSecured ? 'ARMORY POD' : 'ARMORY POD  ⚠ HOSTILE', 18, 22);

  // player HP bar
  const hpW = 120;
  ctx.fillStyle = '#300'; ctx.fillRect(canvas.width - hpW - 18, 8, hpW, 16);
  ctx.fillStyle = playerHP/PLAYER_HP_MAX > 0.5 ? '#22cc55' : playerHP/PLAYER_HP_MAX > 0.25 ? '#ffaa00' : '#ff2222';
  ctx.fillRect(canvas.width - hpW - 18, 8, hpW * (playerHP/PLAYER_HP_MAX), 16);
  ctx.strokeStyle = '#4FC3C388'; ctx.lineWidth = 1;
  ctx.strokeRect(canvas.width - hpW - 18, 8, hpW, 16);
  ctx.fillStyle = '#fff'; ctx.font = 'bold 10px Courier New';
  ctx.textAlign = 'center';
  ctx.fillText('HP ' + playerHP + '/' + PLAYER_HP_MAX, canvas.width - hpW/2 - 18, 21);
  ctx.textAlign = 'left';

  // weapon status (bottom left)
  if (weapon) {
    ctx.fillStyle = '#000000aa'; ctx.fillRect(12, canvas.height-40, 180, 28);
    ctx.strokeStyle = '#38bdf8aa'; ctx.strokeRect(12, canvas.height-40, 180, 28);
    ctx.fillStyle = '#38bdf8'; ctx.font = 'bold 11px Courier New';
    ctx.fillText('PULSE RIFLE  ' + weapon.ammo + '/' + weapon.maxAmmo, 22, canvas.height-22);
  }

  // controls hint
  ctx.fillStyle = '#4a6070'; ctx.font = '10px Courier New';
  ctx.fillText('WASD=MOVE  CLICK=SHOOT', canvas.width/2 - 80, canvas.height - 14);

  // proximity prompts
  if (podSecured) {
    const distDoor = Math.hypot(iPlayerX - DOOR_COL - 0.5, iPlayerY - DOOR_ROW - 0.5);
    if (distDoor < 1.5) {
      ctx.font = 'bold 13px Courier New'; ctx.fillStyle = '#4FC3C3';
      ctx.textAlign = 'center';
      ctx.fillText('[E]  EXIT TO SPACE', canvas.width/2, canvas.height - 60);
      ctx.textAlign = 'left';
    }
  }

  // weapon pickup prompt
  if (!weaponPickedUp) {
    const distWep = Math.hypot(iPlayerX - WEAPON_PICKUP_POS.col - 0.5, iPlayerY - WEAPON_PICKUP_POS.row - 0.5);
    if (distWep < 1.2) {
      ctx.font = 'bold 13px Courier New'; ctx.fillStyle = '#38bdf8';
      ctx.textAlign = 'center';
      ctx.fillText('[E]  PICK UP PULSE RIFLE', canvas.width/2, canvas.height - 60);
      ctx.textAlign = 'left';
    }
  }

  // secured banner (brief flash)
  if (podSecured && drone && drone.hp <= 0 && !drone._bannerDone) {
    drone._bannerDone = true;
  }
}

'''
    d = d.replace(old_draw, new_draw, 1)
    ok.append('drawInterior replaced')
else:
    print('ERR drawInterior not found', bool(m_start), bool(m_end))

# ══════════════════════════════════════════════════════════════════════
# PATCH 3 — Replace updateInteriorPlayer with combat-aware version
# ══════════════════════════════════════════════════════════════════════
m_uip_start = re.search(r'function updateInteriorPlayer\(\) \{', d)
m_uip_end   = re.search(r'\n// ── INTERIOR FADE', d)
if m_uip_start and m_uip_end:
    old_uip = d[m_uip_start.start():m_uip_end.start()]
    new_uip = r'''function updateInteriorPlayer() {
  if (!interiorMode) return;
  const cols = ARMORY_MAP[0].length, rows = ARMORY_MAP.length;

  // Movement
  let nx = iPlayerX, ny = iPlayerY;
  if (keys['ArrowUp']    || keys['KeyW']) ny -= I_SPEED;
  if (keys['ArrowDown']  || keys['KeyS']) ny += I_SPEED;
  if (keys['ArrowLeft']  || keys['KeyA']) nx -= I_SPEED;
  if (keys['ArrowRight'] || keys['KeyD']) nx += I_SPEED;
  const margin = 0.35;
  const walkable = t => t===1 || t===3 || t===4 || t===5;
  const tileAt = (x,y) => {
    const tc=Math.floor(x), tr=Math.floor(y);
    if (tr<0||tr>=rows||tc<0||tc>=cols) return 2;
    return ARMORY_MAP[tr][tc];
  };
  if (walkable(tileAt(nx+margin,iPlayerY)) && walkable(tileAt(nx-margin,iPlayerY))) iPlayerX=nx;
  if (walkable(tileAt(iPlayerX,ny+margin)) && walkable(tileAt(iPlayerX,ny-margin))) iPlayerY=ny;

  // Invincibility countdown
  if (playerInvTimer > 0) playerInvTimer--;

  // ── SPAWN DRONE on entry if pod not yet secured ──
  if (!podSecured && !drone) {
    drone = { x: 4.5, y: 1.5, hp: DRONE_HP_MAX, vx: 0, vy: 0, _bannerDone: false };
  }

  // ── DRONE AI ──
  if (drone && drone.hp > 0) {
    // chase player
    const ddx = iPlayerX - drone.x, ddy = iPlayerY - drone.y;
    const dist = Math.hypot(ddx, ddy);
    if (dist > 0.01) {
      drone.x += (ddx/dist) * DRONE_SPEED;
      drone.y += (ddy/dist) * DRONE_SPEED;
    }
    // melee attack
    droneFireTimer = Math.max(0, droneFireTimer - 1);
    if (dist < DRONE_ATTACK_R && droneFireTimer === 0) {
      droneFireTimer = DRONE_FIRE_CD;
      if (playerInvTimer === 0) {
        playerHP = Math.max(0, playerHP - DRONE_DMG);
        playerInvTimer = PLAYER_INV_DUR;
        droneAlertFlash = 20;
        if (playerHP <= 0) {
          // player KO — respawn at door with half HP
          iPlayerX = 4.5; iPlayerY = 6.5;
          playerHP = Math.floor(PLAYER_HP_MAX * 0.5);
        }
      }
    }
    // drone wall collision (keep in walkable area)
    const dt = tileAt(drone.x, drone.y);
    if (!walkable(dt)) {
      drone.x = 4.5; drone.y = 1.5;
    }
  }

  // ── PROJECTILES ──
  shootCooldown = Math.max(0, shootCooldown - 1);
  for (let i = projectiles.length - 1; i >= 0; i--) {
    const p = projectiles[i];
    p.x += p.vx; p.y += p.vy; p.life--;
    // wall hit
    if (!walkable(tileAt(p.x, p.y)) || p.life <= 0) {
      projectiles.splice(i, 1); continue;
    }
    // player projectile hits drone
    if (p.owner === 'player' && drone && drone.hp > 0) {
      const hit = Math.hypot(p.x - drone.x, p.y - drone.y) < 0.5;
      if (hit) {
        drone.hp -= 12;
        droneAlertFlash = 12;
        projectiles.splice(i, 1);
        if (drone.hp <= 0) {
          // DRONE DEFEATED
          podSecured = true;
        }
        continue;
      }
    }
  }

  // ── [E] interactions ──
  // weapon pickup
  if (!weaponPickedUp) {
    const distWep = Math.hypot(iPlayerX - WEAPON_PICKUP_POS.col - 0.5, iPlayerY - WEAPON_PICKUP_POS.row - 0.5);
    if (distWep < 1.2 && _ePressed) {
      weapon = { type: 'pulse_rifle', ammo: 24, maxAmmo: 24 };
      weaponPickedUp = true;
      showToast('⚡ PULSE RIFLE acquired  24/24');
      _ePressed = false;
    }
  }

  // door exit (only if secured)
  const onDoor = Math.floor(iPlayerX)===DOOR_COL && Math.floor(iPlayerY)===DOOR_ROW;
  if (onDoor && podSecured && _ePressed) {
    interiorFadeDir = -1; _ePressed = false;
  }
}

'''
    d = d.replace(old_uip, new_uip, 1)
    ok.append('updateInteriorPlayer replaced')
else:
    print('ERR updateInteriorPlayer bounds:', bool(m_uip_start), bool(m_uip_end))

# ══════════════════════════════════════════════════════════════════════
# PATCH 4 — Mouse click to shoot (inject into canvas mousedown handler)
# ══════════════════════════════════════════════════════════════════════
# Find existing mouse handler or inject a new one near the keydown block
MOUSECLICK_ANCHOR = "canvas.addEventListener('mousedown'"
if MOUSECLICK_ANCHOR in d:
    # find it and inject interior shoot into existing handler
    idx = d.find(MOUSECLICK_ANCHOR)
    # find the first { after it and inject at start of function body
    brace_idx = d.find('{', idx)
    insert_shoot = '''
    // Interior shooting
    if (interiorMode && weapon && weapon.ammo > 0 && shootCooldown === 0) {
      // convert canvas click to tile coords
      const rect2  = canvas.getBoundingClientRect();
      const scaleX = canvas.width  / rect2.width;
      const scaleY = canvas.height / rect2.height;
      const _cx2   = canvas.width/2, _cy2 = canvas.height/2;
      const mapW2  = ARMORY_MAP[0].length * TILE;
      const mapH2  = ARMORY_MAP.length    * TILE;
      const offX2  = (_cx2*2 - mapW2) / 2;
      const offY2  = (_cy2*2 - mapH2) / 2;
      const mx2 = ((e.clientX - rect2.left) * scaleX - offX2) / TILE;
      const my2 = ((e.clientY - rect2.top)  * scaleY - offY2) / TILE;
      const dx2 = mx2 - iPlayerX, dy2 = my2 - iPlayerY;
      const dist2 = Math.hypot(dx2, dy2);
      if (dist2 > 0.01) {
        projectiles.push({ x: iPlayerX, y: iPlayerY,
          vx: (dx2/dist2)*PROJ_SPEED, vy: (dy2/dist2)*PROJ_SPEED,
          owner: 'player', life: PROJ_LIFE });
        weapon.ammo--;
        shootCooldown = SHOOT_CD;
      }
      return;
    }
'''
    d = d[:brace_idx+1] + insert_shoot + d[brace_idx+1:]
    ok.append('mouse shoot injected')
else:
    # inject a fresh mousedown listener before </script>
    SCRIPT_END = '</script>'
    idx_se = d.rfind(SCRIPT_END)
    NEW_MOUSE = '''
canvas.addEventListener('mousedown', function(e) {
  if (interiorMode && weapon && weapon.ammo > 0 && shootCooldown === 0) {
    const rect2  = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect2.width;
    const scaleY = canvas.height / rect2.height;
    const offX2  = (canvas.width  - ARMORY_MAP[0].length * TILE) / 2;
    const offY2  = (canvas.height - ARMORY_MAP.length    * TILE) / 2;
    const mx2 = ((e.clientX - rect2.left) * scaleX - offX2) / TILE;
    const my2 = ((e.clientY - rect2.top)  * scaleY - offY2) / TILE;
    const dx2 = mx2 - iPlayerX, dy2 = my2 - iPlayerY;
    const dist2 = Math.hypot(dx2, dy2);
    if (dist2 > 0.01) {
      projectiles.push({ x: iPlayerX, y: iPlayerY,
        vx: (dx2/dist2)*PROJ_SPEED, vy: (dy2/dist2)*PROJ_SPEED,
        owner: 'player', life: PROJ_LIFE });
      weapon.ammo--;
      shootCooldown = SHOOT_CD;
    }
  }
});
'''
    d = d[:idx_se] + NEW_MOUSE + '\n' + d[idx_se:]
    ok.append('mouse shoot listener added (new)')

print('Patches applied:', ok)

import re as _re
depth = 0
for ch in _re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
print('Done.')
