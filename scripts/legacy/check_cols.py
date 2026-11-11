import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
cols = db.execute("PRAGMA table_info(regions)").fetchall()
print("Regions columns:", [c[1] for c in cols])
db.close()