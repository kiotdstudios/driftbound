with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. HUD FONTS 2x (CRLF)
# ══════════════════════════════════════════════════════════════════
old = "const HUD_FONT    = '13px Courier New';\r\nconst HUD_FONT_SM = '11px Courier New';"
new = "const HUD_FONT    = '26px Courier New';\r\nconst HUD_FONT_SM = '22px Courier New';"
if old in d:
    d = d.replace(old, new); fixes.append('HUD fonts 2x')
else:
    fixes.append('HUD fonts: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. SHIP DESTRUCTION + RESPAWN
# ══════════════════════════════════════════════════════════════════
old = ("  if (ship.hp <= 0 && Math.floor(Date.now()/400)%2===0) {\r\n"
       "    ctx.fillStyle = '#ff2222'; ctx.font = 'bold 28px Courier New'; ctx.textAlign = 'center';\r\n"
       "    ctx.fillText('\\u2715 HULL BREACH \\u2014 CRITICAL', canvas.width/2, canvas.height/2 - 20);\r\n"
       "    ctx.textAlign = 'left';\r\n"
       "  }")
new = ("  if (ship.hp <= 0) {\r\n"
       "    if (!ship.destroyed) {\r\n"
       "      ship.destroyed = true; ship.destroyedAt = Date.now();\r\n"
       "      for (let i = 0; i < 60; i++) {\r\n"
       "        const ang = Math.random()*Math.PI*2, spd = 1+Math.random()*5;\r\n"
       "        particles.push({x:canvas.width/2,y:canvas.height/2,\r\n"
       "          vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,\r\n"
       "          life:80+Math.random()*60,maxLife:140,\r\n"
       "          color:['#ff4444','#ff8800','#ffcc00','#ffffff'][Math.floor(Math.random()*4)],\r\n"
       "          size:2+Math.random()*4});\r\n"
       "      }\r\n"
       "    }\r\n"
       "    const elapsed = Date.now() - (ship.destroyedAt||Date.now());\r\n"
       "    const remaining = Math.ceil((4000-elapsed)/1000);\r\n"
       "    ctx.fillStyle='#000000bb'; ctx.fillRect(0,0,canvas.width,canvas.height);\r\n"
       "    ctx.textAlign='center';\r\n"
       "    ctx.font='bold 32px Courier New'; ctx.fillStyle='#ff2222';\r\n"
       "    ctx.fillText('\\u2715  SHIP DESTROYED',canvas.width/2,canvas.height/2-30);\r\n"
       "    ctx.font='20px Courier New'; ctx.fillStyle='#ff8800';\r\n"
       "    ctx.fillText('RESPAWNING IN '+Math.max(0,remaining)+'...',canvas.width/2,canvas.height/2+14);\r\n"
       "    ctx.textAlign='left';\r\n"
       "    if (elapsed>=4000) {\r\n"
       "      ship.hp=SHIP_MAX_HP; ship.worldX=(Math.random()-0.5)*300; ship.worldY=(Math.random()-0.5)*300;\r\n"
       "      ship.vx=0; ship.vy=0; ship.destroyed=false; showToast('RESPAWNED','#22c55e');\r\n"
       "    }\r\n"
       "  }")
if old in d:
    d = d.replace(old, new); fixes.append('ship destruction+respawn')
else:
    # Try without the exact newline after "- 20"
    import re
    m = re.search(r"if \(ship\.hp <= 0 && Math\.floor\(Date\.now\(\)/400\)%2===0\) \{.*?ctx\.textAlign = 'left';\r\n  \}", d, re.DOTALL)
    if m:
        d = d[:m.start()] + new + d[m.end():]
        fixes.append('ship destruction+respawn (regex)')
    else:
        fixes.append('ship destruction: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 3. REMOTE HP BAR — bigger, close-range detail
# ══════════════════════════════════════════════════════════════════
old = ("    ctx.save();\r\n"
       "    ctx.font = '10px monospace'; ctx.fillStyle = p.color; ctx.textAlign = 'center';\r\n"
       "    ctx.fillText(p.name, sx, sy - 26);\r\n"
       "    const barW = 36, hpPct = Math.max(0, p.hp / 100);\r\n"
       "    ctx.fillStyle = '#0d1520';\r\n"
       "    ctx.fillRect(sx - barW/2 - 1, sy - 22, barW + 2, 4);\r\n"
       "    ctx.fillStyle = hpPct > 0.5 ? '#22c55e' : hpPct > 0.25 ? '#f59e0b' : '#ef4444';\r\n"
       "    ctx.fillRect(sx - barW/2, sy - 21, barW * hpPct, 2);\r\n"
       "    ctx.restore();")
new = ("    const worldDist = Math.hypot(p.worldX-ship.worldX, p.worldY-ship.worldY);\r\n"
       "    const _hpPct = Math.max(0,(p.hp||100)/100);\r\n"
       "    const _hpCol = _hpPct>0.5?'#22c55e':_hpPct>0.25?'#f59e0b':'#ef4444';\r\n"
       "    ctx.save();\r\n"
       "    ctx.textAlign='center';\r\n"
       "    ctx.font='13px monospace'; ctx.fillStyle=p.color;\r\n"
       "    ctx.fillText(p.name, sx, sy-32);\r\n"
       "    if (worldDist < 600) {\r\n"
       "      const bW=80,bH=8,bx=sx-40,by=sy-26;\r\n"
       "      ctx.fillStyle='#000000cc'; ctx.fillRect(bx-2,by-2,bW+4,bH+4);\r\n"
       "      ctx.fillStyle='#0d1520';   ctx.fillRect(bx,by,bW,bH);\r\n"
       "      ctx.fillStyle=_hpCol;      ctx.fillRect(bx,by,bW*_hpPct,bH);\r\n"
       "      ctx.strokeStyle=_hpCol+'88'; ctx.lineWidth=1; ctx.strokeRect(bx,by,bW,bH);\r\n"
       "      ctx.font='10px Courier New'; ctx.fillStyle=_hpCol;\r\n"
       "      ctx.fillText(Math.round(p.hp||100)+'/100', sx, by+bH+13);\r\n"
       "    } else {\r\n"
       "      const bW=36;\r\n"
       "      ctx.fillStyle='#0d1520';  ctx.fillRect(sx-bW/2-1,sy-22,bW+2,4);\r\n"
       "      ctx.fillStyle=_hpCol;     ctx.fillRect(sx-bW/2,sy-21,bW*_hpPct,2);\r\n"
       "    }\r\n"
       "    ctx.restore();")
if old in d:
    d = d.replace(old, new); fixes.append('remote HP bar enhanced')
else:
    fixes.append('remote HP bar: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 4. BEAM COORDS IN MOVE PAYLOAD
# ══════════════════════════════════════════════════════════════════
old = "worldX: ship.worldX, worldY: ship.worldY,\r\n    vx: ship.vx, vy: ship.vy, dir: ship.dir,"
new = ("worldX: ship.worldX, worldY: ship.worldY,\r\n"
       "    vx: ship.vx, vy: ship.vy, dir: ship.dir,\r\n"
       "    laserWx: ship.laserWx||null, laserWy: ship.laserWy||null, laserTimer: ship.laserTimer||0,")
if old in d:
    d = d.replace(old, new); fixes.append('beam coords in move payload')
else:
    fixes.append('beam coords: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 5. PLAYER_MOVE CASE — store beam state
# ══════════════════════════════════════════════════════════════════
old = ("    case 'player_move':\r\n"
       "      if (msg.pid !== myPid) remotePlayers[msg.pid] = msg.player;\r\n"
       "      break;")
new = ("    case 'player_move':\r\n"
       "      if (msg.pid !== myPid) {\r\n"
       "        remotePlayers[msg.pid] = msg.player;\r\n"
       "      } break;")
if old in d:
    d = d.replace(old, new); fixes.append('player_move case')
else:
    fixes.append('player_move case: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 6. REMOTE BEAM DRAW — inject into drawRemotePlayers before closing brace
# ══════════════════════════════════════════════════════════════════
old = ("    ctx.restore();\r\n"
       "  }\r\n"
       "}\r\n"
       "\r\n"
       "function drawPlayerIndicator")
new = ("    ctx.restore();\r\n"
       "\r\n"
       "    // Remote player mining beam\r\n"
       "    if (p.laserTimer > 0 && p.laserWx != null) {\r\n"
       "      const btx = cx+(p.laserWx-ship.worldX), bty = cy+(p.laserWy-ship.worldY);\r\n"
       "      const ba  = Math.min(1, p.laserTimer/10)*0.7;\r\n"
       "      ctx.save();\r\n"
       "      ctx.globalAlpha=ba; ctx.strokeStyle=p.color; ctx.lineWidth=1.5;\r\n"
       "      ctx.setLineDash([4,4]);\r\n"
       "      ctx.beginPath(); ctx.moveTo(sx,sy); ctx.lineTo(btx,bty); ctx.stroke();\r\n"
       "      ctx.setLineDash([]);\r\n"
       "      ctx.shadowColor=p.color; ctx.shadowBlur=12;\r\n"
       "      ctx.beginPath(); ctx.arc(btx,bty,5,0,Math.PI*2);\r\n"
       "      ctx.fillStyle=p.color; ctx.fill();\r\n"
       "      ctx.shadowBlur=0; ctx.restore();\r\n"
       "    }\r\n"
       "  }\r\n"
       "}\r\n"
       "\r\n"
       "function drawPlayerIndicator")
if old in d:
    d = d.replace(old, new); fixes.append('remote beam draw')
else:
    fixes.append('remote beam draw: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 7. ORE PICKUPS — bigger, color-coded by loot type
# ══════════════════════════════════════════════════════════════════
old_ore_font = "  ctx.font   = '9px Courier New';\r\n"
new_ore_font = "  ctx.font   = '13px Courier New';\r\n"
if old_ore_font in d:
    d = d.replace(old_ore_font, new_ore_font); fixes.append('ore font 13px')

old = ("    const r     = 3 + pulse * 2.5;\r\n"
       "\r\n"
       "    // Glow ring\r\n"
       "\r\n"
       "    ctx.globalAlpha = 0.25 * pulse;\r\n"
       "\r\n"
       "    ctx.strokeStyle = '#FFD700';\r\n"
       "\r\n"
       "    ctx.lineWidth   = 1;\r\n"
       "\r\n"
       "    ctx.beginPath(); ctx.arc(sx, sy, r + 4, 0, Math.PI * 2); ctx.stroke();\r\n"
       "\r\n"
       "    // Core dot\r\n"
       "\r\n"
       "    ctx.globalAlpha = 0.7 + 0.3 * pulse;\r\n"
       "\r\n"
       "    ctx.fillStyle   = '#FFD700';\r\n"
       "\r\n"
       "    ctx.beginPath(); ctx.arc(sx, sy, r, 0, Math.PI * 2); ctx.fill();\r\n"
       "\r\n"
       "    // Label\r\n"
       "\r\n"
       "    ctx.globalAlpha = 0.8;\r\n"
       "\r\n"
       "    ctx.fillStyle   = '#FFD700';\r\n"
       "\r\n"
       "    ctx.fillText(ore.amount + ' ORE', sx + r + 4, sy + 4);\r\n"
       "\r\n"
       "    ctx.globalAlpha = 1;")
new = ("    const r = 6 + pulse * 4;\r\n"
       "    const lootCol = ore.lootType==='armalcolite'?'#38bdf8':ore.lootType==='mineral'?'#a78bfa':'#FFD700';\r\n"
       "    const lootLbl = ore.lootType==='armalcolite'?(ore.amount+' ARMALCOLITE')\r\n"
       "                  : ore.lootType==='mineral'?    (ore.amount+' MINERAL MAT')\r\n"
       "                  :                              (ore.amount+' NEBULITE');\r\n"
       "    // Outer glow\r\n"
       "    ctx.globalAlpha=0.35*pulse; ctx.strokeStyle=lootCol; ctx.lineWidth=2;\r\n"
       "    ctx.beginPath(); ctx.arc(sx,sy,r+8,0,Math.PI*2); ctx.stroke();\r\n"
       "    // Inner ring\r\n"
       "    ctx.globalAlpha=0.55*pulse; ctx.lineWidth=1.5;\r\n"
       "    ctx.beginPath(); ctx.arc(sx,sy,r+3,0,Math.PI*2); ctx.stroke();\r\n"
       "    // Core\r\n"
       "    ctx.globalAlpha=0.85+0.15*pulse;\r\n"
       "    ctx.fillStyle=lootCol; ctx.shadowColor=lootCol; ctx.shadowBlur=14;\r\n"
       "    ctx.beginPath(); ctx.arc(sx,sy,r,0,Math.PI*2); ctx.fill();\r\n"
       "    ctx.shadowBlur=0;\r\n"
       "    // Label\r\n"
       "    ctx.globalAlpha=1; ctx.fillStyle=lootCol;\r\n"
       "    ctx.fillText(lootLbl, sx+r+6, sy+5);\r\n"
       "    ctx.globalAlpha=1;")
if old in d:
    d = d.replace(old, new); fixes.append('ore pickup visuals enhanced')
else:
    fixes.append('ore pickup: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
