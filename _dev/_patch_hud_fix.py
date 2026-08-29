raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

# ── 1. FIX drawAttachedPods: pod sprite looks like a ship — replace with glowing hex ──
OLD_PODS='''function drawAttachedPods(cx, cy) {
  if (attachedPods.length) {
    const t = Date.now() * 0.001;
    const DIR_OFFSETS = {
      north:{ox:0,oy:38},northeast:{ox:-27,oy:27},east:{ox:-38,oy:0},
      southeast:{ox:-27,oy:-27},south:{ox:0,oy:-38},southwest:{ox:27,oy:-27},
      west:{ox:38,oy:0},northwest:{ox:27,oy:27},
    };
    const off = DIR_OFFSETS[ship.dir] || {ox:0,oy:38};
    attachedPods.forEach((pod, idx) => {
      const dist  = 42 + idx * 36;
      const ratio = dist / 38;
      const px = cx + off.ox * ratio;
      const py = cy + off.oy * ratio;
      ctx.save();
      ctx.strokeStyle = "#38bdf866"; ctx.lineWidth = 1.5;
      ctx.setLineDash([4,4]);
      ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(px,py); ctx.stroke();
      ctx.setLineDash([]);
      ctx.translate(px, py + Math.sin(t*1.8+idx*1.2)*2);
      ctx.shadowColor = pod.color || "#38bdf8"; ctx.shadowBlur = 10;
      const podFrame = podRotations["south"];
      if (podFrame) {
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(podFrame, -22, -22, 44, 44);
      } else {
        ctx.fillStyle = (pod.color||"#38bdf8")+"cc";
        ctx.beginPath();
        for(let k=0;k<6;k++){const a=(k/6)*Math.PI*2-Math.PI/6;
          k===0?ctx.moveTo(Math.cos(a)*14,Math.sin(a)*14):ctx.lineTo(Math.cos(a)*14,Math.sin(a)*14);}
        ctx.closePath(); ctx.fill();
      }
      ctx.shadowBlur=0; ctx.restore();
    });
  }'''

NEW_PODS='''function drawAttachedPods(cx, cy) {
  if (attachedPods.length) {
    const t = Date.now() * 0.001;
    const DIR_OFFSETS = {
      north:{ox:0,oy:38},northeast:{ox:-27,oy:27},east:{ox:-38,oy:0},
      southeast:{ox:-27,oy:-27},south:{ox:0,oy:-38},southwest:{ox:27,oy:-27},
      west:{ox:38,oy:0},northwest:{ox:27,oy:27},
    };
    const off = DIR_OFFSETS[ship.dir] || {ox:0,oy:38};
    attachedPods.forEach((pod, idx) => {
      const dist  = 42 + idx * 36;
      const ratio = dist / 38;
      const px = cx + off.ox * ratio;
      const py = cy + off.oy * ratio + Math.sin(t*1.8+idx*1.2)*2;
      ctx.save();
      // dashed tether line
      ctx.strokeStyle = "#38bdf866"; ctx.lineWidth = 1.5;
      ctx.setLineDash([4,4]);
      ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(px,py); ctx.stroke();
      ctx.setLineDash([]);
      // draw pod as a glowing hexagon (NOT a ship sprite)
      const col = pod.color||"#38bdf8";
      const pulse = 0.7 + 0.3*Math.sin(t*2.4+idx*1.5);
      ctx.shadowColor = col; ctx.shadowBlur = 12*pulse;
      ctx.fillStyle = col+"44";
      ctx.strokeStyle = col;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for(let k=0;k<6;k++){
        const a=(k/6)*Math.PI*2 - Math.PI/6;
        const r=12;
        k===0?ctx.moveTo(px+Math.cos(a)*r,py+Math.sin(a)*r)
             :ctx.lineTo(px+Math.cos(a)*r,py+Math.sin(a)*r);
      }
      ctx.closePath(); ctx.fill(); ctx.stroke();
      // inner bright core dot
      ctx.shadowColor=col; ctx.shadowBlur=8;
      ctx.fillStyle=col+"cc";
      ctx.beginPath(); ctx.arc(px,py,3,0,Math.PI*2); ctx.fill();
      ctx.shadowBlur=0; ctx.restore();
    });
  }'''

if OLD_PODS in d:
    d=d.replace(OLD_PODS,NEW_PODS,1)
    print('OK pods fixed')
else:
    print('PODS NOT FOUND - will check partial')
    idx=d.find('function drawAttachedPods')
    print(repr(d[idx:idx+200]))

# ── 2. FIX panelH — compute it precisely to match actual content rendered ──
# The panel height must account for every y increment in the draw loop.
# Layout (fixed rows, no content dependency):
#   y starts at 30
#   NAVIGATION sBar: y+=LINE+2=24, then 3x kv rows y+=LINE=22 each = 66, then y+=LINE+4=26 → 30+24+66+26=146
#   SHIP sBar: y+=LINE+2=24
#   THRUST label: y+=4, hbar y+=16 = 20
#   HULL label+bar: y+=4, hbar y+=16 = 20
#   FUEL label: y+=4, segs y+=16 = 20
#   LOW FUEL warning (conditional, add 1 LINE=22 buffer)
#   CARGO sBar: y+=LINE+2=24
#   cargo bar: y+=14
#   resCount rows: y+=LINE each
#   empty hold line (if no cargo, add 1 LINE=22 buffer)
#   MODULES sBar+rows: (LINE+2) + modRows*LINE
#   ACTIONS sBar: y+=LINE+2=24
#   2 action rows: y+=LINE each = 44
#   NETWORK sBar+row: (LINE+2)+LINE = 46 if multiMode
#   compass: sits in top-right, no y advance
#   bottom padding: 14
#
# We'll replace panelH calculation with a proper pre-computed version
OLD_PANEL='''  const resCount=(ship.ore>0?1:0)+(ship.mineral>0?1:0)+(ship.armalcolite>0?1:0);
  const modRows =attachedPods.length;
  const netRow  =(typeof multiMode!==\"undefined\"&&multiMode)?1:0;
  const panelH  =312+resCount*LINE+(modRows?(LINE*(modRows+1)):0)+(netRow?LINE*2:0);'''

NEW_PANEL='''  const resCount=(ship.ore>0?1:0)+(ship.mineral>0?1:0)+(ship.armalcolite>0?1:0);
  const modRows =attachedPods.length;
  const netRow  =(typeof multiMode!=="undefined"&&multiMode)?1:0;
  const fuelWarning=(ship.fuel<=0||ship.fuel/FUEL_CAPACITY<0.2)?1:0;
  const emptyHold=(cargoUsed()===0)?1:0;
  // base: nav(24+66+26) + ship_sbar(24) + thrust(20) + hull(20) + fuel(20) + cargo_sbar(24) + cargo_bar(14) + actions_sbar(24) + actions_rows(44) + padding(20)
  const BASE_H = 24+66+26 + 24+20+20+20 + 24+14 + 24+44 + 20;
  const panelH = BASE_H
    + fuelWarning*LINE
    + resCount*LINE
    + emptyHold*LINE
    + (modRows?(LINE+2+modRows*LINE):0)
    + (netRow?(LINE+2+LINE):0);'''

if OLD_PANEL in d:
    d=d.replace(OLD_PANEL,NEW_PANEL,1)
    print('OK panelH fixed')
else:
    print('PANEL NOT FOUND')
    idx=d.find('const resCount=')
    print(repr(d[idx:idx+300]))

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
print('done')
