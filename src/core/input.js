// ═══════════════════════════════════════════════════════════════════════════
// CENTRALIZED INPUT — src/core/input.js  (Phase 2 extraction, see MIGRATION_PLAN.md)
// Single owner of: keydown/keyup listeners, held-key state, E edge-trigger,
// focus/blur input clearing, mouse screen position, wheel capture.
// Does NOT decide what a key means (no gameplay/dev effects, no camera zoom
// math, no cheat execution) — callers poll/subscribe and decide.
// "Input may say: Slash was pressed. Gameplay/dev systems decide: restore
// fuel." — ownership separation per chief brief.
//
// Logic below is preserved verbatim from src/main.js (behavior-preserving
// extraction only): held-key map, E edge-trigger, preventDefault list,
// input log, blur/visibilitychange clearing, mouse tracking, wheel capture.
// ═══════════════════════════════════════════════════════════════════════════

// ── Held-key state. Exported as a live object (not a copy) so existing
//    call sites across main.js (`keys['KeyW']`) keep working unchanged —
//    deliberate low-risk choice for this behavior-preserving phase. New/
//    future consumers (Camera, HUD, interaction phases) should prefer the
//    explicit isHeld() query below instead of reaching into this object. ──
export const keys = {};

// ── E edge-trigger. Kept module-private; exposed via isEEdge()/clearEEdge()
//    because callers need to WRITE (clear) it, and an imported `let`/`var`
//    binding cannot be reassigned from outside its own module. ──
let eEdge = false;
export function isEEdge()    { return eEdge; }
export function clearEEdge() { eEdge = false; }

// ── Input event log (DEV F1 debug panel "LAST 8 INPUTS" + "KEYS HELD"). ──
export const INPUT_LOG_MAX = 30;       // keep last 30 input events
export const inputLog = [];            // [{t, type, code}]

// ── Mouse screen position (raw, CSS px). ──
let _mouseX = 0, _mouseY = 0, _mouseDX = 0, _mouseDY = 0;
export function getMousePosition() {
  return { x: _mouseX, y: _mouseY, dx: _mouseDX, dy: _mouseDY };
}

// ── Explicit query API — preferred surface for new/future consumers. ──
export function isHeld(code) { return !!keys[code]; }

// ── Subscriber hooks: input.js reports raw events; callers decide meaning. ──
const _keydownSubscribers = [];
const _wheelSubscribers    = [];
const _clearSubscribers    = [];
export function onKeyDown(fn) { _keydownSubscribers.push(fn); }
export function onWheel(fn)   { _wheelSubscribers.push(fn); }
export function onClear(fn)   { _clearSubscribers.push(fn); }

// Focus loss / tab switch must clear ALL held input so keys never "stick"
// (a stuck movement or Shift key would otherwise cause runaway thrust/boost).
export function clearAllInput() {
  for (const k in keys) keys[k] = false;
  eEdge = false;
  _clearSubscribers.forEach(fn => fn());
}

window.addEventListener('keydown', e => {
  keys[e.code] = true;

  if (e.code === 'KeyE' && !e.repeat) eEdge = true;

  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code))
    e.preventDefault();

  // Record for debugger
  inputLog.push({ t: Date.now(), type: 'keydown', code: e.code });
  if (inputLog.length > INPUT_LOG_MAX) inputLog.shift();

  _keydownSubscribers.forEach(fn => fn(e));
});

window.addEventListener('keyup', e => {
  keys[e.code] = false;

  inputLog.push({ t: Date.now(), type: 'keyup', code: e.code });
  if (inputLog.length > INPUT_LOG_MAX) inputLog.shift();
});

window.addEventListener('blur', clearAllInput);
document.addEventListener('visibilitychange', () => { if (document.hidden) clearAllInput(); });

// Mouse-wheel capture. input.js does not decide what wheel means (zoom, etc.)
// — the INPUT/TEXTAREA guard for "ignore wheel over menu text inputs" is
// kept at the point of use (the subscriber) since that is a decision about
// what the wheel does, not about capturing the raw event.
window.addEventListener('wheel', e => {
  _wheelSubscribers.forEach(fn => fn(e));
}, { passive: true });

// Mouse screen-position tracking. Call once with the game canvas.
export function initMouseTracking(canvas) {
  canvas.addEventListener('mousemove', e => {
    _mouseDX = e.clientX - _mouseX;
    _mouseDY = e.clientY - _mouseY;
    _mouseX  = e.clientX;
    _mouseY  = e.clientY;

    inputLog.push({ t: Date.now(), type: 'mouse', x: _mouseX, y: _mouseY, dx: _mouseDX, dy: _mouseDY });
    if (inputLog.length > INPUT_LOG_MAX) inputLog.shift();
  });
}
