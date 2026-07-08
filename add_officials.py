import json

in_path = 'countries_raw.json'
out_path = 'countries_with_officials.json'

with open(in_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    langs = item.get('languages', [])
    if langs and isinstance(langs, list) and len(langs) > 0:
        # choose the first language's name as official_language
        first = langs[0]
        item['official_language'] = first.get('name') if isinstance(first, dict) else None
    else:
        item['official_language'] = None

    # official religion data not present in source; set to None
    item['official_religion'] = None

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Wrote {len(data)} entries to {out_path}')
