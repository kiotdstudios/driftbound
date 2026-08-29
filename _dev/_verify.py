import ast

with open('driftbound_server.py','r') as f:
    src = f.read()
try:
    ast.parse(src)
    print('driftbound_server.py: syntax OK')
except SyntaxError as e:
    print('SYNTAX ERROR:', e)

with open('driftbound_flight_test.html','r',encoding='utf-8') as f:
    html = f.read()

print('HTML size:', len(html)//1024, 'KB')
checks = [
    ('Lobby',           'lobbyConnect'),
    ('drawRemotePlayers','drawRemotePlayers'),
    ('getAsteroids',    'getAsteroids()'),
    ('sendMove',        'sendMove()'),
    ('ESC solo bypass', 'Solo mode'),
    ('Player indicators','drawPlayerIndicator'),
    ('multiMode flag',  'multiMode'),
    ('serverAsteroids', 'serverAsteroids'),
    ('WS port 8766',    '8766'),
]
for label, token in checks:
    print(f'  {label}: {"OK" if token in html else "MISSING"}')
