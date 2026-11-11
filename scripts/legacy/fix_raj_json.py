import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Rajasthan is at index 30
# The current list has 55 districts; we need to keep only the first 41
raj_entry = data[30]
current_districts = raj_entry['districts']
print(f"Current Rajasthan districts: {len(current_districts)}")

# Keep first 41 districts
updated_raj = current_districts[:41]
data[30]['districts'] = updated_raj
print(f"Updated Rajasthan districts: {len(updated_raj)}")

# Save
with open('data/india-states-districts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Source JSON updated - Rajasthan now has 41 districts")