import re

mapping = {
    'BAC by Ruangguru': 'bac_by_ruangguru.png',
    'BMKG': 'bkmg_tarakan.png',
    'BWS (PUPR)': 'bws_pupr.png',
    'CE-UBT': 'ce_ubt.png',
    'Dicoding': 'dicoding.png',
    'DOT Indonesia': 'dot_indonesia.png',
    'Dundalk Institute of Technology': 'dundalk_institute_of_technology.png',
    'EAC by Ruangguru': 'eac_by_ruangguru.png',
    'Earth Species Project': 'earth_species_project.png',
    'Generation of Harmony': 'generation_of_harmony.png',
    'IISMA': 'iisma.png',
    'Kemendikbudristek': 'kemendikbud.png',
    'KPH Tarakan': 'kph_tarakan.png',
    'Meaningful Design': 'meaningful_design_group.png',
    'MIT': 'mit.png',
    'Perbanas Institute': 'perbanas_institute.png',
    'Pertamina Foundation': 'pertamina_foundation.png',
    'SMK Darul Muslim (Bogor)': 'smk_darul_muslim.png',
    'UNESCO': 'unesco.png',
    'Universitas Borneo Tarakan': 'universitas_borneo_tarakan.png',
    'University of Edinburgh': 'university_of_edinburgh.png',
    'University of Sussex': 'university_of_sussex.png',
    'World Water Council': 'world_water_council.png'
}

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

for title, filename in mapping.items():
    pattern = r'(<div class=\"logo-item\" title=\"' + re.escape(title) + r'\"><img src=\")[^\"]+(\" onerror=\"[^\"]+\")( alt=\"[^\"]+\"></div>)'
    replacement = r'\g<1>assets/img/logos_real/' + filename + r'\3'
    html = re.sub(pattern, replacement, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html successfully with local logos mapping.')
