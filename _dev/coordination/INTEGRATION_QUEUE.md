# INTEGRATION_QUEUE.md

Feature agents never self-integrate. Only Chief moves items from APPROVED
into INTEGRATING/INTEGRATED on `refactor/modular-core`.

States: **WAITING → APPROVED → INTEGRATING → INTEGRATED** (or **REJECTED / REWORK**)

---

## INTEGRATED

| Order | Directive | Source Branch | Source Commit | Integration Commit (on refactor/modular-core) | Notes |
|---|---|---|---|---|---|
| 1 | A1a | agent/core-gameplay | 79939be | 79939be | Map-open propulsion suppression fix. Integrated directly (pre-dates this queue system); logged retroactively. |
| 2 | W1 | agent/world-ui | 5f4ad30 | 712880b | Minimap extraction to src/render/minimap.js. Note: integration commit hash differs from source hash (replayed/cherry-picked, not fast-forwarded) — content verified identical (main.js -114/+10, minimap.js new +150). Integrated directly (pre-dates this queue system); logged retroactively. |
| 3 | COORD-1 | (direct on refactor/modular-core) | — | 5fffc07 | Coordination system install. Documentation-only. |
| 4 | (direct) | (direct on refactor/modular-core) | — | 36b1921 | Chief confirmation of approved HEAD 5fffc07, HOLD notice for next parallel cycle. Documentation-only. |
| 5 | (direct) | (direct on refactor/modular-core) | — | 31ed323 | Chief authorization of Parallel Cycle 03 (A2 + W2, both STATUS: GO). Documentation-only. |
| 6 | A2 / CP2 | agent/core-gameplay | 73f21ef | 7dd3289 | Physical pod docking state machine (IDLE→ALIGNING→PULLING_IN→LOCKING→COMPLETE, +ABORTING). Merged via `git merge --no-ff` (no conflicts). Full history: d973c63 (initial) → cb0446d (rework: stable IDs + complete DOCK_STATE enum) → 28fe949 (rework2: ore available/reserved/consumed ledger) → d587b4f (final: safe-release on mid-dock invalidation) → 73f21ef (status log). |
| 7 | W2 | agent/world-ui | e6944ea | 32a4c02 | HUD extraction to src/render/hud.js. Merged via `git merge --no-ff` (auto-merged src/main.js cleanly, no conflicts — verified no duplicate top-level functions/declarations post-merge). |
| 8 | (direct) | (direct on refactor/modular-core) | — | ba10a0d | Chief standing requirement: expanded AKI_STATUS.md/ORCHA_STATUS.md checkpoint format. Documentation-only. |
| 9 | (direct, integration-pass fix) | (direct on refactor/modular-core) | — | ca6de88 | Fixed waitForDock() race condition in shared test harness (_dev/e_interaction_regression.mjs, _dev/phase1_pod_assembly_verify.mjs) discovered during Integration Pass 03's regression sweep. Chief-approved (Option 1). Test-harness-only; no gameplay code touched, no assertions weakened. |

## INTEGRATING

*(none currently)*

## APPROVED

*(none currently — awaiting Chief approval before any new directive moves here)*

## WAITING

*(none currently — no directives submitted for review)*

## REJECTED / REWORK

*(none)*

---

## Chief note on retroactive entries #1–#2

Both A1a and W1 were committed directly to this integration worktree's local
`refactor/modular-core` branch by an active session prior to this
coordination system being installed, and were **not yet pushed to origin**
at the time COORD-1 began. They are being pushed together with the
coordination files in this same checkpoint. Going forward, all integrations
must be explicitly moved through WAITING → APPROVED → INTEGRATING →
INTEGRATED in this file before landing on `refactor/modular-core`.
