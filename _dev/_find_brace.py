import re
f=open('driftbound_flight_test.html','rb'); raw=f.read(); f.close()
d=raw.decode('utf-8','replace')
s=re.findall(r'<script[^>]*>(.*?)</script>',d,re.DOTALL)[0]
lines=s.split('\n')
depth=0
for i,l in enumerate(lines,1):
    prev=depth
    depth += l.count('{') - l.count('}')
    if depth < prev and depth < 0:
        print(f'L{i} depth={depth}: {repr(l[:100])}')
        # show context
        for j in range(max(0,i-4),min(len(lines),i+4)):
            print(f'  ctx L{j+1}: {repr(lines[j][:80])}')
        break
print('final depth:',depth)
