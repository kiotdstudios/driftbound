txt = open('driftbound_flight_test.html','r',encoding='utf-8').read()
print(f"Total chars: {len(txt)}")
print(f"Total lines: {txt.count(chr(10))}")

# Key structural anchors
anchors = [
    'const ship =',
    'function gameLoop',
    'function update(',
    'function draw(',
    'function drawShip(',
    'function drawHUD(',
    'function spawnAsteroid(',
    'asteroids.push(',
    'keys[',
    'requestAnimationFrame',
    'window.onload',
    'BASE_PATH',
    'img.src =',
    'loadBgSet(',
    'const DIRS',
    'ship.worldX',
    'canvas.width',
    'socket',
    'WebSocket',
]
for a in anchors:
    idx = txt.find(a)
    if idx >= 0:
        print(f'\n[{a}] @ {idx}')
        print(txt[idx:idx+120])
    else:
        print(f'\nNOT FOUND: {a}')
