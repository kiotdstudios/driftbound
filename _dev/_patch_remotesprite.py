with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

old = "    ctx.save();\r\n    ctx.translate(sx, sy);\r\n    ctx.shadowColor = p.color; ctx.shadowBlur = 14;\r\n    ctx.beginPath();\r\n    ctx.moveTo(0, -18); ctx.lineTo(11, 8); ctx.lineTo(0, 4); ctx.lineTo(-11, 8);\r\n    ctx.closePath();\r\n    ctx.fillStyle = p.color + 'cc'; ctx.fill();\r\n    ctx.strokeStyle = p.color; ctx.lineWidth = 1.5; ctx.stroke();\r\n    if (p.boosting || p.thrusting) {\r\n      ctx.beginPath(); ctx.moveTo(-5,6); ctx.lineTo(0, 14+Math.random()*4); ctx.lineTo(5,6);\r\n      ctx.fillStyle = p.color + '88'; ctx.fill();\r\n    }\r\n    ctx.shadowBlur = 0; ctx.restore();"

new = """    ctx.save();
    ctx.translate(sx, sy);
    const pDir = p.dir || 'south';
    const pMoving = (p.thrusting || p.boosting);
    const pFrame = (p.animFrame || 0) % FRAME_COUNT;
    const pImg = pMoving
      ? (animations[pDir] && animations[pDir][pFrame])
      : rotations[pDir];
    if (pImg) {
      ctx.shadowColor = p.color; ctx.shadowBlur = 10;
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(pImg, Math.round(-DISPLAY_SIZE/2), Math.round(-DISPLAY_SIZE/2), DISPLAY_SIZE, DISPLAY_SIZE);
      ctx.shadowBlur = 0;
    } else {
      ctx.shadowColor = p.color; ctx.shadowBlur = 14;
      ctx.beginPath();
      ctx.moveTo(0, -18); ctx.lineTo(11, 8); ctx.lineTo(0, 4); ctx.lineTo(-11, 8);
      ctx.closePath();
      ctx.fillStyle = p.color + 'cc'; ctx.fill();
      ctx.strokeStyle = p.color; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.shadowBlur = 0;
    }
    ctx.restore();"""

if old in d:
    d = d.replace(old, new)
    print('patched exact')
else:
    print('STILL NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('pImg present:', 'pImg' in d)
