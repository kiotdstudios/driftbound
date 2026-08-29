# DRIFTBOUND — Dev Log
> Auto-updated by Orcha. Any agent working on this project should read this first.
> Main file: `driftbound_flight_test.html` | Location: `C:\Users\diepowel\Documents\DRIFTBOUND\`
> Serve: `python -m http.server 8420` from DRIFTBOUND folder
> Repo: https://github.com/kiotdstudios/driftbound (auto-deploys to Render ~2min)
> Scratch/patch scripts: `_dev/` subfolder — do NOT clutter root

---

## Folder Structure
```
DRIFTBOUND/
  driftbound_flight_test.html     ← main game file
  driftbound_flight_test.html.bak ← last known good backup
  driftbound_server.py            ← local WS multiplayer server
  driftbound_agent_context.json   ← agent context/state
  Driftbound_Game_Design_Document_v1.docx  ← GDD
  Ditharts_Free_Scifi_Tileset_v01/         ← interior tileset (extracted)
  Ditharts_Free_Scifi_Tileset_v01.zip
  DEVLOG.md                       ← this file
  SHIP_STATS.md
  pod_sprites/                    ← ship directional sprites
  Demo_assets/                    ← planets, asteroids
  vapor_bg/                       ← background layers
  mockups/
  _dev/                           ← ALL scratch/patch/audit scripts live here
```

---

## Current Build Constants (v0.6 — 2026-08-29)
| Constant | Value | Notes |
|---|---|---|
| NORMAL_MAX | 0.65 | cruise speed cap |
| BOOST_MAX | 5.28 | boost speed cap (Shift) |
| THRUST | 0.126 | accel/frame cruise (-30% from 0.18) |
| BOOST_THRUST | 0.294 | accel/frame boost (-30% from 0.42) |
| BOOST_RAMP_UP | 0.022 | ~45 frames to full boost |
| BOOST_RAMP_DOWN | 0.006 | ~167 frames coast-down |
| FRICTION | 0.984 | inertia |
| FUEL_CAPACITY | 10 | gallons |
| SHIP_MAX_HP | 100 | hull points |

---

## Session Log

### v0.1 — Base prototype
- Single HTML file, no build step
- Pod sprite 8-dir (68×68px), 9-frame flying animation
- void_01 parallax background (3 layers)
- WASD/Arrow movement with inertia
- HUD: SPD, DIR, POS, mini compass

### v0.2 — Fuel, Polish, Background Switcher
- Fuel system: 10 gal tank, segmented gauge
- 20 background maps (`[`/`]` cycle)
- HUD unified to canvas (DOM removed)

### v0.3 — Nebula Animation + Boost System
- Per-layer nebula drift (vx/vy/wave)
- Two-tier speed: NORMAL_MAX / BOOST_MAX
- Exponential fuel burn at high speed

### v0.4 — Debug System
- F1 toggle debug overlay (FPS, particles, ship state, input log)

### v0.5 — Speed Fix + Boost Feel + HUD Readability
- Speed bug fixed (dead else-if branch)
- wasBoost flag for graceful speed bleed
- HUD panel opacity/border polish

### v0.6 — Acceleration Tuning + Fuel Burn Animation + HUD Fixes (2026-08-29)
- THRUST and BOOST_THRUST reduced 30%
- Fuel gauge flame animation when boosting (per-segment flicker, glow, exhaust spark)
- Pod sprite fixed: was drawing ship spritesheet as pod, now draws glowing hexagon
- HUD panel height (panelH) rewritten with precise per-row accounting — no more overflow
- 114 scratch/patch files moved to `_dev/`, root cleaned

---

## Known Issues
- Tile seams faintly visible on some backgrounds during fast movement (non-critical, pulseAmp=0 is the mitigation)
- DEVLOG constants were stale after v0.6 acceleration patch — corrected above

---

## GDD Production Order Status (Section 16)
- [x] 1. Lock movement scale, sprite size, tile size, camera
- [x] 2. Prototype exterior salvage area
- [x] 3. Interaction + inventory + 3 resources
- [x] 4. Crafting for repair/docking component
- [x] 5. Pod discovery + docking
- [ ] **6. One abandoned pod with hostile encounter** ← IN PROGRESS
- [ ] **7. Pod secured state gating docking**
- [ ] **8. Attached pod becomes seamless walkable room** ← NEXT BUILD TARGET
- [ ] 9. Functional reward inside it (Armory)
- [ ] 10. Enemies, regions, story, progression

## Next Build: Interior System (GDD Step 8)
- Press `[E]` near attached pod → fade to interior canvas view
- Render pod room using Ditharts_Free_Scifi_Tileset_v01 (64×64px tiles)
- Room layout: floor tiles + wall border + door/hatch
- `[E]` at door/hatch → fade back to exterior
- Tileset location: `Ditharts_Free_Scifi_Tileset_v01/texture/upscaled/free_scifi_tileset_64x64.png`
- Tile size: 64×64px | Sheet: 512×960 (8 cols × 15 rows = 120 tiles)
