import re
d = open('driftbound_flight_test.html','rb').read().decode('utf-8','replace')

# replace old updateInteriorPlayer by brace counting
fn_start = d.find('function updateInteriorPlayer()')
depth=0; i=fn_start
while i < len(d):
    if d[i]=='{': depth+=1
    elif d[i]=='}':
        depth-=1
        if depth==0:
            fn_end = i+1
            break
    i+=1

old_fn = d[fn_start:fn_end]
new_fn = r'''function updateInteriorPlayer() {
  if (!interiorMode) return;
  const cols = ARMORY_MAP[0].length, rows = ARMORY_MAP.length;

  // ── MOVEMENT ──
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

  // ── INVINCIBILITY TIMER ──
  if (playerInvTimer > 0) playerInvTimer--;

  // ── SPAWN DRONE if not yet secured ──
  if (!podSecured && !drone) {
    drone = { x: 4.5, y: 1.5, hp: DRONE_HP_MAX, vx: 0, vy: 0, _bannerDone: false };
  }

  // ── DRONE AI ──
  if (drone && drone.hp > 0) {
    const ddx = iPlayerX - drone.x, ddy = iPlayerY - drone.y;
    const dist = Math.hypot(ddx, ddy);
    if (dist > 0.01) {
      drone.x += (ddx/dist) * DRONE_SPEED;
      drone.y += (ddy/dist) * DRONE_SPEED;
    }
    // drone wall clamp
    if (!walkable(tileAt(drone.x, drone.y))) { drone.x=4.5; drone.y=1.5; }
    // melee attack
    droneFireTimer = Math.max(0, droneFireTimer-1);
    if (dist < DRONE_ATTACK_R && droneFireTimer===0) {
      droneFireTimer = DRONE_FIRE_CD;
      if (playerInvTimer===0) {
        playerHP = Math.max(0, playerHP - DRONE_DMG);
        playerInvTimer = PLAYER_INV_DUR;
        droneAlertFlash = 20;
        if (playerHP<=0) { iPlayerX=4.5; iPlayerY=6.5; playerHP=Math.floor(PLAYER_HP_MAX*0.5); }
      }
    }
  }

  // ── PROJECTILES ──
  shootCooldown = Math.max(0, shootCooldown-1);
  for (let i = projectiles.length-1; i>=0; i--) {
    const p = projectiles[i];
    p.x += p.vx; p.y += p.vy; p.life--;
    if (!walkable(tileAt(p.x, p.y)) || p.life<=0) { projectiles.splice(i,1); continue; }
    if (p.owner==='player' && drone && drone.hp>0) {
      if (Math.hypot(p.x - drone.x, p.y - drone.y) < 0.5) {
        drone.hp -= 12; droneAlertFlash=12; projectiles.splice(i,1);
        if (drone.hp<=0) { podSecured=true; showToast('✓ POD SECURED — dock to attach'); }
        continue;
      }
    }
  }

  // ── [E] INTERACTIONS ──
  // weapon pickup
  if (!weaponPickedUp) {
    const dw = Math.hypot(iPlayerX - WEAPON_PICKUP_POS.col - 0.5, iPlayerY - WEAPON_PICKUP_POS.row - 0.5);
    if (dw < 1.2 && _ePressed) {
      weapon = { type:'pulse_rifle', ammo:24, maxAmmo:24 };
      weaponPickedUp = true;
      showToast('⚡ PULSE RIFLE acquired  24/24');
      _ePressed = false;
    }
  }
  // door exit (secured only)
  const onDoor = Math.floor(iPlayerX)===DOOR_COL && Math.floor(iPlayerY)===DOOR_ROW;
  if (onDoor && podSecured && _ePressed) {
    interiorFadeDir = -1; _ePressed = false;
  }
}'''

d = d[:fn_start] + new_fn + d[fn_end:]
print('updateInteriorPlayer replaced')

# brace check
depth=0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch=='{': depth+=1
    elif ch=='}': depth-=1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
print('Done.')
