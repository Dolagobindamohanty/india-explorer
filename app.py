from contextlib import contextmanager
from html import escape
import json
import math
import os
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from seed import STATE_COVER_IMAGES, seed

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
        heritage_columns = {row[1] for row in db.execute('PRAGMA table_info(heritage_sites)')}
        if 'cover_image_url' not in region_columns:
            db.execute("ALTER TABLE regions ADD COLUMN cover_image_url TEXT NOT NULL DEFAULT ''")
        if 'image_url' not in place_columns:
            db.execute("ALTER TABLE places ADD COLUMN image_url TEXT NOT NULL DEFAULT ''")
        if 'entry_fee' not in place_columns:
            db.execute("ALTER TABLE places ADD COLUMN entry_fee TEXT NOT NULL DEFAULT ''")
        if 'address' not in place_columns:
            db.execute("ALTER TABLE places ADD COLUMN address TEXT NOT NULL DEFAULT ''")
        if 'designation' not in heritage_columns:
            db.execute("ALTER TABLE heritage_sites ADD COLUMN designation TEXT NOT NULL DEFAULT 'world_heritage_site'")
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
        r.name AS state, r.slug AS state_slug, h.name AS heritage_name, h.unesco_url,
        h.designation AS heritage_designation
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

    def query_places(q='', state='', district='', month=None, category='', unesco=False, limit=500):
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
            item['districts'] = rows('''SELECT d.name, d.slug, r.name AS state, r.slug AS state_slug
                FROM districts d JOIN regions r ON r.id=d.region_id
                JOIN festival_districts fd ON fd.district_id=d.id
                WHERE fd.festival_id=? ORDER BY r.name, d.name''', (item['id'],))
            item['occurrences'] = rows('SELECT starts_on, ends_on, source_url, verified_at FROM festival_occurrences WHERE festival_id=? ORDER BY starts_on', (item['id'],))
        return result

    @app.get('/api/circuits')
    def api_circuits():
        circuits_list = rows('SELECT * FROM circuits ORDER BY id')
        for c in circuits_list:
            c['stops'] = rows('''SELECT cp.stop_order, cp.notes, p.name, p.slug, p.category, p.image_url,
                d.name AS district, r.name AS state, r.slug AS state_slug, p.latitude, p.longitude
                FROM circuit_places cp
                JOIN places p ON p.id=cp.place_id
                JOIN districts d ON d.id=p.district_id
                JOIN regions r ON r.id=d.region_id
                WHERE cp.circuit_id=?
                ORDER BY cp.stop_order''', (c['id'],))
        return circuits_list

    @app.get('/api/circuits/{slug}')
    def api_circuit(slug: str):
        c = one('SELECT * FROM circuits WHERE slug=?', (slug,))
        c['stops'] = rows('''SELECT cp.stop_order, cp.notes, p.name, p.slug, p.category, p.image_url,
            p.description, p.how_to_reach, d.name AS district, r.name AS state, r.slug AS state_slug,
            p.latitude, p.longitude
            FROM circuit_places cp
            JOIN places p ON p.id=cp.place_id
            JOIN districts d ON d.id=p.district_id
            JOIN regions r ON r.id=d.region_id
            WHERE cp.circuit_id=?
            ORDER BY cp.stop_order''', (c['id'],))
        return c

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

    def editorial_status():
        with connection() as db:
            detailed_places = db.execute('SELECT COUNT(*) FROM places').fetchone()[0]
            reviewed_places = db.execute(
                "SELECT COUNT(*) FROM places WHERE verification_status='verified'"
            ).fetchone()[0]
            confirmed_festival_dates = db.execute('SELECT COUNT(*) FROM festival_occurrences').fetchone()[0]
            return {
                'detailed_places': detailed_places,
                'reviewed_places': reviewed_places,
                'unreviewed_places': detailed_places - reviewed_places,
                'confirmed_festival_dates': confirmed_festival_dates,
            }

    @app.get('/api/editorial-status')
    def editorial_status_api():
        return editorial_status()

    def page_document(title, content, description='Explore states, districts, heritage, beaches, mountains, culture and festivals across India.', canonical_path='/'):
        counts = directory_counts()
        canonical_url = SITE_URL + canonical_path
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><link rel="canonical" href="{escape(canonical_url, quote=True)}">
<title>{escape(title)} · India Explorer</title><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"></head>
<body data-app="india-explorer" data-server-rendered="true"><header class="nav"><a class="brand" href="/" aria-label="India Explorer home">India<span>Explorer</span><i>✳</i></a><button class="menu-toggle" id="menu-toggle" aria-label="Open navigation" aria-expanded="false">☰</button>
<nav class="nav-links" id="nav-links" aria-label="Main navigation"><a href="/explore">Explore</a><a href="/area">States</a><a href="/circuits">Travel trails</a><a href="/festivals">Festival calendar</a><a href="/about">About</a><a class="nav-search-link" href="/explore" aria-label="Search destinations">⌕ <span>Search</span></a><a href="/saved">♡ Favorites <span id="saved-count">0</span></a><button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle dark mode">☀ <span>Light</span></button></nav></header>
<main id="app" tabindex="-1">{content}</main><footer><div class="footer-inner"><div><a class="brand" href="/">India<span>Explorer</span></a><p>Find a place to visit. Find a place to belong.</p></div><small>{counts['states']} states · {counts['union_territories']} union territories · {counts['districts']} district entries · {counts['places']} detailed places<br>Editorial sample: verify schedules and practical details with official sources.</small></div></footer><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script src="/app.js"></script></body></html>'''

    def server_place_card(item):
        image_url = escape(item.get('image_url') or fallback_image(item.get('state_slug')), quote=True)
        category = escape(item.get('category') or 'Destination')
        labels = {'heritage': 'Heritage', 'beach': 'Beaches', 'nature': 'Nature', 'spiritual': 'Spiritual', 'culture': 'Culture'}
        desig = item.get('heritage_designation')
        if desig == 'world_heritage_site':
            badge = 'UNESCO World Heritage'
        elif desig == 'component_site':
            badge = 'UNESCO Component'
        elif desig == 'tentative_list':
            badge = 'UNESCO Tentative List'
        else:
            badge = labels.get(item.get('category'), category)
        fee_badge = f'<span class="badge fee-badge">🎟 {escape(item["entry_fee"])}</span>' if item.get('entry_fee') else ''
        sector_display = f'📍 {escape(item["address"])}' if item.get('address') else escape(item['district'] + ' · ' + item['state'])
        months = ', '.join(MONTH_NAMES[month - 1] for month in item.get('best_months', []))
        timing = f'Best in {escape(months)}' if months else 'Seasonal details pending'
        return f'''<article class="card place-card" data-category="{escape(item.get('category',''))}"><a href="/place/{escape(item['slug'])}" class="art"><img src="{image_url}" alt="{escape(item['name'])} destination photo" loading="lazy"><span class="badge">{escape(badge)}</span>{fee_badge}</a><div class="card-body"><div class="meta">{sector_display}</div><h3><a href="/place/{escape(item['slug'])}">{escape(item['name'])}</a></h3><p>{escape(item['description'])}</p><div class="card-bottom"><span>{timing}</span><button class="save" data-save="{escape(item['slug'])}" aria-label="Save {escape(item['name'])}">♡ Save</button></div></div></article>'''

    def category_filter_strip(places_list):
        if len(places_list) < 4:
            return ''
        cats = sorted(set(p.get('category', '') for p in places_list if p.get('category')))
        cat_labels = {'heritage': '🏛 Heritage & Monuments', 'nature': '🌿 Nature & Gardens', 'culture': '🎨 Culture & City', 'spiritual': '🙏 Spiritual', 'beach': '🏖 Beaches'}
        pills = [f'<button type="button" class="cat-pill active" data-filter="all">All ({len(places_list)})</button>']
        for c in cats:
            cnt = sum(1 for p in places_list if p.get('category') == c)
            label = cat_labels.get(c, c.title())
            pills.append(f'<button type="button" class="cat-pill" data-filter="{c}">{label} ({cnt})</button>')
        return f'<div class="category-filter-strip" id="category-filter-strip">{"".join(pills)}</div>'

    def server_cards(items):
        return '<div class="cards">' + ''.join(server_place_card(item) for item in items) + '</div>' if items else '<p class="empty">No detailed places match this selection yet.</p>'

    def fallback_image(state):
        return STATE_COVER_IMAGES.get(state) or (f'/assets/states/{state}.jpg' if state else '/assets/state-cover.svg')

    def server_region_link(region):
        cover = escape(region.get('cover_image_url') or fallback_image(region.get('slug')), quote=True)
        return f'''<a class="card region-card" href="/state/{escape(region['slug'])}"><div class="art"><img src="{cover}" alt="{escape(region['name'])} destination image" loading="lazy"></div><div class="card-body"><div class="meta">{escape(region['kind'].replace('_', ' ').title())} · {region['district_count']} districts</div><h3>{escape(region['name'])} <span class="arrow">↗</span></h3><p>{escape(region['description'])}</p></div></a>'''

    def server_festival_card(item):
        months_str = ', '.join(MONTH_NAMES[m - 1] for m in item.get('months', []))
        locations = []
        for d in item.get('districts', []):
            st = d.get('state', '')
            dt = d.get('name', '')
            locations.append(f'<span class="festival-location">📍 <strong>{escape(st)}</strong>: <a href="/district/{escape(d["slug"])}">{escape(dt)}</a></span>')
        locations_html = ' '.join(locations) if locations else '<span class="festival-location">📍 Pan-India</span>'
        timing = f'Typically in {escape(months_str)}' if months_str else 'Seasonal timing varies'
        source_link = f'<a class="source" href="{escape(item["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer">Official tourism reference ↗</a>' if item.get('source_url') else ''
        return f'''<article class="card festival-card"><div class="card-body"><div class="meta">{locations_html}</div><h3>{escape(item['name'])}</h3><p>{escape(item['description'])}</p><div class="card-bottom"><span>🗓 {escape(timing)}</span>{source_link}</div></div></article>'''

    def server_circuit_card(c):
        cover = escape(c.get('cover_image_url') or '/assets/state-cover.svg', quote=True)
        stops_count = len(c.get('stops', []))
        stops_preview = ' → '.join(escape(s['name']) for s in c.get('stops', [])[:3])
        if stops_count > 3:
            stops_preview += f' and {stops_count - 3} more'
        return f'''<article class="card circuit-card"><a href="/circuit/{escape(c['slug'])}" class="art"><img src="{cover}" alt="{escape(c['name'])} trail photo" loading="lazy"><span class="badge">🧭 {escape(c['duration'])}</span></a><div class="card-body"><div class="meta">Trail · {stops_count} curated stops · {escape(c['best_season'])}</div><h3><a href="/circuit/{escape(c['slug'])}">{escape(c['name'])} <span class="arrow">↗</span></a></h3><p>{escape(c['description'])}</p><div class="circuit-route-preview"><strong>Stops:</strong> {stops_preview}</div><div class="card-bottom"><span>🗓 Best: {escape(c['best_season'])}</span><a class="button secondary compact" href="/circuit/{escape(c['slug'])}">Explore trail ↗</a></div></div></article>'''

    def month_tabs_html(active_month=None):
        tabs = [f'<a href="/festivals" class="month-tab {"active" if active_month is None else ""}">All Months</a>']
        for i, name in enumerate(MONTH_NAMES, 1):
            is_act = active_month == i
            tabs.append(f'<a href="/festivals?month={i}" class="month-tab {"active" if is_act else ""}">{name[:3]}</a>')
        return f'<nav class="month-selector-tabs" aria-label="Filter festivals by month">{"".join(tabs)}</nav>'

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
        featured = enrich_places(rows(place_select + ' ORDER BY (p.heritage_id IS NOT NULL) DESC, p.id LIMIT 6'))
        featured_states = [r for r in regions if r['slug'] in ('odisha', 'rajasthan', 'kerala', 'goa', 'himachal-pradesh', 'tamil-nadu')][:6]
        state_cards = ''.join(server_region_link(r) for r in featured_states)
        hero_slides_data = [
            ('/assets/places/konark-sun-temple.jpg', 'Puri, Odisha', 'Konark Sun Temple'),
            ('/assets/states/uttar-pradesh.jpg', 'Agra, Uttar Pradesh', 'Taj Mahal'),
            ('/assets/places/aguada-fort.jpg', 'North Goa', 'Fort Aguada & Lighthouse'),
            ('/assets/states/punjab.jpg', 'Amritsar, Punjab', 'Harmandir Sahib (Golden Temple)'),
            ('/assets/places/alappuzha-backwaters.jpg', 'Alappuzha, Kerala', 'Backwaters of Kerala'),
            ('/assets/states/rajasthan.jpg', 'Jaipur, Rajasthan', 'Hawa Mahal (Pink City)'),
            ('/assets/states/maharashtra.jpg', 'Mumbai, Maharashtra', 'Gateway of India'),
            ('/assets/states/west-bengal.jpg', 'Kolkata, West Bengal', 'Victoria Memorial'),
            ('/assets/places/puri-jagannath-temple.jpg', 'Puri, Odisha', 'Shree Jagannath Temple'),
            ('/assets/states/jammu-and-kashmir.jpg', 'Srinagar, Jammu & Kashmir', 'Dal Lake Shikaras'),
            ('/assets/places/palolem-beach.jpg', 'Canacona, South Goa', 'Palolem Beach'),
            ('/assets/states/ladakh.jpg', 'Ladakh', 'Thiksey Monastery'),
        ]
        slides_html = ''.join(f'''<div class="hero-slide {'active' if i == 0 else ''}" style="background-image:linear-gradient(180deg,rgba(20,38,32,0.15) 0%,rgba(20,38,32,0.85) 100%),url('{img}')" data-caption-sub="{escape(sub)}" data-caption-title="{escape(title)}"></div>''' for i, (img, sub, title) in enumerate(hero_slides_data))
        dots_html = ''.join(f'''<span class="hero-dot {'active' if i == 0 else ''}" data-slide-index="{i}" role="button" aria-label="Slide {i+1}: {escape(title)}"></span>''' for i, (_, _, title) in enumerate(hero_slides_data))

        content = f'''<section class="hero hero-search-first"><div class="hero-copy"><p class="eyebrow">Your next Indian story starts here</p><h1>Explore <span>Incredible India.</span></h1><p class="hero-lead">Discover states, cities, monuments and culture—one curious search at a time.</p><form method="get" action="/explore" class="hero-search"><span>⌕</span><input name="q" placeholder="Search destinations, states or districts…"><button>Search</button></form></div><div class="hero-art" id="hero-slideshow" role="region" aria-label="Featured destinations slideshow"><div class="hero-slides">{slides_html}</div><div class="hero-art-caption"><span id="hero-art-sub">{hero_slides_data[0][1]}</span><strong id="hero-art-title">{hero_slides_data[0][2]}</strong><div class="hero-dots" aria-label="Slideshow navigation">{dots_html}</div></div></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Start with a feeling</p><h2>What are you looking for?</h2></div></div><div class="category-chips"><a class="category-chip" href="/explore?category=heritage">🏛 Heritage</a><a class="category-chip" href="/explore?category=beach">🏖 Beaches</a><a class="category-chip" href="/explore?category=nature">🌿 Nature</a><a class="category-chip" href="/explore?category=spiritual">🙏 Spiritual</a><a class="category-chip" href="/explore?category=culture">🎨 Culture</a></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">A curated starting point</p><h2>Featured destinations</h2></div><a href="/explore">View all ↗</a></div>{server_cards(featured)}</section><section class="section"><div class="section-head"><div><p class="eyebrow">Explore by region</p><h2>Featured States</h2><p>A glimpse into India’s diverse states. Explore them district by district.</p></div><a class="button secondary" href="/area">View all 28 States & 8 UTs ↗</a></div><div class="cards">{state_cards}</div><div style="margin-top:28px;text-align:center;"><a class="button" href="/area">Explore All 28 States & 8 Union Territories ↗</a></div></section>'''
        return page_document('Explore Incredible India', content)

    @app.get('/explore', response_class=HTMLResponse)
    def rendered_explore(q: str = '', state: str = '', month: int | None = Query(None, ge=1, le=12), category: str = '', unesco: bool = False):
        query = {'q': q, 'state': state, 'month': str(month) if month else '', 'category': category, 'unesco': 'true' if unesco else ''}
        result = places(q=q, state=state, month=month, category=category, unesco=unesco)
        places_json = json.dumps([{'slug': p['slug'], 'name': p['name'], 'category': p['category'], 'lat': p['latitude'], 'lon': p['longitude'], 'image_url': p.get('image_url') or fallback_image(p.get('state_slug')), 'district': p['district'], 'state': p['state']} for p in result])
        content = f'''{breadcrumb_html('Destinations')}<p class="eyebrow">Follow your curiosity</p><h1>Find your kind of place.</h1><p>Browse our directory by season, state and interest.</p>{server_filters(query)}<div class="explore-toolbar"><p><strong>{len(result)}</strong> detailed places found</p><div class="view-toggles"><button type="button" class="view-toggle active" id="view-grid-btn">⊞ Grid View</button><button type="button" class="view-toggle" id="view-map-btn">🗺 Interactive Map</button></div></div><div id="explore-map-container" class="explore-map-wrap" style="display:none;"><div id="explore-leaflet-map" class="explore-leaflet-map" data-places="{escape(places_json, quote=True)}"></div></div><div id="explore-grid-container">{server_cards(result)}</div>'''
        return page_document('Explore destinations', content, canonical_path='/explore')

    def breadcrumb_html(label, parent_label=None, parent_url=None):
        if parent_label and parent_url:
            return f'<div class="breadcrumb"><a href="/">Home</a> / <a href="{escape(parent_url)}">{escape(parent_label)}</a> / {escape(label)}</div>'
        return f'<div class="breadcrumb"><a href="/">Home</a> / {escape(label)}</div>'

    @app.get('/state/{slug}', response_class=HTMLResponse)
    def rendered_state(slug: str):
        result = one('SELECT * FROM regions WHERE slug=?', (slug,))
        result['districts'] = rows('SELECT * FROM districts WHERE region_id=? ORDER BY name', (result['id'],))
        result['places'] = enrich_places(rows(place_select + ' WHERE r.id=? ORDER BY p.name', (result['id'],)))
        cover = escape(result.get('cover_image_url') or fallback_image(result['slug']), quote=True)
        districts_html = ''.join(f'<a href="/district/{escape(d["slug"])}">{escape(d["name"])} <span>↗</span></a>' for d in result['districts'])
        content = f'''{breadcrumb_html(result['name'], 'States', '/area')}<div class="state-hero" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.08) 0%,rgba(15,28,24,0.65) 60%,rgba(15,28,24,0.92) 100%),url('{cover}')"><div class="state-hero-card"><span class="hero-badge-pill">{escape(result['kind'].replace('_', ' ').title())} Guide</span><h1>{escape(result['name'])}</h1><p>{escape(result['description'])}</p><div class="hero-stats-strip"><span>🏛 <strong>{len(result['districts'])}</strong> districts</span><span>📍 <strong>{len(result['places'])}</strong> curated attractions</span></div></div></div><div class="section-head"><div><p class="eyebrow">Administrative directory</p><h2>All districts in {escape(result['name'])}</h2></div><span class="meta">{len(result['districts'])} district entries</span></div><div class="districts">{districts_html}</div><section class="section" id="destinations"><div class="section-head"><div><p class="eyebrow">Curated field guide</p><h2>Places with a story</h2></div><span class="meta">{len(result['places'])} attractions</span></div>{category_filter_strip(result['places'])}{server_cards(result['places'])}</section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/state/{slug}')

    @app.get('/district/{slug}', response_class=HTMLResponse)
    def rendered_district(slug: str):
        result = one('''SELECT d.*, r.name AS state, r.slug AS state_slug FROM districts d JOIN regions r ON r.id=d.region_id WHERE d.slug=?''', (slug,))
        result['places'] = enrich_places(rows(place_select + ' WHERE d.id=? ORDER BY p.name', (result['id'],)))
        result['festivals'] = festivals(month=None, district=slug)
        cover = escape(fallback_image(result['state_slug']), quote=True)
        festival_html = ''.join(server_festival_card(item) for item in result['festivals']) or '<p class="empty">No festivals recorded for this district yet.</p>'
        content = f'''{breadcrumb_html(result['name'], result['state'], f'/state/{result["state_slug"]}')}<div class="state-hero district-hero" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.08) 0%,rgba(15,28,24,0.65) 60%,rgba(15,28,24,0.92) 100%),url('{cover}')"><div class="state-hero-card"><span class="hero-badge-pill">{escape(result['state'])} · District Field Guide</span><h1>{escape(result['name'])}</h1><p>{escape(result['description'])}</p><div class="hero-stats-strip"><span>📍 <strong>{len(result['places'])}</strong> detailed attractions</span><span>🎉 <strong>{len(result['festivals'])}</strong> festivals</span></div></div></div><div class="band"><div><h3>A taste of the district</h3><p>{escape(result['food_notes'])}</p></div><a class="source" href="{escape(result['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Official information ↗</a></div><section class="section" id="destinations"><div class="section-head"><div><p class="eyebrow">Curated attractions</p><h2>Make a day of it</h2></div><span class="meta">{len(result['places'])} attractions in {escape(result['name'])}</span></div>{category_filter_strip(result['places'])}{server_cards(result['places'])}</section><section class="section"><h2>Local celebrations</h2><div class="cards two">{festival_html}</div></section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/district/{slug}')

    @app.get('/place/{slug}', response_class=HTMLResponse)
    def rendered_place(slug: str):
        result = place(slug)
        months_text = ', '.join(MONTH_NAMES[item - 1] for item in result['best_months'])
        month_pills = []
        for m in range(1, 13):
            is_best = m in result['best_months']
            label = MONTH_NAMES[m - 1][:3]
            cls = 'pill-best' if is_best else 'pill-off'
            month_pills.append(f'<span class="season-pill {cls}" title="{MONTH_NAMES[m-1]}: {"Ideal time to visit" if is_best else "Low / off season"}">{label}</span>')
        season_bar_html = f'<div class="season-pill-strip">{"".join(month_pills)}</div>'

        cat = result.get('category')
        cat_tips = {
            'heritage': 'Wear comfortable walking shoes with grip. A licensed monument guide helps unearth historical details.',
            'beach': 'Swim only in designated lifeguard-patrolled zones. High-SPF sunscreen and light cottons recommended.',
            'spiritual': 'Modest attire covering shoulders and knees is strictly required. Remove footwear and deposit electronics outside.',
            'nature': 'Eco-sensitive sanctuary. Carry reusable water bottles, insect repellent, and avoid plastic litter.',
            'culture': 'Support local artisan cooperatives and ask for permission before photographing people or private residences.'
        }
        tip = cat_tips.get(cat, 'Check weather updates and confirm entry schedules with official tourism authorities.')

        unesco_badge = ''
        desig = result.get('heritage_designation')
        if desig == 'world_heritage_site':
            unesco_badge = f'''<div class="unesco-detail-box"><span class="badge">UNESCO World Heritage Site</span><p>Officially inscribed World Heritage property: <a class="source" href="{escape(result['unesco_url'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(result['heritage_name'])} ↗</a></p></div>'''
        elif desig == 'component_site':
            unesco_badge = f'''<div class="unesco-detail-box"><span class="badge">UNESCO Component Site</span><p>Component of serial World Heritage property: <a class="source" href="{escape(result['unesco_url'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(result['heritage_name'])} ↗</a></p></div>'''
        elif desig == 'tentative_list':
            unesco_badge = f'''<div class="unesco-detail-box"><span class="badge">UNESCO Tentative List</span><p>Nominated on UNESCO’s Tentative List: <a class="source" href="{escape(result['unesco_url'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(result['heritage_name'])} ↗</a></p></div>'''

        fee_box = f'''<div class="aside-box"><h3>Official Entry Fee</h3><p class="entry-fee-highlight">🎟 <strong>{escape(result['entry_fee'])}</strong></p></div>''' if result.get('entry_fee') else ''
        addr_box = f'''<div class="aside-box"><h3>Location / Address</h3><p>📍 {escape(result['address'])}</p></div>''' if result.get('address') else ''

        content = f'''{breadcrumb_html(result['name'], 'Destinations', '/explore')}<p class="eyebrow">{escape(result['category'].title())} · {escape(result['district'])} · {escape(result['state'])}</p><h1>{escape(result['name'])}</h1><div class="detail"><div><p class="lead">{escape(result['description'])}</p>{unesco_badge}<h3>How to reach</h3><p>{escape(result['how_to_reach'])}</p><h3>Before you go & practical notes</h3><p>{escape(result['practical_notes'])}</p><div class="travel-tip-card"><strong>💡 Traveler’s Protocol:</strong> {escape(tip)}</div><p class="notice">Pilot editorial entry. Confirm access, fees and opening hours with the official source.</p><a class="source" href="{escape(result['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Official reference ↗</a></div><aside>{fee_box}{addr_box}<div class="aside-box"><h3>Best time to visit</h3><p>Typical peak months: <strong>{escape(months_text)}</strong></p>{season_bar_html}<div class="season-legend"><span class="legend-dot best"></span> Peak Season <span class="legend-dot off"></span> Low/Monsoon</div></div><div class="aside-box"><h3>Coordinates</h3><p><a class="source" href="https://www.openstreetmap.org/?mlat={result['latitude']}&mlon={result['longitude']}" target="_blank" rel="noopener noreferrer">Open on OpenStreetMap ↗</a></p><button class="save" data-save="{escape(result['slug'])}">♡ Save to Favorites</button></div></aside></div><section class="section"><h2>A little further along</h2>{server_cards(result['nearby'])}</section>'''
        return page_document(result['name'], content, result['description'], canonical_path=f'/place/{slug}')

    @app.get('/circuits', response_class=HTMLResponse)
    def rendered_circuits():
        circuits_list = api_circuits()
        cards_html = f'<div class="cards two">{"".join(server_circuit_card(c) for c in circuits_list)}</div>'
        content = f'''{breadcrumb_html('Curated travel circuits')}<p class="eyebrow">Themed journeys</p><h1>Curated travel trails.</h1><p class="lead">Follow hand-crafted routes connecting iconic landmarks, sacred heritage, clifftop sea bastions, and high Himalayan valleys across India.</p>{cards_html}'''
        return page_document('Curated travel trails', content, canonical_path='/circuits')

    @app.get('/circuit/{slug}', response_class=HTMLResponse)
    def rendered_circuit(slug: str):
        c = api_circuit(slug)
        cover = escape(c.get('cover_image_url') or '/assets/state-cover.svg', quote=True)
        stops_html = []
        for s in c['stops']:
            stops_html.append(f'''<div class="timeline-stop"><div class="stop-badge">Stop {s['stop_order']}</div><div class="stop-content"><h3><a href="/place/{escape(s['slug'])}">{escape(s['name'])} ↗</a></h3><div class="meta">{escape(s['district'])} · {escape(s['state'])} · {escape(s['category'].title())}</div><p>{escape(s['description'])}</p><div class="stop-note">💡 <strong>Trail note:</strong> {escape(s['notes'])}</div></div></div>''')
        content = f'''{breadcrumb_html(c['name'], 'Travel trails', '/circuits')}<div class="state-hero circuit-hero" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.08) 0%,rgba(15,28,24,0.65) 60%,rgba(15,28,24,0.92) 100%),url('{cover}')"><div class="state-hero-card"><span class="hero-badge-pill">Curated Trail · {escape(c['duration'])}</span><h1>{escape(c['name'])}</h1><p>{escape(c['tagline'])}</p><div class="hero-stats-strip"><span>🗓 <strong>{escape(c['best_season'])}</strong></span><span>🧭 <strong>{len(c['stops'])}</strong> curated stops</span></div></div></div><div class="circuit-detail-header"><div class="circuit-meta-pill"><strong>Duration:</strong> {escape(c['duration'])}</div><div class="circuit-meta-pill"><strong>Best season:</strong> {escape(c['best_season'])}</div><div class="circuit-meta-pill"><strong>Stops:</strong> {len(c['stops'])} destinations</div></div><p class="lead">{escape(c['description'])}</p><section class="section"><h2>Itinerary & stops</h2><div class="circuit-timeline">{''.join(stops_html)}</div></section><section class="section"><h2>Destinations on this trail</h2>{server_cards([dict(s, district_slug='', state_slug=s.get('state_slug','')) for s in c['stops']])}</section>'''
        return page_document(c['name'], content, c['description'], canonical_path=f'/circuit/{slug}')

    @app.get('/festivals', response_class=HTMLResponse)
    def rendered_festivals(month: int | None = Query(None, ge=1, le=12)):
        result = festivals(month=month)
        month_name = MONTH_NAMES[month - 1] if month else ''
        title = f'Festivals in {month_name}' if month else 'Festivals Across India'
        eyebrow = f'India in {month_name}' if month else 'Cultural calendar'
        heading = f'Festivals in {month_name}.' if month else 'Celebrations across India.'
        lead = f'Explore traditional festivals, fairs and celebrations observed in {month_name} across Indian states and districts.' if month else 'Select a month to explore vibrant traditional festivals, fairs and celebrations across Indian states and districts.'
        tabs = month_tabs_html(month)
        cards_html = f'<div class="cards two">{"".join(server_festival_card(item) for item in result)}</div>' if result else '<p class="empty">No festivals recorded for this selection yet.</p>'
        notice = '<p class="notice">Festival months represent recurring seasonal windows. Always verify exact dates, venues and schedules with official state tourism authorities.</p>'
        content = f'''{breadcrumb_html('Festival calendar')}<p class="eyebrow">{eyebrow}</p><h1>{heading}</h1><p class="lead">{lead}</p>{tabs}{notice}<p><strong>{len(result)}</strong> celebrations found across India</p>{cards_html}'''
        return page_document(title, content, canonical_path=f'/festivals{f"?month={month}" if month else ""}')

    @app.get('/month/{value}', response_class=HTMLResponse)
    def rendered_month(value: int):
        if value < 1 or value > 12:
            raise HTTPException(422, 'Choose a month from January to December.')
        return rendered_festivals(month=value)

    @app.get('/saved', response_class=HTMLResponse)
    def rendered_saved():
        content = f'''{breadcrumb_html('Saved places')}<p class="eyebrow">Trip planning & favorites</p><h1>Your saved collection.</h1><p class="lead">Save destinations across India as you explore. Turn your collection into a day-by-day smart travel itinerary, calculate road distances, and share directly to WhatsApp.</p><div id="saved-itinerary-builder"></div><div id="saved-cards-container"><a class="button" href="/explore">Explore destinations</a></div>'''
        return page_document('Saved places', content, canonical_path='/saved')

    @app.get('/area', response_class=HTMLResponse)
    def rendered_area():
        regions = states()
        territories = union_territories()
        state_links = ''.join(server_region_link(region) for region in regions)
        territory_links = ''.join(server_region_link(region) for region in territories)
        content = f'''{breadcrumb_html('Explore by region')}<p class="eyebrow">Start close to home</p><h1>Every corner has a story.</h1><p class="lead">Choose a state or union territory, then select a district for places, local food and celebrations.</p><div class="state-search-box"><span>⌕</span><input type="text" id="state-filter-input" placeholder="Quick find a state or territory (e.g. Odisha, Sikkim, Goa)..." aria-label="Filter states"></div><div id="states-group-wrap"><section class="section"><p class="eyebrow">States</p><h2>Choose a state</h2><div class="cards">{state_links}</div></section><section class="section"><p class="eyebrow">Union territories</p><h2>Choose a union territory</h2><div class="cards">{territory_links}</div></section></div>'''
        return page_document('Explore states and union territories', content, canonical_path='/area')

    @app.get('/about', response_class=HTMLResponse)
    def rendered_about():
        content = f'''{breadcrumb_html('About')}<p class="eyebrow">Built for curious travellers</p><h1>Travel deeper,<br>one district at a time.</h1><p class="lead">India Explorer helps you move beyond a checklist of famous landmarks. Find the local context, heritage, celebrations and practical starting points that make a destination memorable.</p><div class="about-grid"><div><h3>Explore with context</h3><p>Browse India’s states and union territories, then follow the directory into districts and detailed places.</p></div><div><h3>Save your ideas</h3><p>Favorites and recently viewed places stay on this device, so planning feels personal without an account.</p></div><div><h3>Travel responsibly</h3><p>Tourism details and festival dates can change. Use the linked official sources to confirm plans before you go.</p></div></div>'''
        return page_document('About India Explorer', content, canonical_path='/about')

    @app.get('/sitemap.xml', response_class=Response)
    def sitemap():
        urls = ['/', '/explore', '/area', '/circuits', '/festivals', '/about', '/saved']
        urls.extend(f"/circuit/{item['slug']}" for item in rows('SELECT slug FROM circuits'))
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
