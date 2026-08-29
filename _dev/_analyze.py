with open('driftbound_flight_test.html','rb') as f:
    src = f.read().decode('utf-8')

tokens = ["currentBgIdx = ", "toxic_01", "NORMAL_MAX", "BOOST_RAMP_DOWN", "spawnAsteroid", "const asteroids"]
for tok in tokens:
    idx = src.find(tok)
    if idx != -1:
        print(f"=== {tok} @ {idx} ===")
        print(src[idx:idx+120])
        print()
