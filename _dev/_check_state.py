import re
raw = open('driftbound_flight_test.html','rb').read()
d = raw.decode('utf-8','replace')

checks = {
    'interiorMode var': 'let interiorMode',
    'drawInterior fn': 'function drawInterior()',
    'updateInteriorPlayer fn': 'function updateInteriorPlayer()',
    'interior fade in gameLoop': 'interiorFadeDir === 1',
    'ARMORY_MAP defined': 'ARMORY_MAP',
    'attachedPods var': 'attachedPods',
    'hostiles/enemies': 'hostile' in d or 'enemy' in d.lower() or 'Enemy' in d,
    'pod secured state': 'secured' in d or 'podSecured' in d,
    'crafting system': 'craft' in d.lower(),
    'mining system': 'mine' in d.lower() and 'mineTarget' in d,
    'save/load': 'localStorage' in d,
    'ARMORY reward item': 'armoryLoot' in d or 'armory_reward' in d or 'lootArmory' in d,
}

print('=== INTERIOR SYSTEM ===')
for k,v in checks.items():
    if isinstance(v, str):
        status = '✓' if v in d else '✗'
    else:
        status = '✓' if v else '✗'
    print(f'  {status} {k}')

# check size
print(f'\nFile size: {len(raw):,} bytes')
print(f'JS lines approx: {d.count(chr(10))}')

# Check GDD step 8 completeness
print('\n=== GDD STEP 8 GAPS ===')
gaps = {
    'secured pod state gates E entry': 'interiorMode' in d and ('secured' in d or 'podSecured' in d),
    'hostile enemy in pod pre-securing': 'hostile' in d,
    'armory loot reward inside': 'armoryLoot' in d or 'armory_reward' in d or 'ARMORY_LOOT' in d,
}
for k,v in gaps.items():
    print(f'  {"✓" if v else "✗"} {k}')
