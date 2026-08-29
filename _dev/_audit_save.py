with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

import re

# Check for any localStorage / sessionStorage / IndexedDB usage
print('=== persistence calls ===')
for i, line in enumerate(lines, 1):
    if any(t in line for t in ['localStorage', 'sessionStorage', 'IndexedDB', 'save(', 'load(', 'JSON.stringify', 'JSON.parse']):
        print(f'L{i}: {line.rstrip()[:120]}')

# Show ship object init to see what fields exist
print('\n=== ship object fields ===')
m = re.search(r'const ship\s*=\s*\{.*?\};', d, re.DOTALL)
if m:
    print(d[m.start():m.end()])
else:
    # try let ship
    m = re.search(r'let ship\s*=\s*\{.*?\};', d, re.DOTALL)
    if m:
        print(d[m.start():m.end()])
    else:
        print('ship object: NOT FOUND as simple block')
        for i, line in enumerate(lines, 1):
            if 'ship =' in line or 'const ship' in line or 'let ship' in line:
                print(f'L{i}: {line.rstrip()}')
