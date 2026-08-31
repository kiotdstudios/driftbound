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
