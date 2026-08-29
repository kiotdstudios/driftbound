import re
lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

start = None
for i, l in enumerate(lines):
    if 'function updateMining' in l:
        start = i
        break

# Find end (next top-level function)
end = None
for i, l in enumerate(lines[start+1:], start=start+1):
    if re.match(r'function \w+|async function \w+', l.strip()):
        end = i
        break

print(f"updateMining: lines {start+1} to {end+1 if end else '?'}")

depth = 0
for i, l in enumerate(lines[start:end], start=start):
    l2 = re.sub(r'`[^`]*`', '``', l)
    l2 = re.sub(r'"[^"]*"', '""', l2)
    l2 = re.sub(r"'[^']*'", "''", l2)
    l2 = re.sub(r'//.*', '', l2)
    opens  = l2.count('{')
    closes = l2.count('}')
    depth += opens - closes
    if opens != closes:
        print(f'{i+1:4} [d={depth:+d}]: {l.rstrip()[:100]}')

print(f"\nFinal depth of updateMining: {depth}")
if end:
    print(f"\nLast 10 lines before next function (line {end+1}):")
    for j in range(max(start, end-10), end+2):
        print(f'{j+1:4}: {lines[j]}', end='')
