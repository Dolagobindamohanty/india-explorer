import sqlite3, json, sys

# 1. Update the database district counts
# Based on external data showing specific counts per state/UT

db = sqlite3.connect('data/explorer.sqlite3')

# Check current Rajasthan and Ladakh
raj_districts = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"Current Rajasthan districts: {len(raj_districts)}")

lad_districts = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"Current Ladakh districts: {len(lad_districts)}")

# The external data shows Rajasthan=55, Ladakh=2
# We need to add districts back to Rajasthan and remove some from Ladakh

# For Rajasthan - add back the 14 districts we removed
districts_to_add = [
    "Phalodi", "Pratapgarh", "Rajsamand", "Salumbar", "Sambhar Lake",
    "Sanchore", "Sawai Madhopur", "Shahpura", "Sikar", "Sirohi",
    "Sujangarh", "Suratgarh", "Tonk", "Udaipur"
]

# We need to insert these into the districts table
# Get the max ID
max_id = db.execute('SELECT MAX(id) FROM districts').fetchone()[0]
print(f"Max district ID: {max_id}")

lad_region_id = db.execute("SELECT id FROM regions WHERE name='Ladakh'").fetchone()[0]
print(f"Ladakh region_id: {lad_region_id}")

# Add districts back to Rajasthan
for i, name in enumerate(districts_to_add):
    did = max_id + 1 + i
    db.execute("INSERT INTO districts (id, region_id, name, slug, description, food_notes, source_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
               (did, 2, name, name.lower().replace(' ', '-'), f'District {name} in Rajasthan', '', 'https://www.tourism.rajasthan.gov.in/'))
    print(f"Added Rajasthan district: {name} (ID: {did})")

db.commit()

# Now update Ladakh - remove districts to leave only 2 (Kargil and Leh)
# First, get current Ladakh districts
current_lad = [d[0] for d in db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()]
print(f"Ladakh before cleanup: {current_lad}")

# We need to keep only Kargil and Leh, remove the other 6
# Get IDs of districts to remove
to_remove = [d for d in current_lad if d not in ['Kargil', 'Leh']]
print(f"Districts to remove from Ladakh: {to_remove}")

for name in to_remove:
    db.execute("DELETE FROM districts WHERE name=?", (name,))

db.commit()

# Verify
raj_after = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"Rajasthan after: {len(raj_after)}")

lad_after = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"Ladakh after: {len(lad_after)}")

db.close()

# 2. Update the source JSON
print("\nUpdating source JSON...")

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update Rajasthan - add the 14 districts back
raj_entry = data[30]
current_raj = raj_entry['districts']
for d in districts_to_add:
    if d not in current_raj:
        current_raj.append(d)
raj_entry['districts'] = current_raj
print(f"Rajasthan in JSON: {len(raj_entry['districts'])} districts")

# Update Ladakh to 2 districts
lad_entry = data[15]
current_lad_json = lad_entry['districts']
lad_entry['districts'] = [d for d in current_lad_json if d in ['Kargil', 'Leh']]
print(f"Ladakh in JSON: {len(lad_entry['districts'])} districts")

# Save
with open('data/india-states-districts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Source JSON updated successfully")