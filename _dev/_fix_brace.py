import re
f=open('driftbound_flight_test.html','rb'); raw=f.read(); f.close()
d=raw.decode('utf-8','replace')

# Find the exact bytes around "}\nfunction drawAttachedPods"
target = 'function drawAttachedPods'
idx = d.find(target)
print('before target:', repr(d[idx-60:idx]))

# The stray brace is the lone } on the line just before the blank line before the function
# Check what's exactly there
chunk = d[idx-60:idx]
print('chunk repr:', repr(chunk))

# Remove just the last standalone } line before the function
# Pattern: ends with }\r\n\r\nfunction   or  }\n\nfunction
for old, new in [
    ('}\r\n\r\nfunction drawAttachedPods', '\r\n\r\nfunction drawAttachedPods'),
    ('}\n\nfunction drawAttachedPods',     '\n\nfunction drawAttachedPods'),
    ('}\r\nfunction drawAttachedPods',     '\r\nfunction drawAttachedPods'),
    ('}\nfunction drawAttachedPods',       '\nfunction drawAttachedPods'),
]:
    if old in d:
        count_before = d.count(old)
        d = d.replace(old, new, 1)
        print(f'Replaced: {repr(old[:40])} (was {count_before}x)')
        break
else:
    print('NO PATTERN MATCHED')

# verify
scripts=re.findall(r'<script[^>]*>(.*?)</script>',d,re.DOTALL)
s=scripts[0]
print('new brace diff:', s.count('{')-s.count('}'))

f=open('driftbound_flight_test.html','wb'); f.write(d.encode('utf-8')); f.close()
