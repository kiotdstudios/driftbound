// ════════════════════════════════════════════════════════
// DEV MONITOR — persistent dev log. Never blocks the game.
// Console API: DevLog.dump() | DevLog.errors() | DevLog.recent(n) | DevLog.clear()
// Stored in localStorage under key 'driftbound_devlog_v1' (separate from saves)
//
// PHASE 1 EXTRACTION (verbatim from src/main.js, no behavior changes).
// Owner: src/systems/devTools.js — single source of truth for DevLog.
// Public API: `DevLog` (named export + window.DevLog for console access).
// ════════════════════════════════════════════════════════
export const DevLog = (() => {
  const STORE_KEY  = 'driftbound_devlog_v1';
  const MAX_ENTRIES = 300;
  const ROTATE_TO   = 200;

  let _buf = [];
  try {
    const stored = localStorage.getItem(STORE_KEY);
    if (stored) { const p = JSON.parse(stored); if (Array.isArray(p)) _buf = p; }
  } catch(e) { _buf = []; }

  function _ts() {
    const d = new Date();
    return d.toLocaleTimeString('en-US',{hour12:false}) + '.' +
           String(d.getMilliseconds()).padStart(3,'0');
  }

  function _flush() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(_buf)); } catch(e) { /* never block */ }
  }

  function _write(level, system, message, ctx) {
    try {
      // Dedup: collapse consecutive identical entries; track count+lastTs instead of flooding
      if (_buf.length > 0) {
        const last = _buf[_buf.length - 1];
        if (last.system === system && last.message === message && last.level === level) {
          last.count  = (last.count || 1) + 1;
          last.lastTs = _ts();
          _flush();
          return;
        }
      }
      const entry = { ts:_ts(), level, system, message };
      if (ctx !== undefined) entry.ctx = ctx;
      _buf.push(entry);
      if (_buf.length >= MAX_ENTRIES) {
        _buf = _buf.slice(_buf.length - ROTATE_TO);
        _buf.unshift({ ts:_ts(), level:'INFO', system:'DevLog',
          message:`[rotated — keeping newest ${ROTATE_TO} entries]` });
      }
      _flush();
      if (level === 'CRITICAL' || level === 'ERROR')
        console.error(`[DB ${level}][${system}] ${message}`, ctx||'');
      else if (level === 'WARNING')
        console.warn(`[DB WARNING][${system}] ${message}`, ctx||'');
    } catch(e) { /* logging must never throw */ }
  }

  const api = {
    info    : (s,m,c) => _write('INFO',     s, m, c),
    warn    : (s,m,c) => _write('WARNING',  s, m, c),
    error   : (s,m,c) => _write('ERROR',    s, m, c),
    critical: (s,m,c) => _write('CRITICAL', s, m, c),

    dump   : ()   => { console.table(_buf); return [..._buf]; },
    errors : ()   => { const e=_buf.filter(x=>x.level==='ERROR'||x.level==='CRITICAL');
                       console.table(e); return e; },
    recent : (n=20) => { const r=_buf.slice(-(n||20)); console.table(r); return r; },
    clear  : ()   => { _buf=[]; _flush(); console.log('[DevLog] cleared'); },
    get entries()    { return [..._buf]; },
    get errorCount() { return _buf.filter(x=>x.level==='ERROR'||x.level==='CRITICAL').length; },
  };

  window.DevLog = api;
  return api;
})();

DevLog.info('DevLog', 'Session started', { href: location.href, ts: new Date().toISOString() });
