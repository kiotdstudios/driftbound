raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

checks = {
    # Movement
    '8-dir movement':       any(k in d for k in ['DIRS','DIR_ANGLES','north','northeast']),
    'Acceleration/physics': 'THRUST' in d and 'vx' in d,
    'Boost/dash':           'BOOST_THRUST' in d,
    # Character sprite
    'Character sprite':     'drawImage' in d and ('sprite' in d.lower() or 'frame' in d.lower()),
    # Exterior space
    'Exterior zone':        any(k in d for k in ['worldX','worldY','nebula','asteroid']),
    # Resources
    '3+ resource types':    all(k in d for k in ['ore','mineral','armalcolite']),
    'Mining':               'mine' in d.lower() and '[E]' in d,
    # Crafting
    'Craft station':        'REFINE' in d or 'craft' in d.lower(),
    'Recipes':              'FUEL_PER_CRAFT' in d,
    # Weapons
    'Ranged weapon':        any(k in d for k in ['bullet','projectile','fire','shoot']),
    # Enemies
    'Enemy types':          'enemy' in d.lower() or 'hostile' in d.lower(),
    # Pod system
    'Pod discovery':        'worldPods' in d or 'attachedPods' in d,
    'Pod docking':          'attachedPods' in d,
    'Walk into pod':        'interior' in d.lower() or 'room' in d.lower(),
    # Vitals
    'Fuel/oxygen system':   'FUEL_CAPACITY' in d and 'ship.fuel' in d,
    'Hull/HP system':       'SHIP_MAX_HP' in d and 'ship.hp' in d,
    # Save/load
    'Save/load':            'saveGame' in d or 'localStorage' in d,
    # Multiplayer (non-goal for MVP)
    'Multiplayer (non-MVP)': 'multiMode' in d or 'remotePlayers' in d,
    # Combat
    'Combat system':        any(k in d for k in ['bullet','laser','weapon','shoot']),
    # Narrative
    'Narrative thread':     any(k in d for k in ['signal','log','distress','story']),
    # Interior / pod interior walkable
    'Walkable pod interior': 'interior' in d.lower() and ('room' in d.lower() or 'walk' in d.lower()),
}

lines=[]
done=[k for k,v in checks.items() if v]
missing=[k for k,v in checks.items() if not v]
lines.append(f'=== BUILT ({len(done)}) ===')
for k in done: lines.append(f'  [x] {k}')
lines.append(f'\n=== MISSING ({len(missing)}) ===')
for k in missing: lines.append(f'  [ ] {k}')

out='\n'.join(lines)
open('_gdd_audit.txt','w').write(out)
print(out)
