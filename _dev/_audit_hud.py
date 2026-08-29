raw=open('driftbound_flight_test.html','rb').read()
d=raw.decode('utf-8','replace')

# Dump the full drawHUD function
idx=d.find('function drawHUD')
end=d.find('\nfunction ', idx+10)
open('_hud_full.txt','w',encoding='utf-8').write(d[idx:end])

# Dump drawAttachedPods
idx2=d.find('function drawAttachedPods')
end2=d.find('\nfunction ', idx2+10)
open('_pods_full.txt','w',encoding='utf-8').write(d[idx2:end2])

print('drawHUD chars:', end-idx)
print('drawAttachedPods chars:', end2-idx2)
