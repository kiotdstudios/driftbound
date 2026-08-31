# PROJECT_STATUS.md

_Last updated: 2026-08-30 19:43 PDT (22:43 EDT) — by Orcha, per Chief authorization of Parallel Cycle 03._

## Approved integration HEAD
**APPROVED INTEGRATION HEAD: `5fffc07`**

`refactor/modular-core` @ `5fffc07` — Chief-confirmed. Contains, in order:
`d172ca4` (prior approved baseline) → `79939be` (Aki, A1a map-input
suppression) → `712880b` (Orcha, W1 minimap extraction) → `5fffc07`
(Orcha, COORD-1 coordination system install). COORD-1 accepted by Chief as
documentation/coordination-only; no rollback required.

## Parallel cycle status
**PARALLEL CYCLE 03 — ACTIVE**
- **A2 CP2 DOCKING — GO** (Aki / `agent/core-gameplay`, baseline `5fffc07`)
- **W2 HUD EXTRACTION — GO** (Orcha / `agent/world-ui`, baseline `5fffc07`)

Both directives sync from code baseline `5fffc07`. `36b1921` is coordination
metadata only and does not alter the code baseline. See `CHIEF_DIRECTIVES.md`
for full scope. Aki owns docking/gameplay; Orcha owns HUD presentation.
Neither agent edits the other's status file, touches the integration
worktree, or merges/cherry-picks/rebases the other's work.

**Integration remains HOLD** until both feature branches report back
(checkpoint entries in `AKI_STATUS.md` / `ORCHA_STATUS.md`) and Chief
reviews. No additional integration or gameplay work is to be performed from
the `integration/` worktree without an explicit Chief `GO` directive.

## Active branches
- `refactor/modular-core` — integration branch (this file's home). Local
  worktree: `integration/`.
- `agent/core-gameplay` — Aki. Worktree: `agent-core/`.
- `agent/world-ui` — Orcha. Worktree: `agent-world-ui/`. Head: `5f4ad30`.
- `main` — untouched by current work.

## Active directives
See `CHIEF_DIRECTIVES.md`. As of this checkpoint: `A2` (Aki, CP2 Physical
Docking) and `W2` (Orcha, HUD Module Extraction) are both `STATUS: GO` —
Parallel Cycle 03. Integration worktree HOLDs — no further integration or
gameplay work from `integration/` until both feature branches report back
per their own status files and Chief reviews.

## Completed systems
- Regional map overlay extraction (`src/render/map.js`)
- Minimap extraction (`src/render/minimap.js`) — W1
- Map-open propulsion suppression fix — A1a
- Connector/assembly graph (pod attach/dock, mass/accel/fuel multipliers)
- HUD layout (multi-resolution verified)
- Camera system (zoom, lead, round-trip world↔screen)
- E-action interaction resolver (mine / attach pod / enter pod interior)

## Systems in progress
- CP2 Physical Docking (Aki, `agent/core-gameplay`, directive A2) — GO, in progress.
- HUD Module Extraction to `src/render/hud.js` (Orcha, `agent/world-ui`, directive W2) — GO, in progress.

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

## Current MVP milestone
Modular refactor of `src/main.js` into owned domain modules
(`src/render/*`, `src/systems/*`) with zero behavioral regression,
verified by the existing Phase 0/1 regression suite, plus the new
coordination/process layer (`_dev/coordination/`) to formalize multi-agent
integration going forward.
