f = open('driftbound_flight_test.html', 'rb')
d = f.read().decode('utf-8', 'replace')
f.close()

# Show BG_BASE value
idx = d.find('BG_BASE')
print('BG_BASE:', d[idx:idx+60])
print()

# Show the static route in main.py
f2 = open('main.py', 'r', encoding='utf-8')
m = f2.read()
f2.close()
for line in m.split('\n'):
    if 'vapor' in line or 'static' in line:
        print('main.py:', line.strip())
