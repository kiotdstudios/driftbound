with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. HUD FONT — bump from 11px/13px to 22px/26px (2x)
# ══════════════════════════════════════════════════════════════════
old = ("const HUD_FONT    = '13px Courier New';\n"
       "const HUD_FONT_SM = '11px Courier New';")
new = ("const HUD_FONT    = '26px Courier New';\n"
       "const HUD_FONT_SM = '22px Courier New';")
if old in d:
    d = d.replace(old, new); fixes.append('HUD fonts 2x')
else:
    fixes.append('HUD fonts: NO MATCH')

# Also bump the bold header inside CARGO section
old2 = "ctx.font = 'bold 9px Courier New'; ctx.fillStyle = '#4FC3C3';"
new2 = "ctx.font = 'bold 18px Courier New'; ctx.fillStyle = '#4FC3C3';"
if old2 in d:
    d = d.replace(old2, new2); fixes.append('CARGO header font 2x')

old3 = "ctx.font = 'bold 12px monospace';"
new3 = "ctx.font = 'bold 24px monospace';"
if old3 in d:
    d = d.replace(old3, new3); fixes.append('mineral icon font 2x')

# Toast font
old4 = "ctx.font        = '11px Courier New';"
new4 = "ctx.font        = '22px Courier New';"
if old4 in d:
    d = d.replace(old4, new4); fixes.append('toast font 2x')

# Hull breach label
old5 = "ctx.font = 'bold 14px Courier New';"
new5 = "ctx.font = 'bold 28px Courier New';"
if old5 in d:
    d = d.replace(old5, new5); fixes.append('hull breach font 2x')

# ══════════════════════════════════════════════════════════════════
# 2. HUD PANEL WIDTH — double PW so layout doesn't cramp
# ══════════════════════════════════════════════════════════════════
old = "  const PW    = 245;"
new = "  const PW    = 490;"
if old in d:
    d = d.replace(old, new); fixes.append('HUD panel width 2x')

# Double LH (line height) and bar thicknesses
old = "  const LH    = 17;"
new = "  const LH    = 34;"
if old in d:
    d = d.replace(old, new); fixes.append('HUD LH 2x')

# Thrust/hull bar heights (bh / hbh)
old = "  const bx = LEFT, by = thrustY, bw = PW - 34, bh = 5;"
new = "  const bx = LEFT, by = thrustY, bw = PW - 68, bh = 10;"
if old in d:
    d = d.replace(old, new); fixes.append('thrust bar height 2x')

old = "  const hbx = LEFT, hby = hullY, hbw = PW - 34, hbh = 5;"
new = "  const hbx = LEFT, hby = hullY, hbw = PW - 68, hbh = 10;"
if old in d:
    d = d.replace(old, new); fixes.append('hull bar height 2x')

# Fuel segments
old = "  const segCount = 10, segW = Math.floor((PW - 36) / 10) - 1, segH = 12, segGap = 2;"
new = "  const segCount = 10, segW = Math.floor((PW - 68) / 10) - 2, segH = 24, segGap = 3;"
if old in d:
    d = d.replace(old, new); fixes.append('fuel seg 2x')

# Cargo bar width
old = "  const cUsed = cargoUsed(), cMax = CARGO_LIMIT, cbw = PW - 36;"
new = "  const cUsed = cargoUsed(), cMax = CARGO_LIMIT, cbw = PW - 68;"
if old in d:
    d = d.replace(old, new); fixes.append('cargo bar width')

# ══════════════════════════════════════════════════════════════════
# 3. REMOTE PLAYER HEALTH BAR — bigger and only when close (< 600px)
# ══════════════════════════════════════════════════════════════════
old = """    ctx.save();
    ctx.font = '10px monospace'; ctx.fillStyle = p.color; ctx.textAlign = 'center';
    ctx.fillText(p.name, sx, sy - 26);
    const barW = 36, hpPct = Math.max(0, p.hp / 100);
    ctx.fillStyle = '#0d1520';
    ctx.fillRect(sx - barW/2 - 1, sy - 22, barW + 2, 4);
    ctx.fillStyle = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#f59e0b' : '#ef4444';
    ctx.fillRect(sx - barW/2, sy - 21, barW * hpPct, 2);
    ctx.restore();"""
new = """    const worldDist = Math.hypot(p.worldX - ship.worldX, p.worldY - ship.worldY);
    const hpPct = Math.max(0, (p.hp || 100) / 100);
    const hpColor = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#f59e0b' : '#ef4444';
    ctx.save();
    ctx.textAlign = 'center';
    // Name tag — always visible
    ctx.font = '13px monospace'; ctx.fillStyle = p.color;
    ctx.fillText(p.name, sx, sy - 30);
    if (worldDist < 600) {
      // Big health bar when close
      const barW = 80, barH = 8;
      const bx = sx - barW / 2, by = sy - 24;
      ctx.fillStyle = '#000000cc';
      ctx.fillRect(bx - 2, by - 2, barW + 4, barH + 4);
      ctx.fillStyle = '#0d1520';
      ctx.fillRect(bx, by, barW, barH);
      ctx.fillStyle = hpColor;
      ctx.fillRect(bx, by, barW * hpPct, barH);
      ctx.strokeStyle = hpColor + '88';
      ctx.lineWidth = 1;
      ctx.strokeRect(bx, by, barW, barH);
      // HP number
      ctx.font = '10px Courier New'; ctx.fillStyle = hpColor;
      ctx.fillText(Math.round((p.hp || 100)) + '/100', sx, by + barH + 13);
    } else {
      // Small dot bar when far
      const barW = 36;
      ctx.fillStyle = '#0d1520';
      ctx.fillRect(sx - barW/2 - 1, sy - 22, barW + 2, 4);
      ctx.fillStyle = hpColor;
      ctx.fillRect(sx - barW/2, sy - 21, barW * hpPct, 2);
    }
    ctx.restore();"""
if old in d:
    d = d.replace(old, new); fixes.append('remote HP bar enhanced')
else:
    fixes.append('remote HP bar: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 4. SHIP DESTRUCTION at hp <= 0
# ══════════════════════════════════════════════════════════════════
# Replace the blinking text with a full explosion + freeze
old = """  if (ship.hp <= 0 && Math.floor(Date.now()/400)%2===0) {
    ctx.fillStyle = '#ff2222'; ctx.font = 'bold 14px Courier New'; ctx.textAlign = 'center';
    ctx.fillText('\u2715 HULL BREACH \u2014 CRITICAL', canvas.width/2, canvas.height/2 - 20);
    ctx.textAlign = 'left';
  }"""
new = """  if (ship.hp <= 0) {
    // Mark destroyed (once)
    if (!ship.destroyed) {
      ship.destroyed = true;
      ship.destroyedAt = Date.now();
      // Big explosion burst
      for (let i = 0; i < 60; i++) {
        const ang = Math.random() * Math.PI * 2;
        const spd = 1 + Math.random() * 5;
        particles.push({ x: canvas.width/2, y: canvas.height/2,
          vx: Math.cos(ang)*spd, vy: Math.sin(ang)*spd,
          life: 80 + Math.random()*60, maxLife: 140,
          color: ['#ff4444','#ff8800','#ffcc00','#ffffff'][Math.floor(Math.random()*4)],
          size: 2 + Math.random()*4 });
      }
    }
    // Respawn after 4 seconds
    const elapsed = Date.now() - (ship.destroyedAt || Date.now());
    const remaining = Math.ceil((4000 - elapsed) / 1000);
    // Full-screen dark overlay
    ctx.fillStyle = '#000000bb';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.textAlign = 'center';
    ctx.font = 'bold 32px Courier New'; ctx.fillStyle = '#ff2222';
    ctx.fillText('\u2715  SHIP DESTROYED', canvas.width/2, canvas.height/2 - 30);
    ctx.font = '20px Courier New'; ctx.fillStyle = '#ff8800';
    ctx.fillText('RESPAWNING IN ' + Math.max(0, remaining) + '...', canvas.width/2, canvas.height/2 + 14);
    ctx.textAlign = 'left';
    if (elapsed >= 4000) {
      // Respawn
      ship.hp        = SHIP_MAX_HP;
      ship.worldX    = (Math.random() - 0.5) * 300;
      ship.worldY    = (Math.random() - 0.5) * 300;
      ship.vx        = 0; ship.vy = 0;
      ship.destroyed = false;
      showToast('RESPAWNED', '#22c55e');
    }
  }"""
if old in d:
    d = d.replace(old, new); fixes.append('ship destruction + respawn')
else:
    fixes.append('ship destruction: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 5. MINING LASER — make it visible to remote players
#    Send beam target coords in the move payload,
#    draw remote player beams in drawRemotePlayers
# ══════════════════════════════════════════════════════════════════
# Add laserWx/laserWy to move payload
old_move = ("          worldX: ship.worldX, worldY: ship.worldY,\r\n"
            "          vx: ship.vx, vy: ship.vy,")
new_move  = ("          worldX: ship.worldX, worldY: ship.worldY,\r\n"
             "          vx: ship.vx, vy: ship.vy,\r\n"
             "          laserWx: ship.laserWx, laserWy: ship.laserWy, laserTimer: ship.laserTimer,")
if old_move in d:
    d = d.replace(old_move, new_move); fixes.append('beam coords in move payload (CRLF)')
else:
    old_move2 = ("          worldX: ship.worldX, worldY: ship.worldY,\n"
                 "          vx: ship.vx, vy: ship.vy,")
    new_move2  = ("          worldX: ship.worldX, worldY: ship.worldY,\n"
                  "          vx: ship.vx, vy: ship.vy,\n"
                  "          laserWx: ship.laserWx, laserWy: ship.laserWy, laserTimer: ship.laserTimer,")
    if old_move2 in d:
        d = d.replace(old_move2, new_move2); fixes.append('beam coords in move payload (LF)')
    else:
        fixes.append('beam coords move payload: NO MATCH')

# Store laser state on remote player
old_move_case = ("            case 'player_move': if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player; break;")
new_move_case  = ("            case 'player_move':\r\n"
                  "              if (msg.pid !== myPid) {\r\n"
                  "                remotePlayers[msg.pid] = msg.player;\r\n"
                  "                // preserve beam state from payload\r\n"
                  "                if (msg.player.laserTimer > 0) {\r\n"
                  "                  remotePlayers[msg.pid].laserWx = msg.player.laserWx;\r\n"
                  "                  remotePlayers[msg.pid].laserWy = msg.player.laserWy;\r\n"
                  "                  remotePlayers[msg.pid].laserTimer = msg.player.laserTimer;\r\n"
                  "                }\r\n"
                  "              } break;")
if old_move_case in d:
    d = d.replace(old_move_case, new_move_case); fixes.append('beam state on remote player')
else:
    old_mc2 = ("            case 'player_move': if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player; break;")
    if old_mc2 in d:
        d = d.replace(old_mc2, new_move_case); fixes.append('beam state on remote player (alt)')
    else:
        fixes.append('beam state case: NO MATCH — trying loose search')
        import re
        m = re.search(r"case 'player_move'.*?break;", d, re.DOTALL)
        if m:
            print(f'  found at {m.start()}: {repr(d[m.start():m.start()+120])}')

# Draw remote player beams in drawRemotePlayers
old_rp_end = """    ctx.restore();
  }
}

function drawPlayerIndicator"""
new_rp_end = """    ctx.restore();

    // Draw remote player mining beam
    if (p.laserTimer > 0 && p.laserWx != null) {
      const tx = cx + (p.laserWx - ship.worldX);
      const ty = cy + (p.laserWy - ship.worldY);
      const alpha = Math.min(1, p.laserTimer / 10) * 0.7;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = p.color;
      ctx.lineWidth   = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(tx, ty); ctx.stroke();
      ctx.setLineDash([]);
      // Glow at target
      ctx.shadowColor = p.color; ctx.shadowBlur = 12;
      ctx.beginPath(); ctx.arc(tx, ty, 5, 0, Math.PI*2); ctx.fillStyle = p.color; ctx.fill();
      ctx.shadowBlur = 0;
      ctx.restore();
    }
  }
}

function drawPlayerIndicator"""
if old_rp_end in d:
    d = d.replace(old_rp_end, new_rp_end); fixes.append('remote beam draw')
else:
    fixes.append('remote beam draw: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 6. ORE PICKUPS — make them visible to ALL players (server-owned)
#    drawOrePickups already iterates getOrePickups() which routes to
#    serverOres in multiMode — but let's verify the label and make
#    them bigger / more visible
# ══════════════════════════════════════════════════════════════════
old_ore = """    const r     = 3 + pulse * 2.5;

    // Glow ring

    ctx.globalAlpha = 0.25 * pulse;

    ctx.strokeStyle = '#FFD700';

    ctx.lineWidth   = 1;

    ctx.beginPath(); ctx.arc(sx, sy, r + 4, 0, Math.PI * 2); ctx.stroke();

    // Core dot

    ctx.globalAlpha = 0.7 + 0.3 * pulse;

    ctx.fillStyle   = '#FFD700';

    ctx.beginPath(); ctx.arc(sx, sy, r, 0, Math.PI * 2); ctx.fill();

    // Label

    ctx.globalAlpha = 0.8;

    ctx.fillStyle   = '#FFD700';

    ctx.fillText(ore.amount + ' ORE', sx + r + 4, sy + 4);

    ctx.globalAlpha = 1;"""
new_ore = """    const r     = 6 + pulse * 4;  // bigger

    // Outer glow
    ctx.globalAlpha = 0.35 * pulse;
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth   = 2;
    ctx.beginPath(); ctx.arc(sx, sy, r + 8, 0, Math.PI * 2); ctx.stroke();

    // Glow ring
    ctx.globalAlpha = 0.5 * pulse;
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth   = 1.5;
    ctx.beginPath(); ctx.arc(sx, sy, r + 3, 0, Math.PI * 2); ctx.stroke();

    // Core dot
    ctx.globalAlpha = 0.85 + 0.15 * pulse;
    const lootColor = ore.lootType === 'armalcolite' ? '#38bdf8'
                    : ore.lootType === 'mineral'      ? '#a78bfa'
                    : '#FFD700';
    ctx.fillStyle   = lootColor;
    ctx.shadowColor = lootColor; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.arc(sx, sy, r, 0, Math.PI * 2); ctx.fill();
    ctx.shadowBlur  = 0;

    // Label — bigger font
    ctx.globalAlpha = 1;
    ctx.font        = '13px Courier New';
    ctx.fillStyle   = lootColor;
    const lootLabel = ore.lootType === 'armalcolite' ? ore.amount + ' ARMALCOLITE'
                    : ore.lootType === 'mineral'      ? ore.amount + ' MINERAL MAT'
                    : ore.amount + ' NEBULITE';
    ctx.fillText(lootLabel, sx + r + 6, sy + 5);
    ctx.globalAlpha = 1;"""
if old_ore in d:
    d = d.replace(old_ore, new_ore); fixes.append('ore pickup visuals enhanced')
else:
    fixes.append('ore pickup: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
