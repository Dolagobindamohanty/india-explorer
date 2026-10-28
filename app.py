from contextlib import contextmanager
import math
import os
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from seed import seed

ROOT = Path(__file__).resolve().parent


def create_app(database_path=None):
    default_path = Path('/tmp/india-explorer.sqlite3') if os.getenv('VERCEL') else ROOT / 'data' / 'explorer.sqlite3'
    path = Path(database_path or os.getenv('INDIA_EXPLORER_DB_PATH', default_path))
    path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection():
        db = sqlite3.connect(path)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
        finally:
            db.close()

    with connection() as db:
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        region_columns = {row[1] for row in db.execute('PRAGMA table_info(regions)')}
        place_columns = {row[1] for row in db.execute('PRAGMA table_info(places)')}
        if 'cover_image_url' not in region_columns:
            db.execute("ALTER TABLE regions ADD COLUMN cover_image_url TEXT NOT NULL DEFAULT ''")
        if 'image_url' not in place_columns:
            db.execute("ALTER TABLE places ADD COLUMN image_url TEXT NOT NULL DEFAULT ''")
        with db:
            # INSERT OR IGNORE makes this safe for the original two-state DB:
            # existing records are retained while new states and image metadata
            # are added on the next app start.
            seed(db)

    app = FastAPI(title='India, locally', version='0.1.0')

    def rows(sql, params=()):
        with connection() as db:
            return [dict(r) for r in db.execute(sql, params)]

    def one(sql, params):
        result = rows(sql, params)
        if not result:
            raise HTTPException(404, 'This destination is not in our pilot directory.')
        return result[0]

    def enrich_places(items):
        for item in items:
            item['best_months'] = [r['month'] for r in rows('SELECT month FROM place_months WHERE place_id=? ORDER BY month', (item['id'],))]
            item['tags'] = [r['name'] for r in rows('SELECT t.name FROM tags t JOIN place_tags pt ON pt.tag_id=t.id WHERE pt.place_id=?', (item['id'],))]
        return items

    place_select = '''SELECT p.*, d.name AS district, d.slug AS district_slug,
        r.name AS state, r.slug AS state_slug, h.name AS heritage_name, h.unesco_url
        FROM places p JOIN districts d ON d.id=p.district_id
        JOIN regions r ON r.id=d.region_id LEFT JOIN heritage_sites h ON h.id=p.heritage_id'''

    @app.get('/api/states')
    def states():
        return rows('''SELECT r.*, COUNT(DISTINCT d.id) AS district_count,
            COUNT(DISTINCT p.id) AS place_count FROM regions r
            LEFT JOIN districts d ON d.region_id=r.id LEFT JOIN places p ON p.district_id=d.id
            WHERE r.kind='state' GROUP BY r.id ORDER BY r.name''')

    @app.get('/api/union-territories')
    def union_territories():
        return rows('''SELECT r.*, COUNT(DISTINCT d.id) AS district_count,
            COUNT(DISTINCT p.id) AS place_count FROM regions r
            LEFT JOIN districts d ON d.region_id=r.id LEFT JOIN places p ON p.district_id=d.id
            WHERE r.kind='union_territory' GROUP BY r.id ORDER BY r.name''')

    @app.get('/api/states/{slug}')
    def state(slug: str):
        result = one('SELECT * FROM regions WHERE slug=?', (slug,))
        result['districts'] = rows('SELECT * FROM districts WHERE region_id=? ORDER BY name', (result['id'],))
        result['places'] = enrich_places(rows(place_select + ' WHERE r.id=? ORDER BY p.name', (result['id'],)))
        return result

    @app.get('/api/districts')
    def districts(region: str = '', kind: str = ''):
        clauses, params = ['1=1'], []
        if region:
            clauses.append('r.slug=?')
            params.append(region)
        if kind:
            clauses.append('r.kind=?')
            params.append('union_territory' if kind in ('ut', 'union-territory') else 'state')
        return rows('''SELECT d.*, r.name AS state, r.slug AS state_slug, r.kind AS region_kind
            FROM districts d JOIN regions r ON r.id=d.region_id WHERE ''' + ' AND '.join(clauses) + ' ORDER BY r.name, d.name', params)

    @app.get('/api/districts/{slug}')
    def district(slug: str):
        result = one('''SELECT d.*, r.name AS state, r.slug AS state_slug
            FROM districts d JOIN regions r ON r.id=d.region_id WHERE d.slug=?''', (slug,))
        result['places'] = enrich_places(rows(place_select + ' WHERE d.id=? ORDER BY p.name', (result['id'],)))
        result['festivals'] = festivals(month=None, district=slug)
        return result

    @app.get('/api/places')
    def places(q: str = Query('', max_length=120), state: str = '', district: str = '',
               month: int | None = Query(None, ge=1, le=12), category: str = '', unesco: bool = False):
        clauses, params = ['1=1'], []
        if q.strip():
            clauses.append('(p.name LIKE ? OR p.description LIKE ? OR d.name LIKE ?)')
            params.extend(['%' + q.strip() + '%'] * 3)
        for column, value in [('r.slug', state), ('d.slug', district), ('p.category', category)]:
            if value:
                clauses.append(column + '=?')
                params.append(value)
        if month is not None:
            clauses.append('EXISTS (SELECT 1 FROM place_months pm WHERE pm.place_id=p.id AND pm.month=?)')
            params.append(month)
        if unesco:
            clauses.append('p.heritage_id IS NOT NULL')
        return enrich_places(rows(place_select + ' WHERE ' + ' AND '.join(clauses) + ' ORDER BY p.name LIMIT 100', params))

    @app.get('/api/places/{slug}')
    def place(slug: str):
        result = enrich_places([one(place_select + ' WHERE p.slug=?', (slug,))])[0]
        candidates = enrich_places(rows(place_select + ' WHERE p.id != ?', (result['id'],)))
        for candidate in candidates:
            candidate['distance_km'] = round(distance(result, candidate), 1)
        result['nearby'] = sorted(candidates, key=lambda p: p['distance_km'])[:3]
        return result

    @app.get('/api/festivals')
    def festivals(month: int | None = Query(None, ge=1, le=12), district: str = ''):
        clauses, params = ['1=1'], []
        if month is not None:
            clauses.append('EXISTS (SELECT 1 FROM festival_months fm WHERE fm.festival_id=f.id AND fm.month=?)')
            params.append(month)
        if district:
            clauses.append('''EXISTS (SELECT 1 FROM festival_districts fd JOIN districts d
                ON d.id=fd.district_id WHERE fd.festival_id=f.id AND d.slug=?)''')
            params.append(district)
        result = rows('SELECT f.* FROM festivals f WHERE ' + ' AND '.join(clauses) + ' ORDER BY name', params)
        for item in result:
            item['months'] = [r['month'] for r in rows('SELECT month FROM festival_months WHERE festival_id=? ORDER BY month', (item['id'],))]
            item['districts'] = rows('SELECT d.name, d.slug FROM districts d JOIN festival_districts fd ON fd.district_id=d.id WHERE fd.festival_id=?', (item['id'],))
            item['occurrences'] = rows('SELECT starts_on, ends_on, source_url, verified_at FROM festival_occurrences WHERE festival_id=? ORDER BY starts_on', (item['id'],))
        return result

    @app.get('/healthz')
    def health():
        return {'status': 'ok', 'places': rows('SELECT COUNT(*) AS n FROM places')[0]['n']}

    app.mount('/', StaticFiles(directory=ROOT / 'static', html=True), name='website')
    return app


def distance(a, b):
    """Straight-line kilometres, not road distance or journey time."""
    lat1, lat2 = map(math.radians, [a['latitude'], b['latitude']])
    delta_lat = lat2 - lat1
    delta_lon = math.radians(b['longitude'] - a['longitude'])
    h = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    return 6371 * 2 * math.asin(min(1, math.sqrt(h)))


app = create_app()
