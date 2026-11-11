import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
# Get Rajasthan districts
raj_districts = db.execute("SELECT d.name, d.slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"Rajasthan districts in DB ({len(raj_districts)}):")
for d in raj_districts:
    print(f"  {d[0]} ({d[1]})")

# Get Ladakh districts
lad_districts = db.execute("SELECT d.name, d.slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"\nLadakh districts in DB ({len(lad_districts)}):")
for d in lad_districts:
    print(f"  {d[0]} ({d[1]})")

# Get all regions to understand structure
regions = db.execute("SELECT * FROM regions ORDER BY name").fetchall()
print(f"\nRegions ({len(regions)}):")
for r in regions:
    print(f"  {r[0]}: {r[1]} (kind={r[2]})")

db.close()