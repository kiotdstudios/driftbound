raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')
import re
# find lines with boosting variable usage
lines=d.split('\n')
out=open('_boost_vars.txt','w',encoding='utf-8')
for i,l in enumerate(lines):
    if 'boosting' in l or ('keys[' in l and 'Shift' in l) or ('boost' in l.lower() and ('thrust' in l.lower() or 'keys' in l.lower() or 'fuel' in l.lower())):
        out.write(f"L{i+1}: {l.rstrip()}\n")
out.close()
print('done')
