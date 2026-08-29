lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()
# Show lines 1018-1032
for i, l in enumerate(lines[1017:1035], start=1018):
    print(f'{i:4}: {l}', end='')
