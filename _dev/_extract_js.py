lines = open('driftbound_flight_test.html','r',encoding='utf-8').readlines()

# Extract just the JS between <script> and </script>
in_script = False
js_lines = []
js_start_line = 0
for i, l in enumerate(lines):
    if '<script>' in l and not in_script:
        in_script = True
        js_start_line = i + 1
        continue
    if '</script>' in l and in_script:
        in_script = False
        continue
    if in_script:
        js_lines.append(l)

with open('_extracted.js', 'w', encoding='utf-8') as f:
    f.writelines(js_lines)

print(f"Extracted {len(js_lines)} lines of JS (starting at HTML line {js_start_line})")
print("Saved to _extracted.js")
