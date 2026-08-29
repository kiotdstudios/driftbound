txt = open('driftbound_flight_test.html','r',encoding='utf-8').read()

idx = txt.find('const BG_SETS')
print('=== BG_SETS ===')
print(txt[idx:idx+1500])

idx2 = txt.find('ASTEROID_TYPES')
print('\n=== ASTEROID_TYPES ===')
print(txt[idx2:idx2+1200])

idx3 = txt.find('oreMin')
print('\n=== first ore ref ===')
print(txt[idx3-100:idx3+200])
