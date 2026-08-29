f = open('driftbound_flight_test.html', 'rb'); raw = f.read(); f.close()

OLD = (b"} else if (ore.lootType === 'armalcolite') {\r\n"
       b"          if (cargoUsed() < CARGO_LIMIT) {\r\n"
       b"            ship.armalcolite++;\r\n"
       b"            showToast('\xe2\x97\x88 ARMALCOLITE extracted \xe2\x80\x94 refine for fuel [' + cargoUsed() + '/' + CARGO_LIMIT + ']', '#34d399');")

NEW = (b"} else if (ore.lootType === 'armalcolite') {\r\n"
       b"          if (cargoUsed() < CARGO_LIMIT) {\r\n"
       b"            ship.armalcolite++;\r\n"
       b"            showToast('\xe2\x97\x88 ARMALCOLITE  [' + ship.armalcolite + ' held]  \xe2\x80\x94  [C] to refine \xe2\x86\x92 fuel', '#34d399');")

if OLD in raw:
    raw = raw.replace(OLD, NEW, 1)
    f = open('driftbound_flight_test.html', 'wb'); f.write(raw); f.close()
    print('  \u2713 armalcolite pickup toast fixed')
else:
    print('  \u2717 NO MATCH')
