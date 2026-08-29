with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
import re

# Pull all top-level const/let/var declarations that are game tuning values
print('=== SHIP / GAME CONSTANTS ===')
for m in re.finditer(r'^(?:const|let|var)\s+([A-Z_0-9]+)\s*=\s*([^;\n]+);', d, re.MULTILINE):
    name, val = m.group(1), m.group(2).strip()
    # Only pure numeric / simple values
    if re.match(r'^[\d\.\-\+\s\*\/\(\)]+$', val) or re.match(r"^'[^']+'$", val):
        print(f'  {name} = {val}')

print('\n=== SHIP_TYPES ===')
m = re.search(r'const SHIP_TYPES = \{.*?\};', d, re.DOTALL)
if m: print(d[m.start():m.end()])
