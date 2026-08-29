lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Show line 1113 area
print("=== LINE 1108-1120 ===")
for i, l in enumerate(lines[1107:1122], start=1108):
    print(f'{i:4}: {l}', end='')

# Also find the broken refine block from earlier patch
print("\n=== SEARCHING FOR BROKEN REFINE BLOCK ===")
for i, l in enumerate(lines):
    if 'else if (true)' in l or 'if (multiMode) { sendRefine' in l:
        print(f'{i+1:4}: {l}', end='')
        for j in range(i, min(i+15, len(lines))):
            print(f'{j+1:4}: {lines[j]}', end='')
        break
