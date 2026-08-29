LINE=22
BASE_H = (24+66+26) + (24+20+20+20) + (24+14) + (24+44) + 34
print(f'BASE_H = {BASE_H}')

# trace the 2-mod case manually: rc=3, mc=2, fw=0, nr=1, eh=0
rc,mc,fw,nr,eh = 3,2,0,1,0
label='3 resources, 2 mods, net, no warn'

# panelH formula
panelH = BASE_H + fw*LINE + rc*LINE + eh*LINE + (LINE+2+mc*LINE if mc else 0) + (LINE+2+LINE if nr else 0)
print(f'panelH breakdown: BASE={BASE_H} fw={fw*LINE} rc={rc*LINE} eh={eh*LINE} mods={(LINE+2+mc*LINE) if mc else 0} net={(LINE+2+LINE) if nr else 0}')
print(f'panelH = {panelH}')

# y walk
y=30
y+=LINE+2;  print(f'after nav sbar: y={y}')
y+=LINE; y+=LINE; y+=LINE; y+=LINE+4; print(f'after 3 kv + gap: y={y}')
y+=LINE+2; print(f'after ship sbar: y={y}')
y+=4; y+=16; print(f'after thrust bar: y={y}')
y+=4; y+=16; print(f'after hull bar: y={y}')
y+=4; y+=16; print(f'after fuel segs: y={y}')
if fw: y+=LINE; print(f'after fuel warn: y={y}')
y+=LINE+2; print(f'after cargo sbar: y={y}')
y+=14; print(f'after cargo bar: y={y}')
y+=rc*LINE; print(f'after {rc} res rows: y={y}')
if eh==1: y+=LINE
if mc: y+=LINE+2; y+=mc*LINE; print(f'after modules sbar+{mc} rows: y={y}')
y+=LINE+2; y+=LINE; y+=LINE; print(f'after actions sbar+2 rows: y={y}')
if nr: y+=LINE+2; y+=LINE; print(f'after network: y={y}')
y+=14; print(f'after bottom padding: y={y}')
needed=y-10
print(f'needed={needed}  panelH={panelH}  diff={panelH-needed}')
