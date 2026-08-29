with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# ── 1. Ship type definition + cargo cap constant ──
ship_type_def = """\r\n// ─── SHIP TYPES ─────────────────────────────────────────────────────────────\r\n// Each ship has a name, cargo cap, and which cargo types it accepts.\r\n// Future ships can restrict to one type (e.g. fuel-only freighter).\r\nconst SHIP_TYPES = {\r\n  vagrant: {\r\n    name:       'VAGRANT',\r\n    cargoLimit: 50,\r\n    accepts:    ['ore', 'armalcolite'],   // Nebulite + Armalcolite share hold\r\n    desc:       'General-purpose miner. Carries 50 units of mixed mineral cargo.'\r\n  },\r\n};\r\n\r\nconst SHIP_TYPE    = SHIP_TYPES.vagrant;\r\nconst CARGO_LIMIT  = SHIP_TYPE.cargoLimit;\r\n"""

# Insert after ASTEROID_TYPES block (before ASTEROID_POOL or rehydrate)
marker = '// Rehydrate a server asteroid'
if 'SHIP_TYPES' not in d:
    idx = d.find(marker)
    if idx != -1:
        d = d[:idx] + ship_type_def + '\r\n' + d[idx:]
        print('SHIP_TYPES: injected')
    else:
        # fallback: insert before const ASTEROID_POOL
        marker2 = 'const ASTEROID_POOL'
        idx2 = d.find(marker2)
        if idx2 != -1:
            d = d[:idx2] + ship_type_def + '\r\n' + d[idx2:]
            print('SHIP_TYPES: injected (fallback marker)')
        else:
            print('SHIP_TYPES: no marker found')
else:
    print('SHIP_TYPES: already present')

# ── 2. Add shipType to ship object ──
old_ship_ore = "  ore:        0,   // Nebulite ore in cargo"
new_ship_ore  = "  shipType:   SHIP_TYPE,  // which ship this is\r\n  ore:        0,   // Nebulite ore in cargo"
if old_ship_ore in d:
    d = d.replace(old_ship_ore, new_ship_ore)
    print('ship.shipType: added')
else:
    print('ship.shipType: no match')

# ── 3. Cargo total helper ──
cargo_helper = """\r\n// Total cargo units used (Nebulite + Armalcolite share the hold)\r\nfunction cargoUsed() { return ship.ore + ship.armalcolite; }\r\nfunction cargoFull()  { return cargoUsed() >= CARGO_LIMIT; }\r\n"""
if 'function cargoUsed' not in d:
    # insert before the rehydrateAsteroid function
    marker3 = 'function rehydrateAsteroid'
    idx3 = d.find(marker3)
    if idx3 != -1:
        d = d[:idx3] + cargo_helper + '\r\n' + d[idx3:]
        print('cargoUsed helper: injected')
    else:
        print('cargoUsed helper: marker not found')
else:
    print('cargoUsed helper: already present')

# ── 4. Block local ore pickup when cargo is full ──
old_pickup = "    if (d < ORE_COLLECT_R) {\r\n\r\n      ship.ore += ore.amount;"
new_pickup  = "    if (d < ORE_COLLECT_R) {\r\n      const space = CARGO_LIMIT - cargoUsed();\r\n      if (space <= 0) { showToast('⚠ CARGO FULL — ' + cargoUsed() + '/' + CARGO_LIMIT, '#ef4444'); orePickups.splice(i, 1); continue; }\r\n      const take = Math.min(ore.amount, space);\r\n\r\n      ship.ore += take;"
if old_pickup in d:
    d = d.replace(old_pickup, new_pickup)
    # fix the toast to show take not ore.amount
    d = d.replace("showToast('+' + ore.amount + ' NEBULITE')", "showToast('+' + take + ' NEBULITE  [' + cargoUsed() + '/' + CARGO_LIMIT + ']')")
    print('ore pickup cap: patched')
else:
    # try LF
    old_p2 = "    if (d < ORE_COLLECT_R) {\n\n      ship.ore += ore.amount;"
    new_p2  = "    if (d < ORE_COLLECT_R) {\n      const space = CARGO_LIMIT - cargoUsed();\n      if (space <= 0) { showToast('⚠ CARGO FULL — ' + cargoUsed() + '/' + CARGO_LIMIT, '#ef4444'); orePickups.splice(i, 1); continue; }\n      const take = Math.min(ore.amount, space);\n\n      ship.ore += take;"
    if old_p2 in d:
        d = d.replace(old_p2, new_p2)
        d = d.replace("showToast('+' + ore.amount + ' NEBULITE')", "showToast('+' + take + ' NEBULITE  [' + cargoUsed() + '/' + CARGO_LIMIT + ']')")
        print('ore pickup cap: patched (LF)')
    else:
        print('ore pickup cap: no match')

# ── 5. Block armalcolite loot drop if cargo full ──
old_arm_loot = "        } else if (ore.lootType === 'armalcolite') {\r\n          ship.armalcolite++;\r\n          showToast('◈ ARMALCOLITE extracted — refine for fuel (' + ship.armalcolite + ' held)', '#34d399');"
new_arm_loot  = "        } else if (ore.lootType === 'armalcolite') {\r\n          if (cargoUsed() < CARGO_LIMIT) {\r\n            ship.armalcolite++;\r\n            showToast('◈ ARMALCOLITE extracted — refine for fuel [' + cargoUsed() + '/' + CARGO_LIMIT + ']', '#34d399');\r\n          } else {\r\n            showToast('⚠ CARGO FULL — ARMALCOLITE lost', '#ef4444');\r\n          }"
if old_arm_loot in d:
    d = d.replace(old_arm_loot, new_arm_loot)
    print('armalcolite cap: patched')
else:
    old_arm2 = "        } else if (ore.lootType === 'armalcolite') {\n          ship.armalcolite++;\n          showToast('◈ ARMALCOLITE extracted — refine for fuel (' + ship.armalcolite + ' held)', '#34d399');"
    new_arm2  = "        } else if (ore.lootType === 'armalcolite') {\n          if (cargoUsed() < CARGO_LIMIT) {\n            ship.armalcolite++;\n            showToast('◈ ARMALCOLITE extracted — refine for fuel [' + cargoUsed() + '/' + CARGO_LIMIT + ']', '#34d399');\n          } else {\n            showToast('⚠ CARGO FULL — ARMALCOLITE lost', '#ef4444');\n          }"
    if old_arm2 in d:
        d = d.replace(old_arm2, new_arm2)
        print('armalcolite cap: patched (LF)')
    else:
        print('armalcolite cap: no match')

# ── 6. Upgrade HUD: show ship name, cargo bar ──
# Replace the CARGO label section with a richer block
old_cargo_hud = "  ctx.fillText('CARGO', LEFT, oreY);"
new_cargo_hud = (
    "  // Ship name header\r\n"
    "  ctx.font = 'bold 9px Courier New'; ctx.fillStyle = '#4FC3C3';\r\n"
    "  ctx.fillText('⬡ ' + ship.shipType.name, LEFT, oreY - 2);\r\n"
    "  // Cargo bar\r\n"
    "  const cUsed = cargoUsed(), cMax = CARGO_LIMIT, cbw = PW - 36;\r\n"
    "  const cPct  = Math.min(cUsed / cMax, 1);\r\n"
    "  const cFull = cUsed >= cMax;\r\n"
    "  ctx.font = HUD_FONT_SM;\r\n"
    "  ctx.fillStyle = cFull ? '#ef4444' : HUD_DIM;\r\n"
    "  ctx.fillText('CARGO  ' + cUsed + '/' + cMax + (cFull ? '  ■ FULL' : ''), LEFT, oreY + 12);\r\n"
    "  ctx.fillStyle = '#0d1520'; ctx.fillRect(LEFT-1, oreY+15, cbw+2, 5);\r\n"
    "  const cGrad = ctx.createLinearGradient(LEFT, 0, LEFT+cbw, 0);\r\n"
    "  if (cPct < 0.7)       { cGrad.addColorStop(0,'#4FC3C3'); cGrad.addColorStop(1,'#22aacc'); }\r\n"
    "  else if (cPct < 0.95) { cGrad.addColorStop(0,'#D9541E'); cGrad.addColorStop(1,'#ffaa44'); }\r\n"
    "  else                  { cGrad.addColorStop(0,'#ff2222'); cGrad.addColorStop(1,'#ff6666'); }\r\n"
    "  ctx.fillStyle = cGrad; ctx.fillRect(LEFT, oreY+16, cbw * cPct, 3);\r\n"
    "  ctx.strokeStyle = '#ffffff18'; ctx.strokeRect(LEFT, oreY+16, cbw, 3);\r\n"
    "  ctx.fillText('CARGO', LEFT, oreY + 28);  // spacer label for layout"
)
if old_cargo_hud in d:
    d = d.replace(old_cargo_hud, new_cargo_hud)
    print('HUD cargo bar: patched')
else:
    print('HUD cargo bar: no match')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print()
print('=== VERIFY ===')
print('SHIP_TYPES:', 'const SHIP_TYPES' in d)
print('CARGO_LIMIT:', 'const CARGO_LIMIT' in d)
print('cargoUsed():', 'function cargoUsed' in d)
print('pickup cap:', 'CARGO_LIMIT - cargoUsed()' in d)
print('armalcolite cap:', 'CARGO FULL — ARMALCOLITE' in d)
print('HUD bar:', 'ship.shipType.name' in d)
