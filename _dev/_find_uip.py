import re
d = open('driftbound_flight_test.html','rb').read().decode('utf-8','replace')
# find what comes right after updateInteriorPlayer closing brace
m = re.search(r'function updateInteriorPlayer\(\).*?(?=\nfunction |\n// ── INTERIOR FADE)', d, re.DOTALL)
if m:
    print('Found, ends at char', m.end())
    print('Tail of function:', repr(d[m.end()-80:m.end()+60]))
else:
    # find by brace counting
    idx = d.find('function updateInteriorPlayer()')
    print('Function start at:', idx)
    depth = 0; i = idx
    while i < len(d):
        if d[i]=='{': depth+=1
        elif d[i]=='}':
            depth-=1
            if depth==0:
                print('Function end at:', i)
                print('Context after:', repr(d[i:i+100]))
                break
        i+=1
