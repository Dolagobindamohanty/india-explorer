import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Get max district ID
max_id = db.execute('SELECT MAX(id) FROM districts').fetchone()[0]
print(f"Max district ID: {max_id}")

# Get current Ladakh districts
lad_districts = db.execute("SELECT d.name, d.slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"Current Ladakh districts: {len(lad_districts)}")
for d in lad_districts:
    print(f"  {d[0]} ({d[1]})")

# Define 4 new districts to add to Ladakh
# Per audit: "Five new districts were approved in April 2026, and Sankoo became the eighth district in October 2026"
new_districts = [
    (max_id + 1, 'Drass', 'drass', 'A frontier town in Ladakh known for its strategic location and the Drass War Memorial'),
    (max_id + 2, 'Khalsi', 'khalsi', 'A high-altitude area in Ladakh known for its stark landscapes and Buddhist monasteries'),
    (max_id + 3, 'Sham', 'sham', 'The Sham region of Ladakh, culturally rich with traditional villages and monasteries'),
    (max_id + 4, 'Sankoo', 'sankoo', 'A newly approved district headquarters in Ladakh, becoming the eighth district in October 2026'),
]

# Find Ladakh's region_id
lad_region = db.execute("SELECT id FROM regions WHERE name='Ladakh'").fetchone()
lad_region_id = lad_region[0]
print(f"\nLadakh region_id: {lad_region_id}")

for did, name, slug, description in new_districts:
    # Check if already exists
    existing = db.execute("SELECT id FROM districts WHERE name=? AND region_id=?", (name, lad_region_id)).fetchone()
    if existing:
        print(f"  District {name} already exists, skipping.")
        continue
    db.execute("INSERT INTO districts (id, region_id, name, slug, description, food_notes, source_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
               (did, lad_region_id, name, slug, description, '', 'https://ladakh.gov.in/tourism/'))
    print(f"  Added: {name} ({slug})")

db.commit()

# Verify the count
remaining = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"\nLadakh districts: {len(remaining)}")
for r in remaining:
    print(f"  {r[0]}")

# Verify total districts
total_districts = db.execute('SELECT COUNT(*) FROM districts').fetchone()[0]
print(f"\nTotal districts in DB: {total_districts}")

db.close()