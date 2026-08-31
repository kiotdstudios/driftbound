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
| 3 | COORD-1 | (direct on refactor/modular-core) | — | *(recorded in PROJECT_STATUS.md after push)* | Coordination system install. Documentation-only. |

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
