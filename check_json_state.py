import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check West Bengal
wb_entry = data[35]
print(f"West Bengal districts type: {type(wb_entry['districts'])}")
print(f"West Bengal districts count: {len(wb_entry['districts'])}")
print(f"West Bengal districts: {wb_entry['districts']}")

# Check Goa (should be 2, not 3)
goa_entries = [e for e in data if e['state'] == 'Goa']
for g in goa_entries:
    print(f"Goa entry: {g['state']}, districts: {g['districts']}")

# Check total
total_districts = sum(len(e['districts']) for e in data)
print(f"\nTotal districts in JSON: {total_districts}")