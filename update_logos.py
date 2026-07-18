with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Delete Linguae Paris
    if 'title="Linguae Paris"' in line:
        continue
        
    # 2. Add no-invert to World Water Council
    if 'title="World Water Council"' in line:
        line = line.replace('<img src="', '<img class="no-invert" src="')
        
    # 3. Replace HMTK UBT source
    if 'title="HMTK UBT"' in line:
        # replace the entire inner HTML of the div to be safe
        import re
        line = re.sub(r'<img[^>]+>', '<img src="assets/img/logos_real/hmtk_ft_ubt.png" alt="HMTK UBT">', line)
        
    new_lines.append(line)

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Updated index.html successfully.')
