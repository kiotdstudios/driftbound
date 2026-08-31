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

## STANDING REQUIREMENT — Chief Communication Protocol (effective 2026-08-31, supersedes prior 2026-08-31 checkpoint-format note below)

Any information Chief may need must be written to GitHub **before** an
agent declares a task/check-in complete. Rule of thumb: **if Chief cannot
reconstruct your full check-in from GitHub alone, the check-in is
incomplete.** Do not rely on the user to copy/paste messages between
sessions.

Put task completion details in your own agent status file (never the
other agent's):
- Aki → `_dev/coordination/AKI_STATUS.md`
- Orcha → `_dev/coordination/ORCHA_STATUS.md`

Every checkpoint entry MUST include ALL of the following fields, in this
order:

- STATUS
- BRANCH + COMMIT
- FILES CHANGED
- IMPLEMENTATION SUMMARY
- TESTS / RESULTS
- RUNTIME / CONSOLE STATUS
- KNOWN DELTAS
- KNOWN WARNINGS
- BLOCKERS
- BUGS DISCOVERED
- BAD NEWS / UNEXPECTED FINDINGS
- QUESTIONS FOR CHIEF (if none, write literally `QUESTIONS FOR CHIEF: NONE`)
- DECISIONS NEEDED FROM CHIEF (if none, write literally `DECISIONS NEEDED FROM CHIEF: NONE`)
- RECOMMENDED NEXT ACTION
- CURRENT HOLD/GO STATE

An agent does **not** declare a task "done" until this complete report has
been written to their status file, committed, and pushed. A verbal/chat
summary to the user is not a substitute — the pushed status file is the
authoritative record Chief reconstructs from.

**`_dev/coordination/TEAM_NOTES.md`** is the catch-all for anything
broader than a single directive/task: new discoveries, QA findings, bad
news, architecture risks, technical debt, test-harness quirks, and
cross-agent notes that don't belong to one directive or one agent's
personal status file. Both agents read and write here.

If a finding — in a personal status file or in `TEAM_NOTES.md` — changes
project direction or affects the other agent, it must **also** be
reflected in `PROJECT_STATUS.md` and/or `DECISIONS.md`. Those two files
remain the canonical, current-state record; `TEAM_NOTES.md` and the
per-agent status logs are the historical/discovery record that feeds them.

## Directive Template (for Chief use)

```

---

## DIRECTIVE: CP3e — Multi-pod chain connector continuity
- **ASSIGNED TO:** Aki / Core Gameplay
- **BRANCH:** `agent/core-gameplay`
- **BASELINE:** `agent/core-gameplay @ aca2261` (CP3d)
- **STATUS:** GO
- **QA EVIDENCE:** Chief screenshot supplied 2026-08-31 shows a north-side chain of two pods. The lower pod is separated from the ship by an excessive exposed line, while the upper pod appears to float with a large empty gap and no visible connector/strut. CP3d therefore does not yet produce a visually continuous multi-module assembly.
- **OBJECTIVE:** Correct attached-module placement and connector rendering for every parent→child edge in a chained assembly, including core→pod and pod→pod. Each module must read as physically connected: sprite edges must not overlap, float apart, or lose the visible connector between them.
- **REQUIREMENTS:**
  - Diagnose the actual core→pod and pod→pod geometry independently; do not assume the same face extent or anchor works for both.
  - Derive placement from each parent and child sprite's real directional visible bounds/anchor for the relevant connector faces.
  - Render the connector/strut from the parent's visible face edge to the child's visible face edge for every graph edge. No strut may terminate inside a sprite, extend through the ship, disappear between chained pods, or leave an unexplained empty gap.
  - Use one authoritative computed transform for attached rendering, strut endpoints, hover targeting, and the completed docking target so interaction geometry cannot drift from visuals.
  - Preserve correct rotation for N/E/S/W connections and for the ship's heading. Verify at least a two-pod chain in all four directions.
  - Preserve graph topology, saved `local_position`, connector state, docking state machine, resource costs, mass, and pod scale. This is a render/interaction-coordinate correction, not a graph or balance redesign.
  - Do not treat a stale browser/server as the explanation unless the exact served commit is positively identified in the runtime. Capture the tested commit hash in the checkpoint.
- **ALLOWED FILES / OWNERSHIP:** Attached-module render/transform helpers and their minimal call sites in `src/main.js`; additive render-coordinate exposure from `src/systems/docking.js` only if strictly necessary; dedicated CP3 connector/hover regression tests; `AKI_STATUS.md` and cross-agent notes as required.
- **DO NOT TOUCH:** Pod scale tuning; HUD/map/minimap/background/VFX modules; movement, mining, save schema, resource balance; Orcha-owned files; integration worktree; `ORCHA_STATUS.md`.
- **ACCEPTANCE TESTS:**
  - Automated assertions for both core→pod and pod→pod edges that independently reject sprite overlap, unexplained empty gaps, missing struts, and struts drawn inside either sprite.
  - Two-or-more attached pods tested at N/E/S/W connectors and under ship rotation/heading changes.
  - Hover hit position must match each rendered attached pod after the placement correction.
  - Docking completion must not visibly jump to a different target position.
  - Existing CP2 docking, assembly, interaction, hover, map-input, smoke, and CP3 render regressions must pass sequentially. Report any known timing flake separately and rerun it in isolation before classifying it as environmental.
- **STOP CONDITION:** Write the complete checkpoint to `AKI_STATUS.md`, including final commit hash and explicit pushed confirmation; commit and push **only** to `agent/core-gameplay`; then HOLD for Chief visual review. Do not self-integrate.
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
