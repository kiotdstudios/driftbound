d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

before = d.count('gameLoop')
d = d.replace('requestAnimationFrame(gameLoop)', 'requestAnimationFrame(loop)')
after = d.count('gameLoop')

print(f"Replaced {before - after} occurrence(s) of gameLoop -> loop")
print(f"Remaining 'gameLoop' refs: {after}")

import re
depth = 0
for ch in re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
