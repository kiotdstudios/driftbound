import base64, os

# --- encode tileset as base64 ---
ts_path = r'Ditharts_Free_Scifi_Tileset_v01\texture\upscaled\free_scifi_tileset_64x64.png'
with open(ts_path, 'rb') as f:
    ts_b64 = base64.b64encode(f.read()).decode()

raw = open('driftbound_flight_test.html', 'rb').read()
d = raw.decode('utf-8', 'replace')

# ── INJECT: interior state variables after existing globals ──
GLOBALS_ANCHOR = 'let _boosting  = false;'
GLOBALS_INSERT = '''let _boosting  = false;

// ── INTERIOR SYSTEM ──────────────────────────────────────────
let interiorMode   = false;   // true when player is inside a pod
let interiorPodIdx = -1;      // which attachedPods[] we're in
let interiorFade   = 0;       // 0=space, 1=interior (tweens 0↔1)
let interiorFadeDir= 0;       // +1 fading in, -1 fading out, 0 idle
const FADE_SPEED   = 0.04;

// player interior position (tile coords)
let iPlayerX = 4.5, iPlayerY = 5.5;  // center of room
const I_SPEED = 0.08;
const TILE    = 64;

// tileset image
const tilesetImg = new Image();
tilesetImg.src = 'data:image/png;base64,''' + ts_b64 + '''\';

// Interior room map for an Armory pod (9×9 tiles)
// Tile IDs (row*8 + col in tileset, 0-indexed):
//   WALL variants drawn procedurally — we use solid colour tiles for now
//   0  = void/nothing (skip draw)
//   1  = floor (dark metal panel — tile row4 col0 = id 32)
//   2  = wall  (solid — drawn as filled rect)
//   3  = door  (south wall centre — teal)
//   4  = crate prop (drawn as coloured box placeholder)
//   5  = weapon rack (drawn as coloured box placeholder)
const ARMORY_MAP = [
  [2,2,2,2,2,2,2,2,2],
  [2,1,1,1,1,1,1,1,2],
  [2,1,4,1,1,1,5,1,2],
  [2,1,4,1,1,1,5,1,2],
  [2,1,1,1,1,1,1,1,2],
  [2,1,1,1,1,1,1,1,2],
  [2,1,1,1,1,1,1,1,2],
  [2,1,1,1,1,1,1,1,2],
  [2,2,2,2,3,2,2,2,2],  // door at bottom centre (col 4)
];
const DOOR_ROW = 8, DOOR_COL = 4;  // exit door tile position
'''

if GLOBALS_ANCHOR in d:
    d = d.replace(GLOBALS_ANCHOR, GLOBALS_INSERT, 1)
    print('OK globals injected')
else:
    print('ANCHOR NOT FOUND:', repr(GLOBALS_ANCHOR))

# ── INJECT: drawInterior function before drawHUD ──
DRAW_HUD_ANCHOR = 'function drawHUD(speed) {'
DRAW_INTERIOR = '''// ── INTERIOR RENDERER ───────────────────────────────────────
function drawInterior() {
  const cols = ARMORY_MAP[0].length;
  const rows = ARMORY_MAP.length;
  const mapW  = cols * TILE;
  const mapH  = rows * TILE;
  const offX  = (canvas.width  - mapW) / 2;
  const offY  = (canvas.height - mapH) / 2;

  // background fill
  ctx.fillStyle = '#0a0e14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // draw tiles
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const tx = offX + c * TILE;
      const ty = offY + r * TILE;
      const t  = ARMORY_MAP[r][c];
      if (t === 0) continue;

      if (t === 1) {
        // floor — dark metal panel
        ctx.fillStyle = '#1a2230';
        ctx.fillRect(tx, ty, TILE, TILE);
        // subtle grid line
        ctx.strokeStyle = '#2a3545';
        ctx.lineWidth = 1;
        ctx.strokeRect(tx+1, ty+1, TILE-2, TILE-2);
      } else if (t === 2) {
        // wall
        ctx.fillStyle = '#2c3a4a';
        ctx.fillRect(tx, ty, TILE, TILE);
        ctx.fillStyle = '#3d4f63';
        ctx.fillRect(tx+4, ty+4, TILE-8, TILE-8);
        ctx.fillStyle = '#1a2230';
        ctx.fillRect(tx+8, ty+8, TILE-16, TILE-16);
      } else if (t === 3) {
        // door — teal sliding panel
        ctx.fillStyle = '#0d3340';
        ctx.fillRect(tx, ty, TILE, TILE);
        ctx.fillStyle = '#1a6070';
        ctx.fillRect(tx+6, ty+6, TILE-12, TILE-12);
        ctx.fillStyle = '#4FC3C3';
        ctx.fillRect(tx+10, ty+10, (TILE-20)/2-2, TILE-20);
        ctx.fillRect(tx+10+(TILE-20)/2+2, ty+10, (TILE-20)/2-2, TILE-20);
        // door label
        ctx.font = 'bold 9px Courier New';
        ctx.fillStyle = '#4FC3C3';
        ctx.textAlign = 'center';
        ctx.fillText('EXIT', tx+TILE/2, ty+TILE-8);
        ctx.textAlign = 'left';
      } else if (t === 4) {
        // crate
        ctx.fillStyle = '#3a2800';
        ctx.fillRect(tx+8, ty+8, TILE-16, TILE-16);
        ctx.fillStyle = '#c47a1e';
        ctx.fillRect(tx+10, ty+10, TILE-20, TILE-20);
        ctx.strokeStyle = '#8a5010';
        ctx.lineWidth = 2;
        ctx.strokeRect(tx+10, ty+10, TILE-20, TILE-20);
        // cross brace
        ctx.beginPath();
        ctx.moveTo(tx+10, ty+10); ctx.lineTo(tx+TILE-10, ty+TILE-10);
        ctx.moveTo(tx+TILE-10, ty+10); ctx.lineTo(tx+10, ty+TILE-10);
        ctx.stroke();
      } else if (t === 5) {
        // weapon rack
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(tx+6, ty+6, TILE-12, TILE-12);
        ctx.strokeStyle = '#D9541E';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(tx+8, ty+8, TILE-16, TILE-16);
        // weapon silhouettes (3 stacked lines)
        ctx.strokeStyle = '#ff7744';
        ctx.lineWidth = 3;
        for (let i = 0; i < 3; i++) {
          const wy = ty + 16 + i*14;
          ctx.beginPath();
          ctx.moveTo(tx+14, wy); ctx.lineTo(tx+TILE-14, wy);
          ctx.stroke();
        }
        ctx.font = 'bold 8px Courier New';
        ctx.fillStyle = '#D9541E';
        ctx.textAlign = 'center';
        ctx.fillText('ARMORY', tx+TILE/2, ty+TILE-8);
        ctx.textAlign = 'left';
      }
    }
  }

  // draw player character (simple circle + direction indicator)
  const px = offX + iPlayerX * TILE;
  const py = offY + iPlayerY * TILE;
  ctx.shadowColor = '#4FC3C3'; ctx.shadowBlur = 12;
  ctx.fillStyle = '#4FC3C3';
  ctx.beginPath(); ctx.arc(px, py, 12, 0, Math.PI*2); ctx.fill();
  ctx.shadowBlur = 0;
  ctx.fillStyle = '#0a1520';
  ctx.beginPath(); ctx.arc(px, py, 6, 0, Math.PI*2); ctx.fill();
  // inner dot
  ctx.fillStyle = '#4FC3C3';
  ctx.beginPath(); ctx.arc(px, py, 3, 0, Math.PI*2); ctx.fill();

  // proximity hint for door
  const distDoor = Math.hypot(iPlayerX - DOOR_COL - 0.5, iPlayerY - DOOR_ROW - 0.5);
  if (distDoor < 1.5) {
    ctx.font = 'bold 13px Courier New';
    ctx.fillStyle = '#4FC3C3';
    ctx.textAlign = 'center';
    ctx.fillText('[E]  EXIT TO SPACE', canvas.width/2, canvas.height - 60);
    ctx.textAlign = 'left';
  }

  // interior HUD strip — top bar
  ctx.fillStyle = '#000000cc';
  ctx.fillRect(0, 0, canvas.width, 34);
  ctx.strokeStyle = '#4FC3C388';
  ctx.lineWidth = 1;
  ctx.strokeRect(0, 0, canvas.width, 34);
  ctx.font = 'bold 13px Courier New';
  ctx.fillStyle = '#4FC3C3';
  ctx.fillText('ARMORY POD', 18, 22);
  ctx.fillStyle = '#4a6070';
  ctx.fillText('WASD — MOVE    [E] — EXIT AT DOOR', 200, 22);
}

function updateInteriorPlayer() {
  if (!interiorMode) return;
  const cols = ARMORY_MAP[0].length;
  const rows = ARMORY_MAP.length;

  let nx = iPlayerX, ny = iPlayerY;
  if (keys['ArrowUp']   || keys['KeyW']) ny -= I_SPEED;
  if (keys['ArrowDown'] || keys['KeyS']) ny += I_SPEED;
  if (keys['ArrowLeft'] || keys['KeyA']) nx -= I_SPEED;
  if (keys['ArrowRight']|| keys['KeyD']) nx += I_SPEED;

  // collision: stay on floor tiles (t===1 or t===3)
  const tileAt = (x, y) => {
    const tc = Math.floor(x), tr = Math.floor(y);
    if (tr < 0 || tr >= rows || tc < 0 || tc >= cols) return 2;
    return ARMORY_MAP[tr][tc];
  };
  const margin = 0.35;
  const walkable = t => t === 1 || t === 3 || t === 4 || t === 5;

  if (walkable(tileAt(nx + margin, iPlayerY)) && walkable(tileAt(nx - margin, iPlayerY))) iPlayerX = nx;
  if (walkable(tileAt(iPlayerX, ny + margin)) && walkable(tileAt(iPlayerX, ny - margin))) iPlayerY = ny;

  // exit trigger: stand on door tile and press E
  const onDoor = Math.floor(iPlayerX) === DOOR_COL && Math.floor(iPlayerY) === DOOR_ROW;
  if (onDoor && _ePressed) {
    interiorFadeDir = -1;  // fade out back to space
    _ePressed = false;
  }
}

'''

if DRAW_HUD_ANCHOR in d:
    d = d.replace(DRAW_HUD_ANCHOR, DRAW_INTERIOR + DRAW_HUD_ANCHOR, 1)
    print('OK drawInterior injected')
else:
    print('drawHUD anchor not found')

# ── INJECT: _ePressed tracking + interior entry in keydown handler ──
# Find the [E] mine key handler and add interior entry logic
OLD_E_KEY = "case 'KeyE':"
NEW_E_KEY = """case 'KeyE':
        _ePressed = true;
        // enter pod interior if standing near an attached pod and not already inside
        if (!interiorMode && interiorFadeDir === 0) {
          const cx = canvas.width/2, cy = canvas.height/2;
          for (let pi = 0; pi < attachedPods.length; pi++) {
            const pod = attachedPods[pi];
            const DIR_OFFSETS = {
              north:{ox:0,oy:38},northeast:{ox:-27,oy:27},east:{ox:-38,oy:0},
              southeast:{ox:-27,oy:-27},south:{ox:0,oy:-38},southwest:{ox:27,oy:-27},
              west:{ox:38,oy:0},northwest:{ox:27,oy:27},
            };
            const off = DIR_OFFSETS[ship.dir] || {ox:0,oy:38};
            const dist = 42 + pi*36, ratio = dist/38;
            const podSX = cx + off.ox*ratio, podSY = cy + off.oy*ratio;
            const dx = podSX - cx, dy = podSY - cy;
            if (Math.hypot(dx, dy) < 80) {
              interiorPodIdx = pi;
              interiorFadeDir = 1;
              iPlayerX = 4.5; iPlayerY = 6.5;  // spawn near door
              break;
            }
          }
        }"""

if OLD_E_KEY in d:
    d = d.replace(OLD_E_KEY, NEW_E_KEY, 1)
    print('OK KeyE handler updated')
else:
    print('KeyE not found')

# ── INJECT: _ePressed reset on keyup ──
OLD_KEYUP = "case 'KeyE':\n        mineTarget = null; break;"
NEW_KEYUP = "case 'KeyE':\n        mineTarget = null; _ePressed = false; break;"
if OLD_KEYUP in d:
    d = d.replace(OLD_KEYUP, NEW_KEYUP, 1)
    print('OK keyup E reset')
else:
    # try alternative
    idx = d.find("mineTarget = null; break;")
    print(f'keyup E alt search at {idx}, ctx:', repr(d[idx-30:idx+40]) if idx>0 else 'not found')

# ── INJECT: _ePressed global declaration ──
EPRESSED_ANCHOR = 'let _boosting  = false;'
if 'let _ePressed' not in d:
    d = d.replace('let _boosting  = false;', 'let _boosting  = false;\nlet _ePressed  = false;', 1)
    print('OK _ePressed global added')

# ── INJECT: fade logic + interior render in main game loop ──
# Find the main draw loop call site — after drawHUD, inject fade overlay and interior switch
OLD_DRAW_LOOP = 'function gameLoop() {'
NEW_DRAW_LOOP = '''function gameLoop() {'''
# We need to inject into the existing gameLoop — find where drawHUD is called
OLD_LOOP_BODY = '  drawHUD(spd);'
NEW_LOOP_BODY = '''  drawHUD(spd);

  // ── INTERIOR FADE + RENDER ──
  // advance fade
  if (interiorFadeDir === 1) {
    interiorFade = Math.min(1, interiorFade + FADE_SPEED);
    if (interiorFade >= 1) { interiorMode = true; interiorFadeDir = 0; }
  } else if (interiorFadeDir === -1) {
    interiorFade = Math.max(0, interiorFade - FADE_SPEED);
    if (interiorFade <= 0) { interiorMode = false; interiorFadeDir = 0; interiorPodIdx = -1; }
  }

  // fade-to-black overlay (used for both transitions)
  if (interiorFade > 0 && !interiorMode) {
    ctx.fillStyle = `rgba(0,0,0,${interiorFade})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  // render interior on top when fully in
  if (interiorMode) {
    updateInteriorPlayer();
    drawInterior();
    // fade-in overlay fading out
    if (interiorFade < 1) {
      ctx.fillStyle = `rgba(0,0,0,${1 - interiorFade})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  }'''

if OLD_LOOP_BODY in d:
    d = d.replace(OLD_LOOP_BODY, NEW_LOOP_BODY, 1)
    print('OK gameLoop interior render injected')
else:
    print('gameLoop drawHUD anchor not found')
    idx = d.find('drawHUD(')
    print(f'drawHUD calls at: {idx}', repr(d[idx-10:idx+40]) if idx>0 else '')

# ── block space controls while in interior ──
OLD_THRUST = 'const shiftHeld = (keys[\'ShiftLeft\'] || keys[\'ShiftRight\']) && ship.fuel > 0;'
NEW_THRUST = "if (interiorMode) { requestAnimationFrame(gameLoop); return; }\n  const shiftHeld = (keys['ShiftLeft'] || keys['ShiftRight']) && ship.fuel > 0;"
if OLD_THRUST in d:
    d = d.replace(OLD_THRUST, NEW_THRUST, 1)
    print('OK interior mode blocks space controls')
else:
    print('shiftHeld anchor not found')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('\nDone. File written.')
