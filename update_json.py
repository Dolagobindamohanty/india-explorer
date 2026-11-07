import json

with open('data/india-states-districts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Remove Pratapgarh from UP districts (index 34)
up_entry = data[34]
# districts is a list of strings, so just filter the string names
updated_up = [d for d in up_entry['districts'] if d != 'Pratapgarh']
data[34]['districts'] = updated_up
print(f"UP districts count: {len(updated_up)}")

# Rajasthan already has 41 districts (from earlier fix), verify
raj_entry = data[30]
print(f"Rajasthan districts: {len(raj_entry['districts'])}")

# Save
with open('data/india-states-districts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Source JSON updated successfully")