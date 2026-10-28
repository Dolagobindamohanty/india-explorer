"""Run integrity checks for the India Explorer editorial/admin directory."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'explorer.sqlite3'
SOURCE = ROOT / 'data' / 'india-states-districts.json'


def normalized(value: str) -> str:
    return re.sub(r'[^a-z0-9]', '', value.lower())


def verify() -> dict:
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    state_count = db.execute("SELECT COUNT(*) FROM regions WHERE kind='state'").fetchone()[0]
    ut_count = db.execute("SELECT COUNT(*) FROM regions WHERE kind='union_territory'").fetchone()[0]
    district_count = db.execute('SELECT COUNT(*) FROM districts').fetchone()[0]
    place_count = db.execute('SELECT COUNT(*) FROM places').fetchone()[0]
    duplicate_images = [dict(row) for row in db.execute('''SELECT image_url, COUNT(*) AS count
        FROM places WHERE image_url <> '' GROUP BY image_url HAVING COUNT(*) > 1''')]
    missing_region_images = [row[0] for row in db.execute("SELECT name FROM regions WHERE cover_image_url='' OR cover_image_url IS NULL")]
    orphan_districts = db.execute('''SELECT COUNT(*) FROM districts d LEFT JOIN regions r ON r.id=d.region_id
        WHERE r.id IS NULL''').fetchone()[0]
    orphan_places = db.execute('''SELECT COUNT(*) FROM places p LEFT JOIN districts d ON d.id=p.district_id
        WHERE d.id IS NULL''').fetchone()[0]
    source = json.loads(SOURCE.read_text(encoding='utf-8')) if SOURCE.exists() else []
    source_district_count = sum(len(entry.get('districts', [])) for entry in source)
    source_pairs = {(normalized(entry.get('state', '')), normalized(name))
        for entry in source for name in entry.get('districts', [])}
    database_pairs = {(normalized(row['state']), normalized(row['name'])) for row in db.execute(
        'SELECT r.name AS state, d.name FROM districts d JOIN regions r ON r.id=d.region_id')}
    missing_source_districts = sorted([' / '.join(pair) for pair in source_pairs - database_pairs])
    report = {
        'database': str(DB),
        'source_file': str(SOURCE),
        'states': state_count,
        'union_territories': ut_count,
        'districts': district_count,
        'detailed_places': place_count,
        'source_districts': source_district_count,
        'source_districts_missing_from_database': missing_source_districts,
        'duplicate_place_images': duplicate_images,
        'regions_missing_cover_images': missing_region_images,
        'orphan_districts': orphan_districts,
        'orphan_places': orphan_places,
        'pass': (
            state_count == 28 and ut_count == 8 and source_district_count > 0
            and not missing_source_districts
            and not duplicate_images and not missing_region_images
            and orphan_districts == 0 and orphan_places == 0
        ),
        'notes': [
            'Administrative names/counts are checked against the bundled source JSON.',
            'Tourist descriptions, seasonal advice and annual festival dates still require editorial/source review.',
            'Image URLs are checked for uniqueness and presence; licensing/visual identity should be checked before publication.',
        ],
    }
    db.close()
    return report


if __name__ == '__main__':
    report = verify()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['pass'] else 1)
