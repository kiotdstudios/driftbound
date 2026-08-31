// ═══════════════════════════════════════════════════════════════════════════
// CAMERA — src/core/camera.js  (Phase 3 extraction, see MIGRATION_PLAN.md)
// Single owner of: camera lead, camera shake, zoom index/current/target/easing,
// screen-center calculation, world<->screen conversion, world-transform
// apply/restore. Behavior-preserving extraction only — every formula below is
// copied verbatim from src/main.js. Feel/values (CAM_LEAD, CAM_LAG, ZOOM_LEVELS,
// ZOOM_LERP, shake decay/impulse) are UNCHANGED.
//
// Background rendering is explicitly NOT owned here — the parallax background
// renders outside the world zoom transform by design (see MIGRATION_PLAN.md);
// Camera only owns the transform math/state, never background drawing.
//
// CP3 note (for Aki's future InteractionTarget system): screenToWorld() is the
// single authoritative inverse transform. Feed it raw mouse screen coordinates
// (from src/core/input.js getMousePosition()) to get world-space hover
// coordinates. Hover targeting itself is NOT implemented here.
// ═══════════════════════════════════════════════════════════════════════════

// ── Camera lead + shake state (verbatim from src/main.js) ──
let camLeadX = 0, camLeadY = 0;
let camShakeX = 0, camShakeY = 0;
let _prevBoosting = false;  // edge-detect for boost-start flare

// ── Zoom state (verbatim from src/main.js) ──
// World-only zoom. HUD/minimap/map/diag/notifications NEVER scaled.
// Scales around screen center (not ship) so smooth camera lead is preserved.
const ZOOM_LEVELS  = [0.70, 0.85, 1.00, 1.15, 1.30];
let   camZoomIdx    = 1;               // default = 0.85x
let   camZoom       = ZOOM_LEVELS[1];  // current eased value
let   camZoomTarget = ZOOM_LEVELS[1];  // target level
const ZOOM_LERP     = 0.14;            // easing speed toward target

let _canvas = null;
// World point the camera is currently centered on (ship.worldX/Y each frame).
let _focusWorldX = 0, _focusWorldY = 0;

export function initCamera(canvas) {
  _canvas = canvas;
}

export function addCameraShake(amt) {
  camShakeX += (Math.random() - 0.5) * amt * 2;
  camShakeY += (Math.random() - 0.5) * amt * 2;
}

// ── Explicit zoom control API ──
export function getZoomLevels() { return ZOOM_LEVELS; }
export function getZoomIndex()  { return camZoomIdx; }
export function setZoomIndex(idx) {
  camZoomIdx = Math.max(0, Math.min(ZOOM_LEVELS.length - 1, idx));
}
export function zoomIn()    { setZoomIndex(camZoomIdx + 1); }
export function zoomOut()   { setZoomIndex(camZoomIdx - 1); }
export function resetZoom() { camZoomIdx = 1; }

// ── Per-frame update. Call once per frame in loop(), BEFORE rendering. ──
// Mirrors the exact original inline math from src/main.js loop(). Returns
// true the single frame boost-start shake fires (caller spawns the flare
// particle burst — that's a gameplay/VFX concern, not camera's).
export function updateCamera(focusX, focusY, focusVx, focusVy, boostActiveForShake) {
  _focusWorldX = focusX;
  _focusWorldY = focusY;

  const CAM_LEAD = 18, CAM_LAG = 0.09;
  camLeadX += (focusVx * CAM_LEAD - camLeadX) * CAM_LAG;
  camLeadY += (focusVy * CAM_LEAD - camLeadY) * CAM_LAG;
  camShakeX *= 0.74; camShakeY *= 0.74;

  camZoomTarget = ZOOM_LEVELS[camZoomIdx];
  camZoom += (camZoomTarget - camZoom) * ZOOM_LERP;

  let boostJustStarted = false;
  if (boostActiveForShake && !_prevBoosting) {
    addCameraShake(6);
    boostJustStarted = true;
  }
  _prevBoosting = boostActiveForShake;

  return boostJustStarted;
}

export function getCameraState() {
  return {
    camLeadX, camLeadY, camShakeX, camShakeY,
    zoom: camZoom, zoomTarget: camZoomTarget, zoomIdx: camZoomIdx,
  };
}

// Screen-center point the world is drawn around, BEFORE zoom scaling
// (this is the "cx, cy" used throughout the original draw*() functions).
export function getScreenCenter() {
  return {
    cx: Math.round(_canvas.width  / 2 - camLeadX + camShakeX),
    cy: Math.round(_canvas.height / 2 - camLeadY + camShakeY),
  };
}

// ── World <-> Screen conversion — the single authoritative transform pair. ──
// Derived from the exact composed canvas transform used at render time:
//   ctx.translate(zcx,zcy); ctx.scale(zoom,zoom); ctx.translate(-zcx,-zcy)
// applied on top of the unscaled per-object screen position
//   unscaled = (cx,cy) + (worldPos - focusWorldPos)
// worldToScreen/screenToWorld below are algebraically exact inverses of that
// composed transform (verified via round-trip regression, see
// _dev/camera_roundtrip_verify.mjs).
export function worldToScreen(worldX, worldY) {
  const zcx = _canvas.width / 2, zcy = _canvas.height / 2;
  const { cx, cy } = getScreenCenter();
  const unscaledX = cx + (worldX - _focusWorldX);
  const unscaledY = cy + (worldY - _focusWorldY);
  return {
    x: zcx + (unscaledX - zcx) * camZoom,
    y: zcy + (unscaledY - zcy) * camZoom,
  };
}

export function screenToWorld(screenX, screenY) {
  const zcx = _canvas.width / 2, zcy = _canvas.height / 2;
  const { cx, cy } = getScreenCenter();
  const unscaledX = zcx + (screenX - zcx) / camZoom;
  const unscaledY = zcy + (screenY - zcy) / camZoom;
  return {
    x: _focusWorldX + (unscaledX - cx),
    y: _focusWorldY + (unscaledY - cy),
  };
}

// ── World-zoom transform apply/restore (identical math, both call sites in
//    src/main.js loop() — world objects, then ship — used this verbatim). ──
export function applyWorldTransform(ctx) {
  const zcx = _canvas.width / 2, zcy = _canvas.height / 2;
  ctx.save();
  ctx.translate(zcx, zcy);
  ctx.scale(camZoom, camZoom);
  ctx.translate(-zcx, -zcy);
}

export function restoreWorldTransform(ctx) {
  ctx.restore();
}
