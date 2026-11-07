import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")
for i, entry in enumerate(data):
    print(f"{i}: {entry['state']}")

# Find UP and Rajasthan
for entry in data:
    if entry['state'] == 'Uttar Pradesh':
        print(f"\nUP districts: {len(entry['districts'])}")
        print(f"UP districts sample: {entry['districts'][:3]}")
    if entry['state'] == 'Rajasthan':
        print(f"\nRajasthan districts: {len(entry['districts'])}")
        print(f"Rajasthan districts sample: {entry['districts'][:3]}")