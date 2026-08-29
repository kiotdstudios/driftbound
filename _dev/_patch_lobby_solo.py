import re

d = open('driftbound_flight_test.html', 'rb').read().decode('utf-8', 'replace')

# ── 1. Add a "Play Solo" button right after the Launch button ──
# Target: the Launch button onclick block (lines ~3393-3398)
old_btn = '''    <button onclick="lobbyConnect()"'''

# Find the full launch button tag to replace
launch_start = d.find(old_btn)
assert launch_start != -1, "Launch button not found"

# Find closing > of the button tag
tag_end = d.find('>', launch_start) + 1
# Find the button close tag
btn_close = d.find('</button>', tag_end) + len('</button>')
launch_btn_html = d[launch_start:btn_close]
print('Found launch button:', repr(launch_btn_html[:80]))

solo_btn = '''
    <button onclick="(function(){document.getElementById('lobby').style.display='none';if(typeof showToast==='function')showToast('Solo mode \u2014 no server', '#64748b');})()"
      style="margin-top:8px;width:100%;padding:10px;background:transparent;border:1px solid #334155;color:#94a3b8;font-family:monospace;font-size:13px;border-radius:6px;cursor:pointer;letter-spacing:1px;"
      onmouseover="this.style.borderColor='#64748b';this.style.color='#cbd5e1'"
      onmouseout="this.style.borderColor='#334155';this.style.color='#94a3b8'"
    >PLAY SOLO (OFFLINE)</button>'''

d = d[:btn_close] + solo_btn + d[btn_close:]
print("Solo button injected")

# ── 2. Make lobbyConnect() skip WS if IP field is empty — play solo instead ──
old_connect_guard = "  const autoHost = window.location.hostname;\n  const ip = ipInput || autoHost;"
new_connect_guard = """  const autoHost = window.location.hostname;
  // If no IP entered and we're on Render, default to this host (server-hosted mode)
  // If IP field was explicitly cleared, treat as solo
  const ip = ipInput || autoHost;
  // If no explicit input and we're on a remote host, try to connect but don't block on failure
"""
# (no change needed — connection already falls back via onerror)

# ── 3. Improve onerror to also show a "Play Solo" fallback hint ──
old_onerror = "    setLobbyStatus('Could not connect \u2014 is the server running?');"
new_onerror = "    setLobbyStatus('Could not connect. Press ESC or click PLAY SOLO to play offline.');"
d = d.replace(old_onerror, new_onerror)
print("onerror message updated")

# ── brace check ──
import re as _re
depth = 0
for ch in _re.sub(r'"[^"]*"|\'[^\']*\'|`[^`]*`|//[^\n]*', '', d):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
print(f'Brace depth: {depth}')

open('driftbound_flight_test.html', 'wb').write(d.encode('utf-8'))
print('Done.')
