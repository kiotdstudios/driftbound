"""
DRIFTBOUND Multiplayer Server
Run: py driftbound_server.py
Serves game on http://0.0.0.0:8765
WebSocket on ws://0.0.0.0:8765/ws
"""

import asyncio
import json
import math
import random
import time
import uuid
import http.server
import threading
import os
from pathlib import Path

try:
    import websockets
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'websockets'])
    import websockets

# ─── CONFIG ───────────────────────────────────────────────────────────────────
HOST            = '0.0.0.0'
WS_PORT         = 8766
HTTP_PORT       = 8765
TICK_RATE       = 20          # server ticks per second
WORLD_SIZE      = 4000
NUM_ASTEROIDS   = 30
GAME_DIR        = Path(__file__).parent

# ─── ASTEROID TYPES (mirrors client) ─────────────────────────────────────────
ASTEROID_TYPES = [
    {'id': 'sm_brown',  'hp': 3, 'oreMin': 1, 'oreMax': 2, 'lootType': 'mineral',     'lootChance': 0.02},
    {'id': 'lg_brown',  'hp': 5, 'oreMin': 2, 'oreMax': 3, 'lootType': 'mineral',     'lootChance': 0.02},
    {'id': 'lg_planet', 'hp': 6, 'oreMin': 3, 'oreMax': 5, 'lootType': 'armalcolite', 'lootChance': 1.00},
]
# Spawn weights: sm_brown x4, lg_brown x3, lg_planet x3
ASTEROID_POOL = [0,0,0,0, 1,1,1, 2,2,2]

SHIP_COLORS = ['#00ff88', '#ff6b35', '#7c3aed', '#facc15', '#38bdf8']

# ─── SERVER STATE ─────────────────────────────────────────────────────────────
players    = {}    # pid -> player dict
asteroids  = {}    # aid -> asteroid dict
ore_pickups = {}   # oid -> ore dict
connected  = {}    # pid -> websocket

def spawn_asteroid(aid=None):
    if aid is None:
        aid = str(uuid.uuid4())[:8]
    t   = ASTEROID_TYPES[ASTEROID_POOL[random.randint(0, len(ASTEROID_POOL)-1)]]
    ang = random.uniform(0, math.pi * 2)
    dist = random.uniform(400, WORLD_SIZE)
    return {
        'aid':      aid,
        'type_id':  t['id'],
        'lootType': t['lootType'],
        'lootChance': t['lootChance'],
        'hp':       t['hp'],
        'maxHp':    t['hp'],
        'oreMin':   t['oreMin'],
        'oreMax':   t['oreMax'],
        'worldX':   math.cos(ang) * dist,
        'worldY':   math.sin(ang) * dist,
        'angle':    random.uniform(0, math.pi * 2),
        'rotSpeed': (random.random() - 0.5) * 0.008,
        'driftVx':  (random.random() - 0.5) * 0.08,
        'driftVy':  (random.random() - 0.5) * 0.08,
    }

def init_asteroids():
    for _ in range(NUM_ASTEROIDS):
        a = spawn_asteroid()
        asteroids[a['aid']] = a

def new_player(pid, name):
    color = SHIP_COLORS[len(players) % len(SHIP_COLORS)]
    return {
        'pid':          pid,
        'name':         name,
        'color':        color,
        'worldX':       random.uniform(-300, 300),
        'worldY':       random.uniform(-300, 300),
        'vx':           0,
        'vy':           0,
        'dir':          'north',
        'speed':        0,
        'animFrame':    0,
        'hp':           100,
        'fuel':         10.0,
        'ore':          0,
        'mineral':      0,
        'armalcolite':  0,
        'thrusting':    False,
        'boosting':     False,
        'lastSeen':     time.time(),
    }

# ─── BROADCAST ────────────────────────────────────────────────────────────────
async def broadcast(msg, exclude=None):
    if not connected:
        return
    data = json.dumps(msg)
    dead = []
    for pid, ws in connected.items():
        if pid == exclude:
            continue
        try:
            await ws.send(data)
        except Exception:
            dead.append(pid)
    for pid in dead:
        await drop_player(pid)

async def send_to(pid, msg):
    ws = connected.get(pid)
    if ws:
        try:
            await ws.send(json.dumps(msg))
        except Exception:
            pass

async def drop_player(pid):
    connected.pop(pid, None)
    p = players.pop(pid, None)
    if p:
        await broadcast({'type': 'player_left', 'pid': pid, 'name': p['name']})
        print(f'[DRIFTBOUND] {p["name"]} disconnected. {len(players)} players online.')

# ─── SERVER TICK ─────────────────────────────────────────────────────────────
async def game_tick():
    while True:
        await asyncio.sleep(1 / TICK_RATE)
        if not players:
            continue

        # Drift asteroids
        for a in asteroids.values():
            a['worldX'] += a['driftVx']
            a['worldY'] += a['driftVy']
            a['angle']  += a['rotSpeed']

        # Drift ore pickups + expire
        expired = []
        for oid, o in ore_pickups.items():
            o['life'] -= 1
            o['worldX'] += o.get('vx', 0)
            o['worldY'] += o.get('vy', 0)
            if o['life'] <= 0:
                expired.append(oid)
        for oid in expired:
            ore_pickups.pop(oid, None)

        # Build state snapshot
        state = {
            'type':      'state',
            'players':   list(players.values()),
            'asteroids': list(asteroids.values()),
            'ores':      list(ore_pickups.values()),
            't':         time.time(),
        }
        await broadcast(state)

# ─── MESSAGE HANDLER ─────────────────────────────────────────────────────────
async def handle_message(pid, raw):
    try:
        msg = json.loads(raw)
    except Exception:
        return

    mtype = msg.get('type')
    p     = players.get(pid)

    if mtype == 'move':
        if p:
            p['worldX']   = msg.get('worldX',  p['worldX'])
            p['worldY']   = msg.get('worldY',  p['worldY'])
            p['vx']       = msg.get('vx',       0)
            p['vy']       = msg.get('vy',       0)
            p['dir']      = msg.get('dir',      p['dir'])
            p['speed']    = msg.get('speed',    0)
            p['animFrame']= msg.get('animFrame',0)
            p['hp']       = msg.get('hp',       p['hp'])
            p['fuel']     = msg.get('fuel',     p['fuel'])
            p['ore']      = msg.get('ore',      p['ore'])
            p['mineral']  = msg.get('mineral',  p['mineral'])
            p['armalcolite'] = msg.get('armalcolite', p['armalcolite'])
            p['thrusting']= msg.get('thrusting', False)
            p['boosting'] = msg.get('boosting',  False)
            p['lastSeen'] = time.time()

    elif mtype == 'mine':
        # Player hit an asteroid
        aid    = msg.get('aid')
        damage = msg.get('damage', 1)
        a      = asteroids.get(aid)
        if a:
            a['hp'] -= damage
            if a['hp'] <= 0:
                # Asteroid destroyed — spawn ore
                ore_amount = random.randint(a['oreMin'], a['oreMax'])
                oid = str(uuid.uuid4())[:8]
                ore_pickups[oid] = {
                    'oid':       oid,
                    'worldX':    a['worldX'],
                    'worldY':    a['worldY'],
                    'amount':    ore_amount,
                    'lootType':  a['lootType'],
                    'lootChance':a['lootChance'],
                    'vx':        (random.random()-0.5)*0.5,
                    'vy':        (random.random()-0.5)*0.5,
                    'life':      600,
                }
                asteroids.pop(aid, None)
                # Respawn a new asteroid elsewhere
                new_a = spawn_asteroid()
                asteroids[new_a['aid']] = new_a
                await broadcast({
                    'type':    'asteroid_destroyed',
                    'aid':     aid,
                    'oid':     oid,
                    'ore':     ore_pickups[oid],
                    'new_ast': new_a,
                })
            else:
                await broadcast({
                    'type': 'asteroid_hit',
                    'aid':  aid,
                    'hp':   a['hp'],
                })

    elif mtype == 'collect_ore':
        oid = msg.get('oid')
        o   = ore_pickups.pop(oid, None)
        if o and p:
            p['ore'] += o['amount']
            # Loot roll
            loot = None
            if o.get('lootType') and random.random() < o.get('lootChance', 0):
                if o['lootType'] == 'mineral':
                    p['mineral'] += 1
                    loot = 'mineral'
                elif o['lootType'] == 'armalcolite':
                    p['armalcolite'] += 1
                    loot = 'armalcolite'
            await send_to(pid, {
                'type':   'ore_collected',
                'oid':    oid,
                'amount': o['amount'],
                'loot':   loot,
                'totals': {
                    'ore':          p['ore'],
                    'mineral':      p['mineral'],
                    'armalcolite':  p['armalcolite'],
                }
            })
            # Tell others this ore is gone
            await broadcast({'type': 'ore_gone', 'oid': oid}, exclude=pid)

    elif mtype == 'refine':
        if p and p['armalcolite'] > 0:
            p['armalcolite'] -= 1
            gained = 2.0
            p['fuel'] = min(10.0, p['fuel'] + gained)
            await send_to(pid, {
                'type':  'refined',
                'fuel':  p['fuel'],
                'armalcolite': p['armalcolite'],
            })

# ─── WEBSOCKET HANDLER ───────────────────────────────────────────────────────
async def ws_handler(websocket):
    # First message must be join
    try:
        raw  = await asyncio.wait_for(websocket.recv(), timeout=10)
        msg  = json.loads(raw)
        if msg.get('type') != 'join':
            await websocket.close()
            return
        name = str(msg.get('name', 'Pilot'))[:20].strip() or 'Pilot'
        pid  = str(uuid.uuid4())[:8]
        p    = new_player(pid, name)
        players[pid]   = p
        connected[pid] = websocket

        print(f'[DRIFTBOUND] {name} joined ({pid}). {len(players)} players online.')

        # Send this player their init packet
        await send_to(pid, {
            'type':       'init',
            'pid':        pid,
            'name':       name,
            'color':      p['color'],
            'players':    list(players.values()),
            'asteroids':  list(asteroids.values()),
            'ores':       list(ore_pickups.values()),
        })

        # Tell everyone else
        await broadcast({'type': 'player_joined', 'player': p}, exclude=pid)

        # Listen loop
        async for raw in websocket:
            await handle_message(pid, raw)

    except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
        pass
    except Exception as e:
        print(f'[DRIFTBOUND] Error: {e}')
    finally:
        if 'pid' in locals():
            await drop_player(pid)

# ─── HTTP SERVER (serves game files) ─────────────────────────────────────────
class GameHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(GAME_DIR), **kwargs)
    def log_message(self, fmt, *args):
        pass  # silence access logs

def run_http():
    server = http.server.HTTPServer((HOST, HTTP_PORT), GameHTTPHandler)
    print(f'[DRIFTBOUND] HTTP  → http://localhost:{HTTP_PORT}/driftbound_flight_test.html')
    server.serve_forever()

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    init_asteroids()
    print(f'[DRIFTBOUND] Server starting...')
    print(f'[DRIFTBOUND] WS    → ws://localhost:{WS_PORT}')
    print(f'[DRIFTBOUND] {NUM_ASTEROIDS} asteroids spawned')
    print(f'[DRIFTBOUND] Share your IP with your friend to play together')
    print(f'─────────────────────────────────────────────────')

    # HTTP in background thread
    t = threading.Thread(target=run_http, daemon=True)
    t.start()

    # Game tick + WS server
    async with websockets.serve(ws_handler, HOST, WS_PORT):
        await game_tick()

if __name__ == '__main__':
    asyncio.run(main())
