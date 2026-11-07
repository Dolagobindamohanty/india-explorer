import json

with open('data/mizoram-places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

# Generate seed.py format tuples with IDs starting from 495
print("# Mizoram places (add to seed.py places list)")
print()
for i, place in enumerate(places):
    new_id = 495 + i
    heritage_id = place.get('heritage_id')
    if heritage_id is None:
        heritage_id = 'None'
    
    # Escape single quotes in strings
    desc = place['description'].replace("'", "\\'")
    how_to_reach = place['how_to_reach'].replace("'", "\\'")
    practical_notes = place['practical_notes'].replace("'", "\\'")
    source_url = place['source_url'].replace("'", "\\'")
    entry_fee = place.get('entry_fee', '').replace("'", "\\'")
    address = place.get('address', '').replace("'", "\\'")
    
    tuple_str = f"""        ({new_id}, {place['district_id']}, '{place['slug']}', '{place['name']}', '{desc}', '{place['category']}', {place['latitude']}, {place['longitude']}, '{how_to_reach}', '{practical_notes}', {heritage_id}, '{source_url}', place_image('{place['slug']}')),"""
    print(tuple_str)