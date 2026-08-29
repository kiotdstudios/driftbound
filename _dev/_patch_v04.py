txt = open('driftbound_flight_test.html', 'r', encoding='utf-8').read()

# ─── 1. BG_SETS — vapor only (vapor_01, vapor_03, vapor_04, vapor_05)
# vapor_02 doesn't exist in assets, skip it
old_bg = """const BG_SETS = [

  'stellar_01','stellar_02','stellar_03','stellar_04','stellar_05',

  'vapor_01',  'vapor_02',  'vapor_03',  'vapor_04',  'vapor_05',

  'toxic_01',  'toxic_02',  'toxic_03',  'toxic_04',  'toxic_05',

  'void_01',   'void_02',   'void_03',   'void_04',   'void_05',

];

let currentBgIdx = 7;   // vapor_03 — purple/teal nebula (original default)"""

new_bg = """const BG_SETS = [
  'vapor_01', 'vapor_03', 'vapor_04', 'vapor_05',
];

let currentBgIdx = 1;   // vapor_03 default (index 1 in vapor-only list)"""

if old_bg in txt:
    txt = txt.replace(old_bg, new_bg)
    print("BG_SETS updated to vapor-only")
else:
    print("WARNING: BG_SETS block not matched exactly - trying fallback")
    # fallback: just replace the array line
    import re
    txt = re.sub(
        r"const BG_SETS = \[[\s\S]*?\];",
        "const BG_SETS = [\n  'vapor_01', 'vapor_03', 'vapor_04', 'vapor_05',\n];",
        txt
    )
    txt = re.sub(r"let currentBgIdx = \d+;[^\n]*", "let currentBgIdx = 1;   // vapor_03 default", txt)
    print("BG_SETS fallback applied")

# ─── 2. ASTEROID_TYPES — only sm_brown, lg_brown, lg_planet
# sm_brown = basic rock, 2% chance mineral material on mine
# lg_brown = basic rock, 2% chance mineral material on mine  
# lg_planet = Armalcolite source for fuel, 30% spawn weight

old_types = """const ASTEROID_TYPES = [

  { id: 'sm_gray',    hp: 3, oreMin: 1, oreMax: 2, w: 40, h: 34 },

  { id: 'sm_brown',   hp: 3, oreMin: 1, oreMax: 2, w: 38, h: 32 },

  { id: 'xs_gray',    hp: 2, oreMin: 1, oreMax: 1, w: 29, h: 26 },

  { id: 'sm_tan',     hp: 3, oreMin: 1, oreMax: 2, w: 33, h: 30 },

  { id: 'lg_craggy',  hp: 5, oreMin: 2, oreMax: 4, w: 61, h: 41 },

  { id: 'lg_rocky',   hp: 5, oreMin: 2, oreMax: 4, w: 63, h: 61 },

  { id: 'lg_brown',   hp: 5, oreMin: 2, oreMax: 3, w: 40, h: 39 },

  { id: 'lg_planet',  hp: 6, oreMin: 3, oreMax: 5, w: 42, h: 39 },

  { id: 'void_dark',  hp: 4, oreMin: 2, oreMax: 4, w: 40, h: 39 },

  { id: 'lava',       hp: 3, oreMin: 1, oreMax: 3, w: 34, h: 23 },

];"""

# lootTable: 'mineral' = craftable material (2% on browns)
# lootTable: 'armalcolite' = fuel ore (lg_planet only)
new_types = """const ASTEROID_TYPES = [
  // id          hp  oreMin  oreMax  size        type          loot chance
  { id: 'sm_brown',  hp: 3, oreMin: 1, oreMax: 2, w: 38, h: 32, lootType: 'mineral',     lootChance: 0.02 },
  { id: 'lg_brown',  hp: 5, oreMin: 2, oreMax: 3, w: 40, h: 39, lootType: 'mineral',     lootChance: 0.02 },
  { id: 'lg_planet', hp: 6, oreMin: 3, oreMax: 5, w: 42, h: 39, lootType: 'armalcolite', lootChance: 1.00 },
];

// Spawn weights: lg_planet = 30%, sm_brown = 42%, lg_brown = 28%
// 10 slots: 3 planet, 4 sm_brown, 3 lg_brown
const ASTEROID_POOL = [2, 0,0,0,0, 1,1,1, 2,2];  // index into ASTEROID_TYPES"""

if old_types in txt:
    txt = txt.replace(old_types, new_types)
    print("ASTEROID_TYPES replaced")
else:
    print("WARNING: ASTEROID_TYPES exact match failed - trying regex")
    import re
    txt = re.sub(
        r"const ASTEROID_TYPES = \[[\s\S]*?\];",
        new_types,
        txt
    )
    print("ASTEROID_TYPES regex applied")

# ─── 3. Fix spawn pool — replace old pool array with ASTEROID_POOL reference
import re
# Old pool was: const pool = [0,0,0,...]; inside spawnAsteroid or similar
txt = re.sub(
    r"const pool = \[[^\]]+\];",
    "const pool = ASTEROID_POOL;",
    txt
)
print("Spawn pool reference updated")

# ─── 4. Add loot drop logic to the mining/destroy section
# When asteroid hp hits 0, check lootType + lootChance and award accordingly
# Find the ore pickup spawn and add loot drop after it

# Look for where we award ore on asteroid destroy
old_ore_drop = "oreCount += ore;"
new_ore_drop = """oreCount += ore;
        // Loot drop — mineral material (craftable) or armalcolite (fuel ore)
        if (a.lootType && Math.random() < a.lootChance) {
          if (a.lootType === 'mineral') {
            mineralCount = (mineralCount || 0) + 1;
            showToast('✦ MINERAL MATERIAL found! (' + mineralCount + ' held)', '#a78bfa');
          } else if (a.lootType === 'armalcolite') {
            armalcoliteCount = (armalcoliteCount || 0) + 1;
            showToast('◈ ARMALCOLITE extracted — refine for fuel (' + armalcoliteCount + ' held)', '#34d399');
          }
        }"""

if old_ore_drop in txt:
    txt = txt.replace(old_ore_drop, new_ore_drop, 1)
    print("Loot drop logic injected")
else:
    print("WARNING: ore drop anchor not found")

# ─── 5. Add mineral/armalcolite counters near oreCount declaration
old_ore_var = "let oreCount   = 0;"
new_ore_var  = """let oreCount        = 0;
let mineralCount    = 0;   // craftable mineral material
let armalcoliteCount = 0;  // fuel ore — refine with C key"""

if old_ore_var in txt:
    txt = txt.replace(old_ore_var, new_ore_var)
    print("Counters added")
else:
    print("WARNING: oreCount declaration not found")

# ─── 6. Hook armalcolite into fuel refining (C key)
# Find the refine block — currently refines oreCount to fuel
# We want: armalcolite refines to fuel (not ore — ore stays as ore)
old_refine = "if (oreCount > 0) {"
new_refine  = """if (armalcoliteCount > 0) {"""
# Only replace the FIRST one (in the C-key handler, not elsewhere)
if old_refine in txt:
    txt = txt.replace(old_refine, new_refine, 1)
    print("Refine gated to armalcolite")

# Also swap the counter used in refining
old_refine_use = "oreCount--;"
new_refine_use  = "armalcoliteCount--;"
if old_refine_use in txt:
    txt = txt.replace(old_refine_use, new_refine_use, 1)
    print("Refine counter swapped to armalcoliteCount")

# ─── 7. Update HUD to show mineral + armalcolite counts
# Find ore bar / ore HUD line and add mineral/armalcolite display
old_hud_ore = "Ore: ${oreCount}"
new_hud_ore  = "Ore: ${oreCount}  |  Mineral: ${mineralCount}  |  Armalcolite: ${armalcoliteCount}"
if old_hud_ore in txt:
    txt = txt.replace(old_hud_ore, new_hud_ore)
    print("HUD updated with new materials")
else:
    # Try alternate HUD format
    old_hud_ore2 = "'Ore: ' + oreCount"
    new_hud_ore2  = "'Ore: ' + oreCount + '  Mineral: ' + mineralCount + '  Armalcolite: ' + armalcoliteCount"
    if old_hud_ore2 in txt:
        txt = txt.replace(old_hud_ore2, new_hud_ore2)
        print("HUD updated (alternate format)")
    else:
        print("WARNING: HUD ore line not found - check manually")

open('driftbound_flight_test.html', 'w', encoding='utf-8').write(txt)
print("\n=== PATCH COMPLETE ===")
print("BGs: vapor_01, vapor_03, vapor_04, vapor_05 only")
print("Asteroids: sm_brown (2% mineral), lg_brown (2% mineral), lg_planet (100% armalcolite)")
print("lg_planet spawn weight: ~30%")
print("Armalcolite refines to fuel via C key")
