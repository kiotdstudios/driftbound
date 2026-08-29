import re

js = open('_extracted.js', 'r', encoding='utf-8').read()

# Strip single-line comments
js_nc = re.sub(r'//[^\n]*', '', js)
# Strip multi-line comments
js_nc = re.sub(r'/\*.*?\*/', '', js_nc, flags=re.DOTALL)
# Strip string literals (single and double quoted, non-greedy)
js_nc = re.sub(r'"(?:[^"\\]|\\.)*"', '""', js_nc)
js_nc = re.sub(r"'(?:[^'\\]|\\.)*'", "''", js_nc)
# Strip template literals (basic - no nested)
js_nc = re.sub(r'`(?:[^`\\]|\\.)*`', '``', js_nc)

opens  = js_nc.count('{')
closes = js_nc.count('}')
print(f"Opens: {opens}  Closes: {closes}  Diff: {opens - closes}")

if opens != closes:
    # Find which line has the imbalance
    lines = js_nc.split('\n')
    depth = 0
    for i, l in enumerate(lines):
        for ch in l:
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
        if depth < 0:
            print(f"GOES NEGATIVE at JS line {i+1}  (HTML line ~{i+133})")
            print(f"  {lines[i][:120]}")
            depth = 0  # reset and keep scanning

    # Also show where depth is highest (potential missing close)
    depth = 0
    max_depth = 0
    max_line  = 0
    for i, l in enumerate(lines):
        for ch in l:
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
        if depth > max_depth:
            max_depth = depth
            max_line  = i

    print(f"\nMax depth {max_depth} reached at JS line {max_line+1} (HTML ~{max_line+133})")

    # Show final running depth at each function
    depth = 0
    print("\n=== FUNCTION-LEVEL DEPTH TRACE ===")
    for i, l in enumerate(lines):
        for ch in l:
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
        orig = open('_extracted.js','r',encoding='utf-8').readlines()
        if i < len(orig) and 'function ' in orig[i]:
            print(f"  After JS line {i+1} (HTML ~{i+133}) d={depth}: {orig[i].strip()[:80]}")
