import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Update Diskit Monastery's district_id to Leh (valid Ladakh district)
db.execute("UPDATE places SET district_id=? WHERE id=70", (24,))

db.commit()

# Verify the fix
p = db.execute("SELECT * FROM places WHERE id=70").fetchone()
print(f"Updated place 70 district_id: {p[2]}")

# Check what district this is now
d = db.execute("SELECT d.name FROM districts d WHERE d.id=?", (p[2],)).fetchone()
print(f"District name: {d[0] if d else 'NOT FOUND'}")

# Check for any other orphan places
orphan_places = db.execute('''SELECT COUNT(*) FROM places p LEFT JOIN districts d ON d.id=p.district_id
    WHERE d.id IS NULL''').fetchone()[0]
print(f"Orphan places after fix: {orphan_places}")

db.close()
print("Fix completed successfully")