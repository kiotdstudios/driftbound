data = open('driftbound_flight_test.html','rb').read()

# Find and replace the entire broken refine block
# It starts at the craftCooldown check and ends after the else block

old = (b"    if (multiMode) { sendRefine(); craftCooldown = 30; }\r\n"
       b"    else if (true) {\r\n"
       b"      const used   = 1;  // 1 armalcolite per refine\r\n"
       b"      const gained = FUEL_PER_CRAFT;\r\n"
       b"      ship.armalcolite -= used;\r\n"
       b"      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
       b"      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ' / ' + FUEL_CAPACITY + ')')\r\n"
       b"\r\n"
       b"    } else {\r\n"
       b"\r\n"
       b"      showToast('NEED ' + ORE_'ARMALCOLITE  \\u00b7  HAVE ' + ship.armalcolite);\r\n"
       b"\r\n"
       b"    }")

new = (b"    if (multiMode) {\r\n"
       b"      sendRefine();\r\n"
       b"    } else {\r\n"
       b"      // Solo mode refine\r\n"
       b"      const gained = FUEL_PER_CRAFT;\r\n"
       b"      ship.armalcolite -= 1;\r\n"
       b"      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\r\n"
       b"      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\r\n"
       b"    }")

if old in data:
    data = data.replace(old, new)
    print("Refine block fixed cleanly")
else:
    print("Exact match failed - using line-based replacement")
    # Read as text, find the block by line numbers and replace
    txt = data.decode('utf-8', errors='replace')
    lines = txt.split('\n')

    # Find the multiMode sendRefine line
    start_idx = None
    end_idx   = None
    for i, l in enumerate(lines):
        if 'if (multiMode) { sendRefine()' in l:
            start_idx = i
        if start_idx and i > start_idx and '    }' in l and end_idx is None:
            # find the closing } of the else block
            if i > start_idx + 8:
                end_idx = i
                break

    if start_idx and end_idx:
        print(f"Replacing lines {start_idx+1} to {end_idx+1}")
        replacement = [
            '    if (multiMode) {\n',
            '      sendRefine();\n',
            '    } else {\n',
            '      const gained = FUEL_PER_CRAFT;\n',
            '      ship.armalcolite -= 1;\n',
            '      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);\n',
            "      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ')');\n",
            '    }',
        ]
        lines[start_idx:end_idx+1] = replacement
        data = '\n'.join(lines).encode('utf-8')
        print("Line-based replacement done")
    else:
        print(f"Could not locate block: start={start_idx} end={end_idx}")

open('driftbound_flight_test.html','wb').write(data)

# Verify — show the refine area
lines2 = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()
print("\n=== REFINE BLOCK NOW ===")
for i, l in enumerate(lines2):
    if 'sendRefine' in l:
        for j in range(max(0,i-2), min(len(lines2), i+14)):
            print(f'{j+1:4}: {lines2[j]}', end='')
        break

# Also check line 1113 area
print("\n=== LINE 1108-1120 NOW ===")
for i, l in enumerate(lines2[1107:1122], start=1108):
    print(f'{i:4}: {l}', end='')
