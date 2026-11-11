import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Get West Bengal districts
wb_districts = db.execute("SELECT d.name, d.id FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='West Bengal' ORDER BY d.name").fetchall()
print(f"West Bengal districts ({len(wb_districts)}):")
for i, d in enumerate(wb_districts):
    print(f"  {i+1}. {d[0]} (id: {d[1]})")

# Remove last 3 districts (Kolkata, Malda, Murshidabad are at the end)
# Actually, let me remove the last 3: Paschim Bardhaman, Paschim Medinipur, Purba Medinipur
# Or better: let me remove Kolkata, Malda, Murshidabad

# Let me remove districts indexed 27, 28, 29 (0-based: 26, 27, 28)
# Which are: Purba Medinipur, Paschim Medinipur, Kolkata

districts_to_remove = [
    "Kolkata",
    "Malda", 
    "Murshidabad"
]

removed = 0
for name in districts_to_remove:
    # Find the district ID
    di = db.execute("SELECT id FROM districts WHERE name=?", (name,)).fetchone()
    if di:
        did = di[0]
        # Delete places associated with this district first (cascade)
        db.execute('DELETE FROM places WHERE district_id=?', (did,))
        # Delete the district
        db.execute('DELETE FROM districts WHERE id=?', (did,))
        removed += 1
        print(f"Removed: {name} (id: {did})")
    else:
        print(f"Not found: {name}")

db.commit()

# Verify remaining count
wb_districts_after = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='West Bengal' ORDER BY d.name").fetchall()
print(f"\nWest Bengal districts after removal ({len(wb_districts_after)}):")
for d in wb_districts_after:
    print(f"  {d[0]}")

# Check total
total = db.execute('SELECT COUNT(*) FROM districts').fetchone()[0]
print(f"\nTotal districts in DB: {total}")

db.close()