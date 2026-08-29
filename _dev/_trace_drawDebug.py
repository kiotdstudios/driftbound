import re
lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

start = None
for i, l in enumerate(lines):
    if 'function drawDebug' in l:
        start = i
        break

print(f"drawDebug at line {start+1}")

depth = 0
for i, l in enumerate(lines[start:], start=start):
    l2 = re.sub(r'"[^"]*"', '""', l)
    l2 = re.sub(r"'[^']*'", "''", l2)
    l2 = re.sub(r'//.*', '', l2)
    opens  = l2.count('{')
    closes = l2.count('}')
    depth += opens - closes
    if opens != closes:
        print(f'{i+1:4} [d={depth:+d}]: {l.rstrip()[:100]}')
    if depth == 0 and i > start:
        print(f"\n>>> drawDebug closes at line {i+1}")
        for j in range(i-2, min(i+5, len(lines))):
            print(f'{j+1:4}: {lines[j]}', end='')
        break
    if i > start + 250:
        print(f"\n>>> NEVER CLOSED, depth={depth} after 250 lines")
        print(f"Last 5 lines checked:")
        for j in range(i-4, i+1):
            print(f'{j+1:4}: {lines[j]}', end='')
        break
