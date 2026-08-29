import re

d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Remove vapor_bg jobs from loadAll() — find and excise the bgPromises block
# ─────────────────────────────────────────────────────────────────────────────
old_bg_block = re.search(
    r'  // Background layers.*?jobs\.push\(Promise\.all\(bgPromises\).*?\}\)\);\n',
    d, re.DOTALL
)
if old_bg_block:
    d = d[:old_bg_block.start()] + d[old_bg_block.end():]
    print("Removed vapor_bg block from loadAll()")
else:
    print("WARNING: bg block not found in loadAll — may already be removed")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Replace drawBG with procedural parallax
# ─────────────────────────────────────────────────────────────────────────────
fn_start = d.find('function drawBG(camX, camY)')
assert fn_start != -1, "drawBG not found"
depth = 0; i = fn_start
while i < len(d):
    if d[i] == '{': depth += 1
    elif d[i] == '}':
        depth -= 1
        if depth == 0:
            fn_end = i + 1
            break
    i += 1

new_drawBG = r'''function drawBG(camX, camY) {
  const W = canvas.width, H = canvas.height;
  const cx = W / 2, cy = H / 2;

  // ── Deep void base ──
  ctx.fillStyle = '#020508';
  ctx.fillRect(0, 0, W, H);

  // ── Vignette ──
  const vg = ctx.createRadialGradient(cx, cy, H * 0.15, cx, cy, H * 0.85);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(0,2,8,0.72)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, W, H);

  // ── Nebula clouds ──
  for (const n of _BG.nebulae) {
    const px = ((n.wx - camX * n.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cx;
    const py = ((n.wy - camY * n.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cy;
    const r = n.r * Math.max(W, H);
    const g = ctx.createRadialGradient(px, py, 0, px, py, r);
    g.addColorStop(0, n.c0);
    g.addColorStop(0.5, n.c1);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save();
    ctx.globalAlpha = n.a;
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.ellipse(px, py, r * n.ex, r * n.ey, n.rot, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // ── Stars ──
  for (const s of _BG.stars) {
    const px = ((s.wx - camX * s.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cx;
    const py = ((s.wy - camY * s.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cy;
    if (px < -8 || px > W + 8 || py < -8 || py > H + 8) continue;
    ctx.globalAlpha = s.a;
    if (s.bloom) {
      const bloom = ctx.createRadialGradient(px, py, 0, px, py, s.r * 6);
      bloom.addColorStop(0, s.col);
      bloom.addColorStop(0.15, s.col);
      bloom.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = bloom;
      ctx.beginPath(); ctx.arc(px, py, s.r * 6, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = s.col; ctx.lineWidth = 0.5; ctx.globalAlpha = s.a * 0.35;
      ctx.beginPath(); ctx.moveTo(px - s.r*10, py); ctx.lineTo(px + s.r*10, py); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(px, py - s.r*10); ctx.lineTo(px, py + s.r*10); ctx.stroke();
      ctx.globalAlpha = s.a;
    }
    ctx.fillStyle = s.col;
    ctx.beginPath(); ctx.arc(px, py, s.r, 0, Math.PI * 2); ctx.fill();
  }

  // ── Dust streaks ──
  for (const dk of _BG.dust) {
    const px = ((dk.wx - camX * dk.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cx;
    const py = ((dk.wy - camY * dk.par) % (WORLD_SIZE * 2) + WORLD_SIZE * 2) % (WORLD_SIZE * 2) - WORLD_SIZE + cy;
    if (px < -220 || px > W + 220 || py < -220 || py > H + 220) continue;
    ctx.save();
    ctx.globalAlpha = dk.a;
    ctx.translate(px, py); ctx.rotate(dk.rot);
    const dg = ctx.createRadialGradient(0, 0, 0, 0, 0, dk.len);
    dg.addColorStop(0, dk.col); dg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = dg; ctx.scale(1, 0.18);
    ctx.beginPath(); ctx.arc(0, 0, dk.len, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  ctx.globalAlpha = 1;
}'''

d = d[:fn_start] + new_drawBG + d[fn_end:]
print("drawBG replaced with procedural parallax")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Inject _BG data object + _initBG() right before loadAll
# ─────────────────────────────────────────────────────────────────────────────
bg_system_js = r'''
// ═══════════════════════════════════════════════════════════════════════════
// PROCEDURAL BACKGROUND — seeded LCG, deterministic layout every run
// ═══════════════════════════════════════════════════════════════════════════
const _BG = { stars: [], nebulae: [], dust: [] };

function _initBG() {
  let _s = 42;
  const rng = () => { _s = (_s * 1664525 + 1013904223) & 0xFFFFFFFF; return (_s >>> 0) / 0xFFFFFFFF; };
  const WS2 = WORLD_SIZE * 2;

  // Nebulae
  const nebPal = [
    ['rgba(20,5,60,0)','rgba(40,10,100,0.18)'],
    ['rgba(0,20,50,0)','rgba(0,60,120,0.14)'],
    ['rgba(30,0,20,0)','rgba(90,10,60,0.12)'],
    ['rgba(0,30,20,0)','rgba(0,80,60,0.10)'],
    ['rgba(50,20,0,0)','rgba(120,50,10,0.09)'],
  ];
  for (let i = 0; i < 10; i++) {
    const p = nebPal[Math.floor(rng() * nebPal.length)];
    _BG.nebulae.push({ wx:(rng()-.5)*WS2*1.4, wy:(rng()-.5)*WS2*1.4,
      r:.3+rng()*.5, ex:.6+rng()*.8, ey:.4+rng()*.6, rot:rng()*Math.PI*2,
      a:.55+rng()*.35, par:.08+rng()*.06, c0:p[1], c1:p[0] });
  }

  // Deep dust (layer 0)
  for (let i = 0; i < 2200; i++) {
    _BG.stars.push({ wx:(rng()-.5)*WS2*1.6, wy:(rng()-.5)*WS2*1.6,
      r:.3+rng()*.4, a:.15+rng()*.35, par:.012+rng()*.015, bloom:false,
      col:`rgb(${180+~~(rng()*60)},${185+~~(rng()*55)},${200+~~(rng()*55)})` });
  }
  // Mid stars (layer 1)
  for (let i = 0; i < 600; i++) {
    const w = rng()>.5;
    _BG.stars.push({ wx:(rng()-.5)*WS2*1.6, wy:(rng()-.5)*WS2*1.6,
      r:.5+rng()*.7, a:.45+rng()*.45, par:.05+rng()*.04, bloom:false,
      col: w ? `rgb(${220+~~(rng()*35)},${200+~~(rng()*40)},${150+~~(rng()*60)})`
             : `rgb(${160+~~(rng()*60)},${200+~~(rng()*40)},${230+~~(rng()*25)})` });
  }
  // Bright stars (layer 2)
  for (let i = 0; i < 90; i++) {
    const bloom = rng()>.75, t = rng();
    const col = t<.3 ? `rgb(255,${160+~~(t*200)},${80+~~(t*100)})`
              : t<.7 ? `rgb(230,235,255)`
                     : `rgb(${160+~~((1-t)*200)},${190+~~((1-t)*60)},255)`;
    _BG.stars.push({ wx:(rng()-.5)*WS2*1.6, wy:(rng()-.5)*WS2*1.6,
      r:1.0+rng()*1.4, a:.75+rng()*.25, par:.14+rng()*.08, bloom, col });
  }

  // Dust streaks
  const dCols=['rgba(80,100,160,1)','rgba(60,80,130,1)','rgba(100,80,140,1)','rgba(60,100,110,1)'];
  for (let i = 0; i < 45; i++) {
    _BG.dust.push({ wx:(rng()-.5)*WS2*1.5, wy:(rng()-.5)*WS2*1.5,
      len:60+rng()*180, rot:rng()*Math.PI*2, a:.04+rng()*.08,
      par:.28+rng()*.12, col:dCols[~~(rng()*dCols.length)] });
  }
}

'''

loadall_pos = d.find('async function loadAll()')
assert loadall_pos != -1, "loadAll not found"
d = d[:loadall_pos] + bg_system_js + d[loadall_pos:]
print("_BG system injected before loadAll()")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Add _initBG() call in boot() — find by brace-counting boot()
# ─────────────────────────────────────────────────────────────────────────────
boot_start = d.find('async function boot()')
assert boot_start != -1, "boot() not found"
depth = 0; i = boot_start
while i < len(d):
    if d[i] == '{': depth += 1
    elif d[i] == '}':
        depth -= 1
        if depth == 0:
            boot_end = i  # position of closing brace
            break
    i += 1

# Insert _initBG() call just before the closing brace of boot()
insert = '\n  _initBG();'
# Find the requestAnimationFrame(loop) line inside boot and insert after it
raf_in_boot = d.rfind('requestAnimationFrame(loop)', boot_start, boot_end)
assert raf_in_boot != -1, "RAF not found inside boot()"
after_raf = d.find('\n', raf_in_boot) + 1
d = d[:raf_in_boot] + '_initBG();\n  ' + d[raf_in_boot:]
print("_initBG() call added before RAF in boot()")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Remove old null guard if present
# ─────────────────────────────────────────────────────────────────────────────
old_null_guard = "\n  if (!bgLayers || bgLayers.length === 0) { ctx.fillStyle='#040810'; ctx.fillRect(0,0,canvas.width,canvas.height); return; }"
if old_null_guard in d:
    d = d.replace(old_null_guard, '')
    print("Old null guard removed")

# ── Brace check ──
depth = 0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
