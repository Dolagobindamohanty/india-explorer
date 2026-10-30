"""Validate canonical and fully seeded data. Intended for local and CI use."""

import sqlite3
from data_pipeline import ROOT, validate_all_state_data, validate_database
from seed import seed


def main():
    errors, warnings = validate_all_state_data()
    with sqlite3.connect(':memory:') as db:
        db.row_factory = sqlite3.Row
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        seed(db)
        database_errors, database_warnings = validate_database(db)
        errors.extend(database_errors)
        warnings.extend(database_warnings)
    for warning in warnings:
        print(f'WARNING: {warning}')
    for error in errors:
        print(f'ERROR: {error}')
    if errors:
        raise SystemExit(1)
    print('State data validation passed.')


if __name__ == '__main__':
    main()
