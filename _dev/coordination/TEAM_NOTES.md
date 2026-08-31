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
---

## 2026-08-31 — Aki: Local dev-server port conflict + duplicate Driftbound folders on disk (user's machine)

**Context:** Chief/user reported CP3b-2 (attached-pod scale fix) still looked
broken on manual retest. Automated Playwright repro against the exact pushed
commit (agent/core-gameplay @ a5d5ad4) confirmed the code itself renders
correctly at all 4 connector directions — this is an environment/serving
issue on the user's machine, not a code regression.

**Finding 1 — two processes bound to port 8420 simultaneously.**
`netstat -ano | findstr :8420` on the user's machine showed:
- PID `21444` listening on `0.0.0.0:8420` and `[::]:8420` (all interfaces)
- PID `13988` listening on `127.0.0.1:8420` (localhost-only)

One of these is very likely a stale/leftover dev server silently answering
`localhost:8420` ahead of whatever fresh server is started from the correct
folder — with no error or warning to signal it. This would explain why a
correct code fix still "looks broken" in the browser, even in a fresh
Incognito window (ruling out normal cache). Confirmed on the user's build via
console: `window.__DB.attachedPodRenderSize` read `undefined` instead of the
expected ~126.13, which only happens if the browser isn't actually running
the current build.

Neither process has been killed yet (pending chief/user go-ahead). Not yet
confirmed which specific PID/folder is the one actually answering the user's
browser requests.

**Finding 2 — two separate top-level Driftbound folders exist in the user's Documents.**
- `Documents/DRIFTBOUND` — created 8/30/2026 4:41 PM
- `Documents/driftbound_work/` — created 8/31/2026 12:15 AM, contains
  `agent-core` (the worktree used for all Aki/core-gameplay work this cycle),
  `agent-world-ui`, and `integration`.

Contents/history of the 8/30 `DRIFTBOUND` folder have not yet been inspected
(could be an old standalone clone, a scratch copy, or an independent checkout
with its own local server history). Having two similarly-named project
folders on disk is a standing risk for exactly the kind of silent
stale-serving confusion described above, and for divergent/duplicated local
edits if anyone works out of the wrong one by mistake.

**Recommendation:** analyze the contents of both folders, consolidate into one
canonical location, and archive or delete whichever is not the live working
copy. Until that happens, always confirm both (a) which folder a running dev
server was started from and (b) `git log -1` / `git branch --show-current`
in that exact folder before trusting a browser-side manual QA result.

**Status:** flagged to chief for a decision; no folder or process changes
made yet on the user's machine.

## 2026-08-31 (follow-up) — Aki: port conflict resolved, DRIFTBOUND folder inspected, CP3b-2 re-confirmed GOOD

**Port 8420 fix.** Killed both stale listeners (PID 21444, PID 13988 — both were
plain `python -m http.server 8420` processes, one bound wildcard, one
localhost-only). Verified `netstat` showed a fully clear port afterward.
Started exactly one fresh server from `Documents/driftbound_work/agent-core`
(the intended test worktree), confirmed via `netstat` that only one PID is
now bound to 8420, and confirmed via browser (`window.__DB.attachedPodRenderSize`)
that this server is serving the current build (~126.13, matching CP3b-2).

**DRIFTBOUND (8/30 folder) inspected — not touched, not deleted.**
- **Not git-controlled** — no `.git` directory. No branch/HEAD applicable.
- It is a plain folder copy of an earlier project state, missing files that
  `driftbound_work/agent-core` has (`OWNERSHIP.md`, `START_GAME.bat`,
  `driftbound_flight_test.html.bak`), and its `index.html` cache-bust version
  tag is one version behind agent-core's (`main.js?v=20260830-5` vs
  `...-6`) — i.e. it is stale relative to the working repo.
- It DOES contain a handful of files not present in `driftbound_work` at
  all: `_check.txt`, `_idx.txt`, `_inspect.txt`, `_keys.txt`, `_patch_blue.py`,
  `_test.txt`, and a 16MB `test blue map.html`. These read as scratch/debug
  artifacts from earlier experimentation, not obviously load-bearing, but
  not yet confirmed disposable — no deletion has happened.
- Its `src/` layout also differs: it has `assets/`, `player/`, `world/`
  subfolders that don't exist in the current modular `src/` in agent-core
  (which only has `core/`, `render/`, `systems/`, `main.js`) — consistent
  with DRIFTBOUND being a pre-refactor snapshot, not an actively maintained
  parallel branch.
- **Recommendation unchanged:** before archiving/deleting, someone should
  specifically check whether the unique scratch files above hold anything
  worth keeping; otherwise DRIFTBOUND can be archived (not necessarily
  deleted) once confirmed. No action taken yet — awaiting chief's call.

**CP3b-2 re-confirmed GOOD against the clean, single-server environment.**
- Docked at all 4 connector directions (N/E/S/W) fresh against the newly
  started clean server — pod substantial, flush, no gap, ship hull clearly
  visible in every direction (screenshots taken, held locally, not committed).
- Ran the actual committed `_dev/hover_targeting_verify.mjs` suite against
  the clean server: **22/22 passed** — world pod / attached pod / asteroid /
  empty-space hover correct at all 5 zoom levels, hover confirmed decoupled
  from the E-key resolver.
- **Conclusion: the "still broken" report was an environment false-negative**
  (stale server on port 8420 answering ahead of the fresh one). CP3b-2
  (`0655257`) is closed as correct. No further code changes needed from Aki
  on this directive.
