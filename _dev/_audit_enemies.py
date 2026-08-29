import re
d = open('driftbound_flight_test.html','rb').read().decode('utf-8','replace')

# find hostile / enemy references
print('=== HOSTILE/ENEMY REFS ===')
for m in re.finditer(r'.{0,40}(?:hostile|enemy|enemies|Enemy).{0,60}', d):
    print(' ', repr(m.group()))

print('\n=== WEAPON / FIRE / SHOOT REFS ===')
for m in re.finditer(r'.{0,20}(?:weapon|shoot|fire|bullet|projectile|ammo).{0,40}', d, re.IGNORECASE):
    print(' ', repr(m.group()))

print('\n=== POD SECURED / DOCK STATE ===')
for m in re.finditer(r'.{0,20}(?:secured|docked|dock|podState|pod_state).{0,60}', d, re.IGNORECASE):
    print(' ', repr(m.group()))

print('\n=== INVENTORY / ITEM SLOTS ===')
for m in re.finditer(r'.{0,10}(?:inventory|inv\b|item|slot|pickup|loot).{0,50}', d, re.IGNORECASE):
    print(' ', repr(m.group()))
