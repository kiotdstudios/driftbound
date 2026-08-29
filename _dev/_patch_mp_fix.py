html = open('driftbound_flight_test.html','r',encoding='utf-8').read()

# Find the last </script> and inject MULTI_JS right before it
MULTI_JS = """
// ═══════════════════════════════════════════════════════════════════════════
// DRIFTBOUND MULTIPLAYER CLIENT
// ═══════════════════════════════════════════════════════════════════════════

let socket        = null;
let myPid         = null;
let myColor       = '#00ff88';
let remotePlayers = {};
let serverAsteroids = {};
let serverOres    = {};
let multiMode     = false;
let serverTick    = 0;

function lobbyConnect() {
  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();
  const ip   = (document.getElementById('lobby-ip').value  || 'localhost').trim();
  const url  = 'ws://' + ip + ':8766';
  setLobbyStatus('Connecting to ' + url + '...');
  try { socket = new WebSocket(url); } catch(e) { setLobbyStatus('Invalid address.'); return; }
  socket.onopen    = () => socket.send(JSON.stringify({ type: 'join', name }));
  socket.onmessage = (ev) => handleServerMsg(JSON.parse(ev.data));
  socket.onerror   = () => { setLobbyStatus('Could not connect — is the server running?'); socket = null; };
  socket.onclose   = () => { if (multiMode) showToast('Disconnected from server', '#ef4444'); multiMode = false; socket = null; };
}

function setLobbyStatus(msg) {
  document.getElementById('lobby-status').textContent = msg;
}

function handleServerMsg(msg) {
  switch (msg.type) {
    case 'init':
      myPid   = msg.pid;
      myColor = msg.color;
      multiMode = true;
      serverAsteroids = {};
      for (const a of msg.asteroids) serverAsteroids[a.aid] = a;
      serverOres = {};
      for (const o of msg.ores) serverOres[o.oid] = o;
      remotePlayers = {};
      for (const p of msg.players) { if (p.pid !== myPid) remotePlayers[p.pid] = p; }
      document.getElementById('lobby').style.display = 'none';
      showToast('Connected as ' + msg.name, myColor);
      break;

    case 'state':
      remotePlayers = {};
      for (const p of msg.players) { if (p.pid !== myPid) remotePlayers[p.pid] = p; }
      serverAsteroids = {};
      for (const a of msg.asteroids) serverAsteroids[a.aid] = a;
      serverOres = {};
      for (const o of msg.ores) serverOres[o.oid] = o;
      break;

    case 'player_joined':
      if (msg.player.pid !== myPid) { remotePlayers[msg.player.pid] = msg.player; showToast('\u26a1 ' + msg.player.name + ' entered the drift', '#38bdf8'); }
      break;

    case 'player_left':
      delete remotePlayers[msg.pid];
      showToast('\u2756 ' + msg.name + ' disconnected', '#64748b');
      break;

    case 'asteroid_hit':
      if (serverAsteroids[msg.aid]) serverAsteroids[msg.aid].hp = msg.hp;
      break;

    case 'asteroid_destroyed':
      delete serverAsteroids[msg.aid];
      serverOres[msg.oid] = msg.ore;
      serverAsteroids[msg.new_ast.aid] = msg.new_ast;
      break;

    case 'ore_collected':
      delete serverOres[msg.oid];
      ship.ore = msg.totals.ore; ship.mineral = msg.totals.mineral; ship.armalcolite = msg.totals.armalcolite;
      if (msg.loot === 'mineral')      showToast('\u2756 MINERAL MATERIAL found! (' + ship.mineral + ' held)', '#a78bfa');
      else if (msg.loot === 'armalcolite') showToast('\u25c8 ARMALCOLITE extracted (' + ship.armalcolite + ' held)', '#34d399');
      break;

    case 'ore_gone':
      delete serverOres[msg.oid];
      break;

    case 'refined':
      ship.fuel = msg.fuel; ship.armalcolite = msg.armalcolite;
      showToast('REFINED ARMALCOLITE \u2192 +2.0 FUEL  (' + ship.fuel.toFixed(1) + ')', '#34d399');
      break;
  }
}

let _lastSend = 0;
let _thrusting = false;
let _boosting  = false;

function sendMove() {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  const now = performance.now();
  if (now - _lastSend < 50) return;
  _lastSend = now;
  socket.send(JSON.stringify({
    type: 'move', worldX: ship.worldX, worldY: ship.worldY,
    vx: ship.vx, vy: ship.vy, dir: ship.dir,
    speed: Math.hypot(ship.vx, ship.vy), animFrame: ship.animFrame,
    hp: ship.hp, fuel: ship.fuel, ore: ship.ore,
    mineral: ship.mineral, armalcolite: ship.armalcolite,
    thrusting: _thrusting, boosting: _boosting,
  }));
}

function sendMine(aid, damage) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type: 'mine', aid, damage }));
}

function sendCollectOre(oid) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type: 'collect_ore', oid }));
}

function sendRefine() {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type: 'refine' }));
}

function drawRemotePlayers(cx, cy) {
  if (!multiMode) return;
  for (const p of Object.values(remotePlayers)) {
    const sx = cx + (p.worldX - ship.worldX);
    const sy = cy + (p.worldY - ship.worldY);
    const margin = 120;
    if (sx < -margin || sx > canvas.width + margin || sy < -margin || sy > canvas.height + margin) {
      drawPlayerIndicator(p, cx, cy, sx, sy);
      continue;
    }
    ctx.save();
    ctx.translate(sx, sy);
    ctx.shadowColor = p.color; ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.moveTo(0, -18); ctx.lineTo(11, 8); ctx.lineTo(0, 4); ctx.lineTo(-11, 8);
    ctx.closePath();
    ctx.fillStyle = p.color + 'cc'; ctx.fill();
    ctx.strokeStyle = p.color; ctx.lineWidth = 1.5; ctx.stroke();
    if (p.boosting || p.thrusting) {
      ctx.beginPath(); ctx.moveTo(-5,6); ctx.lineTo(0, 14+Math.random()*4); ctx.lineTo(5,6);
      ctx.fillStyle = p.color + '88'; ctx.fill();
    }
    ctx.shadowBlur = 0; ctx.restore();
    ctx.save();
    ctx.font = '10px monospace'; ctx.fillStyle = p.color; ctx.textAlign = 'center';
    ctx.fillText(p.name, sx, sy - 26);
    const barW = 36, hpPct = Math.max(0, p.hp / 100);
    ctx.fillStyle = '#0d1520';
    ctx.fillRect(sx - barW/2 - 1, sy - 22, barW + 2, 4);
    ctx.fillStyle = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#f59e0b' : '#ef4444';
    ctx.fillRect(sx - barW/2, sy - 21, barW * hpPct, 2);
    ctx.restore();
  }
}

function drawPlayerIndicator(p, cx, cy, sx, sy) {
  const angle = Math.atan2(sy - cy, sx - cx);
  const r     = Math.min(canvas.width, canvas.height) / 2 - 40;
  const edgeX = cx + Math.cos(angle) * r;
  const edgeY = cy + Math.sin(angle) * r;
  const dist  = Math.round(Math.hypot(sx - cx, sy - cy) / 10) / 10;
  ctx.save();
  ctx.translate(edgeX, edgeY); ctx.rotate(angle + Math.PI / 2);
  ctx.beginPath(); ctx.moveTo(0,-8); ctx.lineTo(6,4); ctx.lineTo(-6,4); ctx.closePath();
  ctx.fillStyle = p.color + 'cc'; ctx.fill();
  ctx.restore();
  ctx.save();
  ctx.font = '9px monospace'; ctx.fillStyle = p.color + 'aa'; ctx.textAlign = 'center';
  ctx.fillText(p.name + ' ' + dist + 'km', edgeX, edgeY + 20);
  ctx.restore();
}
"""

# Inject right before the last </script>
last_close = html.rfind('</script>')
html = html[:last_close] + MULTI_JS + '\n' + html[last_close:]
print("MULTI_JS injected before </script>")

# Fix sendMove() call in update — add after 'return speed;'
old_ret = "  return speed;\n}"
new_ret = """  _thrusting = thrusting;
  _boosting  = shiftHeld;
  if (multiMode) sendMove();
  return speed;
}"""
if old_ret in html:
    html = html.replace(old_ret, new_ret, 1)
    print("sendMove() hooked into update()")
else:
    print("WARNING: return speed not found")

# Fix FPS HUD to show pilot count
old_fps = "fpsDisplay + ' FPS'"
new_fps  = "fpsDisplay + ' FPS' + (multiMode ? '  |  ' + (Object.keys(remotePlayers).length + 1) + ' PILOTS' : '')"
if old_fps in html:
    html = html.replace(old_fps, new_fps, 1)
    print("HUD pilot count added")
else:
    print("WARNING: FPS HUD line not found")

open('driftbound_flight_test.html','w',encoding='utf-8').write(html)
print("\n=== FIX COMPLETE ===")
print("Verifying...")
for token, label in [('sendMove','sendMove'),('drawPlayerIndicator','drawPlayerIndicator'),('8766','port 8766'),('lobbyConnect','lobbyConnect'),('multiMode','multiMode')]:
    print(f"  {label}: {'OK' if token in html else 'MISSING'}")
