lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Trace updateMining with full depth tracking, show where it goes wrong
start = None
for i, l in enumerate(lines):
    if 'function updateMining' in l:
        start = i
        break

print(f"updateMining starts at line {start+1}")

depth = 0
for i, l in enumerate(lines[start:], start=start):
    opens  = l.count('{')
    closes = l.count('}')
    depth += opens - closes
    # Show depth changes
    if opens != closes:
        print(f'{i+1:4} [d={depth:+3}]: {l.rstrip()[:100]}')
    if depth == 0 and i > start:
        print(f"\n>>> updateMining CLOSES at line {i+1}")
        break
    if i > start + 300:
        print(f"\n>>> NEVER CLOSED after {i-start} lines, depth={depth}")
        # Show last 10 lines searched
        print("Last lines:")
        for j in lines[i-5:i+1]:
            print(f'  {j.rstrip()}')
        break
