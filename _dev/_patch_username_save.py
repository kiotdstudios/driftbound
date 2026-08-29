with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. Save username when lobbyConnect() reads it
# ══════════════════════════════════════════════════════════════════
OLD_NAME_READ = "  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();"
NEW_NAME_READ = """  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();
  if (name && name !== 'Pilot') localStorage.setItem('driftbound_username', name);"""

if OLD_NAME_READ in d:
    d = d.replace(OLD_NAME_READ, NEW_NAME_READ)
    fixes.append('username saved on connect')
else:
    fixes.append('lobbyConnect name read: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. Autofill lobby-name input from localStorage on page load
#    The IP prefill block is right after lobby HTML — add name prefill there
# ══════════════════════════════════════════════════════════════════
OLD_PREFILL = "  const field = document.getElementById('lobby-ip');"
NEW_PREFILL = """  // Autofill saved username
  const savedName = localStorage.getItem('driftbound_username');
  if (savedName) {
    const nameField = document.getElementById('lobby-name');
    if (nameField) nameField.value = savedName;
  }

  const field = document.getElementById('lobby-ip');"""

if OLD_PREFILL in d:
    d = d.replace(OLD_PREFILL, NEW_PREFILL)
    fixes.append('username autofilled on load')
else:
    fixes.append('prefill block: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 3. Also fold username into the main save blob so it travels
#    with the save file (nice-to-have, makes save self-contained)
# ══════════════════════════════════════════════════════════════════
OLD_SAVE_DATA = "    savedAt:      Date.now(),"
NEW_SAVE_DATA = """    savedAt:      Date.now(),
    username:     localStorage.getItem('driftbound_username') || null,"""

if OLD_SAVE_DATA in d:
    d = d.replace(OLD_SAVE_DATA, NEW_SAVE_DATA)
    fixes.append('username stored in save blob')
else:
    fixes.append('save blob: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
