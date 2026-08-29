lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Check loadAll — it should close before showToast
# Find loadAll and trace to its close
start = None
for i, l in enumerate(lines):
    if 'async function loadAll' in l:
        start = i
        break

print(f"loadAll at HTML line {start+1}")
print("=== loadAll body ===")
depth = 0
for i, l in enumerate(lines[start:], start=start):
    opens  = l.count('{')
    closes = l.count('}')
    depth += opens - closes
    print(f'{i+1:4} [d={depth}]: {l.rstrip()[:120]}')
    if depth == 0 and i > start:
        print(f"\n>>> loadAll closes at line {i+1}")
        # show a few lines after
        for j in range(i+1, min(i+8, len(lines))):
            print(f'{j+1:4}: {lines[j].rstrip()[:120]}')
        break
    if i > start + 200:
        print(f"\n>>> Gave up, depth={depth}")
        break
