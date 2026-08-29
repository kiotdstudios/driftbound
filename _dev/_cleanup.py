import os, shutil

base = r'C:\Users\diepowel\Documents\DRIFTBOUND'
dev_dir = os.path.join(base, '_dev')
os.makedirs(dev_dir, exist_ok=True)

# Files to KEEP in root
KEEP = {
    'driftbound_flight_test.html',
    'driftbound_flight_test.html.bak',
    'driftbound_server.py',
    'driftbound_server_replit.py',
    'driftbound_agent_context.json',
    'Driftbound_Game_Design_Document_v1.docx',
    'Ditharts_Free_Scifi_Tileset_v01.zip',
    'DEVLOG.md',
    'SHIP_STATS.md',
    'requirements.txt',
    'main.py',
    'serve.py',
    'modular_space_pod.zip',
    # temp cleanup scripts themselves
    '_cleanup.py',
}

moved = []
for f in os.listdir(base):
    fp = os.path.join(base, f)
    if not os.path.isfile(fp):
        continue
    if f in KEEP:
        continue
    if f.startswith('~$'):  # Word lock file
        continue
    # move to _dev/
    dest = os.path.join(dev_dir, f)
    shutil.move(fp, dest)
    moved.append(f)

print(f'Moved {len(moved)} files to _dev/:')
for f in sorted(moved):
    print(f'  {f}')

# Also clean __pycache__
pycache = os.path.join(base, '__pycache__')
if os.path.exists(pycache):
    shutil.rmtree(pycache)
    print('\nRemoved __pycache__/')
