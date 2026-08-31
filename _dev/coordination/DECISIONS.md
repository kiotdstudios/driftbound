# DECISIONS.md — Permanent Design/Architecture Decisions

These are locked. Agents must not unknowingly reverse any of these. If a
decision needs to change, it must be proposed to Chief explicitly and this
file updated with the change and rationale — never silently overridden by
a code edit.

1. `index.html` is the canonical modular entry point. Legacy HTML is
   rollback/reference only — not a live target for edits.
2. `X` = brake during normal flight.
3. `Space` is reserved (not bound to a current action; do not repurpose
   without Chief sign-off).
4. The regional map suppresses propulsion — all directional input
   (W/S/D/A/ArrowUp/Down/Left/Right, including boost) is inert while the
   map overlay is open; existing velocity still decays normally (coast
   logic intact); controls restore immediately on close. (See A1a.)
5. The connector graph is the authoritative source of ship assembly —
   mass/accel/fuel multipliers and rendering are derived from it, not the
   reverse.
6. Docking reserves resources/connectors before LOCK; the actual graph
   mutation occurs only at docking LOCK, not before.
7. Authoritative state uses stable IDs (not array indices) for ship
   modules/pods.
8. Mouse hover and interaction range are separate systems — hover is a
   presentation/targeting concern, interaction range is the gameplay gate
   for the E-action resolver.
9. Asteroid sprites remain at native asset scale until larger/replacement
   art exists — do not rescale as a stopgap.
10. The current background/parallax is frozen pending a dedicated
    environment pass — do not iterate on it piecemeal.
11. Module ownership boundaries (established in `OWNERSHIP.md`, baseline
    `53a41ad8`): Aki/Core Gameplay owns interaction resolver, docking,
    connector/assembly, movement/physics, mining, gameplay state; Orcha/
    World & UI owns map, minimap, HUD, background/parallax, environmental
    presentation, visual diagnostics. `src/main.js` cross-domain
    orchestration, `index.html`, save schema, and shared interfaces
    (`window.__DB`, `src/core/camera.js`, `src/core/input.js` exports) are
    LOCKED — Chief approval required regardless of which workstream
    proposes the change.
12. Feature agents never self-integrate into `refactor/modular-core`; all
    integration is Chief-approved and tracked through
    `_dev/coordination/INTEGRATION_QUEUE.md`.
13. Regression scripts that spawn Playwright/Chromium must be run
    sequentially, not batched in parallel, on this dev machine — parallel
    execution produces CPU-contention timing flakes (e.g. rAF starvation,
    decay-curve tests failing spuriously) that are environmental, not code
    regressions. Always retry a suspicious solo-vs-batch discrepancy before
    reporting a regression.
