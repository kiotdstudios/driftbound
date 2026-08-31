// ─── CP2: Physical Docking State Machine ──────────────────────────────────────
// Replaces the instant-attach in tryClaimWorldPod with a staged sequence:
//   IDLE → ALIGNING (500 ms) → PULLING_IN (900 ms) → LOCKING (350 ms) → IDLE
//   ABORTING: cancel mid-dock, refund ore, restore connector to free.
//
// Resources (ore) and the connector slot are reserved at ALIGNING start.
// The actual graph mutation (shipAssembly update) happens only at LOCK commit.
// (DECISIONS.md rule #6: reserve before LOCK, mutate at LOCK — not before.)

export const DOCK_STATE = Object.freeze({
  IDLE:       'IDLE',
  ALIGNING:   'ALIGNING',
  PULLING_IN: 'PULLING_IN',
  LOCKING:    'LOCKING',
});

const TIMING = {
  ALIGNING:   500,
  PULLING_IN: 900,
  LOCKING:    350,
};

let _ctx = null;

const _s = {
  phase:  DOCK_STATE.IDLE,
  elapsed: 0,
  pod:    null,   // reference to the worldPod being docked
  slot:   null,   // { mod, conn } — reserved connector
  pid:    null,   // pod_instance_id shorthand
};

// ── Public API ────────────────────────────────────────────────────────────────

export function initDocking(context) {
  _ctx = context;
}

export function isDocking() {
  return _s.phase !== DOCK_STATE.IDLE;
}

// Safe snapshot for tests and __DB bridge.
export function getDockingState() {
  return {
    phase:           _s.phase,
    elapsed:         _s.elapsed,
    pod_instance_id: _s.pid,
    slotMod:         _s.slot ? _s.slot.mod.pod_instance_id : null,
    slotConn:        _s.slot ? _s.slot.conn.id             : null,
  };
}

// Rendering data for main.js drawDockingPod — null when not docking.
export function getDockingAnimData() {
  if (_s.phase === DOCK_STATE.IDLE) return null;
  const pod  = _s.pod;
  const slot = _s.slot;
  if (!pod || !slot) return null;

  let progress = 0;
  if (_s.phase === DOCK_STATE.ALIGNING)   progress = Math.min(1, _s.elapsed / TIMING.ALIGNING);
  else if (_s.phase === DOCK_STATE.PULLING_IN) progress = Math.min(1, _s.elapsed / TIMING.PULLING_IN);
  else progress = 1.0; // LOCKING — at target

  return {
    pid:          pod.pid,
    type:         pod.type,
    phase:        _s.phase,
    progress,
    srcX:         pod.worldX,
    srcY:         pod.worldY,
    slotModLocalPos: slot.mod.local_position,   // {x, y} ship-local
    slotConnDir:     slot.conn.dir,             // 'north'/'east'/'south'/'west'
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
  ship.ore          -= POD_ATTACH_COST;
  slot.conn.free     = false;
  slot.conn.state    = 'reserved';

  _s.phase   = DOCK_STATE.ALIGNING;
  _s.elapsed = 0;
  _s.pod     = pod;
  _s.slot    = slot;
  _s.pid     = pod.pid;

  return true;
}

// Cancel docking: refund ore, restore connector, reset state.
export function abortDocking(_reason) {
  if (_s.phase === DOCK_STATE.IDLE) return;

  const { ship, POD_ATTACH_COST, showToast } = _ctx;

  ship.ore += POD_ATTACH_COST;

  if (_s.slot) {
    _s.slot.conn.free  = true;
    _s.slot.conn.state = 'free';
    // connected_to is only written at commit, so no cleanup needed there.
  }

  showToast('DOCKING ABORTED', '#ef4444');
  _reset();
}

// Called every frame from loop() with dt in ms.
export function updateDocking(dt) {
  if (_s.phase === DOCK_STATE.IDLE) return;

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
  const {
    getShipAssembly, getPOD_TYPES, makeModuleNode,
    removeWorldPodByPid, addAttachedPod, applyCargoBonus,
    saveGame, showToast, spawnLockParticles, addCameraShake,
  } = _ctx;

  const pod          = _s.pod;
  const slot         = _s.slot;
  const podType      = getPOD_TYPES()[pod.type] || {};
  const shipAssembly = getShipAssembly();

  // Graph mutation: build child node, wire into assembly.
  const node = makeModuleNode(pod.pid, pod.type, slot.mod, slot.conn);
  shipAssembly[pod.pid]               = node;
  slot.conn.state                     = 'connected';
  slot.mod.connected_to[slot.conn.id] = pod.pid;

  // Remove from world list; add to legacy attached list.
  removeWorldPodByPid(pod.pid);
  addAttachedPod({ ...podType, pid: pod.pid, mod_id: pod.pid });
  applyCargoBonus(pod.type);

  showToast(
    'POD DOCKED  ' + slot.mod.pod_instance_id.toUpperCase() + '\u00B7' + slot.conn.id +
    '  (+' + (podType.mass || 0) + ' MASS)',
    '#38bdf8'
  );

  addCameraShake(4);
  spawnLockParticles(14);
  saveGame();

  _reset();
}

function _reset() {
  _s.phase   = DOCK_STATE.IDLE;
  _s.elapsed = 0;
  _s.pod     = null;
  _s.slot    = null;
  _s.pid     = null;
}
