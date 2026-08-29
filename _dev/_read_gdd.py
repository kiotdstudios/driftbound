from docx import Document
doc = Document('Driftbound_Game_Design_Document_v1.docx')
lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
# write to txt for safe reading
with open('_gdd_full.txt','w',encoding='utf-8') as f:
    for i,l in enumerate(lines):
        f.write(f'[{i:03d}] {l}\n')
print(f'Written {len(lines)} lines to _gdd_full.txt')
# Print sections around production order / steps 6-10
for i,l in enumerate(lines):
    if any(kw in l.lower() for kw in ['production','step','secured','armory','hostile','reward','interior','loot','weapon','pod']):
        print(f'[{i:03d}] {l}')
