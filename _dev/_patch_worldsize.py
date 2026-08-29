"""
Fix: WORLD_SIZE constant was never declared — causes ReferenceError at script
parse time (line 463: const WS2 = WORLD_SIZE * 2) which kills everything.
WORLD_SIZE = 8000 (2x the WORLD_SPREAD spawn radius of 4000) gives parallax
enough room to wrap cleanly without visible seams.
Inject it right after WORLD_SPREAD is defined.
"""

SRC  = r'C:\Users\diepowel\Documents\DRIFTBOUND\driftbound_flight_test.html'

d = open(SRC, 'rb').read().decode('utf-8', 'replace')

ANCHOR = 'const WORLD_SPREAD   = 4000;   // max spawn radius'
assert ANCHOR in d, "ANCHOR not found"
assert 'WORLD_SIZE' not in d.split(ANCHOR)[0].split('const WS2')[0], "WORLD_SIZE already declared before anchor"

# Inject the declaration on the next line after WORLD_SPREAD
d = d.replace(
    ANCHOR,
    ANCHOR + '\nconst WORLD_SIZE     = 8000;   // parallax wrap boundary (2× spawn radius)'
)

# Verify
import re
anchor_pos = d.find('const WORLD_SIZE')
ws2_pos    = d.find('const WS2')
print(f"WORLD_SIZE declared at char {anchor_pos} (line {d[:anchor_pos].count(chr(10))+1})")
print(f"WS2 uses it at char {ws2_pos} (line {d[:ws2_pos].count(chr(10))+1})")
assert anchor_pos < ws2_pos, "WORLD_SIZE must be declared before WS2"
print("Order OK")
print(f"Total lines: {len(d.splitlines())}")

open(SRC, 'wb').write(d.encode('utf-8'))
print("Written.")
