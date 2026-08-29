raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

# ── 1. Wrap the [E] mine handler to also trigger interior entry ──
OLD_E = "  if (keys['KeyE'] && mineTarget) {\r\n"
NEW_E = """  // [E] — interior entry (near attached pod) or mine
  if (keys['KeyE'] && !interiorMode && interiorFadeDir === 0 && attachedPods.length > 0) {
    // check proximity to any attached pod (drawn ~42-80px from ship centre)
    const _cx = canvas.width/2, _cy = canvas.height/2;
    const _DIR_OFF = {
      north:{ox:0,oy:38},northeast:{ox:-27,oy:27},east:{ox:-38,oy:0},
      southeast:{ox:-27,oy:-27},south:{ox:0,oy:-38},southwest:{ox:27,oy:-27},
      west:{ox:38,oy:0},northwest:{ox:27,oy:27},
    };
    const _off = _DIR_OFF[ship.dir] || {ox:0,oy:38};
    for (let _pi = 0; _pi < attachedPods.length; _pi++) {
      const _dist = 42 + _pi*36, _ratio = _dist/38;
      const _pdx = _off.ox*_ratio, _pdy = _off.oy*_ratio;
      if (Math.hypot(_pdx, _pdy) < 100) {
        interiorPodIdx = _pi;
        interiorFadeDir = 1;
        iPlayerX = 4.5; iPlayerY = 6.5;
        break;
      }
    }
  }
  if (keys['KeyE'] && mineTarget) {\r\n"""

if OLD_E in d:
    d = d.replace(OLD_E, NEW_E, 1)
    print('OK E key handler updated')
else:
    print('E key anchor not found, trying CRLF variant')
    OLD_E2 = "  if (keys['KeyE'] && mineTarget) {\n"
    if OLD_E2 in d:
        d = d.replace(OLD_E2, NEW_E.replace('\r\n','\n'), 1)
        print('OK E key handler updated (LF)')
    else:
        import re
        idx = [m.start() for m in re.finditer(r"keys\['KeyE'\]", d)]
        print('KeyE positions:', idx)
        if idx:
            print(repr(d[idx[0]-5:idx[0]+80]))

# ── 2. Fix gameLoop drawHUD call anchor ──
OLD_LOOP = '  drawHUD(speed);\r\n'
NEW_LOOP = '''  drawHUD(speed);

  // ── INTERIOR FADE + RENDER ──
  if (interiorFadeDir === 1) {
    interiorFade = Math.min(1, interiorFade + FADE_SPEED);
    if (interiorFade >= 1) { interiorMode = true; interiorFadeDir = 0; }
  } else if (interiorFadeDir === -1) {
    interiorFade = Math.max(0, interiorFade - FADE_SPEED);
    if (interiorFade <= 0) { interiorMode = false; interiorFadeDir = 0; interiorPodIdx = -1; }
  }
  if (interiorFadeDir !== 0 && !interiorMode) {
    ctx.fillStyle = `rgba(0,0,0,${interiorFadeDir===1 ? interiorFade : 1-interiorFade})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  if (interiorMode) {
    updateInteriorPlayer();
    drawInterior();
    if (interiorFade < 1) {
      ctx.fillStyle = `rgba(0,0,0,${1 - interiorFade})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
  }\r\n'''

if OLD_LOOP in d:
    d = d.replace(OLD_LOOP, NEW_LOOP, 1)
    print('OK gameLoop interior render injected')
else:
    OLD_LOOP2 = '  drawHUD(speed);\n'
    if OLD_LOOP2 in d:
        d = d.replace(OLD_LOOP2, NEW_LOOP.replace('\r\n','\n'), 1)
        print('OK gameLoop interior render injected (LF)')
    else:
        print('drawHUD(speed) anchor not found')

# ── 3. Add E key interior exit on keyup ──
# find keyup handler for E — look for mineTarget=null
import re
m = re.search(r"mineTarget\s*=\s*null\s*;", d)
if m:
    old_s = d[m.start():m.end()]
    new_s = old_s + ' _ePressed = false;'
    d = d.replace(old_s, new_s, 1)
    print('OK mineTarget reset + _ePressed cleared')

    # also add interior exit on keyup E
    OLD_MINE_NULL = old_s + ' _ePressed = false;'
    NEW_MINE_NULL = OLD_MINE_NULL  # already set, now add exit check nearby — find keyup 'E' context
    # inject exit trigger near keyup block
    KEYUP_ANCHOR = 'mineTarget = null; _ePressed = false;'
    KEYUP_INJECT = '''mineTarget = null; _ePressed = false;
      // exit interior if standing on door tile
      if (interiorMode && Math.floor(iPlayerX) === DOOR_COL && Math.floor(iPlayerY) === DOOR_ROW) {
        interiorFadeDir = -1;
      }'''
    d = d.replace(KEYUP_ANCHOR, KEYUP_INJECT, 1)
    print('OK interior exit on keyup E added')
else:
    print('mineTarget=null not found')

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
print('Done.')
