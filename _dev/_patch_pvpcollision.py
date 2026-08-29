with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# Inject player_hit case right after the 'refined' case (last in the switch)
new_pvp_case = (
    "\r\n\r\n    case 'player_hit':\r\n"
    "      if (msg.pid === myPid) {\r\n"
    "        ship.hp         = Math.max(0, ship.hp - (msg.damage || PVP_DAMAGE));\r\n"
    "        ship.pvpIframes = PVP_IFRAMES;\r\n"
    "        ship.hitFlash   = 22;\r\n"
    "        const attacker  = remotePlayers[msg.by];\r\n"
    "        const aName     = attacker ? attacker.name : 'enemy';\r\n"
    "        showToast('HIT BY ' + aName + '  \u2502  HULL ' + ship.hp + '/' + SHIP_MAX_HP, '#ef4444');\r\n"
    "      }\r\n"
    "      break;"
)

# Find the 'refined' case break in the switch — it's the last case before closing
# Look for it specifically inside handleServerMsg
idx_fn = d.find('function handleServerMsg')
switch_body = d[idx_fn:idx_fn+4000]
refined_idx = switch_body.rfind("case 'refined'")
if refined_idx == -1:
    print("'refined' case not found in handleServerMsg")
else:
    # Find its break;
    break_idx = switch_body.find('break;', refined_idx)
    abs_break  = idx_fn + break_idx + len('break;')
    if "case 'player_hit'" not in d:
        d = d[:abs_break] + new_pvp_case + d[abs_break:]
        print("player_hit case: injected after 'refined'")
    else:
        print('player_hit case: already present')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

# Verify
import re
idx2 = d.find('function handleServerMsg')
cases = re.findall(r"case '(\w+)'", d[idx2:idx2+4000])
print('switch cases:', cases)
