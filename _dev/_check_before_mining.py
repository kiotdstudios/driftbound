lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Show lines 895-940
print("=== LINES 895-940 ===")
for i, l in enumerate(lines[894:940], start=895):
    print(f'{i:4}: {l}', end='')
