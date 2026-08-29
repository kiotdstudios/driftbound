with open('driftbound_flight_test_v03.html', 'rb') as f:
    src = f.read().decode('utf-8')

src = src.replace('\r\n', '\n')

# 1. Revert BG back to vapor_03 (original default, index 7)
src = src.replace(
    "let currentBgIdx = 10;  // toxic_01 \u2014 pink void, locked as main space BG",
    "let currentBgIdx = 7;   // vapor_03 \u2014 purple/teal nebula (original default)"
)

# 2. Slower ramp: UP = 0.022 (~45 frames to full boost), DOWN = 0.006 (~167 frames coast)
src = src.replace(
    "const BOOST_RAMP_UP   = 0.045; // ramp to full boost: ~22 frames\nconst BOOST_RAMP_DOWN = 0.012; // ramp back to cruise: ~83 frames \u2014 gradual coast",
    "const BOOST_RAMP_UP   = 0.022; // ramp to full boost: ~45 frames \u2014 slow engine spool\nconst BOOST_RAMP_DOWN = 0.006; // ramp back to cruise: ~167 frames \u2014 long inertia coast"
)

with open('driftbound_flight_test.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('Written to driftbound_flight_test.html')

checks = [
    ('BG vapor_03 restored',  'currentBgIdx = 7'),
    ('Ramp UP slower',         'BOOST_RAMP_UP   = 0.022'),
    ('Ramp DOWN slower',       'BOOST_RAMP_DOWN = 0.006'),
    ('Collision detection',    'COLLISION DETECTION'),
    ('Health bar',             'HULL INTEGRITY'),
    ('Asteroid rotation',      'rotSpeed'),
    ('Asteroid drift',         'driftVx'),
    ('Rotate draw',            'ctx.rotate(rot)'),
    ('Hit flash',              'hitFlash'),
    ('Hull hp state',          'hp:       100'),
]
all_ok = True
for label, tok in checks:
    ok = tok in src
    if not ok: all_ok = False
    print(f"  [{'OK' if ok else 'MISSING'}] {label}")

print('\nALL GOOD' if all_ok else '\nSOME MISSING')
