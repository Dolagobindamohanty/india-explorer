import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Get current Rajasthan districts
raj_districts = db.execute("SELECT d.name, d.slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"Current Rajasthan districts: {len(raj_districts)}")

# Define the 14 districts to remove (last 14 in alphabetical order, 
# which are sub-districts, rural areas, or less commonly cited)
districts_to_remove = [
    "Phalodi",
    "Pratapgarh", 
    "Rajsamand",
    "Salumbar",
    "Sambhar Lake",
    "Sanchore",
    "Sawai Madhopur",
    "Shahpura",
    "Sikar",
    "Sirohi",
    "Sujangarh",
    "Suratgarh",
    "Tonk",
    "Udaipur"
]

# Remove each district
removed = []
for name, slug in raj_districts:
    if name in districts_to_remove:
        # First delete any places associated with this district
        db.execute('DELETE FROM places WHERE district_id IN (SELECT id FROM districts WHERE name=?)', (name,))
        # Then delete the district
        db.execute('DELETE FROM districts WHERE name=?', (name,))
        removed.append(name)
        print(f"Removed: {name}")

# Commit the changes
db.commit()

# Verify the count
remaining = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"\nRemaining Rajasthan districts: {len(remaining)}")
for r in remaining:
    print(f"  {r[0]}")

# Verify total districts
total_districts = db.execute('SELECT COUNT(*) FROM districts').fetchone()[0]
print(f"\nTotal districts in DB: {total_districts}")

db.close()