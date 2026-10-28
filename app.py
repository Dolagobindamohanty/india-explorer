from contextlib import contextmanager
from html import escape
import math
import os
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from seed import seed

ROOT = Path(__file__).resolve().parent
MONTH_NAMES = ('January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December')
SITE_URL = os.getenv('SITE_URL', 'https://india-explorer-hazel.vercel.app').rstrip('/')


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

    app = FastAPI(title='India Explorer', version='0.1.0')

    def rows(sql, params=()):
        with connection() as db:
            return [dict(r) for r in db.execute(sql, params)]

    def one(sql, params):
        result = rows(sql, params)
        if not result:
            raise HTTPException(404, 'This destination is not in our pilot directory.')
        return result[0]

    def enrich_places(items):
        if not items:
            return items
        ids = [item['id'] for item in items]
        placeholders = ','.join('?' for _ in ids)
        with connection() as db:
            month_rows = db.execute(
                f'SELECT place_id, month FROM place_months WHERE place_id IN ({placeholders}) ORDER BY month', ids
            ).fetchall()
            tag_rows = db.execute(
                f'''SELECT pt.place_id, t.name FROM tags t
                    JOIN place_tags pt ON pt.tag_id=t.id
                    WHERE pt.place_id IN ({placeholders}) ORDER BY t.name''', ids
            ).fetchall()
        months_by_place = {place_id: [] for place_id in ids}
        tags_by_place = {place_id: [] for place_id in ids}
        for row in month_rows:
            months_by_place[row['place_id']].append(row['month'])
        for row in tag_rows:
            tags_by_place[row['place_id']].append(row['name'])
        for item in items:
            item['best_months'] = months_by_place[item['id']]
            item['tags'] = tags_by_place[item['id']]
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

    def query_places(q='', state='', district='', month=None, category='', unesco=False, limit=100):
        clauses, params = ['1=1'], []
        if q.strip():
            search = q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            clauses.append('''(p.name LIKE ? ESCAPE '\\' OR p.description LIKE ? ESCAPE '\\'
                OR d.name LIKE ? ESCAPE '\\')''')
            params.extend(['%' + search + '%'] * 3)
        for column, value in [('r.slug', state), ('d.slug', district), ('p.category', category)]:
            if value:
                clauses.append(column + '=?')
                params.append(value)
        if month is not None:
            clauses.append('EXISTS (SELECT 1 FROM place_months pm WHERE pm.place_id=p.id AND pm.month=?)')
            params.append(month)
        if unesco:
            clauses.append('p.heritage_id IS NOT NULL')
        params.append(limit)
        return enrich_places(rows(place_select + ' WHERE ' + ' AND '.join(clauses) + ' ORDER BY p.name LIMIT ?', params))

    @app.get('/api/places')
    def places(q: str = Query('', max_length=120), state: str = '', district: str = '',
               month: int | None = Query(None, ge=1, le=12), category: str = '', unesco: bool = False):
        return query_places(q=q, state=state, district=district, month=month, category=category, unesco=unesco)

    @app.get('/api/places/{slug}')
    def place(slug: str):
        result = enrich_places([one(place_select + ' WHERE p.slug=?', (slug,))])[0]
        coordinates = rows('SELECT id, latitude, longitude FROM places WHERE id != ?', (result['id'],))
        nearest = sorted(
            ((round(distance(result, candidate), 1), candidate['id']) for candidate in coordinates),
            key=lambda item: item[0]
        )[:3]
        nearest_ids = [item[1] for item in nearest]
        if nearest_ids:
            placeholders = ','.join('?' for _ in nearest_ids)
            nearby = enrich_places(rows(place_select + f' WHERE p.id IN ({placeholders})', nearest_ids))
            distances = {place_id: distance_km for distance_km, place_id in nearest}
            for candidate in nearby:
                candidate['distance_km'] = distances[candidate['id']]
            result['nearby'] = sorted(nearby, key=lambda p: p['distance_km'])
        else:
            result['nearby'] = []
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

    def directory_counts():
        with connection() as db:
            return {
                'states': db.execute("SELECT COUNT(*) FROM regions WHERE kind='state'").fetchone()[0],
                'union_territories': db.execute("SELECT COUNT(*) FROM regions WHERE kind='union_territory'").fetchone()[0],
                'districts': db.execute('SELECT COUNT(*) FROM districts').fetchone()[0],
                'places': db.execute('SELECT COUNT(*) FROM places').fetchone()[0],
            }

    def page_document(title, content, description='Explore states, districts, heritage, beaches, mountains, culture and festivals across India.', canonical_path='/'):
        counts = directory_counts()
        canonical_url = SITE_URL + canonical_path
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><link rel="canonical" href="{escape(canonical_url, quote=True)}">
<title>{escape(title)} · India Explorer</title><link rel="stylesheet" href="/style.css"></head>
<body data-app="india-explorer"><header class="nav"><a class="brand" href="/" aria-label="India Explorer home">India<span>Explorer</span><i>✳</i></a><button class="menu-toggle" id="menu-toggle" aria-label="Open navigation" aria-expanded="false">☰</button>
<nav class="nav-links" id="nav-links" aria-label="Main navigation"><a href="/explore">Explore</a><a href="/area">States</a><a href="/month/8">Festival calendar</a><a href="/about">About</a><a class="nav-search-link" href="/explore" aria-label="Search destinations">⌕ <span>Search</span></a><a href="/saved">♡ Favorites <span id="saved-count">0</span></a><button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle dark mode">☀ <span>Light</span></button></nav></header>
<main id="app" tabindex="-1">{content}</main><footer><div class="footer-inner"><div><a class="brand" href="/">India<span>Explorer</span></a><p>Find a place to visit. Find a place to belong.</p></div><small>{counts['states']} states · {counts['union_territories']} union territories · {counts['districts']} district entries · {counts['places']} detailed places<br>Editorial sample: verify schedules and practical details with official sources.</small></div></footer><script src="/app.js"></script></body></html>'''

    def server_place_card(item):
        image_url = escape(item.get('image_url') or fallback_image(item.get('state_slug')), quote=True)
        category = escape(item.get('category') or 'Destination')
        labels = {'heritage': 'Heritage', 'beach': 'Beaches', 'nature': 'Nature', 'spiritual': 'Spiritual', 'culture': 'Culture'}
        badge = 'UNESCO heritage' if item.get('heritage_id') else labels.get(item.get('category'), category)
        months = ', '.join(MONTH_NAMES[month - 1] for month in item.get('best_months', []))
        timing = f'Best in {escape(months)}' if months else 'Seasonal details pending'
        return f'''<article class="card place-card"><a href="/place/{escape(item['slug'])}" class="art"><img src="{image_url}" alt="{escape(item['name'])} destination photo"><strong class="art-title">{escape(item['name'])}</strong><span class="badge">{escape(badge)}</span></a><div class="card-body"><div class="meta">{escape(item['district'])} · {escape(item['state'])}</div><h3><a href="/place/{escape(item['slug'])}">{escape(item['name'])}</a></h3><p>{escape(item['description'])}</p><div class="card-bottom"><span>{timing}</span><button class="save" data-save="{escape(item['slug'])}" aria-label="Save {escape(item['name'])}">♡ Save</button></div></div></article>'''

    def server_cards(items):
        return '<div class="cards">' + ''.join(server_place_card(item) for item in items) + '</div>' if items else '<p class="empty">No detailed places match this selection yet.</p>'

    def fallback_image(state):
        if state == 'kerala':
            return 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=80'
        if state == 'rajasthan':
            return 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=900&q=80'
        return 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80'

    def server_region_link(region):
        return f'''<a class="card region-card" href="/state/{escape(region['slug'])}"><div class="art"><img src="{escape(region.get('cover_image_url') or fallback_image(region['slug']), quote=True)}" alt="{escape(region['name'])} destination image"></div><div class="card-body"><div class="meta">{escape(region['kind'].replace('_', ' ').title())} · {region['district_count']} districts</div><h3>{escape(region['name'])} <span class="arrow">↗</span></h3><p>{escape(region['description'])}</p></div></a>'''

    def server_filters(query):
        params = query.copy()
        options = '<option value="">All states and UTs</option>' + ''.join(f'''<option value="{escape(region['slug'])}" {'selected' if params.get('state') == region['slug'] else ''}>{escape(region['name'])}</option>''' for region in states())
        categories = ['heritage', 'beach', 'nature', 'spiritual', 'culture']
        category_options = '<option value="">Any interest</option>' + ''.join(f'''<option value="{item}" {'selected' if params.get('category') == item else ''}>{item.title()}</option>''' for item in categories)
        month_options = '<option value="">Any month</option>' + ''.join(f'''<option value="{n}" {'selected' if params.get('month') == str(n) else ''}>{name}</option>''' for n, name in enumerate(MONTH_NAMES, 1))
        return f'''<form method="get" action="/explore" class="filters"><div class="filter-search"><span>⌕</span><input name="q" placeholder="Search places or districts" value="{escape(params.get('q', ''), quote=True)}"></div><select name="state">{options}</select><select name="month">{month_options}</select><select name="category">{category_options}</select><label class="check"><input type="checkbox" name="unesco" value="true" {'checked' if params.get('unesco') == 'true' else ''}> UNESCO only</label><button class="button">Find places</button></form>'''

    @app.get('/', response_class=HTMLResponse)
    def rendered_home():
        regions = states()
        territories = union_territories()
        featured = enrich_places(rows(place_select + ' ORDER BY (p.heritage_id IS NOT NULL) DESC, p.id LIMIT 5'))
        content = f'''<section class="hero hero-search-first"><div class="hero-copy"><p class="eyebrow">Your next Indian story starts here</p><h1>Explore <span>Incredible India.</span></h1><p class="hero-lead">Discover states, cities, monuments and culture—one curious search at a time.</p><form method="get" action="/explore" class="hero-search"><span>⌕</span><input name="q" placeholder="Search destinations, states or districts…"><button>Search</button></form></div><div class="hero-art"><div class="hero-art-caption"><span>Many places. One beautiful beginning.</span><strong>Go a little further.</strong></div></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Start with a feeling</p><h2>What are you looking for?</h2></div></div><div class="category-chips"><a class="category-chip" href="/explore?category=heritage">🏛 Heritage</a><a class="category-chip" href="/explore?category=beach">🏖 Beaches</a><a class="category-chip" href="/explore?category=nature">🌿 Nature</a><a class="category-chip" href="/explore?category=spiritual">🙏 Spiritual</a></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">A curated starting point</p><h2>Featured destinations</h2></div><a href="/explore">View all ↗</a></div>{server_cards(featured)}</section><section class="section"><div class="section-head"><div><p class="eyebrow">The full directory</p><h2>Every corner has a story.</h2><p>Browse {len(regions)} states and {len(territories)} union territories, then go district by district.</p></div></div><div class="cards">{''.join(server_region_link(region) for region in regions)}</div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Explore separately</p><h2>Union territories.</h2></div><span class="meta">{len(territories)} territories in the directory</span></div><div class="cards">{''.join(server_region_link(region) for region in territories)}</div></section>'''
        return page_document('Explore Incredible India', content)

    @app.get('/explore', response_class=HTMLResponse)
    def rendered_explore(q: str = '', state: str = '', month: int | None = Query(None, ge=1, le=12), category: str = '', unesco: bool = False):
        query = {'q': q, 'state': state, 'month': str(month) if month else '', 'category': category, 'unesco': 'true' if unesco else ''}
        result = places(q=q, state=state, month=month, category=category, unesco=unesco)
        content = f'''{breadcrumb_html('Destinations')}<p class="eyebrow">Follow your curiosity</p><h1>Find your kind of place.</h1><p>Browse our directory by season, state and interest.</p>{server_filters(query)}<p>{len(result)} detailed places found</p>{server_cards(result)}'''
        return page_document('Explore destinations', content, canonical_path='/explore')

    def breadcrumb_html(label):
        return f'<div class="breadcrumb"><a href="/">Home</a> / {escape(label)}</div>'

    @app.get('/state/{slug}', response_class=HTMLResponse)
    def rendered_state(slug: str):
        result = one('SELECT * FROM regions WHERE slug=?', (slug,))
        result['districts'] = rows('SELECT * FROM districts WHERE region_id=? ORDER BY name', (result['id'],))
        result['places'] = enrich_places(rows(place_select + ' WHERE r.id=? ORDER BY p.name', (result['id'],)))
        cover = escape(result.get('cover_image_url') or fallback_image(result['slug']), quote=True)
        districts_html = ''.join(f'<a href="/district/{escape(d["slug"])}">{escape(d["name"])} <span>↗</span></a>' for d in result['districts'])
        content = f'''{breadcrumb_html(result['name'])}<div class="state-hero" style="background-image:linear-gradient(90deg,rgba(30,58,95,.92),rgba(30,58,95,.28)),url('{cover}')"><div><p class="eyebrow">{escape(result['kind'].replace('_', ' ').title())} guide</p><h1>{escape(result['name'])}</h1><p>{escape(result['description'])}</p></div></div><div class="section-head"><div><p class="eyebrow">Administrative directory</p><h2>All districts in {escape(result['name'])}</h2></div><span class="meta">{len(result['districts'])} district entries</span></div><div class="districts">{districts_html}</div><section class="section"><h2>Places with a story</h2>{server_cards(result['places'])}</section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/state/{slug}')

    @app.get('/district/{slug}', response_class=HTMLResponse)
    def rendered_district(slug: str):
        result = one('''SELECT d.*, r.name AS state, r.slug AS state_slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE d.slug=?''', (slug,))
        result['places'] = enrich_places(rows(place_select + ' WHERE d.id=? ORDER BY p.name', (result['id'],)))
        result['festivals'] = festivals(month=None, district=slug)
        festival_html = ''.join(f'<article class="festival"><h3>{escape(item["name"])}</h3><p>{escape(item["description"])}</p><small>Typical months: {", ".join(MONTH_NAMES[month - 1] for month in item["months"])}</small></article>' for item in result['festivals']) or '<p class="empty">No festivals recorded for this district yet.</p>'
        content = f'''{breadcrumb_html(result['name'])}<p class="eyebrow">{escape(result['state'])} · Local field guide</p><h1>{escape(result['name'])}</h1><p class="lead">{escape(result['description'])}</p><div class="band"><div><h3>A taste of the district</h3><p>{escape(result['food_notes'])}</p></div><a class="source" href="{escape(result['source_url'], quote=True)}">Official information ↗</a></div><section class="section"><h2>Make a day of it</h2>{server_cards(result['places'])}</section><section class="section"><h2>Local celebrations</h2><div class="cards two">{festival_html}</div></section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/district/{slug}')

    @app.get('/place/{slug}', response_class=HTMLResponse)
    def rendered_place(slug: str):
        result = place(slug)
        months_text = ', '.join(MONTH_NAMES[item - 1] for item in result['best_months'])
        content = f'''{breadcrumb_html(result['name'])}<p class="eyebrow">{escape(result['category'])} · {escape(result['district'])}</p><h1>{escape(result['name'])}</h1><div class="detail"><div><p class="lead">{escape(result['description'])}</p><h3>How to reach</h3><p>{escape(result['how_to_reach'])}</p><h3>Before you go</h3><p>{escape(result['practical_notes'])}</p><p class="notice">Pilot editorial entry. Confirm access, fees and opening hours with the official source.</p><a class="source" href="{escape(result['source_url'], quote=True)}">Official reference ↗</a></div><aside><h3>A good time to go</h3><p>Typical months: {escape(months_text)}</p><p><a class="source" href="https://www.openstreetmap.org/?mlat={result['latitude']}&mlon={result['longitude']}">Open location on map ↗</a></p><button class="save" data-save="{escape(result['slug'])}">♡ Save</button></aside></div><section class="section"><h2>A little further along</h2>{server_cards(result['nearby'])}</section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/place/{slug}')

    @app.get('/month/{value}', response_class=HTMLResponse)
    def rendered_month(value: int):
        if value < 1 or value > 12:
            raise HTTPException(422, 'Choose a month from January to December.')
        result = places(q='', state='', district='', month=value, category='', unesco=False)
        festivals_result = festivals(month=value)
        festival_html = ''.join(f'<article class="festival"><h3>{escape(item["name"])}</h3><p>{escape(item["description"])}</p><small>Typical seasonal window: {", ".join(MONTH_NAMES[month - 1] for month in item["months"])}</small></article>' for item in festivals_result) or '<p class="empty">No festivals recorded for this month yet.</p>'
        content = f'''{breadcrumb_html('Festival calendar')}<p class="eyebrow">Let the calendar be your compass</p><h1>India in {MONTH_NAMES[value - 1]}.</h1><p>Seasonal inspiration and typical festival months from our pilot districts.</p><section class="section"><h2>Celebrations to discover</h2><div class="cards two">{festival_html}</div></section><section class="section"><h2>A good season for…</h2>{server_cards(result)}</section>'''
        return page_document('Festival calendar', content, canonical_path=f'/month/{value}')

    @app.get('/saved', response_class=HTMLResponse)
    def rendered_saved():
        content = f'''{breadcrumb_html('Saved places')}<p class="eyebrow">For another day</p><h1>Your little collection.</h1><p>Favorites are saved privately in your browser when JavaScript is enabled. Browse the destinations and choose <strong>Save</strong> to build your list.</p><a class="button" href="/explore">Explore destinations</a>'''
        return page_document('Saved places', content, canonical_path='/saved')

    @app.get('/area', response_class=HTMLResponse)
    def rendered_area():
        regions = states()
        territories = union_territories()
        state_links = ''.join(server_region_link(region) for region in regions)
        territory_links = ''.join(server_region_link(region) for region in territories)
        content = f'''{breadcrumb_html('Explore by region')}<p class="eyebrow">Start close to home</p><h1>Every corner has a story.</h1><p class="lead">Choose a state or union territory, then select a district for places, local food and celebrations.</p><section class="section"><p class="eyebrow">States</p><h2>Choose a state</h2><div class="cards">{state_links}</div></section><section class="section"><p class="eyebrow">Union territories</p><h2>Choose a union territory</h2><div class="cards">{territory_links}</div></section>'''
        return page_document('Explore states and union territories', content, canonical_path='/area')

    @app.get('/about', response_class=HTMLResponse)
    def rendered_about():
        content = f'''{breadcrumb_html('About')}<p class="eyebrow">Built for curious travellers</p><h1>Travel deeper,<br>one district at a time.</h1><p class="lead">India Explorer helps you move beyond a checklist of famous landmarks. Find the local context, heritage, celebrations and practical starting points that make a destination memorable.</p>'''
        return page_document('About India Explorer', content, canonical_path='/about')

    @app.get('/sitemap.xml', response_class=Response)
    def sitemap():
        urls = ['/', '/explore', '/area', '/about', '/saved']
        urls.extend(f"/state/{item['slug']}" for item in rows('SELECT slug FROM regions'))
        urls.extend(f"/district/{item['slug']}" for item in rows('SELECT slug FROM districts'))
        urls.extend(f"/place/{item['slug']}" for item in rows('SELECT slug FROM places'))
        urls.extend(f'/month/{month}' for month in range(1, 13))
        body = ''.join(f'<url><loc>{escape(SITE_URL + url)}</loc></url>' for url in urls)
        return Response(
            content=f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
            media_type='application/xml',
        )

    @app.get('/robots.txt', response_class=PlainTextResponse)
    def robots():
        return f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n'

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
