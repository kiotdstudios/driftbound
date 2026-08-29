data = open('driftbound_flight_test.html','rb').read()
import re

# Find the return Math.hypot in update()
upd_start = data.find(b'function update(')
upd_slice = data[upd_start:upd_start+5000]

ret_idx = upd_slice.find(b'return Math')
print('return line:')
print(repr(upd_slice[ret_idx:ret_idx+100]))

# Get everything from start of that line
line_start = upd_slice.rfind(b'\n', 0, ret_idx) + 1
print('full line:')
print(repr(upd_slice[line_start:ret_idx+80]))

# Now build the patch — inject before the return
old_bytes = upd_slice[line_start:ret_idx + upd_slice.find(b'\r\n', ret_idx) + 2]
print('\nold_bytes:')
print(repr(old_bytes))

inject = (b'  _thrusting = thrusting;\r\n'
          b'  _boosting  = shiftHeld;\r\n'
          b'  if (typeof multiMode !== "undefined" && multiMode) sendMove();\r\n')

new_bytes = inject + old_bytes

# Apply patch to full file
abs_line_start = upd_start + line_start
abs_old_end    = upd_start + line_start + len(old_bytes)
patched = data[:abs_line_start] + new_bytes + data[abs_old_end:]

# ─── Also add pilot count to HUD panel
# Find where ore MINERAL line is drawn (we added it) — add pilots line after armalcolite
armalcolite_text = b'ARMALCOLITE\', LEFT + 30, armY);'
idx_arm = patched.find(armalcolite_text)
if idx_arm >= 0:
    end_arm = patched.find(b'\r\n', idx_arm) + 2
    pilot_block = (b'\r\n'
                   b'  // Pilot count (multiplayer only)\r\n'
                   b'  if (typeof multiMode !== "undefined" && multiMode) {\r\n'
                   b'    const pilotY = armY + 22;\r\n'
                   b'    ctx.fillStyle = \'#38bdf8\';\r\n'
                   b'    ctx.font = \'bold 11px monospace\';\r\n'
                   b'    ctx.fillText(\'\\u25a0\', LEFT + 14, pilotY);\r\n'
                   b'    ctx.font = \'11px monospace\';\r\n'
                   b"    ctx.fillText((Object.keys(remotePlayers).length + 1) + ' PILOTS ONLINE', LEFT + 30, pilotY);\r\n"
                   b'  }\r\n')
    patched = patched[:end_arm] + pilot_block + patched[end_arm:]
    print('Pilot count HUD added')
else:
    print('WARNING: armalcolite HUD line not found')

open('driftbound_flight_test.html','wb').write(patched)
print('\n=== FINAL WIRE COMPLETE ===')

# Verify
final = patched.decode('utf-8','ignore')
for token, label in [
    ('sendMove()',     'sendMove call'),
    ('_thrusting',    '_thrusting flag'),
    ('PILOTS ONLINE', 'pilot HUD'),
    ('drawPlayerIndicator', 'indicator fn'),
    ('8766',          'WS port'),
]:
    print(f'  {label}: {"OK" if token in final else "MISSING"}')
