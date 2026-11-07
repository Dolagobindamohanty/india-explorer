import sqlite3, json

db = sqlite3.connect('data/explorer.sqlite3')

# Get all regions with their districts
regions = db.execute('''SELECT name, kind, id FROM regions ORDER BY name''').fetchall()

data = []
for r_name, r_kind, r_id in regions:
    districts = db.execute("SELECT name FROM districts WHERE region_id=? ORDER BY name", (r_id,)).fetchall()
    district_names = [d[0] for d in districts]
    data.append({
        "state": r_name,
        "districts": district_names
    })

# Save
with open('data/india-states-districts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Rebuilt JSON with {len(data)} states/UTs")
total = sum(len(e['districts']) for e in data)
print(f"Total districts: {total}")

db.close()