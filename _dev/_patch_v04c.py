txt = open('driftbound_flight_test.html', 'r', encoding='utf-8').read()
import re

# ─── 1. Ensure asteroid spawn stores type object reference (for loot lookup)
# Find where an asteroid is created and pushed into the asteroids array
# Pattern: find "type:" assignment in asteroid spawn using ASTEROID_TYPES[...]
# Replace with storing the full type object as ast.type
idx = txt.find('const pool = ASTEROID_POOL;')
if idx >= 0:
    print("Pool ref found, checking nearby spawn code...")
    print(txt[idx:idx+400])

# Look for the actual asteroid object creation
ast_push = txt.find('asteroids.push(')
if ast_push >= 0:
    print("\nasteroids.push found at", ast_push)
    print(txt[ast_push:ast_push+300])

# ─── 2. Add Mineral / Armalcolite text lines to HUD
# Find where fuel and ore are displayed as text in drawHUD
# Insert after the ore bar section

# Find the end of the ore bar drawing section
ore_bar_end_idx = txt.find('oreBarX-1, oreBarY-1')
if ore_bar_end_idx >= 0:
    # Find the closing of the ore bar block - look for next major HUD section
    # We want to insert MINERAL and ARMALCOLITE count lines after the ore bar
    # Find the area after ore bar fill
    after_ore = txt.find('ctx.fillStyle', ore_bar_end_idx + 100)
    print("\nAfter ore bar fillStyle at", after_ore)
    print(txt[after_ore:after_ore+300])

# Find where ore count is displayed as text (fillText with ship.ore)
ore_text_search = re.findall(r'[^\n]{0,40}ship\.ore[^\n]{0,80}', txt)
print("\nAll ship.ore text refs:")
for r in ore_text_search:
    print(repr(r))
