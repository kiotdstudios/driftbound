html = open('driftbound_flight_test.html','r',encoding='utf-8').read()

# Find return speed
idx = html.find('return speed;')
print('=== return speed context ===')
print(repr(html[idx-100:idx+60]))

# Find FPS display
idx2 = html.find('fpsDisplay')
print('\n=== fpsDisplay context ===')
print(repr(html[idx2:idx2+150]))

# find shiftHeld
idx3 = html.find('shiftHeld')
print('\n=== shiftHeld context ===')
print(html[idx3:idx3+200])
