import os

search_roots = [
    r'C:\Users\diepowel\Desktop',
    r'C:\Users\diepowel\Documents',
    r'C:\Users\diepowel\Downloads',
    r'C:\Users\diepowel\OneDrive - amazon.com',
]

results = []
for root in search_roots:
    for dirpath, dirnames, files in os.walk(root):
        dn = os.path.basename(dirpath).lower()
        if 'dithart' in dn or 'scifi' in dn or 'ditharts' in dn:
            results.append(f'DIR: {dirpath}')
            for f in files:
                fp = os.path.join(dirpath, f)
                results.append(f'  {f}  ({os.path.getsize(fp)} bytes)')

open('_tileset_search.txt','w').write('\n'.join(results))
print(f'{len(results)} lines')
print('\n'.join(results[:80]))
