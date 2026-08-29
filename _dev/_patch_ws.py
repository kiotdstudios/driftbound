import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# Replace the lobbyConnect function's isLocal + url logic
# so it auto-detects the host from window.location instead of the IP field
old = "  const ip   = (document.getElementById('lobby-ip').value  || 'localhost').trim();\r\n\r\n  const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');\r\n\r\n  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';"

new = """  const ipInput = (document.getElementById('lobby-ip').value || '').trim();
  const autoHost = window.location.hostname;
  const ip = ipInput || autoHost;
  const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');
  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';"""

if old in d:
    d = d.replace(old, new)
    print('patched via exact match')
else:
    # fallback: regex
    d = re.sub(
        r"const ip\s*=\s*\(document\.getElementById\('lobby-ip'\)\.value\s*\|\|\s*'localhost'\)\.trim\(\);[\s\S]*?const url = isLocal \? 'ws://'\+ip\+':8080/ws' : 'wss://'\+ip\+'/ws';",
        new, d
    )
    print('patched via regex')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

# verify
idx = d.find('autoHost')
print('autoHost present:', idx != -1)
print(d[idx-50:idx+200])
