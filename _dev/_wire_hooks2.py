data = open('driftbound_flight_test.html','rb').read()
import re

# Find 'return speed' anywhere
hits = [m.start() for m in re.finditer(rb'return speed', data)]
print(f"'return speed' occurrences: {len(hits)}")
for h in hits:
    print(repr(data[h:h+80]))

# Find end of update() function — look for 'return speed' then next }
# Also find where shiftHeld is used the LAST time in update
sh_hits = [m.start() for m in re.finditer(rb'shiftHeld', data)]
print(f"\nshiftHeld refs: {len(sh_hits)}")
for h in sh_hits:
    print(repr(data[h:h+60]))

# Find the closing brace of update() — after the last code in update
# update() ends somewhere... find it
upd_start = data.find(b'function update(')
print(f"\nupdate() starts at: {upd_start}")
print(repr(data[upd_start:upd_start+80]))

# scan forward for the pattern: \n} followed by \nfunction
# or just find where update() returns
upd_slice = data[upd_start:upd_start+5000]
speed_idx = upd_slice.find(b'speed')
print(f"\n'speed' first appears in update at offset {speed_idx}")
print(repr(upd_slice[speed_idx:speed_idx+300]))
