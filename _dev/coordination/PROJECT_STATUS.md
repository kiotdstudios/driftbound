# PROJECT_STATUS.md

_Last updated: 2026-08-31 — Integration Pass 04._

**See also `TEAM_NOTES.md`** for cross-agent findings, architecture notes,
and test-harness quirks discovered during recent work that don't belong to
a single directive (e.g. the merge-integrity checklist used for Integration
Pass 03, and the full root-cause writeup of the `waitForDock()` race).

## Approved integration HEAD
**APPROVED INTEGRATION HEAD: `692fc51`**

`refactor/modular-core` @ `692fc51`. Integration Pass 04 merged Aki's
Chief-approved CP3→CP3e lineage from `agent/core-gameplay @ b298885`
(CP3e implementation `9d62022`) on top of the prior approved integration
baseline and Chief approval record `4cfb56c`. See `INTEGRATION_QUEUE.md`.

## Integration status
**INTEGRATION PASS 04 — COMPLETE.** CP3 through CP3e is integrated. The
merge had one documentation-only add/add conflict in `TEAM_NOTES.md`; both
histories were preserved. Production code auto-merged cleanly.

**Integration worktree now HOLDs again** pending the next Chief directive.
No further integration or gameplay work from `integration/` without an
explicit Chief `GO`.

## Active branches
- `refactor/modular-core` — integration branch (this file's home). Local
  worktree: `integration/`. Head: `692fc51` (coordination follow-up pending).
- `agent/core-gameplay` — Aki. Worktree: `agent-core/`. Head: `b298885` (integrated).
- `agent/world-ui` — Orcha. Worktree: `agent-world-ui/`. Head: `e6944ea` (integrated).
- `main` — untouched by current work.

## Active directives
See `CHIEF_DIRECTIVES.md`. CP3e is INTEGRATED. No directive is currently
`STATUS: GO`; agents and the integration worktree HOLD for Chief.

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

## Systems in progress
- None currently assigned. HOLD — awaiting next Chief directive.

## P0 / P1 / P2 defects
- **P0:** None open.
- **P1:** None open.
- **P2:** None open.

## Known stale/flaky tests
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

## Current MVP milestone
Modular refactor of `src/main.js` into owned domain modules
(`src/render/*`, `src/systems/*`) with zero behavioral regression,
verified by the existing Phase 0/1 regression suite, plus the new
coordination/process layer (`_dev/coordination/`) to formalize multi-agent
integration going forward.
