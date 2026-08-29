import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ══════════════════════════════════════════════════════════════════
# 1. lg_planet drop rate 100% → 35%
# ══════════════════════════════════════════════════════════════════
OLD_DROP = "{ id: 'lg_planet', hp: 6, oreMin: 3, oreMax: 5, w: 42, h: 39, lootType: 'armalcolite', lootChance: 1.00 }"
NEW_DROP = "{ id: 'lg_planet', hp: 6, oreMin: 3, oreMax: 5, w: 42, h: 39, lootType: 'armalcolite', lootChance: 0.35 }"
if OLD_DROP in d:
    d = d.replace(OLD_DROP, NEW_DROP)
    fixes.append('lg_planet lootChance 1.00 → 0.35')
else:
    fixes.append('lg_planet drop: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 2. Remove auto-fuel on armalcolite pickup (L1172-1175)
#    Was: ship.armalcolite++; showToast refine for fuel
#    Now: just increment + show "press C to refine" toast
#    Also fix [C] REFINE hint text to say "1 ARMALCOLITE → +2.0 FUEL"
#    and remove the misleading ORE_PER_FUEL reference in the hint
# ══════════════════════════════════════════════════════════════════
OLD_ARM_PICKUP = ("        } else if (ore.lootType === 'armalcolite') {\r\n"
                  "            ship.armalcolite++;\r\n"
                  "            showToast('\u25c8 ARMALCOLITE extracted \u2014 refine for fuel [' + cargoUsed() + '/' + CARGO_LIMIT + ']', '#34d399');\r\n"
                  "          }")
NEW_ARM_PICKUP = ("        } else if (ore.lootType === 'armalcolite') {\r\n"
                  "            ship.armalcolite++;\r\n"
                  "            showToast('\u25c8 ARMALCOLITE  [' + ship.armalcolite + ' held]  \u2014  [C] to refine \u2192 fuel', '#34d399');\r\n"
                  "          }")
if OLD_ARM_PICKUP in d:
    d = d.replace(OLD_ARM_PICKUP, NEW_ARM_PICKUP)
    fixes.append('armalcolite pickup toast fixed (no auto-fuel)')
else:
    # Try regex for CRLF tolerance
    pat = re.compile(
        r"} else if \(ore\.lootType === 'armalcolite'\) \{\s*"
        r"ship\.armalcolite\+\+;\s*"
        r"showToast\('.*?', '#34d399'\);\s*"
        r"\}",
        re.DOTALL
    )
    if pat.search(d):
        d = pat.sub(("} else if (ore.lootType === 'armalcolite') {\n"
                     "            ship.armalcolite++;\n"
                     "            showToast('\u25c8 ARMALCOLITE  [' + ship.armalcolite + ' held]  \u2014  [C] to refine \u2192 fuel', '#34d399');\n"
                     "          }"), d)
        fixes.append('armalcolite pickup toast fixed (regex path)')
    else:
        fixes.append('armalcolite pickup: NO MATCH')

# Fix [C] REFINE hint label — "5 ORE → +2.0 FUEL" is wrong, armalcolite refines not ore
OLD_HINT_LABEL = re.compile(
    r"ctx\.fillText\(ORE_PER_FUEL \+ ' ORE .*?FUEL', LEFT \+ 84, resRowY\);",
    re.DOTALL
)
NEW_HINT_LABEL = "ctx.fillText('1 ARMALCOLITE \u2192 +' + FUEL_PER_CRAFT.toFixed(1) + ' FUEL', LEFT + 84, resRowY);"
if OLD_HINT_LABEL.search(d):
    d = OLD_HINT_LABEL.sub(NEW_HINT_LABEL, d)
    fixes.append('[C] REFINE hint corrected to 1 ARMALCOLITE → +2.0 FUEL')
else:
    fixes.append('refine hint: NO MATCH')

# Also fix the multiplayer toast which hardcodes "ARMALCOLITE → +2.0 FUEL"
# (already correct copy, just making sure)

# ══════════════════════════════════════════════════════════════════
# 3. RESPAWN — drop cargo, spawn a wreck pod at death location
#    Current respawn line L1834-1836:
#    if (elapsed>=4000) { ship.hp=100; ship.worldX=...; ship.worldY=...; ship.vx=0; ship.vy=0; ship.destroyed=false; showToast... }
# ══════════════════════════════════════════════════════════════════
OLD_RESPAWN = re.compile(
    r"if \(elapsed>=4000\) \{\s*"
    r"ship\.hp=SHIP_MAX_HP; ship\.worldX=\(Math\.random\(\)-0\.5\)\*300; ship\.worldY=\(Math\.random\(\)-0\.5\)\*300;\s*"
    r"ship\.vx=0; ship\.vy=0; ship\.destroyed=false; showToast\('RESPAWNED','#22c55e'\);\s*"
    r"\}",
    re.DOTALL
)
NEW_RESPAWN = """if (elapsed >= 4000) {
        // ── Spawn a wreck pod at the death location before wiping cargo ──
        if (ship.ore > 0 || ship.mineral > 0 || ship.armalcolite > 0) {
          worldPods.push({
            pid:     'wreck_' + Date.now(),
            type:    '_wreck',
            worldX:  ship.worldX + (Math.random()-0.5)*40,
            worldY:  ship.worldY + (Math.random()-0.5)*40,
            angle:   Math.random() * Math.PI * 2,
            cargo:   { ore: ship.ore, mineral: ship.mineral, armalcolite: ship.armalcolite },
            label:   'WRECK',
          });
        }
        // ── Wipe cargo on respawn ──
        ship.ore = 0; ship.mineral = 0; ship.armalcolite = 0;
        ship.hp = SHIP_MAX_HP;
        ship.worldX = (Math.random()-0.5)*300;
        ship.worldY = (Math.random()-0.5)*300;
        ship.vx = 0; ship.vy = 0;
        ship.destroyed = false;
        saveGame();
        showToast('RESPAWNED \u2014 cargo lost. Find your wreck to recover it.', '#f97316');
      }"""
if OLD_RESPAWN.search(d):
    d = OLD_RESPAWN.sub(NEW_RESPAWN, d)
    fixes.append('respawn drops cargo, spawns wreck pod')
else:
    fixes.append('respawn: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 4. Add _wreck to POD_TYPES and draw wreck pods differently
#    Inject _wreck type into POD_TYPES block
# ══════════════════════════════════════════════════════════════════
OLD_POD_TYPES_END = "  modular_space_pod: {\r\n    id:       'modular_space_pod',"
NEW_POD_TYPES_END = ("  // Wreck pod — spawned dynamically on ship death, not in worldPods at boot\r\n"
                     "  _wreck: {\r\n"
                     "    id:         '_wreck',\r\n"
                     "    label:      'WRECK',\r\n"
                     "    color:      '#f97316',\r\n"
                     "    cargoBonus: 0,\r\n"
                     "    desc:       'Your lost cargo. Press F to recover.',\r\n"
                     "  },\r\n"
                     "  modular_space_pod: {\r\n"
                     "    id:       'modular_space_pod',")
if OLD_POD_TYPES_END in d:
    d = d.replace(OLD_POD_TYPES_END, NEW_POD_TYPES_END)
    fixes.append('_wreck type added to POD_TYPES')
else:
    fixes.append('POD_TYPES end: NO MATCH')

# ══════════════════════════════════════════════════════════════════
# 5. drawWorldPods — handle _wreck type specially
#    Wreck pods: orange color, broken hex shape fallback, different attach text
#    Also fix updatePods to return wreck cargo on F
# ══════════════════════════════════════════════════════════════════

# Fix attach prompt inside drawWorldPods to show wreck recovery text
OLD_ATTACH_PROMPT = ("    // Attach prompt when in range\r\n"
                     "    if (inRange) {\r\n"
                     "      const canAfford = ship.ore >= POD_ATTACH_COST;\r\n"
                     "      ctx.font      = '11px Courier New';\r\n"
                     "      ctx.fillStyle = canAfford ? '#22c55e' : '#ef4444';\r\n"
                     "      const costTxt = canAfford\r\n"
                     "        ? `[F]  ATTACH  (${POD_ATTACH_COST} Nebulite)`\r\n"
                     "        : `NEED ${POD_ATTACH_COST} NEBULITE  (have ${ship.ore})`;\r\n"
                     "      ctx.fillText(costTxt, sx, sy + POD_DISPLAY_SIZE/2 + 22);\r\n"
                     "      // Desc line\r\n"
                     "      ctx.font      = '10px Courier New';\r\n"
                     "      ctx.fillStyle = '#ffffff88';\r\n"
                     "      ctx.fillText(podType.desc, sx, sy + POD_DISPLAY_SIZE/2 + 38);\r\n"
                     "    }")
NEW_ATTACH_PROMPT = ("    // Attach prompt when in range\r\n"
                     "    if (inRange) {\r\n"
                     "      ctx.font = '11px Courier New';\r\n"
                     "      if (pod.type === '_wreck') {\r\n"
                     "        // Show wreck cargo contents\r\n"
                     "        ctx.fillStyle = '#f97316';\r\n"
                     "        ctx.fillText('[F] RECOVER CARGO', sx, sy + POD_DISPLAY_SIZE/2 + 22);\r\n"
                     "        ctx.font = '10px Courier New'; ctx.fillStyle = '#ffffff88';\r\n"
                     "        const c = pod.cargo || {};\r\n"
                     "        const inv = [c.ore&&(c.ore+' Nebulite'), c.mineral&&(c.mineral+' Mineral'), c.armalcolite&&(c.armalcolite+' Armalcolite')].filter(Boolean).join('  ');\r\n"
                     "        ctx.fillText(inv || 'empty', sx, sy + POD_DISPLAY_SIZE/2 + 38);\r\n"
                     "      } else {\r\n"
                     "        const canAfford = ship.ore >= POD_ATTACH_COST;\r\n"
                     "        ctx.fillStyle = canAfford ? '#22c55e' : '#ef4444';\r\n"
                     "        const costTxt = canAfford\r\n"
                     "          ? `[F]  ATTACH  (${POD_ATTACH_COST} Nebulite)`\r\n"
                     "          : `NEED ${POD_ATTACH_COST} NEBULITE  (have ${ship.ore})`;\r\n"
                     "        ctx.fillText(costTxt, sx, sy + POD_DISPLAY_SIZE/2 + 22);\r\n"
                     "        ctx.font = '10px Courier New'; ctx.fillStyle = '#ffffff88';\r\n"
                     "        ctx.fillText(podType.desc, sx, sy + POD_DISPLAY_SIZE/2 + 38);\r\n"
                     "      }\r\n"
                     "    }")
if OLD_ATTACH_PROMPT in d:
    d = d.replace(OLD_ATTACH_PROMPT, NEW_ATTACH_PROMPT)
    fixes.append('wreck recovery prompt in drawWorldPods')
else:
    fixes.append('attach prompt: NO MATCH')

# Fix updatePods to handle wreck recovery differently from module attach
OLD_UPDATE_PODS = re.compile(
    r"function updatePods\(\) \{.*?// one pod per keypress\s*\}\s*\}",
    re.DOTALL
)
NEW_UPDATE_PODS = """function updatePods() {
  if (!keys['KeyF']) return;
  for (let i = worldPods.length - 1; i >= 0; i--) {
    const pod  = worldPods[i];
    const dist = Math.hypot(pod.worldX - ship.worldX, pod.worldY - ship.worldY);
    if (dist < POD_ATTACH_RANGE) {

      if (pod.type === '_wreck') {
        // ── Recover wreck cargo ──
        const c = pod.cargo || {};
        ship.ore          += (c.ore          || 0);
        ship.mineral      += (c.mineral      || 0);
        ship.armalcolite  += (c.armalcolite  || 0);
        worldPods.splice(i, 1);
        const recovered = [c.ore&&(c.ore+' Nebulite'), c.mineral&&(c.mineral+' Mineral'), c.armalcolite&&(c.armalcolite+' Armalcolite')].filter(Boolean).join(', ');
        showToast('CARGO RECOVERED  ' + (recovered || '(empty)'), '#f97316');
        saveGame();
        // Burst particles (orange)
        for (let p = 0; p < 25; p++) {
          const ang = Math.random()*Math.PI*2, spd = 1+Math.random()*3;
          particles.push({x:canvas.width/2,y:canvas.height/2,vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
            life:40+Math.random()*30,maxLife:70,color:'#f97316',size:2+Math.random()*2});
        }

      } else {
        // ── Attach module pod ──
        if (ship.ore >= POD_ATTACH_COST) {
          ship.ore -= POD_ATTACH_COST;
          const podType = POD_TYPES[pod.type];
          attachedPods.push({ ...podType, pid: pod.pid });
          worldPods.splice(i, 1);
          if (podType.cargoBonus) ship.shipType.cargoLimit += podType.cargoBonus;
          showToast('POD ATTACHED  +' + (podType.cargoBonus||0) + ' CARGO', '#38bdf8');
          saveGame();
          for (let p = 0; p < 30; p++) {
            const ang = Math.random()*Math.PI*2, spd = 1+Math.random()*3;
            particles.push({x:canvas.width/2,y:canvas.height/2,vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
              life:40+Math.random()*30,maxLife:70,color:'#38bdf8',size:2+Math.random()*2});
          }
        } else {
          showToast('NOT ENOUGH NEBULITE  (' + ship.ore + '/' + POD_ATTACH_COST + ')', '#ef4444');
        }
      }
      return; // one pod per keypress
    }
  }
}"""
if OLD_UPDATE_PODS.search(d):
    d = OLD_UPDATE_PODS.sub(NEW_UPDATE_PODS, d)
    fixes.append('updatePods handles wreck recovery vs module attach')
else:
    fixes.append('updatePods: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
