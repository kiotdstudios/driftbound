data = open('driftbound_flight_test.html', 'rb').read()

# Find the call (not the function definition)
target = b'drawShip(cx, cy, now, speed);'
positions = [i for i in range(len(data)) if data[i:i+len(target)] == target]
print("Call positions:", positions)

removed = 0
for pos in positions:
    line_start = data.rfind(b'\n', 0, pos) + 1
    line_end   = data.find(b'\n', pos) + 1
    line_bytes = data[line_start:line_end]
    print("Line to remove:", repr(line_bytes))
    # Only remove the call line, not the function definition
    if b'function' not in line_bytes:
        data = data[:line_start] + data[line_end:]
        removed += 1
        print("Removed.")
    else:
        print("Skipped (function def).")

open('driftbound_flight_test.html', 'wb').write(data)
print("Writes done. Removed", removed, "lines.")
print("Calls remaining:", data.count(target))
