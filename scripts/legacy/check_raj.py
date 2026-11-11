import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

r = data[30]
print(f"Rajasthan districts: {len(r['districts'])}")
print("First 3:", r['districts'][:3])
print("Last 3:", r['districts'][-3:])