lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Show drawDebug end and divider start — lines 1960-2000
print("=== LINES 1960-2010 ===")
for i, l in enumerate(lines[1959:2010], start=1960):
    print(f'{i:4}: {l}', end='')
