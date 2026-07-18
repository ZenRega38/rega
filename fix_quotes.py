import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the missing double quote
html = re.sub(r'(src=\"assets/img/logos_real/[^\.]+\.png)( alt=\")', r'\1"\2', html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Fixed missing quotes!')
