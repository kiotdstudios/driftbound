data = open('driftbound_flight_test.html','rb').read()

old = b"const url  = 'ws://' + ip + ':8766';"
new = b"const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');\r\n  const url = isLocal ? 'ws://'+ip+':8766' : 'wss://'+ip;"

if old in data:
    data = data.replace(old, new)
    print("Patched!")
else:
    print("Not found")

open('driftbound_flight_test.html','wb').write(data)
