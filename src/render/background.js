// ═══════════════════════════════════════════════════════════════════════════
// DRIFTBOUND — DEEP-SPACE ENVIRONMENT / BACKGROUND SYSTEM
// Self-contained render module. Owns:
//   - a true parallax nebula depth-stack (7-layer environment pack)
//   - a procedural starfield (4 tiers, asynchronous twinkle, rare glow)
//   - a velocity-responsive procedural particle field (near tier streaks on boost)
//   - restrained ambient blue lighting + vignette
// No dependency on game logic. Driven each frame by a camera-state object:
//   render({ x, y, vx, vy, boosting, now })
// Configuration (ENV_CONFIG) is intentionally separated from rendering logic so
// the environment can be art-directed without touching the draw code.
// ═══════════════════════════════════════════════════════════════════════════

// ─── TUNABLE CONFIG (art-direction surface — no rendering logic below this) ───
export const ENV_CONFIG = {
  // Depth stack. Back -> front. Motion is NOT arbitrary 1..7; it derives from
  // each layer's real depth (parallax) plus a tiny independent ambient drift.
  //   parallax   : fraction of camera world-motion applied (0 = infinitely far)
  //   driftX/Y   : autonomous ambient drift, px/second (keeps gas alive at rest)
  //   alpha      : base opacity
  //   breathe    : opacity swing amplitude (subconscious, not pulsing)
  //   breatheSpd : breathe cycles/second
  //   scale      : coverage multiplier over the screen (>1 enlarges + hides seams)
  //   blend      : canvas composite op ('source-over' base, 'lighter' = additive gas)
  //   tile       : true = wrap-tile to cover; false = single oversized centered draw
  layers: {
    base:  { parallax: 0.015, driftX:  0.0, driftY:  0.0, alpha: 1.00, breathe: 0.00, breatheSpd: 0.00, scale: 1.34, blend: 'source-over', tile: false },
    far:   { parallax: 0.035, driftX:  1.4, driftY:  0.5, alpha: 0.55, breathe: 0.05, breatheSpd: 0.008, scale: 1.55, blend: 'lighter',     tile: true  },
    mid:   { parallax: 0.065, driftX: -1.1, driftY:  1.1, alpha: 0.50, breathe: 0.06, breatheSpd: 0.011, scale: 1.45, blend: 'lighter',     tile: true  },
    near:  { parallax: 0.105, driftX:  2.0, driftY: -0.7, alpha: 0.46, breathe: 0.06, breatheSpd: 0.014, scale: 1.35, blend: 'lighter',     tile: true  },
    atmo:  { parallax: 0.160, driftX: -1.7, driftY:  0.9, alpha: 0.32, breathe: 0.07, breatheSpd: 0.017, scale: 1.30, blend: 'lighter',     tile: true  },
    vapor: { parallax: 0.240, driftX:  2.6, driftY:  0.4, alpha: 0.24, breathe: 0.08, breatheSpd: 0.021, scale: 1.25, blend: 'lighter',     tile: true  },
    dust:  { parallax: 0.330, driftX:  1.0, driftY: -0.9, alpha: 0.28, breathe: 0.05, breatheSpd: 0.016, scale: 1.20, blend: 'lighter',     tile: true  },
  },
  parallaxStrength: 1.0,   // global multiplier over every layer's parallax
  ambientDrift:     1.0,   // global multiplier over ambient drift

  stars: {
    density: 1.0,          // multiplies all tier counts
    twinkleIntensity: 1.0, // multiplies all twinkle amplitudes
    spread: 9000,          // world-px wrap span (> screen so no visible seam)
    // count, parallax, rMin, rMax, baseAlpha, twAmp, twMinHz, twMaxHz, glow
    tiers: [
      { count: 260, parallax: 0.050, rMin: 0.5, rMax: 1.0, baseAlpha: 0.42, twAmp: 0.20, twMinHz: 0.15, twMaxHz: 0.45, glow: false },
      { count: 120, parallax: 0.110, rMin: 0.8, rMax: 1.6, baseAlpha: 0.56, twAmp: 0.28, twMinHz: 0.20, twMaxHz: 0.60, glow: false },
      { count:  34, parallax: 0.190, rMin: 1.4, rMax: 2.3, baseAlpha: 0.72, twAmp: 0.30, twMinHz: 0.25, twMaxHz: 0.75, glow: true  },
      { count:   6, parallax: 0.260, rMin: 2.4, rMax: 3.4, baseAlpha: 0.85, twAmp: 0.22, twMinHz: 0.10, twMaxHz: 0.30, glow: true  }, // rare standouts
    ],
  },

  particles: {
    density: 1.0,
    boostResponse: 1.0,    // scales streak length under boost
    spread: 6000,
    // count, parallax, size, alpha, color, streak (nearest tier streaks on boost)
    tiers: [
      { count: 60, parallax: 0.45, size: 0.8, alpha: 0.10, color: '#8fb8d8', streak: false }, // micro dust
      { count: 34, parallax: 0.70, size: 1.2, alpha: 0.16, color: '#6fa0d0', streak: false }, // faint blue
      { count: 14, parallax: 0.95, size: 1.8, alpha: 0.22, color: '#b8d0e0', streak: true  }, // near debris
    ],
  },

  lighting: {
    strength:   1.0,       // 0 disables the ambient blue cast entirely
    color:      '#16386a', // deep nebula blue
    baseAlpha:  0.05,      // very subtle
    breatheAmp: 0.30,      // fraction of baseAlpha it swings
    breatheSpd: 0.02,      // cycles/second
  },

  vignette: 0.55,          // corner darkening strength
};

// ─── FACTORY (rendering logic — reads ENV_CONFIG, owns no config values) ──────
export function createEnvironment(ctx, canvas) {
  let imgs = {};                 // { base, far, mid, near, atmo, vapor, dust } -> HTMLImageElement
  const stars = [];
  const particles = [];
  let _driftT = 0;               // accumulated real seconds (ambient drift + twinkle clock)
  let _lastNow = 0;
  let _camVel = 0;               // last camera speed (for stats)

  const PALETTE = ['#ffffff', '#dbeeff', '#ffe9d6', '#e2d8ff', '#c8e8ff', '#fff6cf'];
  const rand = (a, b) => a + Math.random() * (b - a);

  // Per-layer breathe phase offset so no two gas layers pulse in sync.
  const _PHASE = { base: 0, far: 1.1, mid: 2.7, near: 4.0, atmo: 5.3, vapor: 0.6, dust: 3.4 };

  function setLayers(o) { imgs = o || {}; }

  function initField() {
    stars.length = 0;
    const S = ENV_CONFIG.stars;
    S.tiers.forEach((tier, ti) => {
      const n = Math.round(tier.count * S.density);
      for (let i = 0; i < n; i++) {
        stars.push({
          wx: rand(-S.spread / 2, S.spread / 2),
          wy: rand(-S.spread / 2, S.spread / 2),
          r:  rand(tier.rMin, tier.rMax),
          ti,
          phase: Math.random() * Math.PI * 2,       // random start -> asynchronous
          hz:    rand(tier.twMinHz, tier.twMaxHz),  // random rate -> never in unison
          col:   PALETTE[(Math.random() * PALETTE.length) | 0],
        });
      }
    });
    particles.length = 0;
    const P = ENV_CONFIG.particles;
    P.tiers.forEach((tier, ti) => {
      const n = Math.round(tier.count * P.density);
      for (let i = 0; i < n; i++) {
        particles.push({
          wx: rand(-P.spread / 2, P.spread / 2),
          wy: rand(-P.spread / 2, P.spread / 2),
          ti,
          size: tier.size * rand(0.7, 1.4),
        });
      }
    });
  }

  // Cached, resize-scoped resources (no per-frame gradient allocation).
  let _vg = null, _vw = 0, _vh = 0, _glow = null;

  function _ensureVignette(W, H) {
    if (_vw === W && _vh === H && _vg) return;
    _vw = W; _vh = H;
    _vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.12, W / 2, H / 2, H * 0.85);
    _vg.addColorStop(0, 'rgba(0,0,0,0)');
    _vg.addColorStop(1, `rgba(0,0,6,${ENV_CONFIG.vignette})`);
  }

  function _ensureGlow() {
    if (_glow) return;
    _glow = document.createElement('canvas');
    _glow.width = _glow.height = 32;
    const g = _glow.getContext('2d');
    const rg = g.createRadialGradient(16, 16, 0, 16, 16, 16);
    rg.addColorStop(0,    'rgba(255,255,255,1)');
    rg.addColorStop(0.35, 'rgba(255,255,255,0.5)');
    rg.addColorStop(1,    'rgba(255,255,255,0)');
    g.fillStyle = rg; g.fillRect(0, 0, 32, 32);
  }

  function _drawLayer(key, cam, W, H) {
    const img = imgs[key];
    const cfg = ENV_CONFIG.layers[key];
    if (!img || !img.naturalWidth || !cfg) return;
    const iw = img.naturalWidth, ih = img.naturalHeight;
    const sc = Math.max(W / iw, H / ih) * cfg.scale;
    const sw = Math.ceil(iw * sc), sh = Math.ceil(ih * sc);
    const par = cfg.parallax * ENV_CONFIG.parallaxStrength;
    const drift = ENV_CONFIG.ambientDrift;

    // Motion = actual camera world-position * depth + independent ambient drift.
    // (NOT Date.now()*speed. Camera pos reflects real ship velocity integrated;
    //  ambient drift is the small allowed time component that keeps gas alive.)
    let offX = -(cam.x * par) + cfg.driftX * drift * _driftT;
    let offY = -(cam.y * par) + cfg.driftY * drift * _driftT;

    const ph = _PHASE[key] || 0;
    const alpha = Math.max(0, cfg.alpha + cfg.breathe * Math.sin(_driftT * cfg.breatheSpd * 2 * Math.PI + ph));
    ctx.globalAlpha = alpha;
    ctx.globalCompositeOperation = cfg.blend;

    if (!cfg.tile) {
      // Single oversized centered copy — used for the opaque base whose edges do
      // not tile. Coverage margin (scale) far exceeds its tiny parallax excursion,
      // so a seam can never enter the viewport.
      ctx.drawImage(img, W / 2 - sw / 2 - cam.x * par, H / 2 - sh / 2 - cam.y * par, sw, sh);
    } else {
      offX = ((offX % sw) + sw) % sw;
      offY = ((offY % sh) + sh) % sh;
      for (let x = offX - sw; x < W + sw; x += sw)
        for (let y = offY - sh; y < H + sh; y += sh)
          ctx.drawImage(img, x, y, sw, sh);
    }
  }

  function _drawStars(cam, W, H) {
    const S = ENV_CONFIG.stars, SS = S.spread, ti = S.twinkleIntensity, t = _driftT;
    _ensureGlow();
    ctx.globalCompositeOperation = 'lighter';
    for (const s of stars) {
      const tier = S.tiers[s.ti];
      const par = tier.parallax;
      const sx = (((s.wx - cam.x * par) % SS) + SS) % SS - SS / 2 + W / 2;
      const sy = (((s.wy - cam.y * par) % SS) + SS) % SS - SS / 2 + H / 2;
      if (sx < -6 || sx > W + 6 || sy < -6 || sy > H + 6) continue;
      // Asynchronous twinkle: unique phase AND rate per star -> the sky as a whole
      // never brightens or dims together.
      const tw = tier.twAmp * ti * Math.sin(t * s.hz * 2 * Math.PI + s.phase);
      ctx.globalAlpha = Math.max(0.05, tier.baseAlpha + tw);
      if (tier.glow && s.r > 1.3) {
        const gsz = s.r * 6;
        ctx.drawImage(_glow, sx - gsz / 2, sy - gsz / 2, gsz, gsz);   // cached sprite, no gradient alloc
        ctx.fillStyle = s.col;
        ctx.fillRect(Math.round(sx), Math.round(sy), 1, 1);           // crisp core
      } else {
        ctx.fillStyle = s.col;
        const pr = Math.max(1, Math.round(s.r));
        ctx.fillRect(Math.round(sx - pr / 2), Math.round(sy - pr / 2), pr, pr);
      }
    }
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  }

  function _drawParticles(cam, W, H) {
    const P = ENV_CONFIG.particles, SS = P.spread;
    const sp = Math.hypot(cam.vx || 0, cam.vy || 0);
    _camVel = sp;
    ctx.globalCompositeOperation = 'lighter';
    for (const p of particles) {
      const tier = P.tiers[p.ti];
      const par = tier.parallax;
      const sx = (((p.wx - cam.x * par) % SS) + SS) % SS - SS / 2 + W / 2;
      const sy = (((p.wy - cam.y * par) % SS) + SS) % SS - SS / 2 + H / 2;
      if (sx < -8 || sx > W + 8 || sy < -8 || sy > H + 8) continue;
      ctx.globalAlpha = tier.alpha;
      // Only the nearest tier streaks, only under boost, capped short — not hyperspace.
      if (tier.streak && cam.boosting && sp > 0.5) {
        const len = Math.min(14, sp * par * 2.2 * P.boostResponse);
        const ux = -cam.vx / sp, uy = -cam.vy / sp;
        ctx.strokeStyle = tier.color;
        ctx.lineWidth = Math.max(1, p.size);
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + ux * len, sy + uy * len);
        ctx.stroke();
      } else {
        ctx.fillStyle = tier.color;
        ctx.fillRect(sx, sy, p.size, p.size);
      }
    }
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  }

  function _drawAmbient(W, H) {
    const L = ENV_CONFIG.lighting;
    if (L.strength <= 0) return;
    const b = 1 + L.breatheAmp * Math.sin(_driftT * L.breatheSpd * 2 * Math.PI);
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = Math.max(0, L.baseAlpha * L.strength * b);
    ctx.fillStyle = L.color;
    ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  }

  // Main entry — draws the entire environment behind the world. Called before the
  // world zoom transform in the host, so it is immune to zoom and camera lead
  // (always fills the screen -> no black edges, no stretching, works at all zooms).
  function render(cam) {
    const W = canvas.width, H = canvas.height;
    if (!_lastNow) _lastNow = cam.now;
    let dt = (cam.now - _lastNow) / 1000;
    _lastNow = cam.now;
    if (dt > 0.1) dt = 0.1;        // clamp tab-switch / long-pause spikes
    if (dt < 0)   dt = 0;
    _driftT += dt;
    _ensureVignette(W, H);

    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#05010a';
    ctx.fillRect(0, 0, W, H);

    // Back gas
    _drawLayer('base', cam, W, H);
    _drawLayer('far',  cam, W, H);
    _drawLayer('mid',  cam, W, H);
    // Distant stars sit within the gas so nearer vapor can veil them (depth).
    _drawStars(cam, W, H);
    // Near gas
    _drawLayer('near',  cam, W, H);
    _drawLayer('atmo',  cam, W, H);
    _drawLayer('vapor', cam, W, H);
    _drawLayer('dust',  cam, W, H);   // baked speckle texture (additive)
    // Velocity-responsive procedural particles (nearest environment element)
    _drawParticles(cam, W, H);
    // Restrained ambient blue cast + vignette
    _drawAmbient(W, H);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.fillStyle = _vg;
    ctx.fillRect(0, 0, W, H);
  }

  function stats() {
    const loaded = Object.keys(ENV_CONFIG.layers).filter(k => imgs[k] && imgs[k].naturalWidth).length;
    return { layers: loaded, stars: stars.length, particles: particles.length, camVel: _camVel };
  }

  return { setLayers, initField, render, stats };
}
