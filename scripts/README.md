# Scripts

Maintenance helpers, kept out of the application root.

## Active

| Script | Purpose |
|---|---|
| `smoke_routes.py` | Boots a throwaway app and checks every region API route. |
| `import_report.py` | Prints a JSON import-readiness report for the canonical datasets. |
| `verify_data.py` | Integrity checks against `data/explorer.sqlite3`. |

Run them from the repository root, for example:

```cmd
python scripts/verify_data.py
python scripts/smoke_routes.py
python scripts/import_report.py
```

## Legacy

`legacy/` contains one-off investigation, repair and migration scripts from the
data build-out: Mizoram inserts, Rajasthan fixes, image audits, placeholder
generation and similar. They are kept for reference only. Most assume they are
run from the repository root and may reference slugs or files that no longer
exist.

`legacy/artifacts/` holds the text output those scripts produced.
