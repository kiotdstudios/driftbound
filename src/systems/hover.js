// src/systems/hover.js
// ─── MOUSE HOVER TARGETING ───────────────────────────────────────────────────
// Pure hit-testing: world-space cursor point -> closest InteractionTarget
// candidate. Completely decoupled from the E-key interaction resolver
// (src/systems/interactions.js) — that module remains the single authoritative
// E consumer. Hover only answers "what is the cursor pointing at"; it never
// gates or performs an action itself. Whether E *can* act on a hovered target
// is a separate range check that already lives where each action lives
// (proximity checks in interactions.js / updateMining()) and is untouched by
// this module.
//
// Generic candidate shape so future object types (turrets, wrecks, NPCs, ...)
// plug into hover with zero new hit-test code:
//   {
//     type:      string   — 'world_pod' | 'attached_pod' | 'asteroid' | ...
//     id:        string|number,
//     worldX:    number,
//     worldY:    number,
//     hitRadius: number,   // world-px; point-in-circle test
//     ref:       object,   // the underlying game object, for the caller to act on
//   }
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Hit-test a world-space point against a list of InteractionTarget candidates.
 * Returns the closest candidate whose hitRadius contains the point, or null
 * if none do. Distance ties favor the earlier candidate (callers control
 * priority via the order they build the candidate list).
 *
 * @param {number} worldX
 * @param {number} worldY
 * @param {Array}  candidates
 * @returns {object|null}
 */
export function resolveHover(worldX, worldY, candidates) {
  let best = null, bestDist = Infinity;
  for (const c of candidates) {
    const d = Math.hypot(c.worldX - worldX, c.worldY - worldY);
    if (d <= c.hitRadius && d < bestDist) {
      best = c;
      bestDist = d;
    }
  }
  return best;
}
