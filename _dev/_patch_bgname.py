import re

# Fix HTML
with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
d = d.replace("'vapor space bg/'", "'vapor_bg/'")
with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))
print('HTML BG_BASE:', 'vapor_bg/' in d, '| old gone:', 'vapor space bg' not in d)

# Fix main.py
with open('main.py', 'r', encoding='utf-8') as f:
    m = f.read()
m = m.replace("'/vapor space bg',                 'vapor space bg'", "'/vapor_bg',                       'vapor_bg'")
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(m)
print('main.py route:', 'vapor_bg' in m, '| old gone:', 'vapor space bg' not in m)
