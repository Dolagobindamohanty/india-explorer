import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Check which places reference which districts in Ladakh
# Current Ladakh districts: Kargil, Leh (only 2)
# But there are places referencing other districts

# Get all places with their district IDs
places = db.execute('SELECT p.id, p.name, p.district_id FROM places p ORDER BY p.name').fetchall()
print("All places with district_id:")
for p in places:
    d = db.execute("SELECT name FROM districts WHERE id=?", (p[2],)).fetchone()
    print(f"  {p[0]}: {p[1]} -> district_id={p[2]}, district={d[0] if d else 'NOT FOUND'}")

db.close()