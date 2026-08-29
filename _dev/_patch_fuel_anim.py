raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

OLD = '''  const fuelPct=ship.fuel/FUEL_CAPACITY;
  const segW=Math.floor((PW-28)/10)-2, filledSegs=Math.ceil(fuelPct*10);
  ctx.font=SML; ctx.fillStyle=DIM; ctx.fillText("FUEL",L,y);
  ctx.font=SML; ctx.fillStyle=fuelPct<0.25?ORANGE:WHT;
  ctx.fillText(ship.fuel.toFixed(1)+" gal",L+68,y); y+=4;
  for(let i=0;i<10;i++){
    const lit=i<filledSegs;
    ctx.fillStyle=!lit?"#0d1520":fuelPct>0.5?"#3db87a":fuelPct>0.25?"#e6c040":
      (fuelPct<0.1&&Math.floor(Date.now()/300)%2===0)?"#ff2222":ORANGE;
    ctx.fillRect(L+i*(segW+2),y,segW,10);
    ctx.strokeStyle="#4FC3C318"; ctx.lineWidth=0.5;
    ctx.strokeRect(L+i*(segW+2),y,segW,10);
  }
  y+=16;
  if(ship.fuel<=0){ctx.font=SML;ctx.fillStyle="#ff4444";ctx.fillText("✕ FUEL EMPTY",L,y);y+=LINE;}
  else if(fuelPct<0.2&&Math.floor(Date.now()/500)%2===0){ctx.font=SML;ctx.fillStyle=ORANGE;ctx.fillText("⚠ LOW FUEL",L,y);y+=LINE;}'''

NEW = '''  const fuelPct=ship.fuel/FUEL_CAPACITY;
  const segW=Math.floor((PW-28)/10)-2, filledSegs=Math.ceil(fuelPct*10);
  const fuelBurning=_boosting && ship.fuel>0;
  const _ft=Date.now();
  // label — glow orange-white when burning
  ctx.font=SML;
  if(fuelBurning){
    ctx.shadowColor="#ff8800"; ctx.shadowBlur=8;
    ctx.fillStyle="#ffcc66";
  } else {
    ctx.shadowBlur=0; ctx.fillStyle=DIM;
  }
  ctx.fillText("FUEL",L,y);
  ctx.shadowBlur=0;
  ctx.font=SML; ctx.fillStyle=fuelPct<0.25?ORANGE:WHT;
  ctx.fillText(ship.fuel.toFixed(1)+" gal",L+68,y); y+=4;
  for(let i=0;i<10;i++){
    const lit=i<filledSegs;
    let segCol;
    if(!lit){
      segCol="#0d1520";
    } else if(fuelBurning){
      // flame flicker: each segment pulses with staggered sine at different phase
      const flicker=0.55+0.45*Math.sin(_ft*0.018+i*0.9);
      const r=Math.round(255);
      const g=Math.round(80+120*flicker);
      const b=Math.round(10+30*flicker);
      segCol=`rgb(${r},${g},${b})`;
    } else {
      segCol=fuelPct>0.5?"#3db87a":fuelPct>0.25?"#e6c040":
        (fuelPct<0.1&&Math.floor(_ft/300)%2===0)?"#ff2222":ORANGE;
    }
    ctx.fillStyle=segCol;
    if(fuelBurning&&lit){
      ctx.shadowColor="#ff6600"; ctx.shadowBlur=6+4*Math.sin(_ft*0.02+i);
    }
    ctx.fillRect(L+i*(segW+2),y,segW,10);
    ctx.shadowBlur=0;
    ctx.strokeStyle="#4FC3C318"; ctx.lineWidth=0.5;
    ctx.strokeRect(L+i*(segW+2),y,segW,10);
  }
  // exhaust spark: tiny bright pip on the rightmost lit seg when burning
  if(fuelBurning&&filledSegs>0){
    const sx=L+(filledSegs-1)*(segW+2)+segW;
    const sy=y+5;
    ctx.fillStyle="#ffffff";
    ctx.shadowColor="#ffaa00"; ctx.shadowBlur=10;
    ctx.fillRect(sx-1,sy-1,3,3);
    ctx.shadowBlur=0;
  }
  y+=16;
  if(ship.fuel<=0){ctx.font=SML;ctx.fillStyle="#ff4444";ctx.fillText("✕ FUEL EMPTY",L,y);y+=LINE;}
  else if(fuelPct<0.2&&Math.floor(_ft/500)%2===0){ctx.font=SML;ctx.fillStyle=ORANGE;ctx.fillText("⚠ LOW FUEL",L,y);y+=LINE;}'''

if OLD in d:
    d=d.replace(OLD,NEW,1)
    print('OK - fuel burn anim patched')
else:
    print('NOT FOUND - checking partial...')
    # show where the fuel segment starts
    idx=d.find('const fuelPct=ship.fuel/FUEL_CAPACITY')
    print('fuelPct block at char:',idx)
    print(repr(d[idx:idx+200]))

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
