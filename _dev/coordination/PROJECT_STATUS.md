# PROJECT_STATUS.md

_Last updated: 2026-08-31 03:50 PDT — by Orcha, Integration Pass 03 complete._

## Approved integration HEAD
**APPROVED INTEGRATION HEAD: `ca6de88`**

`refactor/modular-core` @ `ca6de88`. Contains, in order since the last
Chief-confirmed baseline `5fffc07`: `36b1921` (Chief HOLD confirmation) →
`31ed323` (Chief authorization of Parallel Cycle 03) → `7dd3289` (merge:
A2/CP2 physical docking, Aki, source `73f21ef`) → `32a4c02` (merge: W2 HUD
extraction, Orcha, source `e6944ea`) → `ba10a0d` (Chief standing
checkpoint-format requirement) → `ca6de88` (test-harness `waitForDock()`
race fix, Chief-approved, Integration Pass 03). See `INTEGRATION_QUEUE.md`
for the full itemized integration log.

## Parallel cycle status
**PARALLEL CYCLE 03 — INTEGRATED.** Both `A2` (Aki, CP2 Physical Docking)
and `W2` (Orcha, HUD Module Extraction) merged cleanly into
`refactor/modular-core` — no merge conflicts, no duplicate top-level
functions/declarations post-merge (verified). Full combined regression
sweep green (see `INTEGRATION_QUEUE.md` entry 9 for the one test-harness
fix required along the way — Chief-approved, test-only, no gameplay
changes).

**Integration worktree now HOLDs again** pending the next Chief directive.
No further integration or gameplay work from `integration/` without an
explicit Chief `GO`.

## Active branches
- `refactor/modular-core` — integration branch (this file's home). Local
  worktree: `integration/`. Head: `ca6de88`.
- `agent/core-gameplay` — Aki. Worktree: `agent-core/`. Head: `73f21ef` (integrated).
- `agent/world-ui` — Orcha. Worktree: `agent-world-ui/`. Head: `e6944ea` (integrated).
- `main` — untouched by current work.

## Active directives
See `CHIEF_DIRECTIVES.md`. As of this checkpoint: `A2` and `W2` are both
INTEGRATED. No directive is currently `STATUS: GO`. Both agents and the
integration worktree HOLD until Chief issues the next directive.

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

## Systems in progress
- None currently assigned. HOLD — awaiting next Chief directive.

## P0 / P1 / P2 defects
- **P0:** None open.
- **P1:** None open.
- **P2:** None open.

## Known stale/flaky tests
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
