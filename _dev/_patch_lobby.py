with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

old_connect = """function lobbyConnect() {
  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();
  const rawInput = (document.getElementById('lobby-ip').value || '').trim();
  // Strip protocol if browser autofilled the full URL
  const ipInput = rawInput.replace(/^https?:\\/\\//, '').replace(/\\/$/, '');
  const autoHost = window.location.hostname;
  const ip = ipInput || autoHost;
  const isLocal = ip==='localhost'||ip.startsWith('192.')||ip.startsWith('10.');
  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';"""

new_connect = """function lobbyConnect() {
  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();
  const rawInput = (document.getElementById('lobby-ip').value || '').trim();
  // Strip any protocol, trailing slashes, and port remnants from autofill
  const ipInput = rawInput
    .replace(/^wss?:\\/\\//, '')
    .replace(/^https?:\\/\\//, '')
    .replace(/\\/.*$/, '')   // strip any path after host
    .trim();
  const autoHost = window.location.hostname;
  const ip = ipInput || autoHost;
  const port = window.location.port;
  const isLocal = ip === 'localhost' || ip.startsWith('192.') || ip.startsWith('10.') || ip.startsWith('127.');
  // On Render (or any non-local host) use wss:// on the same host, no explicit port
  // Locally use ws:// with the dev port
  const url = isLocal
    ? 'ws://' + ip + ':' + (port || '8080') + '/ws'
    : 'wss://' + ip + '/ws';"""

if old_connect in d:
    d = d.replace(old_connect, new_connect)
    print('lobbyConnect URL builder: patched')
else:
    print('no exact match — trying relaxed replace')
    # Replace just the url line
    old_url = "  const url = isLocal ? 'ws://'+ip+':8080/ws' : 'wss://'+ip+'/ws';"
    new_url  = ("  const port = window.location.port;\n"
                "  const url = isLocal\n"
                "    ? 'ws://' + ip + ':' + (port || '8080') + '/ws'\n"
                "    : 'wss://' + ip + '/ws';")
    if old_url in d:
        d = d.replace(old_url, new_url)
        print('URL line: patched')
    else:
        print('URL line: no match either')

# Also pre-fill the lobby-ip field with current hostname on page load
# so it's never blank and never has a stale value
old_fill = "document.getElementById('lobby-ip').value"
# Find where the lobby IP placeholder is set (or find DOMContentLoaded)
# Inject a script block right before lobbyConnect
autofill_script = """\r\n<script>\r\n// Pre-fill lobby IP with current hostname so it's always correct\r\ndocument.addEventListener('DOMContentLoaded', () => {\r\n  const field = document.getElementById('lobby-ip');\r\n  if (field && !field.value) {\r\n    field.value = window.location.hostname;\r\n    field.placeholder = window.location.hostname;\r\n  }\r\n});\r\n</script>\r\n"""

if 'Pre-fill lobby IP' not in d:
    # Insert just before </body>
    idx = d.rfind('</body>')
    if idx != -1:
        d = d[:idx] + autofill_script + d[idx:]
        print('autofill script: injected')
    else:
        print('autofill: no </body> found')
else:
    print('autofill: already present')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

# Quick verify — build what the URL would be for Render
print()
host = 'driftbound-ir5b.onrender.com'
isLocal = host == 'localhost' or host.startswith('192.') or host.startswith('10.') or host.startswith('127.')
url = 'ws://' + host + ':8080/ws' if isLocal else 'wss://' + host + '/ws'
print(f'Render URL would be: {url}')
print('Expected:            wss://driftbound-ir5b.onrender.com/ws')
print('Match:', url == 'wss://driftbound-ir5b.onrender.com/ws')
