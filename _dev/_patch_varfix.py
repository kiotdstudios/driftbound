import re

d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

# ── Find the two script block boundaries ──
script1_end = d.find('</script>')           # end of first script block
script2_start = d.find('<script>', script1_end + 1)  # start of second script block
script2_end = d.find('</script>', script2_start)

print(f"Script 1 ends at char {script1_end}")
print(f"Script 2: {script2_start} -> {script2_end}")

# ── Extract the interior/combat variable block from script 2 ──
# Everything from "let _lastSend" down to the end of the interior state vars
# We want: the interior system vars + combat vars + projectile vars

# Find the combat vars section start in script 2
combat_start_marker = "// ── INTERIOR SYSTEM"
# Try alternate (garbled encoding)
combat_section = d.find("let   podSecured = false;", script2_start, script2_end)
if combat_section == -1:
    combat_section = d.find("let podSecured", script2_start, script2_end)
print(f"Combat vars start at {combat_section}")

# Find the end — last interior var before the multiplayer client functions
# The block ends before "function lobbyConnect" or "var socket"
combat_end_marker = d.find("var socket", script2_start, script2_end)
if combat_end_marker == -1:
    combat_end_marker = d.find("function lobbyConnect", script2_start, script2_end)
print(f"Combat vars end at {combat_end_marker}")

# Back up to find the full comment header before podSecured
# Look for the INTERIOR SYSTEM comment just before podSecured
block_search_start = max(script2_start, combat_section - 600)
interior_comment = d.rfind('//', block_search_start, combat_section)
# Find the start of that comment line
line_start = d.rfind('\n', block_search_start, interior_comment) + 1
print(f"Full block starts at {line_start}")

combat_block = d[line_start:combat_end_marker].rstrip()
print(f"Extracted {len(combat_block)} chars of combat vars")
print("First 200:", repr(combat_block[:200]))

# ── Remove combat block from script 2 ──
d = d[:line_start] + d[combat_end_marker:]
print("Removed from script 2")

# ── Find where to inject in script 1 — right before boot() ──
boot_pos = d.find('async function boot()')
assert boot_pos != -1

# Back up to find blank line before boot
inject_pos = d.rfind('\n\n', 0, boot_pos) + 2
print(f"Injecting at {inject_pos} (before boot at {boot_pos})")

injection = combat_block.strip() + '\n\n'
d = d[:inject_pos] + injection + d[inject_pos:]
print("Injected combat vars into script 1")

# ── Also fix the stray `_ePressed = false` on the mineTarget line in script 1 ──
d = d.replace(
    "let   mineTarget   = null; _ePressed = false;",
    "let   mineTarget   = null;"
)
print("Fixed stray _ePressed assignment on mineTarget line")

# ── Brace check ──
depth = 0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
