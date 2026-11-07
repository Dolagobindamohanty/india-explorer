import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
# Check district 89
d = db.execute("SELECT * FROM districts WHERE id=89").fetchone()
print(f"District 89: {d}")
# Check what region it belongs to
if d:
    r = db.execute("SELECT * FROM regions WHERE id=?", (d[1],)).fetchone()
    print(f"Region: {r}")
db.close()