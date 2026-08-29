with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

# Dump drawShip function
in_fn = False; depth = 0; start = 0
for i, l in enumerate(lines, 1):
    if 'function drawShip' in l:
        in_fn = True; start = i
    if in_fn:
        print(f'L{i}: {l.rstrip()}')
        depth += l.count('{') - l.count('}')
        if in_fn and depth <= 0 and i > start:
            break

print('\n--- drawAttachedPods ---')
in_fn = False; depth = 0; start = 0
for i, l in enumerate(lines, 1):
    if 'function drawAttachedPods' in l:
        in_fn = True; start = i
    if in_fn:
        print(f'L{i}: {l.rstrip()}')
        depth += l.count('{') - l.count('}')
        if in_fn and depth <= 0 and i > start:
            break
