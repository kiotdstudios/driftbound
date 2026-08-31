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
- **STOP CONDITION:** Files pushed to `refactor/modular-core`; new integration hash reported to Chief; Aki notified to read the new system. No further action until Chief issues a new `STATUS: GO` directive.

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
