# CHIEF_DIRECTIVES.md — Authoritative Task Board

This is the single source of truth for what each agent is allowed to work on.
Agents may execute **only** directives marked `STATUS: GO`. If no directive
assigned to you has `STATUS: GO`, you HOLD — do not invent your own next
feature.

---

## DIRECTIVE: A1a
- **ASSIGNED TO:** Aki
- **BRANCH:** `agent/core-gameplay`
- **BASELINE:** `refactor/modular-core @ d172ca4`
- **STATUS:** INTEGRATED (pre-dates this coordination system; logged retroactively)
- **OBJECTIVE:** Fix propulsion input leaking through while the regional map overlay is open (W/S/D/ArrowUp/Down/Right continued to accelerate the ship; only A/ArrowLeft was guarded).
- **ALLOWED FILES / OWNERSHIP:** `src/main.js` (movement/physics block only), `index.html` (cache-bust version bump), new test file.
- **DO NOT TOUCH:** `src/render/*`, HUD, minimap, connector/assembly graph.
- **ACCEPTANCE TESTS:** `_dev/map_input_suppression_verify.mjs` — 18/18 PASS (map-closed accel confirmed; map-open + all 4 directions suppressed; coast/decay intact; boost suppression intact; controls restore on close).
- **STOP CONDITION:** Met — fix verified, committed (`79939be`), no known deltas.

## DIRECTIVE: W1
- **ASSIGNED TO:** Orcha
- **BRANCH:** `agent/world-ui`
- **BASELINE:** `refactor/modular-core @ d172ca4`
- **STATUS:** INTEGRATED (pre-dates this coordination system; logged retroactively)
- **OBJECTIVE:** Extract `drawMinimap()` out of `src/main.js` into `src/render/minimap.js`, following the `createRegionalMap`-style factory pattern already established in `map.js`. Behavior-preserving move only — no feature changes.
- **ALLOWED FILES / OWNERSHIP:** `src/render/minimap.js` (new), `src/main.js` (import + call-site wiring only).
- **DO NOT TOUCH:** movement/physics, docking, connector/assembly graph, mining, save schema.
- **ACCEPTANCE TESTS:** `phase0_smoke`, `hud_layout_regression` (27/27), `hud_zoom_regression`, `phase0_controls_verify`, `camera_roundtrip_verify` (36/36), `phase1_pod_assembly_verify` (23/23), `e_interaction_regression` (25/25), `phase0_mining_jitter_verify`, `phase0_review_verify` — all PASS, run sequentially (parallel browser instances produced CPU-contention timing flakes, not real regressions).
- **STOP CONDITION:** Met — fix verified, committed (`712880b` on integration branch, source `5f4ad30` on `agent/world-ui`), no known deltas.

## DIRECTIVE: COORD-1
- **ASSIGNED TO:** Orcha
- **BRANCH:** `refactor/modular-core` (direct — coordination/documentation checkpoint, not a feature branch task)
- **BASELINE:** `refactor/modular-core` local HEAD at time of task (`712880b`, i.e. `d172ca4` + A1a + W1)
- **STATUS:** GO → INTEGRATING (this commit)
- **OBJECTIVE:** Install the `_dev/coordination/` system (this file + AKI_STATUS.md, ORCHA_STATUS.md, INTEGRATION_QUEUE.md, PROJECT_STATUS.md, DECISIONS.md, SCORECARD.md) as the authoritative project-management layer going forward.
- **ALLOWED FILES / OWNERSHIP:** `_dev/coordination/**` only.
- **DO NOT TOUCH:** Any gameplay, rendering, or test file. Documentation-only checkpoint.
- **ACCEPTANCE TESTS:** N/A — non-executable documentation. Sanity check: files created, committed, pushed; no `src/*` or `index.html` diff in this commit.
- **STOP CONDITION:** Met — files pushed to `refactor/modular-core` (`5fffc07`); new integration hash reported to Chief; Aki notified to read the new system. Chief-confirmed accepted, documentation/coordination-only, no rollback (see follow-up confirmation commit `36b1921`).

---

## PARALLEL CYCLE 03 — Chief-authorized

Both directives below sync from **code baseline `5fffc07`**. `36b1921` is
coordination metadata only and does not alter the code baseline. Aki owns
docking/gameplay; Orcha owns HUD presentation. Neither agent edits the
other's status file, touches the integration worktree, or
merges/cherry-picks/rebases the other's work. Integration remains **HOLD**
until both feature branches report back.

## DIRECTIVE: A2
- **ASSIGNED TO:** Aki / Core Gameplay
- **BRANCH:** `agent/core-gameplay`
- **BASELINE:** `refactor/modular-core @ 5fffc07`
- **STATUS:** GO
- **OBJECTIVE:** Implement the approved physical pod docking system (CP2 Physical Docking). State machine: `IDLE → ALIGNING → PULLING_IN → LOCKING → COMPLETE`, plus `ABORTING`.
- **REQUIREMENTS:**
  - Validate pod/range/resources/connector before docking.
  - Select the spatially appropriate FREE connector across the entire assembly.
  - Reserve resources at docking start; connector state `FREE → RESERVED → CONNECTED`.
  - Use stable IDs, not authoritative raw object references.
  - Continuously recompute connector world target from ship/module transform.
  - Graph remains unchanged until LOCK; consume resources and mutate graph exactly once, at LOCK.
  - Attached pod orientation must persist correctly.
  - World pod must disappear exactly once. Mass recalculated exactly once.
  - `X` = CANCEL while docking; `X` = BRAKE otherwise.
  - Abort releases resources + connector and leaves graph unchanged.
  - Save cannot serialize a half-attached state. Successful completion triggers a safe save.
  - Normal sequence target: ~1.5–2.5 seconds. Restrained alignment/pull-in/lock feedback only.
- **ALLOWED FILES / OWNERSHIP:** Docking, connector/assembly graph, movement/physics integration points, mining (per `OWNERSHIP.md` Aki/Core Gameplay ownership), new dedicated docking regression test(s).
- **DO NOT TOUCH:** `src/render/*` (map, minimap, HUD), visual diagnostics/dev-controls presentation, save schema shape beyond what's required to prevent half-attached serialization (flag any schema change to Chief before landing), the integration worktree, Orcha's status file.
- **ACCEPTANCE TESTS:** Dedicated new regressions covering: success path; reservations (FREE→RESERVED→CONNECTED); pre-LOCK graph integrity (no mutation before LOCK); abort during ALIGNING; abort during PULLING_IN; insufficient resources; invalid pod; docking while ship is moving/rotating; connector selection (spatially appropriate, across full assembly); orientation persistence; no duplication; mass recalculated exactly once; save safety (no half-attached serialization); contextual `X` (CANCEL vs BRAKE); `E`/`X` double-fire safety. Plus: run existing interaction/assembly/movement/map/runtime regressions to confirm no cross-domain regression.
- **STOP CONDITION:** Update `AKI_STATUS.md` with full checkpoint report, commit and push **only to `agent/core-gameplay`**, then STOP. Do not integrate, do not touch `refactor/modular-core`.

## DIRECTIVE: W2
- **ASSIGNED TO:** Orcha / World-UI
- **BRANCH:** `agent/world-ui`
- **BASELINE:** `refactor/modular-core @ 5fffc07`
- **STATUS:** GO
- **OBJECTIVE:** Extract the existing gameplay HUD from `src/main.js` into `src/render/hud.js`. Behavior-preserving only — this is NOT a redesign.
- **REQUIREMENTS:**
  - HUD module owns presentation/rendering for: Navigation, Ship, Hull, Fuel, Cargo/resources, pod information, context/action prompts, warnings.
  - Consume gameplay information through explicit state input (no closures back into `main.js`).
  - Must remain screen-space and independent of camera zoom.
  - Preserve draw order: HUD → minimap → dev controls.
- **ALLOWED FILES / OWNERSHIP:** `src/render/hud.js` (new), `src/main.js` (import + call-site wiring only), per `OWNERSHIP.md` Orcha/World & UI ownership (HUD).
- **DO NOT TOUCH:** Docking, interactions, movement, assembly, mining, map behavior, save schema. Do NOT add CP2 docking UI yet. The integration worktree, Aki's status file.
- **ACCEPTANCE TESTS:** HUD layout/zoom regression at all existing resolutions, plus camera, map, interaction, assembly, and runtime regressions (the full existing Phase 0/1 suite) — run sequentially to avoid CPU-contention flakes (see `DECISIONS.md` #13).
- **STOP CONDITION:** Update `ORCHA_STATUS.md` with full checkpoint report, commit and push **only to `agent/world-ui`**, then STOP. Do not integrate, do not touch `refactor/modular-core`.

---

## Directive Template (for Chief use)

```
## DIRECTIVE: <ID>
- ASSIGNED TO:
- BRANCH:
- BASELINE:
- STATUS: HOLD | GO | INTEGRATING | INTEGRATED | REWORK
- OBJECTIVE:
- ALLOWED FILES / OWNERSHIP:
- DO NOT TOUCH:
- ACCEPTANCE TESTS:
- STOP CONDITION:
```
