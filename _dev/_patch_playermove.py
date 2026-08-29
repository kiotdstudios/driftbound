import re

f = open('driftbound_flight_test.html', 'rb')
raw = f.read()
f.close()
d = raw.decode('utf-8', 'replace')

old = "    case 'player_left':\r\n      delete remotePlayers[msg.pid];"
new = "    case 'player_move':\r\n      if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player;\r\n      break;\r\n\r\n    case 'player_left':\r\n      delete remotePlayers[msg.pid];"

if old in d:
    d = d.replace(old, new)
    print('patched exact')
else:
    # LF fallback
    old2 = "    case 'player_left':\n      delete remotePlayers[msg.pid];"
    new2 = "    case 'player_move':\n      if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player;\n      break;\n\n    case 'player_left':\n      delete remotePlayers[msg.pid];"
    if old2 in d:
        d = d.replace(old2, new2)
        print('patched LF')
    else:
        d = re.sub(
            r"(case 'player_left':\s*\r?\n\s*delete remotePlayers)",
            "case 'player_move':\r\n      if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player;\r\n      break;\r\n\r\n    case 'player_left':\r\n      delete remotePlayers",
            d
        )
        print('patched regex')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('player_move in client:', "'player_move'" in d)
