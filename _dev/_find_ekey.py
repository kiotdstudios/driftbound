raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')
import re

# find KeyE references
for m in re.finditer(r".{0,60}KeyE.{0,80}", d):
    print(repr(m.group()))
    print('---')

# find drawHUD call in loop
for m in re.finditer(r".{0,40}drawHUD.{0,40}", d):
    print(repr(m.group()))
    print('---')
