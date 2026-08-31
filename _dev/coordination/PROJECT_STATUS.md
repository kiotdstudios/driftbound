# PROJECT_STATUS.md

_Last updated: 2026-08-30 19:41 PDT (22:41 EDT) — by Orcha, per Chief confirmation of COORD-1._

## Approved integration HEAD
**APPROVED INTEGRATION HEAD: `5fffc07`**

`refactor/modular-core` @ `5fffc07` — Chief-confirmed. Contains, in order:
`d172ca4` (prior approved baseline) → `79939be` (Aki, A1a map-input
suppression) → `712880b` (Orcha, W1 minimap extraction) → `5fffc07`
(Orcha, COORD-1 coordination system install). COORD-1 accepted by Chief as
documentation/coordination-only; no rollback required.

## Next parallel cycle
**NEXT PARALLEL CYCLE: Aki CP2 Docking / Orcha HUD Extraction**

Not yet `STATUS: GO` — awaiting Chief-authored directives in
`CHIEF_DIRECTIVES.md` with full scope (objective, allowed files, do-not-touch,
acceptance tests, stop condition) before either agent begins. Per Chief
instruction: **HOLD integration until both feature branches report back.**
No additional integration or gameplay work is to be performed from the
`integration/` worktree without an explicit Chief `GO` directive.

## Active branches
- `refactor/modular-core` — integration branch (this file's home). Local
  worktree: `integration/`.
- `agent/core-gameplay` — Aki. Worktree: `agent-core/`.
- `agent/world-ui` — Orcha. Worktree: `agent-world-ui/`. Head: `5f4ad30`.
- `main` — untouched by current work.

## Active directives
See `CHIEF_DIRECTIVES.md`. As of this checkpoint: no directive is
`STATUS: GO` for new feature work. Both agents HOLD until Chief issues
`GO` directives for the next parallel cycle (Aki CP2 Docking / Orcha HUD
Extraction — see "Next parallel cycle" above). Integration worktree HOLDs
as well — no further integration or gameplay work until both feature
branches report back per their own status files.

## Completed systems
- Regional map overlay extraction (`src/render/map.js`)
- Minimap extraction (`src/render/minimap.js`) — W1
- Map-open propulsion suppression fix — A1a
- Connector/assembly graph (pod attach/dock, mass/accel/fuel multipliers)
- HUD layout (multi-resolution verified)
- Camera system (zoom, lead, round-trip world↔screen)
- E-action interaction resolver (mine / attach pod / enter pod interior)

## Systems in progress
- None currently assigned (holding for next Chief directive).

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
