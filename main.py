"""
DRIFTBOUND Multiplayer Server
- Serves the game HTML + all assets as static files
- WebSocket multiplayer on the same port
- Visit: https://driftbound-ir5b.onrender.com/
"""
import asyncio, json, math, random, uuid, os

try:
    from aiohttp import web
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'aiohttp'])
    from aiohttp import web

PORT       = int(os.environ.get('PORT', 8080))
HOST       = '0.0.0.0'
TICK_RATE  = 20
WORLD_SIZE = 4000
NUM_ASTEROIDS = 30

ASTEROID_TYPES = [
    {'id':'sm_brown',  'hp':3,'oreMin':1,'oreMax':2,'lootType':'mineral',     'lootChance':0.02},
    {'id':'lg_brown',  'hp':5,'oreMin':2,'oreMax':3,'lootType':'mineral',     'lootChance':0.02},
    {'id':'lg_planet', 'hp':6,'oreMin':3,'oreMax':5,'lootType':'armalcolite', 'lootChance':1.00},
]
ASTEROID_POOL = [0,0,0,0,1,1,1,2,2,2]
SHIP_COLORS   = ['#00ff88','#ff6b35','#7c3aed','#facc15','#38bdf8']

players={};asteroids={};ore_pickups={};connected={}

def spawn_asteroid(aid=None):
    if aid is None: aid=str(uuid.uuid4())[:8]
    t=ASTEROID_TYPES[ASTEROID_POOL[random.randint(0,len(ASTEROID_POOL)-1)]]
    ang=random.uniform(0,math.pi*2);dist=random.uniform(400,WORLD_SIZE)
    return {'aid':aid,'type_id':t['id'],'lootType':t['lootType'],'lootChance':t['lootChance'],
            'hp':t['hp'],'maxHp':t['hp'],'oreMin':t['oreMin'],'oreMax':t['oreMax'],
            'worldX':math.cos(ang)*dist,'worldY':math.sin(ang)*dist,
            'angle':random.uniform(0,math.pi*2),'rotSpeed':(random.random()-0.5)*0.008,
            'driftVx':(random.random()-0.5)*0.08,'driftVy':(random.random()-0.5)*0.08}

def init_asteroids():
    for _ in range(NUM_ASTEROIDS):
        a=spawn_asteroid();asteroids[a['aid']]=a

def new_player(pid,name):
    color=SHIP_COLORS[len(players)%len(SHIP_COLORS)]
    return {'pid':pid,'name':name,'color':color,
            'worldX':random.uniform(-300,300),'worldY':random.uniform(-300,300),
            'vx':0,'vy':0,'dir':'north','speed':0,'animFrame':0,
            'hp':100,'fuel':10.0,'ore':0,'mineral':0,'armalcolite':0,
            'thrusting':False,'boosting':False}

async def broadcast(msg, exclude=None):
    data=json.dumps(msg)
    for pid,ws in list(connected.items()):
        if pid!=exclude:
            try: await ws.send_str(data)
            except: pass

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    pid = str(uuid.uuid4())[:8]
    connected[pid] = ws
    try:
        async for msg in ws:
            if msg.type != web.WSMsgType.TEXT:
                continue
            try: data = json.loads(msg.data)
            except: continue
            t = data.get('type')
            if t == 'join':
                name = data.get('name','Pilot')[:16]
                players[pid] = new_player(pid, name)
                p = players[pid]
                await ws.send_str(json.dumps({
                    'type':'init','pid':pid,'name':name,'color':p['color'],
                    'asteroids':list(asteroids.values()),
                    'ores':list(ore_pickups.values()),
                    'players':list(players.values()),
                }))
                await broadcast({'type':'player_joined','player':p}, exclude=pid)
                print(f'[+] {name} joined — {len(players)} online')
            elif t == 'move' and pid in players:
                p = players[pid]
                for k in ('worldX','worldY','vx','vy','dir','speed','animFrame',
                          'hp','fuel','ore','mineral','armalcolite','thrusting','boosting'):
                    if k in data: p[k] = data[k]
                await broadcast({'type':'player_move','pid':pid,'player':p}, exclude=pid)
            elif t == 'mine' and pid in players:
                aid=data.get('aid'); dmg=data.get('damage',1)
                if aid in asteroids:
                    ast=asteroids[aid]; ast['hp']=max(0,ast['hp']-dmg)
                    await broadcast({'type':'asteroid_hit','aid':aid,'hp':ast['hp'],'maxHp':ast['maxHp']})
                    if ast['hp']<=0:
                        amt=random.randint(ast['oreMin'],ast['oreMax'])
                        oid=str(uuid.uuid4())[:8]
                        new_ast=spawn_asteroid()
                        ore={'oid':oid,'worldX':ast['worldX'],'worldY':ast['worldY'],
                             'amount':amt,'lootType':ast['lootType'],'lootChance':ast['lootChance']}
                        ore_pickups[oid]=ore; asteroids[new_ast['aid']]=new_ast; del asteroids[aid]
                        await broadcast({'type':'asteroid_destroyed','aid':aid,'oid':oid,'ore':ore,'new_ast':new_ast})
            elif t == 'collect_ore' and pid in players:
                oid=data.get('oid')
                if oid in ore_pickups:
                    ore=ore_pickups.pop(oid)
                    players[pid]['ore']=players[pid].get('ore',0)+ore['amount']
                    loot=None
                    if ore.get('lootType') and random.random()<ore.get('lootChance',0):
                        loot=ore['lootType']
                        if loot=='mineral':     players[pid]['mineral']=players[pid].get('mineral',0)+1
                        if loot=='armalcolite': players[pid]['armalcolite']=players[pid].get('armalcolite',0)+1
                    p=players[pid]
                    await broadcast({'type':'ore_collected','oid':oid,'pid':pid,'loot':loot,
                                     'totals':{'ore':p['ore'],'mineral':p['mineral'],'armalcolite':p['armalcolite']}})
            elif t == 'refine' and pid in players:
                p=players[pid]
                if p.get('armalcolite',0)>0:
                    p['armalcolite']-=1; p['fuel']=min(10.0,p.get('fuel',0)+2.0)
                    await ws.send_str(json.dumps({'type':'refined','fuel':p['fuel'],'armalcolite':p['armalcolite']}))
    except Exception as e:
        print(f'[ws error] {e}')
    finally:
        connected.pop(pid,None); p=players.pop(pid,None)
        if p: await broadcast({'type':'player_left','pid':pid,'name':p['name']})
    return ws

async def tick_loop():
    while True:
        await asyncio.sleep(1/TICK_RATE)
        for ast in asteroids.values():
            ast['worldX']+=ast['driftVx']; ast['worldY']+=ast['driftVy']; ast['angle']+=ast['rotSpeed']

async def main():
    init_asteroids()
    app = web.Application()

    # WebSocket endpoint
    app.router.add_get('/ws', ws_handler)

    # Game HTML at root
    app.router.add_get('/', lambda r: web.FileResponse('driftbound_flight_test.html'))
    app.router.add_get('/driftbound_flight_test.html', lambda r: web.FileResponse('driftbound_flight_test.html'))

    # Static asset folders
    app.router.add_static('/pod_sprites',                    'pod_sprites',                    show_index=False)
    app.router.add_static('/space_parallax_backgrounds_v1',  'space_parallax_backgrounds_v1',  show_index=False)
    app.router.add_static('/Demo_assets',                    'Demo_assets',                    show_index=False)
    app.router.add_static('/vapor space bg',                 'vapor space bg',                 show_index=False)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    print(f'[DRIFTBOUND] Server running on port {PORT}')
    print(f'[DRIFTBOUND] Game: http://localhost:{PORT}/')
    print(f'[DRIFTBOUND] WS:   ws://localhost:{PORT}/ws')
    await tick_loop()

asyncio.run(main())
