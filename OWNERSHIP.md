# OWNERSHIP.md — DRIFTBOUND Modular Branch

Established at parallel-development authorization, baseline commit:
`53a41ad827d0407e9655ab2ca138376a1ed236c0` (branch `refactor/modular-core`).

This file defines module/domain ownership for the two parallel workstreams.
It exists to prevent cross-boundary edits and merge conflicts before they
happen. If your task requires touching a module outside your ownership,
**stop and propose the interface change instead of editing across the
boundary.**

Workstream branches/worktrees:
- `agent/core-gameplay` — worktree `agent-core/`
- `agent/world-ui` — worktree `agent-world-ui/`

Neither feature agent works directly in `integration/` (tracks
`refactor/modular-core`). Neither feature agent merges the other's branch.
Only approved commits are merged/cherry-picked into `refactor/modular-core`,
by chief approval.

---

## Aki / Core Gameplay
Branch: `agent/core-gameplay`

Owns:
- interaction resolver (the single-E-action-per-frame resolver currently
  inside `updateMining()` in `src/main.js` — first extraction target:
  `src/systems/interactions.js`)
- docking
- connector/assembly gameplay (`shipAssembly`, `SHIP_BALANCE`, connector
  graph, mass/accel/fuel multipliers)
- movement/physics (ship thrust/boost/friction/collision integration)
- mining behavior (asteroid HP, ore drops, mine range/cooldown)
- gameplay state implications (ship/cargo/fuel/hp state and anything that
  feeds save data describing gameplay state)

## Orcha / World & UI
Branch: `agent/world-ui`

Owns:
- map (regional map overlay)
- minimap
- HUD (`drawHUD`, HUD layout/rows/sections)
- background/parallax (`src/render/background.js`, `ENV_CONFIG`)
- environmental presentation (stars, particles, ambient lighting, vignette)
- visual diagnostics (F1/F2 debug + diagnostics overlays, dev controls panel
  presentation)

---

## LOCKED / CHIEF APPROVAL ONLY

The following require chief approval before any change lands, regardless of
which workstream proposes it:

- `src/main.js` orchestration changes that affect **both** domains (the main
  loop wiring, boot sequence, shared module imports/exports)
- `index.html`
- save schema (`saveGame()`/`loadGame()` data shape, `SAVE_KEY` contents)
- shared interfaces (`window.__DB` test bridge shape, `src/core/camera.js`
  and `src/core/input.js` public exports, and any other contract consumed
  by both workstreams)

---

## Escalation

If either agent needs another owner's module changed to complete their
task: **do not edit it.** Stop, describe the exact interface/behavior you
need, and propose it back for chief + owning-agent review. This applies
symmetrically — Aki does not edit World/UI modules, Orcha does not edit
Core Gameplay modules, and neither edits a LOCKED file without chief
sign-off.
