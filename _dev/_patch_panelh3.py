raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

OLD='''    + (modRows?(LINE+2)*1+modRows*LINE:0)'''
NEW='''    + (modRows?(LINE+2+modRows*LINE):0)'''

if OLD in d:
    d=d.replace(OLD,NEW,1)
    print('OK')
else:
    print('NOT FOUND')
    idx=d.find('modRows?(LINE+2')
    print(repr(d[idx-10:idx+80]))

open('driftbound_flight_test.html','wb').write(d.encode('utf-8'))
