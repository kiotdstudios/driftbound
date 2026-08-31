# AKI_STATUS.md — Aki's Status Log

**Ownership:** This file is owned exclusively by Aki. Only Aki writes checkpoint
entries here. Orcha and Chief may read it, not edit it (this initial skeleton
was created by Orcha only to install the coordination system per Chief
directive COORD-1; all entries from this point forward are Aki's).

Newest entries at the top. Push the status update with or immediately after
your implementation checkpoint commit.

---

## Checkpoint template

```
### DIRECTIVE ID:
- STATUS:
- BRANCH:
- COMMIT:
- FILES CHANGED:
- IMPLEMENTATION SUMMARY:
- TEST RESULTS:
- RUNTIME READY:
- CONSOLE ERRORS:
- KNOWN DELTAS:
- KNOWN WARNINGS:
- PUSHED TO GITHUB:
- QUESTIONS FOR CHIEF:
```


### DIRECTIVE ID: CP3b-2 — Attached-pod render scale rework + mouse hover targeting
- STATUS: COMPLETE — HOLD for chief review
- BRANCH: agent/core-gameplay
- COMMIT: 0655257
- FILES CHANGED: src/main.js (attached-pod scale formula reworked; hover system added), src/systems/hover.js (new), _dev/cp3_attached_pod_render_verify.mjs (rewritten, 10/10), _dev/hover_targeting_verify.mjs (new, 22/22)
- IMPLEMENTATION SUMMARY: Chief QA rejected the prior CP3 fix (S=96 via POD_DISPLAY_SIZE) as still too small/detached, and added a second requirement (mouse hover). Two independent fixes, one commit:

  1. Attached-pod render scale. First attempt (not committed) matched the pod's real visible content half-extent 1:1 to the ship's own — computed S=151.8, but visually swallowed the ship (screenshot + pixel-probe confirmed only ~41% of the ship's own silhouette stayed visible). Reworked getAttachedPodRenderSize() to anchor on CONNECTOR_GAP (the CP2 graph constant, not a sprite pixel count) instead: setting the pod's own visible half-width equal to CONNECTOR_GAP makes the ship's remaining-visible-fraction along the connector axis collapse to exactly 0.5 algebraically, independent of the ship's own actual size. Result: S=126.1 -- substantially bigger than the old rejected 96 (reads as a full module), well short of the 151.8 that swallows the ship. Verified via screenshot (ship hull clearly visible, pod flush with zero gap) and pixel-probe scan (dynamic bounding-box + connector-edge measurement, not a single hardcoded pixel color).

  2. Mouse hover targeting (new file src/systems/hover.js + main.js wiring). resolveHover(worldX, worldY, candidates) is a pure nearest-candidate hit test with zero side effects and zero dependency on main.js. getInteractionCandidates() builds the frame's candidate list from world pods, attached pods, and asteroids (shape documented as extensible for future InteractionTarget-compatible objects). updateHover() runs the full spec'd path every frame: mouse screen position -> camera.screenToWorld() -> world-space point -> resolveHover() -> hoveredTarget, gated by the existing interiorMode early-return in loop(). Hover and interaction range are fully decoupled -- hover has no range concept at all, it only answers "what is the cursor pointing at". Does not touch src/systems/interactions.js (confirmed still the sole E-key resolver) or src/core/camera.js (Orcha-owned, provides screenToWorld/worldToScreen unmodified).

- TEST RESULTS: cp2_docking_verify 30/30, phase1_pod_assembly_verify 23/23, map_input_suppression_verify 18/18, cp3_attached_pod_render_verify 10/10 (rewritten -- now measures live bounding-box/connector-edge geometry instead of hardcoded pixel colors), hover_targeting_verify 22/22 (new -- world pod / attached pod / asteroid / empty-space hover at all 5 zoom levels, plus side-effect-free and no-range-gating checks). phase0_smoke and e_interaction_regression test [6] (pod-interior fade timing) both show a pre-existing flaky failure -- confirmed present on the unmodified baseline commit c224fc2 via git stash + 3x rerun before any of this session's changes were applied, so not a regression from this work.
- RUNTIME READY: yes (flake noted above is baseline-pre-existing, unrelated to timing changes in this diff)
- CONSOLE ERRORS: 0 across all test runs
- KNOWN DELTAS: attached-pod visual scale is now a derived/measured value (126.1px draw size), not a fixed constant -- will shift automatically if CONNECTOR_GAP or the pod/ship sprite assets ever change, per design.
- KNOWN WARNINGS: none new.
- PUSHED TO GITHUB: yes -- agent/core-gameplay only (c224fc2..0655257)
- QUESTIONS FOR CHIEF: none -- holding for review/GO.

---

### DIRECTIVE ID: CP3 — Attached-pod render fix (scale + z-order)
- STATUS: COMPLETE — HOLD for chief review
- BRANCH: agent/core-gameplay
- COMMIT: 1cd7a04
- FILES CHANGED: src/main.js (2 edits), _dev/cp3_attached_pod_render_verify.mjs (new, 6/6)
- IMPLEMENTATION SUMMARY: Manual QA bug (Chief): docked pod rendered too small and offset beside/below the core instead of flush-mounted.
  Root cause was purely render-side, not a docking/graph bug:
  1. drawAttachedPods() used a stale hardcoded sprite size `const S = 52` instead of `POD_DISPLAY_SIZE` (96) used by every other pod render call site (world pods, in-flight docking animation) — pod rendered at ~54% correct scale.
  2. drawAttachedPods(cx, cy) was called BEFORE drawShip(cx, cy, ...) in the render loop. Since CONNECTOR_GAP (46px) places the pod center inside the ship's own visible-sprite radius (~51px), the ship sprite painted over the pod on every frame, leaving only a small sliver visible (read by QA as "offset").
  Fix (main.js only): S = 52 -> S = POD_DISPLAY_SIZE; moved drawAttachedPods(cx, cy) to run immediately after drawShip(cx, cy, now, speed) inside the same world-transform block.
  CP2 docking logic and graph data (local_position, CONNECTOR_GAP, docking.js state machine) were NOT touched — the stored transform was already correct, confirmed by the new test's graph-sanity check. Per directive, docking.js changes were only authorized if the render fix proved the stored transform wrong; it did not, so docking.js is untouched.
  Note on scope: main.js is nominally chief-approval-locked for orchestration changes, but this was a directly chief-commissioned bug-fix directive, so proceeding was in scope. drawAttachedPods/drawShip render pipeline is Aki/Core Gameplay ownership (ship graph/docking), not Orcha's HUD/map/minimap/BG/VFX modules — no Orcha-owned files touched.
- TEST RESULTS: cp3_attached_pod_render_verify 6/6 (new) | cp2_docking_verify 30/30 | map_input_suppression_verify 18/18 | e_interaction_regression 25/25 | phase1_pod_assembly_verify 23/23 | phase0_smoke PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: none — render-order/scale fix only, no behavior change to docking state machine or graph data
- KNOWN WARNINGS: none
- PUSHED TO GITHUB: agent/core-gameplay only (per directive)
- QUESTIONS FOR CHIEF: none — awaiting review/GO on CP2-final + this CP3 render fix together

---

### DIRECTIVE ID: A2 / CP2-final — Safe release on mid-dock invalidation
- STATUS: COMPLETE (final safety correction)
- BRANCH: agent/core-gameplay
- COMMIT: d587b4f
- FILES CHANGED: src/systems/docking.js (3 edits), _dev/cp2_docking_verify.mjs (+4 tests, 30/30)
- IMPLEMENTATION SUMMARY: If _getPod(), _getMod(), or _getConn() becomes null during an active dock, the system now routes through _safeRelease() instead of calling raw _reset().
  Problem: Two sites called _reset() directly on null-lookup failure — updateDocking() (per-tick validity check, added new) and _commitDock() null guard. This abandoned any reserved ore and left the connector in 'reserved' state forever.
  Fix (3 edits to docking.js):
  1. Added _safeRelease() private function: restores _s.reservedOre to ship.ore (if > 0), frees the connector if still in 'reserved' state (conn.free=true, conn.state='free'), then calls _reset(). Safe to call from any phase; does not depend on isDocking() being true.
  2. updateDocking() validity guard (new): at the top of every tick, if _getPod()||_getMod()||_getConn() returns null while isDocking(), call showToast('DOCKING ABORTED') + _safeRelease() and return. Handles the case where an external system removes a pod, module, or connector mid-animation.
  3. _commitDock() null guard: was calling _reset() directly. Now calls showToast + _safeRelease(). Also moved _s.phase = DOCK_STATE.COMPLETE assignment to AFTER the null check, so COMPLETE is only set when all refs are confirmed valid.
- TEST RESULTS: cp2_docking_verify.mjs 30/30 PASS (+4 new: mid-dock invalidation ore restored, connector freed, graph not mutated, phase IDLE) | map_input_suppression_verify.mjs 18/18 PASS | e_interaction_regression.mjs 25/25 PASS | phase1_pod_assembly_verify.mjs 23/23 PASS | phase0_smoke.mjs PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: None
- PUSHED TO GITHUB: YES — 78de4d0..d587b4f → agent/core-gameplay
- QUESTIONS FOR CHIEF: None — HOLDING for next directive

---

### DIRECTIVE ID: A2 / CP2 — REWORK PASS 2 (ore reservation model)
- STATUS: COMPLETE (rework 2)
- BRANCH: agent/core-gameplay
- COMMIT: 28fe949
- FILES CHANGED: src/systems/docking.js (6 targeted edits), _dev/cp2_docking_verify.mjs (+4 tests)
- REWORK SUMMARY: Ore reservation model — available/reserved/consumed semantics implemented per directive requirement.
  Problem: _s had no reservedOre field. abortDocking() refunded the bare POD_ATTACH_COST constant rather than the actual reserved amount. No reservation ledger was exposed in getDockingState().
  Fix (6 edits to docking.js only):
  1. Added _s.reservedOre: 0 to state — tracks ore moved from available to reserved at ALIGNING start.
  2. getDockingState() now exposes reservedOre in its snapshot.
  3. startDocking(): after ship.ore -= POD_ATTACH_COST, sets _s.reservedOre = POD_ATTACH_COST. Comment documents the available→reserved transition.
  4. abortDocking(): refunds ship.ore += _s.reservedOre (exact reserved amount) and clears _s.reservedOre = 0. Not the constant — the ledger.
  5. _commitDock(): clears _s.reservedOre = 0 before _reset(). Ore was already removed from ship.ore at reservation; clearing the ledger marks it consumed.
  6. _reset(): includes _s.reservedOre = 0.
  Model: ship.ore = available ore (decremented at ALIGNING). _s.reservedOre = amount earmarked for this dock. On abort: available += reserved, reserved = 0. On commit: reserved = 0 (consumed — available already reduced at start).
- TEST RESULTS: cp2_docking_verify.mjs 26/26 PASS (+4 new: reservedOre==cost during ALIGNING, available+reserved==pre-dock total, reservedOre==0 after commit, reservedOre==0 after abort) | map_input_suppression_verify.mjs 18/18 PASS | e_interaction_regression.mjs 25/25 PASS | phase1_pod_assembly_verify.mjs 23/23 PASS | phase0_smoke.mjs PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: None
- PUSHED TO GITHUB: YES — agent/core-gameplay @ 28fe949
- QUESTIONS FOR CHIEF: None. Holding for chief's verdict.

### DIRECTIVE ID: A2 / CP2 — REWORK PASS
- STATUS: COMPLETE (rework)
- BRANCH: agent/core-gameplay
- COMMIT: cb0446d
- FILES CHANGED: src/systems/docking.js (rewritten), src/main.js (2-line field rename in drawDockingPod only — no logic change). Zero new code touched outside docking.js.
- REWORK SUMMARY: Two architecture issues fixed per chief REWORK verdict:
  1. RAW REFS → STABLE IDs: _s.pod and _s.slot were raw JS object references, violating the directive requirement "use stable IDs, not authoritative raw object references." Replaced with _s.podPid (string), _s.slotModId (string), _s.slotConnId (string). Added _getPod()/_getMod()/_getConn() helpers that look up fresh from context getters at every use site. No cached object refs remain in module state.
  2. MISSING STATES: DOCK_STATE enum was missing COMPLETE and ABORTING, violating the directive-specified state machine. Full machine now implemented: IDLE→ALIGNING→PULLING_IN→LOCKING→COMPLETE plus ABORTING. abortDocking() transits through ABORTING before resetting to IDLE; _commitDock() transits through COMPLETE before resetting to IDLE. isDocking() explicitly enumerates the three animation phases (ALIGNING, PULLING_IN, LOCKING) only — COMPLETE and ABORTING are not "active docking."
- TEST RESULTS: cp2_docking_verify.mjs 22/22 PASS | map_input_suppression_verify.mjs 18/18 PASS | e_interaction_regression.mjs 25/25 PASS | phase1_pod_assembly_verify.mjs 23/23 PASS | phase0_smoke.mjs PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: None
- PUSHED TO GITHUB: YES — agent/core-gameplay @ cb0446d
- QUESTIONS FOR CHIEF: None. Holding for chief's verdict.

### DIRECTIVE ID: A2 / CP2
- STATUS: COMPLETE
- BRANCH: agent/core-gameplay
- COMMIT: 76a0f84
- FILES CHANGED: src/systems/docking.js (NEW), src/main.js (11 targeted edits), _dev/cp2_docking_verify.mjs (NEW), _dev/e_interaction_regression.mjs (waitForDock compat), _dev/phase1_pod_assembly_verify.mjs (waitForDock compat)
- IMPLEMENTATION SUMMARY: Physical docking state machine extracted into src/systems/docking.js. Replaces the instant-attach in tryClaimWorldPod with a staged IDLE→ALIGNING (500ms)→PULLING_IN (900ms)→LOCKING (350ms)→IDLE sequence (~1.75s total). Connector selection by approach direction via findBestConnector() (dot product of ship-local connector world vectors vs pod approach vector). Resources (ore) and connector reserved at ALIGNING start; graph mutation (shipAssembly update) happens only at LOCK commit — per DECISIONS.md rule #6. X key during docking cancels (refunds ore, frees connector), not brakes. drawDockingPod() renders animated pod in-flight between drawWorldPods and drawAttachedPods. Save safety by construction: pod stays in worldPods until LOCK commit, so saveGame() during ALIGNING/PULLING_IN serializes it as uncollected. Dev panel X key description is context-sensitive (shows "Cancel Docking" during active docking). Full __DB bridge added.
- TEST RESULTS: cp2_docking_verify.mjs 22/22 PASS | map_input_suppression_verify.mjs 18/18 PASS | e_interaction_regression.mjs 25/25 PASS | phase1_pod_assembly_verify.mjs 23/23 PASS | phase0_smoke.mjs PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: None
- PUSHED TO GITHUB: YES — agent/core-gameplay
- QUESTIONS FOR CHIEF: None. CP2 complete. Holding for next directive per protocol.

## Retroactive entry (logged by Orcha/Chief for continuity — predates this system)

### DIRECTIVE ID: A1a
- STATUS: INTEGRATED
- BRANCH: agent/core-gameplay
- COMMIT: 79939be (integrated into refactor/modular-core)
- FILES CHANGED: src/main.js, index.html, _dev/map_input_suppression_verify.mjs (new)
- IMPLEMENTATION SUMMARY: Root cause — outer thrust guard `if (!braking)` in update() was not also checking `_mapOpen`, so W/S/D/ArrowUp/Down/Right kept accelerating the ship while the regional map was open (only A/ArrowLeft had a per-line guard). Fixed by changing the outer guard to `if (!braking && !_mapOpen)` and removing the now-redundant per-line guard. Added `window.__DB.mapOpen` getter/setter and dbgAX/dbgAY bridge fields for test observability.
- TEST RESULTS: _dev/map_input_suppression_verify.mjs — 18/18 PASS
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: None
- PUSHED TO GITHUB: Integrated locally into refactor/modular-core; pushed to origin as part of COORD-1 checkpoint (this was not yet pushed at time of the A1a commit itself — flagged to Chief).
- QUESTIONS FOR CHIEF: None on record.

Aki: please confirm/correct the above retroactive entry and use the template for all future checkpoints.
