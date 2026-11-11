import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')
# Check schema
cursor = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='places'")
print("Schema:", cursor.fetchone()[0])
# Check amber-fort
cursor = db.execute("SELECT * FROM places WHERE slug='amber-fort'")
rows = cursor.fetchall()
print("Number of rows:", len(rows))
if rows:
    for i, col in enumerate(cursor.description):
        print(f"Col {i}: {col[0]}")
    for row in rows:
        print("Row data:")
        for j, val in enumerate(row):
            print(f"  {cursor.description[j][0]}: {val}")
db.close()