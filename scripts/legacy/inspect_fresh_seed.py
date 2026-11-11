import sqlite3
from pathlib import Path

from seed import seed

with sqlite3.connect(':memory:') as db:
    db.row_factory = sqlite3.Row
    db.executescript(Path('schema.sql').read_text(encoding='utf-8'))
    seed(db)
    total = db.execute('SELECT COUNT(*) FROM places').fetchone()[0]
    mizoram = db.execute('''SELECT p.id, p.slug, d.name AS district
        FROM places p
        JOIN districts d ON d.id=p.district_id
        JOIN regions r ON r.id=d.region_id
        WHERE r.slug='mizoram'
        ORDER BY p.id''').fetchall()
    print(f'Total places: {total}')
    print(f'Mizoram places: {len(mizoram)}')
    for place in mizoram:
        print(f"{place['id']}: {place['slug']} ({place['district']})")
    print('Foreign key violations:', db.execute('PRAGMA foreign_key_check').fetchall())