txt = open('driftbound_flight_test.html', 'r', encoding='utf-8').read()

# ─── 1. Inject lobby HTML overlay (before </body>)
LOBBY_HTML = """
<!-- ─── MULTIPLAYER LOBBY ──────────────────────────────────────────────── -->
<div id="lobby" style="
  position:fixed; inset:0; background:#020810ee;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  z-index:999; font-family:monospace; color:#e2e8f0;
">
  <div style="font-size:11px;letter-spacing:4px;color:#64748b;margin-bottom:8px;">DRIFTBOUND</div>
  <div style="font-size:28px;font-weight:bold;letter-spacing:2px;color:#7c3aed;margin-bottom:4px;">MULTIPLAYER</div>
  <div style="font-size:11px;letter-spacing:3px;color:#475569;margin-bottom:40px;">ALPHA</div>

  <div style="width:320px;">
    <div style="font-size:10px;letter-spacing:2px;color:#64748b;margin-bottom:8px;">PILOT NAME</div>
    <input id="lobby-name" maxlength="16" placeholder="Enter your name..."
      style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid #334155;
             color:#e2e8f0;padding:12px 16px;font-size:14px;font-family:monospace;
             outline:none;letter-spacing:1px;margin-bottom:16px;"
      onkeydown="if(event.key==='Enter')lobbyConnect()"
    />
    <div style="font-size:10px;letter-spacing:2px;color:#64748b;margin-bottom:8px;">SERVER IP</div>
    <input id="lobby-ip" placeholder="localhost  (or friend's IP)"
      style="width:100%;box-sizing:border-box;background:#0f172a;border:1px solid #334155;
             color:#e2e8f0;padding:12px 16px;font-size:14px;font-family:monospace;
             outline:none;letter-spacing:1px;margin-bottom:24px;"
      onkeydown="if(event.key==='Enter')lobbyConnect()"
    />
    <button onclick="lobbyConnect()"
      style="width:100%;padding:14px;background:#7c3aed;border:none;color:#fff;
             font-size:13px;font-family:monospace;letter-spacing:3px;cursor:pointer;">
      LAUNCH ▶
    </button>
    <div id="lobby-status" style="margin-top:16px;font-size:11px;color:#64748b;text-align:center;min-height:20px;"></div>
  </div>
</div>
"""

txt = txt.replace('</body>', LOBBY_HTML + '\n</body>')
print("Lobby HTML injected")

# ─── 2. Inject multiplayer JS before the closing </script> tag
MULTI_JS = """
// ═══════════════════════════════════════════════════════════════════════════
// DRIFTBOUND MULTIPLAYER CLIENT
// ═══════════════════════════════════════════════════════════════════════════

let socket       = null;
let myPid        = null;
let myColor      = '#00ff88';
let remotePlayers = {};   // pid -> player state from server
let serverAsteroids = {}; // aid -> asteroid (authoritative from server)
let serverOres    = {};   // oid -> ore pickup
let multiMode     = false;
let serverTick    = 0;

// ─── LOBBY ────────────────────────────────────────────────────────────────
function lobbyConnect() {
  const name = (document.getElementById('lobby-name').value || 'Pilot').trim();
  const ip   = (document.getElementById('lobby-ip').value  || 'localhost').trim();
  const url  = `ws://${ip}:8766`;

  setLobbyStatus('Connecting to ' + url + '...');

  try {
    socket = new WebSocket(url);
  } catch(e) {
    setLobbyStatus('Invalid address.');
    return;
  }

  socket.onopen = () => {
    socket.send(JSON.stringify({ type: 'join', name }));
  };

  socket.onmessage = (ev) => {
    handleServerMsg(JSON.parse(ev.data));
  };

  socket.onerror = () => {
    setLobbyStatus('Could not connect — is the server running?');
    socket = null;
  };

  socket.onclose = () => {
    if (multiMode) showToast('Disconnected from server', '#ef4444');
    multiMode = false;
    socket = null;
  };
}

function setLobbyStatus(msg) {
  document.getElementById('lobby-status').textContent = msg;
}

// ─── SERVER MESSAGES ─────────────────────────────────────────────────────
function handleServerMsg(msg) {
  switch (msg.type) {

    case 'init':
      myPid    = msg.pid;
      myColor  = msg.color;
      multiMode = true;
      // Load server asteroids as authoritative
      serverAsteroids = {};
      for (const a of msg.asteroids) serverAsteroids[a.aid] = a;
      serverOres = {};
      for (const o of msg.ores) serverOres[o.oid] = o;
      // Load other players
      remotePlayers = {};
      for (const p of msg.players) {
        if (p.pid !== myPid) remotePlayers[p.pid] = p;
      }
      // Hide lobby
      document.getElementById('lobby').style.display = 'none';
      showToast('Connected as ' + msg.name + '  ' + msg.color, myColor);
      break;

    case 'state':
      serverTick++;
      // Update remote players
      remotePlayers = {};
      for (const p of msg.players) {
        if (p.pid !== myPid) remotePlayers[p.pid] = p;
      }
      // Sync asteroids from server
      serverAsteroids = {};
      for (const a of msg.asteroids) serverAsteroids[a.aid] = a;
      // Sync ore pickups
      serverOres = {};
      for (const o of msg.ores) serverOres[o.oid] = o;
      break;

    case 'player_joined':
      if (msg.player.pid !== myPid) {
        remotePlayers[msg.player.pid] = msg.player;
        showToast('⚡ ' + msg.player.name + ' entered the drift', '#38bdf8');
      }
      break;

    case 'player_left':
      delete remotePlayers[msg.pid];
      showToast('✦ ' + msg.name + ' disconnected', '#64748b');
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
      // Server is authoritative — update local cargo
      ship.ore          = msg.totals.ore;
      ship.mineral      = msg.totals.mineral;
      ship.armalcolite  = msg.totals.armalcolite;
      if (msg.loot === 'mineral') {
        showToast('✦ MINERAL MATERIAL found! (' + ship.mineral + ' held)', '#a78bfa');
      } else if (msg.loot === 'armalcolite') {
        showToast('◈ ARMALCOLITE extracted (' + ship.armalcolite + ' held)', '#34d399');
      }
      break;

    case 'ore_gone':
      delete serverOres[msg.oid];
      break;

    case 'refined':
      ship.fuel        = msg.fuel;
      ship.armalcolite = msg.armalcolite;
      showToast('REFINED ARMALCOLITE → +2.0 FUEL  (' + ship.fuel.toFixed(1) + ')', '#34d399');
      break;
  }
}

// ─── SEND PLAYER STATE ────────────────────────────────────────────────────
let _lastSend = 0;
function sendMove() {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  const now = performance.now();
  if (now - _lastSend < 50) return;   // max 20 sends/sec
  _lastSend = now;
  socket.send(JSON.stringify({
    type:        'move',
    worldX:      ship.worldX,
    worldY:      ship.worldY,
    vx:          ship.vx,
    vy:          ship.vy,
    dir:         ship.dir,
    speed:       Math.hypot(ship.vx, ship.vy),
    animFrame:   ship.animFrame,
    hp:          ship.hp,
    fuel:        ship.fuel,
    ore:         ship.ore,
    mineral:     ship.mineral,
    armalcolite: ship.armalcolite,
    thrusting:   _thrusting,
    boosting:    _boosting,
  }));
}

let _thrusting = false;
let _boosting  = false;

// ─── SEND MINE ACTION ─────────────────────────────────────────────────────
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

// ─── DRAW REMOTE PLAYERS ─────────────────────────────────────────────────
function drawRemotePlayers(cx, cy) {
  if (!multiMode) return;
  for (const p of Object.values(remotePlayers)) {
    const sx = cx + (p.worldX - ship.worldX);
    const sy = cy + (p.worldY - ship.worldY);

    // Only draw if on screen (with margin)
    const margin = 120;
    if (sx < -margin || sx > canvas.width + margin ||
        sy < -margin || sy > canvas.height + margin) {
      // Draw off-screen arrow indicator
      drawPlayerIndicator(p, cx, cy, sx, sy);
      continue;
    }

    // Ship body — colored diamond
    ctx.save();
    ctx.translate(sx, sy);

    // Glow
    ctx.shadowColor = p.color;
    ctx.shadowBlur  = 12;

    // Ship shape
    ctx.beginPath();
    ctx.moveTo(0, -18);
    ctx.lineTo(10, 8);
    ctx.lineTo(0, 4);
    ctx.lineTo(-10, 8);
    ctx.closePath();
    ctx.fillStyle = p.color + 'cc';
    ctx.fill();
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Thruster glow when boosting
    if (p.boosting || p.thrusting) {
      ctx.beginPath();
      ctx.moveTo(-5, 6);
      ctx.lineTo(0, 14 + Math.random()*4);
      ctx.lineTo(5, 6);
      ctx.fillStyle = p.color + '88';
      ctx.fill();
    }

    ctx.shadowBlur = 0;
    ctx.restore();

    // Name tag
    ctx.save();
    ctx.font = '10px monospace';
    ctx.fillStyle = p.color;
    ctx.textAlign = 'center';
    ctx.fillText(p.name, sx, sy - 26);

    // HP bar
    const barW = 36;
    const hpPct = Math.max(0, p.hp / 100);
    ctx.fillStyle = '#0d1520';
    ctx.fillRect(sx - barW/2 - 1, sy - 22, barW + 2, 4);
    ctx.fillStyle = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#f59e0b' : '#ef4444';
    ctx.fillRect(sx - barW/2, sy - 21, barW * hpPct, 2);
    ctx.restore();
  }
}

function drawPlayerIndicator(p, cx, cy, sx, sy) {
  // Edge arrow pointing toward remote player
  const angle = Math.atan2(sy - cy, sx - cx);
  const edgeX = cx + Math.cos(angle) * (Math.min(canvas.width, canvas.height) / 2 - 40);
  const edgeY = cy + Math.sin(angle) * (Math.min(canvas.width, canvas.height) / 2 - 40);
  const dist  = Math.round(Math.hypot(sx - cx, sy - cy) / 10) / 10;

  ctx.save();
  ctx.translate(edgeX, edgeY);
  ctx.rotate(angle + Math.PI / 2);
  ctx.beginPath();
  ctx.moveTo(0, -8);
  ctx.lineTo(6, 4);
  ctx.lineTo(-6, 4);
  ctx.closePath();
  ctx.fillStyle = p.color + 'cc';
  ctx.fill();
  ctx.restore();

  ctx.save();
  ctx.font = '9px monospace';
  ctx.fillStyle = p.color + 'aa';
  ctx.textAlign = 'center';
  ctx.fillText(p.name + ' ' + dist + 'km', edgeX, edgeY + 20);
  ctx.restore();
}
"""

# Inject before </script>
txt = txt.replace('</script>\n\n</body>', MULTI_JS + '\n</script>\n\n</body>')
print("Multiplayer JS injected")

# ─── 3. Patch main loop to draw remote players
old_draw_ore = "  drawOrePickups(cx, cy);"
new_draw_ore = """  drawOrePickups(cx, cy);
  drawRemotePlayers(cx, cy);"""
txt = txt.replace(old_draw_ore, new_draw_ore)
print("drawRemotePlayers added to loop")

# ─── 4. Patch update() to set _thrusting/_boosting flags + sendMove
old_update_end = "  return speed;\n}"
new_update_end = """  // Multiplayer: flag thrust state + broadcast
  _thrusting = thrusting;
  _boosting  = boosting;
  if (multiMode) sendMove();

  return speed;
}"""
txt = txt.replace(old_update_end, new_update_end)
print("sendMove hooked into update()")

# ─── 5. Use server asteroids when in multiMode — patch drawAsteroids/collision
# Replace the asteroids array reference in the draw + collision with a helper
# We'll add a getter at the top of script
old_const_ast = "const ASTEROID_POOL = [2, 0,0,0,0, 1,1,1, 2,2];  // index into ASTEROID_TYPES"
new_const_ast = """const ASTEROID_POOL = [2, 0,0,0,0, 1,1,1, 2,2];  // index into ASTEROID_TYPES

// In multiMode, server owns asteroid state — use this getter everywhere
function getAsteroids() {
  return multiMode ? Object.values(serverAsteroids) : asteroids;
}
function getOrePickups() {
  return multiMode ? Object.values(serverOres) : orePickups;
}"""
txt = txt.replace(old_const_ast, new_const_ast)
print("getAsteroids/getOrePickups helpers added")

# ─── 6. Patch drawAsteroids to use getAsteroids()
txt = txt.replace(
    'function drawAsteroids(cx, cy) {\n\n  for (const a of asteroids) {',
    'function drawAsteroids(cx, cy) {\n\n  for (const a of getAsteroids()) {'
)
txt = txt.replace(
    'function drawAsteroids(cx, cy) {\n  for (const a of asteroids) {',
    'function drawAsteroids(cx, cy) {\n  for (const a of getAsteroids()) {'
)
print("drawAsteroids patched")

# ─── 7. Patch drawOrePickups to use getOrePickups()
txt = txt.replace(
    'for (const o of orePickups) {',
    'for (const o of getOrePickups()) {'
)
print("drawOrePickups patched")

# ─── 8. Patch C key refine to also send to server
old_refine_send = "if (ship.armalcolite > 0) {"
new_refine_send = """if (ship.armalcolite > 0) {
    if (multiMode) { sendRefine(); craftCooldown = 30; }
    else if (true) {"""
# Only patch the C-key handler (first occurrence)
idx = txt.find("if (keys['KeyC'] && craftCooldown <= 0)")
if idx >= 0:
    block_start = txt.find('if (ship.armalcolite > 0)', idx)
    if block_start >= 0 and block_start < idx + 500:
        # Close the extra else if with matching brace at end of refine block
        txt = txt[:block_start] + new_refine_send + txt[block_start + len('if (ship.armalcolite > 0) {'):]
        print("Refine sends to server in multiMode")

# ─── 9. Add player count to HUD
old_hud_fps = "fpsDisplay + ' FPS'"
new_hud_fps  = "fpsDisplay + ' FPS' + (multiMode ? '  |  ' + (Object.keys(remotePlayers).length + 1) + ' PILOTS' : '')"
txt = txt.replace(old_hud_fps, new_hud_fps)
print("Player count in HUD")

# ─── 10. Singleplayer still works when lobby is bypassed (press ESC)
old_boot = "boot();"
new_boot  = """// Press ESC in lobby to play solo
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    const lobby = document.getElementById('lobby');
    if (lobby && lobby.style.display !== 'none') {
      lobby.style.display = 'none';
      showToast('Solo mode — no server connected', '#64748b');
    }
  }
});

boot();"""
txt = txt.replace(old_boot, new_boot)
print("ESC solo bypass added")

open('driftbound_flight_test.html', 'w', encoding='utf-8').write(txt)
print("\n=== MULTIPLAYER PATCH COMPLETE ===")
print("Lobby: shows on load, ESC to play solo")
print("Server: ws://localhost:8766")
print("HTTP:   http://localhost:8765/driftbound_flight_test.html")
