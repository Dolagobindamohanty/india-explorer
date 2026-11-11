import sys
import tempfile
from pathlib import Path

# Allow running as `python scripts/smoke_routes.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from app import create_app  # noqa: E402

path = Path(tempfile.mkdtemp()) / 'smoke.sqlite3'
client = TestClient(create_app(path))
regions = client.get('/api/states').json() + client.get('/api/union-territories').json()
failures = []
for region in regions:
    response = client.get(f"/api/states/{region['slug']}")
    if response.status_code != 200:
        failures.append((region['slug'], response.status_code))

print(f"Regions checked: {len(regions)}")
print(f"Failures: {failures}")
print(f"Mizoram places: {len(client.get('/api/states/mizoram').json()['places'])}")
print(f"Health: {client.get('/healthz').json()}")