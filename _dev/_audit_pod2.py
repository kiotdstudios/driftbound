with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

# Show the full image loading block L302-460
print('=== image loading L302-460 ===')
for i, line in enumerate(lines, 1):
    if 302 <= i <= 460:
        print(f'L{i}: {line.rstrip()}')

# Show gameLoop / main draw loop L2240-2290
print('\n=== gameLoop L2240-2290 ===')
for i, line in enumerate(lines, 1):
    if 2240 <= i <= 2290:
        print(f'L{i}: {line.rstrip()}')

# Show serverOres / orePickups declarations
print('\n=== orePickups declarations ===')
import re
for i, line in enumerate(lines, 1):
    if re.search(r'(orePickups|serverOres)\s*[=\{]', line):
        print(f'L{i}: {line.rstrip()}')
