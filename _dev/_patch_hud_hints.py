import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# Fix pilots online — regex match
OLD_PILOT_PAT = re.compile(
    r"if \(typeof multiMode !== 'undefined' && multiMode\) \{\s*"
    r"ctx\.font = 'bold 24px monospace'; ctx\.fillStyle = '#38bdf8';\s*"
    r"ctx\.fillText\('\\u25a0', LEFT \+ 14, pilotY\);\s*"
    r"ctx\.font = HUD_FONT_SM; ctx\.fillStyle = '#38bdf8';\s*"
    r"ctx\.fillText\(\(Object\.keys\(remotePlayers\)\.length \+ 1\) \+ ' PILOTS ONLINE', LEFT \+ 30, pilotY\);\s*"
    r"\}",
    re.DOTALL
)
NEW_PILOT = ("  if (typeof multiMode !== 'undefined' && multiMode) {\n"
             "    ctx.font = 'bold 22px monospace'; ctx.fillStyle = '#38bdf8';\n"
             "    ctx.fillText('\u25a0', LEFT + 14, resRowY);\n"
             "    ctx.font = HUD_FONT_SM; ctx.fillStyle = '#38bdf8';\n"
             "    ctx.fillText((Object.keys(remotePlayers).length + 1) + ' PILOTS ONLINE', LEFT + 32, resRowY);\n"
             "    resRowY += 28;\n"
             "  }")
if OLD_PILOT_PAT.search(d):
    d = OLD_PILOT_PAT.sub(NEW_PILOT, d)
    fixes.append('pilots online follows resRowY')
else:
    fixes.append('pilot regex: NO MATCH')

# Fix action hints — regex match
OLD_HINTS_PAT = re.compile(
    r"// ACTION HINTS\s*"
    r"const canCraft = ship\.armalcolite > 0;\s*"
    r"ctx\.font = HUD_FONT_SM;\s*"
    r"ctx\.fillStyle = canCraft \? '#FFD700' : '#3a3010';\s*"
    r"ctx\.fillText\('\[C\] REFINE', LEFT, hintY\);\s*"
    r"ctx\.fillStyle = canCraft \? HUD_COLOR : '#2a3040';\s*"
    r"ctx\.fillText\(ORE_PER_FUEL \+ ' ORE \\u2192 \+' \+ FUEL_PER_CRAFT\.toFixed\(1\) \+ ' FUEL', LEFT \+ 84, hintY\);\s*"
    r"ctx\.fillStyle = mineTarget \? '#4FC3C3' : '#2a3a4a';\s*"
    r"ctx\.fillText\('\[E\] MINE', LEFT, hintY \+ LH\);\s*"
    r"if \(mineTarget\) \{\s*"
    r"ctx\.fillStyle = '#4FC3C380';\s*"
    r"ctx\.fillText\(Math\.round\(mineDist\) \+ 'px', LEFT \+ 72, hintY \+ LH\);\s*"
    r"\}",
    re.DOTALL
)
NEW_HINTS = ("  // ACTION HINTS — sit below dynamic resource rows\n"
             "  resRowY += 6;\n"
             "  const canCraft = ship.armalcolite > 0;\n"
             "  ctx.font = HUD_FONT_SM;\n"
             "  ctx.fillStyle = canCraft ? '#FFD700' : '#3a3010';\n"
             "  ctx.fillText('[C] REFINE', LEFT, resRowY);\n"
             "  ctx.fillStyle = canCraft ? HUD_COLOR : '#2a3040';\n"
             "  ctx.fillText(ORE_PER_FUEL + ' ORE \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', LEFT + 84, resRowY);\n\n"
             "  ctx.fillStyle = mineTarget ? '#4FC3C3' : '#2a3a4a';\n"
             "  ctx.fillText('[E] MINE', LEFT, resRowY + LH);\n"
             "  if (mineTarget) {\n"
             "    ctx.fillStyle = '#4FC3C380';\n"
             "    ctx.fillText(Math.round(mineDist) + 'px', LEFT + 72, resRowY + LH);\n"
             "  }")
if OLD_HINTS_PAT.search(d):
    d = OLD_HINTS_PAT.sub(NEW_HINTS, d)
    fixes.append('action hints follow resRowY')
else:
    fixes.append('hints regex: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
