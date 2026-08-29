raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')
open('_hud_dump.txt','w',encoding='utf-8').write(
    f"filelen={len(d)}\n"
    f"drawHUD={d.find('drawHUD')}\n"
    f"FUEL={d.find('FUEL')}\n"
    f"fuel={d.find('fuel')}\n"
    f"boostFactor={d.find('boostFactor')}\n"
    f"boosting={d.find('boosting')}\n"
    f"shiftKey={d.find('shiftKey')}\n"
    f"isBoosting={d.find('isBoosting')}\n"
)
# dump drawHUD function
idx=d.find('function drawHUD')
open('_hud_func.txt','w',encoding='utf-8').write(d[idx:idx+5000])
print('done')
