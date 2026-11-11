import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# West Bengal is at index 35
wb_entry = data[35]
print(f"West Bengal districts type: {type(wb_entry['districts'])}")
print(f"West Bengal districts count: {len(wb_entry['districts'])}")
print(f"First 3: {wb_entry['districts'][:3]}")

# Remove kolkata, malda, murshidabad
new_districts = [d for d in wb_entry['districts'] if d not in ['Kolkata', 'Malda', 'Murshidabad']]
print(f"New count: {len(new_districts)}")
print(f"First 3 new: {new_districts[:3]}")

wb_entry['districts'] = new_districts

# Save
with open('data/india-states-districts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Source JSON updated successfully")