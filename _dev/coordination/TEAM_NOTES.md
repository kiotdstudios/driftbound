# TEAM_NOTES.md — Shared Cross-Agent Notes

Catch-all for discoveries, QA findings, bad news, architecture risks, technical
debt, test quirks, and cross-agent notes that don't belong to a single
directive or a single agent's personal status file. Both Aki and Orcha may
append here. Newest entries at the top.


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
