raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

OLD='''  // base: nav(24+66+26) + ship_sbar(24) + thrust(20) + hull(20) + fuel(20) + cargo_sbar(24) + cargo_bar(14) + actions_sbar(24) + actions_rows(44) + padding(20)
  const BASE_H = 24+66+26 + 24+20+20+20 + 24+14 + 24+44 + 20;
  const panelH = BASE_H
    + fuelWarning*LINE
    + resCount*LINE
    + emptyHold*LINE
    + (modRows?(LINE+2+modRows*LINE):0)
    + (netRow?(LINE+2+LINE):0);'''

NEW='''  // base: nav(24+66+26) + ship_sbar(24) + thrust(20) + hull(20) + fuel(20) + cargo_sbar(24) + cargo_bar(14) + actions_sbar(24) + actions_rows(44) + padding(34)
  const BASE_H = 24+66+26 + 24+20+20+20 + 24+14 + 24+44 + 34;
  const panelH = BASE_H
    + fuelWarning*LINE
    + resCount*LINE
    + emptyHold*LINE
    + (modRows?(LINE+2)*1+modRows*LINE:0)
    + (netRow?(LINE+2+LINE):0);'''

if OLD in d:
    d=d.replace(OLD,NEW,1)
    print('OK panelH v2 patched')
else:
    print('NOT FOUND')

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
