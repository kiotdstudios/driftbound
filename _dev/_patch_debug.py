import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

old = """  const ipInput = (document.getElementById('lobby-ip').value || '').trim();
  const autoHost = window.location.hostname;
  const ip = ipInput || autoHost;
  const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');
  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';
  console.log('[DB] lobbyConnect() called');
  console.log('[DB] window.location.hostname =', autoHost);
  console.log('[DB] window.location.href =', window.location.href);
  console.log('[DB] ipInput (from field) =', JSON.stringify(ipInput));
  console.log('[DB] ip resolved =', ip);
  console.log('[DB] isLocal =', isLocal);
  console.log('[DB] WebSocket URL =', url);"""

new = """  const rawInput = (document.getElementById('lobby-ip').value || '').trim();
  // Strip protocol if browser autofilled the full URL
  const ipInput = rawInput.replace(/^https?:\\/\\//, '').replace(/\\/$/, '');
  const autoHost = window.location.hostname;
  const ip = ipInput || autoHost;
  const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');
  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';
  console.log('[DB] lobbyConnect() called');
  console.log('[DB] window.location.hostname =', autoHost);
  console.log('[DB] rawInput =', JSON.stringify(rawInput));
  console.log('[DB] ipInput (cleaned) =', JSON.stringify(ipInput));
  console.log('[DB] ip resolved =', ip);
  console.log('[DB] isLocal =', isLocal);
  console.log('[DB] WebSocket URL =', url);"""

if old in d:
    d = d.replace(old, new)
    print('patched exact')
else:
    print('EXACT FAILED — trying regex')
    d = re.sub(
        r'const rawInput.*?console\.log\(\'\[DB\] WebSocket URL',
        new.split('console.log')[0] + "console.log('[DB] WebSocket URL",
        d, flags=re.DOTALL
    )

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('protocol strip present:', "replace(/^https?:\\/\\//," in d)
print('WebSocket URL log present:', "[DB] WebSocket URL" in d)
