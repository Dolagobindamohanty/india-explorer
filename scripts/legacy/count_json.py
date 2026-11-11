import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("State/UT district counts in JSON:")
total = 0
for entry in data:
    cnt = len(entry['districts'])
    total += cnt
    print(f"  {entry['state']}: {cnt}")

print(f"\nTotal: {total}")