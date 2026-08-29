import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# 1. Fix BG_BASE path
d = re.sub(r"const BG_BASE\s*=\s*'[^']*';", "const BG_BASE  = 'vapor space bg/';", d)

# 2. Fix BG_SETS
d = re.sub(r'const BG_SETS\s*=\s*\[[\s\S]*?\];', "const BG_SETS = [\n  'vapor_01', 'vapor_02', 'vapor_04', 'vapor_05',\n];", d)

# 3. Fix currentBgIdx default
d = re.sub(r'let currentBgIdx\s*=\s*\d+;[^\r\n]*', 'let currentBgIdx = 1;   // vapor_02 default (most complete set)', d)

# 4. Remove flat/ and layers/ subfolders — covers both ${name} and ${bgName} variants
d = re.sub(r'`flat/\$\{(\w+)\}_FLAT\.png`',      r'`${\1}_FLAT.png`',      d)
d = re.sub(r'`layers/\$\{(\w+)\}_L1_far\.png`',  r'`${\1}_L1_far.png`',  d)
d = re.sub(r'`layers/\$\{(\w+)\}_L2_mid\.png`',  r'`${\1}_L2_mid.png`',  d)
d = re.sub(r'`layers/\$\{(\w+)\}_L3_near\.png`', r'`${\1}_L3_near.png`', d)

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('BG_BASE vapor space bg:', 'vapor space bg' in d)
print('old parallax gone:',      'space_parallax_backgrounds_v1' not in d)
print('flat/ gone:',             'flat/' not in d)
print('layers/ gone:',           'layers/' not in d)
print('vapor_02 in sets:',       "'vapor_02'" in d)
print('ALL CLEAR:',              all(['vapor space bg' in d, 'space_parallax_backgrounds_v1' not in d, 'flat/' not in d, 'layers/' not in d]))
