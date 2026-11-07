import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
total = db.execute('SELECT COUNT(*) FROM districts').fetchone()[0]
print(f"Total districts in DB: {total}")

# Check WB districts in DB
wb = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='West Bengal' ORDER BY d.name").fetchall()
print(f"West Bengal districts in DB: {len(wb)}")
print(f"First 3: {[x[0] for x in wb[:3]]}")
print(f"Last 3: {[x[0] for x in wb[-3:]]}")

db.close()