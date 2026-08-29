"""
DRIFTBOUND Multiplayer Server — Replit Edition
WebSocket only (no HTTP server — Replit handles HTTP itself)
"""

import asyncio, json, math, random, time, uuid, os
from pathlib import Path

try:
    import websockets
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'websockets'])
    import websockets

# ─── CONFIG ──────────────────────────────────────────────────────────────────
HOST            = '0.0.0.0'
WS_PORT         = int(os.environ.get('PORT', 8766))  # Replit sets PORT env var
TICK_RATE       = 20
WORLD_SIZE      = 4000
NUM_ASTEROIDS   = 30

# ─── ASTEROID TYPES ──────────────────────────────────────────────────────────
ASTEROID_TYPES = [
    {'id': 'sm_brown',  'hp': 3, 'oreMin': 1, 'oreMax': 2, 'lootType': 'mineral',     'lootChance': 0.02},
    {'id': 'lg_brown',  'hp': 5, 'oreMin': 2, 'oreMax': 3, 'lootType': 'mineral',     'lootChance': 0.02},
    {'id': 'lg_planet', 'hp': 6, 'oreMin': 3, 'oreMax': 5, 'lootType': 'armalcolite', 'lootChance': 1.00},
]
ASTEROID_POOL = [0,0,0,0, 1,1,1, 2,2,2]
SHIP_COLORS   = ['#00ff88', '#ff6b35', '#7c3aed', '#facc15', '#38bdf8']

# ─── STATE ───────────────────────────────────────────────────────────────────
players     = {}
asteroids   = {}
ore_pickups = {}
connected   = {}

def spawn_asteroid(aid=None):
    if aid is None: aid = str(uuid.uuid4())[:8]
    t   = ASTEROID_TYPES[ASTEROID_POOL[random.randint(0, len(ASTEROID_POOL)-1)]]
    ang = random.uniform(0, math.pi * 2)
    dist = random.uniform(400, WORLD_SIZE)
    return {
        'aid': aid, 'type_id': t['id'], 'lootType': t['lootType'],
        'lootChance': t['lootChance'], 'hp': t['hp'], 'maxHp': t['hp'],
        'oreMin': t['oreMin'], 'oreMax': t['oreMax'],
        'worldX': math.cos(ang)*dist, 'worldY': math.sin(ang)*dist,
        'angle': random.uniform(0, math.pi*2),
        'rotSpeed': (random.random()-0.5)*0.008,
        'driftVx': (random.random()-0.5)*0.08,
        'driftVy': (random.random()-0.5)*0.08,
    }

def init_asteroids():
    for _ in range(NUM_ASTEROIDS):
        a = spawn_asteroid(); asteroids[a['aid']] = a

def new_player(pid, name):
    color = SHIP_COLORS[len(players) % len(SHIP_COLORS)]
    return {
        'pid': pid, 'name': name, 'color': color,
        'worldX': random.uniform(-300,300), 'worldY': random.uniform(-300,300),
        'vx': 0, 'vy': 0, 'dir': 'north', 'speed': 0, 'animFrame': 0,
        'hp': 100, 'fuel': 10.0, 'ore': 0, 'mineral': 0, 'armalcolite': 0,
        'thrusting': False, 'boosting': False, 'lastSeen': time.time(),
    }

async def broadcast(msg, exclude=None):
    data = json.dumps(msg)
    for pid, ws in list(connected.items()):
        if pid != exclude:
            try: await ws.send(data)
            except: pass

async def handle(ws):
    pid = str(uuid.uuid4())[:8]
    connected[pid] = ws
    try:
        async for raw in ws:
            try: msg = json.loads(raw)
            except: continue
            t = msg.get('type')

            if t == 'join':
                name = msg.get('name','Pilot')[:16]
                players[pid] = new_player(pid, name)
                await ws.send(json.dumps({
                    'type': 'welcome', 'pid': pid, 'player': players[pid],
                    'asteroids': list(asteroids.values()),
                    'ore_pickups': list(ore_pickups.values()),
                    'players': list(players.values()),
                }))
                await broadcast({'type':'player_join','player':players[pid]}, exclude=pid)
                print(f'[+] {name} ({pid}) joined — {len(players)} pilots online')

            elif t == 'move' and pid in players:
                p = players[pid]
                for k in ('worldX','worldY','vx','vy','dir','speed','animFrame','hp','fuel','ore','mineral','armalcolite','thrusting','boosting'):
                    if k in msg: p[k] = msg[k]
                p['lastSeen'] = time.time()
                await broadcast({'type':'player_move','pid':pid,'player':p}, exclude=pid)

            elif t == 'mine' and pid in players:
                aid = msg.get('aid'); dmg = msg.get('damage',1)
                if aid in asteroids:
                    ast = asteroids[aid]
                    ast['hp'] = max(0, ast['hp'] - dmg)
                    await broadcast({'type':'asteroid_hit','aid':aid,'hp':ast['hp'],'maxHp':ast['maxHp']})
                    if ast['hp'] <= 0:
                        amt = random.randint(ast['oreMin'], ast['oreMax'])
                        oid = str(uuid.uuid4())[:8]
                        ore = {'oid':oid,'worldX':ast['worldX'],'worldY':ast['worldY'],
                               'amount':amt,'lootType':ast['lootType'],'lootChance':ast['lootChance']}
                        ore_pickups[oid] = ore
                        del asteroids[aid]
                        await broadcast({'type':'asteroid_destroyed','aid':aid,'ore':ore})
                        asyncio.get_event_loop().call_later(15, lambda a=aid: asyncio.ensure_future(respawn_asteroid(a)))

            elif t == 'collect_ore' and pid in players:
                oid = msg.get('oid')
                if oid in ore_pickups:
                    ore = ore_pickups.pop(oid)
                    players[pid]['ore'] = players[pid].get('ore',0) + ore['amount']
                    loot = None
                    if ore.get('lootType') and random.random() < ore.get('lootChance',0):
                        loot = ore['lootType']
                        if loot == 'mineral':    players[pid]['mineral']     = players[pid].get('mineral',0) + 1
                        if loot == 'armalcolite': players[pid]['armalcolite'] = players[pid].get('armalcolite',0) + 1
                    await broadcast({'type':'ore_collected','oid':oid,'pid':pid,'loot':loot})

            elif t == 'refine' and pid in players:
                p = players[pid]
                if p.get('armalcolite',0) > 0:
                    p['armalcolite'] -= 1
                    p['fuel'] = min(10.0, p.get('fuel',0) + 2.0)
                    await ws.send(json.dumps({'type':'refined','fuel':p['fuel'],'armalcolite':p['armalcolite']}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected.pop(pid, None)
        p = players.pop(pid, None)
        if p:
            await broadcast({'type':'player_leave','pid':pid,'name':p['name']})
            print(f'[-] {p["name"]} ({pid}) left — {len(players)} pilots online')

async def respawn_asteroid(aid):
    a = spawn_asteroid(aid)
    asteroids[aid] = a
    await broadcast({'type':'asteroid_spawn','asteroid':a})

async def tick_loop():
    while True:
        await asyncio.sleep(1/TICK_RATE)
        # Drift asteroids
        for ast in asteroids.values():
            ast['worldX'] += ast['driftVx']
            ast['worldY'] += ast['driftVy']
            ast['angle']  += ast['rotSpeed']
        # Prune stale ore
        now = time.time()
        stale = [oid for oid,o in ore_pickups.items() if o.get('spawned',now) < now-30]
        for oid in stale: ore_pickups.pop(oid,None)

async def main():
    init_asteroids()
    print(f'[DRIFTBOUND] Server starting on ws://0.0.0.0:{WS_PORT}')
    print(f'[DRIFTBOUND] {len(asteroids)} asteroids spawned')
    async with websockets.serve(handle, HOST, WS_PORT):
        await tick_loop()

if __name__ == '__main__':
    asyncio.run(main())
