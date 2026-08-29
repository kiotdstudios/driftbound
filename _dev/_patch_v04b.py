txt = open('driftbound_flight_test.html', 'r', encoding='utf-8').read()

# ─── 1. Add mineral + armalcolite fields to ship object
old_ship_ore = "ore:        0,   // Nebulite ore in cargo"
new_ship_ore = """ore:        0,   // Nebulite ore in cargo
  mineral:    0,   // Craftable mineral material (2% drop from brown asteroids)
  armalcolite:0,   // Fuel ore from lg_planet — refine with C key"""

if old_ship_ore in txt:
    txt = txt.replace(old_ship_ore, new_ship_ore)
    print("ship fields added")
else:
    print("WARNING: ship ore field not found")

# ─── 2. Inject loot drop after ore pickup: ship.ore += ore.amount
# Find the ore pickup block and inject after the showToast for Nebulite
old_ore_pickup = """ship.ore += ore.amount;

      showToast('+' + ore.amount + ' NEBULITE');

      orePickups.splice(i, 1);"""

new_ore_pickup = """ship.ore += ore.amount;

      showToast('+' + ore.amount + ' NEBULITE');

      // Loot drop — check parent asteroid's loot
      if (ore.lootType && Math.random() < ore.lootChance) {
        if (ore.lootType === 'mineral') {
          ship.mineral++;
          showToast('✦ MINERAL MATERIAL found! (' + ship.mineral + ' held)', '#a78bfa');
        } else if (ore.lootType === 'armalcolite') {
          ship.armalcolite++;
          showToast('◈ ARMALCOLITE extracted — refine for fuel (' + ship.armalcolite + ' held)', '#34d399');
        }
      }

      orePickups.splice(i, 1);"""

if old_ore_pickup in txt:
    txt = txt.replace(old_ore_pickup, new_ore_pickup)
    print("Loot drop injected into ore pickup")
else:
    print("WARNING: ore pickup block not matched")

# ─── 3. Pass lootType + lootChance onto ore pickups when spawned from asteroid
# Find where orePickups are created (spawnOre or similar)
# Look for the ore spawn: { worldX, worldY, amount ... }
import re
# Find the ore push pattern
ore_spawn_match = re.search(r'orePickups\.push\(\{[^}]*amount[^}]*\}\)', txt)
if ore_spawn_match:
    old_spawn = ore_spawn_match.group(0)
    print("ore spawn found:", repr(old_spawn[:80]))
    # Add lootType and lootChance from the parent asteroid (variable a)
    new_spawn = old_spawn.rstrip(')')
    # insert loot fields before closing brace
    new_spawn = new_spawn.rstrip('})')
    new_spawn += """,
        lootType: a.type.lootType || null,
        lootChance: a.type.lootChance || 0
      })"""
    txt = txt.replace(old_spawn, new_spawn, 1)
    print("Loot fields added to ore spawn")
else:
    print("WARNING: ore spawn push not found via regex - trying manual anchor")
    # Manual anchor: find where orePickups.push is
    idx = txt.find('orePickups.push(')
    if idx >= 0:
        print("Found orePickups.push at", idx)
        print(repr(txt[idx:idx+200]))

# ─── 4. Gate C-key refining on armalcolite instead of ore
old_refine_check = "if (ship.ore >= ORE_PER_FUEL) {"
new_refine_check  = "if (ship.armalcolite > 0) {"
if old_refine_check in txt:
    txt = txt.replace(old_refine_check, new_refine_check, 1)
    print("Refine gated to armalcolite")
else:
    print("WARNING: refine check not found")

# ─── 5. Update refine block to consume armalcolite + produce fuel
# Old: calculates batches from ore, deducts ship.ore
old_refine_body = """const batches ="""
# Find full refine block context
idx = txt.find('ship.ore  -= used;')
if idx >= 0:
    # replace the refine consumption
    old_consume = """const batches ="""
    # Get the full block
    block_start = txt.rfind('if (ship.armalcolite > 0)', 0, idx)
    block_end   = txt.find('showToast(', idx)
    block_end   = txt.find(';', block_end) + 1
    old_block = txt[block_start:block_end]
    print("Refine block found:")
    print(repr(old_block[:300]))

    new_refine_block = """if (ship.armalcolite > 0) {
      const used   = 1;  // 1 armalcolite per refine
      const gained = FUEL_PER_CRAFT;
      ship.armalcolite -= used;
      ship.fuel = Math.min(FUEL_CAPACITY, ship.fuel + gained);
      showToast('REFINED ARMALCOLITE \\u2192 +' + gained.toFixed(1) + ' FUEL  (' + ship.fuel.toFixed(1) + ' / ' + FUEL_CAPACITY + ')')"""

    txt = txt[:block_start] + new_refine_block + txt[block_end:]
    print("Refine block replaced")
else:
    print("WARNING: ship.ore -= used not found")

# ─── 6. Update asteroid type reference in spawn — ASTEROID_TYPES now stores type obj directly
# When spawning asteroid, store reference to its type object on the asteroid
# Find asteroid spawn: const type = ASTEROID_TYPES[...]
idx = txt.find('ASTEROID_POOL')
if idx >= 0:
    print("ASTEROID_POOL found at", idx)
    print(txt[idx:idx+200])

# ─── 7. HUD — add mineral and armalcolite display
# Find the ore bar HUD section and add text lines
old_hud = "if (ship.ore > 0) {"
# Find context around oreBar display
idx = txt.find("const oreBarX")
if idx >= 0:
    # Find the line that shows ore count text in HUD
    ore_text_idx = txt.find('ship.ore', idx)
    print("HUD ore ref found at", ore_text_idx)
    print(repr(txt[ore_text_idx:ore_text_idx+200]))

open('driftbound_flight_test.html', 'w', encoding='utf-8').write(txt)
print("\n=== PATCH v04b COMPLETE ===")

# Verify
txt2 = open('driftbound_flight_test.html','r',encoding='utf-8').read()
print("ship.mineral declared:", 'mineral:    0' in txt2)
print("armalcolite field:", 'armalcolite:0' in txt2)
print("loot drop injected:", 'lootType' in txt2)
print("refine on armalcolite:", 'ship.armalcolite > 0' in txt2)
