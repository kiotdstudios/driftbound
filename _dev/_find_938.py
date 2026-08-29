lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

print("=== LINE 930-950 ===")
for i, l in enumerate(lines[929:952], start=930):
    print(f'{i:4}: {l}', end='')
