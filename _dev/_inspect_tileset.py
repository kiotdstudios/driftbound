import zipfile, os

zp = 'Ditharts_Free_Scifi_Tileset_v01.zip'
out_dir = 'Ditharts_Free_Scifi_Tileset_v01'

# list contents first
with zipfile.ZipFile(zp) as z:
    names = z.namelist()
    open('_tileset_contents.txt','w').write('\n'.join(names))
    print(f'{len(names)} files in zip:')
    for n in names:
        print(' ', n)

# extract if not already done
if not os.path.exists(out_dir):
    with zipfile.ZipFile(zp) as z:
        z.extractall(out_dir)
    print(f'\nExtracted to {out_dir}')
else:
    print(f'\nAlready extracted at {out_dir}')
