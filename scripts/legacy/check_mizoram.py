import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
r = db.execute("SELECT d.name, d.id FROM districts d JOIN regions r ON r.id=d.region_id WHERE r.name='Mizoram' ORDER BY d.name").fetchall()
for x in r:
    print(f"{x[0]} (id: {x[1]})")
db.close()