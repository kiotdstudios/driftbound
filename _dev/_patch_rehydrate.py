with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# ── 1. Inject rehydrateAsteroid helper right after ASTEROID_TYPES definition ──
helper = """\r\n\r\n// Rehydrate a server asteroid: attach full type object from ASTEROID_TYPES by type_id\r\nfunction rehydrateAsteroid(a) {\r\n  if (a.type && a.type.w) return a;  // already has full type, nothing to do\r\n  const t = ASTEROID_TYPES.find(t => t.id === a.type_id);\r\n  if (t) a.type = t;\r\n  // Ensure maxHp exists\r\n  if (!a.maxHp && t) a.maxHp = t.hp;\r\n  return a;\r\n}"""

marker = 'const ASTEROID_POOL'
if 'function rehydrateAsteroid' not in d:
    idx = d.find(marker)
    if idx != -1:
        # go back to start of that line
        line_start = d.rfind('\n', 0, idx) + 1
        d = d[:line_start] + helper + '\r\n\r\n' + d[line_start:]
        print('rehydrateAsteroid: injected')
    else:
        print('rehydrateAsteroid: marker not found')
else:
    print('rehydrateAsteroid: already present')

# ── 2. Fix init case: rehydrate each asteroid from server ──
old_init_ast = 'for (const a of msg.asteroids) serverAsteroids[a.aid] = a;'
new_init_ast = 'for (const a of msg.asteroids) serverAsteroids[a.aid] = rehydrateAsteroid(a);'
if old_init_ast in d:
    d = d.replace(old_init_ast, new_init_ast)
    print('init rehydrate: patched')
else:
    print('init rehydrate: no match')

# ── 3. Fix asteroid_destroyed case: rehydrate new_ast ──
old_destroyed = 'serverAsteroids[msg.new_ast.aid] = msg.new_ast;'
new_destroyed  = 'serverAsteroids[msg.new_ast.aid] = rehydrateAsteroid(msg.new_ast);'
if old_destroyed in d:
    d = d.replace(old_destroyed, new_destroyed)
    print('destroyed rehydrate: patched')
else:
    print('destroyed rehydrate: no match')

# ── 4. Fix asteroid_sync case: rehydrate on position update ──
old_sync = """    case 'asteroid_sync':\r\n      for (const a of msg.asteroids) {\r\n        if (serverAsteroids[a.aid]) {\r\n          serverAsteroids[a.aid].worldX = a.worldX;\r\n          serverAsteroids[a.aid].worldY = a.worldY;\r\n          serverAsteroids[a.aid].angle  = a.angle;\r\n        }\r\n      }\r\n      break;"""
new_sync = """    case 'asteroid_sync':\r\n      for (const a of msg.asteroids) {\r\n        if (serverAsteroids[a.aid]) {\r\n          serverAsteroids[a.aid].worldX = a.worldX;\r\n          serverAsteroids[a.aid].worldY = a.worldY;\r\n          serverAsteroids[a.aid].angle  = a.angle;\r\n          rehydrateAsteroid(serverAsteroids[a.aid]);\r\n        } else {\r\n          // New asteroid we don't have yet — add and rehydrate\r\n          serverAsteroids[a.aid] = rehydrateAsteroid(a);\r\n        }\r\n      }\r\n      break;"""

if old_sync in d:
    d = d.replace(old_sync, new_sync)
    print('sync rehydrate: patched')
else:
    print('sync rehydrate: no match — trying LF')
    old_sync2 = "    case 'asteroid_sync':\n      for (const a of msg.asteroids) {\n        if (serverAsteroids[a.aid]) {\n          serverAsteroids[a.aid].worldX = a.worldX;\n          serverAsteroids[a.aid].worldY = a.worldY;\n          serverAsteroids[a.aid].angle  = a.angle;\n        }\n      }\n      break;"
    new_sync2 = "    case 'asteroid_sync':\n      for (const a of msg.asteroids) {\n        if (serverAsteroids[a.aid]) {\n          serverAsteroids[a.aid].worldX = a.worldX;\n          serverAsteroids[a.aid].worldY = a.worldY;\n          serverAsteroids[a.aid].angle  = a.angle;\n          rehydrateAsteroid(serverAsteroids[a.aid]);\n        } else {\n          serverAsteroids[a.aid] = rehydrateAsteroid(a);\n        }\n      }\n      break;"
    if old_sync2 in d:
        d = d.replace(old_sync2, new_sync2)
        print('sync rehydrate: patched (LF)')
    else:
        # just find and show
        idx = d.find("case 'asteroid_sync':")
        print(repr(d[idx:idx+300]))

# ── 5. Guard collision loop: skip asteroids without a valid type ──
# The for loop over getAsteroids() in collision — add a guard at the top
old_collision = "    for (const ast of getAsteroids()) {\r\n\r\n      const dx   = ast.worldX - ship.worldX;"
new_collision = "    for (const ast of getAsteroids()) {\r\n      if (!ast.type || !ast.type.w) continue;  // skip if not yet rehydrated\r\n\r\n      const dx   = ast.worldX - ship.worldX;"
if old_collision in d:
    d = d.replace(old_collision, new_collision)
    print('collision guard: patched')
else:
    print('collision guard: no match (LF?)')
    old_c2 = "    for (const ast of getAsteroids()) {\n\n      const dx   = ast.worldX - ship.worldX;"
    new_c2 = "    for (const ast of getAsteroids()) {\n      if (!ast.type || !ast.type.w) continue;\n\n      const dx   = ast.worldX - ship.worldX;"
    if old_c2 in d:
        d = d.replace(old_c2, new_c2)
        print('collision guard: patched (LF)')
    else:
        print('collision guard: STILL no match')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print()
print('=== VERIFY ===')
print('rehydrateAsteroid fn:', 'function rehydrateAsteroid' in d)
print('init rehydrates:', 'rehydrateAsteroid(a)' in d)
print('sync rehydrates:', 'rehydrateAsteroid(serverAsteroids' in d)
print('collision guard:', '!ast.type || !ast.type.w' in d)
