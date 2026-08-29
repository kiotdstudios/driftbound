import re

d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

# ── 1. Version string in loading screen ──
d = re.sub(r'FLIGHT TEST v[\d.]+', 'ALPHA v0.2', d)
d = re.sub(r'flight.test.v[\d.]+', 'alpha_v0.2', d, flags=re.IGNORECASE)
d = d.replace('driftbound_flight_test', 'driftbound_alpha_v0.2')
print("Version string updated to ALPHA v0.2")

# ── 2. Replace the entire loadAll() with a timeout-safe version ──
# Find function boundaries via brace counting
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
  const jobs = [];

  // Helper: load with timeout — never hangs the boot if an asset 404s
  function loadImgSafe(src, ms=4000) {
    totalAssets++;
    return new Promise(resolve => {
      const img = new Image();
      const tid = setTimeout(() => { loadedAssets++; refreshBar(); resolve(null); }, ms);
      img.onload  = () => { clearTimeout(tid); loadedAssets++; refreshBar(); resolve(img); };
      img.onerror = () => { clearTimeout(tid); loadedAssets++; refreshBar(); resolve(null); };
      img.src = src;
    });
  }

  // Pod ship sprites (external PNGs — timeout-safe)
  for (const dir of DIRS) {
    jobs.push(loadImgSafe(`${POD_BASE}rotations/${dir}.png`).then(img => { rotations[dir] = img; }));
  }
  for (const dir of DIRS) {
    animations[dir] = new Array(FRAME_COUNT).fill(null);
    for (let f = 0; f < FRAME_COUNT; f++) {
      const ff = f, pad = String(f).padStart(3, '0');
      jobs.push(
        loadImgSafe(`${POD_BASE}animations/${ANIM_KEY}/${dir}/frame_${pad}.png`)
          .then(img => { animations[dir][ff] = img; })
      );
    }
  }
  for (const dir of DIRS) {
    jobs.push(loadImgSafe(`${POD_SPRITE_BASE}rotations/${dir}.png`).then(img => { podRotations[dir] = img; }));
  }
  for (const dir of DIRS) {
    podAnimations[dir] = new Array(FRAME_COUNT).fill(null);
    for (let f = 0; f < FRAME_COUNT; f++) {
      const ff = f, pad = String(f).padStart(3, '0');
      jobs.push(
        loadImgSafe(`${POD_SPRITE_BASE}animations/${POD_ANIM_KEY}/${dir}/frame_${pad}.png`)
          .then(img => { podAnimations[dir][ff] = img; })
      );
    }
  }

  // Background layers (external PNGs — timeout-safe, fall back to procedural if null)
  const bgName = BG_SETS[currentBgIdx];
  const bgDefs = [
    { file: `${bgName}_FLAT.png`,    speed: 0.05 },
    { file: `${bgName}_L1_far.png`,  speed: 0.20 },
    { file: `${bgName}_L2_mid.png`,  speed: 0.50 },
    { file: `${bgName}_L3_near.png`, speed: 1.00 },
  ];
  const bgPromises = bgDefs.map(d =>
    loadImgSafe(`${BG_BASE}${d.file}`, 5000).then(img => ({ img, speed: d.speed }))
  );
  jobs.push(Promise.all(bgPromises).then(layers => {
    // Keep only layers where image loaded — fall back to null (drawBG handles null gracefully)
    bgLayers = layers.sort((a, b) => a.speed - b.speed);
  }));

  // Asteroid sprites (timeout-safe)
  for (const t of ASTEROID_TYPES) {
    jobs.push(loadImgSafe('Demo_assets/asteroids/' + t.id + '.png')
      .then(img => { asteroidImgs[t.id] = img; }));
  }

  await Promise.all(jobs);
}'''

d = d[:fn_start] + new_loadAll + d[fn_end:]
print("loadAll() replaced with timeout-safe version")

# ── 3. Make drawBG handle null bgLayers gracefully (skip render, use solid fallback) ──
# Find drawBG and add a null-check guard at the top
fn2_start = d.find('function drawBG(camX, camY)')
assert fn2_start != -1, "drawBG not found"
# Find opening brace
brace_open = d.find('{', fn2_start)
# Insert null guard right after opening brace
null_guard = "\n  if (!bgLayers || bgLayers.length === 0) { ctx.fillStyle='#040810'; ctx.fillRect(0,0,canvas.width,canvas.height); return; }"
d = d[:brace_open+1] + null_guard + d[brace_open+1:]
print("drawBG null-guard added")

# ── 4. Brace check ──
depth = 0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
