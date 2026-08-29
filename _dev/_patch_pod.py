with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. POD CONSTANTS + DATA  — inject after ANIM_KEY line
# ══════════════════════════════════════════════════════════════════
POD_CONST_ANCHOR = "const ANIM_KEY = '8-frame_spaceship_flying_animation._Keep_the_ship';"
POD_CONST_BLOCK = r"""const ANIM_KEY = '8-frame_spaceship_flying_animation._Keep_the_ship';

// ─── MODULAR POD SYSTEM ───────────────────────────────────────────────────────
const POD_SPRITE_BASE  = 'pod_sprites/Create_a_small_modular_spacecr/';
const POD_ANIM_KEY     = '8-frame_spaceship_flying_animation._Keep_the_ship';
const POD_ATTACH_RANGE = 120;   // world-px — proximity to trigger attach prompt
const POD_ATTACH_COST  = 10;    // Nebulite ore required to claim a pod
const POD_DISPLAY_SIZE = 96;    // rendered size (slightly bigger than ship)

// Pod definitions — add more types here later
const POD_TYPES = {
  modular_space_pod: {
    id:       'modular_space_pod',
    label:    'MODULAR POD',
    color:    '#38bdf8',
    cargoBonus: 25,   // +25 cargo capacity when attached
    desc:     'Expands cargo hold by 25 units.',
  },
};

// Active world pods — spawned at boot, removed when claimed
const worldPods = [
  { pid: 'pod_001', type: 'modular_space_pod', worldX: 350, worldY: -200, angle: 0.4 },
];

// Player's attached pods
const attachedPods = [];

// Pod sprite cache
const podRotations  = {};
const podAnimations = {};"""

if POD_CONST_ANCHOR in d:
    d = d.replace(POD_CONST_ANCHOR, POD_CONST_BLOCK)
    fixes.append('pod constants + data injected')
else:
    fixes.append('pod constants: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. LOAD POD SPRITES — inside loadAll(), after main ship frames
# ══════════════════════════════════════════════════════════════════
LOAD_ANCHOR = "  // Initial BG loaded through normal loadImg so progress bar counts it"
POD_LOAD = """  // ── Load modular pod sprites ──
  for (const dir of DIRS) {
    jobs.push(loadImg(`${POD_SPRITE_BASE}rotations/${dir}.png`).then(img => {
      podRotations[dir] = img;
    }));
  }
  for (const dir of DIRS) {
    podAnimations[dir] = new Array(FRAME_COUNT).fill(null);
    for (let f = 0; f < FRAME_COUNT; f++) {
      const ff = f, pad = String(f).padStart(3,'0');
      jobs.push(
        loadImg(`${POD_SPRITE_BASE}animations/${POD_ANIM_KEY}/${dir}/frame_${pad}.png`)
          .then(img => { podAnimations[dir][ff] = img; })
      );
    }
  }

  // Initial BG loaded through normal loadImg so progress bar counts it"""

if LOAD_ANCHOR in d:
    d = d.replace(LOAD_ANCHOR, POD_LOAD)
    fixes.append('pod sprites loaded in loadAll()')
else:
    fixes.append('pod load anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 3. drawWorldPods() function — inject before drawOrePickups
# ══════════════════════════════════════════════════════════════════
DRAW_ANCHOR = "function drawOrePickups(cx, cy) {"
POD_DRAW = """// ─── DRAW WORLD PODS ─────────────────────────────────────────────────────────

function drawWorldPods(cx, cy) {
  const t = Date.now() * 0.001;
  for (const pod of worldPods) {
    const sx = cx + (pod.worldX - ship.worldX);
    const sy = cy + (pod.worldY - ship.worldY);
    if (sx < -100 || sx > canvas.width+100 || sy < -100 || sy > canvas.height+100) continue;

    const podType = POD_TYPES[pod.type];
    const dist    = Math.hypot(pod.worldX - ship.worldX, pod.worldY - ship.worldY);
    const inRange = dist < POD_ATTACH_RANGE;

    // Idle slow rotation
    pod.angle = (pod.angle || 0) + 0.004;

    // Beacon pulse ring
    const pulse = 0.5 + 0.5 * Math.sin(t * 2 + pod.worldX * 0.01);
    ctx.save();
    ctx.globalAlpha = inRange ? 0.5 + 0.3 * pulse : 0.2 * pulse;
    ctx.strokeStyle = inRange ? podType.color : '#ffffff44';
    ctx.lineWidth   = inRange ? 2 : 1;
    ctx.beginPath();
    ctx.arc(sx, sy, POD_DISPLAY_SIZE * 0.7 + pulse * 10, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Draw pod sprite (use south rotation, slowly spinning)
    const spinDir = 'south'; // static direction — pod floats in space
    const podImg  = podRotations[spinDir];
    ctx.save();
    ctx.translate(sx, sy);
    ctx.rotate(pod.angle);
    if (podImg) {
      ctx.imageSmoothingEnabled = false;
      ctx.shadowColor = podType.color;
      ctx.shadowBlur  = inRange ? 18 : 8;
      ctx.drawImage(podImg,
        -POD_DISPLAY_SIZE/2, -POD_DISPLAY_SIZE/2,
        POD_DISPLAY_SIZE, POD_DISPLAY_SIZE);
      ctx.shadowBlur = 0;
    } else {
      // Fallback hexagon
      ctx.fillStyle = podType.color + 'aa';
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const a = (i/6)*Math.PI*2 - Math.PI/2;
        i === 0 ? ctx.moveTo(Math.cos(a)*28, Math.sin(a)*28)
                : ctx.lineTo(Math.cos(a)*28, Math.sin(a)*28);
      }
      ctx.closePath(); ctx.fill();
    }
    ctx.restore();

    // Label
    ctx.save();
    ctx.textAlign = 'center';
    ctx.font      = '12px Courier New';
    ctx.fillStyle = podType.color;
    ctx.globalAlpha = inRange ? 1 : 0.6;
    ctx.fillText(podType.label, sx, sy - POD_DISPLAY_SIZE/2 - 10);

    // Attach prompt when in range
    if (inRange) {
      const canAfford = ship.ore >= POD_ATTACH_COST;
      ctx.font      = '11px Courier New';
      ctx.fillStyle = canAfford ? '#22c55e' : '#ef4444';
      const costTxt = canAfford
        ? `[F]  ATTACH  (${POD_ATTACH_COST} Nebulite)`
        : `NEED ${POD_ATTACH_COST} NEBULITE  (have ${ship.ore})`;
      ctx.fillText(costTxt, sx, sy + POD_DISPLAY_SIZE/2 + 22);
      // Desc line
      ctx.font      = '10px Courier New';
      ctx.fillStyle = '#ffffff88';
      ctx.fillText(podType.desc, sx, sy + POD_DISPLAY_SIZE/2 + 38);
    }
    ctx.restore();
  }
}

// ─── ATTACH POD LOGIC ────────────────────────────────────────────────────────

function updatePods() {
  if (!keys['KeyF']) return;
  for (let i = worldPods.length - 1; i >= 0; i--) {
    const pod  = worldPods[i];
    const dist = Math.hypot(pod.worldX - ship.worldX, pod.worldY - ship.worldY);
    if (dist < POD_ATTACH_RANGE) {
      if (ship.ore >= POD_ATTACH_COST) {
        ship.ore -= POD_ATTACH_COST;
        attachedPods.push({ ...POD_TYPES[pod.type], pid: pod.pid });
        worldPods.splice(i, 1);

        // Apply cargo bonus
        const podType = POD_TYPES[pod.type];
        if (podType.cargoBonus) {
          ship.shipType.cargoLimit += podType.cargoBonus;
        }
        showToast('POD ATTACHED  +' + (podType.cargoBonus||0) + ' CARGO', '#38bdf8');
        // Burst particles
        const sx = canvas.width/2, sy = canvas.height/2;
        for (let p = 0; p < 30; p++) {
          const ang = Math.random()*Math.PI*2, spd = 1+Math.random()*3;
          particles.push({x:sx,y:sy,vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
            life:40+Math.random()*30,maxLife:70,color:'#38bdf8',size:2+Math.random()*2});
        }
      } else {
        showToast('NOT ENOUGH NEBULITE  (' + ship.ore + '/' + POD_ATTACH_COST + ')', '#ef4444');
      }
      return; // one pod per keypress
    }
  }
}

function drawAttachedPods(cx, cy) {
  if (!attachedPods.length) return;
  // Draw small icons on HUD (top-right corner)
  ctx.save();
  ctx.textAlign = 'right';
  ctx.font = '11px Courier New';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('MODULES:', canvas.width - 14, 28);
  attachedPods.forEach((p, i) => {
    ctx.fillStyle = p.color || '#38bdf8';
    ctx.fillText('⬡ ' + p.label, canvas.width - 14, 28 + (i+1)*16);
  });
  ctx.restore();
}

function drawOrePickups(cx, cy) {"""

if DRAW_ANCHOR in d:
    d = d.replace(DRAW_ANCHOR, POD_DRAW)
    fixes.append('drawWorldPods + updatePods injected')
else:
    fixes.append('draw anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 4. CALL drawWorldPods + updatePods in the game loop
#    Inject just before drawOrePickups call
# ══════════════════════════════════════════════════════════════════
LOOP_ANCHOR = "  drawMiningLaser(cx, cy);"
POD_LOOP_CALLS = """  drawWorldPods(cx, cy);
  updatePods();
  drawAttachedPods(cx, cy);
  drawMiningLaser(cx, cy);"""

if LOOP_ANCHOR in d:
    d = d.replace(LOOP_ANCHOR, POD_LOOP_CALLS)
    fixes.append('pod calls wired in game loop')
else:
    fixes.append('loop anchor: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 5. SERVER — add pod_sprites static route to main.py
# ══════════════════════════════════════════════════════════════════
with open('main.py', 'rb') as f:
    mp = f.read().decode('utf-8')

OLD_STATIC = "    app.router.add_static('/vapor_bg',                       'vapor_bg',                 show_index=False)"
NEW_STATIC  = ("    app.router.add_static('/vapor_bg',                       'vapor_bg',                 show_index=False)\r\n"
               "    app.router.add_static('/pod_sprites',                    'pod_sprites',              show_index=False)")

if OLD_STATIC in mp and '/pod_sprites' not in mp:
    mp = mp.replace(OLD_STATIC, NEW_STATIC)
    with open('main.py', 'wb') as f:
        f.write(mp.encode('utf-8'))
    fixes.append('main.py pod_sprites route added')
elif '/pod_sprites' in mp:
    fixes.append('main.py pod_sprites route already exists')
else:
    fixes.append('main.py static anchor: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
