import os, glob

base = r'C:\Users\diepowel\Documents\DRIFTBOUND'
out = []
for root, dirs, files in os.walk(base):
    for f in files:
        if any(k in f.lower() for k in ['gdd','design','doc','readme','spec','roadmap','plan']):
            fp = os.path.join(root, f)
            out.append(f'{fp}  ({os.path.getsize(fp)} bytes)')

open('_gdd_search.txt','w').write('\n'.join(out))
print(f'{len(out)} files found')
print('\n'.join(out))
