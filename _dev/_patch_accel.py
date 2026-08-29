f=open('driftbound_flight_test.html','rb'); raw=f.read(); f.close()
d=raw.decode('utf-8','replace')

changes = [
    ('const THRUST       = 0.18;', 'const THRUST       = 0.126; // -30% accel'),
    ('const BOOST_THRUST = 0.42;', 'const BOOST_THRUST = 0.294; // -30% accel'),
]

for old, new in changes:
    if old in d:
        d = d.replace(old, new, 1)
        print(f'OK: {old} -> {new}')
    else:
        print(f'NOT FOUND: {old}')

f=open('driftbound_flight_test.html','wb'); f.write(d.encode('utf-8')); f.close()
