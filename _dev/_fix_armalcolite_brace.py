data = open('driftbound_flight_test.html','rb').read()

# Current broken block:
# if (ship.armalcolite > 0) {
#     if (multiMode) {
#       sendRefine();
#     } else {
#       ...
#     }
#   }   <-- this closes keys['KeyC'], NOT armalcolite > 0
# 
# Need one more } to close ship.armalcolite > 0

old = (b"    if (ship.armalcolite > 0) {\r\n"
       b"    if (multiMode) {\r\n"
       b"      sendRefine();\r\n"
       b"    } else {\r\n"
       b"      // Solo mode refine\r\n"
       b"      const gained = FUEL_PER_CRAFT;\r\n"
       b"      ship.armalcolite -= 1;\r\n"
       b"      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
       b"      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\r\n"
       b"    }\r\n"
       b"\r\n"
       b"  }")

new = (b"    if (ship.armalcolite > 0) {\r\n"
       b"      if (multiMode) {\r\n"
       b"        sendRefine();\r\n"
       b"      } else {\r\n"
       b"        // Solo mode refine\r\n"
       b"        const gained = FUEL_PER_CRAFT;\r\n"
       b"        ship.armalcolite -= 1;\r\n"
       b"        ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
       b"        showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\r\n"
       b"      }\r\n"
       b"      craftCooldown = 30;\r\n"
       b"    }\r\n"
       b"\r\n"
       b"  }")

if old in data:
    data = data.replace(old, new)
    print("Fixed: added missing } for armalcolite block")
else:
    print("Exact match failed, trying regex approach")
    import re as _re
    # Just insert a } after the inner block closes
    # Pattern: the } that closes multiMode/else is followed by \r\n\r\n  }
    # We need to add another } between them
    old2 = (b"    } else {\r\n"
            b"      // Solo mode refine\r\n"
            b"      const gained = FUEL_PER_CRAFT;\r\n"
            b"      ship.armalcolite -= 1;\r\n"
            b"      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
            b"      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\r\n"
            b"    }\r\n"
            b"\r\n"
            b"  }")
    new2 = (b"    } else {\r\n"
            b"      // Solo mode refine\r\n"
            b"      const gained = FUEL_PER_CRAFT;\r\n"
            b"      ship.armalcolite -= 1;\r\n"
            b"      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
            b"      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\r\n"
            b"    }\r\n"
            b"    craftCooldown = 30;\r\n"
            b"  }\r\n"
            b"\r\n"
            b"  }")
    if old2 in data:
        data = data.replace(old2, new2)
        print("Regex approach worked")
    else:
        print("Both patterns failed - manual search needed")
        # Show the area around the refine block
        idx = data.find(b'ship.armalcolite > 0')
        print(f"Found at byte {idx}")
        print(data[idx:idx+400])

open('driftbound_flight_test.html','wb').write(data)

# Verify
lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()
print("\n=== LINES 1098-1122 ===")
for i, l in enumerate(lines[1097:1122], start=1098):
    print(f'{i:4}: {l}', end='')
