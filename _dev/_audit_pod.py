with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

targets = ['POD_BASE', 'ANIM_KEY', 'const rotations', 'const animations',
           'loadImages', 'function loadImages', 'allLoaded', 'Promise.all',
           'drawOrePickups(', 'drawMiningLaser(', 'drawCompass',
           'serverOres', 'orePickups =', 'let orePickups',
           'var socket', 'let myPid', 'var myPid',
           'function gameLoop', 'gameLoop()', 'requestAnimationFrame']

found = {}
for i, line in enumerate(lines, 1):
    for t in targets:
        if t in line and t not in found:
            found[t] = (i, line.rstrip())

for k in sorted(found, key=lambda x: found[x][0]):
    print(f'L{found[k][0]}  [{k}]: {found[k][1][:100]}')

# Also show the image loading block
print('\n=== image loading block ===')
in_load = False
count = 0
for i, line in enumerate(lines, 1):
    if 'loadImages' in line or 'rotations[' in line or 'animations[' in line:
        if not in_load:
            in_load = True
            start = i
        print(f'L{i}: {line.rstrip()[:120]}')
        count += 1
        if count > 5:
            break
