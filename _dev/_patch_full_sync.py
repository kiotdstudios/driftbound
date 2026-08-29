with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

sync_case = "\r\n\r\n    case 'asteroid_sync':\r\n      for (const a of msg.asteroids) {\r\n        if (serverAsteroids[a.aid]) {\r\n          serverAsteroids[a.aid].worldX = a.worldX;\r\n          serverAsteroids[a.aid].worldY = a.worldY;\r\n          serverAsteroids[a.aid].angle  = a.angle;\r\n        }\r\n      }\r\n      break;"

target = "      serverAsteroids[msg.new_ast.aid] = msg.new_ast;\r\n      break;\r\n\r\n    case 'ore_collected':"
replacement = "      serverAsteroids[msg.new_ast.aid] = msg.new_ast;\r\n      break;" + sync_case + "\r\n\r\n    case 'ore_collected':"

if target in d:
    d = d.replace(target, replacement)
    print('injected')
else:
    print('no match — showing ore_collected context:')
    idx = d.find("case 'ore_collected'")
    print(repr(d[max(0,idx-200):idx+50]))

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('asteroid_sync present:', "case 'asteroid_sync'" in d)
