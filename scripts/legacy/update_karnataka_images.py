import json

with open(r'C:\Users\ADMIN\omnirush.ai\india-explorer\data\karnataka-places.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for p in data:
    if p['image_url'].endswith('.svg'):
        old = p['image_url']
        new_url = old.replace('.svg', '.jpg')
        p['image_url'] = new_url
        updated += 1
        print(f"Updated {p['name']}: {old} -> {new_url}")

with open(r'C:\Users\ADMIN\omnirush.ai\india-explorer\data\karnataka-places.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Total updated: {updated}')
