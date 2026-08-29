lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Find spawnMineChips and trace it
start = None
for i, l in enumerate(lines):
    if 'function spawnMineChips' in l:
        start = i
        break

print(f"spawnMineChips at line {start+1}")
depth = 0
for i, l in enumerate(lines[start:], start=start):
    opens  = l.count('{')
    closes = l.count('}')
    depth += opens - closes
    print(f'{i+1:4} [d={depth}]: {l.rstrip()[:120]}')
    if depth == 0 and i > start:
        print(f"\n>>> Closes at line {i+1}")
        break
    if i > start + 80:
        print(f"\n>>> Gave up depth={depth}")
        break
