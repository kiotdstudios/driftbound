txt = open('driftbound_flight_test.html', 'r', encoding='utf-8').read()

# ─── 1. Fix ore spawn loot fields — ast.type.lootType (not a.type)
# Earlier patch added: lootType: a.type.lootType — but the variable is 'ast' not 'a'
txt = txt.replace(
    'lootType: a.type.lootType || null,\n        lootChance: a.type.lootChance || 0',
    'lootType: ast.type.lootType || null,\n        lootChance: ast.type.lootChance || 0'
)
print("Fixed: loot fields use ast.type (not a.type)")

# ─── 2. Update craft hint — now based on armalcolite
old_craft_hint = "const canCraft = ship.ore >= ORE_PER_FUEL;"
new_craft_hint  = "const canCraft = ship.armalcolite > 0;"
txt = txt.replace(old_craft_hint, new_craft_hint)
print("Craft hint updated to armalcolite")

old_craft_text = "PER_FUEL + ' NEBULITE  \\u00b7  HAVE ' + ship.ore);"
new_craft_text  = "'ARMALCOLITE  \\u00b7  HAVE ' + ship.armalcolite);"
txt = txt.replace(old_craft_text, new_craft_text)
print("Craft text updated")

# ─── 3. Add Mineral + Armalcolite lines to HUD, after the NEBULITE ore line
old_hud_ore_line = "  ctx.fillText(ship.ore + ' NEBULITE', LEFT + 30, oreY);"
new_hud_ore_line  = """  ctx.fillText(ship.ore + ' NEBULITE', LEFT + 30, oreY);

  // Mineral material count
  const minY = oreY + 18;
  ctx.fillStyle = ship.mineral > 0 ? '#a78bfa' : '#a78bfa35';
  ctx.font = 'bold 11px monospace';
  ctx.fillText('\\u2666', LEFT + 14, minY);
  ctx.fillStyle = ship.mineral > 0 ? '#c4b5fd' : '#c4b5fd50';
  ctx.font = '11px monospace';
  ctx.fillText(ship.mineral + ' MINERAL', LEFT + 30, minY);

  // Armalcolite count
  const armY = minY + 18;
  ctx.fillStyle = ship.armalcolite > 0 ? '#34d399' : '#34d39935';
  ctx.font = 'bold 11px monospace';
  ctx.fillText('\\u25c8', LEFT + 14, armY);
  ctx.fillStyle = ship.armalcolite > 0 ? '#6ee7b7' : '#6ee7b750';
  ctx.font = '11px monospace';
  ctx.fillText(ship.armalcolite + ' ARMALCOLITE', LEFT + 30, armY);"""

txt = txt.replace(old_hud_ore_line, new_hud_ore_line)
print("HUD mineral + armalcolite lines added")

# ─── 4. Also fix the ore bar craft hint label under the ore bar
# Find "C  REFINE" or similar hint text near canCraft
old_refine_label_search = "C  REFINE"
idx = txt.find(old_refine_label_search)
if idx >= 0:
    print("Refine label at", idx, ":", repr(txt[idx:idx+80]))

# Find the canCraft text block
import re
hints = re.findall(r"[^\n]{0,30}canCraft[^\n]{0,100}", txt)
print("\ncanCraft references:")
for h in hints:
    print(repr(h))

open('driftbound_flight_test.html', 'w', encoding='utf-8').write(txt)
print("\n=== PATCH v04d COMPLETE ===")

# Verify
txt2 = open('driftbound_flight_test.html','r',encoding='utf-8').read()
print("loot uses ast.type:", 'ast.type.lootType' in txt2)
print("craft hint on armalcolite:", 'ship.armalcolite > 0' in txt2)
print("HUD mineral line:", 'MINERAL' in txt2)
print("HUD armalcolite line:", 'ARMALCOLITE' in txt2)
