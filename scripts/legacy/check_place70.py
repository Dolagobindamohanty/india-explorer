import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
# Check place 70
p = db.execute("SELECT * FROM places WHERE id=70").fetchone()
print(f"Place 70: {p}")
db.close()