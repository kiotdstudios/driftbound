txt = open('driftbound_flight_test.html','r',encoding='utf-8').read()
anchors = ['oreCount +=', 'oreCount+=', 'let oreCount', 'var oreCount',
           'Ore:', 'oreBar', 'refine', 'oreCount > 0', 'oreCount--',
           'drawHUD', 'FUEL', 'fuelLevel']
for a in anchors:
    idx = txt.find(a)
    if idx >= 0:
        print(f'\n--- [{a}] at {idx} ---')
        print(txt[idx:idx+150])
    else:
        print(f'NOT FOUND: {a}')
