with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

# Dump drawHUD fully
in_fn = False; depth = 0; start = 0
for i, l in enumerate(lines, 1):
    if 'function drawHUD' in l:
        in_fn = True; start = i
    if in_fn:
        depth += l.count('{') - l.count('}')
        if in_fn and depth <= 0 and i > start:
            print(f'drawHUD ends L{i}')
            break

print(f'drawHUD starts L{start}')

# Also find drawShip and drawAttachedPods
for i, l in enumerate(lines, 1):
    if any(t in l for t in ['function drawShip', 'function drawAttachedPods',
                             'attachedPods', 'POD_DISPLAY', 'drawWorldPods']):
        print(f'L{i}: {l.rstrip()[:120]}')
