with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# ── 1. Remove the PVP consts from their current wrong location ──
old_pvp_block = ("const PVP_COLLISION_R  = COLLISION_RADIUS * 2;  // ship-to-ship hit radius\r\n"
                 "const PVP_DAMAGE       = 6;   // hull damage per ship collision\r\n"
                 "const PVP_IFRAMES      = 90;  // longer iframes after pvp hit\r\n"
                 "const PVP_BOUNCE       = 0.6; // harder bounce than asteroid")

if old_pvp_block in d:
    d = d.replace(old_pvp_block, "// PVP constants moved below COLLISION_RADIUS")
    print('PVP block removed from wrong location')
else:
    print('PVP block: no CRLF match, trying LF')
    old_pvp_lf = ("const PVP_COLLISION_R  = COLLISION_RADIUS * 2;  // ship-to-ship hit radius\n"
                  "const PVP_DAMAGE       = 6;   // hull damage per ship collision\n"
                  "const PVP_IFRAMES      = 90;  // longer iframes after pvp hit\n"
                  "const PVP_BOUNCE       = 0.6; // harder bounce than asteroid")
    if old_pvp_lf in d:
        d = d.replace(old_pvp_lf, "// PVP constants moved below COLLISION_RADIUS")
        print('PVP block removed (LF)')
    else:
        print('PVP block: STILL no match')

# ── 2. Insert PVP consts right AFTER COLLISION_RADIUS = 28 ──
old_cr = "const COLLISION_RADIUS = 28;"
new_cr  = ("const COLLISION_RADIUS = 28;\r\n"
           "const PVP_COLLISION_R  = COLLISION_RADIUS * 2;  // ship-to-ship hit radius\r\n"
           "const PVP_DAMAGE       = 6;    // hull damage per ship collision\r\n"
           "const PVP_IFRAMES      = 90;   // invincibility frames after pvp hit\r\n"
           "const PVP_BOUNCE       = 0.6;  // harder bounce than asteroid")

if old_cr in d:
    d = d.replace(old_cr, new_cr)
    print('PVP consts re-inserted after COLLISION_RADIUS')
else:
    print('COLLISION_RADIUS line: no match')

# ── 3. Fix socket TDZ — change `let socket = null` to `var socket = null`
# var is function-scoped and hoisted without TDZ, safe for this pattern
old_socket = "let socket        = null;"
new_socket  = "var socket        = null;  // var avoids TDZ with lobbyConnect"
if old_socket in d:
    d = d.replace(old_socket, new_socket)
    print('socket: let → var')
else:
    # try without extra spaces
    old_s2 = "let socket = null;"
    if old_s2 in d:
        d = d.replace(old_s2, "var socket = null;  // var avoids TDZ")
        print('socket: let → var (compact)')
    else:
        print('socket let: no match — checking')
        import re
        for m in re.finditer(r'let socket', d):
            print(f'  found at offset {m.start()}: {repr(d[m.start():m.start()+40])}')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print()
print('=== VERIFY ===')
# Check order: COLLISION_RADIUS before PVP_COLLISION_R
cr_idx  = d.find('const COLLISION_RADIUS = 28')
pvp_idx = d.find('const PVP_COLLISION_R')
print(f'COLLISION_RADIUS at {cr_idx}, PVP_COLLISION_R at {pvp_idx}')
print('Order OK:', cr_idx < pvp_idx)
print('socket is var:', 'var socket' in d)
print('let socket gone:', 'let socket' not in d)
