import re

with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')

fixes = []

# ── armalcolite pickup toast ──
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
    fixes.append('armalcolite pickup toast fixed')
else:
    fixes.append('armalcolite pickup: NO MATCH')

# ── _wreck into POD_TYPES ──
pat2 = re.compile(
    r"(const POD_TYPES = \{.*?)(  modular_space_pod: \{)",
    re.DOTALL
)
WRECK_TYPE = ("  // Wreck pod — spawned dynamically on ship death\n"
              "  _wreck: {\n"
              "    id:         '_wreck',\n"
              "    label:      'WRECK',\n"
              "    color:      '#f97316',\n"
              "    cargoBonus: 0,\n"
              "    desc:       'Your lost cargo. Press F to recover.',\n"
              "  },\n"
              "  modular_space_pod: {")
if pat2.search(d):
    d = pat2.sub(lambda m: m.group(1) + WRECK_TYPE, d)
    fixes.append('_wreck type added to POD_TYPES')
else:
    fixes.append('POD_TYPES _wreck: NO MATCH')

# ── attach prompt in drawWorldPods ──
pat3 = re.compile(
    r"// Attach prompt when in range\s*"
    r"if \(inRange\) \{.*?"
    r"ctx\.fillText\(podType\.desc,.*?\);\s*"
    r"\}",
    re.DOTALL
)
NEW_PROMPT = """// Attach prompt when in range
    if (inRange) {
      ctx.font = '11px Courier New';
      if (pod.type === '_wreck') {
        ctx.fillStyle = '#f97316';
        ctx.fillText('[F] RECOVER CARGO', sx, sy + POD_DISPLAY_SIZE/2 + 22);
        ctx.font = '10px Courier New'; ctx.fillStyle = '#ffffff88';
        const c = pod.cargo || {};
        const inv = [c.ore&&(c.ore+' Nebulite'), c.mineral&&(c.mineral+' Mineral'), c.armalcolite&&(c.armalcolite+' Armalcolite')].filter(Boolean).join('  ');
        ctx.fillText(inv || 'empty', sx, sy + POD_DISPLAY_SIZE/2 + 38);
      } else {
        const canAfford = ship.ore >= POD_ATTACH_COST;
        ctx.fillStyle = canAfford ? '#22c55e' : '#ef4444';
        const costTxt = canAfford
          ? `[F]  ATTACH  (${POD_ATTACH_COST} Nebulite)`
          : `NEED ${POD_ATTACH_COST} NEBULITE  (have ${ship.ore})`;
        ctx.fillText(costTxt, sx, sy + POD_DISPLAY_SIZE/2 + 22);
        ctx.font = '10px Courier New'; ctx.fillStyle = '#ffffff88';
        ctx.fillText(podType.desc, sx, sy + POD_DISPLAY_SIZE/2 + 38);
      }
    }"""
if pat3.search(d):
    d = pat3.sub(NEW_PROMPT, d)
    fixes.append('wreck recovery prompt in drawWorldPods')
else:
    fixes.append('attach prompt: NO MATCH')

with open('driftbound_flight_test.html', 'wb') as f:
    f.write(d.encode('utf-8'))

print('\n'.join(f'  {"✓" if "NO MATCH" not in v else "✗"} {v}' for v in fixes))
