data = open('driftbound_flight_test.html', 'rb').read()
txt = data.decode('utf-8')

# 1. Put drawShip call back in the loop (it was removed last patch)
if 'drawShip(cx, cy, now, speed);' not in txt:
    txt = txt.replace(
        '  drawHUD(speed);',
        '  drawShip(cx, cy, now, speed);\n  drawHUD(speed);'
    )
    print("drawShip call restored")
else:
    print("drawShip call already present")

# 2. Remove the boxy hanger-looking asteroid type from ASTEROID_TYPES
# The offender is 'sm_slab' - wide rectangular slab shape that looks like a hangar door
# Also 'sm_metal' and 'dark_metal' look like metal boxes - remove those too
lines = txt.split('\n')
filtered = []
skip_ids = {'sm_slab', 'sm_metal', 'dark_metal'}
for line in lines:
    skip = False
    for sid in skip_ids:
        if f"id: '{sid}'" in line:
            skip = True
            break
    if skip:
        print(f"Removed asteroid type line: {line.strip()}")
    else:
        filtered.append(line)
txt = '\n'.join(filtered)

# 3. Also remove those IDs from the weighted spawn pool
for sid in skip_ids:
    # Find their index in ASTEROID_TYPES and remove from pool
    pass  # pool uses numeric indices, we'll just rebuild it clean below

# Rebuild the pool without indices 4 (sm_slab=4), 5 (sm_metal=5), 10 (dark_metal=10)
# Original pool: [0,0,0,1,1,1,2,2,3,3,3,4,4,5,6,6,7,7,8,9,10,10,11,12]
# Remove entries 4,5,10 -> [0,0,0,1,1,1,2,2,3,3,3,6,6,7,7,8,9,11,12]
# But indices shift after removal - sm_slab(4) sm_metal(5) dark_metal(10) removed
# Remaining types by new index:
# 0=sm_gray 1=sm_brown 2=xs_gray 3=sm_tan 4=lg_craggy 5=lg_rocky
# 6=lg_brown 7=lg_planet 8=void_dark 9=lava
old_pool = "const pool = [0,0,0,1,1,1,2,2,3,3,3,4,4,5,6,6,7,7,8,9,10,10,11,12];"
new_pool = "const pool = [0,0,0,1,1,1,2,2,3,3,3,4,4,5,5,6,6,7,8,8,9];"
if old_pool in txt:
    txt = txt.replace(old_pool, new_pool)
    print("Spawn pool updated")
else:
    print("WARNING: pool line not found - may need manual check")

open('driftbound_flight_test.html', 'w', encoding='utf-8').write(txt)
print("\nAll done.")
print("drawShip present:", 'drawShip(cx, cy, now, speed);' in txt)
print("sm_slab present:", "id: 'sm_slab'" in txt)
print("sm_metal present:", "id: 'sm_metal'" in txt)
print("dark_metal present:", "id: 'dark_metal'" in txt)
