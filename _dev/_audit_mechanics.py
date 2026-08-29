with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

import re

# 1. lg_planet drop rate
print('=== asteroid / ore drop config ===')
for i, l in enumerate(lines, 1):
    if any(t in l for t in ['lg_planet', 'armalcolite', 'Armalcolite', 'drop', 'DROP', '100%', 'oreType', 'OreType']):
        print(f'L{i}: {l.rstrip()[:140]}')

print('\n=== refine / craft fuel logic ===')
for i, l in enumerate(lines, 1):
    if any(t in l for t in ['refine', 'REFINE', 'FUEL_PER_CRAFT', 'ORE_PER_FUEL', 'armalcolite', 'KeyC']):
        print(f'L{i}: {l.rstrip()[:140]}')

print('\n=== respawn logic ===')
for i, l in enumerate(lines, 1):
    if any(t in l for t in ['RESPAWN', 'respawn', 'destroyedAt', 'elapsed>=', 'ship.ore', 'ship.mineral', 'ship.armalco']):
        print(f'L{i}: {l.rstrip()[:140]}')
