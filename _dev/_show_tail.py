lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()
total = len(lines)
print(f"Total lines: {total}")
print("\n=== LAST 60 LINES ===")
for i, l in enumerate(lines[total-60:], start=total-59):
    print(f'{i:4}: {l}', end='')
