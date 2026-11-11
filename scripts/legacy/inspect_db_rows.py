import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Check Rajasthan
r = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Rajasthan' ORDER BY d.name").fetchall()
print(f"Rajasthan districts: {len(r)}")

# Check Ladakh
r2 = db.execute("SELECT d.name FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Ladakh' ORDER BY d.name").fetchall()
print(f"Ladakh districts: {len(r2)}")
for d in r2:
    print(f"  {d[0]}")

db.close()