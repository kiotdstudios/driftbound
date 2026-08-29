"""
Restore from a8fedda clean baseline + apply only the gameLoop fix.
No structural changes — combat vars are already in script-1 at parse time,
so there is no TDZ issue. The only real bug was gameLoop -> loop.
"""
import re

SRC  = r'C:\Users\diepowel\Documents\DRIFTBOUND\_dev\_backup_a8fedda.html'
DEST = r'C:\Users\diepowel\Documents\DRIFTBOUND\driftbound_flight_test.html'

d = open(SRC, 'rb').read().decode('utf-8', 'replace')
print(f"Loaded {len(d.splitlines())} lines from clean baseline")

# ── Fix 1: gameLoop -> loop ───────────────────────────────────────────────
count = d.count('requestAnimationFrame(gameLoop)')
d = d.replace('requestAnimationFrame(gameLoop)', 'requestAnimationFrame(loop)')
print(f"[1] Fixed {count} gameLoop -> loop")

# ── Validate structure ────────────────────────────────────────────────────
script_tags = [(m.start(), m.group()) for m in re.finditer(r'</?script[^>]*>', d)]
print("\nScript tag structure:")
for pos, tag in script_tags:
    line = d[:pos].count('\n') + 1
    print(f"  line {line}: {tag}")

remaining_gl = d.count('gameLoop')
print(f"\ngameLoop refs remaining: {remaining_gl}")

# Verify </body></html> at end
last_200 = d[-200:].strip()
print(f"\nLast 200 chars: {repr(last_200)}")

print(f"\nTotal lines: {len(d.splitlines())}")
open(DEST, 'wb').write(d.encode('utf-8'))
print(f"Written to {DEST}")
