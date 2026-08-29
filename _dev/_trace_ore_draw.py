lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

start = None
for i, l in enumerate(lines):
    if 'function drawOrePickups' in l:
        start = i
        break

print(f"drawOrePickups starts at line {start+1}")
print("=== FULL FUNCTION ===")
depth = 0
for i, l in enumerate(lines[start:], start=start):
    opens  = l.count('{')
    closes = l.count('}')
    depth += opens - closes
    print(f'{i+1:4} [d={depth}]: {l.rstrip()[:120]}')
    if depth == 0 and i > start:
        print(f"\n>>> Closes at line {i+1}")
        break
    if i > start + 100:
        print(f"\n>>> Gave up at line {i+1}, depth={depth}")
        break
