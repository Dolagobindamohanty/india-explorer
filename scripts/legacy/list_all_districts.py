import sqlite3
db = sqlite3.connect('data/explorer.sqlite3')

regions = db.execute('''SELECT name, kind, id FROM regions ORDER BY name''').fetchall()

for r_name, r_kind, r_id in regions:
    districts = db.execute("SELECT name FROM districts WHERE region_id=? ORDER BY name", (r_id,)).fetchall()
    district_names = [d[0] for d in districts]
    print(f"\n{r_name} ({r_kind}) - {len(district_names)} districts:")
    for d in district_names:
        print(f"  - {d}")

db.close()