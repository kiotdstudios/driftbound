import re

lines = open('driftbound_flight_test.html', 'r', encoding='utf-8').readlines()

# Find all top-level function declarations and their expected close lines
# We'll track depth per function
in_script = False
script_lines = []
script_offset = 0

for i, l in enumerate(lines):
    if '<script>' in l:
        in_script = True
        script_offset = i + 1
        continue
    if '</script>' in l:
        in_script = False
        continue
    if in_script:
        script_lines.append((i + 1, l))  # (html_line_num, content)

# Now find all function declarations and check each closes at depth 0
fn_starts = []
for idx, (html_ln, l) in enumerate(script_lines):
    if re.match(r'\s*(async\s+)?function\s+\w+', l):
        fn_starts.append((idx, html_ln, l.strip()))

print(f"Found {len(fn_starts)} functions\n")

# For each function, count braces until depth returns to 0
results = []
for fn_idx, (start_idx, html_ln, fn_sig) in enumerate(fn_starts):
    # Find the end: next function start or end of script
    if fn_idx + 1 < len(fn_starts):
        end_idx = fn_starts[fn_idx + 1][0]
    else:
        end_idx = len(script_lines)
    
    # Count raw braces in this function's span
    depth = 0
    for i in range(start_idx, end_idx):
        _, l = script_lines[i]
        # strip strings/comments crudely
        l2 = re.sub(r'"[^"]*"', '""', l)
        l2 = re.sub(r"'[^']*'", "''", l2)
        l2 = re.sub(r'//.*', '', l2)
        depth += l2.count('{') - l2.count('}')
    
    results.append((html_ln, fn_sig[:60], depth))
    if depth != 0:
        print(f"  *** UNBALANCED: d={depth:+d} at HTML line {html_ln}: {fn_sig[:60]}")
    else:
        print(f"  OK d={depth:+d} HTML line {html_ln}: {fn_sig[:50]}")

print(f"\nTotal imbalance: {sum(r[2] for r in results)}")
