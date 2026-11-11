import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

# Get district counts per region
counts = db.execute('''SELECT r.name as state, r.kind, COUNT(d.id) as cnt 
    FROM regions r LEFT JOIN districts d ON d.region_id=r.id 
    GROUP BY r.name, r.kind ORDER BY r.name''').fetchall()

print("Current database district counts per state/UT:")
total = 0
for c in counts:
    print(f"  {c[0]} ({c[1]}): {c[2]}")
    total += c[2]
print(f"Total: {total}")

db.close()