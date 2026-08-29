import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

# drawAsteroids uses raw `asteroids` — swap to getAsteroids()
old = 'for (const ast of asteroids) {'
new = 'for (const ast of getAsteroids()) {'
count = d.count(old)
d = d.replace(old, new)
print(f'drawAsteroids loop fixed: {count} replacement(s)')

# Also fix remote ship rendering — swap triangle for sprite
old_triangle = """    ctx.save();
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
    ctx.shadowBlur = 0; ctx.restore();"""

new_sprite = """    ctx.save();
    ctx.translate(sx, sy);
    // Use same sprite as local player
    const pDir = p.dir || 'south';
    const pFrame = p.animFrame || 0;
    const pMoving = (p.thrusting || p.boosting);
    const pImg = pMoving
      ? (animations[pDir] && animations[pDir][pFrame % FRAME_COUNT])
      : rotations[pDir];
    if (pImg) {
      ctx.shadowColor = p.color; ctx.shadowBlur = 10;
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(pImg, Math.round(-DISPLAY_SIZE/2), Math.round(-DISPLAY_SIZE/2), DISPLAY_SIZE, DISPLAY_SIZE);
      ctx.shadowBlur = 0;
    } else {
      // fallback triangle if sprite not loaded
      ctx.shadowColor = p.color; ctx.shadowBlur = 14;
      ctx.beginPath();
      ctx.moveTo(0, -18); ctx.lineTo(11, 8); ctx.lineTo(0, 4); ctx.lineTo(-11, 8);
      ctx.closePath();
      ctx.fillStyle = p.color + 'cc'; ctx.fill();
      ctx.strokeStyle = p.color; ctx.lineWidth = 1.5; ctx.stroke();
    }
    ctx.restore();"""

if old_triangle in d:
    d = d.replace(old_triangle, new_sprite)
    print('remote sprite: patched exact')
else:
    print('remote sprite: exact match failed — triangle stays for now')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('getAsteroids in draw:', 'for (const ast of getAsteroids())' in d)
print('remote sprite logic:', 'pImg' in d)
