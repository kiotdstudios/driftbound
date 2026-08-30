# DRIFTBOUND — Modular Core Refactor Plan

Branch: `refactor/modular-core` (branched from `main` @ d295fa3, the known-good build).
Rule: REFACTOR ONLY. No gameplay/balance/asset/save changes. Preserve behavior exactly.
`main` stays the known-good fallback. Do not merge until live approval.

## Loop contract (main.js orchestrates, does not own logic)
updateInput() -> updatePlayer() -> updateWorld() -> updateInteractions()
-> updateCamera() -> renderBackground() -> renderWorld() -> renderHUD()

## Single ownership map
- input      -> src/core/input.js       (all keydown/keyup; modules query, never listen)
- camera     -> src/core/camera.js       (camX/camY/zoom, lead, shake)
- game loop  -> src/core/gameLoop.js
- state      -> src/core/state.js        (one explicit GameState)
- background -> src/render/background.js  (parallax, nebula layers)
- hud        -> src/render/hud.js         (always begins in screen space)
- minimap    -> src/render/minimap.js
- effects    -> src/render/effects.js
- renderer   -> src/render/renderer.js
- asteroids  -> src/world/asteroids.js
- pods       -> src/world/pods.js
- resources  -> src/world/resources.js
- sector     -> src/world/sector.js
- ship       -> src/player/ship.js
- movement   -> src/player/movement.js
- damage     -> src/player/damage.js
- mining     -> src/systems/mining.js
- interactions -> src/systems/interactions.js  (the single [E] resolver)
- map        -> src/systems/map.js
- save       -> src/systems/save.js
- devTools   -> src/systems/devTools.js         (DevLog + cheats)
- assets     -> src/assets/assetLoader.js        (paths/manifest; request IDs not paths)

## Canvas safety
Render modules own+restore ctx state (save/restore). HUD always begins in screen space.
No module leaves transform/alpha/clip/font/shadow/alignment active for another.

## Known coupling risks (must handle during extraction)
1. Inline HTML on*= handlers reference script-scope fns: lobbyConnect (4593/4600/4602),
   showToast (4607). Under module scope these break -> bound to window in Phase 0.
2. Two <script> blocks currently SHARE scope: the tail block (canvas mousedown shoot +
   DOMContentLoaded lobby prefill) reads canvas/interiorMode/weapon/ARMORY_MAP/projectiles/
   TILE/iPlayerX/iPlayerY/PROJ_SPEED/PROJ_LIFE/SHOOT_CD from the main block. Merged into
   one main.js in Phase 0; split out with the owning systems later.
3. Pervasive global-scope coupling: hundreds of top-level const/let/function share script
   scope. Extraction must thread state via imports / GameState, not accidental globals.
4. Test bridge: ALL existing _dev/*.mjs regression tests read/write module-scoped vars via
   page.evaluate(()=>ship) etc. Under module scope these break. Phase 0 exposes a read/write
   debug bridge on window.__DB so tests migrate to keyboard/click drive + __DB reads.

## Migration order (one at a time: run -> live test -> compare -> commit+push after EACH)
0. FOUNDATION: index.html thin shell + src/main.js (all JS verbatim, module), window bindings,
   window.__DB bridge. driftbound_flight_test.html kept as reference until modular build passes.
1. DevLog / dev tools -> src/systems/devTools.js
2. Input             -> src/core/input.js
3. Camera            -> src/core/camera.js
4. Background renderer-> src/render/background.js
5. HUD / minimap     -> src/render/hud.js, minimap.js
6. Asset loader      -> src/assets/assetLoader.js
7. Asteroids / mining-> src/world/asteroids.js, src/systems/mining.js
8. Player movement   -> src/player/ship.js, movement.js, damage.js
9. Pod systems       -> src/world/pods.js
10. Map              -> src/systems/map.js
11. Save / persistence-> src/systems/save.js

## Acceptance gate (must match known-good pre-refactor build)
ship movement, boost, zoom, mining, HUD, minimap, map, assets load, background/parallax,
dev cheats, save/load ALL identical; zero uncaught exceptions; RUNTIME READY: PASS.
