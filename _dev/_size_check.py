import os

total = 0
files = []

# Asteroid assets we actually use
keep_asteroids = ['sm_brown', 'lg_brown', 'lg_planet']
for f in os.listdir('Demo_assets/asteroids'):
    if f.endswith('.png') and any(x in f for x in keep_asteroids):
        p = os.path.join('Demo_assets/asteroids', f)
        s = os.path.getsize(p)
        files.append((s, p))
        total += s

# Vapor BG assets only
for root, dirs, fs in os.walk('space_parallax_backgrounds_v1/assets'):
    for f in fs:
        if f.endswith('.png') and 'vapor' in f:
            p = os.path.join(root, f)
            s = os.path.getsize(p)
            files.append((s, p))
            total += s

# Current HTML size
html_size = os.path.getsize('driftbound_flight_test.html')

for s, p in sorted(files, reverse=True):
    print(f'{s//1024:>5}KB  {p}')

print(f'\nAssets total : {total//1024}KB ({total//1048576}MB)')
print(f'HTML current : {html_size//1024}KB')
print(f'Embedded est : {int(total*1.37)//1024}KB ({int(total*1.37)//1048576}MB) [base64 +37%]')
print(f'Final file   : {(html_size + int(total*1.37))//1024}KB')
