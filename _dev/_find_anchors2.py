txt = open('driftbound_flight_test.html','r',encoding='utf-8').read()
anchors = ['ship.ore', 'ship.fuel', 'ORE_PER_FUEL', 'ship.hp',
           'ship = {', 'const ship', 'let ship',
           'oreBar', 'ore :', 'ore:']
for a in anchors:
    idx = txt.find(a)
    if idx >= 0:
        print(f'\n--- [{a}] at {idx} ---')
        print(txt[idx:idx+200])
    else:
        print(f'NOT FOUND: {a}')
