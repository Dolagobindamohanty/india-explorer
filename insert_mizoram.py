import sqlite3
import json

db = sqlite3.connect('data/explorer.sqlite3')

# Load Mizoram places
with open('data/mizoram-places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

# Get the maximum existing place ID
max_id = db.execute('SELECT MAX(id) FROM places').fetchone()[0] or 0
print(f"Current max place ID: {max_id}")

# Reassign IDs starting from max_id + 1
new_places = []
for i, place in enumerate(places):
    new_id = max_id + 1 + i
    new_place = dict(place)
    new_place['id'] = new_id
    new_places.append(new_place)

# Insert places
inserted = 0
for place in new_places:
    pid = place['id']
    # Check if already exists (shouldn't with new IDs)
    existing = db.execute("SELECT id FROM places WHERE id=?", (pid,)).fetchone()
    if existing:
        print(f"Place ID {pid} ({place['name']}) already exists, skipping")
        continue
    
    db.execute('''
        INSERT INTO places (id, district_id, slug, name, description, category, latitude, longitude, 
                           how_to_reach, practical_notes, heritage_id, source_url, image_url, entry_fee, address, 
                           verification_status, last_verified_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pid,
        place['district_id'],
        place['slug'],
        place['name'],
        place['description'],
        place['category'],
        place['latitude'],
        place['longitude'],
        place['how_to_reach'],
        place['practical_notes'],
        place.get('heritage_id'),
        place['source_url'],
        place['image_url'],
        place.get('entry_fee', ''),
        place.get('address', ''),
        'needs_review',
        None
    ))
    inserted += 1
    print(f"Inserted: {place['name']} (ID: {pid})")

db.commit()
print(f"\nInserted {inserted} new places for Mizoram")

# Verify
count = db.execute("SELECT COUNT(*) FROM places WHERE district_id IN (SELECT d.id FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Mizoram')").fetchone()[0]
print(f"Total places in Mizoram: {count}")

# Show the new places
places_list = db.execute("SELECT id, name, district_id FROM places WHERE district_id IN (SELECT d.id FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Mizoram') ORDER BY id").fetchall()
for p in places_list:
    print(f"  ID {p[0]}: {p[1]} (district_id: {p[2]})")

db.close()