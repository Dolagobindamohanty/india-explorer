"""Print a JSON import readiness report for canonical state datasets."""

import json
import sqlite3

from data_pipeline import ROOT, import_report, validate_database
from seed import seed


if __name__ == '__main__':
    report = import_report()
    with sqlite3.connect(':memory:') as db:
        db.row_factory = sqlite3.Row
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        seed(db)
        errors, warnings = validate_database(db)
        report['seeded_catalogue'] = {
            'state_count': db.execute("SELECT COUNT(*) FROM regions WHERE kind='state'").fetchone()[0],
            'union_territory_count': db.execute("SELECT COUNT(*) FROM regions WHERE kind='union_territory'").fetchone()[0],
            'district_count': db.execute('SELECT COUNT(*) FROM districts').fetchone()[0],
            'place_count': db.execute('SELECT COUNT(*) FROM places').fetchone()[0],
            'errors': errors,
            'warnings': warnings,
        }
        report['errors'].extend(errors)
        report['warnings'].extend(warnings)
    print(json.dumps(report, indent=2, ensure_ascii=False))
