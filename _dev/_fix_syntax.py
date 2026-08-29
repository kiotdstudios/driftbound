data = open('driftbound_flight_test.html','rb').read()

# The broken block looks like:
# orePickups.push({\r\n\r\n          worldX: ast.worldX, worldY: ast.worldY,\r\n\r\n          amount: oreAmt, life: 480,\r\n\r\n        ,\r\n        lootType: ast.type.lootType || null,\r\n        lootChance: ast.type.lootChance || 0\r\n      });

old = (b'          amount: oreAmt, life: 480,\r\n'
       b'\r\n'
       b'        ,\r\n'
       b'        lootType: ast.type.lootType || null,\r\n'
       b'        lootChance: ast.type.lootChance || 0\r\n'
       b'      });')

new = (b'          amount: oreAmt, life: 480,\r\n'
       b'          lootType: ast.type.lootType || null,\r\n'
       b'          lootChance: ast.type.lootChance || 0,\r\n'
       b'        });')

if old in data:
    data = data.replace(old, new)
    print("Syntax fix applied")
else:
    print("Pattern not found - trying broader fix")
    # Find the bad comma line and remove it
    import re
    # Replace the bad ",\r\n        lootType" with ",\r\n          lootType"
    data = re.sub(
        rb'(amount: oreAmt, life: 480,\r\n)\r\n        ,\r\n        (lootType)',
        rb'\1          \2',
        data
    )
    data = re.sub(
        rb'(lootChance: ast\.type\.lootChance \|\| 0)\r\n      \}\);',
        rb'\1,\r\n        });',
        data
    )
    print("Broad fix applied")

open('driftbound_flight_test.html','wb').write(data)

# Verify line 1024 area
lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()
print("\nLines 1018-1032:")
for i, l in enumerate(lines[1017:1035], start=1018):
    print(f'{i:4}: {l}', end='')
