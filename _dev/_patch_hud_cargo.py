import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# Replace the entire cargo block using a regex that handles CRLF/LF
# Match from "// CARGO" through the last armalcolite fillText line
OLD_PAT = re.compile(
    r"// CARGO\r?\n.*?ctx\.fillText\(ship\.armalcolite \+ ' ARMALCOLITE',.*?\);",
    re.DOTALL
)

NEW_CARGO = """// CARGO — ship name + bar + resource rows (only show rows with qty > 0)
  ctx.font = 'bold 18px Courier New'; ctx.fillStyle = '#4FC3C3';
  ctx.fillText('\u26a1 ' + ship.shipType.name, LEFT, oreY - 2);

  const cUsed = cargoUsed(), cMax = ship.shipType.cargoLimit || CARGO_LIMIT, cbw = PW - 68;
  const cPct  = Math.min(cUsed / cMax, 1);
  const cFull = cUsed >= cMax;
  ctx.font = HUD_FONT_SM;
  ctx.fillStyle = cFull ? '#ef4444' : HUD_DIM;
  ctx.fillText('CARGO  ' + cUsed + '/' + cMax + (cFull ? '  \u25a0 FULL' : ''), LEFT, oreY + 16);
  ctx.fillStyle = '#0d1520'; ctx.fillRect(LEFT-1, oreY+19, cbw+2, 5);
  const cGrad = ctx.createLinearGradient(LEFT, 0, LEFT+cbw, 0);
  if (cPct < 0.7)       { cGrad.addColorStop(0,'#4FC3C3'); cGrad.addColorStop(1,'#22aacc'); }
  else if (cPct < 0.95) { cGrad.addColorStop(0,'#D9541E'); cGrad.addColorStop(1,'#ffaa44'); }
  else                  { cGrad.addColorStop(0,'#ff2222'); cGrad.addColorStop(1,'#ff6666'); }
  ctx.fillStyle = cGrad; ctx.fillRect(LEFT, oreY+20, cbw * cPct, 3);
  ctx.strokeStyle = '#ffffff18'; ctx.strokeRect(LEFT, oreY+20, cbw, 3);

  // Resource rows — only draw if qty > 0
  let resRowY = oreY + 42;
  const RES_LH = 28;
  if (ship.ore > 0) {
    ctx.font = 'bold 22px monospace'; ctx.fillStyle = '#FFD700';
    ctx.fillText('\u25c6', LEFT + 14, resRowY);
    ctx.font = HUD_FONT_SM;    ctx.fillStyle = '#FFD700';
    ctx.fillText(ship.ore + ' NEBULITE', LEFT + 32, resRowY);
    resRowY += RES_LH;
  }
  if (ship.mineral > 0) {
    ctx.font = 'bold 22px monospace'; ctx.fillStyle = '#a78bfa';
    ctx.fillText('\u2666', LEFT + 14, resRowY);
    ctx.font = HUD_FONT_SM;    ctx.fillStyle = '#c4b5fd';
    ctx.fillText(ship.mineral + ' MINERAL MAT', LEFT + 32, resRowY);
    resRowY += RES_LH;
  }
  if (ship.armalcolite > 0) {
    ctx.font = 'bold 22px monospace'; ctx.fillStyle = '#34d399';
    ctx.fillText('\u25c8', LEFT + 14, resRowY);
    ctx.font = HUD_FONT_SM;    ctx.fillStyle = '#6ee7b7';
    ctx.fillText(ship.armalcolite + ' ARMALCOLITE', LEFT + 32, resRowY);
    resRowY += RES_LH;
  }"""

m = OLD_PAT.search(d)
if m:
    d = d[:m.start()] + NEW_CARGO + d[m.end():]
    fixes.append('cargo block replaced — double CARGO gone, resources hide at 0')
else:
    fixes.append('cargo regex: NO MATCH')

# Also fix the pilots online Y — it was anchored to armY (fixed position)
# Now resources are dynamic so pilot row should follow resRowY.
# We use a JS variable resRowY that's already set after resource rows.
# Replace the hardcoded armY pilot anchor:
OLD_PILOT = "  if (typeof multiMode !== 'undefined' && multiMode) {\r\n    ctx.font = 'bold 24px monospace'; ctx.fillStyle = '#38bdf8';\r\n    ctx.fillText('\u25a0', LEFT + 14, pilotY);\r\n    ctx.font = HUD_FONT_SM; ctx.fillStyle = '#38bdf8';\r\n    ctx.fillText((Object.keys(remotePlayers).length + 1) + ' PILOTS ONLINE', LEFT + 30, pilotY);\r\n  }"
NEW_PILOT = "  if (typeof multiMode !== 'undefined' && multiMode) {\r\n    ctx.font = 'bold 22px monospace'; ctx.fillStyle = '#38bdf8';\r\n    ctx.fillText('\u25a0', LEFT + 14, resRowY);\r\n    ctx.font = HUD_FONT_SM; ctx.fillStyle = '#38bdf8';\r\n    ctx.fillText((Object.keys(remotePlayers).length + 1) + ' PILOTS ONLINE', LEFT + 32, resRowY);\r\n    resRowY += 28;\r\n  }"

if OLD_PILOT in d:
    d = d.replace(OLD_PILOT, NEW_PILOT)
    fixes.append('pilots online row follows dynamic resRowY')
else:
    fixes.append('pilot anchor: NO MATCH (non-critical)')

# Fix action hints to also follow resRowY instead of hardcoded hintY
OLD_HINTS = "  // ACTION HINTS\r\n  const canCraft = ship.armalcolite > 0;\r\n  ctx.font = HUD_FONT_SM;\r\n  ctx.fillStyle = canCraft ? '#FFD700' : '#3a3010';\r\n  ctx.fillText('[C] REFINE', LEFT, hintY);\r\n  ctx.fillStyle = canCraft ? HUD_COLOR : '#2a3040';\r\n  ctx.fillText(ORE_PER_FUEL + ' ORE \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', LEFT + 84, hintY);\r\n\r\n  ctx.fillStyle = mineTarget ? '#4FC3C3' : '#2a3a4a';\r\n  ctx.fillText('[E] MINE', LEFT, hintY + LH);\r\n  if (mineTarget) {\r\n    ctx.fillStyle = '#4FC3C380';\r\n    ctx.fillText(Math.round(mineDist) + 'px', LEFT + 72, hintY + LH);\r\n  }"

NEW_HINTS = "  // ACTION HINTS — anchored to resRowY so they sit below dynamic resource rows\r\n  resRowY += 6;  // small gap\r\n  const canCraft = ship.armalcolite > 0;\r\n  ctx.font = HUD_FONT_SM;\r\n  ctx.fillStyle = canCraft ? '#FFD700' : '#3a3010';\r\n  ctx.fillText('[C] REFINE', LEFT, resRowY);\r\n  ctx.fillStyle = canCraft ? HUD_COLOR : '#2a3040';\r\n  ctx.fillText(ORE_PER_FUEL + ' ORE \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', LEFT + 84, resRowY);\r\n\r\n  ctx.fillStyle = mineTarget ? '#4FC3C3' : '#2a3a4a';\r\n  ctx.fillText('[E] MINE', LEFT, resRowY + LH);\r\n  if (mineTarget) {\r\n    ctx.fillStyle = '#4FC3C380';\r\n    ctx.fillText(Math.round(mineDist) + 'px', LEFT + 72, resRowY + LH);\r\n  }"

if OLD_HINTS in d:
    d = d.replace(OLD_HINTS, NEW_HINTS)
    fixes.append('action hints follow dynamic resRowY')
else:
    fixes.append('hints anchor: NO MATCH (non-critical)')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
