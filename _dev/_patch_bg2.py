import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

d = re.sub(r'const BG_SETS\s*=\s*\[[\s\S]*?\];', "const BG_SETS = [\n  'vapor_02',\n];", d)
d = re.sub(r'let currentBgIdx\s*=\s*\d+;[^\r\n]*', 'let currentBgIdx = 0;', d)

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('done — only vapor_02:', "'vapor_02'" in d and "'vapor_01'" not in d)
