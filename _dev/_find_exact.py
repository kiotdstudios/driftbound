with open('driftbound_flight_test.html','rb') as f:
    raw = f.read()

# Show exact bytes around key spots to check for special chars
checks = [
    b'BOOST_RAMP_UP',
    b'BOOST_RAMP_DOWN',
    b'mineCooldown: 0',
    b'toRespawn    = ',
    b'spawnAsteroid(nearShip)',
    b'Tick flash',
    b'SPEED_THRESH = 0.12',
]
for tok in checks:
    idx = raw.find(tok)
    if idx != -1:
        chunk = raw[idx:idx+180]
        print(f'=== {tok} ===')
        print(repr(chunk))
        print()
    else:
        print(f'NOT FOUND: {tok}')
