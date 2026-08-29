lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Find the <script> block and count braces to find unclosed ones
in_script = False
depth = 0
script_start = 0

for i, l in enumerate(lines):
    if '<script>' in l or '<script ' in l:
        in_script = True
        script_start = i
    if not in_script:
        continue
    if '</script>' in l:
        break
    # Count braces in JS strings is tricky, do basic count
    for ch in l:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1

    # Flag lines where depth goes unexpectedly
    if depth < 0:
        print(f"NEGATIVE DEPTH at line {i+1}: depth={depth}")
        print(f"  {l.rstrip()}")

print(f"\nFinal brace depth: {depth}  (should be 0)")
print(f"Script started at line {script_start+1}")

# Now find updateMining and trace its braces
print("\n=== updateMining brace trace ===")
start = None
for i, l in enumerate(lines):
    if 'function updateMining' in l:
        start = i
        break

if start:
    depth2 = 0
    for i, l in enumerate(lines[start:], start=start):
        for ch in l:
            if ch == '{': depth2 += 1
            elif ch == '}': depth2 -= 1
        if depth2 == 0 and i > start:
            print(f"updateMining closes at line {i+1}")
            # Show last 5 lines
            for j in range(max(start, i-3), i+3):
                print(f'{j+1:4}: {lines[j]}', end='')
            break
        if i > start + 200:
            print(f"updateMining never closed! depth={depth2} after 200 lines")
            break
