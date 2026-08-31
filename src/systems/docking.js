// ─── CP2: Physical Docking State Machine ──────────────────────────────────────
// Replaces the instant-attach in tryClaimWorldPod with a staged sequence:
//   IDLE → ALIGNING (500 ms) → PULLING_IN (900 ms) → LOCKING (350 ms) → COMPLETE → IDLE
//   ABORTING: cancel mid-dock, refund ore, restore connector, return to IDLE.
//
// Resources (ore) and the connector slot are reserved at ALIGNING start.
// The actual graph mutation (shipAssembly update) happens only at LOCK commit.
// (DECISIONS.md rule #6: reserve before LOCK, mutate at LOCK — not before.)
//
// All docking state uses stable IDs (strings), never raw object references.
// Objects are looked up fresh from context getters at each use site.

export const DOCK_STATE = Object.freeze({
  IDLE:       'IDLE',
  ALIGNING:   'ALIGNING',
  PULLING_IN: 'PULLING_IN',
  LOCKING:    'LOCKING',
  COMPLETE:   'COMPLETE',
  ABORTING:   'ABORTING',
});

const TIMING = {
  ALIGNING:   500,
  PULLING_IN: 900,
  LOCKING:    350,
};

let _ctx = null;

// All fields are stable IDs (strings) or primitives — no raw object refs.
const _s = {
  phase:       DOCK_STATE.IDLE,
  elapsed:     0,
  podPid:      null,   // pid of the world pod being docked
  slotModId:   null,   // pod_instance_id of the module hosting the reserved connector
  slotConnId:  null,   // connector id ('N', 'E', 'S', 'W')
  reservedOre: 0,      // ore moved from available→reserved at ALIGNING; refunded on abort, consumed at LOCK
};

// ── Context helpers — always look up fresh, never cache the object ref ────────

function _getPod()  { return _ctx.getWorldPods().find(p => p.pid === _s.podPid) || null; }
function _getMod()  { return _ctx.getShipAssembly()[_s.slotModId] || null; }
function _getConn() {
  const mod = _getMod();
  return mod ? (mod.available_connectors.find(c => c.id === _s.slotConnId) || null) : null;
}

// ── Public API ────────────────────────────────────────────────────────────────

export function initDocking(context) {
  _ctx = context;
}

export function isDocking() {
  // Active only during the three animation phases; COMPLETE/ABORTING are flush-to-IDLE.
  return _s.phase === DOCK_STATE.ALIGNING
      || _s.phase === DOCK_STATE.PULLING_IN
      || _s.phase === DOCK_STATE.LOCKING;
}

// Safe snapshot for tests and __DB bridge — IDs only, no object refs.
export function getDockingState() {
  return {
    phase:           _s.phase,
    elapsed:         _s.elapsed,
    pod_instance_id: _s.podPid,
    slotMod:         _s.slotModId,
    slotConn:        _s.slotConnId,
    reservedOre:     _s.reservedOre,
  };
}

// Rendering data for main.js drawDockingPod — null when inactive.
// Connector world target is recomputed by the caller each frame using ship transform.
export function getDockingAnimData() {
  if (!isDocking()) return null;

  // Look up pod position fresh — pod stays in worldPods until LOCK commit.
  const pod  = _getPod();
  const mod  = _getMod();
  const conn = _getConn();
  if (!pod || !mod || !conn) return null;

  let progress = 0;
  if (_s.phase === DOCK_STATE.ALIGNING)        progress = Math.min(1, _s.elapsed / TIMING.ALIGNING);
  else if (_s.phase === DOCK_STATE.PULLING_IN) progress = Math.min(1, _s.elapsed / TIMING.PULLING_IN);
  else                                          progress = 1.0; // LOCKING — at target

  return {
    pid:             pod.pid,
    type:            pod.type,
    phase:           _s.phase,
    progress,
    srcX:            pod.worldX,   // current world position (fresh lookup)
    srcY:            pod.worldY,
    // Caller recomputes world target from these + ship transform each frame:
    slotModLocalX:   mod.local_position.x,
    slotModLocalY:   mod.local_position.y,
    slotConnDir:     conn.dir,
  };
}

// Called from tryClaimWorldPod.  Returns true if docking started.
export function startDocking(pod) {
  if (_s.phase !== DOCK_STATE.IDLE) return false;

  const { ship, getPOD_TYPES, findBestConnector, POD_ATTACH_COST, showToast } = _ctx;
  const podType = getPOD_TYPES()[pod.type] || {};
  const canDock = podType.connectors && podType.connectors.length > 0;

  if (!canDock) {
    showToast('NO AVAILABLE DOCKING PORT', '#ef4444');
    return false;
  }
  if (ship.ore < POD_ATTACH_COST) {
    showToast('NOT ENOUGH NEBULITE  (' + ship.ore + '/' + POD_ATTACH_COST + ')', '#ef4444');
    return false;
  }

  const slot = findBestConnector(pod);
  if (!slot) {
    showToast('NO AVAILABLE DOCKING PORT', '#ef4444');
    return false;
  }

  // Reserve resources and connector before any graph mutation.
  // Ore moves available → reserved: deducted from ship.ore now, tracked in _s.reservedOre
  // for exact refund on abort. At LOCK it is consumed (reserved cleared, ore stays gone).
  ship.ore            -= POD_ATTACH_COST;
  slot.conn.free       = false;
  slot.conn.state      = 'reserved';

  // Store only stable IDs — no raw object refs.
  _s.phase       = DOCK_STATE.ALIGNING;
  _s.elapsed     = 0;
  _s.podPid      = pod.pid;
  _s.slotModId   = slot.mod.pod_instance_id;
  _s.slotConnId  = slot.conn.id;
  _s.reservedOre = POD_ATTACH_COST;   // exact amount reserved — used for refund, not the constant

  return true;
}

// Cancel docking: refund ore, restore connector, transition through ABORTING → IDLE.
export function abortDocking(_reason) {
  if (!isDocking()) return;

  _s.phase = DOCK_STATE.ABORTING;

  const { ship, POD_ATTACH_COST, showToast } = _ctx;

  // Refund exactly what was reserved — never the bare constant, which could drift.
  ship.ore         += _s.reservedOre;
  _s.reservedOre    = 0;   // reservation released

  // Restore connector via fresh lookup — never cache object refs.
  const conn = _getConn();
  if (conn) {
    conn.free  = true;
    conn.state = 'free';
    // connected_to is written only at LOCK commit, so no cleanup needed here.
  }

  showToast('DOCKING ABORTED', '#ef4444');
  _reset();
}

// Called every frame from loop() with dt in ms.
export function updateDocking(dt) {
  if (!isDocking()) return;

  _s.elapsed += dt;

  if (_s.phase === DOCK_STATE.ALIGNING && _s.elapsed >= TIMING.ALIGNING) {
    _s.elapsed -= TIMING.ALIGNING;
    _s.phase    = DOCK_STATE.PULLING_IN;
  } else if (_s.phase === DOCK_STATE.PULLING_IN && _s.elapsed >= TIMING.PULLING_IN) {
    _s.elapsed -= TIMING.PULLING_IN;
    _s.phase    = DOCK_STATE.LOCKING;
  } else if (_s.phase === DOCK_STATE.LOCKING && _s.elapsed >= TIMING.LOCKING) {
    _commitDock();
  }
}

// ── Private ───────────────────────────────────────────────────────────────────

function _commitDock() {
  // Transition to COMPLETE; then flush state at end of this call.
  _s.phase = DOCK_STATE.COMPLETE;

  const {
    getShipAssembly, getPOD_TYPES, makeModuleNode,
    removeWorldPodByPid, addAttachedPod, applyCargoBonus,
    saveGame, showToast, spawnLockParticles, addCameraShake,
  } = _ctx;

  // Fresh lookups — we stored IDs, not refs.
  const pod          = _getPod();
  const mod          = _getMod();
  const conn         = _getConn();
  const shipAssembly = getShipAssembly();

  if (!pod || !mod || !conn) {
    // Guard against edge case where worldPod disappeared during docking (shouldn't happen).
    _reset();
    return;
  }

  const podType = getPOD_TYPES()[pod.type] || {};

  // Graph mutation: build child node, wire into assembly.
  const node = makeModuleNode(pod.pid, pod.type, mod, conn);
  shipAssembly[pod.pid]            = node;
  conn.state                       = 'connected';
  mod.connected_to[conn.id]        = pod.pid;

  // Remove from world list; add to legacy attached list.
  removeWorldPodByPid(pod.pid);
  addAttachedPod({ ...podType, pid: pod.pid, mod_id: pod.pid });
  applyCargoBonus(pod.type);

  showToast(
    'POD DOCKED  ' + mod.pod_instance_id.toUpperCase() + '\u00B7' + conn.id +
    '  (+' + (podType.mass || 0) + ' MASS)',
    '#38bdf8'
  );

  addCameraShake(4);
  spawnLockParticles(14);
  saveGame();

  // Ore consumed: it was already deducted from ship.ore at reservation.
  // Clear the reserved ledger so _reset() finds it at 0.
  _s.reservedOre = 0;

  _reset();
}

function _reset() {
  _s.phase       = DOCK_STATE.IDLE;
  _s.elapsed     = 0;
  _s.podPid      = null;
  _s.slotModId   = null;
  _s.slotConnId  = null;
  _s.reservedOre = 0;
}
