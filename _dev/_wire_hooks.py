data = open('driftbound_flight_test.html','rb').read()

# ─── 1. Hook sendMove into update() — find 'return speed;' in bytes
import re

# Find return speed; (with possible \r\n or \n before closing })
pattern = rb'(  return speed;\r?\n\})'
matches = list(re.finditer(pattern, data))
print(f"'return speed;' matches: {len(matches)}")
for m in matches:
    print(repr(data[m.start()-80:m.end()]))

# ─── 2. Find fpsDisplay = fpsCounter (the assignment, not declaration)
pattern2 = rb'fpsDisplay = fpsCounter'
idx2 = data.find(pattern2)
print(f"\nfpsDisplay assignment at {idx2}")
if idx2 >= 0:
    print(repr(data[idx2:idx2+200]))

# ─── 3. Find where FPS text is drawn to canvas
pattern3 = rb'fpsDisplay'
hits = [m.start() for m in re.finditer(pattern3, data)]
print(f"\nAll fpsDisplay refs: {hits}")
for h in hits:
    print(repr(data[h:h+120]))
