// src/systems/interactions.js
// ─── E-KEY INTERACTION BOUNDARY ───────────────────────────────────────────────
// Single-action resolver for the space-flight path (NOT called during
// interiorMode — interior E-handling lives inside updateInteriorPlayer).
//
// Priority order, exactly one action per frame:
//   (1) Pod interior enter   — edge-triggered, pods with hasInterior flag only
//   (2) World pod claim      — edge-triggered
//   (3) Mine nearest asteroid — hold-to-mine
//
// All state mutation happens via context callbacks (bound at init), so this
// module has no direct dependencies on main.js globals.
// ─────────────────────────────────────────────────────────────────────────────

import { isEEdge, isHeld } from '../core/input.js';
import { DevLog } from './devTools.js';

let _ctx = null;

/**
 * Call once at startup with live references and mutation callbacks.
 *
 * @param {{
 *   ship:               object,
 *   getMineTarget:      () => object|null,
 *   getAttachedPods:    () => object[],
 *   getInteriorMode:    () => boolean,
 *   getInteriorFadeDir: () => number,
 *   onEnterInterior:    (podIdx: number) => void,
 *   onClaimWorldPod:    () => boolean,
 *   onMineExecute:      (ast: object) => void,
 * }} context
 */
export function initInteractions(context) {
  _ctx = context;
  DevLog.info('interactions', 'initInteractions — context bound');
}

/**
 * Resolve exactly one E action per frame, in priority order.
 * Call once per frame from loop(), after the updateMining() scanning pass.
 * eEdge is cleared by loop() at end-of-frame (line ~3717 in main.js).
 *
 * @returns {boolean} true if an action was taken this frame
 */
export function resolveInteractions() {
  if (!_ctx) return false;

  // Snapshot the edge flag once — isEEdge() is a pure getter (no auto-clear).
  const eEdge = isEEdge();
  let handled = false;

  // (1) Enter an attached pod's interior.
  //     Edge-triggered; pods with hasInterior flag only.
  //     Blocked while a fade transition is already running.
  if (eEdge && !_ctx.getInteriorMode() && _ctx.getInteriorFadeDir() === 0) {
    const pods = _ctx.getAttachedPods();
    for (let i = 0; i < pods.length; i++) {
      if (pods[i].hasInterior) {
        _ctx.onEnterInterior(i);
        handled = true;
        break;
      }
    }
  }

  // (2) Claim / attach a world pod. Edge-triggered.
  if (!handled && eEdge) {
    handled = _ctx.onClaimWorldPod();
  }

  // (3) Mine the nearest asteroid. Hold-to-mine.
  //     Only fires when E claimed nothing else this frame.
  if (!handled) {
    const ast = _ctx.getMineTarget();
    if (isHeld('KeyE') && ast && _ctx.ship.mineCooldown <= 0) {
      _ctx.onMineExecute(ast);
      handled = true;
    }
  }

  return handled;
}
