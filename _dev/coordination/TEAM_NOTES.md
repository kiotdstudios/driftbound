# TEAM_NOTES.md — Cross-Agent / Broader Findings Log

Catch-all for anything broader than a single directive: new discoveries, QA
findings, bad news, architecture risks, technical debt, test-harness quirks,
and cross-agent notes that don't cleanly belong in one agent's personal
status file. Both agents and Chief read and write here. Newest entries at
the top. If a note here changes project direction or affects the other
agent, it must ALSO be reflected in `PROJECT_STATUS.md` and/or
`DECISIONS.md` — this file does not replace those, it feeds them.

Per Chief Communication Protocol (2026-08-31): if Chief cannot reconstruct
a finding from GitHub alone, it does not count as reported. This file
exists so findings that don't fit a single checkpoint template still get
a permanent, GitHub-visible home.

---

## Entry template

```
### [YYYY-MM-DD] <short title> — logged by <Aki|Orcha|Chief>
- CATEGORY: architecture risk | tech debt | test quirk | bad news | cross-agent note | other
- AFFECTS: <agent(s)/system(s)>
- DETAIL: ...
- FOLLOW-UP: (linked directive, or "none — informational")
```

---

### [2026-08-31] Chief Communication Protocol adopted — logged by Orcha
- CATEGORY: cross-agent note (process)
- AFFECTS: both agents, all future checkpoints
- DETAIL: Chief mandated (2026-08-31 09:20 PDT) that every status-file
  checkpoint (`AKI_STATUS.md`/`ORCHA_STATUS.md`) must include: status,
  branch+commit, files changed, implementation summary, tests/results,
  runtime/console status, known deltas, known warnings, **blockers**,
  **bugs discovered**, **bad news/unexpected findings**, questions for
  Chief, decisions needed from Chief, recommended next action, current
  HOLD/GO state. This supersedes/expands the prior standing requirement
  recorded in `CHIEF_DIRECTIVES.md` (commit `ba10a0d`) with three new
  required fields (blockers / bugs discovered / bad news). Anything
  broader than one task — architecture findings, risks, recurring bugs,
  tech debt, cross-agent notes — goes in THIS file, not buried in a
  personal status file. Anything that changes project direction or
  affects the other agent must also update `PROJECT_STATUS.md`/
  `DECISIONS.md`. No relying on the user to relay messages between
  sessions — GitHub is the only source of truth Chief reconstructs from.
- FOLLOW-UP: `CHIEF_DIRECTIVES.md` updated in this same commit to record
  the full expanded checklist and point to this file. All future
  checkpoints (both agents) must conform starting now.

### [2026-08-31] waitForDock() test-harness race condition (root cause + fix) — logged by Orcha
- CATEGORY: test quirk (resolved) / cross-agent note
- AFFECTS: both agents — this pattern can recur in any future test that
  polls an async, keyboard-driven game-state flag
- DETAIL: During Integration Pass 03, merging Aki's CP2 docking (staged
  ~1.75s state machine) with the existing test suite broke
  `phase1_pod_assembly_verify.mjs` and `e_interaction_regression.mjs`
  (test [4]). Root cause: `waitForDock()` polled `isDocking()` once and
  returned as soon as it read `false` — but a `keyboard.press()` call
  returns before the game's rAF loop has processed the resulting E-edge
  into `startDocking()`, so the flag can read `false` because the action
  **never started**, not because it finished. The helper could not tell
  the two cases apart. This was purely a test-harness bug — confirmed via
  isolated repro that `src/systems/docking.js`/`src/main.js` behaved
  correctly (Aki's own dedicated `cp2_docking_verify.mjs`, which calls
  `startDockingByPid()` directly, was 30/30 clean throughout). Chief
  approved a fix requiring an OBSERVED false→true→false lifecycle before
  returning. Fixed identically in both files (commit `ca6de88`). Recorded
  as a **permanent decision** in `DECISIONS.md` #14 so this class of bug
  isn't rediscovered by either agent in a future test.
- FOLLOW-UP: None required — fixed and verified (23/23 and 25/25 clean).
  Flagging here for visibility since it's a reusable lesson, not just a
  one-off fix.

### [2026-08-31] Pre-existing test-harness quirks NOT fixed this pass (out of approved scope) — logged by Orcha
- CATEGORY: tech debt
- AFFECTS: shared test files (`pod_art_check.mjs`, `mining_zoom_regression.mjs`, `boost_regression.mjs`)
- DETAIL: `pod_art_check.mjs` uses a hardcoded 500ms wait after pressing E
  (pre-dates CP2's ~1.75s docking sequence) and reports "attached pods
  after E: 0" — but the script uses a soft `CHECK` status, not
  `process.exit(1)`, so it doesn't fail CI. `mining_zoom_regression.mjs`
  and `boost_regression.mjs` print informational "hp unchanged" lines
  that are not part of either script's actual pass/fail assertion (both
  gate on error-count only). None of these are regressions from
  Integration Pass 03 — all three predate CP2 and were out of the
  Chief-approved fix scope (`waitForDock()` in
  `e_interaction_regression.mjs`/`phase1_pod_assembly_verify.mjs` only).
- FOLLOW-UP: Candidate for a future low-priority test-harness cleanup
  directive. Not blocking, not urgent. Also noted in `PROJECT_STATUS.md`
  "Known stale/flaky tests".

### [2026-08-31] Merge integrity checks performed for Integration Pass 03 — logged by Orcha
- CATEGORY: architecture note / QA finding (clean result)
- AFFECTS: both agents (shared file `src/main.js`)
- DETAIL: Both A2 (Aki) and W2 (Orcha) touched `src/main.js` extensively.
  Before trusting the `git merge --no-ff` auto-merge (clean, no reported
  conflicts) as semantically correct, ran explicit verification: (1) no
  duplicate top-level `function` declarations post-merge (0 found across
  65 functions); (2) no duplicate top-level `const`/`let` declarations
  (0 found across 152 declarations); (3) confirmed both feature imports
  present and correctly wired (`createHUD`, `initDocking`/`updateDocking`/
  `startDocking`/`abortDocking`); (4) confirmed draw order preserved
  (`hud.render → minimap.render → drawDevControls`) and update order
  preserved (`update() → updateDocking(dt) → updateMining()`). All clean.
  Recommending this checklist (dupe-scan + explicit order verification)
  as a standard step for any future multi-branch merge into
  `refactor/modular-core`, not just this pass.
- FOLLOW-UP: None required this pass. Suggest promoting to a permanent
  merge-checklist entry in `DECISIONS.md` if Chief agrees it should be
  mandatory for all future integration passes (currently just documented
  here as the approach taken).
