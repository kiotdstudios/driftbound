f = open('driftbound_flight_test.html', 'rb')
raw = f.read()
f.close()
d = raw.decode('utf-8', 'replace')

# Find where drawRemotePlayers is called
idx = d.find('drawRemotePlayers(')
while idx != -1:
    print('CALL:', d[max(0,idx-60):idx+80])
    print('---')
    idx = d.find('drawRemotePlayers(', idx+1)

# Find player_move handler
idx = d.find("'player_move'")
if idx == -1:
    idx = d.find('"player_move"')
print('\nplayer_move handler:')
print(d[idx-20:idx+200])
