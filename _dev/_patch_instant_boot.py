import re

d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

# ─────────────────────────────────────────────────────────────────────────────
# Replace entire loadAll() with a version that:
#  - fires ALL image loads in the background (no await)
#  - resolves immediately so boot never blocks
#  - asteroid sprites still load (they're small/local) but won't block either
# ─────────────────────────────────────────────────────────────────────────────
fn_start = d.find('async function loadAll()')
assert fn_start != -1, "loadAll not found"
depth = 0; i = fn_start
while i < len(d):
    if d[i] == '{': depth += 1
    elif d[i] == '}':
        depth -= 1
        if depth == 0:
            fn_end = i + 1
            break
    i += 1

new_loadAll = r'''async function loadAll() {
  // Boot is instant — all external assets load in background after game starts.
  // Renderers check for null and draw vector fallbacks if images aren't ready yet.

  function bgLoad(src, onDone) {
    totalAssets++;
    const img = new Image();
    img.onload  = () => { loadedAssets++; refreshBar(); if (onDone) onDone(img); };
    img.onerror = () => { loadedAssets++; refreshBar(); };
    img.src = src;
  }

  // Pod ship sprites — background load, no await
  for (const dir of DIRS) {
    bgLoad(`${POD_BASE}rotations/${dir}.png`,        img => { rotations[dir] = img; });
    bgLoad(`${POD_SPRITE_BASE}rotations/${dir}.png`, img => { podRotations[dir] = img; });
    for (let f = 0; f < FRAME_COUNT; f++) {
      const ff = f, pad = String(f).padStart(3, '0');
      bgLoad(`${POD_BASE}animations/${ANIM_KEY}/${dir}/frame_${pad}.png`,
             img => { animations[dir][ff] = img; });
      bgLoad(`${POD_SPRITE_BASE}animations/${POD_ANIM_KEY}/${dir}/frame_${pad}.png`,
             img => { podAnimations[dir][ff] = img; });
    }
  }

  // Asteroid sprites — background load
  for (const t of ASTEROID_TYPES) {
    bgLoad('Demo_assets/asteroids/' + t.id + '.png', img => { asteroidImgs[t.id] = img; });
  }

  // Return immediately — game starts now, sprites swap in as they arrive
}'''

d = d[:fn_start] + new_loadAll + d[fn_end:]
print("loadAll() replaced — instant boot, background asset loading")

# ─────────────────────────────────────────────────────────────────────────────
# Make sure drawShip handles null sprite gracefully (vector fallback)
# ─────────────────────────────────────────────────────────────────────────────
fn2_start = d.find('function drawShip(')
assert fn2_start != -1, "drawShip not found"
depth = 0; i = fn2_start
while i < len(d):
    if d[i] == '{': depth += 1
    elif d[i] == '}':
        depth -= 1
        if depth == 0:
            fn2_end = i + 1
            break
    i += 1

old_drawShip = d[fn2_start:fn2_end]

# Find the first image draw — it's something like rotations[dir] or ctx.drawImage
# Inject a null check at the top of the function body
brace_open = d.find('{', fn2_start)
null_check = '''
  // ── Vector fallback if sprites not loaded yet ──
  const _shipImg = rotations[ship.dir] || null;
  if (!_shipImg) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(DIR_ANGLES_DEG[DIRS.indexOf(ship.dir)] * Math.PI / 180);
    ctx.strokeStyle = '#4FC3C3'; ctx.lineWidth = 2; ctx.globalAlpha = 0.9;
    ctx.beginPath();
    ctx.moveTo(0, -18); ctx.lineTo(12, 14); ctx.lineTo(0, 8);
    ctx.lineTo(-12, 14); ctx.closePath(); ctx.stroke();
    // engine glow
    if (thrusting || boosting) {
      ctx.strokeStyle = boosting ? '#ff6b35' : '#00ff88';
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(-7, 10); ctx.lineTo(0, 22); ctx.lineTo(7, 10); ctx.stroke();
    }
    ctx.restore();
    return;
  }'''

d = d[:brace_open+1] + null_check + d[brace_open+1:]
print("drawShip vector fallback injected")

# ─────────────────────────────────────────────────────────────────────────────
# Same for drawWorldPods — null check so pods render as shapes before sprites load
# ─────────────────────────────────────────────────────────────────────────────
fn3_start = d.find('function drawWorldPods(')
assert fn3_start != -1, "drawWorldPods not found"
b3 = d.find('{', fn3_start)

pod_null_check = '''
  // pod sprites load in background — rendered as glowing hexagons until ready'''

# Just ensure any ctx.drawImage for pods is guarded — find drawImage calls inside drawWorldPods
# Simpler: wrap the existing sprite draw with an if(img) check
# Find the pattern: ctx.drawImage( inside drawWorldPods
depth = 0; i = fn3_start; fn3_end = fn3_start
while i < len(d):
    if d[i] == '{': depth += 1
    elif d[i] == '}':
        depth -= 1
        if depth == 0:
            fn3_end = i + 1
            break
    i += 1

fn3_body = d[fn3_start:fn3_end]
# Replace unguarded ctx.drawImage with guarded version
fn3_body = re.sub(
    r'(ctx\.drawImage\((?:rotations|podRotations|animations|podAnimations)[^;]+;)',
    r'if (\1.split("(")[1].split(",")[0].trim().includes("null")==false) { \1 }',
    fn3_body
)
# Actually simpler — just guard every ctx.drawImage in the file that uses these arrays
print("Skipping drawWorldPods regex (handled by null img check in drawImage itself)")

# ─────────────────────────────────────────────────────────────────────────────
# Global: guard all ctx.drawImage calls that pass rotations/animations arrays
# drawImage with a null img throws — wrap every such call
# ─────────────────────────────────────────────────────────────────────────────
# Pattern: ctx.drawImage(someVar, ...) where someVar might be null
# Replace with: if (someVar) ctx.drawImage(someVar, ...)
d = re.sub(
    r'ctx\.drawImage\((\w+(?:\[[\w.\'\"]+\])+),',
    r'if (\1) ctx.drawImage(\1,',
    d
)
# But that breaks the semicolons — we need to close them. Actually let's do targeted:
# Revert that and do it properly
d = re.sub(
    r'if \((\w+(?:\[[\w.\'\"]+\])+)\) ctx\.drawImage\(\1,([^;]+);',
    r'if (\1) { ctx.drawImage(\1,\2; }',
    d
)
print("ctx.drawImage null guards added globally")

# ─────────────────────────────────────────────────────────────────────────────
# Brace check
# ─────────────────────────────────────────────────────────────────────────────
depth = 0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
