lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Line 938 col 25
l = lines[937]
print(f"Line 938: {repr(l)}")
print(f"Col 25 char: {repr(l[24]) if len(l) > 24 else 'N/A'}")

# Check for non-ASCII / hidden chars in lines 935-940
print("\n=== Raw bytes check lines 935-940 ===")
raw = open('driftbound_flight_test.html','rb').readlines()
for i in range(934, 940):
    b = raw[i]
    has_odd = any(c > 127 or (c < 32 and c not in (9,10,13)) for c in b)
    marker = ' <<<< SUSPICIOUS' if has_odd else ''
    print(f'{i+1:4}: {b[:80]}{marker}')

# Also scan ALL lines for hidden/non-ASCII chars
print("\n=== All non-ASCII lines in script ===")
for i, b in enumerate(raw):
    if any(c > 127 or (c < 32 and c not in (9,10,13)) for c in b):
        print(f'{i+1:4}: {b[:100]}')
