txt = open('driftbound_flight_test.html','r',encoding='utf-8').read()

# Get the main loop function
idx = txt.find('function loop(')
if idx < 0:
    idx = txt.find('function loop ')
print('=== MAIN LOOP ===')
print(txt[idx:idx+600])

# Get update() full body
idx2 = txt.find('function update(')
print('\n=== UPDATE() START ===')
print(txt[idx2:idx2+800])

# Get the boot sequence
idx3 = txt.find('// ─── BOOT')
print('\n=== BOOT ===')
print(txt[idx3:idx3+400])

# Get image src path pattern - how assets are loaded
idx4 = txt.find("flat/${name}")
if idx4 < 0:
    idx4 = txt.find('flat/')
print('\n=== ASSET PATH ===')
print(txt[idx4:idx4+300])

# Check how asteroid images are loaded
idx5 = txt.find("rotations[")
print('\n=== ROTATIONS LOAD ===')
print(txt[idx5:idx5+400])

# Get canvas/ctx setup
idx6 = txt.find('const ctx')
print('\n=== CTX SETUP ===')
print(txt[idx6:idx6+200])
