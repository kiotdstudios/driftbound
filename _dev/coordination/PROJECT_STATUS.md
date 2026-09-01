# PROJECT_STATUS.md

_Last updated: 2026-08-31 — Integration Pass 05._

**See also `TEAM_NOTES.md`** for cross-agent findings, architecture notes,
and test-harness quirks discovered during recent work that don't belong to
a single directive (e.g. the merge-integrity checklist used for Integration
Pass 03, and the full root-cause writeup of the `waitForDock()` race).

## Approved integration HEAD
**APPROVED INTEGRATION HEAD: `8982d91`** (pending final coordination-doc
commits this pass — see INTEGRATION_QUEUE.md for the exact final SHA
reported to Chief).

`refactor/modular-core` @ `8982d91`. Integration Pass 05 merged two
Chief-approved lineages on top of Integration Pass 04's baseline (`3b7d85b`,
itself Pass 04's `cd1a6cf` plus a documentation-only Orcha check-in):
1. `agent/core-gameplay @ a2bf48f` (Aki — Cycle 04: hoveredTarget API
   contract verification + cargo cap enforcement fix, merge commit `687e503`)
2. `agent/world-ui @ 840eb66` (Orcha — cargo-bar overflow clamp, visible
   hover presentation, and the corrected cargo-limit display fix, merge
   commit `8982d91`)

Both merges were clean (`git merge --no-ff`, zero conflicts reported by
git). See `INTEGRATION_QUEUE.md` for the full itemized record.

## Integration status
**INTEGRATION PASS 05 — COMPLETE.** Cargo cap enforcement (Aki),
hoveredTarget API verification (Aki), cargo-bar overflow clamp (Orcha),
visible hover presentation (Orcha), and the cargo-limit double-count
display correction (Orcha) are all integrated. Both merges auto-merged
with zero conflicts (the two branches touched disjoint regions of
`src/main.js` and different files elsewhere — verified before merging by
inspecting each branch's diff stat). Full merge-integrity checklist run
(dupe-declaration scan: 0 duplicate top-level functions across 76, 0
duplicate top-level const/let across 147; draw order and update order
both confirmed unchanged). Combined regression suite (13 named suites,
~330 individual assertions) run sequentially against the merged build —
**zero failures across every suite**, including the two tests
(`phase0_smoke`, `e_interaction_regression`) that had previously shown
documented environment-timing flakes on isolated branch checkpoints; no
flake reproduced this pass (clean machine, no accumulated background
processes). Nothing to classify as a known-flake exception this pass —
noting the absence explicitly since environment cleanliness materially
affects these two tests' pass rate (see `DECISIONS.md` #13).

**PARALLEL CYCLE 04 — CLOSED.** A3 (Aki, mining extraction) was
superseded by the higher-priority cargo cap enforcement bug found during
verification of the same cycle. W3 (Orcha, dev-controls extraction) was
superseded by two rounds of Chief QA display fixes on the same HUD
surface. Neither A3 nor W3 as originally scoped was executed this cycle;
both remain candidates for a future directive if still desired.

## Active branches
- `refactor/modular-core` — integration branch (this file's home). Local
  worktree: `integration/`. Head: `8982d91` (pending final doc commits).
- `agent/core-gameplay` — Aki. Worktree: `agent-core/`. Head: `a2bf48f` (integrated).
- `agent/world-ui` — Orcha. Worktree: `agent-world-ui/`. Head: `840eb66` (integrated).
- `main` — untouched by current work.

## Active directives
See `CHIEF_DIRECTIVES.md`. Parallel Cycle 04 is CLOSED (superseded by QA
fixes, see above). No new directive is currently `STATUS: GO`. Both
feature branches and the integration worktree HOLD pending Chief's next
directive. Per this pass's explicit instruction, no new features were
started.

## Completed systems
- Regional map overlay extraction (`src/render/map.js`)
- Minimap extraction (`src/render/minimap.js`) — W1
- Map-open propulsion suppression fix — A1a
- Connector/assembly graph (pod attach/dock, mass/accel/fuel multipliers)
- HUD layout (multi-resolution verified)
- HUD module extraction (`src/render/hud.js`) — W2 (INTEGRATED)
- Camera system (zoom, lead, round-trip world↔screen)
- E-action interaction resolver (mine / attach pod / enter pod interior)
- CP2 Physical Docking state machine (`src/systems/docking.js`) — A2 (INTEGRATED)
- CP3–CP3e attached-pod scale, hover targeting, per-axis core/pod hull
  extents, and multi-pod connector continuity (INTEGRATED)
- hoveredTarget API contract verified + documented (world_pod/attached_pod/
  asteroid, real DOM mouse events, never gates E) — Aki (INTEGRATED)
- Cargo cap enforcement fix: `getCargoLimit()` replaces stale `CARGO_LIMIT`
  const in every enforcement path (pickup, dev-cheat, wreck recovery,
  diagnostics denom) so the cap correctly rises when pods attach — Aki
  (INTEGRATED)
- HUD cargo bar: overflow fill clamp `[0,1]` so the bar never draws past
  its own bounds regardless of data — Orcha (INTEGRATED)
- HUD cargo bar: corrected cargo-limit display to read
  `ship.shipType.cargoLimit` exactly once (previously double-counted
  attached-pod bonuses on top of the already-updated authoritative value)
  — Orcha (INTEGRATED)
- Visible hover presentation: dashed highlight ring + concise type label
  for world pods / attached pods / asteroids, reading Aki's `hoveredTarget`
  purely for display, granting no interaction range — Orcha (INTEGRATED)

## Systems in progress
*(none currently — Parallel Cycle 04's A3/W3 closed without execution,
see Integration status above. No new directive is STATUS: GO.)*

## P0 / P1 / P2 defects
- **P0:** None open.
- **P1:** None open.
- **P2:** None open.

## Known stale/flaky tests
- **Integration Pass 05 note:** `phase0_smoke.mjs` and
  `e_interaction_regression.mjs` — both previously documented as
  environment-timing-sensitive (see entries below) — passed 100% clean
  this pass (`boosted: true`, 25/25) with no flake reproduced, on a
  freshly cleaned machine (no accumulated background Chromium/Node
  processes before the run). This is consistent with, not contradictory
  to, the existing documented pattern: these two tests' pass rate tracks
  host CPU contention, not code correctness. Not re-classifying them as
  fixed — the underlying timing sensitivity is unchanged — just recording
  that this pass had nothing to classify as an exception.
- `phase0_review_verify.mjs` has one pre-existing stale assertion
  (`cheat_resources` presses `KeyR`, but the dev cheat was rebound to
  `KeyG` in commit `3a952e3`, before this pass) — confirmed via `git log`
  that the test file predates the rebind and the live `DEV_COMMANDS` map
  no longer includes `KeyR`. Not in scope for either branch this pass
  (neither Aki nor Orcha touched this file); candidate for a future
  test-harness cleanup directive.
- `phase0_saveload_verify.mjs`'s fixed 70s wall-clock wait for
  `tickAutoSave()`'s 1800-frame counter can fail ("save fired... false")
  under sustained frame-rate degradation, since the counter is
  frame-based, not wall-clock-based. Confirmed via `git stash` isolation
  during the prior Orcha checkpoint that this is 100% pre-existing and
  unrelated to any code change. Candidate for the same future
  frame-count-aware test-harness cleanup directive as the item below.
- `cp3e_chain_render_verify.mjs` samples the fully composited animated
  canvas. During Integration Pass 04 its second-edge pixel-bound assertion
  transiently reported 24/25 twice while all geometry assertions passed;
  the same test passed 25/25 against Aki's branch and on the final isolated
  merged-build rerun. No assertion was weakened and no code workaround was
  added. Treat a lone pixel sample as timing-sensitive and rerun isolated.
- `e_interaction_regression.mjs` test [6] (pod interior enter/fade) has a
  pre-existing timing flake where `fade` occasionally lands just under the
  0.99 threshold (e.g. 0.92) on a slow/contended frame. Reproduces clean on
  retry. Not related to any recent code change — accepted/documented
  pattern.
- Any Playwright/Chromium regression script run in parallel with others on
  this machine is prone to CPU-contention timing flakes (rAF starvation,
  decay-curve mismatches). Always run sequentially before concluding a
  regression is real. See `DECISIONS.md` #13.
- `scale_validation.mjs` has one self-documented KNOWN STALE check
  ("Ship < lg_planet" asteroid-scale comparison) — intentionally reverted
  per `DECISIONS.md` #9 (asteroid sprites stay at native scale). Not a
  regression; script does not gate on it.
- `pod_art_check.mjs` and `mining_zoom_regression.mjs`/`boost_regression.mjs`
  print informational "hp unchanged" / "attached pods after E: 0" lines
  from short, non-`waitForDock`-aware E-key waits — these are NOT part of
  those scripts' actual pass/fail assertions (which gate on error-count
  only) and predate CP2. Not fixed this pass (out of the Chief-approved
  scope, which was `waitForDock()` only, in
  `e_interaction_regression.mjs`/`phase1_pod_assembly_verify.mjs`); flagged
  here for a possible future cleanup directive.
- **Candidate future test-harness cleanup directive (accumulating
  backlog, not urgent, none of these gate CI):** stale `KeyR`→`KeyG`
  reference in `phase0_review_verify.mjs`; `tickAutoSave()`'s fixed-wall-clock
  wait in `phase0_saveload_verify.mjs` (should poll frame-count delta
  instead, same pattern as the `waitForDock()` fix in `DECISIONS.md` #14);
  the pre-existing `pod_art_check.mjs`/`mining_zoom_regression.mjs`/
  `boost_regression.mjs` informational-only lines noted above.

## Current MVP milestone
Modular refactor of `src/main.js` into owned domain modules
(`src/render/*`, `src/systems/*`) with zero behavioral regression,
verified by the existing Phase 0/1 regression suite, plus the new
coordination/process layer (`_dev/coordination/`) to formalize multi-agent
integration going forward.
