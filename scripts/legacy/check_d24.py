import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
d = db.execute("SELECT * FROM districts WHERE id=24").fetchone()
print(f"District 24: {d}")
db.close()