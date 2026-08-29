with open('driftbound_flight_test.html', 'rb') as f:
    d = f.read().decode('utf-8', 'replace')
lines = d.split('\n')

# Find the lobby / name input section
for i, line in enumerate(lines, 1):
    if any(t in line.lower() for t in ['input', 'lobby', 'playername', 'player_name',
                                        'your name', 'enter name', 'nameInput',
                                        'name_input', 'txtName', 'querySelector']):
        print(f'L{i}: {line.rstrip()[:140]}')
