import re

raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

# brace check
scripts=re.findall(r'<script[^>]*>(.*?)</script>',d,re.DOTALL)
s=scripts[0]
diff=s.count('{')-s.count('}')
print(f'Brace diff: {diff}')

# simulate panelH with typical values
LINE=22
# BASE
BASE_H = (24+66+26) + (24+20+20+20) + (24+14) + (24+44) + 20
print(f'BASE_H = {BASE_H}')

for scenario in [
    ('empty cargo, no modules, no net, no warn', 0, 0, 0, 0, 1),
    ('1 resource, 1 mod, net, fuel warn',         1, 1, 1, 1, 0),
    ('3 resources, 2 mods, net, no warn',         3, 2, 0, 1, 0),
    ('3 resources, 0 mods, no net, warn',         3, 0, 1, 0, 0),
]:
    label,rc,mc,fw,nr,eh = scenario
    panelH = BASE_H + fw*LINE + rc*LINE + eh*LINE + (mc*(LINE+2+mc*LINE) if mc else 0) + (nr*(LINE+2+LINE) if nr else 0)
    # simulate y walk
    y=30
    y+=LINE+2; y+=LINE; y+=LINE; y+=LINE; y+=LINE+4  # nav
    y+=LINE+2; y+=4; y+=16; y+=4; y+=16; y+=4; y+=16  # ship bars
    if fw: y+=LINE  # fuel warning
    y+=LINE+2; y+=14  # cargo sbar + bar
    y+=rc*LINE  # resource rows
    if eh==1: y+=LINE  # empty hold
    if mc: y+=LINE+2; y+=mc*LINE  # modules
    y+=LINE+2; y+=LINE; y+=LINE  # actions
    if nr: y+=LINE+2; y+=LINE  # network
    y+=14  # bottom padding
    needed=y-10  # panel starts at y=10, so height needed = final_y - 10
    print(f'  [{label}]')
    print(f'    panelH={panelH}  y_end={y}  needed={needed}  diff={panelH-needed}')
