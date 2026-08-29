import os

base = r'C:\Users\diepowel\Documents\DRIFTBOUND'
out = []

for f in sorted(os.listdir(base)):
    fp = os.path.join(base, f)
    if os.path.isfile(fp):
        out.append(f'FILE  {f}  ({os.path.getsize(fp):,} bytes)')
    else:
        out.append(f'DIR   {f}/')

open('_folder_audit.txt','w').write('\n'.join(out))
print('\n'.join(out))
