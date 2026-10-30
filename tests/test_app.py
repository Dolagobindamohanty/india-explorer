import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import create_app, distance


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        yield client


def test_full_destination_journey(client):
    states = client.get('/api/states').json()
    assert len(states) == 28
    assert {s['name'] for s in states} >= {'Kerala', 'Rajasthan', 'Goa', 'Himachal Pradesh', 'Tamil Nadu', 'Karnataka', 'Odisha'}
    covers = {s['slug']: s['cover_image_url'] for s in states}
    assert all(url.startswith('/assets/states/') for url in covers.values())
    assert covers['odisha'] == '/assets/states/odisha.jpg'
    assert covers['haryana'] == '/assets/states/haryana.jpg'
    assert covers['west-bengal'] == '/assets/states/west-bengal.jpg'
    assert covers['maharashtra'] == '/assets/states/maharashtra.jpg'
    assert covers['manipur'] == '/assets/states/manipur.jpg'
    assert covers['nagaland'] == '/assets/states/nagaland.jpg'
    assert covers['uttar-pradesh'] == '/assets/states/uttar-pradesh.jpg'
    territories = client.get('/api/union-territories').json()
    assert len(territories) == 8
    assert {t['name'] for t in territories} == {'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'}
    assert client.get('/api/states/delhi').status_code == 200
    assert len(client.get('/api/districts?kind=ut').json()) >= 45
    assert len(client.get('/api/districts?region=karnataka').json()) >= 31
    assert {d['name'] for d in client.get('/api/districts?region=karnataka').json()} >= {'Bengaluru Urban', 'Mysuru', 'Kodagu', 'Vijayanagara', 'Dakshina Kannada', 'Udupi'}
    kerala = client.get('/api/states/kerala').json()
    assert len(kerala['districts']) == 14
    district = client.get('/api/districts/alappuzha').json()
    assert {f['name'] for f in district['festivals']} == {'Onam', 'Nehru Trophy Boat Race'}
    place = client.get('/api/places/alappuzha-beach').json()
    assert place['district'] == 'Alappuzha'
    assert place['nearby'][0]['slug'] == 'alappuzha-backwaters'
    assert place['verification_status'] == 'needs_review'
    assert place['last_verified_at'] is None
    assert place['image_url'] == '/assets/places/alappuzha-beach.jpg'
    all_places = client.get('/api/places').json()
    assert len(all_places) == 227
    assert all(item['image_url'] == f"/assets/places/{item['slug']}.jpg" for item in all_places)
    place_images = [item['image_url'] for item in all_places]
    assert len(place_images) == len(set(place_images))
    assert client.get('/api/districts/bengaluru-urban').json()['places'] == []
    assert len(client.get('/api/districts/puri').json()['places']) == 12
    assert len(client.get('/api/districts/khordha').json()['places']) == 17
    odisha = client.get('/api/states/odisha').json()
    assert len(odisha['districts']) == 30
    assert len(odisha['places']) == 111
    north_goa = client.get('/api/districts/north-goa').json()
    assert len(north_goa['places']) == 5
    assert {p['slug'] for p in north_goa['places']} >= {'basilica-bom-jesus', 'fontainhas', 'aguada-fort', 'se-cathedral', 'anjuna-beach'}
    south_goa = client.get('/api/districts/south-goa').json()
    assert len(south_goa['places']) == 6
    assert {p['slug'] for p in south_goa['places']} >= {'palolem-beach', 'dudhsagar-falls', 'mangueshi-temple', 'cabo-de-rama-fort', 'shanta-durga-temple', 'agonda-beach'}
    assert len(client.get('/api/states/goa').json()['places']) == 11
    sikkim = client.get('/api/states/sikkim').json()
    assert len(sikkim['districts']) == 6
    assert len(sikkim['places']) == 7
    gangtok = client.get('/api/districts/gangtok').json()
    assert any(p['slug'] == 'tsomgo-lake' for p in gangtok['places'])
    mangan = client.get('/api/districts/mangan').json()
    assert {p['slug'] for p in mangan['places']} >= {'gurudongmar-lake', 'yumthang-valley', 'khangchendzonga-national-park'}
    tripura = client.get('/api/states/tripura').json()
    assert len(tripura['districts']) == 8
    assert len(tripura['places']) == 8
    west_tripura = client.get('/api/districts/west-tripura').json()
    assert any(p['slug'] == 'ujjayanta-palace' for p in west_tripura['places'])
    gomati = client.get('/api/districts/gomati').json()
    assert {p['slug'] for p in gomati['places']} >= {'tripura-sundari-temple', 'chabimura-rock-carvings'}
    sepahijala = client.get('/api/districts/sepahijala').json()
    assert any(p['slug'] == 'neermahal-water-palace' for p in sepahijala['places'])
    unakoti = client.get('/api/districts/unakoti').json()
    assert any(p['slug'] == 'unakoti-rock-carvings' for p in unakoti['places'])
    hp = client.get('/api/states/himachal-pradesh').json()
    assert len(hp['districts']) == 13
    assert len(hp['places']) == 11
    kullu = client.get('/api/districts/kullu').json()
    assert {p['slug'] for p in kullu['places']} >= {'hidimba-devi-temple', 'rohtang-pass'}
    spiti = client.get('/api/districts/spiti').json()
    assert {p['slug'] for p in spiti['places']} >= {'key-monastery', 'chandratal-lake', 'tabo-monastery'}
    # Union Territories comprehensive verification
    andaman = client.get('/api/states/andaman-and-nicobar-islands').json()
    assert len(andaman['districts']) == 3
    assert len(andaman['places']) == 5
    assert {p['slug'] for p in andaman['places']} >= {'cellular-jail', 'radhanagar-beach', 'ross-island-andaman', 'elephant-beach-havelock', 'baratang-island-caves'}
    delhi = client.get('/api/states/delhi').json()
    assert len(delhi['districts']) == 11
    assert len(delhi['places']) == 8
    assert {p['slug'] for p in delhi['places']} >= {'red-fort-delhi', 'qutub-minar', 'humayuns-tomb', 'india-gate', 'akshardham-temple-delhi', 'lotus-temple-delhi', 'jama-masjid-delhi', 'bangla-sahib-delhi'}
    jk = client.get('/api/states/jammu-and-kashmir').json()
    assert len(jk['districts']) == 20
    assert len(jk['places']) == 8
    assert {p['slug'] for p in jk['places']} >= {'dal-lake', 'gulmarg-gondola', 'vaishno-devi', 'martand-sun-temple', 'pahalgam-betaab-valley', 'shankaracharya-temple', 'sonamarg-thajiwas', 'nishat-shalimar-gardens'}
    ladakh = client.get('/api/states/ladakh').json()
    assert len(ladakh['districts']) == 4
    assert len(ladakh['places']) == 7
    assert {p['slug'] for p in ladakh['places']} >= {'thiksey-monastery', 'pangong-tso', 'diskit-monastery', 'leh-palace-shanti-stupa', 'sangam-indus-zanskar', 'khardung-la-pass', 'hemis-monastery'}
    puducherry = client.get('/api/states/puducherry').json()
    assert len(puducherry['districts']) == 4
    assert len(puducherry['places']) == 6
    assert {p['slug'] for p in puducherry['places']} >= {'auroville-matrimandir', 'promenade-beach-pondicherry', 'aurobindo-ashram', 'white-town-pondicherry', 'paradise-beach-pondicherry', 'sacred-heart-basilica-pondicherry'}
    chandigarh = client.get('/api/states/chandigarh').json()
    assert len(chandigarh['places']) == 23
    assert {p['slug'] for p in chandigarh['places']} >= {'rock-garden-chandigarh', 'sukhna-lake', 'rose-garden-chandigarh', 'capitol-complex-open-hand', 'leisure-valley-chandigarh', 'garden-of-fragrance', 'japanese-garden-chandigarh', 'sector-17-plaza'}
    dnh = client.get('/api/states/dadra-and-nagar-haveli-and-daman-and-diu').json()
    assert len(dnh['places']) == 5
    assert {p['slug'] for p in dnh['places']} >= {'diu-fort', 'moti-daman-fort', 'naida-caves-diu', 'nagoa-beach-diu', 'jampore-beach-daman'}
    lakshadweep = client.get('/api/states/lakshadweep').json()
    assert len(lakshadweep['places']) == 4
    assert {p['slug'] for p in lakshadweep['places']} >= {'bangaram-atoll', 'agatti-island-lagoon', 'kavaratti-island', 'kadmat-island-diving'}
    # Explicit UNESCO distinction test:
    # 1. Standalone World Heritage Site
    konark = client.get('/api/places/konark-sun-temple').json()
    assert konark['heritage_designation'] == 'world_heritage_site'
    red_fort = client.get('/api/places/red-fort-delhi').json()
    assert red_fort['heritage_designation'] == 'world_heritage_site'
    # 2. Component of larger serial site
    amber = client.get('/api/places/amber-fort').json()
    assert amber['heritage_designation'] == 'component_site'
    capitol = client.get('/api/places/capitol-complex-open-hand').json()
    assert capitol['heritage_designation'] == 'component_site'
    # 3. Tentative list site
    tabo = client.get('/api/places/tabo-monastery').json()
    assert tabo['heritage_designation'] == 'tentative_list'
    dal = client.get('/api/places/dal-lake').json()
    assert dal['heritage_designation'] == 'tentative_list'
    # 4. Non-UNESCO landmark (Shimla Ridge is not UNESCO)
    ridge = client.get('/api/places/shimla-ridge').json()
    assert ridge['heritage_id'] is None
    assert ridge['heritage_designation'] is None


def test_filters_combine_and_heritage_links(client):
    result = client.get('/api/places', params={'state': 'rajasthan', 'month': 1, 'unesco': 'true'}).json()
    assert {p['slug'] for p in result} == {'amber-fort', 'jantar-mantar', 'jaisalmer-fort'}
    assert all(p['unesco_url'].startswith('https://whc.unesco.org/en/list/') for p in result)
    assert client.get('/api/places?state=kerala&unesco=true').json() == []
    assert len(client.get('/api/places?month=7').json()) == 14
    assert len(client.get('/api/places?month=6').json()) == 26
    assert len(client.get('/api/places?q=Kochi').json()) == 2
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []
    assert client.get('/api/places', params={'q': '%'}).json() == []
    assert client.get('/api/places', params={'q': '_'}).json() == []
    assert len(client.get('/api/places?q=Kochi').json()) == 2
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []
    assert client.get('/api/places', params={'q': '%'}).json() == []
    assert client.get('/api/places', params={'q': '_'}).json() == []


def test_month_calendar_does_not_invent_annual_dates(client):
    result = client.get('/api/festivals?month=8&district=alappuzha').json()
    assert len(result) == 2
    assert all(f['occurrences'] == [] for f in result)
    dec_festivals = client.get('/api/festivals?month=12').json()
    assert len(dec_festivals) >= 2
    assert any(f['name'] == 'Hornbill Festival' for f in dec_festivals)
    assert any(f['name'] == 'Konark Dance & Sand Art Festival' for f in dec_festivals)


@pytest.mark.parametrize('url', ['/api/places?month=13', '/api/festivals?month=0'])
def test_invalid_month(client, url):
    assert client.get(url).status_code == 422


@pytest.mark.parametrize('url', ['/api/states/missing', '/api/districts/missing', '/api/places/missing'])
def test_missing_destination(client, url):
    assert client.get(url).status_code == 404


def test_seed_is_persistent_and_idempotent(tmp_path):
    path = tmp_path / 'persistent.sqlite3'
    create_app(path)
    create_app(path)
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM places').fetchone()[0] == 227
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        db.execute('PRAGMA foreign_keys=ON')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (9999, 1)')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (1, 13)')


def test_seed_refreshes_corrected_odisha_records(tmp_path):
    path = tmp_path / 'odisha-correction.sqlite3'
    create_app(path)
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE places SET description=? WHERE slug='ananta-basudeva-temple'",
            ('T–h–i–s– –i–s– –c–o–r–r–u–p–t–e–d',),
        )
        db.commit()

    create_app(path)

    with sqlite3.connect(path) as db:
        description = db.execute(
            "SELECT description FROM places WHERE slug='ananta-basudeva-temple'"
        ).fetchone()[0]
    assert description.startswith('Located near the sacred Bindusagar tank')
    assert '–' not in description


def test_website_and_health(client):
    homepage = client.get('/').text
    assert 'india' in homepage
    assert 'Explore Incredible India' in homepage
    assert '28' in homepage and '807' in homepage
    assert 'Featured destinations' in homepage
    assert 'href="/explore"' in homepage
    assert 'href="/state/' in homepage
    assert 'Featured States' in homepage
    assert client.get('/app.js').status_code == 200
    assert client.get('/style.css').status_code == 200
    assert client.get('/assets/state-cover.svg').status_code == 200
    assert client.get('/assets/states/odisha.jpg').status_code == 200
    assert client.get('/assets/states/haryana.jpg').status_code == 200
    assert client.get('/assets/states/uttar-pradesh.jpg').status_code == 200
    assert client.get('/healthz').json() == {'status': 'ok', 'places': 227}
    assert distance({'latitude': 0, 'longitude': 0}, {'latitude': 0, 'longitude': 0}) == 0


def test_server_rendered_routes_are_crawlable(client):
    explore = client.get('/explore').text
    assert 'Find your kind of place' in explore
    assert 'class="art"' in explore
    assert 'Alappuzha Backwaters' in explore
    assert 'Kerala' in client.get('/state/kerala').text
    assert 'Alappuzha' in client.get('/district/alappuzha').text
    assert 'Alappuzha Beach' in client.get('/place/alappuzha-beach').text
    assert 'Festival calendar' in client.get('/month/8').text
    assert 'Festivals in August' in client.get('/month/8').text
    assert 'Typically in August' in client.get('/district/alappuzha').text
    assert 'January, February, March, October' in client.get('/place/alappuzha-beach').text
    assert 'Saved places' in client.get('/saved').text
    area = client.get('/area').text
    assert 'Choose a state' in area
    assert 'Kerala' in area and 'Puducherry' in area
    assert '<link rel="canonical" href="https://india-explorer-hazel.vercel.app/explore">' in explore
    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    assert '/state/kerala' in sitemap.text
    assert '/circuits' in sitemap.text
    assert 'Sitemap:' in client.get('/robots.txt').text
    assert 'data-server-rendered="true"' in explore
    festivals_page = client.get('/festivals').text
    assert 'Celebrations across India' in festivals_page
    assert 'month-selector-tabs' in festivals_page
    circuits_page = client.get('/circuits').text
    assert 'Curated travel trails' in circuits_page
    assert 'The Golden Triangle' in circuits_page
    gt_page = client.get('/circuit/golden-triangle').text
    assert 'Stop 1' in gt_page
    assert 'Qutb Minar' in gt_page
    assert 'Taj Mahal' in gt_page
    assert 'Amber Fort' in gt_page
    kashmir_page = client.get('/circuit/paradise-kashmir-trail').text
    assert 'Dal Lake' in kashmir_page
    assert 'Gulmarg' in kashmir_page
    island_page = client.get('/circuit/tropical-island-corals').text
    assert 'Cellular Jail' in island_page
    assert 'Radhanagar Beach' in island_page
    puducherry_page = client.get('/circuit/french-coastal-puducherry').text
    assert 'White Town' in puducherry_page
    assert 'Paradise Beach' in puducherry_page
    chd_page = client.get('/circuit/chandigarh-modernist-trail').text
    assert 'Le Corbusier' in chd_page
    assert 'Nek Chand' in chd_page
    odisha_trail = client.get('/circuit/tribal-odisha-waterfalls').text
    assert 'Deomali' in odisha_trail
    assert 'Duduma' in odisha_trail


def test_editorial_status(client):
    assert client.get('/api/editorial-status').json() == {
        'detailed_places': 227,
        'reviewed_places': 0,
        'unreviewed_places': 227,
        'confirmed_festival_dates': 0,
    }
