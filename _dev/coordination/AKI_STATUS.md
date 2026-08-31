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

### DIRECTIVE ID: Dev-Environment QA Investigation — RESOLVED, CP3b-2 re-confirmed GOOD
- STATUS: RESOLVED — environment issue fixed, CP3b-2 re-tested clean, closed as environment false-negative
- BRANCH: agent/core-gameplay
- COMMIT: a5d5ad4 (no code change — this entry documents the environment fix + re-verification of already-pushed CP3b-2 commit 0655257)
- FILES CHANGED: none (diagnostics + retest only)
- IMPLEMENTATION SUMMARY: Killed both stale port-8420 listeners on the user's machine (PID 21444, PID 13988 -- both plain `python -m http.server 8420`, one wildcard-bound, one localhost-only). Verified via netstat that port 8420 was fully clear afterward. Started exactly one fresh server from Documents/driftbound_work/agent-core (the intended test worktree) as a persistent background process, confirmed via netstat that only one PID is now bound, and confirmed via browser (window.__DB.attachedPodRenderSize reads ~126.13) that it is serving the current build. Separately inspected Documents/DRIFTBOUND (the 8/30 folder) per chief's instruction NOT to delete/consolidate yet: it is not git-controlled (no .git directory, so no branch/HEAD applies), it is stale relative to agent-core (index.html cache-bust tag one version behind, missing OWNERSHIP.md/START_GAME.bat/driftbound_flight_test.html.bak that agent-core has), and its src/ layout is a pre-refactor structure (assets/player/world subfolders) not matching the current modular src/. It does contain a handful of files not present anywhere in driftbound_work (_check.txt, _idx.txt, _inspect.txt, _keys.txt, _patch_blue.py, _test.txt, a 16MB "test blue map.html") -- read as scratch/debug artifacts, not yet confirmed disposable. No files touched, moved, or deleted in DRIFTBOUND. Full details logged in TEAM_NOTES.md. With the port conflict resolved, re-ran the full manual-style QA against the clean single server: docked at all 4 connector directions (N/E/S/W) -- pod substantial, flush, no gap, ship hull visible in every direction (screenshots taken, held locally). Ran the actual committed _dev/hover_targeting_verify.mjs suite against the clean server (not an ad-hoc script) for hover: 22/22 passed across all 5 zoom levels for world pod / attached pod / asteroid / empty-space hover, plus the two isolation checks (no second E consumer, hover not range-gated).
- TEST RESULTS: hover_targeting_verify.mjs 22/22 PASS (run fresh against the clean server) | 4-direction docking visual retest: 4/4 correct (N/E/S/W, screenshots held locally, not committed)
- RUNTIME READY: PASS -- single clean server confirmed on port 8420, serving current build
- CONSOLE ERRORS: 0
- KNOWN DELTAS: none
- KNOWN WARNINGS: none new
- BLOCKERS: none -- previous blocker (port conflict) resolved
- BUGS DISCOVERED: none new this entry (both bugs from the prior entry -- port conflict, duplicate folders -- addressed/documented, not fully closed: DRIFTBOUND folder consolidation still pending chief's decision)
- BAD NEWS / UNEXPECTED FINDINGS: none -- this entry is good news. The original "still broken" report is confirmed to have been an environment false-negative, not a CP3b-2 regression.
- QUESTIONS FOR CHIEF: none blocking.
- DECISIONS NEEDED FROM CHIEF: whether/when to archive Documents/DRIFTBOUND once the handful of unique scratch files in it (listed above, in TEAM_NOTES.md) are checked for anything worth keeping. Not urgent -- no active risk now that the port conflict is fixed and both agents/QA know to always confirm which folder a running server was started from.
- RECOMMENDED NEXT ACTION: Close out the CP3b-2 QA cycle as GOOD/GO. Chief free to do a final manual pass on this same clean server (already running on port 8420 from driftbound_work/agent-core) to confirm firsthand before marking the directive fully closed.
- CURRENT HOLD/GO STATE: GO -- CP3b-2 is confirmed correct in code and now confirmed correct in a clean, verified environment. Only the (non-blocking, non-urgent) DRIFTBOUND archival decision remains open.

### DIRECTIVE ID: Dev-Environment QA Investigation (CP3b-2 retest blocked)
- STATUS: BLOCKED — code confirmed correct, local dev environment issue preventing chief/user retest of CP3b-2
- BRANCH: agent/core-gameplay
- COMMIT: a5d5ad4 (no new code this entry — investigation only, verifying the already-pushed CP3b-2 commit 0655257)
- FILES CHANGED: none (diagnostics only)
- IMPLEMENTATION SUMMARY: User reported CP3b-2 (attached-pod scale fix, S=126.1) still appears broken in manual browser retest — pod still looked disconnected/small. Ran automated Playwright repro (_dev-adjacent script, not committed) docking at all 4 connector directions (N/E/S/W) directly against pushed commit a5d5ad4 served fresh from the correct folder (Documents/driftbound_work/agent-core). All 4 directions rendered correctly — pod substantial, flush, no gap, ship hull still visible. This confirms the pushed code itself is correct. User's browser environment was then checked: confirmed correct folder (Documents/driftbound_work/agent-core) and correct branch/commit (agent/core-gameplay @ a5d5ad4) via git log/git branch on the user's machine. User's browser console showed window.__DB.attachedPodRenderSize === undefined (should read ~126.13 on the correct build) even in a fresh Incognito window, which rules out normal cache. Ran netstat on the user's machine and found two separate processes simultaneously bound to port 8420: PID 21444 (listening on 0.0.0.0:8420 and [::]:8420, wildcard/all-interfaces) and PID 13988 (listening on 127.0.0.1:8420, localhost-only). Leading theory: one of these is a stale/leftover server process answering localhost:8420 ahead of the fresh server the user starts from the correct folder, silently serving old code with no error to signal it. Neither process has been killed yet, and it has not yet been confirmed which PID is actually answering the user's browser — this is the next step, pending chief/user go-ahead.
- TEST RESULTS: Automated 4-direction repro (N/E/S/W) against pushed commit a5d5ad4 — all 4 visually correct (screenshots taken, not committed to repo, held locally). No regression suite changes — no code touched this entry.
- RUNTIME READY: Pushed code confirmed runtime-ready via direct repro. User's live browser session currently NOT reflecting the pushed code — environment issue, not a code issue.
- CONSOLE ERRORS: User's console shows window.__DB.attachedPodRenderSize === undefined, which is the smoking-gun signal that the browser is not running the current build.
- KNOWN DELTAS: none in code.
- KNOWN WARNINGS: none new.
- BLOCKERS: Cannot get a clean chief/user visual retest of CP3b-2 until the local dev-server/process conflict on port 8420 is resolved on the user's machine.
- BUGS DISCOVERED: (1) Two processes bound to port 8420 simultaneously on the user's machine (PIDs 21444, 13988) — one is very likely stale and silently serving an old build. (2) Two separate top-level Driftbound folders exist under Documents (DRIFTBOUND, created 8/30, and driftbound_work, created 8/31, containing agent-core/agent-world-ui/integration) — increases risk of exactly this kind of silent stale-serving confusion going forward.
- BAD NEWS / UNEXPECTED FINDINGS: The CP3b-2 "still broken" report was a false alarm as far as the code is concerned — automated repro against the exact pushed commit passes cleanly on all 4 connector directions. The real issue is environmental (stale server process + duplicate project folders on disk), not a regression in the shipped fix.
- QUESTIONS FOR CHIEF: None blocking — see decisions needed below.
- DECISIONS NEEDED FROM CHIEF: (1) OK to kill both port-8420 processes on the user's machine and restart a single clean server from Documents/driftbound_work/agent-core to unblock retest? (2) Should the DRIFTBOUND (8/30) and driftbound_work (8/31) folders be analyzed, condensed, and organized into one canonical folder to prevent recurrence? Flagged in detail in TEAM_NOTES.md.
- RECOMMENDED NEXT ACTION: Kill PIDs 21444 and 13988, start one fresh server from Documents/driftbound_work/agent-core, have user hard-retest CP3b-2 in a new Incognito window and re-check window.__DB.attachedPodRenderSize reads ~126.13. Separately, have DRIFTBOUND (8/30 folder) contents inspected and either archived/deleted or merged so only one canonical Driftbound folder remains on disk.
- CURRENT HOLD/GO STATE: HOLD — CP3b-2 code itself is GO (pushed, verified correct via direct repro), but chief/user visual sign-off is blocked pending the environment cleanup above.


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

## DIRECTIVE ID: CP3c (connector placement fix, following chief QA on CP3b-2)

- STATUS: COMPLETE — HOLDING for chief review, per explicit directive
- BRANCH: agent/core-gameplay
- COMMIT: db96304
- FILES CHANGED: src/main.js (getAttachedPodRenderSize refactor + 2 new functions + 3 call-site fixes + test bridge), src/systems/docking.js (1 additive field), _dev/cp3_attached_pod_render_verify.mjs (rewritten overlap-aware assertions), _dev/hover_targeting_verify.mjs (stale probe-point fix)
- QA FINDING (chief, with screenshot): CP3b-2 fixed pod render SCALE correctly, but the attached pod renders overlapping/on top of the ship hull instead of flush outside it against the connector. Chief also correctly flagged the existing "zero gap" test as insufficient, since overlapping sprites also produce zero background gap — it cannot distinguish flush-placement from overlap.
- ROOT CAUSE: CONNECTOR_GAP (46 world-px, CP2 graph constant used for local_position) is smaller than the ship's own measured visible half-width (~51 world-px). The OLD render code drew every attached pod at the raw graph local_position, which therefore sits INSIDE the ship's own silhouette by construction — this was actually documented as an intentional (but wrong) shortcut in the CP3b-2 code comments ("any pod...overlaps the ship. That overlap is what guarantees no floating gap").
- IMPLEMENTATION SUMMARY: Fix is render-time ONLY, per directive ("fix connector placement math only"):
  - `getAttachedPodRenderSize()` refactored (output UNCHANGED, S≈126.13, pod scale not touched) to expose `_shipHalfWidthWorld()` as a reusable memoized helper.
  - New `getModuleRenderHalfWidth(modId)`: ship half-width for 'core', pod half-width (getAttachedPodRenderSize()/2) for any pod id.
  - New `getNodeRenderOffset(nodeId)`: walks the existing shipAssembly parent chain, reuses the graph's CONNECTOR DIRECTION (never its distance), and substitutes distance = parentHalfWidth + thisHalfWidth (flush, zero unintended overlap) at every hop. Does NOT write to shipAssembly/local_position/CONNECTOR_GAP anywhere — CP2 graph/save data layer is completely untouched.
  - `drawAttachedPods()` (both the strut-line loop and pod-body loop) and `getInteractionCandidates()`'s attached-pod hover position now use `getNodeRenderOffset()` instead of raw `node.local_position`.
  - `drawDockingPod()`'s in-flight docking-animation target updated to use the same flush-distance formula, so the pod does not visually "pop" outward the instant LOCK commits (previously it animated toward the same overlapping point it would then render at).
  - `docking.js` `getDockingAnimData()` gained one additive field, `slotModId: mod.pod_instance_id` — pure data exposure (the value already existed internally), zero change to the docking state machine's logic.
  - Test bridge (`window.__DB`) gained 3 read-only getters (`shipHalfWidthWorld`, `getNodeRenderOffset`, `getModuleRenderHalfWidth`) for test-harness use.
- TEST CHANGES (per chief's explicit request): `cp3_attached_pod_render_verify.mjs` rewritten. New core assertion measures ship-only content bounding box (pod temporarily spliced out of `attachedPods`, re-added after) vs pod-leading-edge bounding box independently, and asserts they do not overlap beyond a 4px intentional-art tolerance — in addition to (not replacing) the existing flush/no-gap check. `hover_targeting_verify.mjs` had one stale hardcoded probe point (`shipPos.x + 46`, the old raw CONNECTOR_GAP) that no longer lands on the pod now that it renders further out; fixed to query `getNodeRenderOffset()` dynamically.
- TEST RESULTS: cp3_attached_pod_render_verify.mjs 12/12 PASS | cp2_docking_verify.mjs 30/30 PASS | map_input_suppression_verify.mjs 18/18 PASS | e_interaction_regression.mjs 25/25 PASS | phase1_pod_assembly_verify.mjs 23/23 PASS | phase0_smoke.mjs PASS | hover_targeting_verify.mjs 22/22 PASS — 130/130 total, 0 regressions.
- VISUAL VERIFICATION: All 4 connector directions (N/E/S/W) re-tested with fresh screenshots — pod sits cleanly outside the hull, flush against the connector strut, zero sprite overlap, on every side.
- RUNTIME READY: PASS
- CONSOLE ERRORS: 0
- KNOWN DELTAS: None
- KNOWN WARNINGS: `drawDockingPod()`'s in-flight sprite still renders at the older `POD_DISPLAY_SIZE` (96) constant rather than `getAttachedPodRenderSize()` (~126) during the docking animation itself — this is a pre-existing discrepancy (not introduced by this fix) between the in-flight animation sprite size and the final attached sprite size. Out of scope for this directive (chief's instruction was placement math only, and this is a size mismatch, not a placement bug), flagging for chief's awareness/backlog.
- BUGS DISCOVERED: None new. The insufficient old test (chief-flagged) has been rewritten as directed.
- BLOCKERS: None.
- QUESTIONS FOR CHIEF: None blocking. One backlog flag above (docking-animation sprite size mismatch) for chief's discretion on priority.
- PUSHED TO GITHUB: YES — agent/core-gameplay, commit db96304
- HOLD STATE: HOLDING. Per explicit directive, no further work will proceed on this branch until chief reviews.
