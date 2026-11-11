import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Check orphan places
orphan_places = db.execute('''SELECT COUNT(*) FROM places p LEFT JOIN districts d ON d.id=p.district_id
    WHERE d.id IS NULL''').fetchone()[0]
print(f"Orphan places: {orphan_places}")

# Find which places are orphaned
orphan_list = db.execute('''SELECT p.id, p.name, p.district_id FROM places p LEFT JOIN districts d ON d.id=p.district_id
    WHERE d.id IS NULL''').fetchall()
print(f"Orphaned place IDs and names:")
for o in orphan_list:
    print(f"  {o[0]}: {o[1]} (district_id: {o[2]})")

db.close()