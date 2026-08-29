with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

# Show L178-195 (around the COLLISION_RADIUS error at L184)
print('=== L178-200 ===')
for i, line in enumerate(lines, 1):
    if 178 <= i <= 200:
        print(f'  L{i}: {line.rstrip()}')

print()
# Find all const/let declarations for COLLISION_RADIUS, PVP_COLLISION_R, socket
import re
for i, line in enumerate(lines, 1):
    if re.search(r'\b(const|let)\s+(COLLISION_RADIUS|PVP_COLLISION_R|PVP_IFRAMES|socket)\b', line):
        print(f'  L{i}: {line.rstrip()}')
