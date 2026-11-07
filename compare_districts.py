import json
import sqlite3

with open('data/india-states-districts.json', encoding='utf-8') as file:
    source = json.load(file)
source_pairs = {(item['state'], district) for item in source for district in item['districts']}

with sqlite3.connect('data/explorer.sqlite3') as db:
    database_pairs = set(db.execute('''SELECT r.name, d.name
        FROM districts d JOIN regions r ON r.id=d.region_id'''))

print('Extra database districts:')
for state, district in sorted(database_pairs - source_pairs):
    print(f'{state}: {district}')
print('Missing database districts:')
for state, district in sorted(source_pairs - database_pairs):
    print(f'{state}: {district}')